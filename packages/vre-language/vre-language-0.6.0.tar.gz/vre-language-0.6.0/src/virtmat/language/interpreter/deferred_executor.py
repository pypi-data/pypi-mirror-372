# pylint: disable=protected-access
"""
Language interpreter for delayed evaluation
The methods below return the relevant Python functions together with a tuple
with their parameters. The evaluations are lazy and performed via delegation.
"""
import pathlib
from itertools import islice, chain
from functools import partial, reduce, cached_property, cache
from operator import gt, lt, eq, ne, le, ge
from operator import add, neg, mul, truediv
from operator import and_, or_, not_, invert
import numpy
import pandas
import pint_pandas
from pint.errors import PintError
from textx import get_parent_of_type, get_metamodel
from virtmat.language.constraints.imports import get_object_import
from virtmat.language.utilities.textx import isinstance_m
from virtmat.language.utilities.serializable import load_value
from virtmat.language.utilities.formatters import formatter
from virtmat.language.utilities.errors import textxerror_wrap, error_handler
from virtmat.language.utilities.errors import SubscriptingError, PropertyError
from virtmat.language.utilities.errors import InvalidUnitError, RuntimeValueError
from virtmat.language.utilities.errors import RuntimeTypeError, TEXTX_WRAPPED_EXCEPTIONS
from virtmat.language.utilities.typemap import typemap, checktype, checktype_
from virtmat.language.utilities.typemap import is_table_like_type, is_table_like
from virtmat.language.utilities.types import is_array, is_scalar, settype
from virtmat.language.utilities.types import ScalarNumerical, get_datatype_name
from virtmat.language.utilities.types import is_scalar_type, is_numeric_type
from virtmat.language.utilities.types import NC
from virtmat.language.utilities.lists import get_array_aslist
from virtmat.language.utilities.units import get_units, get_dimensionality
from virtmat.language.utilities.units import convert_series_units, convert_quantity_units
from virtmat.language.utilities.arrays import get_nested_array
from virtmat.language.utilities.logging import get_logger
from virtmat.language.utilities import amml, chemistry
from .instant_executor import program_value

pint_pandas.pint_array.DEFAULT_SUBDTYPE = None

# binary operator--function map
binop_map = {'>': gt, '<': lt, '==': eq, '!=': ne, '<=': le, '>=': ge,
             '+': add, '-': lambda x, y: add(x, neg(y)), '*': mul, '/': truediv,
             'or': lambda x, y: x or y, 'and': lambda x, y: x and y,
             'or_': or_, 'and_': and_, '**': pow}


def dummies_right(func, args):
    """reorder arguments so that dummy variables are the end of the list"""
    params = []
    order = []
    for index, arg in enumerate(args):
        if not isinstance_m(arg, ['Dummy']):
            params.append(arg)
            order.append(index)
    for index, arg in enumerate(args):
        if isinstance_m(arg, ['Dummy']):
            params.append(arg)
            order.append(index)
    return lambda *x: func(*[e for i, e in sorted(zip(order, x))]), tuple(params)


def log_eval(func):
    """a logger indicating when a func property is eventually evaluated"""
    logger = get_logger(__name__)

    def logged_func(obj):
        ret_func, pars = func(obj)
        obj_repr = repr(obj)

        def new_ret_func(*args, **kwargs):
            ret_val = ret_func(*args, **kwargs)
            logger.debug(' evaluated %s', obj_repr)
            return ret_val
        return new_ret_func, pars
    return logged_func


def cache_eval(func):
    """cache the function to avoid repeated evaluations, requires hashable pars"""
    def cached_func(obj):
        ret_func, pars = func(obj)
        return cache(ret_func), pars
    return cached_func


def strict_nc(func):
    """apply to functions that cannot use NC"""
    def nc_func(obj):
        ret_func, pars = func(obj)

        def new_ret_func(*args, **kwargs):
            if any(a is NC for a in args):
                return NC
            return ret_func(*args, **kwargs)
        return new_ret_func, pars
    return nc_func


@checktype
def func_value(self):
    """lazy-evaluate an object by wrapping the call to obj.func property"""
    func, pars = self.func
    return func(*map(lambda p: lambda: p.value, pars))


def print_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    func_pars = [par.func for par in self.params]
    funcs = [t[0] for t in func_pars]
    pars = tuple(t[1] for t in func_pars)
    pars_lens = [len(p) for p in pars]

    def retfunc(*args):
        iargs = iter(args)
        pargs = [list(islice(iargs, pl)) for pl in pars_lens]
        values = [formatter(f(*a)) for f, a in zip(funcs, pargs)]
        return ' '.join(values)
    return retfunc, tuple(chain.from_iterable(pars))


def print_parameter_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    if self.inp_units is None:
        return self.param.func
    units = self.inp_units
    func, pars = self.param.func

    def retfunc(*args):
        val = func(*args)
        if val is NC:
            return NC
        if isinstance(val, typemap['Quantity']):
            return convert_quantity_units(val, units)
        assert isinstance(val, typemap['Series'])
        if isinstance(val.dtype, pint_pandas.PintType):
            return convert_series_units(val, units)
        assert val.dtype == 'object'
        elems = [convert_quantity_units(elem, units) for elem in val]
        return typemap['Series'](name=val.name, data=elems, dtype='object')
    return retfunc, pars


def type_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    par = self.param
    name = par.ref.name if isinstance_m(par, ['GeneralReference']) else None
    datatype = getattr(par.type_, 'datatype', None)
    scalar = par.type_ and is_scalar_type(par.type_)
    numeric = par.type_ and is_numeric_type(par.type_)
    partype = par.type_ and par.type_.__name__
    dct = {'name': name, 'type': partype, 'scalar': scalar, 'numeric': numeric,
           'datatype': get_datatype_name(datatype)}
    if (isinstance_m(par, ['GeneralReference']) and isinstance_m(par.ref, ['ObjectImport'])
       and callable(get_object_import(par.ref)) or not numeric):
        return lambda: typemap['Table']([dct]), tuple()
    assert numeric
    func, pars = par.func

    def retfunc(*args):
        try:
            val = func(*args)
            dct['dimensionality'] = str(get_dimensionality(val))
            dct['units'] = str(get_units(val))
        except TEXTX_WRAPPED_EXCEPTIONS:  # not covered
            pass
        return typemap['Table']([dct])
    return retfunc, pars


def quantity_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    if self.inp_value is None:
        url = self.url
        filename = self.filename
        type_ = self.type_
        return lambda: checktype_(load_value(url, filename), type_), tuple()
    numval = self.inp_value.value
    magnitude = numpy.nan if numval is None else numval
    pars = (magnitude, self.inp_units)
    return lambda: typemap['Quantity'](*pars), tuple()


def plain_type_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    if self.__value is None:
        url = self.url
        filename = self.filename
        type_ = self.type_
        return lambda: checktype_(load_value(url, filename), type_), tuple()
    val = self.__value  # evaluate here to allow serialization with dill
    return lambda: val, tuple()


def series_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    datatype = self.type_.datatype
    if self.name is None:
        url = self.url
        filename = self.filename
        type_ = self.type_
        return lambda: checktype_(load_value(url, filename), type_), tuple()
    name = self.name
    if datatype is not None and issubclass(datatype, numpy.ndarray):
        if all(is_numeric_type(e.type_) for e in self.elements):
            elements = (pandas.NA if e.value is None else e.value for e in self.elements)
            elements = [typemap['Quantity'](e, self.inp_units) for e in elements]
        else:
            elements = [e.value for e in self.elements]
        return lambda: typemap['Series'](data=elements, name=name), tuple()
    if datatype in (int, float, complex):
        elements = [e.value for e in self.elements]
        units = self.inp_units if self.inp_units else 'dimensionless'
        dtype = pint_pandas.PintType(units)
        return lambda: typemap['Series'](data=elements, dtype=dtype, name=name), tuple()
    tups = [e.func for e in self.elements]
    funs = [t[0] for t in tups]
    pars = [t[1] for t in tups]
    lens = [len(p) for p in pars]

    def get_series_val(*args):
        iargs = iter(args)
        fargs = [list(islice(iargs, pl)) for pl in lens]
        return typemap['Series']([f(*a) for f, a in zip(funs, fargs)], name=name)

    if datatype is not None and issubclass(datatype, typemap['Quantity']):
        def get_check_series_val(*args):
            ser = get_series_val(*args)
            if len(set(e.units for e in ser)) != 1:
                msg = 'Numeric type series must have elements of the same units.'
                raise InvalidUnitError(msg)
            return ser
        return get_check_series_val, tuple(chain.from_iterable(pars))
    return get_series_val, tuple(chain.from_iterable(pars))


def table_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    if self.url is not None or self.filename is not None:
        url = self.url
        filename = self.filename
        type_ = self.type_
        return lambda: checktype_(load_value(url, filename), type_), tuple()

    funcs = [c.func[0] for c in self.columns]
    pars = [c.func[1] for c in self.columns]
    pars_lens = [len(p) for p in pars]

    def get_table_val(*args):
        iargs = iter(args)
        fargs = [list(islice(iargs, pl)) for pl in pars_lens]
        series = [f(*a) for f, a in zip(funcs, fargs)]
        return typemap['Table'](pandas.concat(series, axis=1))
    return get_table_val, tuple(chain.from_iterable(pars))


def dict_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    funcs = [c.func[0] for c in self.values]
    pars = [c.func[1] for c in self.values]
    pars_lens = [len(p) for p in pars]
    keys = self.keys

    def get_dict_val(*args):
        iargs = iter(args)
        fargs = [list(islice(iargs, pl)) for pl in pars_lens]
        return dict(zip(keys, (f(*a) for f, a in zip(funcs, fargs))))
    return get_dict_val, tuple(chain.from_iterable(pars))


def tag_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    return self.tagtab.func


def alt_table_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    func, pars = dict_func(self) if self.keys and self.values else self.tab.func

    def get_alt_table_val(*args):
        data = func(*args)
        if isinstance(data, dict):
            return pandas.DataFrame.from_records([data])  # not covered
        return data
    return get_alt_table_val, pars


def bool_str_array_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    if self.url or self.filename:
        url = self.url
        filename = self.filename
        type_ = self.type_
        return lambda: checktype_(load_value(url, filename), type_), tuple()
    data = get_array_aslist(self.elements)
    return lambda: numpy.array(data), tuple()


def numeric_array_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    if self.url or self.filename:
        url = self.url
        filename = self.filename
        type_ = self.type_
        return lambda: checktype_(load_value(url, filename), type_), tuple()
    data = numpy.array(get_array_aslist(self.elements), dtype=self.type_.datatype)
    units = self.inp_units if self.inp_units else 'dimensionless'
    array = self.type_(data, units)
    return lambda: array, tuple()


def numeric_subarray_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    arr = numpy.array(get_array_aslist(self.elements), dtype=self.type_.datatype)
    return lambda: arr, tuple()


def get_general_reference_func(func, pars, accessor):
    """return a 2-tuple containing a function and a list of parameters"""
    if accessor.index is not None:
        acc_index = accessor.index

        def get_indexed(value):
            try:
                if isinstance(value, typemap['Table']):
                    dfr = value.iloc[[acc_index]]
                    return tuple(next(dfr.itertuples(index=False, name=None)))
                if isinstance(value, (tuple, list)):
                    return value[acc_index]
                if isinstance(value, typemap['Series']):
                    return value.values[acc_index]
                if is_array(value):
                    return value[acc_index]
                if isinstance(value, amml.AMMLObject):
                    return value[acc_index]
                raise TypeError(f'invalid type {type(value)}')  # not covered
            except IndexError as err:  # not covered
                msg = f'{str(err)}: index {acc_index}, length {len(value)}'
                raise SubscriptingError(msg) from err
        return lambda *x: get_indexed(func(*x)), pars
    acc_id = accessor.id

    def get_property(value):
        try:
            return value[acc_id]
        except KeyError as err:
            raise PropertyError(f'property "{acc_id}" not available') from err  # not covered
    return lambda *x: get_property(func(*x)), pars


def general_reference_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    func, pars = self.ref.func
    for accessor in self.accessors:
        func, pars = get_general_reference_func(func, pars, accessor)
    return func, pars


def iterable_property_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    func, pars = self.obj.func
    if hasattr(self, 'name_') and self.name_:
        return lambda *x: func(*x).name, pars
    if hasattr(self, 'columns') and self.columns:
        return lambda *x: func(*x).columns.to_series(name='columns'), pars
    slice_ = self.slice
    start_ = self.start
    stop_ = self.stop
    step_ = self.step
    array = self.array

    @settype
    def get_sliced_value(*args):
        value = func(*args)
        if slice_:
            value = value[start_:stop_:step_]
        if array:
            arr_val = value.values
            if isinstance(arr_val, pint_pandas.PintArray):
                return arr_val.quantity
            assert isinstance(arr_val, numpy.ndarray)
            if issubclass(arr_val.dtype.type, (numpy.str_, numpy.bool_)):
                return arr_val
            if isinstance(arr_val[0], str):
                return arr_val.astype(str)
            if is_array(arr_val[0]):
                return get_nested_array(arr_val)
            msg = 'array datatype must be numeric, boolean, string or array'
            raise RuntimeTypeError(msg)
        return value
    return get_sliced_value, pars


def iterable_query_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    func, pars = self.obj.func
    pars = list(pars)
    olens = len(pars)
    where = self.where
    where_all = self.where_all
    where_any = self.where_any
    column_names = self.columns
    if where:
        conds = [self.condition] if self.condition else self.conditions
        cfunc = [c.func[0] for c in conds]
        cpars = [c.func[1] for c in conds]
        clens = [len(p) for p in cpars]
        pars.extend(chain.from_iterable(cpars))
    else:
        cfunc = []
        clens = []

    def get_query_value(*args):
        iargs = iter(args)
        oargs = list(islice(iargs, olens))
        value = func(*oargs)
        if where:
            fargs = [list(islice(iargs, cl)) for cl in clens]
            fconds = [f(*a) for f, a in zip(cfunc, fargs)]
            if where_all:
                val = value[reduce(lambda x, y: x & y, fconds)]
            elif where_any:
                val = value[reduce(lambda x, y: x | y, fconds)]
            else:
                val = value[fconds[0]]
        else:
            val = value
        if column_names:
            val = val[column_names]
        return val.reset_index(drop=True)
    return get_query_value, tuple(pars)


def condition_in_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    qobj_ref = get_parent_of_type('IterableQuery', self).obj
    qobj_ref_func, cpars = qobj_ref.func
    column = self.column

    def cfunc(*args):
        val = qobj_ref_func(*args)
        if isinstance(val, typemap['Table']):
            return val[column]
        assert val.name == column
        return val

    cpars_len = len(cpars)
    if self.parameter:  # not covered
        pfunc, ppars = self.parameter.func
        return lambda *x: cfunc(*x[:cpars_len]).isin(pfunc(*x[cpars_len:])), (*cpars, *ppars)
    pfunc = [p.func[0] for p in self.params]
    ppars = tuple(p.func[1] for p in self.params)
    ppars_lens = [len(p) for p in ppars]

    def retfunc_pars(*args):
        iargs = iter(args)
        cargs = list(islice(iargs, cpars_len))
        pargs = [list(islice(iargs, pl)) for pl in ppars_lens]
        return cfunc(*cargs).isin([f(*a) for f, a in zip(pfunc, pargs)])
    return retfunc_pars, tuple(chain.from_iterable((cpars,)+ppars))


def condition_comparison_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    assert self.operand_left is None
    assert self.column_left is not None
    operator = binop_map[self.operator]
    qobj_ref = get_parent_of_type('IterableQuery', self).obj
    qobj_func, qobj_pars = qobj_ref.func
    qobj_parlen = len(qobj_pars)
    cleft, cright = self.column_left, self.column_right

    def operand_type_check(left, right):
        if len(left):
            right0 = right[0] if isinstance(right, pandas.Series) else right
            try:
                operator(left[0], right0)
            except (TypeError, ValueError) as err:
                msg = f'invalid comparison of types {type(left[0])} and {type(right0)}'
                raise RuntimeTypeError(msg) from err
            return operator(left, right)
        return pandas.Series(dtype=bool)  # not covered

    assert qobj_ref.type_ is not None
    if is_table_like_type(qobj_ref.type_):
        if cright:

            def table_column_right(*args):
                val = qobj_func(*args)
                return operand_type_check(val[cleft], val[cright])
            return table_column_right, qobj_pars

        assert self.operand_right
        opr_func, opr_pars = self.operand_right.func

        def table_operand_right(*args):
            val = qobj_func(*args[0:qobj_parlen])
            return operand_type_check(val[cleft], opr_func(*args[qobj_parlen:]))
        return table_operand_right, (*qobj_pars, *opr_pars)

    assert issubclass(qobj_ref.type_, typemap['Series'])
    if self.operand_right:
        opr_func, opr_pars = self.operand_right.func

        def series_operand_right(*args):
            val = qobj_func(*args[0:qobj_parlen])
            if val.name != cleft:
                msg = f'column name must be "{val.name}" but is "{cleft}"'
                raise RuntimeValueError(msg)
            return operand_type_check(val, opr_func(*args[qobj_parlen:]))
        return series_operand_right, (*qobj_pars, *opr_pars)

    assert cright

    def series_column_right(*args):
        val = qobj_func(*args)
        msg = f'column name must be "{val.name}" but is '
        if val.name != cleft:
            raise RuntimeValueError(msg+f'"{cleft}"')
        if val.name != cright:  # not covered
            raise RuntimeValueError(msg+f'"{cright}"')
        return operand_type_check(val, val)  # not covered
    return series_column_right, qobj_pars


def range_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    tup = (self.start, self.stop, self.step)
    tups = [t.func for t in tup]
    funcs = [t[0] for t in tups]
    pars = [t[1] for t in tups]
    lens = [len(t[1]) for t in tups]
    name = self.parent.name if hasattr(self.parent, 'name') else 'range'

    def get_range_val(*args):
        iargs = iter(args)
        fargs = [list(islice(iargs, pl)) for pl in lens]
        cargs = [f(*a) for f, a in zip(funcs, fargs)]
        unit = cargs[0].units
        data = numpy.arange(cargs[0].magnitude, cargs[1].to(unit).magnitude,
                            cargs[2].to(unit).magnitude).tolist()
        dtype = pint_pandas.PintType(unit)
        return typemap['Series'](data=data, name=name, dtype=dtype)
    return get_range_val, tuple(chain.from_iterable(pars))


def map_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    name = self.parent.name if hasattr(self.parent, 'name') else 'map'
    func_def = self.lambda_ if self.lambda_ else self.function
    if not isinstance_m(func_def, ['ObjectImport']):
        nfunc, npars = dummies_right(*func_def.expr.func)
        func_args = func_def.args
    else:
        nfunc = get_object_import(self.function)
        dummy = get_metamodel(self)['Dummy']
        dummy.name = None
        npars = (dummy,)*len(self.params)
        func_args = npars
    func_pars = [p.func for p in self.params]
    plen = sum(not isinstance_m(p, ['Dummy']) for p in npars)
    dummy_funcs = []
    dummy_pars_lens = []
    all_pars = [npars[:plen]]
    for par in npars[plen:]:
        ind = next(i for i, a in enumerate(func_args) if a.name == par.name)
        dummy_funcs.append(func_pars[ind][0])
        all_pars.append(func_pars[ind][1])
        dummy_pars_lens.append(len(func_pars[ind][1]))

    def get_map_val(*args):
        iargs = iter(args)
        pargs = list(islice(iargs, plen))
        dargs = [list(islice(iargs, pl)) for pl in dummy_pars_lens]
        iterables = [f(*a) for f, a in zip(dummy_funcs, dargs)]
        for index, val in enumerate(iterables):
            if is_table_like(val):
                iterables[index] = (dict(p) for _, p in val.iterrows())
        data = list(map(partial(nfunc, *pargs), *iterables))
        if data and all(isinstance(v, dict) for v in data):
            return typemap['Table'].from_records(data)
        if data and all(isinstance(v, typemap['Quantity']) for v in data):
            assert all(is_scalar(e.magnitude) or pandas.isna(e.magnitude) for e in data)
            dtype = pint_pandas.PintType(next(iter(data)).units)
            data = (v.magnitude for v in data)
            return typemap['Series'](name=name, data=data, dtype=dtype)
        return typemap['Series'](data=data, name=name)
    return get_map_val, tuple(chain.from_iterable(all_pars))


def filter_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    name = self.parent.name if hasattr(self.parent, 'name') else 'filter'
    func_def = self.lambda_ if self.lambda_ else self.function
    if not isinstance_m(func_def, ['ObjectImport']):
        nfunc, npars = dummies_right(*func_def.expr.func)
    else:
        nfunc = get_object_import(self.function)
        npars = (get_metamodel(self)['Dummy'],)
    pfun, pars = self.parameter.func
    plen = sum(not isinstance_m(p, ['Dummy']) for p in npars)
    all_pars = npars[:plen] + pars
    dlen = len(npars[plen:])

    def get_filter_val(*args):
        filter_f = partial(lambda *x: nfunc(*x[:plen], *x[plen:]*dlen), *args[:plen])
        filter_d = pfun(*args[plen:]).dropna()  # alt: lambda *x: not(pandas.isna(filter_f(*x)))
        if isinstance(filter_d, typemap['Series']):
            return typemap['Series'](filter(filter_f, filter_d), name=name)
        assert is_table_like(filter_d)
        mask = (filter_f(dict(p)) for _, p in filter_d.iterrows())
        return filter_d[typemap['Series'](mask)]
    return get_filter_val, all_pars


def reduce_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    func_def = self.lambda_ if self.lambda_ else self.function
    pfun, pars = self.parameter.func
    if isinstance_m(func_def, ['ObjectImport']):
        nfunc = get_object_import(self.function)
        return lambda *x: reduce(nfunc, pfun(*x)), pars
    nfunc, npars = dummies_right(*func_def.expr.func)
    plen = sum(not isinstance_m(p, ['Dummy']) for p in npars)
    npars_u = npars[:plen] + tuple(func_def.args)
    mapping = [next(i for i, a in enumerate(npars_u) if a.name == p.name) for p in npars]

    def nfunc_u(*args):
        return partial(lambda *x: nfunc(*[x[i] for i in mapping]), *args)
    apars = npars[:plen] + pars

    def get_reduce_val(*args):
        pval = pfun(*args[plen:])
        if isinstance(pval, typemap['Series']):
            return reduce(nfunc_u(*args[:plen]), pval)
        pval = (dict(r) for _, r in pval.iterrows())
        return typemap['Table'].from_records([reduce(nfunc_u(*args[:plen]), pval)])
    return get_reduce_val, apars


def sum_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    if self.parameter:
        pfun, pars = self.parameter.func
        return lambda *x: sum(pfun(*x)), pars
    tuples = [p.func for p in self.params]
    funcs = [t[0] for t in tuples]
    pars = [t[1] for t in tuples]
    pars_lens = [len(p) for p in pars]

    def get_func_reduce_val(*args):
        iargs = iter(args)
        fargs = [list(islice(iargs, pl)) for pl in pars_lens]
        return sum(f(*a) for f, a in zip(funcs, fargs))
    return get_func_reduce_val, tuple(chain.from_iterable(pars))


def any_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    if self.parameter:
        func, pars = self.parameter.func

        def get_any_val_parameter(*args):
            null = False
            for operand in func(*args):
                if operand:
                    return True
                if operand is None:
                    null = True
            return False if not null else None
        return get_any_val_parameter, pars

    tuples = [p.func for p in self.params]
    funcs = [t[0] for t in tuples]
    pars = [t[1] for t in tuples]
    pars_lens = [len(p) for p in pars]

    def get_any_val_params(*args):
        null = False
        iargs = iter(args)
        fargs = [list(islice(iargs, pl)) for pl in pars_lens]
        for fnc, arg in zip(funcs, fargs):
            operand = fnc(*arg)
            if operand:
                return True
            if operand is None:
                null = True
        return False if not null else None
    return get_any_val_params, tuple(chain.from_iterable(pars))


def all_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    if self.parameter:
        func, pars = self.parameter.func

        def get_all_val_parameter(*args):
            null = False
            for operand in func(*args):
                if operand is None:
                    null = True
                elif not operand:
                    return False
            return True if not null else None
        return get_all_val_parameter, pars

    tuples = [p.func for p in self.params]
    funcs = [t[0] for t in tuples]
    pars = [t[1] for t in tuples]
    pars_lens = [len(p) for p in pars]

    def get_all_val_params(*args):
        null = False
        iargs = iter(args)
        fargs = [list(islice(iargs, pl)) for pl in pars_lens]
        for fnc, arg in zip(funcs, fargs):
            operand = fnc(*arg)
            if operand is None:
                null = True
            elif not operand:
                return False
        return True if not null else None
    return get_all_val_params, tuple(chain.from_iterable(pars))


def in_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    if self.parameter:
        func_x, pars_x = self.element.func
        func_y, pars_y = self.parameter.func
        len_x = len(pars_x)

        def get_in_val_parameter(*args):
            array = func_y(*args[len_x:]).values
            if func_x(*args[:len_x]) in array:
                return True
            if None in array or any(array.isna()):
                return None
            return False
        return get_in_val_parameter, (*pars_x, *pars_y)

    elem_func, elem_pars = self.element.func
    elem_pars_len = len(elem_pars)
    func_pars = [p.func for p in self.params]
    funcs = [t[0] for t in func_pars]
    pars = tuple(t[1] for t in func_pars)
    pars_lens = [len(p) for p in pars]

    def get_in_val_params(*args):
        null = False
        iargs = iter(args)
        elem_value = elem_func(*islice(iargs, elem_pars_len))
        for fnc, arg in zip(funcs, (list(islice(iargs, p)) for p in pars_lens)):
            param_value = fnc(*arg)
            if elem_value == param_value:
                return True
            if (param_value is None or isinstance(param_value, typemap['Quantity'])
               and numpy.isnan(param_value)):
                null = True
        return None if null else False
    return get_in_val_params, tuple(chain.from_iterable(elem_pars+pars))


def binop_func(func, ops, from_the_left=True):
    """binary operator as a 2-tuple with a function and parameters"""
    if len(ops) == 0:
        return func
    operator, operand = ops.pop(0) if from_the_left else ops.pop(-1)
    left_func, left_pars = func if from_the_left else operand.func
    right_func, right_pars = operand.func if from_the_left else func
    pars = left_pars + right_pars
    operator = binop_map[operator]
    left_pars_length = len(left_pars)

    def newfunc(*args):
        return operator(left_func(*args[0:left_pars_length]),
                        right_func(*args[left_pars_length:]))
    return binop_func((newfunc, pars), ops, from_the_left=from_the_left)


def expression_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    func = self.operands[0].func
    ops = list(zip(self.operators, self.operands[1:]))
    return binop_func(func, ops)


def term_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    func = self.operands[0].func
    ops = list(zip(self.operators, self.operands[1:]))
    return binop_func(func, ops)


def factor_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    func = self.operands[-1].func
    operators = ['**']*(len(self.operands)-1)
    ops = list(zip(operators, self.operands[:-1]))
    return binop_func(func, ops, from_the_left=False)


def power_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    func, pars = self.operand.func
    if self.sign == '-':
        return lambda *args: -func(*args), pars
    return func, pars


def binary_operation_func(self, operator):
    """return a 2-tuple containing a function and a list of parameters"""
    func = self.operands[0].func
    ops = list(zip([operator]*len(self.operands[1:]), self.operands[1:]))
    return binop_func(func, ops)


def or_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    funcs = [op.func[0] for op in self.operands]
    pars = [op.func[1] for op in self.operands]
    plens = [len(p) for p in pars]

    def get_or_val(*args):
        nc = False
        null = False
        iter_args = iter(args)
        for func, plen in zip(funcs, plens):
            op_val = func(*list(islice(iter_args, plen)))
            if op_val is NC:
                nc = True
            elif op_val is None:
                null = True
            elif op_val:
                return True
        if nc:
            return NC
        if null:
            return None
        return False
    return get_or_val, tuple(chain.from_iterable(pars))


def and_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    funcs = [op.func[0] for op in self.operands]
    pars = [op.func[1] for op in self.operands]
    plens = [len(p) for p in pars]

    def get_and_val(*args):
        nc = False
        null = False
        iter_args = iter(args)
        for func, plen in zip(funcs, plens):
            op_val = func(*list(islice(iter_args, plen)))
            if op_val is NC:
                nc = True
            elif op_val is None:
                null = True
            elif not op_val:
                return False
        if null:
            return None
        if nc:
            return NC
        return True
    return get_and_val, tuple(chain.from_iterable(pars))


def not_func(self, operator):
    """return a 2-tuple containing a function and a list of parameters"""
    if self.not_:
        func, pars = self.operand.func

        def get_not_func(*args):
            val = func(*args)
            if val is NC:
                return NC
            if val is None:
                return None
            return operator(val)
        return get_not_func, pars
    return self.operand.func


def comparison_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    lfunc, lpars = self.left.func
    rfunc, rpars = self.right.func
    all_pars = (*lpars, *rpars)
    lparslen = len(lpars)
    operator = self.operator

    def get_comparison_val(*args):
        lval = lfunc(*args[:lparslen])
        rval = rfunc(*args[lparslen:])
        for operand in (lval, rval):
            if isinstance(operand, typemap['Quantity']):
                if operand.magnitude is pandas.NA:
                    return None
                assert isinstance(operand.magnitude, ScalarNumerical)
                if isinstance(operand.magnitude, complex):
                    assert operator in ('==', '!=')
            else:
                assert isinstance(operand, (bool, str))
                assert operator in ('==', '!=')
        return bool(binop_map[operator](lval, rval))
    return get_comparison_val, all_pars


def real_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    func, pars = self.parameter.func
    return lambda *args: func(*args).real, pars


def imag_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    func, pars = self.parameter.func
    return lambda *args: func(*args).imag, pars


def if_expression_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    expr_func, expr_pars = self.expr.func
    expr_pars_len = len(expr_pars)
    true_b, true_b_pars = self.true_.func
    true_b_pars_len = expr_pars_len + len(true_b_pars)
    false_b, false_b_pars = self.false_.func

    def iffunc(*args):
        expr_val = expr_func(*args[:expr_pars_len])
        if expr_val is NC:
            return NC
        if expr_val:
            return true_b(*args[expr_pars_len:true_b_pars_len])
        return false_b(*args[true_b_pars_len:])
    return iffunc, (*expr_pars, *true_b_pars, *false_b_pars)


def function_call_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    if isinstance_m(self.function, ['ObjectImport']):
        obj = get_object_import(self.function)
        assert callable(obj)
        func_pars = [p.func for p in self.params]
        pars = [pars for func, pars in func_pars]
        funcs = [func for func, pars in func_pars]
        lens = list(map(len, pars))
        pars_flat = tuple(p for par in pars for p in par)

        def fcall_func(*args):
            iter_args = iter(args)
            fcall_args = [list(islice(iter_args, i)) for i in lens]
            try:
                return obj(*[f(*a) for f, a in zip(funcs, fcall_args)])
            except PintError as err:
                raise err
            except TypeError as err:
                raise RuntimeTypeError(str(err)) from err
        return settype(fcall_func), pars_flat
    assert isinstance_m(self.function, ['FunctionDefinition'])
    if not get_parent_of_type('FunctionDefinition', self):
        return self.expr.func
    # function call in a function definition, e.g. f(x) = 2*g(x)
    return None  # not covered


def object_import_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    obj = get_object_import(self)
    if callable(obj):
        raise RuntimeTypeError(f'callable import {obj} has no value')
    return settype(lambda: obj), tuple()


def tuple_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    tuple_pars = [p.func for p in self.params]
    tpars = [pars for func, pars in tuple_pars]
    funcs = [func for func, pars in tuple_pars]
    tlens = [len(pars) for func, pars in tuple_pars]

    def get_tuple_val(*args):
        iter_args = iter(args)
        targs = [list(islice(iter_args, t)) for t in tlens]
        return tuple(f(*a) for f, a in zip(funcs, targs))
    return get_tuple_val, tuple(chain.from_iterable(tpars))


def amml_structure_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    if self.filename or self.url:
        url = self.url
        type_ = self.type_
        filename = self.filename
        suffix = pathlib.Path(filename).suffix
        if filename and suffix not in ['.yml', '.yaml', '.json']:
            return lambda: amml.AMMLStructure.from_ase_file(filename), tuple()
        return lambda: checktype_(load_value(url, filename), type_), tuple()
    func, pars = self.tab.func
    name = self.name
    return lambda *x: amml.AMMLStructure(func(*x), name), pars


def amml_calculator_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    name = self.name
    pinning = self.pinning
    version = self.version
    task = self.task
    if self.parameters is None:
        return (lambda: amml.Calculator(name, typemap['Table'](), pinning, version,
                                        task), tuple())
    func, pars = self.parameters.func
    return lambda *x: amml.Calculator(name, func(*x), pinning, version, task), pars


def amml_algorithm_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    name = self.name
    m2o = self.many_to_one
    if self.parameters is None:
        return lambda: amml.Algorithm(name, typemap['Table'](), m2o), tuple()
    func, pars = self.parameters.func
    return lambda *x: amml.Algorithm(name, func(*x), m2o), pars


def amml_property_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    sfunc, spars = self.struct.func
    cfunc, cpars = self.calc.func if self.calc else (lambda: None, tuple())
    afunc, apars = self.algo.func if self.algo else (lambda: None, tuple())
    props = self.names
    cpl = len(cpars)
    spl = len(spars)
    apl = len(apars)
    constr_tuples = [c.func for c in self.constrs]
    constr_func = [f for f, p in constr_tuples]
    constr_pars = [p for f, p in constr_tuples]
    constr_pars_lens = [len(p) for p in constr_pars]
    pars = (spars, cpars, apars, *constr_pars)

    def get_property_val(*args):
        iargs = iter(args)
        struct_args = list(islice(iargs, spl))
        calc_args = list(islice(iargs, cpl))
        algo_args = list(islice(iargs, apl))
        constr_args = [list(islice(iargs, pl)) for pl in constr_pars_lens]
        constrs = [f(*x) for f, x in zip(constr_func, constr_args)]
        return amml.Property(props, sfunc(*struct_args), calculator=cfunc(*calc_args),
                             algorithm=afunc(*algo_args), constraints=constrs)
    return get_property_val, tuple(chain.from_iterable(pars))


def amml_constraint_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    name = self.name
    fixed_func, fixed_pars = self.fixed.func
    if self.direction is None:
        return lambda *x: amml.Constraint(name, fixed=fixed_func(*x)), fixed_pars
    fpl = len(fixed_pars)
    direc_func, direc_pars = self.direction.func
    pars = (*fixed_pars, *direc_pars)
    return (lambda *x: amml.Constraint(name, fixed=fixed_func(*x[:fpl]),
                                       direction=direc_func(*x[fpl:])), pars)


def chem_reaction_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    species = [term.species.func for term in self.educts+self.products]
    func_spec = [t[0] for t in species]
    pars_spec = tuple(t[1] for t in species)
    pars_lens = [len(p) for p in pars_spec]
    coeffs = []
    for term in self.educts:
        coeffs.append(-term.coefficient)
    for term in self.products:
        coeffs.append(term.coefficient)

    if self.props is None:
        props_avail = False
        func_props = None
        pars_all = tuple(chain.from_iterable(pars_spec))
    else:
        props_avail = True
        func_props, pars_props = self.props.func
        pars_all = tuple(chain.from_iterable(pars_spec)) + pars_props

    def get_chem_reaction(*args):
        iargs = iter(args)
        pargs = [list(islice(iargs, pl)) for pl in pars_lens]
        specs = [f(*a) for f, a in zip(func_spec, pargs)]
        terms = [{'coefficient': c, 'species': s} for c, s in zip(coeffs, specs)]
        props = func_props(*list(iargs)) if props_avail else None
        return chemistry.ChemReaction(terms, props)
    return get_chem_reaction, pars_all


def chem_species_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    name = self.name
    none_func = (lambda: None, tuple())
    comp_f, comp_p = self.composition.func if self.composition else none_func
    props_f, props_p = self.props.func if self.props else none_func
    comp_plen = len(comp_p)
    return (lambda *x: chemistry.ChemSpecies(name, comp_f(*x[:comp_plen]),
                                             props_f(*x[comp_plen:])),
            tuple(chain.from_iterable((comp_p, props_p))))


def add_func_properties(metamodel):
    """Add class properties using monkey style patching"""
    nc_strict_funcs = {  # functions that return NC if an NC is passed
        'String': plain_type_func,
        'Bool': plain_type_func,
        'Quantity': quantity_func,
        'Power': power_func,
        'Factor': factor_func,
        'Term': term_func,
        'Expression': expression_func,
        'Operand': lambda x: x.operand.func,
        'Comparison': comparison_func,
        'Real': real_func,
        'Imag': imag_func,
        'FunctionCall': function_call_func,
        'Lambda': lambda x: x.expr.func,
        'FunctionDefinition': lambda x: x.expr.func,
        'ObjectImport': object_import_func,
        'Series': series_func,
        'Table': table_func,
        'Dict': dict_func,
        'AltTable': alt_table_func,
        'Tag': tag_func,
        'BoolArray': bool_str_array_func,
        'StrArray': bool_str_array_func,
        'IntArray': numeric_array_func,
        'FloatArray': numeric_array_func,
        'ComplexArray': numeric_array_func,
        'IntSubArray': numeric_subarray_func,
        'FloatSubArray': numeric_subarray_func,
        'ComplexSubArray': numeric_subarray_func,
        'IterableProperty': iterable_property_func,
        'IterableQuery': iterable_query_func,
        'ConditionIn': condition_in_func,
        'ConditionComparison': condition_comparison_func,
        'ConditionOr': partial(binary_operation_func, operator='or_'),
        'ConditionAnd': partial(binary_operation_func, operator='and_'),
        'Range': range_func,
        'In': in_func,
        'Any': any_func,
        'All': all_func,
        'Sum': sum_func,
        'Map': map_func,
        'Filter': filter_func,
        'Reduce': reduce_func,
        'AMMLStructure': amml_structure_func,
        'AMMLCalculator': amml_calculator_func,
        'AMMLAlgorithm': amml_algorithm_func,
        'AMMLProperty': amml_property_func,
        'AMMLConstraint': amml_constraint_func,
        'ChemReaction': chem_reaction_func,
        'ChemSpecies': chem_species_func
    }
    nc_safe_funcs = {  # functions that can process nc values
        'Print': print_func,
        'PrintParameter': print_parameter_func,
        'Type': type_func,
        'Dummy': lambda obj: (lambda x: x, (obj,)),
        'GeneralReference': general_reference_func,
        'Tuple': tuple_func,
        'IfFunction': if_expression_func,
        'IfExpression': if_expression_func,
        'BooleanOperand': lambda x: x.operand.func,
        'And': and_func,
        'Or': or_func,
        'Not': partial(not_func, operator=not_),
        'ConditionNot': partial(not_func, operator=invert),
    }
    for key, function in nc_strict_funcs.items():
        metamodel[key].func = cached_property(log_eval(strict_nc(function)))
        metamodel[key].func.__set_name__(metamodel[key], 'func')
    for key, function in nc_safe_funcs.items():
        metamodel[key].func = cached_property(log_eval(function))
        metamodel[key].func.__set_name__(metamodel[key], 'func')
    metamodel['Variable'].func = cached_property(cache_eval(log_eval(lambda x: x.parameter.func)))
    metamodel['Variable'].func.__set_name__(metamodel['Variable'], 'func')


def add_deferred_value_properties(metamodel):
    """Add class properties using monkey style patching"""
    metamodel_classes = [
      'String', 'Bool', 'Quantity', 'PrintParameter', 'Type',
      'Variable', 'Power', 'Factor', 'Term', 'Expression', 'Operand', 'BooleanOperand',
      'And', 'Or', 'Not', 'Comparison', 'IfFunction', 'IfExpression', 'FunctionCall',
      'ObjectImport', 'Tuple', 'Series', 'Table', 'BoolArray', 'StrArray', 'IntArray',
      'FloatArray', 'ComplexArray', 'IntSubArray', 'FloatSubArray', 'ComplexSubArray',
      'IterableProperty', 'IterableQuery', 'ConditionIn', 'ConditionComparison',
      'ConditionOr', 'ConditionAnd', 'ConditionNot', 'Range', 'In', 'Any', 'All', 'Sum',
      'Map', 'Filter', 'Reduce', 'AMMLStructure', 'AMMLCalculator', 'AMMLAlgorithm',
      'AMMLProperty', 'AMMLConstraint', 'ChemReaction', 'ChemSpecies'
    ]
    for cls in metamodel_classes:
        metamodel[cls].value = cached_property(textxerror_wrap(func_value))
        metamodel[cls].value.__set_name__(metamodel[cls], 'value')
    metamodel['Program'].value = cached_property(textxerror_wrap(program_value))
    metamodel['Program'].value.__set_name__(metamodel['Program'], 'value')
    metamodel['Print'].value = cached_property(error_handler(textxerror_wrap(func_value)))
    metamodel['Print'].value.__set_name__(metamodel['Print'], 'value')
