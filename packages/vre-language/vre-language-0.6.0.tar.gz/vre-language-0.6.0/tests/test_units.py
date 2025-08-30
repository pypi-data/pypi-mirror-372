"""
tests for the units system
"""
import pytest
from textx import get_children_of_type
from textx.exceptions import TextXError
from pint.errors import DimensionalityError, UndefinedUnitError
from virtmat.language.utilities.errors import InvalidUnitError


def test_units_number_literal(meta_model, model_kwargs):
    """test a number literal with units"""
    prog = meta_model.model_from_str('t = 2 [seconds]; n = 3; tn = t * n', **model_kwargs)
    var_objs = get_children_of_type('Variable', prog)
    t_var = next(v for v in var_objs if v.name == 't')
    assert t_var.value.magnitude == 2
    assert str(t_var.value.units) == 'second'
    n_var = next(v for v in var_objs if v.name == 'n')
    assert n_var.value.magnitude == 3
    assert str(n_var.value.units) in ['dimensionless', '']
    tn_var = next(v for v in var_objs if v.name == 'tn')
    assert tn_var.value.magnitude == 6
    assert str(tn_var.value.units) == 'second'


def test_units_expression_literal(meta_model, model_kwargs):
    """test an expression literal with units"""
    prog = meta_model.model_from_str('l = (10 [meter] / 2 - 2 * 100 [cm]) / 3', **model_kwargs)
    var_objs = get_children_of_type('Variable', prog)
    l_var = next(v for v in var_objs if v.name == 'l')
    assert l_var.value.magnitude == 1
    assert str(l_var.value.units) == 'meter'


def test_units_expression_literal_with_error(meta_model, model_kwargs):
    """test an expression literal with units with error"""
    model_str = 'l = (10 [meter] / 2 - 2 * 100 ) / 3'
    prog = meta_model.model_from_str(model_str, **model_kwargs, source_code=model_str)
    var_objs = get_children_of_type('Variable', prog)
    l_var = next(v for v in var_objs if v.name == 'l')
    msg = (r'Cannot convert from \'meter\' \(\[length\]\) to \'dimensionless\' '
           r'\(dimensionless\)')
    with pytest.raises(TextXError, match=msg) as err_info:
        assert l_var.value.magnitude == 1
    assert isinstance(err_info.value.__cause__, DimensionalityError)


def test_units_tuple_variables(meta_model, model_kwargs):
    """test tuple variables with units"""
    prog_inp = ('a = (6 [kilometer], 3 [seconds]); c = 1 [speed_of_light];'
                'ratio = a[0]/a[1]/c')
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    var_objs = get_children_of_type('Variable', prog)
    ratio = next(v for v in var_objs if v.name == 'ratio').value.to_reduced_units()
    assert ratio == pytest.approx(6.67128e-06)
    assert str(ratio.units) in ['dimensionless', '']


def test_units_variables_powers(meta_model, model_kwargs):
    """test variables with units with powers"""
    prog_inp = ('a = 10 [meter ** 3] / 10 [meter**+2]; b = 1 [meter ** -1.];'
                'c = 1 [seconds ** -1.5]')
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    var_objs = get_children_of_type('Variable', prog)
    var_a = next(v for v in var_objs if v.name == 'a').value.to_reduced_units()
    assert var_a.magnitude == 1.0
    assert str(var_a.units) == 'meter'
    var_b = next(v for v in var_objs if v.name == 'b').value.to_reduced_units()
    assert var_b.magnitude == 1.0
    assert str(var_b.units) == '1 / meter'
    var_c = next(v for v in var_objs if v.name == 'c').value.to_reduced_units()
    assert var_c.magnitude == 1
    assert str(var_c.units) == '1 / second ** 1.5'


def test_units_in_expressions(meta_model, model_kwargs):
    """test units in expressions"""
    prog_inp = ('m = 1000. [meter]; k = 1.0 [kilometer]; res_1 = m == k;'
                'res_2 = (m/10) < k; res_3 = m + k; res_4 = m * k')
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    var_objs = get_children_of_type('Variable', prog)
    assert next(v for v in var_objs if v.name == 'res_1').value is True
    assert next(v for v in var_objs if v.name == 'res_2').value is True
    res_3 = next(v for v in var_objs if v.name == 'res_3').value.to_reduced_units()
    assert res_3.magnitude == 2000.0
    assert str(res_3.units) == 'meter'
    res_4 = next(v for v in var_objs if v.name == 'res_4').value.to_reduced_units()
    assert res_4.magnitude == 1.0
    assert str(res_4.units) == 'kilometer ** 2'


def test_units_comparison_of_vars(meta_model, model_kwargs):
    """test units in comparison of two variables in different units"""
    prog_inp = ('mile = 1 [mile]; km = 1 [km]; res_1 = mile == km;'
                'res_2 = mile > km')
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    var_objs = get_children_of_type('Variable', prog)
    assert next(v for v in var_objs if v.name == 'res_1').value is False
    assert next(v for v in var_objs if v.name == 'res_2').value is True


def test_units_dimensionality_errors(meta_model, model_kwargs):
    """test units with dimensionality errors"""
    prog_inp = ('l = 10 [meter] * 3; t = 2 [seconds]; m = 1000. [meter];'
                'k = 1.0 [kilometer]; a = (m*m) > k; b = l + t;'
                'c = 1 [sec] >= 1 [angstrom]')
    prog = meta_model.model_from_str(prog_inp, **model_kwargs, source_code=prog_inp)
    var_objs = get_children_of_type('Variable', prog)
    for var in var_objs:
        if var.name in ['a', 'b', 'c']:
            with pytest.raises(TextXError) as err_info:
                _ = var.value
            assert isinstance(err_info.value.__cause__, DimensionalityError)


def test_units_imported_functions(meta_model, model_kwargs):
    """test units in calls of imported functions"""
    prog_inp = ('q = 100 [meter**2]; use sqrt from numpy; a = sqrt(q);'
                'use power from numpy; b = power(q, 0.5);'
                'res_1 = ((sqrt(q)) == 10.0 [meter]);'
                'res_2 = ((power(q, 0.5)) == 10.0 [meter])')
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    var_objs = get_children_of_type('Variable', prog)
    assert next(v for v in var_objs if v.name == 'res_1').value is True
    assert next(v for v in var_objs if v.name == 'res_2').value is True
    var_a = next(v for v in var_objs if v.name == 'a').value.to_reduced_units()
    assert not var_a == 10.
    assert var_a.magnitude == 10.
    assert str(var_a.units) == 'meter'
    var_b = next(v for v in var_objs if v.name == 'b').value.to_reduced_units()
    assert var_b.magnitude == 10.
    assert str(var_b.units) == 'meter'


def test_units_dimensionless_imported_function(meta_model, model_kwargs):
    """test units in calls of imported dimensionless functions"""
    prog_inp = ('t = 1 [sec]; freq = 1 [Hz]; use exp from numpy;'
                'a = exp(freq * t)')
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    var_objs = get_children_of_type('Variable', prog)
    var_a = next(v for v in var_objs if v.name == 'a').value.to_reduced_units()
    assert str(var_a.units) in ['dimensionless', '']


def test_units_dimensionless_imported_function_error(meta_model, model_kwargs):
    """test units in calls of imported dimensionless functions with error"""
    prog_inp = ('t = 1; freq = 1 [Hz]; use exp from numpy;'
                'a = exp(freq * t)')
    prog = meta_model.model_from_str(prog_inp, **model_kwargs, source_code=prog_inp)
    var_objs = get_children_of_type('Variable', prog)
    with pytest.raises(TextXError) as err_info:
        _ = next(v for v in var_objs if v.name == 'a').value
    assert isinstance(err_info.value.__cause__, DimensionalityError)


def test_units_series(meta_model, model_kwargs):
    """test units in series"""
    prog_inp = ('s1 = (numbers: 1, 2, 3, 4); s3 = (distance: 1, 2, 3, 4) [cm];'
                'print(s1, s3)')
    ref = '(numbers: 1, 2, 3, 4) (distance: 1, 2, 3, 4) [centimeter]'
    assert meta_model.model_from_str(prog_inp, **model_kwargs).value == ref


def test_units_series_static(meta_model, model_kwargs):
    """test series with elements of different units: static check"""
    prog_inp = 's2 = (distance: 1 [kilometer], 2 [meter], 3 [meter], 4 [meter])'
    msg = 'Numeric type series must have elements of the same units.'
    with pytest.raises(TextXError, match=msg) as err:
        meta_model.model_from_str(prog_inp, **model_kwargs)
    assert isinstance(err.value.__cause__, InvalidUnitError)


def test_units_series_dynamic(meta_model, model_kwargs):
    """test series with elements of different units: runtime check"""
    prog_inp = 'a = 1 [meter]; b = 2 [nanometer]; c = (distance: a, b, b, a)'
    msg = 'Numeric type series must have elements of the same units.'
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    var_objs = get_children_of_type('Variable', prog)
    with pytest.raises(TextXError, match=msg) as err:
        _ = next(v for v in var_objs if v.name == 'c').value
    assert isinstance(err.value.__cause__, InvalidUnitError)


def test_units_print_units_series_scalars(meta_model, model_kwargs):
    """test printing numeric scalars and series in given units"""
    prog_inp = ('s = (dist: 1., 2.) [m]; m = (mem: 1, 2) [byte]; t = 1800 [s];'
                'mass = 1 [g]; print(s [cm], m [bits], t [h], mass [kg])\n')
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    ref_val = ('(dist: 100.0, 200.0) [centimeter] (mem: 8, 16) [bit] 0.5 [hour]'
               ' 0.001 [kilogram]')
    assert prog.value == ref_val


def test_units_print_units_arrays(meta_model, model_kwargs):
    """test printing arrays in in given units"""
    prog_inp = 'a = [1., 2.] [m]; print(a [cm], b [bit]); b = [1, 2] [byte]\n'
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    assert prog.value == '[100.0, 200.0] [centimeter] [8, 16] [bit]'


def test_units_import_physical_constants(meta_model, model_kwargs):
    """test import of physical constants"""
    prog_inp = 'use speed_of_light from virtmat.constants; print(speed_of_light [_compact])'
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    assert prog.value == '1.0 [speed_of_light]'


def test_undefined_unit_error(meta_model, model_kwargs):
    """test undefined unit error"""
    msg = "\'blah\' is not defined in the unit registry"
    with pytest.raises(TextXError, match=msg) as err:
        meta_model.model_from_str('a = 1 [blah]', **model_kwargs)
    assert isinstance(err.value.__cause__, UndefinedUnitError)


def test_invalid_unit_error(meta_model, model_kwargs):
    """test invalid unit error"""
    msg = 'Unit expression cannot have a scaling factor'
    with pytest.raises(TextXError, match=msg) as err:
        meta_model.model_from_str('a = 1 [2*m]', **model_kwargs)
    assert isinstance(err.value.__cause__, InvalidUnitError)
