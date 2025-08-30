"""
pint units registry, utility functions for the pint package
"""
from math import floor, ceil
from numbers import Integral
import pint
import pandas
import pint_pandas
from virtmat.language.utilities.errors import StaticValueError, RuntimeTypeError

ureg = pint.UnitRegistry()
ureg.autoconvert_offset_to_baseunit = True
# ureg.setup_matplotlib(True)
# ureg.mpl_formatter = '[{:~P}]'
pint.set_application_registry(ureg)
pint_pandas.pint_array.DEFAULT_SUBDTYPE = None


def get_units(val):
    """extract the unit from pint Quantity or pandas Series"""
    if isinstance(val, ureg.Quantity):
        return val.units
    if isinstance(val.dtype, pint_pandas.PintType):
        return val.dtype.units
    if val.dtype == 'object':
        units = set(v.units for v in val)
        assert len(units) == 1
        return next(iter(units))
    raise RuntimeTypeError(f'unsupported dtype: {val.dtype}')  # not covered


def get_dimensionality(val):
    """evaluate the dimensionality of pint Quantity or pandas Series"""
    if isinstance(val, ureg.Quantity):
        return val.dimensionality
    if isinstance(val.dtype, pint_pandas.PintType):  # not covered
        return val.pint.dimensionality
    if val.dtype == 'object':  # not covered
        dim = set(v.dimensionality for v in val)
        assert len(dim) == 1
        return next(iter(dim))
    raise RuntimeTypeError(f'unsupported dtype: {val.dtype}')  # not covered


def get_df_units(df):
    """extract a tuple of units frompandas DataFrame"""
    tuple_0 = tuple(next(df.iloc[[0]].itertuples(index=False, name=None)))
    return tuple(getattr(t, 'units', None) for t in tuple_0)


def convert_quantity_units(quantity, units):
    """convert quantity units to new units with type casting if needed"""
    converter = {'_base': quantity.to_base_units,
                 '_reduced': quantity.to_reduced_units,
                 '_compact': quantity.to_compact,
                 '_root': quantity.to_root_units}
    if units in converter:
        return converter[units]()
    return quantity.to(units)


def convert_series_units(ser, units):
    """convert series units to new units with type casting if needed"""
    if ser.dtype.units == units:
        return ser
    try:
        return convert_quantity_units(ser.pint, units)
    except TypeError as err:
        if 'cannot safely cast non-equivalent object to int64' in str(err):
            assert issubclass(ser.dtype.subdtype.type, Integral)
            float_type = f'pint[{ser.dtype.units}][float]'
            return convert_quantity_units(ser.astype(float_type).pint, units)
        raise err  # not covered


def convert_df_units(df, units):
    """convert units of dataframe columns of numeric dtype"""
    columns = []
    if any(not isinstance(u, (str, type(None))) for u in units):  # not covered
        w_type = next(u for u in units if not isinstance(u, (str, type(None))))
        raise RuntimeTypeError(f'unsupported dtype: {w_type}')
    for col, unit in zip(df.columns, units):
        if unit:
            if isinstance(df[col].dtype, pint_pandas.PintType):
                columns.append(convert_series_units(df[col], unit))
            elif df[col].dtype == 'object':  # not covered
                columns.append(df[col].apply(lambda x, u=unit: x.to(u)))
            else:  # not covered
                raise RuntimeTypeError(f'unsupported dtype: {df[col].dtype}')
        else:
            columns.append(df[col])
    return pandas.concat(columns, axis='columns')


def strip_units(val):
    """return the magnitude for quantity objects"""
    if isinstance(val, ureg.Quantity):
        return val.magnitude
    return val


def get_pint_series(ser):
    """convert dtype of numeric series from object to PintType"""
    assert isinstance(ser, pandas.Series)
    if (isinstance(ser.dtype, pint_pandas.PintType) or len(ser) == 0
       or not isinstance(ser[0], ureg.Quantity)):
        return ser
    units = set(val.units for val in ser)  # not covered
    assert len(units) == 1
    return ser.astype(pint_pandas.PintType(next(iter(units))))


def norm_mem(mem):
    """
    Convert memory size units to get the next most compact integer magnitude

    Args:
        mem (pint.Quantity): pint.Quantity representing memory size

    Returns:
        tuple(int, str): the magnitude as integer, decimal memory size units

    Raises:
        StaticValueError: if mem is not an integer multiple of 1 byte

    """
    units = {'petabyte': 'PB', 'terabyte': 'TB', 'gigabyte': 'GB',
             'megabyte': 'MB', 'kilobyte': 'KB', 'byte': 'B'}
    for unit, slurm_unit in units.items():
        mag = mem.to(unit).magnitude
        if ceil(mag) == floor(mag):
            return ceil(mag), slurm_unit
    raise StaticValueError('memory size must be integer number of bytes')  # not covered
