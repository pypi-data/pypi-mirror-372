"""
This module contains an IPython kernel for VRE Language
"""
import os
from ipykernel.kernelbase import Kernel
from ipykernel.kernelapp import IPKernelApp
from textx import TextXError, textx_isinstance, metamodel_from_file
from fireworks import LaunchPad
from fireworks.fw_config import LAUNCHPAD_LOC
from virtmat.language.metamodel.processors import table_processor, null_processor, number_processor
from virtmat.language.utilities.textx import GRAMMAR_LOC
from virtmat.language.interpreter.session import Session
from virtmat.language.interpreter.session_manager import add_value_session_model
from virtmat.language.interpreter.session_manager import add_types_session_model
from virtmat.language.interpreter.session_manager import get_prettytable
from virtmat.language.interpreter.session_manager import expand_query_prefix
from virtmat.language.metamodel.properties import add_metamodel_classes_attributes
from virtmat.language.utilities.errors import format_textxerr_msg
from virtmat.language.utilities.errors import RuntimeTypeError, QueryError
from virtmat.language.utilities.errors import ModelNotFoundError, UpdateError
from virtmat.language.utilities.errors import VaryError, ReuseError, CompatibilityError
from virtmat.language.utilities.errors import ConfigurationError, ObjectFromFileError
from virtmat.language.utilities.logging import get_logger
from virtmat.language.utilities.formatters import formatter
from virtmat.language.utilities.fireworks import get_models_overview, get_model_history
from virtmat.language.utilities.fireworks import rerun_vars, cancel_vars
from virtmat.language.utilities.fireworks import get_model_tag, get_lost_reserved_running
from virtmat.language.utilities.fireworks import object_from_file
from virtmat.language.utilities.serializable import tag_serialize
from virtmat.middleware.exceptions import ConfigurationException


class VMKernel(Kernel):
    """
    This is the actual virtmat kernel class derived from the Kernel
    class in ipykernel.kernelbase
    """

    banner = 'VRE Language kernel for computational materials science'

    implementation = 'Virtmat'
    implementation_version = '0.1'
    language = 'virtmat'
    language_version = '0.1'
    language_info = {
        'name': 'virtmat',
        'mimetype': 'text/plain',
        'file_extension': '.vm',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.grammar_path = kwargs.get('grammar_path', GRAMMAR_LOC)

        if LAUNCHPAD_LOC is None:
            if 'MONGOMOCK_SERVERSTORE_FILE' not in os.environ:
                msg = ('Neither default Launchpad file configured nor custom '
                       'Launchpad file is specified.')
                raise ConfigurationError(msg)
            self.lpad = LaunchPad()
            config_dir = os.path.dirname(os.environ['MONGOMOCK_SERVERSTORE_FILE'])
        else:
            self.lpad = object_from_file(LaunchPad, LAUNCHPAD_LOC)
            config_dir = os.path.dirname(LAUNCHPAD_LOC)

        self.vmlang_session = Session(
            self.lpad,
            grammar_path=self.grammar_path,
            create_new=True,
            autorun=True,
            async_run=False,
            config_dir=config_dir,
            detect_duplicates=True,
            lp_path=LAUNCHPAD_LOC,
            model_path=None,
            on_demand=False,
            qadapter=None,
            sleep_time=30,
            unique_launchdir=True,
            uuid=None)

        self.kwargs = {'autorun': True, 'async_run': False,
                       'config_dir': config_dir,
                       'detect_duplicates': True,
                       'lp_path': LAUNCHPAD_LOC,
                       'model_path': None,
                       'on_demand': False,
                       'qadapter': None,
                       'sleep_time': 30,
                       'unique_launchdir': True}

        self.memory = ['print', 'use']

        if self.vmlang_session.uuids:
            self.uuid = self.vmlang_session.uuids[0]
        else:
            self.uuid = None
        self.vmlang_session.process_models('print(true)')

        session_grammar = os.path.join(os.path.dirname(GRAMMAR_LOC), 'session.tx')
        self.metamodel = metamodel_from_file(session_grammar, auto_init_attributes=False)
        add_metamodel_classes_attributes(self.metamodel)
        add_types_session_model(self.metamodel)
        add_value_session_model(self.metamodel)
        obj_processors = {'Null': null_processor, 'Number': number_processor,
                          'Table': table_processor}
        self.metamodel.register_obj_processors(obj_processors)

    def get_model_value(self, *args, **kwargs):
        """evaluated version of get_model() of the Session class"""
        return getattr(self.vmlang_session.get_model(*args, uuid=self.uuid, **kwargs), 'value', '')

    def do_execute(self, code, silent, store_history=True, user_expressions=None,
                   allow_stdin=False, *, cell_meta=None, cell_id=None):

        try:
            model = self.metamodel.model_from_str(code)
        except TextXError as err:
            err_type = err.err_type or type(err).__name__
            evalue = format_textxerr_msg(err)  # not the correct formatting
            self.send_response(self.iopub_socket, 'error', {
                'ename': err_type,
                'evalue': evalue,
                'traceback': [evalue]
            })
            return {
                'status': 'error',
                'execution_count': self.execution_count,
                'ename': err_type,
                'evalue': evalue,
                'traceback': [evalue]
            }

        if textx_isinstance(model, self.metamodel['Magic']):
            try:
                self.process_magic(model)
            except TextXError as err:
                err_type = err.err_type or type(err).__name__
                evalue = format_textxerr_msg(err)  # not the correct formatting
            except (ObjectFromFileError, CompatibilityError, VaryError, QueryError,
                    ReuseError, ModelNotFoundError, ConfigurationError,
                    ConfigurationException, UpdateError) as err:
                error_map = {
                    ObjectFromFileError: 'Data input error',
                    CompatibilityError: 'Compatibility error',
                    VaryError: 'Vary error',
                    QueryError: 'Query error',
                    ReuseError: 'Reuse error',
                    ModelNotFoundError: 'Model not found',
                    ConfigurationError: 'Configuration error',
                    ConfigurationException: 'Configuration error',
                    UpdateError: 'Variable update error'}
                for error_class, message in error_map.items():
                    if isinstance(err, error_class):
                        err_type = type(err).__name__
                        evalue = f'{message}: {err}'
                        break
            except Exception as err:
                err_type = type(err).__name__
                evalue = str(err)
            else:
                return {
                    'status': 'ok',
                    'execution_count': self.execution_count,
                    'payload': [],
                    'user_expressions': {}}
            self.send_response(self.iopub_socket, 'error', {
                'ename': err_type,
                'evalue': evalue,
                'traceback': [evalue]
            })
            return {
                'status': 'error',
                'execution_count': self.execution_count,
                'ename': err_type,
                'evalue': evalue,
                'traceback': [evalue]}
        if textx_isinstance(model, self.metamodel['Program']):
            return self.handle_non_magic(code, silent)
        assert textx_isinstance(model, self.metamodel['Expression'])
        return self.handle_non_magic(f'print({code})', silent)

    def handle_non_magic(self, code, silent):
        """handler of program and expression type inputs"""
        try:
            output = self.get_model_value(code)
        except TextXError as err:
            err_type = err.err_type or type(err).__name__
            formatted = format_textxerr_msg(err)
            tb_lines = [f'{err_type}: {formatted}']
            self.send_response(self.iopub_socket, 'error', {
                'ename': err_type,
                'evalue': formatted,
                'traceback': tb_lines
            })
            return {'status': 'error',
                    'execution_count': self.execution_count,
                    'ename': err_type,
                    'evalue': formatted,
                    'traceback': tb_lines}
        name_list = self.vmlang_session.model.name_list
        if name_list:
            for name_ in filter(lambda x: x not in self.memory, name_list):
                self.memory.append(name_)
        if not silent:
            stream_content = {'name': 'stdout', 'text': output}
            self.send_response(self.iopub_socket, 'stream', stream_content)
        return {'status': 'ok',
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {}}

    def process_magic(self, model):
        """handler of magic command inputs"""
        # use dictionary-based factory pattern for magic commands
        commands = {
            'uuid': self._handle_uuid,
            'help': self._handle_help,
            'stop': self._handle_stop,
            'start': self._handle_start,
            'sleep': self._handle_sleep,
            'new': self._handle_new,
            'vary': self._handle_vary,
            'hist': self._handle_history,
            'history': self._handle_history,
            'tag': self._handle_tag,
            'find': self._handle_find,
            'rerun': self._handle_rerun,
            'cancel': self._handle_cancel
        }

        handler = commands.get(model.com)
        if handler:
            handler(model)
        else:
            self.send_response(self.iopub_socket, 'stream', {
                'name': 'stderr',
                'text': f'Unknown command: %{model.com}\n'
            })

    def _handle_stop(self, _):
        self.vmlang_session.stop_runner()
        self.kwargs['autorun'] = False

    def _handle_start(self, _):
        self.vmlang_session.start_runner()
        self.kwargs['autorun'] = True

    def _handle_sleep(self, model):
        if self.vmlang_session.wfe:
            if model.arg is None:
                self.send_response(self.iopub_socket, 'stream', {
                    'name': 'stdout',
                    'text': str(self.vmlang_session.wfe.sleep_time) + '\n'
                })
            else:
                self.vmlang_session.wfe.sleep_time = model.arg
                self.kwargs['sleep_time'] = model.arg

    def _handle_new(self, _):
        if self.is_launcher_running():
            self.vmlang_session.stop_runner()
        self.vmlang_session = Session(self.lpad, create_new=True,
                                      grammar_path=self.grammar_path,  **self.kwargs)
        self.uuid = self.vmlang_session.uuids[0]
        self.send_response(self.iopub_socket, 'stream', {
            'name': 'stdout',
            'text': f'Started new session with uuids {formatter(self.vmlang_session.uuids)}\n'
        })

    def _handle_vary(self, _):
        self.send_response(self.iopub_socket, 'stream', {
            'name': 'stdout',
            'text': f'vary: {formatter(self.vmlang_session.get_vary_df())}\n'
        })

    def _handle_history(self, _):
        self.send_response(self.iopub_socket, 'stream', {
            'name': 'stdout',
            'text': f'{get_prettytable(get_model_history(self.lpad, self.uuid))}\n'
        })
        if self.vmlang_session.wfe:
            unres_vars, lostj_vars = get_lost_reserved_running(wfengine=self.vmlang_session.wfe)
        else:
            unres_vars, lostj_vars = get_lost_reserved_running(self.lpad, self.uuid)
        self.send_response(self.iopub_socket, 'stream', {
            'name': 'stdout',
            'text': f'Lost RESERVED: {formatter(unres_vars)}\nLost RUNNING: {formatter(lostj_vars)}'
        })

    def _handle_tag(self, _):
        self.send_response(self.iopub_socket, 'stream', {
            'name': 'stdout',
            'text': formatter(get_model_tag(self.lpad, self.uuid))
        })

    def _handle_find(self, model):
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
                    self.send_response(self.iopub_socket, 'stream', {
                        'name': 'stdout',
                        'text': (f'uuids: {formatter(self.uuid)}, '
                                 f'{formatter(self.vmlang_session.uuids)}\n')
                    })
            else:
                self.send_response(self.iopub_socket, 'stream', {
                    'name': 'stdout',
                    'text': repr(get_prettytable(get_models_overview(self.lpad, matching_uuids)))
                })

    def _handle_rerun(self, model):
        rerun_vars(self.lpad, self.uuid, model.args)

    def _handle_cancel(self, model):
        cancel_vars(self.lpad, self.uuid, model.args)

    def _handle_uuid(self, model):
        if model.arg is None:
            uuids_msg = f'uuids: {formatter(self.uuid)} {formatter(self.vmlang_session.uuids)}\n'
            self.send_response(self.iopub_socket, 'stream', {'name': 'stdout', 'text': uuids_msg})
        elif model.arg != self.uuid:
            self.switch_model(model.arg)
            self.send_response(self.iopub_socket, 'stream', {
                'name': 'stdout',
                'text': f'Switched to model with UUID: {model.arg}\n'
            })

    def _handle_help(self, _):
        msg = (
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
            '%help                          show this help\n'
        )
        self.send_response(self.iopub_socket, 'stream', {'name': 'stdout', 'text': msg})

    def switch_model(self, new_uuid):
        """switch from one to another model"""
        if new_uuid in self.vmlang_session.uuids:
            self.uuid = new_uuid
        else:
            start_thread = self.is_launcher_running()
            if start_thread:
                self.vmlang_session.stop_runner()
            try:
                self.vmlang_session = Session(self.lpad, uuid=new_uuid, **self.kwargs)
            except ModelNotFoundError as err:
                if start_thread:
                    self.vmlang_session.start_runner()
                raise err
            self.uuid = new_uuid

    def is_launcher_running(self):
        """return True if launcher thread has been started and is running"""
        return (self.vmlang_session.wfe and self.vmlang_session.wfe.thread and
                self.vmlang_session.wfe.thread.is_alive())

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

    def do_complete(self, code, cursor_pos):
        code = code[:cursor_pos]
        default = {'matches': [], 'cursor_start': 0, 'cursor_end': cursor_pos,
                   'metadata': {}, 'status': 'ok'}

        for char in [';', '(', ')', '=', '**', '*', '/', '+', '-']:
            code = code.replace(char, ' ')

        tokens = code.split()
        if not tokens:
            return default

        token = tokens[-1]
        start = cursor_pos - len(token)

        matches = self.memory
        if not matches:
            return default
        matches = [m for m in matches if m.startswith(token)]

        return {'matches': sorted(matches), 'cursor_start': start,
                'cursor_end': cursor_pos, 'metadata': {},
                'status': 'ok'}

    def do_apply(self, content, bufs, msg_id, reply_metadata):
        raise NotImplementedError

    def do_clear(self):
        raise NotImplementedError

    async def do_debug_request(self, msg):
        raise NotImplementedError


if __name__ == '__main__':
    IPKernelApp.launch_instance(kernel_class=VMKernel)
