"""helper functions for formatting the output of print statements"""
import re
import numpy
import pandas
import pint
import pint_pandas
from virtmat.language.utilities import amml, chemistry
from virtmat.language.utilities.types import ScalarReal, ScalarNumerical, NC

pint_pandas.pint_array.DEFAULT_SUBDTYPE = None


def formatter_pint(magnitude, unit):
    """format a pint quantity value"""
    magnitude_str = magnitude.replace('nan', 'null')
    if str(unit) in ['dimensionless', '']:
        return magnitude_str
    return f'{magnitude_str} [{unit}]'


def formatter_numeric(magnitude):
    """format a scalar numeric value"""
    if isinstance(magnitude, ScalarReal):
        if numpy.isnan(magnitude):
            return 'null'
        return str(magnitude)
    if isinstance(magnitude, numpy.ndarray):
        return formatter_array(magnitude)
    if isinstance(magnitude, type(pandas.NA)):
        return 'null'
    assert isinstance(magnitude, complex)
    sign = '+' if magnitude.imag >= 0 else ''
    return str(magnitude.real)+sign+str(magnitude.imag)+' j'


def formatter_scalar(val):
    """format a scalar value"""
    if hasattr(val, 'units'):
        ret = formatter_pint(formatter_numeric(val.magnitude), val.units)
    elif isinstance(val, bool):
        ret = 'true' if val else 'false'
    elif isinstance(val, ScalarNumerical):
        ret = formatter_numeric(val)
    elif val is NC:
        ret = repr(val)
    elif isinstance(val, str):
        ret = f'\'{val}\''
    elif val is None:
        ret = 'null'
    else:
        ret = str(val)
    return ret


def formatter_series(val):
    """format a series value"""
    name = val.name if re.match(r'^[^\d\W]\w*$', str(val.name)) else f'\'{val.name}\''
    if len(val) == 0:
        if isinstance(val.dtype, pint_pandas.PintType):
            return formatter_pint(f'({name}:)', val.dtype.units)
        return f'({name}:)'
    if hasattr(val.values[0], 'magnitude'):
        if isinstance(val.dtype, pint_pandas.PintType):
            unit = val.dtype.units
            values = ', '.join(formatter_numeric(v.magnitude) for v in val)
        elif val.dtype == 'object':
            units = set(v.units for v in val)
            assert len(units) == 1
            unit = next(iter(units))
            if isinstance(val.values[0].magnitude, numpy.ndarray):
                values = ', '.join(formatter_array(v.magnitude) for v in val)
            else:
                values = ', '.join(formatter_numeric(v.magnitude) for v in val)
        else:
            raise RuntimeError(f'unsupported dtype: {val.dtype}')
        values = values.replace('nan', 'null')
        ret = formatter_pint(f'({name}: {values})', unit)
    else:
        values = ', '.join(formatter(e) for e in val)
        ret = f'({name}: {values})'
    return ret


def formatter_array(val):
    """format an array val; if the array is numeric then val is the magnitude"""
    def recursive_formatter(val_):
        out = []
        for elem in val_:
            if isinstance(elem, (tuple, list)):
                out.append(f'[{recursive_formatter(elem)}]')
            else:
                elem = elem.magnitude if isinstance(elem, pint.Quantity) else elem
                out.append(formatter_scalar(elem))
        return ', '.join(out)
    val_lst = val.tolist()
    if not isinstance(val_lst, list):
        return formatter(val_lst)
    return f'[{recursive_formatter(val_lst)}]'


def formatter(val):
    """format an arbitrary type value"""
    if isinstance(val, pandas.Series):
        ret = formatter_series(val)
    elif isinstance(val, pandas.DataFrame):
        values = ', '.join(formatter_series(val[s]) for s in val.columns)
        ret = f'({values})'
    elif isinstance(val, numpy.ndarray):
        ret = formatter_array(val)
    elif isinstance(val, pint.Quantity) and isinstance(val.magnitude, numpy.ndarray):
        ret = formatter_pint(formatter_array(val.magnitude), val.units)
    elif isinstance(val, (tuple, list)):
        fval = ', '.join(formatter(el) for el in val)
        if len(val) == 1:
            fval += ','
        ret = f'({fval})'
    elif isinstance(val, dict):
        ret = '{' + ', '.join(f'{k}: {formatter(v)}' for k, v in val.items()) + '}'
    elif isinstance(val, amml.AMMLObject):
        ret = formatter_amml_object(val)
    elif isinstance(val, chemistry.ChemBase):
        ret = formatter_chem_object(val)
    else:
        ret = formatter_scalar(val)
    return ret


def formatter_amml_object(val):
    """format an AMML object"""
    if isinstance(val, amml.Calculator):
        ret = formatter_amml_calculator(val)
    elif isinstance(val, amml.Algorithm):
        ret = formatter_amml_algorithm(val)
    elif isinstance(val, amml.AMMLStructure):
        ret = formatter_amml_structure(val)
    elif isinstance(val, amml.Property):
        ret = formatter_amml_property(val)
    elif isinstance(val, amml.Constraint):
        ret = formatter_amml_constraint(val)
    else:
        assert isinstance(val, amml.Trajectory)
        ret = formatter_amml_trajectory(val)
    return ret


def formatter_amml_structure(val):
    """format an AMML Structure object"""
    outp_str = 'Structure'
    if val.name:
        outp_str += f' {val.name}'
    outp_str += f' {formatter(val.tab)}'
    return outp_str


def formatter_amml_calculator(val):
    """format an AMML Calculator object"""
    tab_str = formatter(val.parameters)
    name_ver = val.name
    task_str = f', task: {val.task}' if val.task else ''
    if val.pinning and val.version:
        name_ver += f' {val.pinning} {val.version}'
    return f'Calculator {name_ver} {tab_str}{task_str}'


def formatter_amml_algorithm(val):
    """format an AMML Algorithm object"""
    return f'Algorithm {val.name} {formatter(val.parameters)}'


def formatter_amml_property(val):
    """format an AMML Property object"""
    names = ', '.join(val.names)
    struct = formatter(val.structure)
    calc = formatter(val.calculator)
    algo = formatter(val.algorithm)
    constrs = formatter(val.constraints)
    return (f'Property {names} ((structure: {struct}), (calculator: {calc}), '
            f'(algorithm: {algo}), (constraints: {constrs}))')


def formatter_amml_constraint(val):
    """format an AMML Constraint object"""
    fixed = formatter(val.fixed)
    if val.name == 'FixedPlane':
        return f'FixedPlane normal to {formatter(val.direction)} where {fixed}'
    if val.name == 'FixedLine':
        return f'FixedLine collinear to {formatter(val.direction)} where {fixed}'
    if val.name == 'FixScaled':
        return f'FixScaled along cell vectors {formatter(val.mask)} where {fixed}'
    return f'FixedAtoms where {fixed}'


def formatter_amml_trajectory(val):
    """format an AMML Trajectory object"""
    attrs = ('description', 'structure', 'properties', 'constraints', 'filename')
    elems = [f'{attr}: {formatter(getattr(val, attr))}' for attr in attrs]
    return 'Trajectory(' + ', '.join(elems) + ')'


def formatter_chem_object(val):
    """format a chemistry object"""
    if isinstance(val, chemistry.ChemReaction):
        ret = formatter_chem_reaction(val)
    else:
        assert isinstance(val, chemistry.ChemSpecies)
        ret = formatter_chem_species(val)
    return ret


def formatter_chem_reaction(val):
    """format a chemical reaction object"""
    eterms = [term for term in val.terms if term['coefficient'] < 0]
    pterms = [term for term in val.terms if term['coefficient'] > 0]
    educts = [' '.join([str(-t['coefficient']), t['species'].name]) for t in eterms]
    products = [' '.join([str(t['coefficient']), t['species'].name]) for t in pterms]
    lhs = ' + '.join(educts)
    rhs = ' + '.join(products)
    outp_str = f'Reaction {lhs} = {rhs}'
    if len(val.props) > 0:
        outp_str += f' : {formatter(val.props)}'
    return outp_str


def formatter_chem_species(val):
    """format a chemical species object"""
    outp_str = f'Species {val.name}'
    if getattr(val, 'composition', None):
        outp_str += f', composition: \'{val.composition}\''
    if len(val.props) > 0:
        outp_str += f' {formatter(val.props)}'
    return outp_str
