"""
tests for recursive functions
"""
import pytest
from textx import get_children_of_type
from textx import textx_isinstance
from virtmat.language.metamodel.properties import add_properties
from virtmat.language.constraints.functions import check_function_call


@pytest.fixture(name='meta_model')
def fixture_metamodel(raw_meta_model):
    """parse the grammar and generate the object classes"""
    add_properties(raw_meta_model)
    return raw_meta_model


def test_function_call_if_function_recursion(meta_model):
    """test function call with if-function recursion"""
    prog_inp = 'gt(x, y) = if(x>y, gt(x, y), x)\n'
    prog = meta_model.model_from_str(prog_inp)
    funcs = get_children_of_type('FunctionDefinition', prog)
    calls = get_children_of_type('FunctionCall', prog)
    assert len(funcs) == 1
    assert textx_isinstance(calls[0].parent, meta_model['IfFunction'])
    assert len(calls[0].params) == len(funcs[0].args)
    assert len(calls[0].params) == 2
    check_function_call(calls[0], meta_model)


def test_recursive_function_call_two_arguments(meta_model):
    """test recursive function call with two arguments"""
    prog_inp = 'a = pow(2, 3); pow(x, n) = if(n>0, x*pow(x, n-1), 1)\n'
    prog = meta_model.model_from_str(prog_inp)
    func_defs = get_children_of_type('FunctionDefinition', prog)
    assert len(func_defs) == 1
    calls = get_children_of_type('FunctionCall', prog)
    for call in calls:
        check_function_call(call, meta_model)
        assert (textx_isinstance(call.parent, meta_model['Variable']) or
                textx_isinstance(call.parent, meta_model['Operand']))
