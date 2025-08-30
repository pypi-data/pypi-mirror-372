# pylint: disable=protected-access
"""
static type checker based on a simple recursion
"""
from functools import cached_property
import ase
from textx import textx_isinstance
from textx import get_parent_of_type, get_metamodel
from virtmat.language.metamodel.function import subst
from virtmat.language.utilities.textx import isinstance_m, isinstance_r
from virtmat.language.utilities.textx import get_reference, where_used
from virtmat.language.utilities.errors import textxerror_wrap, raise_exception
from virtmat.language.utilities.errors import PropertyError, SubscriptingError
from virtmat.language.utilities.errors import StaticTypeError, StaticValueError
from virtmat.language.utilities.errors import ExpressionTypeError, TypeMismatchError
from virtmat.language.utilities.errors import IterablePropertyError
from virtmat.language.utilities.typemap import typemap, DType, get_dtype, table_like_type
from virtmat.language.utilities.types import is_numeric_type, is_numeric_scalar_type
from virtmat.language.utilities.types import is_numeric_array_type, is_array_type
from virtmat.language.utilities.types import is_scalar_type, is_scalar_complextype
from virtmat.language.utilities.types import is_scalar_inttype, is_scalar_realtype
from virtmat.language.utilities.types import is_numeric_scalar, ScalarNumerical
from virtmat.language.utilities.types import scalar_type, dtypemap
from .imports import get_object_import, check_function_import
from .units import check_units


def check_series_type(obj, dtype=None):
    """check if the object is series type of the given datatype dtype"""
    if obj.type_ is not None:
        obj_ = get_reference(obj)
        if not issubclass(obj.type_, typemap['Series']):
            msg = 'Parameter must be series or reference to series'
            raise_exception(obj_, StaticTypeError, msg, where_used(obj))
        if dtype is not None and obj.type_.datatype is not None:
            if isinstance(dtype, tuple):
                type_name = ' or '.join(t.__name__ for t in dtype)
            else:
                type_name = dtype.__name__
            msg = f'Series must be of type {type_name}'
            if not issubclass(obj.type_.datatype, dtype):
                raise_exception(obj_, StaticTypeError, msg, where_used(obj))
            if issubclass(obj.type_.datatype, bool):
                if ((isinstance(dtype, tuple) and bool not in dtype)
                   or issubclass(dtype, bool)):
                    raise_exception(obj_, StaticTypeError, msg, where_used(obj))


def print_type(self):
    """check types in a print statement"""
    for par in self.params:
        _ = par.type_
    return str


def print_parameter_type(self):
    """check types in a print parameter"""
    if self.inp_units:
        if self.param.type_ is not None:
            if is_numeric_type(self.param.type_) is False:
                if hasattr(self.param, 'ref'):
                    msg = f'Parameter {self.param.ref.name} is non-numeric type'
                else:
                    msg = 'Print parameter is non-numeric type'
                raise StaticTypeError(msg)
    return self.param.type_


def variable_type(self):
    """evaluate variable type"""
    return self.parameter.type_


def get_numeric_type(datatypes):
    """return datatype of factor/term/expression from its parameters datatypes"""
    if len(datatypes) == 0:
        return None
    if None in datatypes:
        datatypes.discard(None)
        if any(is_scalar_complextype(t) for t in datatypes):
            datatype = complex
        else:
            datatype = None
    elif all(is_scalar_inttype(t) for t in datatypes):
        datatype = int
    elif all(is_scalar_realtype(t) or is_scalar_inttype(t) for t in datatypes):
        datatype = float
    else:
        assert any(is_scalar_complextype(t) for t in datatypes)
        datatype = complex
    return datatype


def expression_type(self):
    """evaluate expression type"""
    for operand in self.operands:
        if operand.type_ is not None and not is_numeric_scalar_type(operand.type_):
            raise ExpressionTypeError(operand)
    datatypes = set(o.type_.datatype for o in self.operands if o.type_ is not None)
    datatype = get_numeric_type(datatypes)
    return DType('Quantity', (typemap['Quantity'],), {'datatype': datatype})


def term_type(self):
    """evaluate term type"""
    for operand in self.operands:
        if operand.type_ is not None and not is_numeric_scalar_type(operand.type_):
            raise ExpressionTypeError(operand)
    datatypes = set(o.type_.datatype for o in self.operands if o.type_ is not None)
    if '/' in self.operators and None not in datatypes:
        if all(is_scalar_realtype(t) or is_scalar_inttype(t) for t in datatypes):
            datatype = float
        else:
            assert any(is_scalar_complextype(t) for t in datatypes)
            datatype = complex
    else:
        datatype = get_numeric_type(datatypes)
    return DType('Quantity', (typemap['Quantity'],), {'datatype': datatype})


def factor_type(self):
    """evaluate factor type"""
    for operand in self.operands:
        if operand.type_ is not None and not is_numeric_scalar_type(operand.type_):
            raise ExpressionTypeError(operand)
    datatypes = set(o.type_.datatype for o in self.operands if o.type_ is not None)
    datatype = get_numeric_type(datatypes)
    return DType('Quantity', (typemap['Quantity'],), {'datatype': datatype})


def power_type(self):
    """evaluate power type"""
    return self.operand.type_


def operand_type(self):
    """evaluate operand type"""
    return self.operand.type_


def boolean_expression_type(self):
    """evaluate boolean expression type"""
    if hasattr(self, 'operand'):
        if self.operand.type_ is not None:
            if not issubclass(self.operand.type_, bool):
                raise ExpressionTypeError(self.operand)
    else:
        assert hasattr(self, 'operands')
        if not all(issubclass(o.type_, bool) for o in self.operands):
            raise ExpressionTypeError(self.operand)
    return bool


def real_imag_type(self):
    """evaluate the type of real/imag object"""
    if self.parameter.type_ is not None:
        if issubclass(self.parameter.type_, typemap['Quantity']):
            if self.parameter.type_.datatype is None:
                return DType('Quantity', (typemap['Quantity'],), {})
            if not issubclass(self.parameter.type_.datatype, complex):
                raise StaticTypeError('real/imag part only defined for complex type')
            return DType('Quantity', (typemap['Quantity'],), {'datatype': float})
        raise StaticTypeError('real/imag part only defined for complex type')
    return None


def if_expression_type(self):
    """evaluate if-expression type"""
    if not issubclass(self.expr.type_, bool):
        raise ExpressionTypeError(self.expr)
    if self.true_.type_ != self.false_.type_:
        raise TypeMismatchError(self.true_, self.false_)
    return self.true_.type_


def comparison_type(self):
    """evaluate comparison type"""
    for lrhs in (self.left.type_, self.right.type_):
        if lrhs is not None:
            if not issubclass(lrhs, (bool, str, typemap['Quantity'])):
                msg = f'invalid type(s) used in comparison: {lrhs.__name__}'
                raise StaticTypeError(msg)
            if self.operator not in ('==', '!='):
                if issubclass(lrhs, (bool, str)):
                    msg = f'comparison not possible with {self.operator}'
                    raise StaticTypeError(msg)
                if issubclass(lrhs, typemap['Quantity']):
                    if lrhs.datatype is not None and issubclass(lrhs.datatype, complex):
                        msg = f'comparison not possible with {self.operator}'
                        raise StaticTypeError(msg)
    if self.left.type_ is not None and self.right.type_ is not None:
        if (issubclass(self.left.type_, typemap['Quantity']) and
           issubclass(self.right.type_, typemap['Quantity'])):
            return bool
        if self.left.type_ != self.right.type_:
            raise TypeMismatchError(self.left, self.right)
    return bool


def object_import_type(self):
    """evaluate the type of an imported object"""
    obj = get_object_import(self)
    if callable(obj):
        return None  # issue #117
    if isinstance(obj, (bool, str)):
        return type(obj)
    if is_numeric_scalar(obj):
        return DType('Quantity', (typemap['Quantity'],), {'datatype': type(obj)})
    raise StaticTypeError(f'Unsupported type of imported object: {type(obj)}')


def function_call_type(self):
    """evaluate the type of a function call"""
    metamodel = get_metamodel(self)
    if textx_isinstance(self.function, metamodel['ObjectImport']):
        if textx_isinstance(self.parent, metamodel['Operand']):
            ret_type = DType('Quantity', (typemap['Quantity'],), {})
        elif textx_isinstance(self.parent, metamodel['BooleanOperand']):
            ret_type = bool
        elif isinstance_m(self.parent, ['Comparison']):
            other = self.parent.right if self.parent.left is self else self.parent.left
            if not ((textx_isinstance(other, metamodel['FunctionCall']) and
                     textx_isinstance(other.function, metamodel['ObjectImport'])) or
                    (textx_isinstance(other, metamodel['GeneralReference']) and
                     textx_isinstance(other.ref, metamodel['ObjectImport']))):
                if issubclass(other.type_, typemap['Quantity']):
                    ret_type = DType('Quantity', (typemap['Quantity'],), {})
                else:
                    ret_type = other.type_
            else:
                ret_type = None
        elif isinstance_m(self.parent, ['IfFunction', 'IfExpression']):
            other = self.parent.true_ if self.parent.false_ is self else self.parent.false_
            if not ((textx_isinstance(other, metamodel['FunctionCall']) and
                     textx_isinstance(other.function, metamodel['ObjectImport'])) or
                    (textx_isinstance(other, metamodel['GeneralReference']) and
                     textx_isinstance(other.ref, metamodel['ObjectImport']))):
                ret_type = other.type_
            else:
                ret_type = None
        else:
            ret_type = None
    else:
        assert textx_isinstance(self.function, metamodel['FunctionDefinition'])
        try:
            ret_type = self.expr.type_
        except ExpressionTypeError as err:
            raise_exception(err.obj, StaticTypeError, err.message, where_used(self))
    return ret_type


def tuple_type(self):
    """evaluate the types in a tuple object"""
    datatype = tuple(param.type_ for param in self.params)
    return DType('Tuple', (tuple,), {'datatype': datatype})


def series_type(self):
    """evaluate / check the type of a series"""
    if self.name is None:
        return DType('Series', (typemap['Series'],), {})
    types = [elem.type_ for elem in self.elements if elem.type_ is not None]
    if len(set(types)) > 1:
        msg = (f'Series elements must have one type but {len(set(types))}'
               f' types were found')
        raise StaticTypeError(msg)
    datatype = next(iter(types)) if len(types) > 0 else None
    typespec = {'datatype': datatype, 'datalen': len(self.elements)}
    return DType('Series', (typemap['Series'],), typespec)


def table_type(self):
    """evaluate / check the types in a table object"""
    if self.url is not None or self.filename is not None:
        return DType('Table', (typemap['Table'],), {})
    names = self.get_column_names()
    if len(set(names)) != len(names):
        msg = 'Repeating column names were found in table'
        raise StaticValueError(msg)
    for column in self.columns:
        if column.type_ and not issubclass(column.type_, typemap['Series']):
            msg = 'The type of table column must be series'
            raise_exception(column, StaticTypeError, msg)
    types = tuple(get_reference(c).type_ for c in self.columns)
    datatypes = tuple(t.datatype for t in types)
    datalens = set(t.datalen for t in types)
    known_datalens = len(datalens-{None})
    if known_datalens > 1:
        msg = f'Table columns must have one size but {known_datalens} sizes were found'
        raise StaticValueError(msg)
    type_spec = {'datatype': datatypes, 'datalen': next(iter(datalens))}
    return DType('Table', (typemap['Table'],), type_spec)


def dict_type(self):
    """evaluate dictionary type"""
    dtypes = tuple(v.type_ for v in self.values)
    return DType('Dict', (typemap['Dict'],), {'datatype': dtypes})


def alt_table_type(self):
    """evaluate alt table type"""
    if self.tab:
        return self.tab.type_
    type_spec = {'datatype': tuple(v.type_ for v in self.values), 'datalen': 1}
    return DType('Table', (typemap['Table'],), type_spec)


def tag_type(self):
    """evaluate tag tyoe"""
    return self.tagtab.type_


def get_array_datalen(obj):
    """get the axes lengths of an array object"""
    if hasattr(obj, 'elements'):
        if len(obj.elements) == 0:
            return (len(obj.elements), 0)
        return (len(obj.elements), *get_array_datalen(obj.elements[0]))
    return tuple()


def array_type(self):
    """return array type"""
    meta = get_metamodel(self)
    mtype, dtype = next((m, d) for m, d in dtypemap.items()
                        if textx_isinstance(self, meta[m]))
    from_file = getattr(self, 'url', None) or getattr(self, 'filename', None)
    datalen = None if from_file else get_array_datalen(self)
    typespec = {'datatype': dtype, 'arraytype': 'True', 'datalen': datalen}
    return DType(mtype, (typemap[mtype],), typespec)


def get_array_type(datatype, typespec):
    """construct and return the proper array type depending on datatype"""
    if datatype is None:
        return None
    try:
        mtype = next(m for m, d in dtypemap.items() if issubclass(datatype, d))
    except StopIteration as err:
        if is_array_type(datatype) and hasattr(datatype, 'datatype'):
            return get_array_type(datatype.datatype, typespec)
        msg = 'array datatype must be numeric, boolean, string or array'
        raise StaticTypeError(msg) from err
    typespec['arraytype'] = True
    return DType(mtype, (typemap[mtype],), typespec)


def get_sliced_type(obj):
    """return a type slice of an iterable object"""
    type_ = obj.obj.type_.datatype
    size_ = obj.obj.type_.datalen
    name_ = obj.obj.type_.__name__
    if obj.slice:
        obj_slice = slice(obj.start, obj.stop, obj.step)
        if size_ is not None:
            size_1d = size_[0] if isinstance(size_, tuple) else size_
            try:
                sl_size = len(range(*obj_slice.indices(size_1d)))
            except ValueError as err:
                if 'step cannot be zero' in str(err):
                    raise StaticValueError(str(err).capitalize()) from err
                raise err
            size_ = (sl_size, *size_[1:]) if isinstance(size_, tuple) else sl_size
    if obj.array:
        return get_array_type(type_, {'datatype': type_, 'datalen': (size_,)})
    return DType(name_, (obj.obj.type_,), {'datatype': type_, 'datalen': size_})


def get_property_type(var, type_, accessor):
    """return the type of a property using an accessor"""
    if type_ is None:
        return None
    if accessor.id is not None:
        if issubclass(type_, typemap['Table']):
            if hasattr(var, 'parameter') and isinstance_r(var, ['Table']):
                # table literal
                assert isinstance_m(var, ['Variable'])
                obj = get_reference(var.parameter).get_column(accessor.id)
                if obj is None:
                    msg = f'column {accessor.id} not found in Table {var.name}'
                    raise PropertyError(msg)
                rettype = obj.type_
            else:
                rettype = get_dtype('Series', basetype='Series')
        elif issubclass(type_, typemap['Dict']):
            if hasattr(var, 'parameter') and isinstance_r(var, ['Dict']):
                # dict literal
                assert isinstance_m(var, ['Variable'])
                dct = get_reference(var.parameter)
                elem = dict(zip(dct.keys, dct.values)).get(accessor.id)
                if elem is None:
                    msg = f'value not found for key {accessor.id} in Dict {var.name}'
                    raise PropertyError(msg)
                rettype = elem.type_
            else:
                rettype = None
        elif issubclass(type_, typemap['Series']):
            raise StaticValueError('Invalid use of series name')
        elif issubclass(type_, tuple(typemap.values())):
            rettype = get_dtype(type_.__name__, id_=accessor.id)
        else:
            raise StaticTypeError(f'Invalid use of an ID in type {type_.__name__}')
        if rettype is None:
            raise PropertyError(f'Invalid key \"{accessor.id}\" in {type_.__name__}')
    else:
        assert accessor.index is not None
        if hasattr(var, '_tx_metamodel'):
            if isinstance_m(var.parameter, ['Table', 'Series']):
                if type_.datalen is not None and not abs(accessor.index) < type_.datalen:
                    raise SubscriptingError('Index out of range')
        if issubclass(type_, typemap['Table']):
            rettype = DType('Tuple', (typemap['Tuple'],), {'datatype': type_.datatype})
        elif issubclass(type_, typemap['Tuple']):
            rettype = type_.datatype[accessor.index]
        elif issubclass(type_, typemap['Series']):
            if type_.datatype is None or issubclass(type_.datatype, (str, bool)):
                rettype = type_.datatype
            elif is_numeric_scalar_type(type_.datatype):
                rettype = DType('Quantity', (typemap['Quantity'],), {'datatype': type_.datatype})
            elif is_numeric_array_type(type_.datatype):
                rettype = get_dtype(type_.datatype.__name__, type_.datatype.__name__)
            else:
                rettype = type_.datatype
        elif is_array_type(type_):
            if type_.datalen is not None:
                assert isinstance(type_.datalen, tuple)
                if len(type_.datalen) > 1:
                    arr_type = next(k for k, v in dtypemap.items() if type_.datatype is v)
                    typespec = {'datatype': type_.datatype, 'arraytype': True,
                                'datalen': type_.datalen[1:]}
                    rettype = DType(arr_type, (typemap[arr_type],), typespec)
                else:
                    assert len(type_.datalen) == 1
                    if is_numeric_type(type_.datatype):
                        rettype = DType('Quantity', (typemap['Quantity'],),
                                        {'datatype': type_.datatype})
                    else:
                        rettype = type_.datatype
                if type_.datalen[0] is not None and abs(accessor.index) >= type_.datalen[0]:
                    msg = (f'Index out of range, index: {accessor.index}, '
                           f'data length: {type_.datalen[0]}')
                    raise SubscriptingError(msg)
            else:
                rettype = None
        elif issubclass(type_, typemap['AMMLStructure']):
            types = (typemap['Table'], typemap['FloatArray'], typemap['BoolArray'])
            rettype = DType('Tuple', (typemap['Tuple'],), {'datatype': types})
        elif issubclass(type_, typemap['AMMLCalculator']):
            rettype = DType('Tuple', (typemap['Tuple'],), {'datatype': None})
        elif issubclass(type_, typemap['AMMLProperty']):
            rettype = DType('Tuple', (typemap['Tuple'],), {'datatype': None})
        elif issubclass(type_, typemap['AMMLTrajectory']):
            rettype = DType('Tuple', (typemap['Tuple'],), {'datatype': None})
        elif issubclass(type_, (typemap['ChemSpecies'], typemap['ChemReaction'])):
            rettype = DType('Tuple', (typemap['Tuple'],), {'datatype': typemap['Quantity']})
        else:
            raise StaticTypeError(f'Invalid use of index in type {type_.__name__}')
    return rettype


def general_reference_type(self):
    """return the type of a reference to an object with data accessors"""
    type_ = self.ref.type_
    for accessor in self.accessors:
        type_ = get_property_type(self.ref, type_, accessor)
    return type_


def iterable_property_type(self):
    """evaluate / check the type of an iterable property object"""
    opt_attrs = (self.array, self.columns, self.name_)
    opt_attrn = ('array', 'columns', 'name')
    if self.obj.type_ is None:
        ret_type = None
    elif issubclass(self.obj.type_, typemap['Table']):
        if self.name_:
            raise IterablePropertyError(self, 'Table', 'name')
        if self.columns:
            ret_type = DType('Series', (typemap['Series'],), {'datatype': str})
        elif self.array:
            raise IterablePropertyError(self, 'Table', 'array')
        else:
            ret_type = get_sliced_type(self)
    elif issubclass(self.obj.type_, typemap['Series']):
        if self.columns:
            raise IterablePropertyError(self, 'Series', 'columns')
        ret_type = str if self.name_ else get_sliced_type(self)
    elif is_array_type(self.obj.type_):
        for attr, attrn in zip(opt_attrs, opt_attrn):
            if attr:
                raise IterablePropertyError(self, self.obj.type_.__name__, attrn)
        ret_type = get_sliced_type(self)
    elif is_scalar_type(self.obj.type_):
        for attr, attrn in zip(opt_attrs, opt_attrn):
            if attr:
                raise IterablePropertyError(self, self.obj.type_.__name__, attrn)
        ret_type = self.obj.type_
    else:
        for attr, attrn in zip(opt_attrs, opt_attrn):
            if attr:
                raise IterablePropertyError(self, self.obj.type_.__name__, attrn)
        ret_type = self.obj.type_
    return ret_type


def iterable_query_type(self):
    """evaluate / check the type of an iterable query object"""
    classes = ['Table', 'Series', 'IterableQuery', 'IterableProperty']
    param = self.obj.ref.parameter
    if isinstance_r(param, classes):
        if len(self.columns) > 0:
            if isinstance_m(param, ['Series']):
                raise IterablePropertyError(self, 'Series', 'columns')
            if isinstance_m(param, ['Table']):
                columns = [param.get_column(c) for c in self.columns]
                types = tuple(c.type_.datatype for c in columns)
            else:
                types = self.obj.type_.datatype
        else:
            types = self.obj.type_.datatype
    else:
        types = None
    size = None if self.where else self.obj.type_.datalen
    typespec = {'datatype': types, 'datalen': size}
    return DType(self.obj.type_.__name__, (self.obj.type_,), typespec)


def check_column(pref, column):
    """check whether a GeneralReference pref contains a column (str)"""
    pref_par = pref.ref.parameter
    pref_name = pref.ref.name
    assert column is not None
    if (pref.type_ and issubclass(pref.type_, typemap['Series']) and
       isinstance_m(pref_par, ['Series'])):
        if column != pref_par.name:
            msg = f'column \"{column}\" does not match Series name \"{pref_name}\"'
            raise StaticValueError(msg)
    if (pref.type_ and issubclass(pref.type_, typemap['Table']) and
       isinstance_m(pref_par, ['Table'])):
        if pref_par.get_column(column) is None:
            msg = f'column \"{column}\" not found in Table \"{pref_name}\"'
            raise StaticValueError(msg)


def condition_in_type(self):
    """evaluate / check the type of condition in"""
    check_column(get_parent_of_type('IterableQuery', self).obj, self.column)
    return DType('Series', (typemap['Series'],), {'datatype': bool})


def condition_comparison_type(self):
    """evaluate / check the type of condition comparison"""
    prop_ref = get_parent_of_type('IterableQuery', self).obj
    if self.column_left is not None:
        check_column(prop_ref, self.column_left)
    if self.column_right is not None:
        check_column(prop_ref, self.column_right)
    return DType('Series', (typemap['Series'],), {'datatype': bool})


def range_type(self):
    """evaluate / check the type of the range builtin function"""
    datatype = None
    for par in (self.start, self.stop, self.step):
        type_ = par.type_
        if type_ and not issubclass(type_, typemap['Quantity']):
            msg = f'Range parameter {par} must be numeric real type'
            raise_exception(par, StaticTypeError, msg)
        if type_ and type_.datatype:
            if issubclass(type_.datatype, float):
                datatype = float
            else:
                assert issubclass(type_.datatype, int)
                datatype = int
        if datatype == float:
            break
    return DType('Series', (typemap['Series'],), {'datatype': datatype})


def sum_type(self):
    """evaluate / check the type of the sum builtin function"""
    if self.parameter is not None:
        check_series_type(self.parameter, ScalarNumerical)
        typespec = {}
        if self.parameter.type_:
            if (self.parameter.type_.datatype and
               not is_numeric_type(self.parameter.type_.datatype)):
                raise StaticTypeError('Sum accepts only inputs of numeric type')
            typespec = {'datatype': self.parameter.type_.datatype}
        return DType('Quantity', (typemap['Quantity'],), typespec)
    assert self.params
    if not all(issubclass(p.type_, typemap['Quantity']) for p in self.params if p.type_):
        raise StaticTypeError('Sum accepts only inputs of numeric type')
    if any(p.type_.datatype is None for p in self.params):
        typespec = {'datatype': None}
    elif any(issubclass(p.type_.datatype, float) for p in self.params):
        typespec = {'datatype': float}
    else:
        typespec = {'datatype': int}
    return DType('Quantity', (typemap['Quantity'],), typespec)


def get_par_datatype(obj, datatype):
    """create test params and types to determine type of map/filter/reduce"""
    if datatype and issubclass(datatype, scalar_type):
        meta = get_metamodel(obj)
        if issubclass(datatype, bool):
            param = meta['Bool']()
            type_ = bool
        elif issubclass(datatype, str):
            param = meta['String']()
            type_ = str
        else:
            assert issubclass(datatype, ScalarNumerical)
            param = meta['Quantity']()
            param.inp_value = 0 if issubclass(datatype, int) else 0.
            param.inp_units = None
            type_ = DType('Quantity', (typemap['Quantity'],), {'datatype': datatype})
        return param, type_
    return None, None


def map_type(self):
    """evaluate / check the type of the map builtin function"""
    func = self.lambda_ if self.lambda_ else self.function
    assert all(p.type_ is not None for p in self.params)
#    if any(p.type_ is None for p in self.params):  # work-around map with func with map
#        return DType('Series', (typemap['Series'],), {})
    if not all(issubclass(p.type_, (typemap['Series'], table_like_type)) for p in self.params):
        raise StaticTypeError('map inputs must be either series or table-like')
    for param in self.params:
        if issubclass(param.type_, typemap['Series']):
            check_series_type(param)
    dsize = self.params[0].type_.datalen
    typespec = {'datalen': dsize}
    if not all(p.type_.datalen == dsize or p.type_.datalen is None for p in self.params):
        raise StaticValueError('map inputs must have equal size')
    if isinstance_m(func, ['ObjectImport']):
        check_function_import(func)
        return DType('Series', (typemap['Series'],), typespec)
    if len(func.args) != len(self.params):
        msg = 'number of map function arguments and map inputs must be equal'
        raise StaticValueError(msg)
    if all(issubclass(p.type_, typemap['Series']) for p in self.params):
        par_types = [get_par_datatype(self, p.type_.datatype) for p in self.params]
        params, types = [p for p, t in par_types], [t for p, t in par_types]
        new_type = subst(self, func, params, types).type_
        if new_type is None or issubclass(new_type, (bool, str)):
            typespec['datatype'] = new_type
        else:
            typespec['datatype'] = new_type.datatype
    if isinstance_m(func.expr, ['Dict']):
        return DType('Table', (typemap['Table'],), typespec)
    return DType('Series', (typemap['Series'],), typespec)


def filter_type(self):
    """evaluate / check the type of the filter builtin function"""
    func = self.lambda_ if self.lambda_ else self.function
    assert self.parameter.type_ is not None
    if not issubclass(self.parameter.type_, (typemap['Series'], table_like_type)):
        raise StaticTypeError('filter input must be either series or table-like')
    if issubclass(self.parameter.type_, typemap['Series']):
        check_series_type(self.parameter)
    datatype = self.parameter.type_.datatype
    if isinstance_m(func, ['ObjectImport']):
        check_function_import(func)
        return DType('Series', (typemap['Series'],), {'datatype': datatype})
    if len(func.args) != 1:
        raise StaticValueError('Filter function must have only one argument')
    if issubclass(self.parameter.type_, typemap['Series']):
        if (isinstance_m(func.expr, ['FunctionCall'])
                and isinstance_m(func.expr.function, ['ObjectImport'])):
            check_function_import(func.expr.function)
            return DType('Series', (typemap['Series'],), {'datatype': datatype})
        param, type_ = get_par_datatype(self, datatype)
        if not issubclass(subst(self, func, [param], [type_]).type_, bool):
            raise StaticTypeError('Filter function must be of boolean type')
        return DType('Series', (typemap['Series'],), {'datatype': datatype})
    t_name = self.parameter.type_.__name__
    return DType(t_name, (typemap[t_name],), {'datatype': datatype})


def reduce_type(self):
    """evaluate / check the type of the reduce builtin function"""
    func = self.lambda_ if self.lambda_ else self.function
    assert self.parameter.type_ is not None
    if not issubclass(self.parameter.type_, (typemap['Series'], table_like_type)):
        raise StaticTypeError('reduce input must be either series or table-like')
    if issubclass(self.parameter.type_, typemap['Series']):
        check_series_type(self.parameter)
    if isinstance_m(func, ['ObjectImport']):
        check_function_import(func)
        return None
    if len(func.args) != 2:
        raise StaticValueError('Reduce function must have exactly two arguments')
    if issubclass(self.parameter.type_, typemap['Series']):
        if (isinstance_m(func.expr, ['FunctionCall'])
                and isinstance_m(func.expr.function, ['ObjectImport'])):
            check_function_import(func.expr.function)
            return None
        param, type_ = get_par_datatype(self, self.parameter.type_.datatype)
        return subst(self, func, [param]*2, [type_]*2).type_
    typespec = {'datatype': self.parameter.type_.datatype, 'datalen': 1}
    return DType('Table', (typemap['Table'],), typespec)


def boolean_reduce_type(self):
    """evaluate / check the type of the boolean reduce builtin function"""
    msg = 'Boolean reduce parameters must be of boolean type'
    if self.parameter is not None:
        check_series_type(self.parameter)
        if (self.parameter.type_.datatype and
           not issubclass(self.parameter.type_.datatype, bool)):
            raise StaticTypeError(msg)
    else:
        if not all(issubclass(p.type_, bool) for p in self.params if p.type_):
            raise StaticTypeError(msg)
    return bool


def in_type(self):
    """evaluate / check the type of in-expression"""
    if self.parameter is not None:
        check_series_type(self.parameter)
    return bool


def quantity_type(self):
    """evaluate the type of a quantity literal"""
    if self.inp_value is None:
        return DType('Quantity', (typemap['Quantity'],), {})
    typespec = {'datatype': self.inp_value.type_}
    return DType('Quantity', (typemap['Quantity'],), typespec)


def amml_structure_type(self):
    """evaluate the type of structure object"""
    rtype = DType('AMMLStructure', (typemap['AMMLStructure'],), {})
    if self.filename or self.url:
        return rtype
    tab_typs = {'atoms': typemap['Table'], 'pbc': typemap['BoolArray'],
                'cell': (typemap['FloatArray'], typemap['FloatSubArray'])}
    column_names = self.tab.get_column_names()
    if 'atoms' not in column_names:
        msg = '\'atoms\' missing in \'structure\''
        raise_exception(self.tab, StaticValueError, msg)
    if not all(n in tab_typs for n in column_names):
        col = next(self.tab.get_column(n) for n in column_names if n not in tab_typs)
        msg = f'invalid parameter \'{col.name}\' in \'structure\''
        raise_exception(col, StaticValueError, msg)
    for col in (self.tab.get_column(n) for n in column_names):
        if isinstance_m(col, ['Series']):
            if col.type_ and col.type_.datatype:
                if not issubclass(col.type_.datatype, tab_typs[col.name]):
                    msg = (f'Series \'{col.name}\' must have type '
                           f'{tab_typs[col.name]} but has type {col.type_.datatype}')
                    raise_exception(col, StaticTypeError, msg)
    fquantity = (float, typemap['Quantity'])
    atoms_dtyps = {'symbols': str, 'x': fquantity, 'y': fquantity, 'z': fquantity,
                   'px': fquantity, 'py': fquantity, 'pz': fquantity, 'tags': int,
                   'masses': fquantity}
    atoms_col = self.tab.get_column('atoms')
    if atoms_col is not None:
        for atoms_elem in atoms_col.elements:
            atoms = get_reference(atoms_elem)
            if atoms.type_ is None:
                continue
            assert issubclass(atoms.type_, typemap['Table'])
            if not isinstance_m(atoms, ['Table']):
                continue
            for col in atoms.columns:
                if col.type_ is None:
                    continue
                assert issubclass(col.type_, typemap['Series'])
                if isinstance_m(col, ['Series']):
                    if col.name not in atoms_dtyps:
                        msg = f'invalid parameter \'{col.name}\' in \'atoms\''
                        raise_exception(col, StaticValueError, msg)
                    if (col.type_.datatype and
                       not issubclass(col.type_.datatype, atoms_dtyps[col.name])):
                        msg = (f'\'{col.name}\' must have type {atoms_dtyps[col.name]}'
                               f' but has type {col.type_.datatype}')
                        raise_exception(col, StaticTypeError, msg)
            symbols = atoms.get_column('symbols')
            if symbols:
                for elem in symbols.elements:
                    if elem.value not in ase.data.chemical_symbols:
                        msg = f'invalid chemical symbol {elem.value} in \'symbols\''
                        raise_exception(elem, StaticValueError, msg)
            elif not atoms.columns_tuple:
                raise_exception(atoms, StaticValueError, 'missing chemical symbols')
            for column in ('x', 'y', 'z'):
                coord = atoms.get_column(column)
                if coord:
                    check_units(coord, '[length]')
                elif not atoms.columns_tuple:
                    raise_exception(atoms, StaticValueError, 'missing atomic coordinates')
            momenta = ('px', 'py', 'pz')
            if any(atoms.get_column(p) is not None for p in momenta):
                if not all(atoms.get_column(p) is not None for p in momenta):
                    missed = next(p for p in momenta if atoms.get_column(p) is None)
                    msg = f'{missed} missing in \'atoms\''
                    raise_exception(atoms, StaticValueError, msg)
            if self.tab.get_column('cell') is not None:
                for cell_elem in self.tab.get_column('cell').elements:
                    if hasattr(get_reference(cell_elem), 'inp_units'):
                        check_units(get_reference(cell_elem), '[length]')
            if any(atoms.get_column(x) is not None for x in ('px', 'py', 'pz')):
                for column in ('px', 'py', 'pz'):
                    momentum = atoms.get_column(column)
                    if momentum is not None:
                        check_units(momentum, '[length]*[mass]/[time]')
            if atoms.get_column('masses') is not None:
                check_units(atoms.get_column('masses'), '[mass]')
    return rtype


def amml_calculator_type(self):
    """evaluate the type of calculator object"""
    assert self.parameters is None or isinstance_m(self.parameters, ['Table'])
    return DType('AMMLCalculator', (typemap['AMMLCalculator'],), {})


def amml_algorithm_type(self):
    """evaluate the type of algorithm object"""
    assert self.parameters is None or isinstance_m(self.parameters, ['Table'])
    return DType('AMMLAlgorithm', (typemap['AMMLAlgorithm'],), {})


def amml_property_type(self):
    """evaluate the type of property object"""
    if self.struct.type_ and not issubclass(self.struct.type_, typemap['AMMLStructure']):
        msg = f'Parameter \"{self.struct.ref.name}\" must be an AMML structure'
        raise_exception(self.struct, StaticTypeError, msg)
    if self.calc and self.calc.type_ and not issubclass(self.calc.type_, typemap['AMMLCalculator']):
        msg = f'parameter \"{self.calc.name}\" must be an AMML calculator'
        raise_exception(self.calc, StaticTypeError, msg)
    if (isinstance_m(self.struct.ref.parameter, ['AMMLStructure']) and
       self.struct.ref.parameter.tab is not None):
        atoms = self.struct.ref.parameter.tab.get_column('atoms')
        if all(isinstance_m(get_reference(e), ['Table']) for e in atoms.elements):
            symbs = [get_reference(e).get_column('symbols').elements for e in atoms.elements]
            for constr in self.constrs:
                if isinstance_m(constr.ref.parameter, ['AMMLConstraint']):
                    if isinstance_m(constr.ref.parameter.fixed, ['Series']):
                        elems = constr.ref.parameter.fixed.elements
                        if not all(len(elems) == len(s) for s in symbs):
                            msg = ('The list of fixed/non-fixed atoms in constraints'
                                   ' and atoms in structure have different lengths')
                            raise StaticValueError(msg)
    if self.algo is not None:
        if self.algo.type_ and not issubclass(self.algo.type_, typemap['AMMLAlgorithm']):
            msg = f'Parameter \"{self.algo.ref.name}\" must be an AMML algorithm'
            raise_exception(self.algo, StaticTypeError, msg)
        if (isinstance_m(self.algo.ref.parameter, ['AMMLAlgorithm']) and
           self.algo.ref.parameter.name == 'RDF'):
            algo_name = self.algo.ref.parameter.name
            if (isinstance_m(self.struct.ref.parameter, ['AMMLStructure']) and
               self.struct.ref.parameter.tab is not None):
                struct_tab = self.struct.ref.parameter.tab
                if struct_tab.get_column('cell') is None:
                    msg = f'Algorithm \"{algo_name}\" requires structure with cell'
                    raise_exception(struct_tab, StaticValueError, msg)
    return DType('AMMLProperty', (typemap['AMMLProperty'],), {})


def amml_constraint_type(self):
    """evaluate the type of constraint object"""
    if self.fixed is not None:
        if self.fixed.type_:
            msg = 'parameter must be a boolean series'
            if not issubclass(self.fixed.type_, typemap['Series']):
                raise_exception(self.fixed, StaticTypeError, msg)
            if self.fixed.type_.datatype and not issubclass(self.fixed.type_.datatype, bool):
                raise_exception(self.fixed, StaticTypeError, msg)
    if self.direction is not None:
        if (not all(isinstance(e, int) for e in self.direction.elements)
           or len(self.direction.elements) != 3):
            msg = 'direction vector must be 1-dim integer array with 3 elements'
            raise_exception(self.direction, StaticTypeError, msg)
    return DType('AMMLConstraint', (typemap['AMMLConstraint'],), {})


def check_numerical_props(tab):
    """check if a table contains only series with given names of float type"""
    keys = ['energy', 'enthalpy', 'entropy', 'free_energy', 'zpe', 'temperature']
    if tab is not None:
        if tab.columns:
            for prop in tab.columns:
                if prop.name not in keys:
                    msg = f'invalid property \'{prop.name}\''
                    raise_exception(prop, StaticValueError, msg)
                check_series_type(prop, (typemap['Quantity'], float))
        if tab.columns_tuple:
            for prop in tab.columns_tuple.params:
                check_series_type(prop, (typemap['Quantity'], float))


def chem_reaction_type(self):
    """evaluate the type of a chemical reaction object"""
    check_numerical_props(self.props)
    for term in self.educts + self.products:
        if not isinstance_m(term.species.ref.parameter, ['ChemSpecies']):
            msg = f'{term.species.ref.name} is no chemical species'
            raise_exception(term, StaticTypeError, msg)
    return DType('ChemReaction', (typemap['ChemReaction'],), {})


def chem_species_type(self):
    """evaluate the type of a chemical species object"""
    if self.composition:
        if self.composition.type_ and not issubclass(self.composition.type_, str):
            raise StaticTypeError('species composition must be of string type')
    check_numerical_props(self.props)
    return DType('ChemSpecies', (typemap['ChemSpecies'],), {})


def add_type_properties(metamodel):
    """Add object class properties using monkey style patching"""
    mapping_dict = {
        'Print': print_type,
        'PrintParameter': print_parameter_type,
        'Variable': variable_type,
        'GeneralReference': general_reference_type,
        'Power': power_type,
        'Factor': factor_type,
        'Term': term_type,
        'Expression': expression_type,
        'Operand': operand_type,
        'BooleanOperand': operand_type,
        'And': boolean_expression_type,
        'Or': boolean_expression_type,
        'Not': boolean_expression_type,
        'Real': real_imag_type,
        'Imag': real_imag_type,
        'IfFunction': if_expression_type,
        'IfExpression': if_expression_type,
        'Comparison': comparison_type,
        'ObjectImport': object_import_type,
        'FunctionCall': function_call_type,
        'Quantity': quantity_type,
        'Tuple': tuple_type,
        'Series': series_type,
        'Table': table_type,
        'Dict': dict_type,
        'AltTable': alt_table_type,
        'Tag': tag_type,
        'BoolArray': array_type,
        'StrArray': array_type,
        'IntArray': array_type,
        'FloatArray': array_type,
        'ComplexArray': array_type,
        'IntSubArray': array_type,
        'FloatSubArray': array_type,
        'ComplexSubArray': array_type,
        'IterableProperty': iterable_property_type,
        'IterableQuery': iterable_query_type,
        'ConditionIn': condition_in_type,
        'ConditionComparison': condition_comparison_type,
        'Range': range_type,
        'In': in_type,
        'Any': boolean_reduce_type,
        'All': boolean_reduce_type,
        'Sum': sum_type,
        'Map': map_type,
        'Filter': filter_type,
        'Reduce': reduce_type,
        'AMMLStructure': amml_structure_type,
        'AMMLCalculator': amml_calculator_type,
        'AMMLAlgorithm': amml_algorithm_type,
        'AMMLProperty': amml_property_type,
        'AMMLConstraint': amml_constraint_type,
        'ChemReaction': chem_reaction_type,
        'ChemSpecies': chem_species_type
    }
    for key, function in mapping_dict.items():
        metamodel[key].type_ = cached_property(textxerror_wrap(function))
        metamodel[key].type_.__set_name__(metamodel[key], 'type_')

    metamodel['Dummy'].type_ = None
    metamodel['Bool'].type_ = bool
    metamodel['String'].type_ = str
    metamodel['Program'].type_ = str
    metamodel['Type'].type_ = get_dtype('Type', 'Table')
    metamodel['ConditionNot'].type_ = typemap['Series']
    metamodel['ConditionAnd'].type_ = typemap['Series']
    metamodel['ConditionOr'].type_ = typemap['Series']
