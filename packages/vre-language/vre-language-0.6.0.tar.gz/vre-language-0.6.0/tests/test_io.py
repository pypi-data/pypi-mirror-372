"""
tests of i/o operations
"""
import os
import urllib
import pytest
import yaml
import numpy
from textx import get_children_of_type
from textx.exceptions import TextXError
from virtmat.language.utilities.serializable import FWSeries, FWDataFrame
from virtmat.language.utilities.serializable import FWBoolArray, FWNumArray, FWStrArray
from virtmat.language.utilities.errors import RuntimeTypeError, EvaluationError
from virtmat.language.utilities.errors import ObjectFromFileError


def tuple2list(obj):
    """convert arbitrarily nested tuples to lists in an arbitrary object"""
    if isinstance(obj, (tuple, list)):
        new_obj = [tuple2list(elem) for elem in obj]
    elif isinstance(obj, dict):
        new_obj = {key: tuple2list(val) for key, val in obj.items()}
    else:
        new_obj = obj
    return new_obj


STRING_DATA = 'domain specific languages help a lot!'
BOOL_DATA = True
NUMBER_DATA = {'_fw_name': '{{virtmat.language.utilities.serializable.FWQuantity}}',
               'data': (3.1415, (('radian', 1),))}
SERIES_DATA = {'_fw_name': '{{virtmat.language.utilities.serializable.FWSeries}}',
               'data': [1.0, 2.0, 3.0], 'name': 'temperature', 'units': 'kelvin',
               'datatype': 'float'}
TABLE_DATA = {'_fw_name': '{{virtmat.language.utilities.serializable.FWDataFrame}}',
              'data': [{'_fw_name': '{{virtmat.language.utilities.serializable.FWSeries}}',
                        'name': 'pressure', 'data': [100.0, 200.0, 300.0], 'units': 'bar',
                        'datatype': 'float'},
                       {'_fw_name': '{{virtmat.language.utilities.serializable.FWSeries}}',
                        'name': 'temperature', 'data': [1.0, 2.0, 3.0], 'units': 'kelvin',
                        'datatype': 'float'},
                       {'_fw_name': '{{virtmat.language.utilities.serializable.FWSeries}}',
                        'name': 'impedance', 'data': [(1., 1e-3), (1.1, 4e-3), (1.2, 2e-3)],
                        'units': 'kiloohm', 'datatype': 'complex'},
                       {'_fw_name': '{{virtmat.language.utilities.serializable.FWSeries}}',
                        'name': 'count', 'data': [4, 55, 1], 'units': 'dimensionless',
                        'datatype': 'int'}]}
B_ARRAY_DATA = {'_fw_name': '{{virtmat.language.utilities.serializable.FWBoolArray}}',
                'data': [[False, True], [True, False]]}
T_ARRAY_DATA = {'_fw_name': '{{virtmat.language.utilities.serializable.FWStrArray}}',
                'data': [['a', 'b'], ['c', 'd']]}

F_ARRAY_DATA = {'_fw_name': '{{virtmat.language.utilities.serializable.FWNumArray}}',
                'data': [[0.59656566, 0.59656566, -1.3e-13],
                         [['bohr', 1], ['elementary_charge', 1]]], 'dtype': 'float64'}
S_ARRAY_DATA = {'_fw_name': '{{virtmat.language.utilities.serializable.FWSeries}}',
                'data': [F_ARRAY_DATA], 'name': 'dipole', 'datatype': 'FWNumArray'}


@pytest.fixture(name='string_input_file')
def string_input_fixture(tmp_path):
    """prepare an input source with a string"""
    source = os.path.join(tmp_path, 'string_in.yaml')
    with open(source, 'w', encoding='utf-8') as ifile:
        yaml.safe_dump(STRING_DATA, ifile)
    return source


@pytest.fixture(name='invalid_input_file')
def invalid_input_fixture(tmp_path):
    """prepare an input source with invalid data"""
    source = os.path.join(tmp_path, 'invalid_in.yaml')
    inv_data = NUMBER_DATA.copy()
    inv_data['data'] = 'blah'
    with open(source, 'w', encoding='utf-8') as ifile:
        yaml.safe_dump(inv_data, ifile)
    return source


@pytest.fixture(name='bool_input_file')
def bool_input_fixture(tmp_path):
    """prepare an input source with a bool"""
    source = os.path.join(tmp_path, 'bool_in.yaml')
    with open(source, 'w', encoding='utf-8') as ifile:
        yaml.safe_dump(BOOL_DATA, ifile)
    return source


@pytest.fixture(name='number_input_file')
def number_input_fixture(tmp_path):
    """prepare an input source with a number"""
    source = os.path.join(tmp_path, 'number_in.yaml')
    with open(source, 'w', encoding='utf-8') as ifile:
        yaml.safe_dump(NUMBER_DATA, ifile)
    return source


@pytest.fixture(name='series_input_file')
def series_input_fixture(tmp_path):
    """prepare an input source with a series"""
    source = os.path.join(tmp_path, 'series_in.yaml')
    with open(source, 'w', encoding='utf-8') as ifile:
        yaml.safe_dump(SERIES_DATA, ifile)
    return source


@pytest.fixture(name='table_input_file')
def table_input_fixture(tmp_path):
    """prepare an input source with a table"""
    source = os.path.join(tmp_path, 'table_in.yaml')
    with open(source, 'w', encoding='utf-8') as ifile:
        yaml.safe_dump(TABLE_DATA, ifile)
    return source


@pytest.fixture(name='array_input_file')
def array_input_fixture(tmp_path):
    """prepare an input source with a float array"""
    source = os.path.join(tmp_path, 'farray_in.yaml')
    with open(source, 'w', encoding='utf-8') as ifile:
        yaml.safe_dump(F_ARRAY_DATA, ifile)
    return source


@pytest.fixture(name='s_array_input_file')
def series_array_input_fixture(tmp_path):
    """prepare an input source with a series of arrays"""
    source = os.path.join(tmp_path, 'sarray_in.yaml')
    with open(source, 'w', encoding='utf-8') as ifile:
        yaml.safe_dump(S_ARRAY_DATA, ifile)
    return source


@pytest.fixture(name='b_array_input_file')
def boolean_array_input_fixture(tmp_path):
    """prepare an input source with a boolean array"""
    source = os.path.join(tmp_path, 'barray_in.yaml')
    with open(source, 'w', encoding='utf-8') as ifile:
        yaml.safe_dump(B_ARRAY_DATA, ifile)
    return source


@pytest.fixture(name='t_array_input_file')
def string_array_input_fixture(tmp_path):
    """prepare an input source with a string array"""
    source = os.path.join(tmp_path, 'tarray_in.yaml')
    with open(source, 'w', encoding='utf-8') as ifile:
        yaml.safe_dump(T_ARRAY_DATA, ifile)
    return source


@pytest.fixture(name='output_file')
def output_file_fixture(tmp_path):
    """prepare an output target"""
    return os.path.join(tmp_path, 'output.yaml')


def test_string_from_file(meta_model, string_input_file, model_kwargs):
    """test reading a string from file"""
    prog_str = "a = String from file \'" + string_input_file + "\'"
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    assert next(v for v in var_list if v.name == 'a').value == STRING_DATA


def test_string_from_url(meta_model, model_kwargs):
    """test reading a string from url"""
    prog_str = "a = String from url 'http://httpbin.org/datafile.json'"
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    with pytest.raises(TextXError, match='HTTP Error') as err_info:
        _ = next(v for v in var_list if v.name == 'a').value
    assert isinstance(err_info.value.__cause__, (urllib.error.HTTPError, EvaluationError))


def test_quantity_from_txt_file(meta_model, model_kwargs):
    """test reading a quantity from txt file (custom format)"""
    prog_str = "a = Quantity from file 'datafile.txt'"
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    msg = 'datastore with custom format not implemented'
    with pytest.raises(TextXError, match=msg) as err_info:
        _ = next(v for v in var_list if v.name == 'a').value
    assert isinstance(err_info.value.__cause__, (NotImplementedError, EvaluationError))


def test_string_from_file_wrong(meta_model, model_kwargs, number_input_file):
    """test reading a string from file with input of wrong type"""
    prog_str = f"a = String from file '{number_input_file}'"
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    match_str = "must be <class 'str'>"
    with pytest.raises(TextXError, match=match_str) as err_info:
        _ = next(v for v in var_list if v.name == 'a').value
    assert isinstance(err_info.value.__cause__, RuntimeTypeError)


def test_input_from_invalid_file(meta_model, model_kwargs, _schema_validate,
                                 invalid_input_file):
    """test reading from a file with data that does not validate"""
    prog_str = f"a = String from file '{invalid_input_file}'"
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    match_str = 'jsonschema.exceptions.ValidationError'
    with pytest.raises(TextXError, match=match_str) as err_info:
        _ = next(v for v in var_list if v.name == 'a').value
    assert isinstance(err_info.value.__cause__, ObjectFromFileError)


def test_bool_from_file(meta_model, model_kwargs, bool_input_file):
    """test reading a boolean from file"""
    prog_str = f"a = Bool from file '{bool_input_file}'"
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    assert next(v for v in var_list if v.name == 'a').value == BOOL_DATA


def test_bool_from_file_wrong(meta_model, model_kwargs, string_input_file):
    """test reading a boolean from file with input of wrong type"""
    prog_str = f"a = Bool from file '{string_input_file}'"
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    match_str = "must be <class 'bool'>"
    with pytest.raises(TextXError, match=match_str) as err_info:
        _ = next(v for v in var_list if v.name == 'a').value
    assert isinstance(err_info.value.__cause__, RuntimeTypeError)


def test_number_from_file(meta_model, model_kwargs, number_input_file):
    """test reading a quantity from file"""
    prog_str = f"a = Quantity from file '{number_input_file}'"
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    a_val = next(v for v in var_list if v.name == 'a').value
    assert a_val.to_tuple() == NUMBER_DATA['data']


def test_number_from_file_wrong(meta_model, model_kwargs, bool_input_file):
    """test reading a quantity from file with input of wrong type"""
    prog_str = f"a = Quantity from file '{bool_input_file}'"
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    match_str = "type must be <class 'pint.Quantity'> but is <class 'bool'>"
    with pytest.raises(TextXError, match=match_str) as err_info:
        _ = next(v for v in var_list if v.name == 'a').value
    assert isinstance(err_info.value.__cause__, RuntimeTypeError)


def test_number_from_file_wrong_schema(meta_model, model_kwargs, series_input_file):
    """test reading a quantity from file with input of wrong schema"""
    prog_str = f"a = Quantity from file '{series_input_file}'"
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    msg = "type must be <class 'pint.(quantity.build_quantity_class.<locals>.)?Quantity'>"
    with pytest.raises(TextXError, match=msg) as err_info:
        _ = next(v for v in var_list if v.name == 'a').value
    assert isinstance(err_info.value.__cause__, RuntimeTypeError)


def test_series_from_file(meta_model, model_kwargs, series_input_file):
    """test reading a series from file"""
    prog_str = f"a = Series from file '{series_input_file}'"
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    a_val = next(v for v in var_list if v.name == 'a').value
    assert FWSeries(a_val).to_dict()['data'] == SERIES_DATA['data']
    assert FWSeries(a_val).to_dict()['name'] == SERIES_DATA['name']
    assert FWSeries(a_val).to_dict()['units'] == SERIES_DATA['units']


def test_series_from_file_wrong(meta_model, model_kwargs, string_input_file):
    """test reading a series from file with input of wrong type"""
    prog_str = f"a = Series from file '{string_input_file}'"
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    match_str = "type must be <class 'pandas.core.series.Series'> but is <class 'str'>"
    with pytest.raises(TextXError, match=match_str) as err_info:
        _ = next(v for v in var_list if v.name == 'a').value
    assert isinstance(err_info.value.__cause__, RuntimeTypeError)


def test_series_from_file_wrong_schema(meta_model, model_kwargs, number_input_file):
    """test reading a series from file with input of wrong schema"""
    prog_str = f"a = Series from file '{number_input_file}'"
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    msg = "type must be <class 'pandas.core.series.Series'>"
    with pytest.raises(TextXError, match=msg) as err_info:
        _ = next(v for v in var_list if v.name == 'a').value
    assert isinstance(err_info.value.__cause__, RuntimeTypeError)


def test_table_from_file(meta_model, model_kwargs, table_input_file):
    """test reading a table from file"""
    prog_str = f"a = Table from file '{table_input_file}'"
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    data_frame = next(v for v in var_list if v.name == 'a').value
    assert data_frame.equals(FWDataFrame.from_dict(TABLE_DATA))


def test_table_from_file_wrong(meta_model, model_kwargs, bool_input_file):
    """test reading a table from file with input of wrong type"""
    prog_str = f"a = Table from file '{bool_input_file}'"
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    match_str = "type must be <class 'pandas.core.frame.DataFrame'> but is <class 'bool'>"
    with pytest.raises(TextXError, match=match_str) as err_info:
        _ = next(v for v in var_list if v.name == 'a').value
    assert isinstance(err_info.value.__cause__, RuntimeTypeError)


def test_table_from_file_wrong_schema(meta_model, model_kwargs, series_input_file):
    """test reading a table from file with input of wrong schema"""
    prog_str = f"a = Table from file '{series_input_file}'"
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    msg = "type must be <class 'pandas.core.frame.DataFrame'>"
    with pytest.raises(TextXError, match=msg) as err_info:
        _ = next(v for v in var_list if v.name == 'a').value
    assert isinstance(err_info.value.__cause__, RuntimeTypeError)


def test_float_array_from_file(meta_model, model_kwargs, array_input_file):
    """test reading a float array from file"""
    prog_str = f"a = FloatArray from file '{array_input_file}'"
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    array = next(v for v in var_list if v.name == 'a').value
    assert numpy.allclose(array, FWNumArray.from_dict(F_ARRAY_DATA))


def test_bool_array_from_file(meta_model, model_kwargs, b_array_input_file):
    """test reading a boolean array from file"""
    prog_str = f"a = BoolArray from file '{b_array_input_file}'"
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    array = next(v for v in var_list if v.name == 'a').value
    assert numpy.array_equal(array, FWBoolArray.from_dict(B_ARRAY_DATA))


def test_str_array_from_file(meta_model, model_kwargs, t_array_input_file):
    """test reading a string array from file"""
    prog_str = f"a = StrArray from file '{t_array_input_file}'"
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    array = next(v for v in var_list if v.name == 'a').value
    assert numpy.array_equal(array, FWStrArray.from_dict(T_ARRAY_DATA))


def test_float_array_from_file_wrong(meta_model, model_kwargs, series_input_file):
    """test reading a float array from a wrong file"""
    prog_str = f"a = FloatArray from file '{series_input_file}'"
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    msg = "type must be <class 'pint.(quantity.build_quantity_class.<locals>.)?Quantity'>"
    with pytest.raises(TextXError, match=msg) as err_info:
        _ = next(v for v in var_list if v.name == 'a').value
    assert isinstance(err_info.value.__cause__, RuntimeTypeError)


def test_series_float_array_from_file(meta_model, model_kwargs, s_array_input_file):
    """test reading a series of float arrays from file"""
    prog_str = f"a = Series from file '{s_array_input_file}'"
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    array = next(v for v in var_list if v.name == 'a').value[0]
    assert numpy.allclose(array, FWNumArray.from_dict(F_ARRAY_DATA))


def test_string_to_file(meta_model, model_kwargs, output_file):
    """test writing a string to file"""
    prog_str = f"a = '{STRING_DATA}'; a to file '{output_file}'"
    meta_model.model_from_str(prog_str, **model_kwargs)
    with open(output_file, 'r', encoding='utf-8') as ofile:
        assert yaml.safe_load(ofile) == STRING_DATA


def test_string_to_from_compressed_file(meta_model, model_kwargs, tmp_path):
    """test writing a string to compresed file"""
    compressed_file = os.path.join(tmp_path, 'output.json.zz')
    prog_str1 = f"a = '{STRING_DATA}'; a to file '{compressed_file}'"
    meta_model.model_from_str(prog_str1, **model_kwargs)
    prog_str2 = f"a = String from file '{compressed_file}'; print(a)"
    assert meta_model.model_from_str(prog_str2, **model_kwargs).value == f"'{STRING_DATA}'"


def test_string_to_from_non_compressed_file(meta_model, model_kwargs, tmp_path):
    """test writing a string to non-compressed file"""
    _file = os.path.join(tmp_path, 'output.json')
    prog_str1 = f"a = '{STRING_DATA}'; a to file '{_file}'"
    meta_model.model_from_str(prog_str1, **model_kwargs)
    prog_str2 = f"a = String from file '{_file}'; print(a)"
    assert meta_model.model_from_str(prog_str2, **model_kwargs).value == f"'{STRING_DATA}'"


def test_string_to_url(meta_model, model_kwargs, test_config):
    """test writing a string to url"""
    prog_str = f"a = '{STRING_DATA}'; a to url 'http://httpbin.org/datafile.json'"
    msg = 'datastore type url not implemented'
    if not test_config[1]:
        with pytest.raises(TextXError, match=msg) as err_info:
            _ = meta_model.model_from_str(prog_str, **model_kwargs).value
        assert isinstance(err_info.value.__cause__, NotImplementedError)


def test_quantity_to_txt(meta_model, model_kwargs, test_config):
    """test writing a quantity to a file in unsupported data format"""
    if not test_config[1]:
        with pytest.raises(TextXError, match='unsupported data type') as err_info:
            meta_model.model_from_str("a = 5; a to file 'q.txt'", **model_kwargs)
        assert isinstance(err_info.value.__cause__, RuntimeTypeError)


def test_quantity_to_hdf(meta_model, model_kwargs, test_config):
    """test writing a quantity to a file in unsupported data format"""
    if not test_config[1]:
        with pytest.raises(TextXError, match='hdf5 not implemented') as err_info:
            meta_model.model_from_str("a = 5; a to file 'q.h5'", **model_kwargs)
        assert isinstance(err_info.value.__cause__, NotImplementedError)


def test_bool_to_file(meta_model, model_kwargs, output_file):
    """test writing a boolean to file"""
    prog_str = f"a = true; a to file '{output_file}'"
    meta_model.model_from_str(prog_str, **model_kwargs)
    with open(output_file, 'r', encoding='utf-8') as ofile:
        assert yaml.safe_load(ofile) is True


def test_number_to_file(meta_model, model_kwargs, output_file):
    """test writing a number to file"""
    prog_str = f"a = 3.1415 [radian]; a to file '{output_file}'"
    meta_model.model_from_str(prog_str, **model_kwargs)
    with open(output_file, 'r', encoding='utf-8') as ofile:
        loaded_data = yaml.safe_load(ofile)
    assert loaded_data['data'] == tuple2list(NUMBER_DATA['data'])


def test_series_to_file(meta_model, model_kwargs, output_file):
    """test writing a series to file"""
    series_repr = "(temperature: 1.0, 2.0, 3.0) [kelvin]"
    prog_str = f"a = {series_repr}; a to file '{output_file}'"
    meta_model.model_from_str(prog_str, **model_kwargs)
    with open(output_file, 'r', encoding='utf-8') as ofile:
        loaded_data = yaml.safe_load(ofile)
    assert loaded_data['name'] == SERIES_DATA['name']
    assert loaded_data['data'] == SERIES_DATA['data']
    assert loaded_data['units'] == SERIES_DATA['units']


def test_table_to_file(meta_model, model_kwargs, output_file):
    """test writing a table to file"""
    table_repr = ("((pressure: 100.0, 200.0, 300.0) [bar], "
                  "(temperature: 1.0, 2.0, 3.0) [kelvin])")
    prog_str = f"a = {table_repr}; a to file '{output_file}'"
    meta_model.model_from_str(prog_str, **model_kwargs)
    with open(output_file, 'r', encoding='utf-8') as ofile:
        loaded_data = yaml.safe_load(ofile)
    assert loaded_data['_fw_name'] == TABLE_DATA['_fw_name']
    for ind in (0, 1):
        assert loaded_data['data'][ind]['_fw_name'] == TABLE_DATA['data'][ind]['_fw_name']
        assert loaded_data['data'][ind]['data'] == TABLE_DATA['data'][ind]['data']
        assert loaded_data['data'][ind]['name'] == TABLE_DATA['data'][ind]['name']
        assert loaded_data['data'][ind]['units'] == TABLE_DATA['data'][ind]['units']


def test_float_array_to_file(meta_model, model_kwargs, output_file):
    """test writing a float array to file"""
    array_repr = '[0.59656566, 0.59656566, -1.3e-13] [bohr*elementary_charge]'
    prog_str = f"a = {array_repr}; a to file '{output_file}'"
    meta_model.model_from_str(prog_str, **model_kwargs)
    with open(output_file, 'r', encoding='utf-8') as ofile:
        loaded_data = yaml.safe_load(ofile)
    assert loaded_data['_fw_name'] == F_ARRAY_DATA['_fw_name']


def test_series_float_array_to_file(meta_model, model_kwargs, output_file):
    """test writing a series with a float array to file"""
    series_repr = '(dipole: [0.59656566, 0.59656566, -1.3e-13]) [bohr*elementary_charge]'
    prog_str = f"a = {series_repr}; a to file '{output_file}'"
    meta_model.model_from_str(prog_str, **model_kwargs)
    with open(output_file, 'r', encoding='utf-8') as ofile:
        loaded_data = yaml.safe_load(ofile)
    assert loaded_data['_fw_name'] == S_ARRAY_DATA['_fw_name']


def test_print_number_units_nounits(meta_model, model_kwargs):
    """test printing numbers with units and no units"""
    prog_str = 'print(3.1 [meter], -1.0)'
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    assert prog.value == '3.1 [meter] -1.0'


def test_print_bool(meta_model, model_kwargs):
    """test printing booleans"""
    prog_str = 'print(true, false)'
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    assert prog.value == 'true false'


def test_print_string(meta_model, model_kwargs):
    """test printing strings"""
    prog_str = 'print("Abc")'
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    assert prog.value == '\'Abc\''


def test_print_series(meta_model, model_kwargs):
    """test printing series"""
    prog_str = ('a = (integers: 1, 2) [meter];'
                'b = (floats: 1., -1.) [cm];'
                'z = (complex: 1+1 j, 1-1 j);'
                'c = (booleans: true, false);'
                'd = (strings: "a", "b");'
                'print(a, b, z, c, d)')
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    assert prog.value == ('(integers: 1, 2) [meter] (floats: 1.0, -1.0) [centimeter] '
                          '(complex: 1.0+1.0 j, 1.0-1.0 j) (booleans: true, false) '
                          '(strings: \'a\', \'b\')')


def test_print_table(meta_model, model_kwargs):
    """test printing a table"""
    table_inp = ('((pressure: 100.0, 200.0, 300.0) [bar], '
                 '(temperature: 1.0, 2.0, 3.0) [kelvin], '
                 '(corrected: true, true, false), '
                 '(source: \'url\', \'file\', \'interactive\'))')
    prog_str = 'a = ' + table_inp + '; print(a)'
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    assert prog.value == table_inp


def test_print_tuple(meta_model, model_kwargs):
    """test printing a tuple"""
    tuple_inp = '(1, 2.0 [centimeter], true, \'string\', (numbs: 1, 3))'
    prog_str = 'a = ' + tuple_inp + '; print(a)'
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    assert prog.value == tuple_inp


def test_print_bool_array(meta_model, model_kwargs):
    """test printing a bool array"""
    array_inp = '[true, true, false]'
    prog_str = 'a = ' + array_inp + '; print(a)'
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    assert prog.value == array_inp


def test_print_str_array(meta_model, model_kwargs):
    """test printing a str array"""
    array_inp = "['a', 'abc']"
    prog_str = 'a = ' + array_inp + '; print(a)'
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    assert prog.value == array_inp


def test_print_int_array(meta_model, model_kwargs):
    """test printing an int array"""
    array_inp = '[[1, 0, 0], [0, 1, 0]]'
    prog_str = 'a = ' + array_inp + '; print(a)'
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    assert prog.value == array_inp


def test_print_float_array(meta_model, model_kwargs):
    """test printing a float array"""
    array_inp = '[[1.0, 0.0, 0.0], [1.0, 1.0, 0.0]] [angstrom]'
    prog_str = 'a = ' + array_inp + '; print(a)'
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    assert prog.value == array_inp


def test_print_series_float_arrays(meta_model, model_kwargs):
    """test printing a series of float arrays"""
    series_inp = '(positions: [[1.0, 0.0, 0.0], [1.0, 1.0, 0.0]]) [angstrom]'
    prog_str = 'a = ' + series_inp + '; print(a)'
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    assert prog.value == series_inp
