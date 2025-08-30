"""Custom classes for the chemistry objects"""
from copy import deepcopy
import numpy
import pandas
import pint_pandas
from ase.formula import Formula
from virtmat.language.utilities.units import ureg
from virtmat.language.utilities.errors import RuntimeValueError
from virtmat.language.utilities.warnings import warnings, TextSUserWarning

pint_pandas.pint_array.DEFAULT_SUBDTYPE = None


def is_equation_balanced(lcomps, lcoeff, rcomps, rcoeff):
    """check equation balance using provided a list of compositions and coefficients"""
    totals = {}
    for side, pre in zip((zip(lcomps, lcoeff), zip(rcomps, rcoeff)), (-1, 1)):
        for comp, coeff in side:
            # for key, val in chemparse.parse_formula(comp).items():
            for key, val in Formula(comp).count().items():
                if key not in totals:
                    totals[key] = pre * coeff * val
                else:
                    totals[key] = totals[key] + pre * coeff * val
    return all(numpy.isclose(v, 0) for v in totals.values())


class ChemBase:
    """base class of all chemistry objects"""
    props_list = ['energy', 'enthalpy', 'entropy', 'free_energy', 'zpe', 'temperature']
    units_list = ['eV', 'eV', 'eV/K', 'eV', 'eV', 'K']
    prop_units = dict(zip(props_list, units_list))

    def __init__(self, props=None):
        self.props = props if props is not None else pandas.DataFrame()

    def __getitem__(self, key):
        if isinstance(key, str):
            if key == 'properties':
                return self.props
            if key in self.props:
                return self.props[key]
            if key in self.props_list:
                dtype = pint_pandas.PintType(self.prop_units[key])
                return pandas.Series(numpy.nan, dtype=dtype, name=key)
        if isinstance(key, int):
            dfr = self.props.iloc[[key]]
            return tuple(next(dfr.itertuples(index=False, name=None)))
        if (isinstance(key, slice) or
           (isinstance(key, pandas.Series) and key.dtype is numpy.dtype(bool)) or
           (isinstance(key, (list, tuple)) and all(isinstance(s, str) for s in key))):
            obj = deepcopy(self)
            obj.props = obj.props[key]
            return obj
        raise TypeError('unknown key type')

    def reset_index(self, *args, **kwargs):
        """resets the index of properties table"""
        inplace = kwargs.get('inplace')
        kwargs['inplace'] = True
        self.props.reset_index(*args, **kwargs)
        if inplace:
            return None
        return self

    def dropna(self):
        """drop non-defined values from props dataframe"""
        obj = deepcopy(self)
        obj.props.dropna(inplace=True)
        return obj

    def iterrows(self):
        """return an iterator over props dataframe rows"""
        return self.props.iterrows()


class ChemReaction(ChemBase):
    """"custom chemical reaction class"""

    def __init__(self, terms, props=None):
        self.terms = terms
        super().__init__(props)
        self.check_balance()

    def check_balance(self):
        """check that reaction equation is balanced"""
        comps = []
        coeff = []
        for term in self.terms:
            composition = term['species'].composition
            if composition:
                comps.append(composition)
                coeff.append(term['coefficient'])
        if len(comps) != len(self.terms):
            msg = ('reaction balance check skipped due to missing composition in'
                   ' some terms')
            warnings.warn(msg, TextSUserWarning)
            return
        if not is_equation_balanced(comps, coeff, [], []):
            raise RuntimeValueError('Reaction equation is not balanced. Check '
                                    'coefficients and compositions of species.')

    def __getitem__(self, key):
        if isinstance(key, str):
            if key in self.props_list and key not in self.props:
                return self.prop_get(key)
        return super().__getitem__(key)

    def prop_get(self, prop):
        """compute a propery of reaction"""
        dtype = pint_pandas.PintType(self.prop_units[prop])
        self.props[prop] = pandas.Series([0.0], dtype=dtype)

        for term in self.terms:
            propval = getattr(term['species'], 'props')
            if prop in propval:
                if 'temperature' in propval and 'temperature' in self.props:
                    if any(propval['temperature'] != self.props['temperature']):
                        msg = 'temperatures of reaction and species must be equal'
                        raise RuntimeValueError(msg)
                self.props.loc[0, prop] += term['coefficient']*propval[prop][0]
            else:
                self.props.loc[0, prop] = ureg.Quantity(numpy.nan, self.prop_units[prop])
        return self.props[prop]


class ChemSpecies(ChemBase):
    """"custom chemical species class"""

    def __init__(self, name, composition=None, props=None):
        self.name = name
        self.composition = composition
        super().__init__(props)
        if any(prop not in self.props for prop in self.props_list):
            self.set_props()

    def set_props(self):
        """calculate and set values of missing properties"""
        if 'ethalpy' not in self.props:
            if all(prop in self.props for prop in ['energy', 'zpe']):
                self.props['enthalpy'] = self.props['energy'] + self.props['zpe']
        if 'free_energy' not in self.props:
            if all(prop in self.props for prop in ['enthalpy', 'entropy', 'temperature']):
                self.props['free_energy'] = (self.props['enthalpy'] -
                                             self.props['temperature']*self.props['entropy'])
        if 'enthalpy' not in self.props:
            if all(prop in self.props for prop in ['free_energy', 'entropy', 'temperature']):
                self.props['enthalpy'] = (self.props['free_energy'] +
                                          self.props['temperature']*self.props['entropy'])
        if 'energy' not in self.props:
            if all(prop in self.props for prop in ['enthalpy', 'zpe']):
                self.props['energy'] = self.props['enthalpy'] - self.props['zpe']
        if 'entropy' not in self.props:
            if all(prop in self.props for prop in ['enthalpy', 'free_energy', 'temperature']):
                self.props['entropy'] = ((self.props['enthalpy'] - self.props['free_energy']) /
                                         self.props['temperature'])

    def __getitem__(self, key):
        if isinstance(key, str):
            if key == 'name':
                return self.name
            if key == 'composition':
                return self.composition
        return super().__getitem__(key)
