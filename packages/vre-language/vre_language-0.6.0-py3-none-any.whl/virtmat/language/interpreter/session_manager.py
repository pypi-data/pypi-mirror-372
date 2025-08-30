"""manage sessions for dynamic model processing / incremental development"""
import os
import sys
import importlib
import readline
from code import InteractiveConsole
from functools import cached_property
from textx import metamodel_from_file, textx_isinstance
from virtmat.language.metamodel.processors import table_processor, null_processor, number_processor
from virtmat.language.metamodel.properties import add_metamodel_classes_attributes
from virtmat.language.utilities.textx import GRAMMAR_LOC, TextXCompleter, GrammarString
from virtmat.language.utilities.textx import get_identifiers
from virtmat.language.utilities.errors import error_handler, ModelNotFoundError
from virtmat.language.utilities.errors import textxerror_wrap
from virtmat.language.utilities.errors import RuntimeTypeError, QueryError
from virtmat.language.utilities.logging import get_logger
from virtmat.language.utilities.warnings import warnings, TextSUserWarning
from virtmat.language.utilities.formatters import formatter
from virtmat.language.utilities.fireworks import get_model_history, get_models_overview
from virtmat.language.utilities.fireworks import rerun_vars, cancel_vars, get_model_tag
from virtmat.language.utilities.fireworks import get_lost_reserved_running
from virtmat.language.utilities.serializable import tag_serialize
from virtmat.language.utilities.typemap import checktype
from virtmat.language.constraints.typechecks import (tuple_type, series_type, table_type,
                                                     dict_type, array_type, quantity_type,
                                                     alt_table_type)
from .instant_executor import (tuple_value, series_value, table_value, dict_value,
                               bool_str_array_value, numeric_array_value, alt_table_value,
                               numeric_subarray_value, plain_type_value, quantity_value)
from .session import Session


def add_value_session_model(metamodel):
    """add the value-property for objects of session manager models"""
    mapping_dict = {
        'Tuple': tuple_value,
        'Series': series_value,
        'Table': table_value,
        'Dict': dict_value,
        'AltTable': alt_table_value,
        'BoolArray': bool_str_array_value,
        'StrArray': bool_str_array_value,
        'IntArray': numeric_array_value,
        'FloatArray': numeric_array_value,
        'ComplexArray': numeric_array_value,
        'IntSubArray': numeric_subarray_value,
        'FloatSubArray': numeric_subarray_value,
        'ComplexSubArray': numeric_subarray_value,
        'String': plain_type_value,
        'Bool': plain_type_value,
        'Quantity': quantity_value
    }
    for key, func in mapping_dict.items():
        metamodel[key].value = cached_property(textxerror_wrap(checktype(func)))
        metamodel[key].value.__set_name__(metamodel[key], 'value')
    metamodel['Null'].value = None


def add_types_session_model(metamodel):
    """add the type-property for objects of session manager models"""
    mapping_dict = {
        'Tuple': tuple_type,
        'Series': series_type,
        'Table': table_type,
        'Dict': dict_type,
        'AltTable': alt_table_type,
        'BoolArray': array_type,
        'StrArray': array_type,
        'IntArray': array_type,
        'FloatArray': array_type,
        'ComplexArray': array_type,
        'IntSubArray': array_type,
        'FloatSubArray': array_type,
        'ComplexSubArray': array_type,
        'Quantity': quantity_type
    }
    for key, function in mapping_dict.items():
        metamodel[key].type_ = cached_property(textxerror_wrap(function))
        metamodel[key].type_.__set_name__(metamodel[key], 'type_')
    metamodel['Bool'].type_ = bool
    metamodel['String'].type_ = str


def expand_query_prefix(query):
    """expand the path prefix in query keys"""
    p_map = {'tags': 'spec._tag.', 'meta': '', 'data': 'spec.'}
    if not all(k in ('tags', 'meta', 'data') for k in query.keys()):
        raise QueryError('query must include tags, meta or data keys')

    def _recursive_q(obj, prefix):
        if isinstance(obj, dict):
            out = {}
            for key, val in obj.items():
                key = prefix + key[1:] if key[0] == '~' else key
                out[key] = _recursive_q(val, prefix)
            return out
        if isinstance(obj, (tuple, list)):
            return [_recursive_q(e, prefix) for e in obj]
        return obj

    return {k: _recursive_q(v, p_map[k]) for k, v in query.items()}


def get_prettytable(dataframe):
    """convert pandas dataframe to a prettytable object"""
    try:
        module = importlib.import_module('prettytable')
        class_ = getattr(module, 'PrettyTable')
    except (ImportError, AttributeError):
        return str(dataframe)  # failover, not covered
    table = class_(list(dataframe.columns))
    for tpl in dataframe.itertuples(index=False, name=None):
        table.add_row(tpl)
    table.align = 'l'
    table.max_width = 120
    return table


class SessionManager(InteractiveConsole):
    """session manager for basic interactive work using a text terminal"""

    options = ['%exit', '%bye', '%close', '%quit', '%start', '%stop', '%new',
               '%vary', '%history', '%hist', '%tag', '%uuid', '%sleep', '%cancel',
               '%rerun', '%find', '%help', 'use', 'print', 'view', 'vary', 'tag']

    def __init__(self, lpad, **kwargs):
        super().__init__()
        self.lpad = lpad
        self.kwargs = dict(kwargs)
        del self.kwargs['uuid']
        del self.kwargs['grammar_path']
        del self.kwargs['model_path']
        create_new = not bool(kwargs['model_path'])
        self.session = Session(lpad, create_new=create_new, **kwargs)
        self.uuid = self.session.uuids[0]
        self.grammar_path = kwargs['grammar_path'] or GRAMMAR_LOC
        session_grammar = os.path.join(os.path.dirname(GRAMMAR_LOC), 'session.tx')
        self.metamodel = metamodel_from_file(session_grammar, auto_init_attributes=False)
        add_metamodel_classes_attributes(self.metamodel)
        add_types_session_model(self.metamodel)
        add_value_session_model(self.metamodel)
        obj_processors = {'Null': null_processor, 'Number': number_processor,
                          'Table': table_processor}
        self.metamodel.register_obj_processors(obj_processors)
        model_grammar = GrammarString(self.grammar_path).string
        self.completer = TextXCompleter(model_grammar, self.options, console=self)
        self._set_completer_ids()
        readline.set_completer(self.completer.complete)
        readline.set_completer_delims('')
        readline.parse_and_bind('tab: complete')

    def main_loop(self):
        """this is the main loop of the interactive session"""
        if not sys.stdin.isatty():
            msg = 'Session running in a shell not connected to a terminal'
            get_logger(__name__).warning(msg)
            warnings.warn(msg, TextSUserWarning)
        ps1_save = getattr(sys, 'ps1', None)
        ps2_save = getattr(sys, 'ps2', None)
        try:
            sys.ps1 = 'Input > '
            sys.ps2 = '      > '
            self.interact(banner='Welcome to textS/textM. Type %help for some help.',
                          exitmsg='')
        finally:
            print('Exiting')
            self.session.stop_runner()
            sys.ps1 = ps1_save
            sys.ps2 = ps2_save

    def runsource(self, source, filename=None, symbol=None):
        """this is used by the superclass to realize a REPL"""
        if source.strip():
            try:
                need_inp = self.process_input(source)
            finally:
                self.check_session()
            return need_inp
        return False  # not covered

    def _set_completer_ids(self):
        """set completer IDs, such as variables, imports, ..."""
        self.completer.ids = [i.name for i in get_identifiers(self.session.model)]

    @error_handler
    def get_model_value(self, *args, **kwargs):
        """wrapped and evaluated version of get_model() of the Session class"""
        return getattr(self.session.get_model(*args, uuid=self.uuid, **kwargs), 'value', '')

    def check_session(self):
        """check session consistency"""
        if (len(self.session.models) != len(self.session.uuids) or
           any(u is None for u in self.session.uuids)):  # not covered
            self.session = Session(self.lpad, uuid=self.uuid, **self.kwargs)
            msg = 'Session has been restarted'
            get_logger(__name__).warning(msg)
            warnings.warn(msg, TextSUserWarning)

    @error_handler
    def process_input(self, input_str):
        """create a session model from input string"""
        model = self.metamodel.model_from_str(input_str)
        get_logger(__name__).debug('process_input: session model: %s', model)
        if textx_isinstance(model, self.metamodel['Magic']):
            self.process_magic(model)
            return False
        if textx_isinstance(model, self.metamodel['Expression']):
            output = self.get_model_value(model_str=f'print({input_str})')
            if output is not None:
                print('Output >', output)
            return False
        assert textx_isinstance(model, self.metamodel['Program'])
        if self.completer.is_complete(input_str):
            output = self.get_model_value(model_str=input_str)
            if output:
                print('Output >', output)
            self._set_completer_ids()
            return False
        return True  # not covered

    @error_handler
    def process_magic(self, model):
        """process a magic command model"""
        if model.com in ('exit', 'bye', 'close', 'quit'):
            raise SystemExit()
        if model.com == 'stop':
            self.session.stop_runner()
            self.kwargs['autorun'] = False
        elif model.com == 'start':
            self.session.start_runner()
            self.kwargs['autorun'] = True
        elif model.com == 'sleep':
            if self.session.wfe:
                if model.arg is None:
                    print(self.session.wfe.sleep_time)
                else:
                    self.session.wfe.sleep_time = model.arg
                    self.kwargs['sleep_time'] = model.arg
        elif model.com == 'new':
            if self.is_launcher_running():
                self.session.stop_runner()
            self.session = Session(self.lpad, create_new=True,
                                   grammar_path=self.grammar_path, **self.kwargs)
            self.uuid = self.session.uuids[0]
            self._set_completer_ids()
            print(f'Started new session with uuids {formatter(self.session.uuids)}')
        elif model.com == 'uuid':
            if model.arg is None:
                print('uuids:', formatter(self.uuid), formatter(self.session.uuids))
            elif model.arg != self.uuid:
                self.switch_model(model.arg)
        elif model.com == 'vary':
            print('vary:', formatter(self.session.get_vary_df()))
        elif model.com in ('hist', 'history'):
            print(get_prettytable(get_model_history(self.lpad, self.uuid)))
            if self.session.wfe:
                unres_vars, lostj_vars = get_lost_reserved_running(wfengine=self.session.wfe)
            else:
                unres_vars, lostj_vars = get_lost_reserved_running(self.lpad, self.uuid)
            print(f'Lost RESERVED: {formatter(unres_vars)}\nLost RUNNING: {formatter(lostj_vars)}')
        elif model.com == 'tag':
            print(formatter(get_model_tag(self.lpad, self.uuid)))
        elif model.com == 'find':
            get_logger(__name__).debug('process_magic: find: %s', formatter(model.arg.value))
            try:
                q_dict = expand_query_prefix(tag_serialize(model.arg.value))
            except RuntimeTypeError as err:
                get_logger(__name__).error('process_magic: %s', str(err))
                raise QueryError(err) from err
            get_logger(__name__).debug('process_magic: query: %s', q_dict)
            matching_uuids = self.get_wflows_from_user_query(q_dict)
            if matching_uuids:
                if model.load_one:
                    if self.uuid not in matching_uuids:
                        self.switch_model(matching_uuids[0])
                        print('uuids:', formatter(self.uuid), formatter(self.session.uuids))
                else:
                    print(get_prettytable(get_models_overview(self.lpad, matching_uuids)))
        elif model.com == 'rerun':
            rerun_vars(self.lpad, self.uuid, model.args)
        elif model.com == 'cancel':
            cancel_vars(self.lpad, self.uuid, model.args)
        else:
            assert model.com == 'help'
            msg = ('%exit, %bye, %close, %quit     close (quit) the session\n'
                   '%start                         activate evaluation\n'
                   '%stop                          deactivate evaluation\n'
                   '%sleep <integer>               set sleep time (sec) for background evaluation\n'
                   '%uuid                          print the UUID of the active model\n'
                   '%uuid <UUID>                   switch to model with UUID\n'
                   '%new                           create a new session and a new model\n'
                   '%hist, %history                print the current model source\n'
                   '%rerun var1[, var2][, ...]     re-evaluate var1, var2, etc.\n'
                   '%cancel var1[, var2][, ...]    cancel evaluation of var1, var2, etc.\n'
                   '%vary                          print the varied parameters\n'
                   '%tag                           print the tag section\n'
                   '%find <query> [action]         perform a global search\n'
                   '%help                          show this help\n')
            print(msg)

    def is_launcher_running(self):
        """return True if launcher thread has been started and is running"""
        return (self.session.wfe and self.session.wfe.thread and
                self.session.wfe.thread.is_alive())

    def get_wflows_from_user_query(self, q_dict):
        """perform a database-wide user query, return a list of matching models"""
        q_data = q_dict.get('data')
        q_tags = q_dict.get('tags')
        fw_q = q_tags and {'name': '_fw_meta_node', **q_tags}
        wf_ids = self.lpad.get_fw_ids_in_wfs(q_dict.get('meta'), fw_query=fw_q)
        if q_data:
            wf_ids = self.lpad.get_fw_ids_in_wfs({'nodes': {'$in': wf_ids}}, q_data)
        wf_q = {'nodes': {'$in': wf_ids}}
        wf_p = {'metadata.uuid': True}
        return [w['metadata']['uuid'] for w in self.lpad.workflows.find(wf_q, wf_p)]

    def switch_model(self, new_uuid):
        """switch from one to another model"""
        if new_uuid in self.session.uuids:
            self.uuid = new_uuid  # not covered
        else:
            start_thread = self.is_launcher_running()
            if start_thread:
                self.session.stop_runner()
            try:
                self.session = Session(self.lpad, uuid=new_uuid, **self.kwargs)
            except ModelNotFoundError as err:
                if start_thread:
                    self.session.start_runner()
                raise err
            self.uuid = new_uuid
            self._set_completer_ids()
