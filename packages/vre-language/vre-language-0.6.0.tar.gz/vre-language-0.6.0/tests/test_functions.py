"""
tests for functions
"""
import pytest
from textx import get_children_of_type
from textx import textx_isinstance
from textx import TextXError, TextXSemanticError
from virtmat.language.utilities.typemap import typemap


def test_function_def_empty_argument_list(meta_model, model_kwargs):
    """test function definition with empty arguments list"""
    prog_inp = 'func1() = 0; func2() = true; func3() = \'Abc\'\n'
    msg = 'Function definition must have at least one argument'
    with pytest.raises(TextXError, match=msg):
        meta_model.model_from_str(prog_inp, **model_kwargs)


def test_function_def_var_reference(meta_model, model_kwargs):
    """test function definition with var reference"""
    prog_inp = 'a = 2; func1(x) = a*x; func2(x) = 3*x; func3(x) = 3 + a/x\n'
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    assert len(get_children_of_type('FunctionDefinition', prog)) == 3


def test_function_def_unused_arguments(meta_model, model_kwargs):
    """test a functin definition with unused arguments"""
    prog_inp = 'f(x, y, z) = 0\n'
    match_str = (r"Dummy variables \[\] do not match arguments "
                 r"\['x', 'y', 'z'\] in function f")
    with pytest.raises(TextXError, match=match_str):
        meta_model.model_from_str(prog_inp, **model_kwargs)


def test_function_def_calling_another_function(meta_model, model_kwargs):
    """test a function definition with a call of another function"""
    prog_inp = 'f(t) = sum(map((x: if(x, 1, 0)), t))'
    meta_model.model_from_str(prog_inp, **model_kwargs)


def test_function_def_calling_another_function_error(meta_model, model_kwargs):
    """test a function definition with a call of another function with error"""
    prog_inp = 'f(t, z) = sum(map((x: if(x, 1, 0)), t))'
    match_str = (r"Dummy variables \['t'\] do not match arguments "
                 r"\['t', 'z'\] in function f")
    with pytest.raises(TextXError, match=match_str):
        meta_model.model_from_str(prog_inp, **model_kwargs)


def test_function_def_unknown_arguments(meta_model, model_kwargs):
    """test a function definition with unknown"""
    prog_inp = 'g(t) = 2*t + y; f(y) = y\n'
    match_str = 'Unknown object "y" of class "OBJECT"'
    with pytest.raises(TextXSemanticError, match=match_str):
        meta_model.model_from_str(prog_inp, **model_kwargs)


def test_function_def_one_argument(meta_model, model_kwargs):
    """test function definition with one argument"""
    prog = meta_model.model_from_str('f(x) = x\n', **model_kwargs)
    func_defs = get_children_of_type('FunctionDefinition', prog)
    assert len(func_defs) == 1


def test_function_def_two_arithmetic(meta_model, model_kwargs):
    """test function definition arithmetic type"""
    prog_inp = 'func(x, y) = a*x + c*y; a = 5+10*c; c = 4\n'
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    assert len(get_children_of_type('FunctionDefinition', prog)) == 1


def test_function_def_two_boolean(meta_model, model_kwargs):
    """test function definition boolean type"""
    prog_inp = 'func(x, y) = (y or (x and not a)); a = true\n'
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    assert len(get_children_of_type('Or', prog)) == 3
    assert len(get_children_of_type('Bool', prog)) == 1
    assert len(get_children_of_type('FunctionDefinition', prog)) == 1


def test_function_def_if_expression(meta_model, model_kwargs):
    """test function definition with two arguments"""
    prog_inp = 'gt(x, y) = x if x>y else y\n'
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    assert len(get_children_of_type('IfExpression', prog)) == 1
    assert len(get_children_of_type('FunctionDefinition', prog)) == 1


def test_function_def_if_function(meta_model, model_kwargs):
    """test function definition with two arguments"""
    prog_inp = 'gt(x, y) = if(x>y, x, y)\n'
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    assert len(get_children_of_type('IfFunction', prog)) == 1
    assert len(get_children_of_type('FunctionDefinition', prog)) == 1


def test_function_call_empty_argument_list(meta_model, model_kwargs):
    """test function call with empty arguments list"""
    prog_inp = 'func() = b; a = func(); b = 1\n'
    msg = 'Function definition must have at least one argument'
    with pytest.raises(TextXError, match=msg):
        meta_model.model_from_str(prog_inp, **model_kwargs)


def test_function_call_one_argument(meta_model, model_kwargs):
    """test function call with one argument"""
    prog_inp = 'a = sqr(2); sqr(x) = x*x\n'
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    assert len(var_list) == 1
    funcs = get_children_of_type('FunctionDefinition', prog)
    calls = get_children_of_type('FunctionCall', prog)
    assert len(funcs) == 1
    assert len(calls) == 1
    assert textx_isinstance(calls[0].parent, meta_model['Variable'])
    assert len(calls[0].params) == len(funcs[0].args)
    assert len(calls[0].params) == 1
    assert issubclass(calls[0].type_, typemap['Quantity'])
    assert issubclass(calls[0].type_.datatype, int)
    var = next(v for v in var_list if v.name == 'a')
    assert issubclass(var.type_, typemap['Quantity'])
    assert issubclass(var.type_.datatype, int)
    assert var.value == 4


def test_nested_function_call_one_argument(meta_model, model_kwargs):
    """test nested function call, i.e. call with a parameter that is a call"""
    prog_inp = 'a = sqr(sqr(2)); sqr(x) = x*x; b = (sqr((sqr(a)/16))-1)\n'
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    calls = get_children_of_type('FunctionCall', prog)
    assert len(var_list) == 2
    assert len(calls) == 4
    assert all(issubclass(c.type_, typemap['Quantity']) for c in calls)
    assert all(issubclass(c.type_.datatype, (int, float)) for c in calls)
    var_a = next(v for v in var_list if v.name == 'a')
    var_b = next(v for v in var_list if v.name == 'b')
    assert issubclass(var_a.type_, typemap['Quantity'])
    assert issubclass(var_a.type_.datatype, int)
    assert var_a.value == 16
    assert issubclass(var_b.type_, typemap['Quantity'])
    assert issubclass(var_b.type_.datatype, float)
    assert var_b.value == 255.


def test_nested_function_call_two_functions(meta_model, model_kwargs):
    """test nested function call with two functions"""
    prog_inp = 'a = diff(sqr(2), sqr(1)); sqr(z) = z*z; diff(x, y) = x - y\n'
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    calls = get_children_of_type('FunctionCall', prog)
    assert len(var_list) == 1
    assert len(calls) == 3
    assert all(issubclass(c.type_, typemap['Quantity']) for c in calls)
    assert all(issubclass(c.type_.datatype, int) for c in calls)
    var_a = next(v for v in var_list if v.name == 'a')
    assert issubclass(var_a.type_, typemap['Quantity'])
    assert issubclass(var_a.type_.datatype, int)
    assert var_a.value == 3


def test_function_call_boolean_type(meta_model, model_kwargs):
    """test function call of boolean type"""
    prog_inp = 'a = lt(1, 3); lt(x, y) = x < y\n'
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    calls = get_children_of_type('FunctionCall', prog)
    assert len(var_list) == 1
    assert len(calls) == 1
    assert issubclass(calls[0].type_, bool)
    var_a = next(v for v in var_list if v.name == 'a')
    assert issubclass(var_a.type_, bool)
    assert var_a.value is True


def test_function_call_if_function(meta_model, model_kwargs):
    """test function call with if function"""
    prog_inp = 'a = max(1, 3); max(x, y) = if(x < y, y, x)\n'
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    calls = get_children_of_type('FunctionCall', prog)
    assert len(var_list) == 1
    assert len(calls) == 1
    assert issubclass(calls[0].type_, typemap['Quantity'])
    assert issubclass(calls[0].type_.datatype, int)
    var_a = next(v for v in var_list if v.name == 'a')
    assert issubclass(var_a.type_, typemap['Quantity'])
    assert issubclass(var_a.type_.datatype, int)
    assert var_a.value == 3


def test_function_definition_with_call(meta_model, model_kwargs):
    """test function definition with a call in its expression"""
    prog_inp = 'sqr(x) = x*x; sqr_min_1(y) = (sqr(y)-1); a = sqr_min_1(2)\n'
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    calls = get_children_of_type('FunctionCall', prog)
    assert len(var_list) == 1
    assert len(calls) == 3
    assert all(issubclass(c.type_, typemap['Quantity']) for c in calls)
    assert all(c.type_.datatype is None or issubclass(c.type_.datatype, int) for c in calls)
    var_a = next(v for v in var_list if v.name == 'a')
    assert issubclass(var_a.type_, typemap['Quantity'])
    assert issubclass(var_a.type_.datatype, int)
    assert var_a.value == 3


def test_function_definition_with_call_boolean(meta_model, model_kwargs):
    """test function definition with a call in its expression boolean type"""
    prog_inp = 'sqr(x) = x*x; lt(y, z) = (sqr(y) < z); a = lt(2, 5)\n'
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    calls = get_children_of_type('FunctionCall', prog)
    assert len(var_list) == 1
    assert len(calls) == 3
    assert all(issubclass(c.type_, (bool, typemap['Quantity'])) for c in calls)
    assert all(issubclass(c.type_, bool) or c.type_.datatype is None or
               issubclass(c.type_.datatype, int) for c in calls)
    var_a = next(v for v in var_list if v.name == 'a')
    assert issubclass(var_a.type_, bool)
    assert var_a.value is True


def test_function_definition_with_call_statement_ordering(meta_model, model_kwargs):
    """test function definition with a call with two statement orderings"""
    inp = ('sqr(x) = x*x; one_minus_sqr(y) = sqr(y); a = one_minus_sqr(2);'
           'b = one_minus_sqr2(2); one_minus_sqr2(y) = sqr(y)\n')
    var_list = get_children_of_type('Variable', meta_model.model_from_str(inp, **model_kwargs))
    assert next(v for v in var_list if v.name == 'a').value == 4
    assert next(v for v in var_list if v.name == 'b').value == 4


def test_function_definition_with_call_dummies_of_different_names(meta_model, model_kwargs):
    """test function definition with a call and dummies of different names"""
    inp = 'f1(x) = 2*x; f2(y) = (f1(4) + y); a = f2(2)\n'
    var_list = get_children_of_type('Variable', meta_model.model_from_str(inp, **model_kwargs))
    assert next(v for v in var_list if v.name == 'a').value == 10


def test_function_definition_with_call_dummies_of_same_names(meta_model, model_kwargs):
    """test a function definition with a call and dummies with the same names"""
    inp = 'f1(x) = 2*x; f2(x) = (f1(4) + x); a = f2(2); print(a)\n'
    assert meta_model.model_from_str(inp, **model_kwargs).value == '10'


def test_function_call_with_dummy_reference(meta_model, model_kwargs):
    """test a call where expr is a reference to a dummy variable"""
    inp = 'f(x) = x; a = f(1); print(a)\n'
    prog = meta_model.model_from_str(inp, **model_kwargs)
    assert prog.value == str(1)


def test_call_undefined_function(meta_model, model_kwargs):
    """test call of undefined function"""
    prog_inp = 'a = 2.*func()\n'
    msg = 'Unknown object "func" of class "Function"'
    with pytest.raises(TextXSemanticError, match=msg):
        meta_model.model_from_str(prog_inp, **model_kwargs)


def test_dummy_variable_names_in_different_scopes(meta_model, model_kwargs):
    """test dummy variable with same names defined in different scopes"""
    prog_inp = 'sqr(x) = x*x; diff(x, y) = x - y; a = sqr(2.); b = diff(2, 1)\n'
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    var_a = next(v for v in var_list if v.name == 'a')
    assert issubclass(var_a.type_, typemap['Quantity'])
    assert issubclass(var_a.type_.datatype, float)
    assert var_a.value == 4.
    var_b = next(v for v in var_list if v.name == 'b')
    assert issubclass(var_b.type_, typemap['Quantity'])
    assert issubclass(var_b.type_.datatype, int)
    assert var_b.value == 1


def test_duplicated_function_names(meta_model, model_kwargs):
    """test repeated initialization"""
    inp = 'v = 7.5; v(x, y) = x*x + y*y'
    with pytest.raises(TextXError, match='Repeated initialization of "v"'):
        meta_model.model_from_str(inp, **model_kwargs)


def test_function_call_invalid_number_of_parameters(meta_model, model_kwargs):
    """test a function call with invalid number of parameters"""
    inps = ['f(x) = x*x; a = f()\n', 'f(x) = x*x; a = f(2, 3)\n']
    msgs = [r'Function "f" takes 1 parameters but 0 were given',
            r'Function "f" takes 1 parameters but 2 were given']
    for inp, msg in zip(inps, msgs):
        with pytest.raises(TextXError, match=msg):
            meta_model.model_from_str(inp, **model_kwargs)


def test_print_function_call(meta_model, model_kwargs):
    """test a print of a function call"""
    inp = 'f(x) = x*x; print(f(3))\n'
    assert meta_model.model_from_str(inp, **model_kwargs).value == '9'


def test_function_definition_repeating_argument_names(meta_model, model_kwargs):
    """test a function definition with repeating argument names"""
    inp = 'h(x, x) = x\n'
    msg = r'Duplicate argument\(s\) in function h: x'
    with pytest.raises(TextXError, match=msg):
        meta_model.model_from_str(inp, **model_kwargs)


def test_function_definition_with_call_dummies_equal_names(meta_model, model_kwargs):
    """test a function definition with call dummies with repeating names"""
    inp = 'h(x, y) = x + y; g(x, y, z) = z + h(x, y); print(g(0, 1, 2))'
    assert meta_model.model_from_str(inp, **model_kwargs).value == '3'


def test_duplicated_dummy_variable_names_local_scope(meta_model, model_kwargs):
    """test duplicated dummy variable names using local scope"""
    inp = 'sqr(x) = x*x; diff(x, y) = x - y; print(diff(2, 1))\n'
    assert meta_model.model_from_str(inp, **model_kwargs).value == '1'


def test_duplicated_names_global_and_local_scope(meta_model, model_kwargs):
    """test repeating names in local and global scope"""
    inp = 'a = 2; f(a) = a + 1; c = f(a); print(c)\n'
    prog = meta_model.model_from_str(inp, **model_kwargs)
    assert prog.value == '3'


def test_function_with_call_expression_two_arguments(meta_model, model_kwargs):
    """test function with a call with an expression and two arguments"""
    inp = 'sqr(x) = x*x; z_minus_sqr(q, r) = 2*sqr(-1*q+r); print(z_minus_sqr(2, 4.))'
    assert meta_model.model_from_str(inp, **model_kwargs).value == '8.0'


def test_function_with_complex_argument(meta_model, model_kwargs):
    """test function with complex argument"""
    inp = 'conjg(z) = real(z) - imag(z) * (0+1 j); a = 1 + 1 j; print(conjg(a))'
    assert meta_model.model_from_str(inp, **model_kwargs).value == '1.0-1.0 j'


def test_function_call_in_numeric_expression(meta_model, model_kwargs):
    """test function call as first parameter of a numeric expression"""
    inp = 'f(x) = x**2; print(f(2)+1)'
    assert meta_model.model_from_str(inp, **model_kwargs).value == '5'


def test_function_call_in_if_expression(meta_model, model_kwargs):
    """test function call as first parameter of an if-expression"""
    inp = 'f(x) = x**2; print(f(2) if true else 1)'
    assert meta_model.model_from_str(inp, **model_kwargs).value == '4'
