"""
tests for object imports
"""
import pytest
from textx import get_children_of_type
from textx import textx_isinstance
from textx.exceptions import TextXError, TextXSyntaxError
from virtmat.language.constraints.imports import ObjectImportError
from virtmat.language.constraints.imports import NonCallableImportError
from virtmat.language.utilities.typemap import typemap
from virtmat.language.utilities.errors import RuntimeTypeError


def test_function_import_two_arguments_import_error(meta_model, model_kwargs):
    """test failing function import due to invalid namespace"""
    prog_inp = 'use stdlib.log10\n'
    with pytest.raises(ObjectImportError,
                       match='Object could not be imported'):
        meta_model.model_from_str(prog_inp, **model_kwargs)


def test_function_import_two_arguments_attribute_error(meta_model, model_kwargs):
    """test failing function import due to invalid name"""
    prog_inp = 'use math.log1\n'
    with pytest.raises(ObjectImportError,
                       match='Object could not be imported'):
        meta_model.model_from_str(prog_inp, **model_kwargs)


def test_function_import_two_arguments(meta_model, model_kwargs):
    """test function import with two arguments"""
    prog_inp = 'use math.log10\n'
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    func_imports = get_children_of_type('ObjectImport', prog)
    assert len(func_imports) == 1
    assert func_imports[0].namespace == ['math']
    assert func_imports[0].name == 'log10'


def test_imported_function_call(meta_model, model_kwargs):
    """test imported function call"""
    prog_inp = 'use sqrt from my.stdlib; a = sqrt(2)\n'
    with pytest.raises(ObjectImportError,
                       match='Object could not be imported: "my.stdlib.sqrt"'):
        meta_model.model_from_str(prog_inp, **model_kwargs)


def test_imported_function_call_value(meta_model, model_kwargs):
    """test call value of imported function"""
    prog_inp = 'use math.exp; use math.log; a = exp(1.0); b = 1 - log(a)\n'
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    funcs = get_children_of_type('ObjectImport', prog)
    assert len(funcs) == 2
    calls = get_children_of_type('FunctionCall', prog)
    assert len(calls) == 2
    exp_func_call = next(v for v in calls if v.function.name == 'exp')
    assert exp_func_call.type_ is None
    assert exp_func_call.value == pytest.approx(2.718281828459045)
    assert textx_isinstance(exp_func_call.parent, meta_model['Variable'])
    log_func_call = next(v for v in calls if v.function.name == 'log')
    assert issubclass(log_func_call.type_, typemap['Quantity'])
    assert log_func_call.type_.datatype is None
    assert log_func_call.value == pytest.approx(1.0)
    assert textx_isinstance(log_func_call.parent, meta_model['Operand'])
    var_list = get_children_of_type('Variable', prog)
    var_a = next(v for v in var_list if v.name == 'a')
    assert var_a.type_ is None  # unbound type because type of exp unknown
    var_b = next(v for v in var_list if v.name == 'b')
    assert issubclass(var_b.type_, typemap['Quantity'])
    assert var_b.type_.datatype is None  # bound to number for log type unknown
    assert var_b.value == pytest.approx(0.0)


def test_imported_function_call_value_boolean(meta_model, model_kwargs):
    """test call value of imported function returning boolean"""
    prog_inp = 'use isclose from math; b = not isclose(1.0, 0.0)\n'
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    funcs = get_children_of_type('ObjectImport', prog)
    assert len(funcs) == 1
    calls = get_children_of_type('FunctionCall', prog)
    assert len(calls) == 1
    isclose_func_call = next(v for v in calls if v.function.name == 'isclose')
    assert issubclass(isclose_func_call.type_, bool)  # because in boolean expression
    assert isclose_func_call.value is False
    assert textx_isinstance(isclose_func_call.parent, meta_model['BooleanOperand'])
    var_list = get_children_of_type('Variable', prog)
    var_b = next(v for v in var_list if v.name == 'b')
    assert issubclass(var_b.type_, bool)
    assert var_b.value is True


def test_non_callable_object_import(meta_model, model_kwargs):
    """test non-callable object import"""
    prog_inp = 'use math.pi\n'
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    objs = get_children_of_type('ObjectImport', prog)
    assert len(objs) == 1
    assert objs[0].value == pytest.approx(3.141592653589793)


def test_non_callable_object_import_call_error(meta_model, model_kwargs):
    """test non-callable object import call error"""
    prog_inp = 'use math.pi; a = pi(3)\n'
    with pytest.raises(NonCallableImportError, match='Imported object is not callable'):
        meta_model.model_from_str(prog_inp, **model_kwargs)


def test_non_callable_object_import_assignment(meta_model, model_kwargs):
    """test non-callable object import with assignment"""
    prog_inp = 'use math.pi; a = pi\n'
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    imports = get_children_of_type('ObjectImport', prog)
    assert len(var_list) == 1
    assert len(imports) == 1
    assert textx_isinstance(var_list[0].parameter, meta_model['GeneralReference'])
    assert var_list[0].parameter.ref == imports[0]
    var_list = get_children_of_type('Variable', prog)
    assert len(var_list) == 1
    var_a = next(v for v in var_list if v.name == 'a')
    assert issubclass(var_a.type_, typemap['Quantity'])  # non-callable import has known type
    assert issubclass(var_a.type_.datatype, float)  # non-callable import has known type
    assert var_a.value == pytest.approx(3.141592653589793)


def test_non_callable_object_import_in_expressions(meta_model, model_kwargs):
    """test non-callable object import in expressions"""
    prog_inp = 'use pi from math; a = 2*pi; b = (0 < pi) and (pi >= 3.)\n'
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    var_a = next(v for v in var_list if v.name == 'a')
    assert issubclass(var_a.type_, typemap['Quantity'])
    assert issubclass(var_a.type_.datatype, float)
    assert var_a.value == pytest.approx(2*3.141592653589793)
    var_b = next(v for v in var_list if v.name == 'b')
    assert issubclass(var_b.type_, bool)
    assert var_b.value is True


def test_repeated_initialization_of_imports(meta_model, model_kwargs):
    """test repeated initialization of object import and imported function"""
    prog_inps = ['use math.pi; pi = 4', 'use math.log; log = 2']
    for inp, var in zip(prog_inps, ('pi', 'log')):
        with pytest.raises(TextXError, match=f'Repeated initialization of "{var}"'):
            meta_model.model_from_str(inp, **model_kwargs)


def test_import_with_missing_namespace(meta_model, model_kwargs):
    """test import with missing namespace should produce syntax error"""
    with pytest.raises(TextXSyntaxError):
        meta_model.model_from_str('use log', **model_kwargs)


def test_callable_import_type_error(meta_model, model_kwargs):
    """test a callable import calling with wrong type"""
    inp = 'use len from builtins; a = len(1)'
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    var_a = next(v for v in var_list if v.name == 'a')
    with pytest.raises(TextXError, match='') as err:
        _ = var_a.value
    assert isinstance(err.value.__cause__, RuntimeTypeError)


def test_evaluate_callable_import_type_error(meta_model, model_kwargs):
    """test evaluate callable import type error"""
    inp = 'use len from builtins; a = len + 1; print(a)'
    msg = 'callable import <built-in function len> has no value'
    with pytest.raises(TextXError, match=msg) as err:
        prog = meta_model.model_from_str(inp, **model_kwargs)
        var_list = get_children_of_type('Variable', prog)
        _ = next(v for v in var_list if v.name == 'a').value
    assert isinstance(err.value.__cause__, RuntimeTypeError)


def test_evaluate_imported_function_runtime_error(meta_model, model_kwargs, capsys):
    """test evaluate imported function with unknown runtime error"""
    inp = 'use randint from numpy.random; print(randint(0, 10, 5))'
    _ = meta_model.model_from_str(inp, **model_kwargs).value
    stderr = capsys.readouterr().err
    msg1 = "Unknown error:"
    msg2 = "Neither Quantity object nor its magnitude (5) has attribute 'size'"
    assert msg1 in stderr
    assert msg2 in stderr
