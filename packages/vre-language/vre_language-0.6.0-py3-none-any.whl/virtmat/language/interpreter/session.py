"""session for dynamic model processing / incremental development"""
import os
from uuid import uuid4
import pandas
import pint
from pint_pandas import PintType
from textx import metamodel_from_file, metamodel_from_str, textx_isinstance
from textx import get_children_of_type
from textx.exceptions import TextXSemanticError
from fireworks.utilities.fw_serializers import load_object
from virtmat.middleware.engine.wfengine import WFEngine
from virtmat.language.metamodel.properties import add_properties
from virtmat.language.metamodel.processors import add_processors, add_obj_processors
from virtmat.language.utilities.textx import GrammarString, get_object_str
from virtmat.language.utilities.errors import ModelNotFoundError, ConfigurationError
from virtmat.language.utilities.errors import VaryError, ReuseError
from virtmat.language.utilities.warnings import warnings, TextSUserWarning
from virtmat.language.utilities.compatibility import check_compatibility
from virtmat.language.utilities.logging import get_logger
from virtmat.language.utilities.formatters import formatter
from virtmat.language.utilities.fireworks import get_nodes_info, get_nodes_providing
from virtmat.language.utilities.fireworks import get_ancestors, safe_update
from virtmat.language.utilities.fireworks import get_model_nodes
from virtmat.language.utilities.serializable import get_serializable
from virtmat.language.utilities.types import get_units


def update_vary(lpad, uuid, vary):
    """updates the vary section in the spec of the meta-node"""
    assert isinstance(vary, pandas.DataFrame)
    spec_update = {'_vary': get_serializable(vary).to_dict()}
    wf_query = {'metadata.uuid': uuid}
    fw_query = {'name': '_fw_meta_node'}
    fw_proj = {'fw_id': True}
    res = get_nodes_info(lpad, wf_query, fw_query, fw_proj)
    assert len(res) == 1
    assert len(res[0]['nodes']) == 1
    safe_update(lpad, res[0]['nodes'][0]['fw_id'], spec_update)
    get_logger(__name__).debug('Updated vary for uuid %s: %s', uuid, formatter(vary))


def vary_model_processor(model, _):
    """model processor for all vary statements"""
    classes = ['GeneralReference', 'FunctionCall', 'IfFunction', 'IfExpression',
               'Comparison', 'Expression', 'BooleanExpression', 'Filter', 'Map',
               'Reduce', 'Sum', 'Any', 'All', 'In', 'Range']
    for obj in get_children_of_type('Vary', model):
        for cls in classes:
            if get_children_of_type(cls, obj):
                msg = 'only literals may be used in vary statements'
                get_logger(__name__).error(msg)
                raise VaryError(msg)


def get_dfr_types(dfr):
    """return the types of the series in a dataframe"""
    dfr_types = {}
    for col in dfr.columns:
        dfr_types_set = set(type(get_serializable(e)) for e in dfr[col])
        assert len(dfr_types_set) == 1
        dfr_types[col] = next(iter(dfr_types_set))
    return dfr_types


class Session:
    """session for dynamic model processing"""

    def __init__(self, lpad, uuid=None, grammar_str=None, grammar_path=None,
                 model_str=None, model_path=None, create_new=False, autorun=False,
                 on_demand=False, async_run=False, config_dir=None,
                 detect_duplicates=False, lp_path=None, **wfe_kwargs):
        self.logger = get_logger(__name__)
        if lpad.fw_id_assigner.find_one({}) is None:
            msg = 'Non-initialized launchpad: please run the command "lpad reset"'
            raise ConfigurationError(msg)
        self.lpad = lpad
        self.lp_path = lp_path
        self.wfe = None
        self.async_run = async_run
        self.textx_debug = False
        self.detect_duplicates = detect_duplicates
        self.logger.info('duplicate detection enabled: %s', self.detect_duplicates)
        self.tx_kwargs = {'auto_init_attributes': False, 'debug': self.textx_debug}
        if uuid is not None:
            if grammar_str or grammar_path:
                msg = 'provided grammar ignored in favor of grammar from provided uuid'
                self.logger.warning(msg)
                warnings.warn(msg, TextSUserWarning)
            match = lpad.workflows.find_one({'metadata.uuid': uuid},
                                            projection={'metadata': True})
            if match is None:
                self.logger.error('Model not found: uuid %s', uuid)
                raise ModelNotFoundError(f'uuid {uuid}')
            self.grammar_str = match['metadata']['grammar_str']
            if not isinstance(self.grammar_str, str):
                msg = 'invalid / missing grammar in model with uuid'
                self.logger.critical('Confguration error: %s %s', msg, uuid)
                raise ConfigurationError(f'{msg} {uuid}')
            self.metamodel = metamodel_from_str(self.grammar_str, **self.tx_kwargs)
            self.g_uuid = match['metadata'].get('g_uuid', None)
            wflows = list(lpad.workflows.find({'metadata.g_uuid': self.g_uuid},
                                              projection={'metadata': True}))
            self.uuids = [wfl['metadata']['uuid'] for wfl in wflows]
            assert uuid in self.uuids
            for wfl in wflows:
                schema_ver = match['metadata'].get('data_schema_version', None)
                check_compatibility(wfl['metadata']['grammar_str'], data_schema=schema_ver)
            self.models = [None]*len(self.uuids)
            self.logger.debug('loaded group with uuid %s', self.g_uuid)
            self.logger.debug('loaded group of models with uuids %s', self.uuids)
        else:
            if grammar_path:
                self.metamodel = metamodel_from_file(grammar_path, **self.tx_kwargs)
                self.grammar_str = GrammarString(grammar_path).string
            elif grammar_str:
                self.metamodel = metamodel_from_str(grammar_str, **self.tx_kwargs)
                self.grammar_str = grammar_str
            else:
                msg = 'grammar must be provided if uuid not provided'
                self.logger.error(msg)
                raise ValueError(msg)
            self.uuids = [None]
            self.models = [None]
            self.g_uuid = uuid4().hex
            self.logger.debug('creating a group with uuid %s', self.g_uuid)
            check_compatibility(self.grammar_str)
        self.modify_metamodel()
        self.autorun = autorun
        self.on_demand = on_demand
        self.unique_launchdir = wfe_kwargs.get('unique_launchdir', False)
        if uuid is None and (create_new or self.async_run):
            self.process_models('print(true)')
        if self.async_run:
            self.init_async_run(config_dir, wfe_kwargs)
        self.process_models(model_str, model_path, active_uuid=uuid)

    @property
    def uuid(self):
        """return the UUID of the first model in the group, deprecated method"""
        return self.uuids[0]

    @property
    def model(self):
        """return the first model in the group, deprecated method"""
        return self.models[0]

    def get_model(self, model_str=None, model_path=None, uuid=None):
        """the main user interface, process all models and returns one model"""
        self.process_models(model_str, model_path, active_uuid=uuid)
        if uuid is not None:
            return self.models[next(i for i, u in enumerate(self.uuids) if u == uuid)]
        return self.models[0]

    def init_async_run(self, config_dir, wfe_kwargs):
        """initialize async run using WFEngine"""
        uuids = [u for u in self.uuids if u is not None]
        wf_query = {'metadata.uuid': {'$in': uuids}}
        self.wfe = WFEngine(self.lpad, wf_query=wf_query, **wfe_kwargs)
        self.logger.info(' Started wfengine.')
        if config_dir is not None:
            self.wfe.to_file(os.path.join(config_dir, f'wfengine-{uuid4().hex}.yaml'))
        if self.on_demand:
            self.wfe.nodes_torun = []
        if self.autorun:
            self.start_runner()

    def start_runner(self):
        """a helper function to activate evaluation"""
        if self.async_run and self.wfe:
            if not (self.wfe.thread and self.wfe.thread.is_alive()):
                self.wfe.start(raise_exception=True)
                self.logger.info(' Started launcher thread.')
            self.autorun = False
        else:
            self.autorun = True

    def stop_runner(self):
        """a helper function to deactivate evaluation"""
        if self.async_run and self.wfe:
            if self.wfe.thread and self.wfe.thread.is_alive():
                self.logger.info(' Stopping launcher thread.')
                print('Stopping launcher thread, please wait ...')
                self.wfe.stop(join=True)
                self.logger.info(' Stopped launcher thread.')
        else:
            self.autorun = False

    def modify_metamodel(self):
        """add class properties, object and model processors to metamodel"""
        add_properties(self.metamodel, deferred_mode=True, workflow_mode=True)
        add_processors(self.metamodel, wflow_processors=True)

    def get_model_str(self, uuid, model_str=''):
        """updates the persistent model string with model_str"""
        fws = get_model_nodes(self.lpad, uuid)
        lines = [line for fwk in fws for line in fwk['spec']['_source_code']]
        pers_model_str = ';'.join(filter(None, list(set(lines))))
        return ';'.join(filter(None, (pers_model_str, model_str)))

    def process_models(self, model_str=None, model_path=None, active_uuid=None):
        """process all models in the group with provided single input"""
        strns, paths, varies = self._process_strings_paths(model_str, model_path)
        assert len(self.models) == len(self.uuids) == len(strns) == len(paths)
        zip_ = zip(self.models, self.uuids, strns, paths, varies)
        for index, (model, uuid, strn, path, vary) in enumerate(zip_):
            if strn or path or (model is None and uuid is not None):
                model, uuid = self._process_model(uuid, strn, path, active_uuid=active_uuid)
                self.models[index] = model
                self.uuids[index] = uuid
            if uuid is not None and vary is not None:
                update_vary(self.lpad, uuid, vary)
        if self.wfe:
            uuids = [u for u in self.uuids if u is not None]
            self.wfe.wf_query = {'metadata.uuid': {'$in': uuids}}

    def _process_strings_paths(self, model_str, model_path):
        """create the textual inputs for all models in the group"""
        if model_path:
            with open(model_path, 'r', encoding='utf-8') as inp:
                model_str = inp.read()
            model_str_ = self._expand_reuse(model_str)
            vary_objs, model_str__ = self._parse_vary(model_str_)
            if model_str__ != model_str:
                strns, varies = self._update_models(vary_objs, model_str__)
                paths = [None]*len(self.models)
            else:
                strns = [None]*len(self.models)
                paths = [model_path]*len(self.models)
                varies = [None]*len(self.models)
            return strns, paths, varies
        if model_str:
            model_str_ = self._expand_reuse(model_str)
            strns, varies = self._update_models(*self._parse_vary(model_str_))
            paths = [None]*len(self.models)
            return strns, paths, varies
        return [model_str]*len(self.models), [model_path]*len(self.models), [None]*len(self.models)

    def _expand_reuse(self, model_str):
        """insert sub-models using a reuse-type reference (varname@uuid)"""
        local_var_names = set(self._get_all_var_names())
        rule = (r"[OBJECT:TrueID|^args, statements, ~statements.names,"
                r" ~statements.variables, ~statements.~varytab.columns]")
        rule_ = r"TrueID ( '@' uuid = /[a-f\d]{32}\b/ )?"
        grammar_str = self.grammar_str.replace(rule, rule_)
        meta = metamodel_from_str(grammar_str, auto_init_attributes=False)
        full_model_str = self.get_model_str(self.uuid, model_str)
        model = meta.model_from_str(full_model_str)
        ref_objs = get_children_of_type('GeneralReference', model)
        reuse_refs = [o for o in ref_objs if o.uuid is not None]
        if len(reuse_refs) == 0:
            return model_str
        src_var_names = set()
        src_src_lines = []
        for obj in reuse_refs:
            wf_q = {'metadata.uuid': obj.uuid}
            self.logger.info('using variable \"%s\" from model %s', obj.ref, obj.uuid)
            ref_fw_ids = get_nodes_providing(self.lpad, obj.uuid, obj.ref)
            if len(ref_fw_ids) == 0:
                if self.lpad.workflows.find_one(wf_q) is None:
                    self.logger.error('Model not found: uuid %s', obj.uuid)
                    raise ModelNotFoundError(f'uuid {obj.uuid}')
                msg = f'reference {obj.ref}@{obj.uuid} could not be resolved'
                self.logger.error(msg)
                raise ReuseError(msg)
            assert len(ref_fw_ids) == 1
            ref_fw_ids.extend(get_ancestors(self.lpad, ref_fw_ids[0]))
            fw_q = {'fw_id': {'$in': ref_fw_ids}, 'spec._source_code': {'$exists': True}}
            proj = {'spec._source_code': True, 'spec._tasks.outputs': True,
                    'spec._grammar_version': True, 'spec._data_schema_version': True}
            wfl = get_nodes_info(self.lpad, wf_q, fw_q, proj)[0]
            for node in wfl['nodes']:
                grammar_ver = node['spec'].get('_grammar_version')
                schema_ver = node['spec'].get('_data_schema_version')
                check_compatibility(grammar_ver=grammar_ver, data_schema=schema_ver)
            vars_ = [v for n in wfl['nodes'] for t in n['spec']['_tasks'] for v in t['outputs']]
            if not src_var_names.isdisjoint(vars_):
                confl = src_var_names.intersection(vars_)
                msg = f'name conflicts between source models: {confl}'
                self.logger.error('Reuse error: %s', msg)
                raise ReuseError(msg)
            src_var_names.update(vars_)
            lines = [line for n in wfl['nodes'] for line in n['spec']['_source_code']]
            src_src_lines.extend(lines)
            fw_q = {'name': '_fw_meta_node'}
            proj = {'spec._source_code': True}
            info_meta = get_nodes_info(self.lpad, wf_q, fw_q, proj)[0]
            assert len(info_meta['nodes']) == 1
            src_src_lines.extend(info_meta['nodes'][0]['spec']['_source_code'])
        self.logger.debug('extracted lines of code: %s', src_src_lines)
        self.logger.info('reused variables: %s', src_var_names)
        self.logger.debug('local variables: %s', local_var_names)
        if not local_var_names.isdisjoint(src_var_names):
            confl = local_var_names.intersection(src_var_names)
            msg = f'name conflicts between source and target models: {confl}'
            self.logger.error('Reuse error: %s', msg)
            raise ReuseError(msg)
        len_pers_model = len(full_model_str) - len(model_str)
        model_str_new = str(model_str)
        for obj in reversed(reuse_refs):
            beg = getattr(obj, '_tx_position') - len_pers_model
            end = getattr(obj, '_tx_position_end') - len_pers_model
            model_str_new = model_str_new[:beg] + obj.ref + model_str_new[end:]
        return ';'.join(filter(None, [model_str_new]+list(set(src_src_lines))))

    def get_vary_df(self):
        """reconstruct the persistent vary statement and return as dataframe"""
        if all(u is None for u in self.uuids):
            varies = [pandas.DataFrame()]*len(self.uuids)
        else:
            assert not any(u is None for u in self.uuids)
            wf_query = {'metadata.uuid': {'$in': self.uuids}}
            fw_query = {'name': '_fw_meta_node', 'spec._vary': {'$exists': True}}
            fw_proj = {'spec._vary': True}
            info = get_nodes_info(self.lpad, wf_query, fw_query, fw_proj)
            assert len(info) == len(self.uuids)
            varies = []
            for uuid in self.uuids:
                nodes = next(d['nodes'] for d in info if d['metadata']['uuid'] == uuid)
                if nodes:
                    assert len(nodes) == 1
                    varies.append(load_object(nodes[0]['spec']['_vary']))
                else:
                    varies.append(pandas.DataFrame())
        df_old = pandas.concat(varies)
        if len(df_old) > 0:
            assert len(df_old) == len(self.uuids)
        df_old['%uuid'] = self.uuids
        self.logger.debug('vary from persistence: %s', formatter(df_old))
        df_old.reset_index(drop=True, inplace=True)
        return df_old

    def _get_all_var_names(self):
        """return the names of all variables in the first persistent model"""
        if all(u is None for u in self.uuids):
            return set()
        wf_q = {'metadata.uuid': next(u for u in self.uuids if u is not None)}
        fw_q = {'spec._source_code': {'$exists': True},
                'spec._tasks.outputs': {'$exists': True}}
        proj = {'spec._tasks.outputs': True}
        nodes = get_nodes_info(self.lpad, wf_q, fw_q, proj)[0]['nodes']
        names = (o for n in nodes for t in n['spec']['_tasks'] for o in t['outputs'])
        return set(names)

    def _get_var_values(self, var_names):
        """return the values of the specified variables in all persistent models"""
        wf_q = {'metadata.uuid': {'$in': self.uuids}}
        fw_q = {'spec._source_code': {'$exists': True},
                'spec._tasks.outputs': {'$in': list(var_names)}}
        proj = {'spec._source_code': True}
        info = get_nodes_info(self.lpad, wf_q, fw_q, proj)
        metamodel = metamodel_from_str(self.grammar_str, **self.tx_kwargs)
        add_properties(metamodel, deferred_mode=False, workflow_mode=False)
        add_processors(metamodel, wflow_processors=False, io_processors=False)
        dfr = pandas.DataFrame()
        for uuid in self.uuids:
            nodes = next(d.get('nodes') for d in info if d['metadata']['uuid'] == uuid)
            lines = [line for n in nodes for line in n['spec']['_source_code']]
            model_str = ';'.join(filter(None, list(set(lines))))
            try:
                model = metamodel.model_from_str(model_str, deferred_mode=False)
            except TextXSemanticError as err:
                msg = 'only literals may be used in vary statements'
                self.logger.error(msg)
                raise VaryError(msg) from err
            var_l = get_children_of_type('Variable', model)
            lst = []
            for var_n in var_names:
                var_v = next(v for v in var_l if v.name == var_n).value
                dtype = None
                if isinstance(var_v, pint.Quantity):
                    dtype = PintType(var_v.units)
                    var_v = var_v.magnitude
                lst.append(pandas.Series(var_v, name=var_n, dtype=dtype))
            dfr = pandas.concat([dfr, pandas.concat(lst, axis='columns')])
            dfr.reset_index(drop=True, inplace=True)
        return dfr

    def _update_models(self, vary, model_str):
        """update the source code according to the information in vary"""
        if len(vary) == 0:
            return [model_str]*len(self.models), [None]*len(self.models)
        df_old = self.get_vary_df()
        df_old_names = set(df_old.drop(columns=['%uuid']).columns)
        vary_names = set(c for v in vary for c in v.varytab.value.columns)
        non_vary_names = self._get_all_var_names() - df_old_names
        extra_var_names = vary_names.intersection(non_vary_names)
        if len(extra_var_names) > 0:
            self.logger.info('extra vars found in vary statement: %s', extra_var_names)
            df_extra_vars = self._get_var_values(extra_var_names)
            self.logger.debug('extra vars: %s', formatter(df_extra_vars))
            df_old = pandas.concat([df_old, df_extra_vars], axis='columns')
            df_old.reset_index(drop=True, inplace=True)
            df_old_names = df_old_names.union(extra_var_names)
            self.logger.debug('vary with extra vars: %s', formatter(df_old))
        if not vary_names.issubset(df_old_names):
            if not vary_names.isdisjoint(df_old_names):
                msg = 'either existing or new variables allowed in vary, not both'
                self.logger.error(msg)
                raise VaryError(msg)
            # only new variables
            return self._update_models_new_vars(vary, df_old, model_str)
        # only old variables
        if df_old_names != vary_names:
            missing = df_old_names - vary_names
            msg = f'missing variables in vary: {missing}'
            self.logger.error(msg)
            raise VaryError(msg)
        return self._update_models_old_vars(vary, df_old, model_str)

    def _update_models_new_vars(self, vary, df_old, model_str):
        """strns: updated models strings, varies: updated vary dataframes"""
        df_norm = vary[0].varytab.value
        for var in vary[1:]:
            df_norm = df_norm.join(var.varytab.value, how='cross')
        self.logger.debug('Vary from extension: %s', formatter(df_norm))
        df_update = df_old.join(df_norm.drop_duplicates(), how='cross')
        self.logger.debug('Updated vary: %s', formatter(df_update))
        strns = []
        varies = []
        self.uuids = []
        self.models = []
        known_ids = set()
        for ind, row in df_update.iterrows():
            row_dct = dict(row)
            upd = {k: v for k, v in row_dct.items() if k in df_norm.columns}
            src = '; '.join(' = '.join([k, formatter(v)]) for k, v in upd.items())
            if row_dct['%uuid'] not in known_ids:
                known_ids.add(row_dct['%uuid'])
                uuid = row_dct['%uuid']
                src_update = ';'.join(filter(None, (model_str, src)))
                self.logger.debug('Source added to model %s: %s', uuid, src_update)
            else:
                uuid = None
                src_new = self.get_model_str(row_dct['%uuid'], src)
                src_update = ';'.join(filter(None, (model_str, src_new)))
                self.logger.debug('Source added to a new model: %s', src_update)
            strns.append(src_update)
            vary_df = df_update.drop(columns=['%uuid']).iloc[[ind]]
            self.logger.debug('Updated vary for model %s: %s', uuid, formatter(vary_df))
            varies.append(vary_df)
            self.uuids.append(uuid)
            self.models.append(None)
        return strns, varies

    def _update_models_old_vars(self, vary, df_old, model_str):
        """strns: updated models strings, varies: updated vary dataframes"""
        assert len(self.models) == len(self.uuids) == len(df_old)
        df_old.drop(columns='%uuid', inplace=True)
        df_norm = pandas.concat(v.varytab.value for v in vary).drop_duplicates()
        df_norm_types = get_dfr_types(df_norm)
        df_old_types = get_dfr_types(df_old)
        self.logger.debug('df_norm_types: %s', df_norm_types)
        self.logger.debug('df_old_types: %s', df_old_types)
        if df_norm_types != df_old_types:
            msg = f'type mismatch in vary: {df_norm_types} vs. {df_old_types}'
            self.logger.error(msg)
            raise VaryError(msg)
        for col in df_norm.columns:
            upd_units = get_units(df_norm[col])
            old_units = get_units(df_old[col])
            if upd_units != old_units:
                msg = f'mismatching units for {col}: {upd_units} vs. {old_units}'
                self.logger.error(msg)
                raise VaryError(msg)
        # start removing duplicated rows comparing to old vary dataframe
        df_aux = pandas.merge(df_norm, df_old, on=list(df_norm.columns), how='inner')
        df_norm = pandas.concat([df_norm, df_aux])
        df_norm['duplicated'] = df_norm.duplicated(keep=False)
        df_norm = df_norm[~df_norm['duplicated']]
        del df_norm['duplicated']
        df_norm.reset_index(drop=True, inplace=True)
        # end removing duplicated rows
        self.logger.debug('Vary from extension: %s', formatter(df_norm))
        old_vary_vars = list(df_old.columns)
        assert self.uuids[0] is not None
        nodes = get_nodes_info(self.lpad, {'metadata.uuid': self.uuids[0]},
                               {'spec._source_code': {'$exists': True},
                                'spec._tasks.outputs': {'$nin': old_vary_vars}},
                               {'spec._source_code': True})[0]['nodes']
        lines = [line for n in nodes for line in n['spec']['_source_code']]
        pers_model_str = ';'.join(filter(None, list(set(lines))))
        strns = [model_str]*len(self.models)
        varies = [df_old.iloc[[ind]] for ind, _ in df_old.iterrows()]
        for ind, row in df_norm.iterrows():
            src = '; '.join(' = '.join([k, formatter(v)]) for k, v in dict(row).items())
            src_update = ';'.join(filter(None, [pers_model_str, src, model_str]))
            self.logger.debug('Source added to a new model: %s', src_update)
            strns.append(src_update)
            varies.append(df_norm.iloc[[ind]])
            self.models.append(None)
            self.uuids.append(None)
        self.logger.debug('New vary information: %s', formatter(varies))
        return strns, varies

    def _parse_vary(self, model_str):
        """parse the full model, collect and remove the vary statements"""
        meta = metamodel_from_str(self.grammar_str, auto_init_attributes=False)
        add_properties(meta)
        add_obj_processors(meta, wflow_processors=True)
        meta.register_model_processor(vary_model_processor)
        full_model_str = self.get_model_str(self.uuid, model_str)
        model = meta.model_from_str(full_model_str)
        if textx_isinstance(model, meta['Program']):
            vary_statements = []
            for obj in model.statements:
                if textx_isinstance(obj, meta['Vary']):
                    vary_statements.append(obj)
            if vary_statements:
                fws = get_model_nodes(self.lpad, self.uuid)
                pers_model_lst = [s for f in fws for s in f['spec']['_source_code']]
                statements = []
                for obj in model.statements:
                    if not textx_isinstance(obj, meta['Vary']):
                        obj_src = get_object_str(full_model_str, obj)
                        if obj_src not in pers_model_lst:
                            statements.append(obj_src)
                return vary_statements, ';'.join(filter(None, statements))
        return [], model_str

    def _get_src_model(self, uuid, model_str, model_path):
        """evaluate textx function, model str/path and source code"""
        if model_str:
            tx_get_model = self.metamodel.model_from_str
            model_src = self.get_model_str(uuid, model_str)
            source_code = model_src
        elif model_path:
            with open(model_path, 'r', encoding='utf-8') as inp:
                model_str = inp.read()
            if uuid is not None:
                tx_get_model = self.metamodel.model_from_str
                model_src = self.get_model_str(uuid, model_str)
                source_code = model_src
            else:
                tx_get_model = self.metamodel.model_from_file
                model_src = model_path
                source_code = model_str
        else:
            tx_get_model = self.metamodel.model_from_str
            model_src = self.get_model_str(uuid)
            source_code = model_src
        return tx_get_model, model_src, source_code

    def _process_model(self, uuid, strn, path, active_uuid=None):
        """create a new textx model instance if model_str/model_path supplied"""
        tx_get_model, model_src, source_code = self._get_src_model(uuid, strn, path)
        model_instance = {'lpad': self.lpad, 'uuid': uuid, 'g_uuid': self.g_uuid,
                          'lp_path': self.lp_path}
        autorun_od = not (self.on_demand and active_uuid and uuid != active_uuid)
        autorun = self.autorun and autorun_od
        model = tx_get_model(model_src, deferred_mode=True,
                             model_instance=model_instance,
                             source_code=source_code,
                             grammar_str=self.grammar_str,
                             autorun=autorun,
                             on_demand=self.on_demand,
                             detect_duplicates=self.detect_duplicates,
                             debug=self.textx_debug,
                             unique_launchdir=self.unique_launchdir)
        if not textx_isinstance(model, self.metamodel['Program']):
            model = None
        elif self.wfe and self.on_demand and autorun_od:
            self.logger.info(' Setting nodes to run on demand.')
            nodes_to_run = list(set(self.wfe.nodes_torun+model.fw_ids_torun))
            self.logger.debug(' Nodes to run: %s', nodes_to_run)
            self.wfe.nodes_torun = nodes_to_run
        return model, getattr(model, 'uuid', uuid)
