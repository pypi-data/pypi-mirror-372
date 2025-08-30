"""
tests for the typechecker
"""
import pytest
from textx import get_children_of_type
from textx.exceptions import TextXError, TextXSyntaxError
from virtmat.language.constraints.typechecks import ExpressionTypeError, TypeMismatchError
from virtmat.language.metamodel.properties import add_properties
from virtmat.language.metamodel.processors import add_processors
from virtmat.language.utilities.typemap import typemap
from virtmat.language.utilities.errors import StaticTypeError


@pytest.fixture(name='meta_model')
def fixture_metamodel(raw_meta_model):
    """parse the grammar and generate the object classes"""
    add_properties(raw_meta_model)
    add_processors(raw_meta_model, constr_processors=True)
    return raw_meta_model


def test_type_int_expression(meta_model):
    """test int type checker for arithmetic expressions and variables"""
    prog_str = "a = 10; b = -1 - a*3 + 15*(a-7)*(3+a) + 4*a*a"
    prog = meta_model.model_from_str(prog_str)
    var_objs = get_children_of_type('Variable', prog)
    exp_objs = get_children_of_type('Expression', prog)
    assert len(var_objs) == 2
    assert len(exp_objs) == 3
    assert len(get_children_of_type('Quantity', prog)) == 7
    assert all(issubclass(obj.type_, typemap['Quantity']) for obj in var_objs)
    assert all(issubclass(obj.type_.datatype, int) for obj in var_objs)
    assert all(issubclass(obj.type_.datatype, int) for obj in exp_objs)


def test_type_float_expression(meta_model):
    """test float type checker for arithmetic expressions and variables"""
    prog_str = "a = 10/c; b = 5*(8*a-3)/(15*(a-7.5)*(3+a)+4.1*a*a-a+6); c = 2"
    prog = meta_model.model_from_str(prog_str)
    var_objs = get_children_of_type('Variable', prog)
    exp_objs = get_children_of_type('Expression', prog)
    assert len(get_children_of_type('Quantity', prog)) == 10
    assert len(var_objs) == 3
    assert len(exp_objs) == 6
    assert next(issubclass(v.type_, typemap['Quantity']) for v in var_objs)
    assert next(issubclass(v.type_.datatype, float) for v in var_objs if v.name == 'a')
    assert next(issubclass(v.type_.datatype, float) for v in var_objs if v.name == 'b')
    assert next(issubclass(v.type_.datatype, int) for v in var_objs if v.name == 'c')
    assert all(issubclass(obj.type_.datatype, float) for obj in exp_objs[:-1])


def test_type_power_expression(meta_model):
    """test power type checker for arithmetic expressions and variables"""
    prog_str = ("z = 3; a = 5**1**3**2+1; b = 5*2**1**13; c = 0.4**-1.2; "
                "d = 0.3*-7**-3; e = z**4")
    prog = meta_model.model_from_str(prog_str)
    var_objs = get_children_of_type('Variable', prog)
    type_list = (int, int, float, float, int)
    name_list = ('a', 'b', 'c', 'd', 'e')
    for name, typ in zip(name_list, type_list):
        var = next(v for v in var_objs if v.name == name)
        assert issubclass(var.type_, typemap['Quantity'])
        assert issubclass(var.type_.datatype, typ)


def test_type_boolean_expression(meta_model):
    """test bool type checker for boolean expression objects and variables"""
    prog_str = "c = false; a = not (b and c); b = (c or true)"
    prog = meta_model.model_from_str(prog_str)
    var_objs = get_children_of_type('Variable', prog)
    exp_objs = get_children_of_type('Or', prog)
    assert len(get_children_of_type('Bool', prog)) == 2
    assert len(var_objs) == 3
    assert len(exp_objs) == 4
    assert all(issubclass(obj.type_, bool) for obj in var_objs)
    assert all(issubclass(obj.type_, bool) for obj in exp_objs)


def test_type_string_objects(meta_model):
    """test str type checker for string objects and variables"""
    prog_str = "a = b; b = 'Abc'"
    prog = meta_model.model_from_str(prog_str)
    var_objs = get_children_of_type('Variable', prog)
    str_objs = get_children_of_type('String', prog)
    assert len(var_objs) == 2
    assert len(str_objs) == 1
    assert all(issubclass(obj.type_, str) for obj in var_objs)
    assert all(issubclass(obj.type_, str) for obj in str_objs)


def test_type_comparison_objects(meta_model):
    """test bool type checker for comparison objects and variables"""
    prog_str = "c = a > b; a = 1; b = 2"
    prog = meta_model.model_from_str(prog_str)
    var_objs = get_children_of_type('Variable', prog)
    cmp_objs = get_children_of_type('Comparison', prog)
    assert len(var_objs) == 3
    assert len(cmp_objs) == 1
    var = next(v for v in var_objs if v.name == 'c')
    assert issubclass(var.type_, bool)


def test_type_comparison_type_mismatch(meta_model):
    """test comparison with a type mismatch"""
    prog_str = "c = a != b; a = 'c'; b = 2"
    msg = 'Type mismatch:'
    with pytest.raises(TypeMismatchError, match=msg):
        meta_model.model_from_str(prog_str)


def test_type_comparison_invalid_type(meta_model):
    """test comparison with invalid type"""
    prog_str = "c = a != b; a = 'a'; b = (b: 2)"
    msg = r'invalid type\(s\) used in comparison: Series'
    with pytest.raises(TextXError, match=msg) as err_info:
        meta_model.model_from_str(prog_str)
    assert isinstance(err_info.value.__cause__, StaticTypeError)


def test_type_comparison_string_type_invalid_operator(meta_model):
    """test comparison of strings with invalid operator"""
    prog_str = "c = a > b; a = 'a'; b = 'b'"
    msg = 'comparison not possible with >'
    with pytest.raises(TextXError, match=msg) as err_info:
        meta_model.model_from_str(prog_str)
    assert isinstance(err_info.value.__cause__, StaticTypeError)


def test_expression_type_error(meta_model):
    """test expression type error catched after parsing"""
    prog_strs = ["bar = true; mixed_0 = 3 * bar # ExpressionTypeError",
                 "bar = true; threebar = 3*bar # ExpressionTypeError",
                 "notbar = false; twobar = 2*notbar # ExpressionTypeError"]
    for prog_str in prog_strs:
        with pytest.raises(ExpressionTypeError):
            meta_model.model_from_str(prog_str)


def test_expression_type_error_anonymous(meta_model):
    """test expression type error for expressions not assigned to variables"""
    prog_strs = ["string = 'Abc'; print(3+string)",
                 "foo = false; string = 'Abc'; print(foo+string)",
                 "foo = true; string = 'Abc'; print(foo*string)",
                 "foo = true; c = 4.3e-1; print(foo-c)",
                 "a = 10; c = 2.; print((a or c))",
                 "a = 1; c = -3; print((a and c))",
                 "a = -1e-5; c = 2.; print(not (a and c))"]
    for prog_str in prog_strs:
        with pytest.raises(ExpressionTypeError):
            meta_model.model_from_str(prog_str)


def test_type_mismatch_error(meta_model):
    """test type mismatch error catched after parsing"""
    prog_strs = ["twotypes = 3 if true else 0.5 # TypeMismatchError",
                 "twotypes = if(true, 3, 0.5) # TypeMismatchError"]
    for prog_str in prog_strs:
        with pytest.raises(TypeMismatchError):
            meta_model.model_from_str(prog_str)


def test_textx_syntax_error(meta_model):
    """test type errors catched during parsing"""
    prog_strs = ["bar = true; twobar = 2*(not bar)",
                 "bar = true; foo = false; mixed_2 = 'bar' + 'foo'",
                 "mixed_3 = 3 + 'foo'"]
    for prog_str in prog_strs:
        with pytest.raises(TextXSyntaxError):
            meta_model.model_from_str(prog_str)


def test_textx_semantic_error(meta_model):
    """test type errors catched during parsing"""
    prog_strs = ["mixed_1 = 3 * true # parser error",
                 "mixed_4 = 3 * 'abc' # parser error"]
    for prog_str in prog_strs:
        with pytest.raises(TextXSyntaxError):
            meta_model.model_from_str(prog_str)


def test_unbound_import_type_comparision(meta_model):
    """unbound import type in comparison expression """
    prog_inp = 'use exp from math; a = (exp(1) < exp(2))\n'
    prog = meta_model.model_from_str(prog_inp)
    var_list = get_children_of_type('Variable', prog)
    calls = get_children_of_type('FunctionCall', prog)
    assert len(calls) == 2
    assert all(call.type_ is None for call in calls)
    assert issubclass(next(v.type_ for v in var_list if v.name == 'a'), bool)


def test_import_type_comparision(meta_model):
    """inferred import type in comparison expression"""
    prog_inp = 'use exp from math; a = (exp(2) > 1); b = (exp(2) > 1.)\n'
    prog = meta_model.model_from_str(prog_inp)
    var_list = get_children_of_type('Variable', prog)
    calls = get_children_of_type('FunctionCall', prog)
    assert len(calls) == 2
    assert all(issubclass(call.type_, typemap['Quantity']) for call in calls)
    assert all(issubclass(var.type_, bool) for var in var_list)


def test_unbound_import_type_if_function(meta_model):
    """unbound import type in if function"""
    prog_inp = 'use exp from math; a = if(true, exp(1), exp(2))\n'
    prog = meta_model.model_from_str(prog_inp)
    var_list = get_children_of_type('Variable', prog)
    calls = get_children_of_type('FunctionCall', prog)
    assert len(calls) == 2
    assert all(call.type_ is None for call in calls)
    var_a = next(v for v in var_list if v.name == 'a')
    assert var_a.type_ is None


def test_import_type_if_function(meta_model):
    """inferred import type in if function"""
    prog_inp = 'use exp from math; a = if(true, exp(1), 3.1)\n'
    prog = meta_model.model_from_str(prog_inp)
    var_list = get_children_of_type('Variable', prog)
    calls = get_children_of_type('FunctionCall', prog)
    assert len(calls) == 1
    assert issubclass(calls[0].type_, typemap['Quantity'])
    assert issubclass(calls[0].type_.datatype, float)
    var_a = next(v for v in var_list if v.name == 'a')
    assert issubclass(var_a.type_.datatype, float)


def test_function_call_type_in_print(meta_model):
    """bug function call type in print builtin"""
    inp = 'f(x) = 1 + x; print(f(1))\n'
    prog = meta_model.model_from_str(inp)
    calls = get_children_of_type('FunctionCall', prog)
    assert issubclass(calls[0].type_, typemap['Quantity'])
    assert issubclass(calls[0].type_.datatype, int)


def test_function_call_invalid_parameter_type(meta_model):
    """"test function calls with invalid parameter types"""
    inps = ['f(x) = x*x; a = f(true)\n', 'f(x) = if(x, 1, 0); a = f(1.)\n']
    match_str = 'Invalid type in expression'
    for inp in inps:
        with pytest.raises(TextXError, match=match_str):
            meta_model.model_from_str(inp)


def test_function_call_variable_type(meta_model):
    """test a function call with a variable type"""
    inp = 'f(x) = x; a = f(1); b = f(not false); c = f("Abc"); d = f(1.2e-5)\n'
    prog = meta_model.model_from_str(inp)
    var_list = get_children_of_type('Variable', prog)
    type_list = (int, bool, str, float)
    name_list = ('a', 'b', 'c', 'd')
    for name, typ in zip(name_list, type_list):
        var = next(v for v in var_list if v.name == name)
        if issubclass(var.type_, (bool, str)):
            assert issubclass(var.type_, typ)
        else:
            assert issubclass(var.type_.datatype, typ)


def test_types_iterable_functions_unknown_datatype(meta_model):
    """check type of iterable functions with parameters of unknown datatype"""
    inp = ('use exp from numpy\n'
           'ene = (v: 0.1, 0.05)\n'
           's = sum(filter((x: x>0), map((e: exp(-e)), ene)))\n'
           'r = reduce((x, y: x+y), filter((x: x>0), map((e: exp(-e)), ene)))\n'
           'b = all(map((x: x>0), map((e: exp(-e)), ene)))\n'
           'a = any(map((x: x>0), map((e: exp(-e)), ene)))\n'
           'd = sum(ene[0], ene[1]); e = sum(ene[0], s)\n'
           'print(s, r, b, a, d, e)')
    meta_model.model_from_str(inp)


def test_parameter_type_function_series(meta_model):
    """check the parameter type of functions on series"""
    inps = ['t = ((a: 1, 2, 3)); a = 5 in t\n',
            't = ((a: 1, 2, 3)); e = all(t)\n',
            't = ((a: 1, 2, 3)); f = sum(t)\n']
    match_str = 'Parameter must be series or reference to series'
    for inp in inps:
        with pytest.raises(TextXError, match=match_str):
            meta_model.model_from_str(inp)


def test_parameter_type_function_non_iterables(meta_model):
    """check the parameter type of functions on non-iterables"""
    inps = ['t = 1; b = filter((x: x > 1), t)',
            't = "abc"; c = map((x: x + 1), t)',
            't = true; d = reduce((x, y: x + y), t)']
    match_str = 'inputs* must be either series or table-like'
    for inp in inps:
        with pytest.raises(TextXError, match=match_str):
            meta_model.model_from_str(inp)


def test_index_error(meta_model):
    """test invalid indexing"""
    inps = ['s = (length: 1, 2, 3) [meter]; print(s[3])',
            't = ((number: 1, 2, 3)); print(t[4])',
            't = ((number: 1, 2, 3)); print(t.number[4])']
    for inp in inps:
        with pytest.raises(TextXError, match='Index out of range'):
            meta_model.model_from_str(inp)


def test_slice_step_error(meta_model):
    """test invalid slice step"""
    inps = ['s = (length: 1, 2, 3) [meter]; print(s[0:2:0])',
            't = ((number: 1, 2, 3)); print(t[0:1:0])']
    for inp in inps:
        with pytest.raises(TextXError, match='Slice step cannot be zero'):
            meta_model.model_from_str(inp)
