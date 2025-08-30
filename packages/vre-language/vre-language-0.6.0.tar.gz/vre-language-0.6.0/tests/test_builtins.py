"""
tests for basic language components
"""
import pytest
from textx import get_children_of_type
from textx.exceptions import TextXError, TextXSyntaxError, TextXSemanticError
from virtmat.language.utilities.typemap import typemap
from virtmat.language.utilities.errors import VaryError
from virtmat.language.utilities.warnings import TextSUserWarning
from virtmat.language.utilities.logging import logging


def test_empty_program(meta_model, model_kwargs):
    """test empty programs"""
    prog_inps = ['', ' ', '\n', '# comment', ' # \n#']
    for prog_inp in prog_inps:
        prog = meta_model.model_from_str(prog_inp, **model_kwargs)
        assert isinstance(prog, str)
        assert prog == ''


def test_multiline_comments(meta_model, model_kwargs):
    """test python-like multiline comment"""
    prog_str = ('"""\nThis is a test set for the scientific computing language'
                '\n"""\n\n""" second multiline comment\n """\n\n"""third multil'
                'ine comment"""')
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    assert isinstance(prog, str)
    assert prog == ''


def test_invalid_statements(meta_model, model_kwargs):
    """test invalid statements in program"""
    prog_inps = ["a == 1", "b", ";", "false or true", "c = 1; c + 1"]
    for inp in prog_inps:
        with pytest.raises(TextXSyntaxError):
            meta_model.model_from_str(inp, **model_kwargs)


def test_print(meta_model, model_kwargs):
    """test print builtin function"""
    prog_str = "print('8', 8)\n"
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    objs = get_children_of_type('Print', prog)
    assert len(objs) == 1
    assert prog.value == '\'8\' 8'


def test_string_literal(meta_model, model_kwargs):
    """test variable initialization with a string literal"""
    prog_str = "string = 'Abc'"
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    var_objs = get_children_of_type('Variable', prog)
    var_strs = get_children_of_type('String', prog)
    assert isinstance(prog.value, str)
    assert prog.value == ''
    assert len(var_objs) == 1
    assert len(var_strs) == 1
    assert issubclass(var_objs[0].type_, str)
    assert var_objs[0].value == 'Abc'
    assert issubclass(var_strs[0].type_, str)
    assert var_strs[0].value == 'Abc'


def test_int_literal(meta_model, model_kwargs):
    """test variable initialization with an integer literal"""
    prog_str = 'a = 10'
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    var_objs = get_children_of_type('Variable', prog)
    assert len(get_children_of_type('Expression', prog)) == 0
    num_objs = get_children_of_type('Quantity', prog)
    assert isinstance(prog.value, str)
    assert prog.value == ''
    assert len(var_objs) == 1
    assert len(num_objs) == 1
    assert issubclass(var_objs[0].type_, typemap['Quantity'])
    assert issubclass(var_objs[0].type_.datatype, int)
    assert var_objs[0].value == 10
    assert issubclass(num_objs[0].type_, typemap['Quantity'])
    assert issubclass(num_objs[0].type_.datatype, int)
    assert num_objs[0].value == 10


def test_int_expression(meta_model, model_kwargs):
    """test variable initialization with an int arithmetic expression"""
    prog_str = 'a = 10; b = 2 * a + 17'
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    var_objs = get_children_of_type('Variable', prog)
    exp_objs = get_children_of_type('Expression', prog)
    assert len(get_children_of_type('Quantity', prog)) == 3
    assert isinstance(prog.value, str)
    assert prog.value == ''
    assert len(var_objs) == 2
    assert len(exp_objs) == 1
    for var in var_objs:
        assert issubclass(var.type_, typemap['Quantity'])
        assert issubclass(var.type_.datatype, int)
        if var.name == 'b':
            assert var.value == 37
        if var.name == 'a':
            assert var.value == 10


def test_float_expression(meta_model, model_kwargs):
    """test variable initialization with an float arithmetic expression"""
    prog_str = 'a = 10; b = 2*a + 17 \nc = -(4-1)*a + (2+4.67) +b*5.89/(.2+7)'
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    var_objs = get_children_of_type('Variable', prog)
    assert prog.value == ''
    assert len(var_objs) == 3
    for var in var_objs:
        if var.name == 'c':
            assert issubclass(var.type_, typemap['Quantity'])
            assert issubclass(var.type_.datatype, float)
            assert var.value == pytest.approx(6.93805555)


def test_power_expression(meta_model, model_kwargs):
    """test power in arithmetic expressions and variables"""
    prog_str = ('z = 3; a = 5**1**3**2+1; b = 5*2**1**13; c = 0.4**-1.2; '
                'd = 0.3*-7**-3; e=z**4')
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    var_objs = get_children_of_type('Variable', prog)
    for var in var_objs:
        if var.name == 'a':
            assert var.value == 6
        if var.name == 'b':
            assert var.value == 10
        if var.name == 'c':
            assert var.value == pytest.approx(3.00281108)
        if var.name == 'd':
            assert var.value == pytest.approx(-0.000874635568513)
        if var.name == 'e':
            assert var.value == 81


def test_undefined_variable_reference(meta_model, model_kwargs):
    """reference to an undefined variable"""
    prog_str = 'a = b'
    with pytest.raises(TextXSemanticError,
                       match='Unknown object "b" of class "OBJECT"'):
        meta_model.model_from_str(prog_str, **model_kwargs)


def test_repeated_initialization_reference(meta_model, model_kwargs):
    """repeated initialization of a variable that has been referenced"""
    prog_str = 'a = 10; b = 2*a + 17; a = 5'
    with pytest.raises(TextXError, match='Repeated initialization of "a"'):
        meta_model.model_from_str(prog_str, **model_kwargs)


def test_repeated_initialization_nonreference(meta_model, model_kwargs):
    """repeated initialization of a variable that has not been referenced"""
    prog_str = 'a = 10; b = 2*a + 17; b = 5'
    with pytest.raises(TextXError, match='Repeated initialization of "b"'):
        meta_model.model_from_str(prog_str, **model_kwargs)


def test_boolean_literal(meta_model, model_kwargs):
    """test variable initialization with boolean literals"""
    prog_str = ('foo = true; baz = false; bar = not (true and false) and not true; '
                'foobar = true or false')
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    var_objs = get_children_of_type('Variable', prog)
    assert prog.value == ''
    assert len(var_objs) == 4
    for var in var_objs:
        assert issubclass(var.type_, bool)
        if var.name == 'foo':
            assert var.value is True
        if var.name == 'bar':
            assert var.value is False
        if var.name == 'foobar':
            assert var.value is True


def test_boolean_expression(meta_model, model_kwargs):
    """test variable initialization with boolean expressions"""
    prog_str = ('blah = not (true and false) and not true; foo = not blah; '
                'foobar = true or false; bar = (foo and blah) or foobar')
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    var_objs = get_children_of_type('Variable', prog)
    assert prog.value == ''
    assert len(var_objs) == 4
    for var in var_objs:
        assert issubclass(var.type_, bool)
        if var.name == 'bar':
            assert var.value is True
        if var.name == 'foo':
            assert var.value is True
        if var.name == 'blah':
            assert var.value is False
        if var.name == 'foobar':
            assert var.value is True


def test_boolean_expression_short_cicuit(meta_model, model_kwargs, test_config, caplog):
    """test short circuiting or/and expressions"""
    l_name = 'deferred' if test_config[0] else 'instant'
    logger_name = f'virtmat.language.interpreter.{l_name}_executor'
    caplog.set_level(logging.DEBUG, logger=logger_name)
    prog_inp = 'a = true; b = true or a; c = false and a; print(b, c)'
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    assert prog.value == 'true false'
    var_list = get_children_of_type('Variable', prog)
    var_a = next(v for v in var_list if v.name == 'a')
    assert 'value' not in var_a.__dict__  # necessary but not sufficient
    if not test_config[1]:
        assert 'evaluated <Variable:a>' not in caplog.text
        assert 'evaluated <Variable:b>' in caplog.text
        assert 'evaluated <Variable:c>' in caplog.text


def test_illegal_use_of_keywords(meta_model, model_kwargs):
    """test illegal use of keywords"""
    prog_strs = ['not = 0', 'true = false', 'all = 4', 'select = 5']
    for prog_str in prog_strs:
        with pytest.raises(TextXSyntaxError):
            meta_model.model_from_str(prog_str, **model_kwargs)


def test_substring_keyword(meta_model, model_kwargs):
    """test variable names that have keywords as substrings"""
    prog_strs = ['select_number = 5', 'notbar= 3.14', 'true_ = 1', '_orkan = 3',
                 "andy = 'Hi!'", 'truefalse = true or false\n']
    for prog_str in prog_strs:
        meta_model.model_from_str(prog_str, **model_kwargs)


def test_noeol_after_keyword(meta_model, model_kwargs):
    """test a keyword at end of string with no eol"""
    prog = meta_model.model_from_str('a = true', **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    assert issubclass(next(v for v in var_list if v.name == 'a').type_, bool)
    assert next(v for v in var_list if v.name == 'a').value is True


def test_eol_after_keyword(meta_model, model_kwargs):
    """test a keyword at end of string followed by eol character"""
    prog_strs = ['a = true\n']
    for prog_str in prog_strs:
        meta_model.model_from_str(prog_str, **model_kwargs)


def test_white_space_around_statement_separators(meta_model, model_kwargs):
    """white space in statement separators and leading/trailing white space"""
    prog_strs = [' \nb = 4\n a = 2', '\n c = 1; \n   print(c)\n\n ']
    for prog_str in prog_strs:
        meta_model.model_from_str(prog_str, **model_kwargs)


def test_multiline_statements(meta_model, model_kwargs):
    """test statements spanning multiple lines"""
    meta_model.model_from_str('a \n =\n 3; b = 3\n   +4\n   -1', **model_kwargs)


def test_no_eol_separator_in_imaginary_number(meta_model, model_kwargs):
    """test the white space separator in imaginary number contains no eol"""
    meta_model.model_from_str('c = 0\nj = 1', **model_kwargs)


def test_semicolon(meta_model, model_kwargs):
    """test missing statement before/after semicolon"""
    prog_strs = ['; b = 1', 'a = 3;']
    for prog_str in prog_strs:
        with pytest.raises(TextXSyntaxError):
            meta_model.model_from_str(prog_str, **model_kwargs)


def test_unordered_boolean(meta_model, model_kwargs):
    """test unordered initialization - boolean"""
    prog_str = "bar = true; foobar = (foo or bar); foo = not bar"
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    var = next(v for v in var_list if v.name == 'foobar')
    assert issubclass(var.type_, bool)
    assert var.value is True


def test_unordered_float(meta_model, model_kwargs):
    """test unordered initialization - float"""
    prog_str = "a = b + c; b = c + 2.; c = 0"
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    var = next(v for v in var_list if v.name == 'a')
    assert issubclass(var.type_, typemap['Quantity'])
    assert issubclass(var.type_.datatype, float)
    assert var.value == 2.0


def test_if_expression_active_branch(meta_model, model_kwargs):
    """test if-expression in an active branch"""
    prog_inp = ("bar = true; foo = true; foobar = bar if not bar else foo\n"
                "foobar2 = 3 / 1 if not (true and false) and not true else 7.")
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    var = next(v for v in var_list if v.name == 'foobar')
    assert len(get_children_of_type('Quantity', prog)) == 3
    assert len(get_children_of_type('Bool', prog)) == 5
    assert issubclass(var.type_, bool)
    assert var.value is True
    var = next(v for v in var_list if v.name == 'foobar2')
    assert issubclass(var.type_, typemap['Quantity'])
    assert issubclass(var.type_.datatype, float)
    assert var.value == 7.


def test_if_expression_non_active_branch(meta_model, model_kwargs):
    """test if-expression in an non-active branch"""
    prog_inp = "a = 3; b = (a + 2) if false else 1"
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    var_a = next(v for v in var_list if v.name == 'a')
    var_b = next(v for v in var_list if v.name == 'b')
    assert issubclass(var_b.type_, typemap['Quantity'])
    assert issubclass(var_b.type_.datatype, int)
    assert 'value' not in var_a.__dict__
    assert var_b.value == 1
    assert 'value' not in var_a.__dict__
    expressions = get_children_of_type('Expression', prog)
    assert len(expressions) == 1
    assert len(get_children_of_type('Quantity', prog)) == 3
    assert len(get_children_of_type('Bool', prog)) == 1
    assert issubclass(expressions[0].type_, typemap['Quantity'])
    assert issubclass(expressions[0].type_.datatype, int)
    assert 'value' not in expressions[0].__dict__


def test_if_expression_nested(meta_model, model_kwargs):
    """test if-expression with nested if expressions"""
    prog_inp = ("a = 3;"
                "c = a if true else 1 if false else 0;"
                "d = (a if true else 1) if false else 0;"
                "e = a if true else (1 if false else 0);"
                "f = 2 if false else a if false else 0")
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    assert next(v for v in var_list if v.name == 'c').value == 3
    assert next(v for v in var_list if v.name == 'd').value == 0
    assert next(v for v in var_list if v.name == 'e').value == 3
    assert next(v for v in var_list if v.name == 'f').value == 0


def test_if_function(meta_model, model_kwargs):
    """test built-in if-function"""
    prog_inp = ("bar = true; true_branch = 'true_branch'\n"
                "p = if(not bar, true_branch, 'false_branch')")
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    var = next(v for v in var_list if v.name == 'p')
    assert issubclass(var.type_, str)
    assert var.value == 'false_branch'
    var = next(v for v in var_list if v.name == 'true_branch')
    assert issubclass(var.type_, str)
    assert var.value == 'true_branch'


def test_if_function_float_expressions(meta_model, model_kwargs):
    """test if-function with a float expression in a non-active branch"""
    prog_inp = "bar = true; a = 10; b = a*2+17; c = if(bar, (b+4)/2, 1/2)"
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    var = next(v for v in var_list if v.name == 'c')
    assert issubclass(var.type_, typemap['Quantity'])
    assert issubclass(var.type_.datatype, float)
    assert var.value == 20.5
    expressions = get_children_of_type('Expression', prog)
    assert len(get_children_of_type('Quantity', prog)) == 7
    assert len(expressions) == 4
    assert issubclass(expressions[3].type_, typemap['Quantity'])
    assert issubclass(expressions[3].type_.datatype, float)
    assert 'value' not in expressions[3].__dict__


def test_nested_if_function(meta_model, model_kwargs):
    """test nested if-functions"""
    prog_inp = ("bar = true; a = 0; b = 1\n"
                "p = if (bar, if(bar, 2, a), if(false, a, b))")
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    var = next(v for v in var_list if v.name == 'p')
    assert issubclass(var.type_, typemap['Quantity'])
    assert issubclass(var.type_.datatype, int)
    assert var.value == 2


def test_if_function_non_strictness(meta_model, model_kwargs, test_config, caplog):
    """test non-strictness of if function / expression"""
    l_name = 'deferred' if test_config[0] else 'instant'
    logger_name = f'virtmat.language.interpreter.{l_name}_executor'
    caplog.set_level(logging.DEBUG, logger=logger_name)
    prog_inp = "a = 1; b = if(true, 2, a); print(b)"
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    assert prog.value == '2'
    var_list = get_children_of_type('Variable', prog)
    var_a = next(v for v in var_list if v.name == 'a')
    assert 'value' not in var_a.__dict__  # necessary but not sufficient
    if not test_config[1]:
        assert 'value' not in var_a.parameter.__dict__
        assert 'evaluated <Variable:a>' not in caplog.text
        assert 'evaluated <Variable:b>' in caplog.text


def test_comparison_literal_operands_assignment(meta_model, model_kwargs):
    """with arithmetic constant operands in variable assignment"""
    prog_inp = ("a = 3 == 3; b = (4 == 2); c = 4 > 2; d = (-3 < 0)\n"
                "e = (4/2 == 2)")
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    for var in var_list:
        assert issubclass(var.type_, bool)
    assert next(v for v in var_list if v.name == 'a').value is True
    assert next(v for v in var_list if v.name == 'b').value is False
    assert next(v for v in var_list if v.name == 'c').value is True
    assert next(v for v in var_list if v.name == 'd').value is True
    assert next(v for v in var_list if v.name == 'e').value is True


def test_comparison_literal_operands_if_function(meta_model, model_kwargs):
    """with arithmetic constant operands in if-function"""
    prog_inp = ("a = if((-3*3 > 10), true, false);"
                "b = if((-3*3 <= 10), true, false)\n"
                "c = if(3 == 2, -1, +1); d = if(3 >= 2, 1, 0)")
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    assert next(v for v in var_list if v.name == 'a').value is False
    assert next(v for v in var_list if v.name == 'b').value is True
    assert next(v for v in var_list if v.name == 'c').value == 1
    assert next(v for v in var_list if v.name == 'd').value == 1


def test_comparison_expression_operands_assignment(meta_model, model_kwargs):
    """comparison with arithmetic expression operands in variable assignment"""
    prog_inp = ("a = 1.0e0; b = 10; c = a == b; d = a > 3*b; e = 10*a-b <= 0;"
                "f = b == b; g = a < 0; h = 2*a-1 == a")
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    assert issubclass(next(v for v in var_list if v.name == 'a').type_, typemap['Quantity'])
    assert issubclass(next(v for v in var_list if v.name == 'a').type_.datatype, float)
    assert issubclass(next(v for v in var_list if v.name == 'b').type_, typemap['Quantity'])
    assert issubclass(next(v for v in var_list if v.name == 'b').type_.datatype, int)
    assert next(v for v in var_list if v.name == 'c').value is False
    assert next(v for v in var_list if v.name == 'd').value is False
    assert next(v for v in var_list if v.name == 'e').value is True
    assert next(v for v in var_list if v.name == 'f').value is True
    assert next(v for v in var_list if v.name == 'g').value is False
    assert next(v for v in var_list if v.name == 'h').value is True


def test_comparison_expression_operands_boolean_expression(meta_model, model_kwargs):
    """comparison with arithmetic expression operands in boolean expressions"""
    prog_inp = ("res = 0\n"
                "ans1 = ((res < 0.0001) and (res >= 0.0)) or\n"
                "((res > -0.0001) and (res <= 0.0))\n"
                "ans2 = not (res == res); ans3 = not (res < res)\n"
                "ans4 = not (res <= res)")
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    assert next(v for v in var_list if v.name == 'ans1').value is True
    assert next(v for v in var_list if v.name == 'ans2').value is False
    assert next(v for v in var_list if v.name == 'ans3').value is True
    assert next(v for v in var_list if v.name == 'ans4').value is False


def test_comparison_boolean_operands(meta_model, model_kwargs):
    """comparison with boolean operands"""
    prog_inp = ("a = true == false; b = false == false; c = false == not false;"
                "bar = true; d = bar == not false;"
                "e = not (bar == true and true);"
                "f = not (bar == false) and true")
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    assert next(v for v in var_list if v.name == 'a').value is False
    assert next(v for v in var_list if v.name == 'b').value is True
    assert next(v for v in var_list if v.name == 'c').value is False
    assert next(v for v in var_list if v.name == 'd').value is True
    assert next(v for v in var_list if v.name == 'e').value is False
    assert next(v for v in var_list if v.name == 'f').value is True


def test_comparison_boolean_operands_invalid_operators(meta_model, model_kwargs):
    """comparison with boolean operands and invalid comparison operators"""
    prog_inps = ['a = true < false', 'b = true <= false', 'c = true > true',
                 'd = true <= true']
    msg = 'comparison not possible with'
    for prog_inp in prog_inps:
        with pytest.raises(TextXError, match=msg):
            meta_model.model_from_str(prog_inp, **model_kwargs)


def test_comparison_string_operands(meta_model, model_kwargs):
    """comparison with string operands in assignments and expressions"""
    prog_inp = ("string = 'Abc'; a = string == string; b = string == 'Abc';"
                "c = not (string == 'Q'); d = 'q' == 'q'; e = 'q' == 'Q'")
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    assert next(v for v in var_list if v.name == 'a').value is True
    assert next(v for v in var_list if v.name == 'b').value is True
    assert next(v for v in var_list if v.name == 'c').value is True
    assert next(v for v in var_list if v.name == 'd').value is True
    assert next(v for v in var_list if v.name == 'e').value is False


def test_comparison_if_expression(meta_model, model_kwargs):
    """comparison in if-expressions"""
    prog_inp = "a = 3.5 if 3 == 2 else 1.\n"
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    assert next(v for v in var_list if v.name == 'a').value == 1.


def test_scalar_complex_literals_and_expressions(meta_model, model_kwargs):
    """scalar complex literals and complex expressions"""
    prog_inp = ("z0 = 1 + 1 j; z1 = 1 - 1 j;"
                "a = z0+z1; b = z0*z1; c = z0**2;"
                "print(z0, z1, a, b, c)\n")
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    assert prog.value == '1.0+1.0 j 1.0-1.0 j 2.0+0.0 j 2.0+0.0 j 0.0+2.0 j'
    var_list = get_children_of_type('Variable', prog)
    assert all(issubclass(v.type_, typemap['Quantity']) for v in var_list)
    assert all(issubclass(v.type_.datatype, complex) for v in var_list)
    assert next(v for v in var_list if v.name == 'a').value == 2
    assert next(v for v in var_list if v.name == 'b').value == 2
    assert next(v for v in var_list if v.name == 'c').value == 2j


def test_scalar_complex_comparison_expressions(meta_model, model_kwargs):
    """scalar complex expressions in comparisons"""
    prog_inp = ("z0 = 1 + 1 j; z1 = 1 - 1 j;"
                "a = z0+z1; b = z0*z1; c = a == b; d = z0 != z1")
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    assert next(v for v in var_list if v.name == 'c').value is True
    assert next(v for v in var_list if v.name == 'd').value is True


def test_scalar_complex_invalid_comparison(meta_model, model_kwargs):
    """scalar complex expressions in invalid comparison"""
    prog_inp = 'z0 = 1 + 1 j; z1 = 1 - 1 j; a = z0 < z1'
    msg = 'comparison not possible with <'
    with pytest.raises(TextXError, match=msg):
        meta_model.model_from_str(prog_inp, **model_kwargs)


def test_scalar_complex_real_imag_parts(meta_model, model_kwargs):
    """real and imaginary parts of scalar complex types"""
    prog_inp = ("z0 = 1 + 1 j; z1 = 1 - 1 j; a = z0 + z1; g = 2*real(a);"
                "f = imag(z0+z1); h = (real(z0+z1) >= imag(a))")
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    assert next(v for v in var_list if v.name == 'g').value == 4.0
    assert next(v for v in var_list if v.name == 'f').value == 0.0
    assert next(v for v in var_list if v.name == 'h').value is True


def test_pointless_use_of_vary_statement(meta_model, model_kwargs):
    """test pointless use of vary statement"""
    if model_kwargs.get('model_instance'):
        meta_model.model_from_str('vary ((a: 1, 2))', **model_kwargs)
    else:
        with pytest.warns(TextSUserWarning, match='vary statement has no effect'):
            meta_model.model_from_str('vary ((a: 1, 2))', **model_kwargs)


def test_invalid_reference_to_vary_statement(meta_model, model_kwargs):
    """test invalid reference to series in a vary statement"""
    msg = 'reference to series \"a\" in vary statement'
    with pytest.raises(VaryError, match=msg):
        meta_model.model_from_str('vary ((a: 1, 2)); print(a)', **model_kwargs)


def test_builtin_info_function(meta_model, model_kwargs, _res_config_loc):
    """test the built-in info function, res_config fixture due to wfengine"""
    prog_inp = "a = 2 * 0.2 [m]; print(info(a))"
    ref = ("((name: 'a'), (type: 'Quantity'), (scalar: true), (numeric: true),"
           " (datatype: 'float'), (dimensionality: '[length]'), (units: 'meter')")
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    assert ref in prog.value
    typ_list = get_children_of_type('Type', prog)
    assert len(typ_list) == 1
    typ = typ_list[0]
    assert typ.value.name.tolist() == ['a']
    assert typ.value.type.tolist() == ['Quantity']
    assert typ.value.datatype.tolist() == ['float']
    assert typ.value.numeric.tolist() == [True]
    assert typ.value.units.tolist() == ['meter']


def test_builtin_info_function_with_eval_error(meta_model, model_kwargs, _res_config_loc):
    """test the built-in info function with evaluation error; res_config due to wfengine"""
    prog_inp = "a = 2 / 0; print(info(a))"
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    ref = ("((name: 'a'), (type: 'Quantity'), (scalar: true), (numeric: true),"
           " (datatype: 'float')")
    assert ref in prog.value


def test_builtin_info_function_callable_import(meta_model, model_kwargs):
    """test the built-in info function with callable import"""
    prog_inp = "use random from numpy.random; print(info(random))"
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    assert "(name: 'random')" in prog.value


def test_if_function_in_numeric_expresion(meta_model, model_kwargs):
    """test if-function as first parameter of a numeric expression"""
    inp = 'print(if(true, 1, 2) + 1)'
    assert meta_model.model_from_str(inp, **model_kwargs).value == '2'


def test_print_in_model_with_errors(meta_model, model_kwargs):
    """test the print result in case of an error not affecting the print"""
    inp = "a = 1 / 0; b = a + 1; c = 2; print(c); print(b)"
    assert meta_model.model_from_str(inp, **model_kwargs).value == '2'


def test_print_evaluate_with_nc_values(meta_model, model_kwargs, test_config):
    """test evaluation with nc values"""
    inp = "f = true; g = 2; print(if(not (false and f), 1, g), (2*g,))"
    if test_config[1]:
        model_kwargs['autorun'] = False
        assert meta_model.model_from_str(inp, **model_kwargs).value == '1 (n.c.,)'
    else:
        assert meta_model.model_from_str(inp, **model_kwargs).value == '1 (4,)'
