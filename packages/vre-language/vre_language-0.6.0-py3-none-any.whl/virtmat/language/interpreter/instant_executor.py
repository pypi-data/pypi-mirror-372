# pylint: disable=protected-access
"""
Language interpreter for immediate local evaluation using python
"""
import pathlib
from operator import gt, lt, eq, ne, le, ge, not_, invert, and_, or_
from functools import partial, reduce, cached_property
import pandas
import numpy
import pint_pandas
from pint.errors import PintError
from textx import get_children_of_type, get_parent_of_type
from textx.exceptions import TextXError
from virtmat.language.constraints.imports import get_object_import
from virtmat.language.metamodel.function import subst
from virtmat.language.utilities.textx import isinstance_m
from virtmat.language.utilities.formatters import formatter
from virtmat.language.utilities.errors import textxerror_wrap, error_handler
from virtmat.language.utilities.errors import SubscriptingError, PropertyError
from virtmat.language.utilities.errors import InvalidUnitError, RuntimeTypeError
from virtmat.language.utilities.errors import RuntimeValueError
from virtmat.language.utilities.typemap import typemap, DType, checktype, checktype_
from virtmat.language.utilities.typemap import is_table_like, table_like_type
from virtmat.language.utilities.types import ScalarNumerical, is_array
from virtmat.language.utilities.types import is_numeric_type, is_numeric_scalar_type
from virtmat.language.utilities.types import is_scalar_type, is_scalar, settype
from virtmat.language.utilities.types import get_datatype_name
from virtmat.language.utilities.lists import get_array_aslist
from virtmat.language.utilities.units import get_units, get_dimensionality
from virtmat.language.utilities.units import convert_series_units, convert_quantity_units
from virtmat.language.utilities.serializable import load_value
from virtmat.language.utilities.arrays import get_nested_array
from virtmat.language.utilities.logging import get_logger
from virtmat.language.utilities import amml, chemistry

pint_pandas.pint_array.DEFAULT_SUBDTYPE = None

comp_operators = ('>', '<', '==', '!=', '<=', '>=')
comp_functions = (gt, lt, eq, ne, le, ge)
comp_map = dict(zip(comp_operators, comp_functions))


def log_eval(func):
    """a logger indicating when a value property is eventually evaluated"""
    logger = get_logger(__name__)

    def logged_value(obj):
        ret_val = func(obj)
        logger.debug(' evaluated %s', repr(obj))
        return ret_val
    return logged_value


def program_value(self):
    """Evaluate print objects in the order of occurence"""
    vals = [p.value for p in get_children_of_type('Print', self) if p.value]
    show = getattr(self, '_tx_model_params').get('display_graphics', True)
    for view in get_children_of_type('View', self):
        view.display(show=show)
    return '\n'.join(vals)


def variable_value(self):
    """Evaluate a variable"""
    return self.parameter.value


def expression_value(self):
    """Evaluate an arithmetic expression"""
    value = self.operands[0].value
    for operation, operand in zip(self.operators, self.operands[1:]):
        if operation == '+':
            value += operand.value
        else:
            value -= operand.value
    return value


def term_value(self):
    """Evaluate a term"""
    value = self.operands[0].value
    for operation, operand in zip(self.operators, self.operands[1:]):
        if operation == '*':
            value *= operand.value
        else:
            value /= operand.value
    return value


def factor_value(self):
    """Evaluate a factor"""
    value = self.operands[-1].value
    for operand in self.operands[-2::-1]:
        value = operand.value**value
    return value


def power_value(self):
    """Evaluate a power"""
    value = self.operand.value
    return -value if self.sign == '-' else value


def operand_value(self):
    """Evaluate an operand"""
    return self.operand.value


def binary_operation_value(self, operator):
    """Evaluate binary operation expression"""
    return reduce(operator, (o.value for o in self.operands))


def or_value(self):
    """Evaluate short-circuiting OR expression"""
    null = False
    for operand in self.operands:
        if operand.value:
            return True
        if operand.value is None:
            null = True
    return False if not null else None


def and_value(self):
    """Evaluate short-circuiting AND expression"""
    null = False
    for operand in self.operands:
        if operand.value is None:
            null = True
        elif not operand.value:
            return False
    return True if not null else None


def not_value(self, operator):
    """Evaluate NOT expression"""
    if self.not_:
        if self.operand.value is None:
            return None
        return operator(self.operand.value)
    return self.operand.value


@property
@error_handler
@textxerror_wrap
def print_value(self):
    """Evaluate the print function"""
    return ' '.join(formatter(par.value) for par in self.params)


def print_parameter_value(self):
    """Evaluate the print parameter"""
    value = self.param.value
    if self.inp_units is None:
        return value
    if isinstance(value, typemap['Quantity']):
        return convert_quantity_units(value, self.inp_units)
    assert isinstance(value, typemap['Series'])
    if isinstance(value.dtype, pint_pandas.PintType):
        return convert_series_units(value, self.inp_units)
    assert value.dtype == 'object'
    elems = [convert_quantity_units(e, self.inp_units) for e in value]
    return typemap['Series'](name=value.name, data=elems, dtype='object')


def type_value(self):
    """Evaluate the type function"""
    par = self.param
    name = par.ref.name if isinstance_m(par, ['GeneralReference']) else None
    datatype = getattr(par.type_, 'datatype', None)
    numeric = par.type_ and is_numeric_type(par.type_)
    dct = {'name': name,
           'type': par.type_ and par.type_.__name__,
           'scalar': par.type_ and is_scalar_type(par.type_),
           'numeric': numeric,
           'datatype': get_datatype_name(datatype)}
    if numeric:
        try:
            dct['dimensionality'] = str(get_dimensionality(par.value))
            dct['units'] = str(get_units(par.value))
        except TextXError:
            pass
    return typemap['Table']([dct])


def if_expression_value(self):
    """Evaluate an if-expression object, returns the expression value"""
    return self.true_.value if self.expr.value else self.false_.value


def comparison_value(self):
    """Evaluate a comparison expression object"""
    for operand in (self.left.value, self.right.value):
        if isinstance(operand, typemap['Quantity']):
            if operand.magnitude is pandas.NA:
                return None
            assert isinstance(operand.magnitude, ScalarNumerical)
            if isinstance(operand.magnitude, complex):
                assert self.operator in ('==', '!=')
        else:
            assert isinstance(operand, (bool, str))
            assert self.operator in ('==', '!=')
    return bool(comp_map[self.operator](self.left.value, self.right.value))


@settype
def object_import_value(self):
    """Evaluate an imported non-callable object"""
    obj = get_object_import(self)
    if callable(obj):
        raise RuntimeTypeError(f'callable import {obj} has no value')
    return obj


@settype
def function_call_value(self):
    """Evaluate a function_call object"""
    if isinstance_m(self.function, ['ObjectImport']):
        obj = get_object_import(self.function)
        assert callable(obj)
        par_values = [p.value for p in self.params]
        try:
            ret = obj(*par_values)
        except PintError as err:
            raise err
        except TypeError as err:
            raise RuntimeTypeError(str(err)) from err
    else:
        assert isinstance_m(self.function, ['FunctionDefinition'])
        if not get_parent_of_type('FunctionDefinition', self):
            ret = self.expr.value
        else:  # not covered
            ret = None
    return ret


def tuple_value(self):
    """Evaluate a tuple object"""
    return tuple(param.value for param in self.params)


def series_value(self):
    """Evaluate a series object"""
    datatype = self.type_.datatype
    if self.name is None:
        return checktype_(load_value(self.url, self.filename), self.type_)
    if datatype is not None and issubclass(datatype, numpy.ndarray):
        elements = (e.value for e in self.elements)
        if all(is_numeric_type(e.type_) for e in self.elements):
            elements = (pandas.NA if e is None else e for e in elements)
            elements = (typemap['Quantity'](e, self.inp_units) for e in elements)
        return typemap['Series'](name=self.name, data=elements)
    elements = (e if isinstance(e, ScalarNumerical) else e.value for e in self.elements)
    if datatype in (int, float, complex):
        units = self.inp_units if self.inp_units else 'dimensionless'
        dtype = pint_pandas.PintType(units)
    elif datatype is not None and issubclass(datatype, typemap['Quantity']):
        elements = list(elements)
        if len(set(e.units for e in elements)) != 1:
            msg = 'Numeric type series must have elements of the same units.'
            raise InvalidUnitError(msg)
        dtype = 'object'
    else:
        dtype = None
    return typemap['Series'](name=self.name, data=elements, dtype=dtype)


def table_value(self):
    """Evaluate a table object"""
    if self.url is not None or self.filename is not None:
        retval = checktype_(load_value(self.url, self.filename), self.type_)
    else:
        retval = pandas.concat((c.value for c in self.columns), axis=1)
    return retval


def dict_value(self):
    """evaluate dictionary value"""
    return dict(zip(self.keys, (v.value for v in self.values)))


def alt_table_value(self):
    """evaluate an alt table object"""
    if self.keys and self.values:
        return pandas.DataFrame.from_records([dict_value(self)])
    return self.tab.value


def bool_str_array_value(self):
    """evaluate an array object of datatypes bool and str"""
    if self.url or self.filename:
        return checktype_(load_value(self.url, self.filename), self.type_)
    return numpy.array(get_array_aslist(self.elements))


def numeric_array_value(self):
    """evaluate an array object of numeric datatype"""
    if self.url or self.filename:
        return checktype_(load_value(self.url, self.filename), self.type_)
    data = numpy.array(get_array_aslist(self.elements), dtype=self.type_.datatype)
    units = self.inp_units if self.inp_units else 'dimensionless'
    return self.type_(data, units)


def numeric_subarray_value(self):
    """evaluate a subarray object of numeric datatype"""
    return numpy.array(get_array_aslist(self.elements), dtype=self.type_.datatype)


@settype
def get_sliced_value(obj):
    """return a slice and/or array of an iterable data structure object"""
    value = obj.obj.value
    if obj.slice:
        value = value[obj.start:obj.stop:obj.step]
    if obj.array:
        array = value.values
        if isinstance(array, pint_pandas.PintArray):
            return array.quantity
        assert isinstance(array, numpy.ndarray)
        if issubclass(array.dtype.type, (numpy.str_, numpy.bool_)):
            return array
        if isinstance(array[0], str):
            return array.astype(str)
        if is_array(array[0]):
            return get_nested_array(array)
        msg = 'array datatype must be numeric, boolean, string or array'
        raise RuntimeTypeError(msg)
    return value


@settype
def general_reference_value(self):
    """Evaluate a reference with a list of optional data accessors"""
    retval = self.ref.value
    for accessor in self.accessors:
        if accessor.index is not None:
            try:
                if isinstance(retval, typemap['Table']):
                    dfr = retval.iloc[[accessor.index]]
                    retval = tuple(next(dfr.itertuples(index=False, name=None)))
                elif isinstance(retval, typemap['Tuple']):
                    retval = retval[accessor.index]
                elif isinstance(retval, typemap['Series']):
                    retval = retval.values[accessor.index]
                elif is_array(retval):
                    retval = retval[accessor.index]
                elif isinstance(retval, (amml.AMMLObject, chemistry.ChemBase)):
                    retval = retval[accessor.index]
                else:
                    raise TypeError(f'invalid type {type(retval)}')  # not covered
            except IndexError as err:  # not covered
                msg = f'{str(err)}: index {accessor.index}, length {len(retval)}'
                raise SubscriptingError(msg) from err
        else:
            try:
                if isinstance(retval, (typemap['Table'], typemap['Dict'])):
                    retval = retval[accessor.id]
                elif isinstance(retval, (amml.AMMLObject, chemistry.ChemBase)):
                    retval = retval[accessor.id]
                else:  # not covered
                    raise TypeError(f'invalid type {type(retval)}')
            except KeyError as err:  # not covered
                msg = f'property "{accessor.id}" not available'
                raise PropertyError(msg) from err
    return retval


def iterable_property_value(self):
    """Evaluate an iterable property object"""
    if hasattr(self, 'name_') and self.name_:
        ret = self.obj.value.name
    elif hasattr(self, 'columns') and self.columns:
        ret = self.obj.value.columns.to_series(name='columns')
    else:
        ret = get_sliced_value(self)
    return ret


def iterable_query_value(self):
    """Evaluate an iterable query object"""
    if self.where:
        if self.condition:
            val = self.obj.value[self.condition.value]
        elif self.where_all:
            cond_values = (c.value for c in self.conditions)
            val = self.obj.value[reduce(lambda x, y: x & y, cond_values)]
        elif self.where_any:
            cond_values = (c.value for c in self.conditions)
            val = self.obj.value[reduce(lambda x, y: x | y, cond_values)]
    else:
        val = self.obj.value
    if self.columns:
        val = val[self.columns]
    return val.reset_index(drop=True)


def condition_in_value(self):
    """Evaluate a condition-in"""
    qobj_ref_val = get_parent_of_type('IterableQuery', self).obj.value
    if isinstance(qobj_ref_val, pandas.core.frame.DataFrame):
        column = qobj_ref_val[self.column]
    else:
        assert isinstance(qobj_ref_val, pandas.core.series.Series)
        column = qobj_ref_val
    if self.parameter:  # not covered
        return column.isin(self.parameter.value.tolist())
    return column.isin([p.value for p in self.params])


def condition_comparison_value(self):
    """Evaluate a condition comparison"""
    qobj_ref_val = get_parent_of_type('IterableQuery', self).obj.value
    if is_table_like(qobj_ref_val):
        column_left = qobj_ref_val[self.column_left] if self.column_left else None
        column_right = qobj_ref_val[self.column_right] if self.column_right else None
    else:
        assert isinstance(qobj_ref_val, typemap['Series'])
        msg = f'column name must be "{qobj_ref_val.name}" but is '
        if self.column_left and self.column_left != qobj_ref_val.name:
            raise RuntimeValueError(msg+f'"{self.column_left}"')
        if self.column_right and self.column_right != qobj_ref_val.name:  # not covered
            raise RuntimeValueError(msg+f'"{self.column_right}"')
        column_left = qobj_ref_val if self.column_left else None
        column_right = qobj_ref_val if self.column_right else None
    left = column_left if self.column_left else self.operand_left.value
    right = column_right if self.column_right else self.operand_right.value
    assert isinstance(left, typemap['Series'])
    if len(left):
        right0 = right[0] if isinstance(right, typemap['Series']) else right
        try:
            comp_map[self.operator](left[0], right0)
        except (TypeError, ValueError) as err:
            msg = f'invalid comparison of types {type(left[0])} and {type(right0)}'
            raise RuntimeTypeError(msg) from err
        return comp_map[self.operator](left, right)
    return typemap['Series'](dtype=bool)  # not covered


def plain_type_value(self):
    """Evaluate an object of plain type (string or boolean)"""
    if self.__value is None:
        self.__value = checktype_(load_value(self.url, self.filename), self.type_)
    return self.__value


def quantity_value(self):
    """Evaluate a quantity object"""
    if self.inp_value is None:
        return checktype_(load_value(self.url, self.filename), self.type_)
    magnitude = numpy.nan if self.inp_value.value is None else self.inp_value.value
    return typemap['Quantity'](magnitude, self.inp_units)


def range_value(self):
    """Evaluate the range builtin function"""
    unit = self.start.value.units
    data = numpy.arange(self.start.value.magnitude,
                        self.stop.value.to(unit).magnitude,
                        self.step.value.to(unit).magnitude).tolist()
    dtype = pint_pandas.PintType(unit)
    name = self.parent.name if hasattr(self.parent, 'name') else 'range'
    return typemap['Series'](data=data, name=name, dtype=dtype)


def map_value(self):
    """Evaluate the map builtin function"""
    name = self.parent.name if hasattr(self.parent, 'name') else 'map'
    func = self.lambda_ if self.lambda_ else self.function
    dtypes = []
    values = []
    for par in self.params:
        val = par.value
        assert par.type_ is not None
        if issubclass(par.type_, table_like_type):
            assert is_table_like(val)
            dtypes.append(None)
            values.append((dict(p) for _, p in val.iterrows()))
        else:
            values.append(val)
            dtype = par.type_.datatype
            if dtype is not None and is_numeric_scalar_type(dtype):
                dtype = DType('Quantity', (typemap['Quantity'],), {'datatype': dtype})
            dtypes.append(dtype)
    if isinstance_m(func, ['ObjectImport']):
        data = map(get_object_import(func), *values)
        return typemap['Series'](name=name, data=data)
    data = [subst(self, func, par, dtypes).value for par in zip(*values)]
    if data and all(isinstance(v, dict) for v in data):
        return typemap['Table'].from_records(data)
    if data and all(isinstance(v, typemap['Quantity']) for v in data):
        assert all(is_scalar(e.magnitude) or pandas.isna(e.magnitude) for e in data)
        dtype = pint_pandas.PintType(next(iter(data)).units)
        data = (v.magnitude for v in data)
        return typemap['Series'](name=name, data=data, dtype=dtype)
    return typemap['Series'](name=name, data=data)


def filter_value(self):
    """Evaluate the filter builtin function"""
    filter_f = self.lambda_ if self.lambda_ else self.function
    filter_d = self.parameter.value.dropna()
    assert self.parameter.type_ is not None
    if issubclass(self.parameter.type_, typemap['Series']):
        name = self.parent.name if hasattr(self.parent, 'name') else 'filter'
        if isinstance_m(filter_f, ['ObjectImport']):
            data = filter(get_object_import(filter_f), filter_d)
            return typemap['Series'](name=name, data=data)
        dtype = self.parameter.type_.datatype
        if is_numeric_scalar_type(dtype):
            dtype = DType('Quantity', (typemap['Quantity'],), {'datatype': dtype})
        data = (p for p in filter_d if subst(self, filter_f, (p,), (dtype,)).value)
        return typemap['Series'](name=name, data=data)
    assert is_table_like(filter_d)
    assert not isinstance_m(filter_f, ['ObjectImport'])
    recs = (dict(p) for _, p in filter_d.iterrows())
    mask = (subst(self, filter_f, (p,), (None,)).value for p in recs)
    return filter_d[typemap['Series'](mask)]


def reduce_value(self):
    """Evaluate the reduce builtin function"""
    func = self.lambda_ if self.lambda_ else self.function
    if isinstance(self.parameter.value, typemap['Series']):
        elements = iter(self.parameter.value)
        if isinstance_m(func, ['ObjectImport']):
            return reduce(get_object_import(func), elements)
        value = next(elements)
        dtype = self.parameter.type_.datatype
        if dtype and is_numeric_scalar_type(dtype):
            dtype = DType('Quantity', (typemap['Quantity'],), {'datatype': dtype})
        for elem in elements:
            value = subst(self, func, (value, elem), (dtype, dtype)).value
        return value
    assert not isinstance_m(func, ['ObjectImport'])
    elements = (dict(r) for _, r in self.parameter.value.iterrows())
    value = next(elements)
    for elem in elements:
        value = subst(self, func, (value, elem), (None, None)).value
    return typemap['Table'].from_records([value])


def sum_value(self):
    """Evaluate sum function"""
    if self.parameter:
        return sum(self.parameter.value)
    return sum(p.value for p in self.params)


def any_value(self):
    """Evaluate short-circuiting any function"""
    null = False
    if self.parameter:
        for operand in self.parameter.value:
            if operand:
                return True
            if operand is None:
                null = True
        return False if not null else None
    for operand in self.params:
        if operand.value:
            return True
        if operand.value is None:
            null = True
    return False if not null else None


def all_value(self):
    """Evaluate short-circuiting all function"""
    null = False
    if self.parameter:
        for operand in self.parameter.value:
            if operand is None:
                null = True
            elif not operand:
                return False
        return True if not null else None
    for operand in self.params:
        if operand.value is None:
            null = True
        elif not operand.value:
            return False
    return True if not null else None


@settype
def in_value(self):
    """Evaluate membership of an object in a tuple, series or table"""
    if self.parameter:
        array = self.parameter.value.values
        if self.element.value in array:
            return True
        if None in array or any(array.isna()):
            return None
        return False
    null = False
    for param in self.params:
        if self.element.value == param.value:
            return True
        if (param.value is None or isinstance(param.value, typemap['Quantity'])
           and numpy.isnan(param.value)):
            null = True
    return None if null else False


def amml_structure_value(self):
    """Evaluate an AMML structure"""
    if self.filename or self.url:
        suffix = pathlib.Path(self.filename).suffix
        if self.filename and suffix not in ['.yml', '.yaml', '.json']:
            return amml.AMMLStructure.from_ase_file(self.filename)
        return checktype_(load_value(self.url, self.filename), self.type_)
    return amml.AMMLStructure(self.tab.value, self.name)


def amml_calculator_value(self):
    """Evaluate an AMML calculator object"""
    params = pandas.DataFrame() if self.parameters is None else self.parameters.value
    return amml.Calculator(self.name, params, pinning=self.pinning,
                           version=self.version, task=self.task)


def amml_algorithm_value(self):
    """Evaluate an AMML algorithm object"""
    params = pandas.DataFrame() if self.parameters is None else self.parameters.value
    return amml.Algorithm(self.name, params, self.many_to_one)


def amml_property_value(self):
    """Evaluate an AMML property object"""
    return amml.Property(self.names, self.struct.value,
                         calculator=self.calc and self.calc.value,
                         algorithm=self.algo and self.algo.value,
                         constraints=[c.value for c in self.constrs])


def amml_constraint_value(self):
    """Evaluate an AMML constraint object"""
    direction = self.direction and self.direction.value
    return amml.Constraint(self.name, fixed=self.fixed.value, direction=direction)


def chem_reaction_value(self):
    """Evaluate a chemical reaction object"""
    species = [t.species.value for t in self.educts+self.products]
    coeffs = []
    for term in self.educts:
        coeffs.append(-term.coefficient)
    for term in self.products:
        coeffs.append(term.coefficient)
    terms = [{'coefficient': c, 'species': s} for c, s in zip(coeffs, species)]
    props = self.props and self.props.value
    return chemistry.ChemReaction(terms, props)


def chem_species_value(self):
    """Evaluate a chemical species object"""
    props = self.props and self.props.value
    composition = self.composition and self.composition.value
    return chemistry.ChemSpecies(self.name, composition, props=props)


def add_value_properties(metamodel):
    """Add object class properties using monkey style patching"""
    mapping_dict = {
        'Program': program_value,
        'Variable': variable_value,
        'GeneralReference': general_reference_value,
        'Factor': factor_value,
        'Term': term_value,
        'Expression': expression_value,
        'Power': power_value,
        'Operand': operand_value,
        'BooleanOperand': operand_value,
        'And': and_value,
        'Or': or_value,
        'Not': partial(not_value, operator=not_),
        'PrintParameter': print_parameter_value,
        'Type': type_value,
        'Real': lambda x: x.parameter.value.real,
        'Imag': lambda x: x.parameter.value.imag,
        'IfFunction': if_expression_value,
        'IfExpression': if_expression_value,
        'Comparison': comparison_value,
        'ObjectImport': object_import_value,
        'FunctionCall': function_call_value,
        'Tuple': tuple_value,
        'Series': series_value,
        'Table': table_value,
        'Dict': dict_value,
        'AltTable': alt_table_value,
        'BoolArray': bool_str_array_value,
        'StrArray': bool_str_array_value,
        'IntArray': numeric_array_value,
        'FloatArray': numeric_array_value,
        'ComplexArray': numeric_array_value,
        'IntSubArray': numeric_subarray_value,
        'FloatSubArray': numeric_subarray_value,
        'ComplexSubArray': numeric_subarray_value,
        'IterableProperty': iterable_property_value,
        'IterableQuery': iterable_query_value,
        'ConditionOr': partial(binary_operation_value, operator=or_),
        'ConditionAnd': partial(binary_operation_value, operator=and_),
        'ConditionNot': partial(not_value, operator=invert),
        'ConditionComparison': condition_comparison_value,
        'ConditionIn': condition_in_value,
        'String': plain_type_value,
        'Bool': plain_type_value,
        'Quantity': quantity_value,
        'Range': range_value,
        'In': in_value,
        'Any': any_value,
        'All': all_value,
        'Sum': sum_value,
        'Map': map_value,
        'Filter': filter_value,
        'Reduce': reduce_value,
        'AMMLStructure': amml_structure_value,
        'AMMLCalculator': amml_calculator_value,
        'AMMLAlgorithm': amml_algorithm_value,
        'AMMLProperty': amml_property_value,
        'AMMLConstraint': amml_constraint_value,
        'ChemReaction': chem_reaction_value,
        'ChemSpecies': chem_species_value
    }
    for key, func in mapping_dict.items():
        metamodel[key].value = cached_property(textxerror_wrap(checktype(log_eval(func))))
        metamodel[key].value.__set_name__(metamodel[key], 'value')
    metamodel['Print'].value = print_value
