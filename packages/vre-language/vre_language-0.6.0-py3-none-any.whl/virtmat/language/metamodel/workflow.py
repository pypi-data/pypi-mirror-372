"""processors to set attributes necessary for the workflow executor"""
import math
from textx import get_children_of_type, textx_isinstance
from virtmat.middleware.resconfig import get_qadapter, get_worker_get_queue
from virtmat.middleware.resconfig import get_default_resconfig
from virtmat.middleware.resconfig.qadapter import get_pre_rocket
from virtmat.middleware.exceptions import ResourceConfigurationError
from virtmat.language.utilities.dupefinder import DupeFinderFunctionTask
from virtmat.language.utilities.errors import raise_exception, textxerror_wrap
from virtmat.language.utilities.errors import StaticValueError
from virtmat.language.utilities.units import norm_mem
from virtmat.language.utilities.textx import get_reference, get_object_str
from virtmat.language.utilities.textx import isinstance_m
from virtmat.language.utilities.logging import get_logger
from virtmat.language.constraints.units import check_number_literal_units
from virtmat.language.constraints.values import check_resources_values
from virtmat.language.constraints.values import check_number_of_chunks


def get_config_nodes(ncores, **kwargs):
    """return first matching worker and queue in resconfig"""
    # use only 'ntasks_per_node', 'mem_per_cpu', 'nodes', 'walltime'
    res = kwargs.copy()
    for nodes in range(1, ncores+1):
        res['nodes'] = nodes
        res['ntasks_per_node'] = math.ceil(ncores/nodes)
        wcfg, qcfg = get_worker_get_queue(**res)
        if wcfg and qcfg:
            return wcfg, qcfg, nodes
    kwargs['ncores'] = ncores
    raise StaticValueError(f'no matching resources {kwargs}')


@textxerror_wrap
def set_compute_resources(obj):
    """Set resource requirements and worker_name in Resources object (obj)"""
    cpus_per_task = 1  # currently only single-threaded tasks supported
    obj.ncores = obj.ncores or 1
    memory_mb = obj.memory.value.to('megabyte').magnitude if obj.memory else 1
    res = {'mem_per_cpu': memory_mb}
    if obj.walltime:
        res['walltime'] = int(obj.walltime.value.to('minutes').magnitude)
    obj.wcfg, obj.qcfg, nodes = get_config_nodes(obj.ncores, **res)
    obj.worker_name = obj.wcfg.name

    obj.compres = {}
    obj.compres['nodes'] = nodes
    if obj.walltime:
        obj.compres['walltime'] = int(obj.walltime.value.to('minutes').magnitude)
    if obj.memory:
        mem = norm_mem(obj.memory.value)
        obj.compres['mem_per_cpu'] = f'{mem[0]}{mem[1]}'
    # if cpus_per_task > 1:
    #    obj.compres['cpus_per_task'] = cpus_per_task
    if obj.ncores % nodes > 0:
        assert obj.ncores % cpus_per_task == 0
        obj.compres['ntasks'] = obj.ncores // cpus_per_task
    else:
        obj.compres['ntasks_per_node'] = obj.ncores // nodes


def resources_processor(obj):
    """Apply unit constraints to Resources object (obj) attributes and then set
    category and qadapter attributes in the Resources object"""
    for attr, unit in (('memory', 'bit'), ('walltime', 'second')):
        number = getattr(obj, attr)
        if number is not None:
            check_number_literal_units(number, attr, unit)
    check_resources_values(obj)
    set_compute_resources(obj)
    obj.qadapter = None


def parallelizable_processor(obj):
    """Processors for parallelizable objects"""
    check_number_of_chunks(obj)


@textxerror_wrap
def default_worker_name_processor(model, _):
    """set the default worker name for the model"""
    if not isinstance(model, str):
        cfg = get_default_resconfig()
        if cfg and cfg.default_worker:
            worker_name = cfg.default_worker.name
        else:
            worker_name = 'local'
        setattr(model, 'worker_name', worker_name)


def source_code_statement_processor(model, _):
    """add source code lines pertinent to the variable objects in the model"""
    if not isinstance(model, str):
        p_src = getattr(model, '_tx_model_params').get('source_code')
        dupli = getattr(model, '_tx_model_params').get('detect_duplicates')
        for obj in get_children_of_type('Variable', model):
            o_src = [get_object_str(p_src, obj)] if p_src else []
            setattr(obj, 'source_code', o_src)
            if dupli and len(o_src) > 0:
                setattr(obj, 'dupefinder', DupeFinderFunctionTask())
        for statement in ['ObjectImports', 'FunctionDefinition', 'ObjectTo']:
            for obj in get_children_of_type(statement, model):
                o_src = [get_object_str(p_src, obj)] if p_src else []
                setattr(obj, 'source_code', o_src)


def qadapter_processor(model, metamodel):
    """creates qadapter for the required resources"""
    for res in get_children_of_type('Resources', model):
        assert isinstance_m(res.parent, ['Variable', 'VariableUpdate'])
        if textx_isinstance(res.parent.parameter, metamodel['AMMLProperty']):
            if res.parent.parameter.calc:
                calc = get_reference(res.parent.parameter.calc)
                assert textx_isinstance(calc, metamodel['AMMLCalculator'])
                try:
                    get_pre_rocket(res.wcfg, **calc.resources)
                except ResourceConfigurationError as err:
                    raise_exception(calc, ResourceConfigurationError, str(err))
                res.compres.update(calc.resources)
        model_instance = getattr(model, '_tx_model_params')['model_instance']
        if model_instance.get('lp_path'):
            res.compres['lp_file'] = model_instance.get('lp_path')
        res.qadapter = get_qadapter(res.wcfg, res.qcfg, **res.compres)


def variable_update_processor(model, metamodel):
    """process variable update objects"""
    if not textx_isinstance(model, metamodel['Program']):
        return
    mod_vars = get_children_of_type('VariableUpdate', model)
    logger = get_logger(__name__)
    p_src = getattr(model, '_tx_model_params').get('source_code')
    dupli = getattr(model, '_tx_model_params').get('detect_duplicates')
    for mod_var in mod_vars:
        logger.info(' updating variable: %s', mod_var.ref.name)
        setattr(mod_var.ref, '_update', True)
        mod_var.name = mod_var.ref.name
        mod_var.ref.parameter = mod_var.parameter
        mod_var.ref.resources = mod_var.resources
        if p_src:
            old_src = mod_var.ref.source_code
            param_src = get_object_str(p_src, mod_var.parameter)
            new_src = f'{mod_var.ref.name} = {param_src}'
            if mod_var.resources:
                new_src = f'{new_src} {get_object_str(p_src, mod_var.resources)}'
            new_src = [new_src]
            setattr(mod_var.ref, 'source_code', new_src)
            logger.info(' updating variable source code: %s -> %s', old_src, new_src)
            if dupli:
                setattr(mod_var.ref, 'dupefinder', DupeFinderFunctionTask())
