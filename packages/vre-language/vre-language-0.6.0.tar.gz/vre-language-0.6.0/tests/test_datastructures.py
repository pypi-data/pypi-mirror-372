"""
tests for data structures
"""
import yaml
import pytest
import numpy
from textx import get_children_of_type
from textx.exceptions import TextXError
from virtmat.language.utilities.typemap import typemap
from virtmat.language.utilities.errors import RuntimeValueError, RuntimeTypeError
from virtmat.language.utilities.errors import StaticTypeError


def test_function_call_returning_tuple(meta_model, model_kwargs):
    """test call of a internal function returning a tuple"""
    inp = 'f(x) = (x*x, 1); j = f(2); k = j[0]; l = j[1]\n'
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    names = ('j', 'k', 'l')
    values = ((4, 1), 4, 1)
    datatypes = ((int, int), int, int, (int, int), (int, int))
    types = (tuple, typemap['Quantity'], typemap['Quantity'], tuple, tuple)
    for ind, name in enumerate(names):
        var = next(v for v in var_list if v.name == name)
        assert var.value == values[ind]
        assert issubclass(var.type_, types[ind])
        if isinstance(var.type_.datatype, tuple):
            types_to_check = zip(var.type_.datatype, datatypes[ind])
            assert all(issubclass(t.datatype, dt) for t, dt in types_to_check)
        else:
            assert issubclass(var.type_.datatype, datatypes[ind])


def test_imported_function_call_returning_tuple(meta_model, model_kwargs):
    """test call of imported function returning a tuple"""
    inp = 'use divmod from builtins; q = divmod(4, 2); p = q[0]; r = q[1]\n'
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    var_p = next(v for v in var_list if v.name == 'p')
    assert var_p.value == 2
    assert var_p.type_ is None
    var_r = next(v for v in var_list if v.name == 'r')
    assert var_r.value == 0
    assert var_r.type_ is None


def test_tuple_if_function(meta_model, model_kwargs):
    """test a tuple with if function call"""
    inp = 'w = if(false, (1, 0), (0, 1)); t = w[0]; z = w[1]\n'
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    var_t = next(v for v in var_list if v.name == 't')
    assert var_t.value == 0
    assert issubclass(var_t.type_, typemap['Quantity'])
    assert issubclass(var_t.type_.datatype, int)
    var_z = next(v for v in var_list if v.name == 'z')
    assert var_z.value == 1
    assert issubclass(var_z.type_, typemap['Quantity'])
    assert issubclass(var_z.type_.datatype, int)


def test_assignment_of_tuple_with_type_mismatch(meta_model, model_kwargs):
    """test assignment of tuple object with type mismatch"""
    inp = 'f(x, y) = (x*x + y*y, 1); e = f(1, true)\n'
    match_str = 'Invalid type in expression'
    with pytest.raises(TextXError, match=match_str):
        meta_model.model_from_str(inp, **model_kwargs)


def test_tuple_function(meta_model, model_kwargs):
    """test function returning a Tuple"""
    inp = 'f(x, y) = (x, x*y, y); e = f(2.0, 3.0)\n'
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    var_e = next(v for v in var_list if v.name == 'e')
    assert var_e.value == (2., 6., 3.)
    assert issubclass(var_e.type_, tuple)
    types_to_check = zip(var_e.type_.datatype, (float, float, float))
    assert all(issubclass(t.datatype, dt) for t, dt in types_to_check)


def test_tuple_subscripting(meta_model, model_kwargs):
    """test subscripting a tuple"""
    inp = ("tup = (1, true, 'abc', (2, 3)); a = tup[0]; b = tup[1]; c = tup[3];"
           "d = tup[0::2]; e = tup[:-1]")
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    assert next(v for v in var_list if v.name == 'a').value == 1
    assert next(v for v in var_list if v.name == 'b').value is True
    assert next(v for v in var_list if v.name == 'c').value == (2, 3)
    assert next(v for v in var_list if v.name == 'd').value == (1, 'abc')
    assert next(v for v in var_list if v.name == 'e').value == (1, True, 'abc')


def test_series_elements_of_different_type(meta_model, model_kwargs):
    """series with elements of different type"""
    inp = 's1 = (numbers: 1, 2, true)\n'
    match_str = 'Series elements must have one type but 2 types were found'
    with pytest.raises(TextXError, match=match_str):
        meta_model.model_from_str(inp, **model_kwargs)


def test_table_columns_of_different_size(meta_model, model_kwargs):
    """table with columns of different size """
    inp = 't = ((temperature: 0, 1, 3), (pressure: 4., 5.))\n'
    match_str = 'Table columns must have one size but 2 sizes were found'
    with pytest.raises(TextXError, match=match_str):
        meta_model.model_from_str(inp, **model_kwargs)


def test_table_columns_with_repeating_names(meta_model, model_kwargs):
    """table with columns with repeating names """
    inp = 't = ((label: 0, 1, 3), (label: 4, 5, 6))\n'
    match_str = 'Repeating column names were found in table'
    with pytest.raises(TextXError, match=match_str):
        meta_model.model_from_str(inp, **model_kwargs)


def test_table_properties(meta_model, model_kwargs):
    """test table properties - slice, columns, indexed row, named column"""
    inp = ('t = ((temperature: 0, 1, 3), (pressure: 4., 5., 6.));'
           'a = t:columns; b = t[0]; c = t[0:1]; d = t[::-1];'
           'e = t.temperature; f = t.temperature[0]; g = t.pressure[1:];'
           'h = t.pressure[::-1]:array; i = t.pressure:name\n')
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    var_t = next(v for v in var_list if v.name == 't')
    assert issubclass(var_t.type_, typemap['Table'])
    assert isinstance(var_t.type_.datatype, tuple)
    assert len(var_t.type_.datatype) == 2
    assert issubclass(var_t.type_.datatype[0], int)
    assert issubclass(var_t.type_.datatype[1], float)
    assert var_t.type_.datalen == 3

    var_a = next(v for v in var_list if v.name == 'a')
    assert issubclass(var_a.type_, typemap['Series'])
    assert issubclass(var_a.type_.datatype, str)
    assert isinstance(var_a.value, typemap['Series'])
    assert issubclass(var_a.value.dtype.type, numpy.object_)
    assert var_a.value.name == 'columns'
    assert var_a.value.to_list() == ['temperature', 'pressure']

    var_b = next(v for v in var_list if v.name == 'b')
    assert issubclass(var_b.type_, tuple)
    assert isinstance(var_b.type_.datatype, tuple)
    assert len(var_b.type_.datatype) == 2
    assert issubclass(var_b.type_.datatype[0], int)
    assert issubclass(var_b.type_.datatype[1], float)
    assert var_b.value == (0, 4.0)

    var_c = next(v for v in var_list if v.name == 'c')
    assert issubclass(var_c.type_, typemap['Table'])
    assert isinstance(var_c.type_.datatype, tuple)
    assert len(var_c.type_.datatype) == 2
    assert issubclass(var_c.type_.datatype[0], int)
    assert issubclass(var_c.type_.datatype[1], float)
    assert var_c.type_.datalen == 1
    assert var_c.value.to_numpy().tolist()[0] == [0, 4.0]

    var_d = next(v for v in var_list if v.name == 'd')
    assert issubclass(var_d.type_, typemap['Table'])
    assert isinstance(var_d.type_.datatype, tuple)
    assert len(var_d.type_.datatype) == 2
    assert issubclass(var_d.type_.datatype[0], int)
    assert issubclass(var_d.type_.datatype[1], float)
    assert var_d.type_.datalen == 3
    assert var_d.value.to_numpy().tolist() == [[3, 6], [1, 5], [0, 4]]

    var_e = next(v for v in var_list if v.name == 'e')
    assert issubclass(var_e.type_, typemap['Series'])
    assert issubclass(var_e.type_.datatype, int)
    assert var_e.type_.datalen == 3
    assert var_e.value.to_numpy().tolist() == [0, 1, 3]

    var_f = next(v for v in var_list if v.name == 'f')
    assert issubclass(var_f.type_, typemap['Quantity'])
    assert issubclass(var_f.type_.datatype, int)
    assert var_f.value == 0

    var_g = next(v for v in var_list if v.name == 'g')
    assert issubclass(var_g.type_, typemap['Series'])
    assert issubclass(var_g.type_.datatype, float)
    assert var_g.type_.datalen == 2
    assert var_g.value.to_numpy().tolist() == [5., 6.]

    var_h = next(v for v in var_list if v.name == 'h')
    assert issubclass(var_h.type_, typemap['FloatArray'])
    assert issubclass(var_h.type_.datatype, float)
    assert var_h.type_.datalen == (3,)
    assert var_h.value.tolist() == [6., 5., 4.]
    var_i = next(v for v in var_list if v.name == 'i')
    assert issubclass(var_i.type_, str)
    assert var_i.value == 'pressure'


def test_iterable_non_literals_filter(meta_model, model_kwargs):
    """test iterable non-literals with a filter function"""
    inp = 't = ((number: 1, 2)); f = filter((x: x > 1), t.number); f0 = f[0]'
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    var = next(v for v in var_list if v.name == 'f0')
    assert issubclass(var.type_, typemap['Quantity'])
    assert issubclass(var.type_.datatype, int)
    assert var.value == 2


def test_iterable_non_literals_map(meta_model, model_kwargs):
    """test iterable non-literals with a map function"""
    inp = ('t = ((number: 1, 2)); s = t.number; m1 = map((x: 2*x), s);'
           'f1 = filter((x: x > 1), m1); f10 = f1[0]')
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    var = next(v for v in var_list if v.name == 'f10')
    assert issubclass(var.type_, typemap['Quantity'])
    assert issubclass(var.type_.datatype, int)
    assert var.value == 2


def test_iterable_non_literals_func(meta_model, model_kwargs):
    """test iterable non-literals with an internal function"""
    inp = ('t = ((number: 1, 2)); g(x) = x; t2 = g(t);'
           't2n = t2.number; t21 = t2[1]')
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    var = next(v for v in var_list if v.name == 't2n')
    assert issubclass(var.type_, typemap['Series'])
    assert var.type_.datatype is None
    assert var.value.values.tolist() == [1, 2]
    assert var.value.name == 'number'
    var = next(v for v in var_list if v.name == 't21')
    assert issubclass(var.type_, typemap['Tuple'])
    assert var.value == (2,)


def test_iterable_non_literals_query(meta_model, model_kwargs):
    """test iterable non-literals with a query"""
    inp = ('t = ((number: 1, 2)); g(x) = x; t2 = g(t);'
           't3 = t2 where number in (1, 2);'
           't4 = t2.number where number in (1, 2)')
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    var = next(v for v in var_list if v.name == 't3')
    assert issubclass(var.type_, typemap['Table'])
    assert var.type_.datatype is None
    assert var.value.values.tolist() == [[1], [2]]
    assert var.value.to_dict(orient='list') == {'number': [1, 2]}
    var = next(v for v in var_list if v.name == 't4')
    assert issubclass(var.type_, typemap['Series'])
    assert var.type_.datatype is None
    assert var.value.values.tolist() == [1, 2]


def test_series_properties(meta_model, model_kwargs):
    """test series properties - name, indexed value, slice, array"""
    inp = ('s1 = (numbers: 1, 2, 3); s2 = (letters: "a", "b", "c");'
           's3 = (booleans: true, false); a = s2; b = s1:name; c = s2[0:1]; '
           'c1 = s3[]; c2 = s3[:1]; c3 = s2[:3:1]; c4 = s2[:]; c5 = s2[::];'
           'd1 = s1[1]; d2 = s1[1:2]; d3 = s1[1:]; e = s2[::-1]:array;'
           'f = s1:array\n')
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    var_s1 = next(v for v in var_list if v.name == 's1')
    assert issubclass(var_s1.type_, typemap['Series'])
    assert issubclass(var_s1.type_.datatype, int)
    assert var_s1.type_.datalen == 3
    var_b = next(v for v in var_list if v.name == 'b')
    assert issubclass(var_b.type_, str)
    assert var_b.value == 'numbers'
    var_c = next(v for v in var_list if v.name == 'c')
    assert issubclass(var_c.type_, typemap['Series'])
    assert issubclass(var_c.type_.datatype, str)
    assert var_c.type_.datalen == 1
    assert var_c.value.to_list() == ['a']
    var_d1 = next(v for v in var_list if v.name == 'd1')
    assert issubclass(var_d1.type_, typemap['Quantity'])
    assert issubclass(var_d1.type_.datatype, int)
    assert var_d1.value == 2
    var_d2 = next(v for v in var_list if v.name == 'd2')
    assert issubclass(var_d2.type_, typemap['Series'])
    assert issubclass(var_d2.type_.datatype, int)
    assert var_d2.type_.datalen == 1
    assert var_d2.value.tolist() == [2]
    var_d3 = next(v for v in var_list if v.name == 'd3')
    assert issubclass(var_d3.type_, typemap['Series'])
    assert issubclass(var_d3.type_.datatype, int)
    assert var_d3.type_.datalen == 2
    assert var_d3.value.tolist() == [2, 3]
    var_e = next(v for v in var_list if v.name == 'e')
    assert issubclass(var_e.type_, typemap['StrArray'])
    assert issubclass(var_e.type_.datatype, str)
    assert var_e.type_.datalen == (3,)
    assert list(var_e.value) == ['c', 'b', 'a']
    var_f = next(v for v in var_list if v.name == 'f')
    assert issubclass(var_f.type_, typemap['IntArray'])
    assert issubclass(var_f.type_.datatype, int)
    assert var_f.type_.datalen == (3,)
    assert list(var_f.value) == [1, 2, 3]


def test_series_properties_invalid_columns_property(meta_model, model_kwargs):
    """test series with invalid columns property"""
    inp = 's = (numbers: 1, 2, 3); g = s:columns\n'
    match_str = 'Parameter of type Series has no property "columns"'
    with pytest.raises(TextXError, match=match_str):
        meta_model.model_from_str(inp, **model_kwargs)


def test_table_properties_invalid_name_property(meta_model, model_kwargs):
    """test table with invalid name property"""
    inp = 't = ((temperature: 0, 1, 3)); a = t:name\n'
    match_str = 'Parameter of type Table has no property "name"'
    with pytest.raises(TextXError, match=match_str):
        meta_model.model_from_str(inp, **model_kwargs)


def test_series_properties_invalid_array_property(meta_model, model_kwargs):
    """test series with invalid array property"""
    inp = 's = (numbers: 1, 2, 3); g = s[1]:array\n'
    match_str = 'Parameter of type Quantity has no property "array"'
    with pytest.raises(TextXError, match=match_str):
        meta_model.model_from_str(inp, **model_kwargs)


def test_table_properties_invalid_element_array_property(meta_model, model_kwargs):
    """test table with invalid element array property"""
    inp = 't = ((temperature: 0, 1, 3)); j = t[0]:array\n'
    match_str = 'Parameter of type Tuple has no property "array"'
    with pytest.raises(TextXError, match=match_str):
        meta_model.model_from_str(inp, **model_kwargs)


def test_table_properties_invalid_array_property(meta_model, model_kwargs):
    """test table with invalid array property"""
    inp = 't = ((temperature: 0, 1, 3)); j = t:array\n'
    match_str = 'Parameter of type Table has no property "array"'
    with pytest.raises(TextXError, match=match_str):
        meta_model.model_from_str(inp, **model_kwargs)


def test_object_properties_zero_slice(meta_model, model_kwargs):
    """test object slice with an invalid slice step"""
    inp = 's = (numbers: 1, 2, 3); g = s[1:2:0]\n'
    with pytest.raises(TextXError, match='Slice step cannot be zero'):
        meta_model.model_from_str(inp, **model_kwargs)


def test_series_properties_invalid_index(meta_model, model_kwargs):
    """test series slice with invalid index"""
    inp = 's = (numbers: 1, 2, 3); g = s[11]\n'
    with pytest.raises(TextXError, match='Index out of range'):
        meta_model.model_from_str(inp, **model_kwargs)


def test_table_properties_invalid_index(meta_model, model_kwargs):
    """test table slice with invalid index"""
    inp = 't = ((numbers: 1, 2, 3), (strings: "c", "a", "b")); g = t[7]\n'
    with pytest.raises(TextXError, match='Index out of range'):
        meta_model.model_from_str(inp, **model_kwargs)


def test_table_from_tuple(meta_model, model_kwargs):
    """test table from a tuple with parameters of series type"""
    inp = ('s = (booleans: true, false)\n'
           't = Table (s, (floats: 1.2, -3.5))\n')
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    t_var = next(v for v in var_list if v.name == 't')
    assert t_var.value['floats'][0] == 1.2
    assert t_var.value['booleans'][1].item() is False


def test_table_from_tuple_type_error(meta_model, model_kwargs):
    """test table from a tuple with parameters of wrong types"""
    inp = 'a = 3; s = (test: 1); t = Table(a, s)\n'
    match_str = 'The type of table column must be series'
    with pytest.raises(TextXError, match=match_str):
        meta_model.model_from_str(inp, **model_kwargs)


def test_series_query(meta_model, model_kwargs):
    """test series query"""
    inp = ('s = (n: 1, 2, 3, 4); s1 = s where column:n > 1 and column:n != 2;'
           's2 = s where n in (1, 2, 3)\n')
    var_list = get_children_of_type('Variable', meta_model.model_from_str(inp, **model_kwargs))
    s1_var = next(v for v in var_list if v.name == 's1')
    assert issubclass(s1_var.type_, typemap['Series'])
    assert issubclass(s1_var.type_.datatype, int)
    assert s1_var.type_.datalen is None
    assert s1_var.value.tolist() == [3, 4]
    s2_var = next(v for v in var_list if v.name == 's2')
    assert issubclass(s2_var.type_, typemap['Series'])
    assert issubclass(s2_var.type_.datatype, int)
    assert s2_var.type_.datalen is None
    assert s2_var.value.tolist() == [1, 2, 3]


def test_series_query_inverse_order_condition_1(meta_model, model_kwargs):
    """test series query w/ inverse order of column and operand in condition"""
    inp = ('s = (n: 1, 2, 3, 4); s1 = s where column:n > 1 and column:n != 2;'
           's2 = s where 1 < column:n and 2 != column:n')
    var_list = get_children_of_type('Variable', meta_model.model_from_str(inp, **model_kwargs))
    s1_var = next(v for v in var_list if v.name == 's1')
    s2_var = next(v for v in var_list if v.name == 's2')
    assert issubclass(s1_var.type_, typemap['Series'])
    assert issubclass(s2_var.type_, typemap['Series'])
    assert issubclass(s1_var.type_.datatype, int)
    assert issubclass(s2_var.type_.datatype, int)
    assert s1_var.type_.datalen is None
    assert s2_var.type_.datalen is None
    assert s1_var.value.tolist() == [3, 4]
    assert s2_var.value.tolist() == [3, 4]


def test_series_query_inverse_order_condition_2(meta_model, model_kwargs):
    """test w/ inverse order of column and operand in condition"""
    inp = ('s = (n: 1, 2, 3, 4); s1 = s where 2 == column:n; s2 = s where 2 != column:n;'
           'print(s1, s2)')
    model_val = meta_model.model_from_str(inp, **model_kwargs).value
    assert model_val == '(n: 2) (n: 1, 3, 4)'


def test_series_query_runtime_value_error(meta_model, model_kwargs):
    """test series query with runtime value errors"""
    inp = ("calc = ((algo: 'Fast', 'VeryFast'), (encut: 400.0, 350.) [eV], "
           "(en: 300., 400.) [eV]); s1 = calc.algo where column:encut > 400.;"
           "s2 = calc.encut where column:en >= column:encut")
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    for var in ('s1', 's2'):
        with pytest.raises(TextXError, match='column name must be') as err:
            _ = next(v for v in var_list if v.name == var).value
        assert isinstance(err.value.__cause__, RuntimeValueError)


def test_table_query_runtime_type_error(meta_model, model_kwargs):
    """test series query with runtime type errors"""
    inp = ("calc = ((algo: 'Fast', 'VeryFast'), (encut: 400.0, 350.) [eV], "
           "(en: 300., 400.) [eV]); t1 = calc where column:encut > column:algo;"
           "t2 = calc where column:encut > 'limit'")
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    for var in ('t1', 't2'):
        with pytest.raises(TextXError, match='invalid comparison of types') as err:
            _ = next(v for v in var_list if v.name == var).value
        assert isinstance(err.value.__cause__, RuntimeTypeError)


def test_table_query_inverse_order_condition(meta_model, model_kwargs):
    """test w/ inverse order of column and operand in condition"""
    inp = ("t = ((n: 1, 2), (s: '1', '2')); s1 = t select s where 2 == column:n;"
           "print(s1)")
    model_val = meta_model.model_from_str(inp, **model_kwargs).value
    assert model_val == "((s: '2'))"


def test_table_query_with_two_column_comparison(meta_model, model_kwargs):
    """test table query with two-column comparison"""
    inp = 't = ((a: 1, 2, 3), (b: 4, 5, 6)); tc = t where column:a < column:b and column:a > 1'
    var_list = get_children_of_type('Variable', meta_model.model_from_str(inp, **model_kwargs))
    tc_var = next(v for v in var_list if v.name == 'tc')
    assert issubclass(tc_var.type_, typemap['Table'])
    assert isinstance(tc_var.type_.datatype, tuple)
    assert issubclass(tc_var.type_.datatype[0], int)
    assert issubclass(tc_var.type_.datatype[1], int)
    assert tc_var.type_.datalen is None
    assert tc_var.value.to_dict(orient='list') == {'a': [2, 3], 'b': [5, 6]}


def test_series_query_property_chains(meta_model, model_kwargs):
    """test series query and property chains"""
    inp = ('s = (n: 1, 2, 3); sq = s where column:n > 1; sqq = sq where column:n > 2; '
           'sqqq = sqq where column:n != 3; sqqq_ref = sqqq; '
           'sqp = sp where column:n > 1; sp = s[0:2]; spq = sq[0]; sqpp = sq[0:1]\n')
    all_vars = get_children_of_type('Variable', meta_model.model_from_str(inp, **model_kwargs))
    assert all(issubclass(v.type_, typemap['Series']) for v in all_vars if 'sq' in v.name)
    assert all(issubclass(v.type_.datatype, int) for v in all_vars if 'sq' in v.name)
    assert all(v.type_.datalen is None for v in all_vars if 'sq' in v.name)
    assert next(issubclass(v.type_, typemap['Quantity']) for v in all_vars if v.name == 'spq')
    assert next(issubclass(v.type_.datatype, int) for v in all_vars if v.name == 'spq')
    assert next(v.value.tolist() == [3] for v in all_vars if v.name == 'sqq')
    assert next(v.value.tolist() == [] for v in all_vars if v.name == 'sqqq')
    assert next(v.value.tolist() == [] for v in all_vars if v.name == 'sqqq_ref')
    assert next(v.value.tolist() == [2] for v in all_vars if v.name == 'sqp')
    assert next(v.value == 2 for v in all_vars if v.name == 'spq')
    assert next(v.value.tolist() == [2] for v in all_vars if v.name == 'sqpp')


def test_series_reference(meta_model, model_kwargs):
    """test uses of series reference"""
    inp = ('s1 = (n: -1, 0, 1, 2); s2 = s1; t1 = ((t: -1, 0, 1, 2));'
           's1_q = s1 where column:n > -1; s1_f = filter((x: x > 0), s1_q);'
           's2_q = s2 where column:n > -1; s2_f = filter((x: x > 0), s2_q);'
           't1_q = t1.t where column:t > -1; t1_f = filter((x: x > 0), s1_q);'
           's1_p = s1[1:]; s1_fp = filter((x: x > 0), s1_p);'
           's2_p = s2[1:]; s2_fp = filter((x: x > 0), s2_p);'
           't1_ff = filter((x: x > 0), t1.t); s2_ff = filter((x: x > 0), s2);'
           'sq_m = map((x, y: x+y), s1_q, s2_q);'
           'sp_m = map((x, y: x+y), s1_p, s2_p);'
           's_qfm = map((x, y: x+y), s1_f, s2_f);'
           's_qmf = filter((x: x > 0), sq_m)\n')
    all_vars = get_children_of_type('Variable', meta_model.model_from_str(inp, **model_kwargs))
    assert all(issubclass(v.type_, typemap['Series']) for v in all_vars if '_f' in v.name)
    assert all(issubclass(v.type_.datatype, int) for v in all_vars if '_f' in v.name)
    assert all(v.type_.datalen is None for v in all_vars if '_f' in v.name)
    assert all(v.value.tolist() == [1, 2] for v in all_vars if '_f' in v.name)
    assert all(v.value.tolist() == [0, 2, 4] for v in all_vars if '_m' in v.name)
    assert all(issubclass(v.type_.datatype, int) for v in all_vars if '_m' in v.name)
    assert all(v.value.tolist() == [2, 4] for v in all_vars if v.name in ('s_qfm', 's_qmf'))
    assert all(issubclass(v.type_, typemap['Series']) for v in all_vars if v.name in ('s_qfm', 's_qmf'))
    assert all(issubclass(v.type_.datatype, int) for v in all_vars if v.name in ('s_qfm', 's_qmf'))
    assert all(v.type_.datalen is None for v in all_vars if v.name in ('s_qfm', 's_qmf'))


def test_nesting_range_map_filter_reduce(meta_model, model_kwargs):
    """test nesting of range, map, filter and reduce functions"""
    inp = ('a = reduce((x, y: x*y), filter((x: x > 0), map((x: 2*x), '
           'range(-3, 4, 1)))); b = sum(filter((x: x > 0), map((x: 2*x), '
           'range(-3, 4, 1)))); c = 6 in filter((x: x > 0), map((x: 2*x), '
           'range(-3, 4, 1)))')
    all_vars = get_children_of_type('Variable', meta_model.model_from_str(inp, **model_kwargs))
    assert next(issubclass(v.type_, typemap['Quantity']) for v in all_vars if v.name == 'a')
    assert next(issubclass(v.type_.datatype, int) for v in all_vars if v.name == 'a')
    assert next(issubclass(v.type_, typemap['Quantity']) for v in all_vars if v.name == 'b')
    assert next(issubclass(v.type_.datatype, int) for v in all_vars if v.name == 'b')
    assert next(issubclass(v.type_, bool) for v in all_vars if v.name == 'c')
    assert next(v.value == 48 for v in all_vars if v.name == 'a')
    assert next(v.value == 12 for v in all_vars if v.name == 'b')
    assert next(v.value is True for v in all_vars if v.name == 'c')


def test_map_size_mismatch(meta_model, model_kwargs):
    """test size mismatch in map function"""
    msg = 'map inputs must have equal size'
    with pytest.raises(TextXError, match=msg):
        meta_model.model_from_str('maps = map((x, y: x*y), (n: 1), (m: 2, 3))', **model_kwargs)


def test_map_arguments_number_mismatch(meta_model, model_kwargs):
    """test number of function arguments mismatch in map function"""
    msg = 'number of map function arguments and map inputs must be equal'
    with pytest.raises(TextXError, match=msg):
        meta_model.model_from_str('maps = map((x, y: x*y), (n: 1))', **model_kwargs)


def test_map_inputs_types(meta_model, model_kwargs):
    """test map inputs are of table or series types"""
    inp = 'p = (1, 2); maps = map((x, y: x*y), p, (n: 1, 2))'
    msg = 'map inputs must be either series or table-like'
    with pytest.raises(TextXError, match=msg):
        meta_model.model_from_str(inp, **model_kwargs)


def test_sum_non_numerical_types(meta_model, model_kwargs):
    """test use of non-numerical types in sum function"""
    msg = 'Series must be of type Number'
    with pytest.raises(TextXError, match=msg) as err:
        meta_model.model_from_str('invalid = sum((strings: "a", "1"))', **model_kwargs)
    assert isinstance(err.value.__cause__, StaticTypeError)
    msg = 'Sum accepts only inputs of numeric type'
    with pytest.raises(TextXError, match=msg) as err:
        meta_model.model_from_str('bsum = sum((bool: true, false))', **model_kwargs)
    assert isinstance(err.value.__cause__, StaticTypeError)


def test_filter_wrong_arguments_number(meta_model, model_kwargs):
    """test wrong number of function arguments in filter function"""
    msg = 'Filter function must have only one argument'
    with pytest.raises(TextXError, match=msg):
        meta_model.model_from_str('fi = filter((x, y: x > y), (n: 1, 2, 3))', **model_kwargs)


def test_filter_wrong_type(meta_model, model_kwargs):
    """test wrong type of function in filter function"""
    msg = 'Filter function must be of boolean type'
    with pytest.raises(TextXError, match=msg):
        meta_model.model_from_str('fi = filter((x: 2*x), (n: 1, 2, 3))', **model_kwargs)


def test_reduce_wrong_arguments_number(meta_model, model_kwargs):
    """test wrong type of function arguments in reduce function"""
    msg = 'Reduce function must have exactly two arguments'
    with pytest.raises(TextXError, match=msg):
        meta_model.model_from_str('re = reduce((x: x + 1), (n: 1, 2, 3))', **model_kwargs)


def test_boolean_reduce_parameters_wrong_type(meta_model, model_kwargs):
    """test wrong type of parameters in boolean reduce function"""
    msg = 'Boolean reduce parameters must be of boolean type'
    with pytest.raises(TextXError, match=msg):
        meta_model.model_from_str('bured = any((n: 1, 2, 3))', **model_kwargs)


def test_in_expression_wrong_type(meta_model, model_kwargs):
    """test wrong type of parameters in in-expression"""
    with pytest.raises(TextXError, match='Parameter must be series or reference to series'):
        meta_model.model_from_str('a = 1; print(1 in a)', **model_kwargs)


def test_table_query_property_chains(meta_model, model_kwargs):
    """test table query and property chains"""
    inp = ('tab = ((n: 1, 2, 3)); tq = tab where column:n > 1; tqq = tq where column:n > 2;'
           'tqqq = tqq where column:n == 3; tqqq_ref = tqqq;'
           'tqp = tp where column:n > 1; tp = tab[0:2]; tpq = tq[0]; tqpp = tq[0:1]\n')
    all_vars = get_children_of_type('Variable', meta_model.model_from_str(inp, **model_kwargs))
    assert all(issubclass(v.type_, typemap['Table']) for v in all_vars if 'tq' in v.name)
    assert all(issubclass(v.type_.datatype[0], int) for v in all_vars if 'tq' in v.name)
    assert all(v.type_.datalen is None for v in all_vars if 'tq' in v.name)
    assert next(issubclass(v.type_, tuple) for v in all_vars if v.name == 'tpq')
    assert next(isinstance(v.type_.datatype, tuple) for v in all_vars if v.name == 'tpq')
    assert next(len(v.type_.datatype) == 1 for v in all_vars if v.name == 'tpq')
    assert next(issubclass(v.type_.datatype[0], int) for v in all_vars if v.name == 'tpq')
    var_names = ('tq', 'tqq', 'tqqq', 'tqqq_ref', 'tqp', 'tqpp')
    var_values = ({'n': [2, 3]}, {'n': [3]}, {'n': [3]}, {'n': [3]}, {'n': [2]},
                  {'n': [2]})
    for var_name, var_value in zip(var_names, var_values):
        var = next(v for v in all_vars if v.name == var_name)
        assert var.value.to_dict(orient='list') == var_value
    assert next(v.value == (2,) for v in all_vars if v.name == 'tpq')


def test_table_query(meta_model, model_kwargs):
    """test table query"""
    inp = ('t = ((a: 1, 2, 3), (b: 4, 5, 6)); t1 = t select a, b where column:a > 3;'
           't2 = t select b where a in (3, 4, 5); t3 = t select a, b;'
           't4 = t where column:b != 4 select a; t5 = t where not (column:a > 1 and column:b < 6);'
           't6 = t where column:a > 1 or column:b < 6; t7 = t where all(column:a > 1, column:b < 6);'
           't8 = t where any(column:a > 1, column:b < 6); t9 = t select a where column:a > 2;'
           's = t.a where column:a > 2\n')
    var_list = get_children_of_type('Variable', meta_model.model_from_str(inp, **model_kwargs))
    var_names = ('t1', 't2', 't3', 't4', 't5', 't6', 't7', 't8', 't9')
    var_types = (((int, int), None), ((int,), None), ((int, int), 3),
                 ((int,), None), ((int, int), None), ((int, int), None),
                 ((int, int), None), ((int, int), None), ((int,), None))
    var_values = ({'a': [], 'b': []}, {'b': [6]},
                  {'a': [1, 2, 3], 'b': [4, 5, 6]},
                  {'a': [2, 3]}, {'a': [1, 3], 'b': [4, 6]},
                  {'a': [1, 2, 3], 'b': [4, 5, 6]},
                  {'a': [2], 'b': [5]}, {'a': [1, 2, 3], 'b': [4, 5, 6]}, {'a': [3]})
    for var_name, var_type, var_value in zip(var_names, var_types, var_values):
        var = next(v for v in var_list if v.name == var_name)
        assert issubclass(var.type_, typemap['Table'])
        assert isinstance(var.type_.datatype, tuple)
        assert len(var.type_.datatype) == len(var_type[0])
        all(issubclass(dt1, dt2) for dt1, dt2 in zip(var.type_.datatype, var_type[0]))
        assert var.type_.datalen == var_type[1]
        assert var.value.to_dict(orient='list') == var_value
    assert next(issubclass(v.type_, typemap['Series']) for v in var_list if v.name == 's')
    assert next(issubclass(v.type_.datatype, int) for v in var_list if v.name == 's')
    assert next(v.type_.datalen is None for v in var_list if v.name == 's')
    s_var_value = next(v.value for v in var_list if v.name == 's')
    assert {s_var_value.name: s_var_value.tolist()} == {'a': [3]}


def test_range_function(meta_model, model_kwargs):
    """test builtin range function"""
    inp = 'a = range(1, 10, 2); b = range from 0 to 1 step 0.2\n'
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    a_var = next(v for v in var_list if v.name == 'a')
    assert issubclass(a_var.type_, typemap['Series'])
    assert issubclass(a_var.type_.datatype, int)
    assert a_var.type_.datalen is None
    assert a_var.value.tolist() == [1, 3, 5, 7, 9]
    b_var = next(v for v in var_list if v.name == 'b')
    assert issubclass(b_var.type_, typemap['Series'])
    assert issubclass(b_var.type_.datatype, float)
    assert b_var.type_.datalen is None
    assert b_var.value.tolist() == pytest.approx([0.0, 0.2, 0.4, 0.6, 0.8])


def test_map_function_arithmetic_lambda(meta_model, model_kwargs):
    """test builtin map function of arithmetic type with lambda"""
    inp = 's1 = (n: 0, 1); s2 = (m: 2, 3); a = map((x, y: x+y), s1, s2)\n'
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    a_var = next(v for v in var_list if v.name == 'a')
    assert issubclass(a_var.type_, typemap['Series'])
    assert issubclass(a_var.type_.datatype, int)
    assert a_var.type_.datalen == 2
    assert a_var.value.tolist() == [2, 4]
    assert a_var.value.name == 'a'


def test_map_function_arithmetic_internal_function(meta_model, model_kwargs):
    """test builtin map function of arithmetic type with internal function"""
    inp = 'n = (numb: 1, 2); f(x) = 2*x; a = map(f, n)\n'
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    a_var = next(v for v in var_list if v.name == 'a')
    assert issubclass(a_var.type_, typemap['Series'])
    assert issubclass(a_var.type_.datatype, int)
    assert a_var.type_.datalen == 2
    assert a_var.value.tolist() == [2, 4]


def test_map_function_repeated_parameters(meta_model, model_kwargs):
    """test builtin map function with repeated parameters"""
    inp = ('a = 2; s = (n: 0, 1); f(x) = x*x; g(x) = 1 + a*x;'
           'h(x, y) = x*y + x - a; b = map(f, s); c = map(g, (n: 1, 2));'
           'd = map(h, s, (n: 1, 2))')
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    assert next(v for v in var_list if v.name == 'b').value.tolist() == [0, 1]
    assert next(v for v in var_list if v.name == 'c').value.tolist() == [3, 5]
    assert next(v for v in var_list if v.name == 'd').value.tolist() == [-2, 1]


def test_map_function_with_imported_function(meta_model, model_kwargs):
    """test builtin map function with imported function"""
    inp = ('use exp from numpy; s = (n: 0., 1.); e1 = map(exp, s);'
           'e2 = map((x: exp(x)), s); my_exp(x) = exp(x); e3 = map(my_exp, s)')
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    e1_var = next(v for v in var_list if v.name == 'e1')
    assert issubclass(e1_var.type_, typemap['Series'])
    assert e1_var.type_.datatype is None
    assert e1_var.type_.datalen == 2
    assert e1_var.value.tolist() == pytest.approx([1., 2.71828183])
    e2_var = next(v for v in var_list if v.name == 'e2')
    assert issubclass(e2_var.type_, typemap['Series'])
    assert e2_var.type_.datatype is None
    assert e2_var.type_.datalen == 2
    assert e2_var.value.tolist() == pytest.approx([1., 2.71828183])
    e3_var = next(v for v in var_list if v.name == 'e3')
    assert issubclass(e3_var.type_, typemap['Series'])
    assert e3_var.type_.datatype is None
    assert e3_var.type_.datalen == 2
    assert e3_var.value.tolist() == pytest.approx([1., 2.71828183])


def test_map_function_boolean_parameter(meta_model, model_kwargs):
    """test builtin map function with boolean parameter"""
    inp = 's = (b: true, false, true); a = map((x: not x), s)\n'
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    a_var = next(v for v in var_list if v.name == 'a')
    assert issubclass(a_var.type_, typemap['Series'])
    assert issubclass(a_var.type_.datatype, bool)
    assert a_var.type_.datalen == 3
    assert a_var.value.tolist() == [False, True, False]
    assert a_var.value.name == 'a'


def test_map_function_boolean_return_type(meta_model, model_kwargs):
    """test builtin map function with boolean return type"""
    inp = 'a = map((x: x > 0), (numbers: -1, 3, 5))\n'
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    a_var = next(v for v in var_list if v.name == 'a')
    assert issubclass(a_var.type_, typemap['Series'])
    assert issubclass(a_var.type_.datatype, bool)
    assert a_var.type_.datalen == 3
    assert a_var.value.tolist() == [False, True, True]
    assert a_var.value.name == 'a'


def test_map_function_multiple_params_in_global_scope(meta_model, model_kwargs):
    """test map function with a function with multiple parameters in global scope"""
    inp = ('a = (a: 2, 3); e = 2; p = 1; f(x) = x/p*e; b = map(f, a); print(b);'
           'print(map((x: x/p*e), a))')
    ref_out = '(b: 4.0, 6.0)\n(map: 4.0, 6.0)'
    assert meta_model.model_from_str(inp, **model_kwargs).value == ref_out


def test_reduce_in_internal_function_expression(meta_model, model_kwargs):
    """test reduce function in the expression of an internal function"""
    inp = 'min(s) = reduce((x, y: if(x<y, x, y)), s); a = (n: 2., 3.); print(min(a))'
    ref_out = '2.0'
    assert meta_model.model_from_str(inp, **model_kwargs).value == ref_out


def test_filter_function_lambda(meta_model, model_kwargs):
    """test builtin filter function with lambda"""
    inp = 's = (numb: 1, -1, 0, 2); a = filter((x: x > 0), s)\n'
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    a_var = next(v for v in var_list if v.name == 'a')
    assert issubclass(a_var.type_, typemap['Series'])
    assert issubclass(a_var.type_.datatype, int)
    assert a_var.type_.datalen is None
    assert a_var.value.tolist() == [1, 2]
    assert a_var.value.name == 'a'


def test_filter_function_internal_function(meta_model, model_kwargs):
    """test builtin filter function with internal function"""
    inp = 's = (n: 4, 5, 6); f(x) = x != 6; a = filter(f, s)\n'
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    a_var = next(v for v in var_list if v.name == 'a')
    assert issubclass(a_var.type_, typemap['Series'])
    assert issubclass(a_var.type_.datatype, int)
    assert a_var.type_.datalen is None
    assert a_var.value.tolist() == [4, 5]


def test_filter_function_repeated_parameters(meta_model, model_kwargs):
    """test builtin filter function with repeated parameters"""
    inp = ('a = 2; s1 = (n: 1, 2); f(x) = 2*x - a < 2; g(x) = (x*x - a) > 1;'
           'b = filter(f, (m: 1, 2)); c = filter(f, s1); d = filter(g, s1)')
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    assert next(v for v in var_list if v.name == 'b').value.tolist() == [1]
    assert next(v for v in var_list if v.name == 'c').value.tolist() == [1]
    assert next(v for v in var_list if v.name == 'd').value.tolist() == [2]


def test_filter_function_with_imported_function(meta_model, model_kwargs):
    """test builtin filter function with imported function"""
    inp = ('use isclose, isfinite from numpy; a = 2.0; b = (n: 1.0, 2.0, 3.0);'
           'c = filter((x: isclose(x, a)), b); e = filter(isfinite, b);'
           'd = filter((x: not isclose(x, a)), b)')
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    assert next(v for v in var_list if v.name == 'c').value.tolist() == [2]
    assert next(v for v in var_list if v.name == 'd').value.tolist() == [1, 3]
    assert next(v for v in var_list if v.name == 'e').value.tolist() == [1, 2, 3]


def test_reduce_function_lambda(meta_model, model_kwargs):
    """test builtin reduce function with lambda"""
    inp = ('t = ((n: 1, 2, 3)); a = reduce((x, y: x+y), t.n);'
           'b = reduce((x, y: x if x > y else y), t.n)')
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    a_var = next(v for v in var_list if v.name == 'a')
    assert issubclass(a_var.type_, typemap['Quantity'])
    assert issubclass(a_var.type_.datatype, int)
    assert a_var.value == 6
    b_var = next(v for v in var_list if v.name == 'b')
    assert issubclass(b_var.type_, typemap['Quantity'])
    assert issubclass(b_var.type_.datatype, int)
    assert b_var.value == 3


def test_reduce_function_internal_function(meta_model, model_kwargs):
    """test builtin reduce function with internal function"""
    inp = 's = (n: 1, 2, 3); f(x, y) = x + y; a = reduce(f, s)\n'
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    a_var = next(v for v in var_list if v.name == 'a')
    assert issubclass(a_var.type_, typemap['Quantity'])
    assert issubclass(a_var.type_.datatype, int)
    assert a_var.value == 6


def test_reduce_function_with_imported_function(meta_model, model_kwargs):
    """test builtin reduce function with imported function"""
    inp = ('b = (b: 30, 10, 2); use operator.floordiv; use builtins.max;'
           'floor = reduce(floordiv, b); maximum = reduce(max, b)')
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    floor = next(v for v in var_list if v.name == 'floor')
    maximum = next(v for v in var_list if v.name == 'maximum')
    assert floor.type_ is None
    assert floor.value == 1
    assert maximum.type_ is None
    assert maximum.value == 30


def test_sum_function(meta_model, model_kwargs):
    """test builtin sum function"""
    inp = ('a = sum(0, 1); s = (numb: 0, 1); b = sum(s); c = sum((n: 0, 1));'
           'd = sum(1)\n')
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    a_var = next(v for v in var_list if v.name == 'a')
    assert issubclass(a_var.type_, typemap['Quantity'])
    assert issubclass(a_var.type_.datatype, int)
    assert a_var.value == 1
    b_var = next(v for v in var_list if v.name == 'b')
    assert issubclass(b_var.type_, typemap['Quantity'])
    assert issubclass(b_var.type_.datatype, int)
    assert b_var.value == 1
    c_var = next(v for v in var_list if v.name == 'c')
    assert issubclass(c_var.type_, typemap['Quantity'])
    assert issubclass(c_var.type_.datatype, int)
    assert c_var.value == 1
    d_var = next(v for v in var_list if v.name == 'd')
    assert issubclass(d_var.type_, typemap['Quantity'])
    assert issubclass(d_var.type_.datatype, int)
    assert d_var.value == 1


def test_all_function(meta_model, model_kwargs):
    """test builtin all function"""
    inp = ('a = all(true, false); s = (b: true, false); b = all(s); f = all(null, true);'
           'c = all((b: true, false)); d = all(true); e = all((n: null, true))')
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    a_var = next(v for v in var_list if v.name == 'a')
    assert issubclass(a_var.type_, bool)
    assert a_var.value is False
    b_var = next(v for v in var_list if v.name == 'b')
    assert issubclass(b_var.type_, bool)
    assert b_var.value is False
    c_var = next(v for v in var_list if v.name == 'c')
    assert issubclass(c_var.type_, bool)
    assert c_var.value is False
    d_var = next(v for v in var_list if v.name == 'd')
    assert issubclass(d_var.type_, bool)
    assert d_var.value is True
    e_var = next(v for v in var_list if v.name == 'e')
    assert issubclass(e_var.type_, bool)
    assert e_var.value is None
    f_var = next(v for v in var_list if v.name == 'f')
    assert issubclass(f_var.type_, bool)
    assert f_var.value is None


def test_any_function(meta_model, model_kwargs):
    """test builtin any function"""
    inp = ('a = any(true, false); s = (b: true, false); b = any(s); f = any(null, false);'
           'c = any((b: true, false)); d = any(false); e = any((n: null, false))')
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    a_var = next(v for v in var_list if v.name == 'a')
    assert issubclass(a_var.type_, bool)
    assert a_var.value is True
    b_var = next(v for v in var_list if v.name == 'b')
    assert issubclass(b_var.type_, bool)
    assert b_var.value is True
    c_var = next(v for v in var_list if v.name == 'c')
    assert issubclass(c_var.type_, bool)
    assert c_var.value is True
    d_var = next(v for v in var_list if v.name == 'd')
    assert issubclass(d_var.type_, bool)
    assert d_var.value is False
    e_var = next(v for v in var_list if v.name == 'e')
    assert issubclass(e_var.type_, bool)
    assert e_var.value is None
    f_var = next(v for v in var_list if v.name == 'f')
    assert issubclass(f_var.type_, bool)
    assert f_var.value is None


def test_in_expression(meta_model, model_kwargs):
    """test builtin in expression"""
    inp = ('s = (n: 0, 1); a = 1 in s; t = ((n: 0, 1), (m: 2, 3)); f = 3 in (null, 4);'
           'b = 4 in t.m; c = 3 in (5, 3, 4); d = 2 in (1); e = 3 in (n: null, 4)')
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    a_var = next(v for v in var_list if v.name == 'a')
    assert issubclass(a_var.type_, bool)
    assert a_var.value is True
    b_var = next(v for v in var_list if v.name == 'b')
    assert issubclass(b_var.type_, bool)
    assert b_var.value is False
    c_var = next(v for v in var_list if v.name == 'c')
    assert issubclass(c_var.type_, bool)
    assert c_var.value is True
    d_var = next(v for v in var_list if v.name == 'd')
    assert issubclass(d_var.type_, bool)
    assert d_var.value is False
    e_var = next(v for v in var_list if v.name == 'e')
    assert issubclass(e_var.type_, bool)
    assert e_var.value is None
    f_var = next(v for v in var_list if v.name == 'f')
    assert issubclass(f_var.type_, bool)
    assert f_var.value is None


def test_array(meta_model, model_kwargs):
    """test the arrays"""
    inp = ('arr1 = [1, 3., 4.] [ns]; arr2 = [1]; arr3 = [true, false];'
           'arr4 = [[1., 2], [3, 4]] [angstrom]; arr5 = ["a", "ab"]')
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    arr1 = next(v for v in var_list if v.name == 'arr1')
    assert issubclass(arr1.type_, typemap['FloatArray'])
    assert issubclass(arr1.type_.datatype, float)
    assert arr1.type_.arraytype
    assert arr1.value.magnitude.tolist() == [1., 3., 4.]
    assert str(arr1.value.units) == 'nanosecond'

    arr2 = next(v for v in var_list if v.name == 'arr2')
    assert issubclass(arr2.type_, typemap['IntArray'])
    assert issubclass(arr2.type_.datatype, int)
    assert arr2.type_.arraytype
    assert arr2.value.tolist() == [1]
    assert all(str(e.units) in ['dimensionless', ''] for e in arr2.value.tolist())

    arr3 = next(v for v in var_list if v.name == 'arr3')
    assert issubclass(arr3.type_, typemap['BoolArray'])
    assert issubclass(arr3.type_.datatype, bool)
    assert arr3.type_.arraytype
    assert arr3.value.tolist() == [True, False]
    assert arr3.value.dtype.type is numpy.bool_

    arr4 = next(v for v in var_list if v.name == 'arr4')
    assert issubclass(arr4.type_, typemap['FloatArray'])
    assert issubclass(arr4.type_.datatype, float)
    assert arr4.type_.arraytype
    assert arr4.value.magnitude.tolist() == [[1., 2], [3, 4]]
    assert str(arr4.value.units) == 'angstrom'

    arr5 = next(v for v in var_list if v.name == 'arr5')
    assert issubclass(arr5.type_, typemap['StrArray'])
    assert issubclass(arr5.type_.datatype, str)
    assert arr5.type_.arraytype
    assert arr5.value.tolist() == ['a', 'ab']
    assert arr5.value.dtype.type is numpy.str_


def test_array_property_indexing_slicing(meta_model, model_kwargs):
    """test array indexing and slicing"""
    inp = ('a = [[1, 2], [3, 4]] [m]; b = (a[0], a[1][0], a[1][0:1:1], '
           'a[1][::-1], a[:1])')
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    bval = next(v for v in var_list if v.name == 'b').value
    for val in bval:
        assert str(val.units) == 'meter'
    assert numpy.array_equal(bval[0].magnitude, numpy.array([1, 2]))
    assert bval[1].magnitude == 3
    assert numpy.array_equal(bval[2].magnitude, numpy.array([3]))
    assert numpy.array_equal(bval[3].magnitude, numpy.array([4, 3]))
    assert numpy.array_equal(bval[4].magnitude, numpy.array([[1, 2]]))


def test_array_property_indexing_slicing_errors(meta_model, model_kwargs):
    """test array indexing and slicing errors"""
    inps = ('a = [[1, 2], [3, 4]] [m]; print(a[2])',
            'a = [[1, 2], [3, 4]] [m]; b = a[1][3]',
            'a = [[1, 2], [3, 4]] [m]; b = a[:2]:array',
            'a = [[1, 2], [3, 4]] [m]; print(a:columns)',
            'a = [[1, 2], [3, 4]] [m]; print(a[1][1]:array)',
            'a = [[1, 2], [3, 4]] [m]; print(a:name)')
    msgs = ('Index out of range, index: 2, data length: 2',
            'Index out of range, index: 3, data length: 2',
            'Parameter of type IntArray has no property "array"',
            'Parameter of type IntArray has no property "columns"',
            'Parameter of type Quantity has no property "array"',
            'Parameter of type IntArray has no property "name"')
    for inp, msg in zip(inps, msgs):
        with pytest.raises(TextXError, match=msg):
            meta_model.model_from_str(inp, **model_kwargs)


def test_indexing_array_from_series(meta_model, model_kwargs):
    """test indexing an array retrieved from series"""
    inps = ('ser = (d: 1.0) [nm]; arr = ser:array; print(arr[0])',
            'ser = (b: true, false); arr = ser:array; print(arr[1])',
            'ser = (s: "a", "b", "abc"); arr = ser:array; print(arr[2])')
    refs = ('1.0 [nanometer]', 'false', "\'abc\'")
    for inp, ref in zip(inps, refs):
        assert meta_model.model_from_str(inp, **model_kwargs).value == ref


def test_scalar_parameters_in_expression(meta_model, model_kwargs):
    """test expressions with general scalar parameters"""
    inp = ('s = (numbers: 1, 2); b = (bools: true, false);'
           'nsum = 2*sum(s);'
           'nallb = not all(b);'
           'nanyb = not any(b);'
           'red = 2*reduce((x, y: x+y), s);'
           'nin = not (0 in s);'
           'ifnin = 2*if(not (0 in s), 1, 0)')
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    nsum = next(v for v in var_list if v.name == 'nsum')
    assert issubclass(nsum.type_, typemap['Quantity'])
    assert issubclass(nsum.type_.datatype, int)
    assert nsum.value == 6
    nallb = next(v for v in var_list if v.name == 'nallb')
    assert issubclass(nallb.type_, bool)
    assert nallb.value is True
    nanyb = next(v for v in var_list if v.name == 'nanyb')
    assert issubclass(nanyb.type_, bool)
    assert nanyb.value is False
    red = next(v for v in var_list if v.name == 'red')
    assert issubclass(red.type_, typemap['Quantity'])
    assert issubclass(red.type_.datatype, int)
    assert red.value == 6
    nin = next(v for v in var_list if v.name == 'nin')
    assert issubclass(nin.type_, bool)
    assert nin.value is True
    ifnin = next(v for v in var_list if v.name == 'ifnin')
    assert issubclass(ifnin.type_, typemap['Quantity'])
    assert issubclass(ifnin.type_.datatype, int)
    assert ifnin.value == 2


def test_series_with_string_names_1(meta_model, model_kwargs):
    """test series with names containing spaces"""
    inp = ('params = (("use resolution of identity": true, false),'
           '(\'total charge\': -1, 0),  (multiplicity: 2, 1));'
           "ri_flg = params.'use resolution of identity'[0];"
           'ri_rec = params select "total charge" where column:\'use resolution of identity\' == true;'
           "tc_rec = params select 'use resolution of identity' where column:'total charge' != 0")
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    ri_flg = next(v for v in var_list if v.name == 'ri_flg')
    assert issubclass(ri_flg.type_, typemap['Boolean'])
    assert ri_flg.value is True
    tc_rec = next(v for v in var_list if v.name == 'tc_rec')
    assert issubclass(tc_rec.type_, typemap['Table'])
    assert len(tc_rec.value['use resolution of identity']) == 1
    assert tc_rec.value['use resolution of identity'][0].item() is True


def test_series_with_string_names_2(meta_model, model_kwargs):
    """test series with names containing spaces"""
    inp = ("t1 = (('final temperature': 0., 1., 3.) [kelvin], (pressure: 4., 5., 6.) [bar]);"
           "a = t1.'final temperature'; b = t1.'final temperature'[0];"
           "t2 = t1 select 'final temperature', pressure where column:pressure < 6.0 [bar] and"
           "column:'final temperature' > 0 [K]")
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    var_a = next(v for v in var_list if v.name == 'a')
    assert issubclass(var_a.type_, typemap['Series'])
    assert var_a.value.values.data.tolist() == [0., 1., 3.]
    assert var_a.value.values.quantity.units == 'kelvin'
    var_b = next(v for v in var_list if v.name == 'b')
    assert issubclass(var_b.type_, typemap['Quantity'])
    assert var_b.value.magnitude == 0.
    assert var_b.value.units == 'kelvin'
    var_t2 = next(v for v in var_list if v.name == 't2')
    assert issubclass(var_t2.type_, typemap['Table'])
    reference = [{'final temperature': typemap['Quantity'](1.0, 'kelvin'),
                  'pressure': typemap['Quantity'](5.0, 'bar')}]
    assert var_t2.value.to_dict(orient='records') == reference


def test_empty_iterable(meta_model, model_kwargs):
    """test empty iterables as result of queries and slicing"""
    inp = ('s = (length: 1., 2., 3.) [meter]; t = ((number: 1, 2, 3));'
           'print(s where column:length > 3 [km]); print(t where column:number > 3);'
           'print(t[0:0]); print(s[1:0:1]); print(t.number[0:0])')
    ref = '(length:) [meter]\n((number:))\n((number:))\n(length:) [meter]\n(number:)'
    prog = meta_model.model_from_str(inp, **model_kwargs)
    assert prog.value == ref


def test_last_element(meta_model, model_kwargs):
    """test indexing the last element"""
    inp = ('s = (length: 1, 2, 3) [meter]; print(s[-1]);'
           't = ((number: 1, 2, 3)); print(t[-1]); print(t.number[-1])')
    ref_output = '3 [meter]\n(3,)\n3'
    assert meta_model.model_from_str(inp, **model_kwargs).value == ref_output


def test_functions_of_series_with_null(meta_model, model_kwargs):
    """test map, reduce, filter functions with series containing null"""
    inp = ('a = (a: 1, 2, null);'
           'b = (b: 4., null, 6.) [kg];'
           's = (booleans: null, false, true);'
           't = ((a: -1, null, 3), (b: 4, 5, null));'
           'a1 = filter((x: x != 2), a);'
           'a2 = filter((x: x == 2), a);'
           'b1 = filter((x: x > 1 [kg]), b);'
           'c = map((x, y: x+y), t.a, t.b);'
           'd = map((x: not x), s);'
           'e = map((x: x > 0), t.a);'
           'h = map((x: 2*x), b);'
           'summe1 = reduce((x, y: x*y), a);'
           'summe2 = sum(b);'
           'and_reduce = reduce((x, y: (x and y)), (boolean: true, true, null));'
           'or_reduce = reduce((x, y: (x or y)), (boolean: true, false, null))')
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    var_a1_vals = next(v for v in var_list if v.name == 'a1').value.to_list()
    assert var_a1_vals[0].magnitude == 1
    assert len(var_a1_vals) == 1
    var_a2_vals = next(v for v in var_list if v.name == 'a2').value.to_list()
    assert var_a2_vals[0].magnitude == 2
    var_b1_vals = next(v for v in var_list if v.name == 'b1').value.to_list()
    assert var_b1_vals[0].magnitude == 4.
    assert var_b1_vals[1].magnitude == 6.
    var_c_vals = next(v for v in var_list if v.name == 'c').value.to_list()
    assert var_c_vals[0].magnitude == 3
    assert str(var_c_vals[1].magnitude) == '<NA>'
    assert str(var_c_vals[2].magnitude) == '<NA>'
    var_d_vals = next(v for v in var_list if v.name == 'd').value.to_list()
    assert var_d_vals[0] is None
    assert var_d_vals[1] is True
    assert var_d_vals[2] is False
    var_e_vals = next(v for v in var_list if v.name == 'e').value.to_list()
    assert var_e_vals[0] is False
    assert var_e_vals[1] is None
    assert var_e_vals[2] is True
    var_h_vals = next(v for v in var_list if v.name == 'h').value.to_list()
    assert all(v.units == 'kilogram' for v in var_h_vals)
    assert var_h_vals[0].magnitude == 8.
    assert str(var_h_vals[1].magnitude) == '<NA>'
    assert var_h_vals[2].magnitude == 12.
    assert str(next(v for v in var_list if v.name == 'summe1').value.magnitude) == '<NA>'
    var_s2_val = next(v for v in var_list if v.name == 'summe2').value
    assert str(var_s2_val.magnitude) == '<NA>'
    assert var_s2_val.units == 'kilogram'
    assert next(v for v in var_list if v.name == 'and_reduce').value is None
    assert next(v for v in var_list if v.name == 'or_reduce').value is True


def test_series_of_complex_type_and_functions(meta_model, model_kwargs):
    """series of complex type and operations"""
    inp = ('s = (z: 1 + 1 j, 1 - 1 j) [m]; sreal = map((x: real(x)), s);'
           'simag = map((x: imag(x)), s); spos = filter((x: (imag(x) > 0 [m])), s);'
           'sred = reduce((x, y: x*y), s); scnjg = map((x: (real(x)-imag(x)*0+1 j)), s);'
           'print(s, sreal, simag, spos, sred, scnjg)')
    prog = meta_model.model_from_str(inp, **model_kwargs)
    output = ('(z: 1.0+1.0 j, 1.0-1.0 j) [meter] (sreal: 1.0, 1.0) [meter] '
              '(simag: 1.0, -1.0) [meter] (spos: 1.0+1.0 j) [meter] '
              '2.0+0.0 j [meter ** 2] (scnjg: 1.0-1.0 j, 1.0+1.0 j) [meter]')
    assert prog.value == output


def test_array_of_complex_type(meta_model, model_kwargs):
    """arrays of complex type"""
    inp = 'arr = [[1, 0. j], [0., 1 j]] [m]; print(arr)'
    prog = meta_model.model_from_str(inp, **model_kwargs)
    output = '[[1.0+0.0 j, 0.0+0.0 j], [0.0+0.0 j, 0.0+1.0 j]] [meter]'
    assert prog.value == output


def test_arrays_in_series(meta_model, model_kwargs):
    """arrays in series"""
    inp = ('si1 = (arr: [1, 0]); si2 = (arr: [1, 0] [m]); sr1 = (arr: [1., 0]) [m];'
           'sr2 = (arr: [1., 0] [m]); sc1 = (arr: [1.+0. j, 0]) [m];'
           'sc2 = (arr: [1., 0+0 j] [m]); scc2 = (arr: [[1.], [0+0 j]] [m]);'
           'print(si1, si2, sr1, sr2, sc1, sc2, scc2)')
    prog = meta_model.model_from_str(inp, **model_kwargs)
    output = ('(arr: [1, 0]) (arr: [1, 0]) [meter] (arr: [1.0, 0.0]) [meter] (arr: '
              '[1.0, 0.0]) [meter] (arr: [1.0+0.0 j, 0.0+0.0 j]) [meter] (arr: '
              '[1.0+0.0 j, 0.0+0.0 j]) [meter] (arr: [[1.0+0.0 j], [0.0+0.0 j]]) '
              '[meter]')
    assert prog.value == output


def test_array_in_series_from_issue(meta_model, model_kwargs):
    """array in series (test case from issue #196)"""
    inp = ('d1 = (dipole: [0.59656566009308, 0.59656566009677, -1.3e-13]) [bohr * elementary_charge]\n'
           'd2 = (dipole: [0.59656566009308, 0.59656566009677, -1.3e-13] [bohr * elementary_charge])\n'
           'print(d1); print(d2); print(d1 [debye]); print(d2 [debye])\n'
           'print(d1[0] [debye]); print(d2[0] [debye])')
    output = ('(dipole: [0.59656566009308, 0.59656566009677, -1.3e-13]) [bohr * elementary_charge]\n'
              '(dipole: [0.59656566009308, 0.59656566009677, -1.3e-13]) [bohr * elementary_charge]\n'
              '(dipole: [1.516318662573084, 1.5163186625824632, -3.304270415158405e-13]) [debye]\n'
              '(dipole: [1.516318662573084, 1.5163186625824632, -3.304270415158405e-13]) [debye]\n'
              '[1.516318662573084, 1.5163186625824632, -3.304270415158405e-13] [debye]\n'
              '[1.516318662573084, 1.5163186625824632, -3.304270415158405e-13] [debye]')
    prog = meta_model.model_from_str(inp, **model_kwargs)
    assert prog.value == output


def test_array_from_series_from_issue(meta_model, model_kwargs):
    """array from series (test case from issue #265)"""
    inp = ('time = map((x: 0.5*x), range(0 [day], 10 [day], 1 [day]));'
           'print(time:array)')
    output = '[0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5] [day]'
    prog = meta_model.model_from_str(inp, **model_kwargs)
    assert prog.value == output


def test_array_from_series_with_unknown_datatype(meta_model, model_kwargs, tmp_yaml):
    """array from series with unknown datatype (test case from issue #443)"""
    ser_dct = {'_fw_name': '{{virtmat.language.utilities.serializable.FWSeries}}',
               '_version': 7, 'data': [1, 2], 'datatype': 'int', 'name': 'a',
               'units': 'dimensionless'}
    with open(tmp_yaml, 'w', encoding='utf-8') as fh:
        yaml.safe_dump(ser_dct, fh)
    inp = f"s = Series from file \'{tmp_yaml}\'; print(s:array)"
    assert meta_model.model_from_str(inp, **model_kwargs).value == '[1, 2]'


def test_array_from_series_with_wrong_dtype(meta_model, model_kwargs):
    """array from series with wrong datatype"""
    inp = 's = (a: (b: 1)); print(s:array)'
    msg = 'array datatype must be numeric, boolean, string or array'
    with pytest.raises(TextXError, match=msg) as err:
        meta_model.model_from_str(inp, **model_kwargs)
    assert isinstance(err.value.__cause__, StaticTypeError)


def test_array_from_series_with_wrong_dtype_rt(meta_model, model_kwargs, tmp_yaml):
    """array from series with wrong datatype at runtime"""
    ser_dct = {'_fw_name': '{{virtmat.language.utilities.serializable.FWSeries}}',
               '_version': 7,
               'data': [{'_fw_name': '{{virtmat.language.utilities.serializable.FWSeries}}',
                         '_version': 7, 'data': [1], 'datatype': 'int', 'name': 'b',
                         'units': 'dimensionless'}], 'datatype': 'object', 'name': 'a'}
    with open(tmp_yaml, 'w', encoding='utf-8') as fh:
        yaml.safe_dump(ser_dct, fh)
    inp = f"s = Series from file \'{tmp_yaml}\'; ar = s:array"
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    var_s = next(v for v in var_list if v.name == 'ar')
    msg = 'array datatype must be numeric, boolean, string or array'
    with pytest.raises(TextXError, match=msg) as err:
        _ = var_s.value
    assert isinstance(err.value.__cause__, RuntimeTypeError)


def test_series_of_int_arrays(meta_model, model_kwargs):
    """series of arrays of int type"""
    inp = ('series_var = (cell: [[12, 0, 0], [0, 12, 0], [0, 0, 12]] [angstrom])\n'
           'array_var = series_var[0]\n'
           'element_var = array_var[1][1]\n'
           'print(element_var)')
    assert meta_model.model_from_str(inp, **model_kwargs).value == '12 [angstrom]'


def test_series_of_float_arrays(meta_model, model_kwargs):
    """series of arrays of float type"""
    inp = ('series_var = (cell: [[12., 0., 0.], [0., 12., 0.], [0., 0., 12.]] [angstrom])\n'
           'array_var = series_var[0]\n'
           'element_var = array_var[1][1]\n'
           'print(element_var)')
    assert meta_model.model_from_str(inp, **model_kwargs).value == '12.0 [angstrom]'


def test_series_of_complex_arrays(meta_model, model_kwargs):
    """series of arrays of complex type"""
    inp = ('series_var = (tensor: [[12., 0.+3. j], [0.+3. j, 12.]] [angstrom])\n'
           'array_var = series_var[0]\n'
           'element_var = array_var[1][1]\n'
           'print(element_var)')
    assert meta_model.model_from_str(inp, **model_kwargs).value == '12.0+0.0 j [angstrom]'


def test_series_of_int_arrays_alternative_formatting(meta_model, model_kwargs):
    """series of arrays of int type with alternative formatting"""
    inp = ('series_var = (cell: [[12, 0, 0], [0, 12, 0], [0, 0, 12]]) [angstrom]\n'
           'array_var = series_var[0]\n'
           'element_var = array_var[1][1]\n'
           'print(element_var)')
    assert meta_model.model_from_str(inp, **model_kwargs).value == '12 [angstrom]'


def test_series_of_float_arrays_alternative_formatting(meta_model, model_kwargs):
    """series of arrays of float type with alternative formatting"""
    inp = ('d = (dipole: [0.59656566009308, 0.59656566009677, -1.3e-13])'
           '    [bohr * elementary_charge]\n'
           'print(d[0][0] [debye])')
    output = '1.516318662573084 [debye]'
    assert meta_model.model_from_str(inp, **model_kwargs).value == output


def test_series_of_complex_arrays_alternative_formatting(meta_model, model_kwargs):
    """series of arrays of complex type with alternative formatting"""
    inp = ('series_var = (tensor: [[12., 0.+3. j], [0.+3. j, 12.]]) [angstrom]\n'
           'array_var = series_var[0]\n'
           'element_var = array_var[1][1]\n'
           'print(element_var)')
    assert meta_model.model_from_str(inp, **model_kwargs).value == '12.0+0.0 j [angstrom]'


def test_sum_function_in_numeric_expression(meta_model, model_kwargs):
    """sum function as first parameter of a numeric expression"""
    inp = 's = (n: 1, 2); d = sum(s) + 1; print(d)'
    assert meta_model.model_from_str(inp, **model_kwargs).value == '4'


def test_filter_table(meta_model, model_kwargs):
    """test filter function on table type data"""
    inp = 't = ((a: 7, 2, 3), (b: 4, 5, 2)); print(filter((x: x.a > x.b), t))'
    ref = '((a: 7, 3), (b: 4, 2))'
    assert meta_model.model_from_str(inp, **model_kwargs).value == ref


def test_map_table(meta_model, model_kwargs):
    """test map function on table type data"""
    inp = 't = ((a: 1, 2), (b: 4, 5)); print(map((x: {a: x.a, b: x.b, c: x.a + x.b}), t))'
    ref = '((a: 1, 2), (b: 4, 5), (c: 5, 7))'
    assert meta_model.model_from_str(inp, **model_kwargs).value == ref


def test_reduce_table(meta_model, model_kwargs):
    """test reduce function on table type data"""
    inp = ('t = ((a: 1, 2, 3), (b: 4, 5, 6)); t_ = reduce((x, y: {a: x.a + y.a, '
           'b: x.b * y.b}), t); print(t_)')
    ref = '((a: 6), (b: 120))'
    assert meta_model.model_from_str(inp, **model_kwargs).value == ref
