"""
tests with computing resources
"""
import os
import pytest
from textx import get_children_of_type
from textx.exceptions import TextXError, TextXSyntaxError
from virtmat.middleware.resconfig import get_resconfig_loc
from virtmat.middleware.exceptions import ResourceConfigurationError
from virtmat.language.constraints.units import InvalidUnitError
from virtmat.language.utilities.errors import StaticValueError, ConfigurationError


def test_number_of_chunks(meta_model_wf, model_kwargs_wf):
    """test a map function with an input in two chunks"""
    prog_inp = 'a = map((x: x**2), b) in 2 chunks; b = (numbers: 1, 2)'
    meta_model_wf.model_from_str(prog_inp, **model_kwargs_wf)


def test_negative_number_of_chunks(meta_model_wf, model_kwargs_wf):
    """test a map function with an input with negative number of chunks"""
    prog_inp = 'a = map((x: x**2), b) in -2 chunks; b = (numbers: 1, 2)'
    msg = 'number of chunks must be a positive integer number'
    with pytest.raises(TextXError, match=msg):
        meta_model_wf.model_from_str(prog_inp, **model_kwargs_wf)


def test_invalid_number_of_chunks_spec(meta_model_wf, model_kwargs_wf):
    """test a map function with an input with invalid number of chunks spec"""
    prog_inp = 'a = map((x: x**2), b) in two chunks; b = (numbers: 1, 2)'
    with pytest.raises(TextXSyntaxError, match='Expected INT'):
        meta_model_wf.model_from_str(prog_inp, **model_kwargs_wf)


def test_resources_interpreter(meta_model_wf, model_kwargs_wf, _res_config_loc):
    """test the interpreter with specifications of computing resources"""
    prog_inp = ('a = map((x: x**2), (numbers: 1, 2)) on 1 core with 3 [GB] '
                'for 1.0 [hour]')
    prog = meta_model_wf.model_from_str(prog_inp, **model_kwargs_wf)
    var_list = get_children_of_type('Variable', prog)
    var_a = next(v for v in var_list if v.name == 'a')
    fw_ids = prog.lpad.get_fw_ids({'name': var_a.fireworks[0].name})
    assert len(fw_ids) == 1
    fw_spec = prog.lpad.get_fw_by_id(fw_ids[0]).spec
    assert '_category' in fw_spec
    assert fw_spec['_category'] == 'batch'
    assert '_queueadapter' in fw_spec
    qadapter = fw_spec['_queueadapter']
    assert qadapter.q_name == 'test_q'
    assert qadapter['walltime'] == 60
    assert qadapter['nodes'] == 1
    assert qadapter['ntasks_per_node'] == 1
    assert qadapter['mem_per_cpu'] == '3GB'


def test_resources_exceed_limits(meta_model_wf, model_kwargs_wf, _res_config_loc):
    """test resource specifications that exceed limits"""
    prog_inp = 'a = 1 on 20 cores with 3 [TB] for 168.0 [hours]'
    msg = ("no matching resources {'mem_per_cpu': 3000000.0, 'walltime': 10080,"
           " 'ncores': 20}")
    with pytest.raises(TextXError, match=msg) as err:
        meta_model_wf.model_from_str(prog_inp, **model_kwargs_wf)
    assert isinstance(err.value.__cause__, StaticValueError)


def test_parallel_map(meta_model_wf, model_kwargs_wf):
    """test parallel map"""
    prog_inp = ('a = (n: 1, 2, 3, 4);'
                'b = map((x: x**2), a) in 2 chunks; print(b)')
    prog = meta_model_wf.model_from_str(prog_inp, **model_kwargs_wf)
    assert prog.value == '(b: 1, 4, 9, 16)'


def test_parallel_filter(meta_model_wf, model_kwargs_wf):
    """test parallel filter"""
    prog_inp = ('a = (lengths: 1, 2, 3, 4) [meter];'
                'b = filter((x: x > 1 [m]), a) in 5 chunks; print(b)')
    prog = meta_model_wf.model_from_str(prog_inp, **model_kwargs_wf)
    assert prog.value == '(b: 2, 3, 4) [meter]'


def test_parallel_reduce(meta_model_wf, model_kwargs_wf):
    """test parallel reduce"""
    prog_inp = ('a = (times: 1, 2, 3, 4) [seconds];'
                's = reduce((x, y: x + y), a) in 2 chunks; print(s)')
    prog = meta_model_wf.model_from_str(prog_inp, **model_kwargs_wf)
    assert prog.value == '10 [second]'


def test_parallelization_error_map_param(meta_model_wf, model_kwargs_wf):
    """test map parallelization error: parameter not reference type """
    prog_inp = 'f = map((x: x**2), (numbers: 1, 2)) in 2 chunks'
    msg = 'parallel map parameters must be references'
    with pytest.raises(TextXError, match=msg):
        meta_model_wf.model_from_str(prog_inp, **model_kwargs_wf)


def test_parallelization_error_filter_param(meta_model_wf, model_kwargs_wf):
    """test filter parallelization error: parameter not reference type"""
    prog_inp = 'f = filter((x: x>1), (numbers: 1, 2)) in 2 chunks'
    msg = 'parameter must be a reference'
    with pytest.raises(TextXError, match=msg):
        meta_model_wf.model_from_str(prog_inp, **model_kwargs_wf)


def test_parallelization_error_print_parent(meta_model_wf, model_kwargs_wf):
    """test parallelization error: map parent is print"""
    prog_inp = 'a = (n: 1, 2); print(map((x: x**2), a) in 2 chunks)'
    msg = 'Parallel map, filter and reduce must be variable parameters'
    with pytest.raises(TextXError, match=msg):
        meta_model_wf.model_from_str(prog_inp, **model_kwargs_wf)


def test_parallelization_error_filter_parent(meta_model_wf, model_kwargs_wf):
    """test parallelization error: map parent is filter"""
    prog_inp = 'a = (n: 1); b = filter((x: x>1), map((x: x**2), a) in 2 chunks)'
    msg = 'Parallel map, filter and reduce must be variable parameters'
    with pytest.raises(TextXError, match=msg):
        meta_model_wf.model_from_str(prog_inp, **model_kwargs_wf)


def test_parallelization_error_large_nchunks(meta_model_wf, model_kwargs_wf):
    """test parallelization error: reduce with nchunks > elements"""
    prog_inp = 'a = (n: 1, 2); b = reduce((x, y: x+y), a) in 3 chunks; print(b)'
    msg = 'Evaluation of b not possible due to failed ancestors'
    prog = meta_model_wf.model_from_str(prog_inp, **model_kwargs_wf)
    var = next(v for v in get_children_of_type('Variable', prog) if v.name == 'b')
    with pytest.raises(TextXError, match=msg):
        print(var.value)


def test_units_in_resources(meta_model_wf, model_kwargs_wf, _res_config_loc):
    """test units in resources specifications"""
    prog_inp = ('b = (numbers: 1, 2); a = map((x: x**2), b) on 1 core '
                'with 3 [GB] for 1.0 [hour]')
    meta_model_wf.model_from_str(prog_inp, **model_kwargs_wf)


def test_default_worker_name(meta_model_wf, model_kwargs_wf, _res_config_loc):
    """test default worker name with resconfig"""
    prog_inp = 'b = (numbers: 1, 2) on 1 core with 3 [GB] for 1.0 [hour]'
    prog = meta_model_wf.model_from_str(prog_inp, **model_kwargs_wf)
    assert prog.worker_name == 'test_w'


@pytest.mark.skipif(os.path.exists(get_resconfig_loc()),
                    reason='resconfig exists outside of test environment')
def test_resources_without_resconfig(meta_model_wf, model_kwargs_wf):
    """test default worker name without resconfig"""
    prog_inp = 'b = (numbers: 1, 2) on 1 core with 3 [GB] for 1.0 [hour]'
    msg = 'Resource configuration file not found.'
    with pytest.raises(TextXError, match=msg) as err:
        meta_model_wf.model_from_str(prog_inp, **model_kwargs_wf)
    assert isinstance(err.value.__cause__, ResourceConfigurationError)


def test_units_in_resources_invalid_memory_unit(meta_model_wf, model_kwargs_wf):
    """test units in resources specifications with invalid memory unit"""
    prog_inp = ('b = (numbers: 1, 2); a = map((x: x**2), b) on 1 core '
                'with 3.5 [meters] for 1 [hour]')
    with pytest.raises(TextXError) as err_info:
        meta_model_wf.model_from_str(prog_inp, **model_kwargs_wf)
    assert isinstance(err_info.value.__cause__, InvalidUnitError)
    assert 'invalid unit of memory: meters' in str(err_info)


def test_units_in_resources_invalid_time_unit(meta_model_wf, model_kwargs_wf):
    """test units in resources specifications with invalid memory unit"""
    prog_inp = ('b = (numbers: 1, 2); a = map((x: x**2), b) on 1 core '
                'with 1.1 [TB] for 2.0 [kg]')
    with pytest.raises(TextXError) as err_info:
        meta_model_wf.model_from_str(prog_inp, **model_kwargs_wf)
    assert isinstance(err_info.value.__cause__, InvalidUnitError)
    assert 'invalid unit of walltime: kg' in str(err_info)


def test_batch_evaluation_with_mongomock(meta_model_wf, model_kwargs_wf,
                                         _res_config_loc, _mongomock_setup):
    """test refusing adding nodes for batch evaluation with mongomock"""
    prog_inp = 'b = (numbers: 1, 2) on 1 core for 1.0 [hour]'
    msg = 'cannot add statements for batch evaluation with Mongomock'
    with pytest.raises(ConfigurationError, match=msg):
        meta_model_wf.model_from_str(prog_inp, **model_kwargs_wf)
