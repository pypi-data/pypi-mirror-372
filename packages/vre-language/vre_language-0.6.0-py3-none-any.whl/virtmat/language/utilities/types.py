"""utility functions and classes to work with types"""
import numbers
from collections.abc import Iterable
import numpy
import pandas
import pint_pandas
from fireworks.utilities.fw_serializers import FWSerializable
from virtmat.language.utilities.units import ureg

pint_pandas.pint_array.DEFAULT_SUBDTYPE = None

dtypemap = {'BoolArray': bool, 'StrArray': str, 'IntArray': int,
            'FloatArray': float, 'ComplexArray': complex, 'IntSubArray': int,
            'FloatSubArray': float, 'ComplexSubArray': complex}

ScalarInteger = numbers.Integral
ScalarReal = numbers.Real
ScalarComplex = numbers.Complex
ScalarNumerical = numbers.Number
scalar_booltype = (bool, numpy.bool_)
scalar_type = (str, *scalar_booltype, numbers.Number)


def repr_type(type_):
    """return a string representation of type_"""
    if issubclass(type_, bool):
        return 'Boolean'
    if issubclass(type_, str):
        return 'String'
    if issubclass(type_, numbers.Integral):
        return 'Integer'
    if issubclass(type_, numbers.Real):
        return 'Float'
    if issubclass(type_, numbers.Complex):
        return 'Complex'
    return repr(type_)


def is_numeric_type(type_):
    """check if type_ is a numeric type"""
    if issubclass(type_, scalar_booltype):
        return False
    if issubclass(type_, (ScalarNumerical, ureg.Quantity)):
        return True
    if issubclass(type_, (pandas.Series, numpy.ndarray)):
        return getattr(type_, 'datatype', None) and is_numeric_type(type_.datatype)
    return False


def is_scalar_type(type_):
    """check if type_ is a scalar type"""
    if issubclass(type_, scalar_type):
        return True
    if issubclass(type_, ureg.Quantity) and not is_array_type(type_):
        return True
    return False


def is_numeric_scalar_type_of(type_, numtype):
    """check if type_ is numeric scalar sub-type of numtype"""
    if not is_scalar_type(type_) or issubclass(type_, scalar_booltype):
        return False
    if issubclass(type_, ureg.Quantity) and type_.datatype:
        return issubclass(type_.datatype, numtype)
    return issubclass(type_, numtype)


def is_scalar_inttype(type_):
    """check if type_ is a scalar integer type"""
    return is_numeric_scalar_type_of(type_, ScalarInteger)


def is_scalar_realtype(type_):
    """check if type_ is a scalar real type"""
    return (is_numeric_scalar_type_of(type_, ScalarReal) and not
            is_numeric_scalar_type_of(type_, ScalarInteger))


def is_scalar_complextype(type_):
    """check if type_ is a scalar complex type"""
    return (is_numeric_scalar_type_of(type_, ScalarComplex) and not
            is_numeric_scalar_type_of(type_, ScalarReal))


def is_array_type(type_):
    """check if type_ is an array type"""
    return ((hasattr(type_, 'arraytype') and type_.arraytype) or
            (hasattr(type_, 'datatype') and is_array_type(type_.datatype)))


def is_numeric_scalar_type(type_):
    """check if type_ is a numeric scalar type"""
    return is_numeric_type(type_) and is_scalar_type(type_)


def is_numeric_array_type(type_):
    """check if type is a numeric array type"""
    return is_numeric_type(type_) and is_array_type(type_)


def is_numeric(obj):
    """check if the object is of numeric type"""
    if isinstance(obj, ScalarNumerical) and not isinstance(obj, bool):
        return True
    if isinstance(obj, ureg.Quantity):
        return True
    if isinstance(obj, pandas.Series):
        if isinstance(obj.dtype, pint_pandas.PintType):
            return True
    if isinstance(obj, str):
        return False
    if isinstance(obj, Iterable):
        return all(is_numeric(item) for item in obj)
    return False


def is_scalar(obj):
    """check if the object is of scalar type"""
    if isinstance(obj, scalar_type):
        return True
    if isinstance(obj, ureg.Quantity) and not isinstance(obj.magnitude, numpy.ndarray):
        return True
    return False


def is_array(obj):
    """check if the obj is of an array type"""
    if isinstance(obj, numpy.ndarray):
        return True
    if isinstance(obj, ureg.Quantity) and isinstance(obj.magnitude, numpy.ndarray):
        return True
    return False


def is_numeric_scalar(obj):
    """check if the object is of numeric scalar type"""
    return is_numeric(obj) and is_scalar(obj)


def is_numeric_array(obj):
    """check if the object is of numeric array type"""
    return is_numeric(obj) and is_array(obj)


def settype(func):
    """
    Adapt the type of values at run time
    func: any value function
    Returns: a wrapped func
    """
    def wrapper(*args, **kwargs):
        rval = func(*args, **kwargs)
        if isinstance(rval, bool):
            return rval
        if isinstance(rval, numpy.bool_):
            return rval.item()
        if isinstance(rval, ScalarNumerical):
            return ureg.Quantity(rval)
        if isinstance(rval, list):
            return tuple(rval)
        if isinstance(rval, FWSerializable) and hasattr(rval, 'to_base'):
            return rval.to_base()
        return rval
    return wrapper


def get_units(obj):
    """return the units of an object; if object is non-numeric return None"""
    if isinstance(obj, ScalarNumerical) and not isinstance(obj, bool):
        return None
    if isinstance(obj, ureg.Quantity):
        return str(obj.units)
    if isinstance(obj, numpy.ndarray) and issubclass(obj.dtype.type, numpy.number):
        return None
    if isinstance(obj, pandas.Series):
        if isinstance(obj.dtype, pint_pandas.PintType):
            return str(obj.pint.units)
    return None


def get_datatype_name(datatype):
    """return datatype name"""
    if isinstance(datatype, tuple):
        # for types Tuple, Table and Dict
        return tuple(get_datatype_name(d) for d in datatype)
    return getattr(datatype, '__name__', None)


class NotComputed:
    """Singleton that acts as placeholder not computed values"""
    _self = None

    def __new__(cls):
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self

    def __repr__(self):
        return 'n.c.'


NC = NotComputed()
