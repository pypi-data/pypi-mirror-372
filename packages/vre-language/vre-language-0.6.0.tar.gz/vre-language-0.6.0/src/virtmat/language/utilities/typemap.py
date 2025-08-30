"""type map and custom type definitions"""
import numpy
import pandas
from virtmat.language.utilities import amml, chemistry
from virtmat.language.utilities.units import ureg
from virtmat.language.utilities.errors import RuntimeTypeError, StaticTypeError
from virtmat.language.utilities.types import NC

typemap = {
    'Boolean': bool,
    'String': str,
    'Integer': int,
    'Float': float,
    'Complex': complex,
    'Tuple': tuple,
    'Dict': dict,
    'Quantity': ureg.Quantity,
    'Table': pandas.DataFrame,
    'Series': pandas.Series,
    'BoolArray': numpy.ndarray,
    'StrArray': numpy.ndarray,
    'IntArray': ureg.Quantity,
    'FloatArray': ureg.Quantity,
    'ComplexArray': ureg.Quantity,
    'IntSubArray': numpy.ndarray,
    'FloatSubArray': numpy.ndarray,
    'ComplexSubArray': numpy.ndarray,
    'AMMLStructure': amml.AMMLStructure,
    'AMMLCalculator': amml.Calculator,
    'AMMLAlgorithm': amml.Algorithm,
    'AMMLProperty': amml.Property,
    'AMMLConstraint': amml.Constraint,
    'AMMLTrajectory': amml.Trajectory,
    'ChemReaction': chemistry.ChemReaction,
    'ChemSpecies': chemistry.ChemSpecies
}

table_like_type = (pandas.DataFrame, amml.AMMLObject, chemistry.ChemBase)


def is_table_like_type(type_):
    """return true if the type is table-like"""
    return issubclass(type_, table_like_type)


def is_table_like(obj):
    """return true if the obj is of table-like type"""
    return isinstance(obj, table_like_type)


class DType(type):
    """
    A special metaclass to create types on the fly. These types (classes) have
    our specific attributes datatype and datalen.
    datatype: either a type (int, float, bool, str) or tuple of types, or None
    datalen: either an int or a tuple of ints (int instances), or None
    """
    datatype = None
    datalen = None
    arraytype = False

    def __init__(cls, *args, **kwargs):
        def new(cls, *args, **kwargs):
            base_cls = cls.__bases__[0]
            obj = base_cls.__new__(base_cls, *args, **kwargs)
            obj.__class__ = cls
            return obj
        cls.__new__ = new
        super().__init__(*args, **kwargs)

    def __eq__(cls, other):
        if other is None:  # None is abused to describe unknown type
            return cls is None
        if set(cls.__bases__) != set(other.__bases__):
            return False
        if cls.datatype is None or other.datatype is None:
            return True
        if cls.datatype != other.datatype:
            return False
        return True

    def __hash__(cls):
        return hash(repr(cls))


def checktype_(rval, type_):
    """
    Check type at run time (dynamic type checking)
    rval: value to typecheck
    type_: bool, str or any type created with DType as metaclass
    Returns rval
    """
    if rval is not None and rval is not NC and type_ is not None:
        try:
            if issubclass(type_, (bool, str)):
                correct_type = type_
                assert isinstance(rval, type_)
            else:
                correct_type = typemap[type_.__name__]
                # assert issubclass(type(rval), correct_type)
                assert isinstance(rval, correct_type)
        except AssertionError as err:
            msg = f'type must be {correct_type} but is {type(rval)}'
            raise RuntimeTypeError(msg) from err
        except Exception as err:
            raise err
    return rval


def checktype(func):
    """
    Wrap a function to check the type of its returned value at run time
    func: a method of a metamodel object
    Returns: a wrapped func
    """
    def wrapper(obj):
        return checktype_(func(obj), obj.type_)
    return wrapper


specs = [
    {'typ': 'Type', 'basetype': 'Table', 'typespec': {}},
    {'typ': 'AMMLStructure', 'basetype': 'AMMLStructure', 'typespec': {'datatype': None}},
    {'typ': 'AMMLStructure', 'id': 'name', 'basetype': str},
    {'typ': 'AMMLStructure', 'id': 'atoms', 'basetype': 'Series',
     'typespec': {'datatype': ('AtomsTable', 'Table')}},
    {'typ': 'AtomsTable', 'basetype': 'Table', 'typespec': {'datatype': None}},
    {'typ': 'AMMLStructure', 'id': 'pbc', 'basetype': 'Series',
     'typespec': {'datatype': ('BoolArray', 'BoolArray')}},
    {'typ': 'AMMLStructure', 'id': 'cell', 'basetype': 'Series',
     'typespec': {'datatype': ('FloatArray', 'FloatArray')}},
    {'typ': 'AMMLStructure', 'id': 'kinetic_energy', 'basetype': 'Series',
     'typespec': {'datatype': float}},
    {'typ': 'AMMLStructure', 'id': 'temperature', 'basetype': 'Series',
     'typespec': {'datatype': float}},
    {'typ': 'AMMLStructure', 'id': 'distance_matrix', 'basetype': 'Series',
     'typespec': {'datatype': ('FloatArray', 'FloatArray')}},
    {'typ': 'AMMLStructure', 'id': 'chemical_formula', 'basetype': 'Series',
     'typespec': {'datatype': str}},
    {'typ': 'AMMLStructure', 'id': 'number_of_atoms', 'basetype': 'Series',
     'typespec': {'datatype': int}},
    {'typ': 'AMMLStructure', 'id': 'cell_volume', 'basetype': 'Series',
     'typespec': {'datatype': float}},
    {'typ': 'AMMLStructure', 'id': 'center_of_mass', 'basetype': 'Series',
     'typespec': {'datatype': 'FloatArray'}},
    {'typ': 'AMMLStructure', 'id': 'radius_of_gyration', 'basetype': 'Series',
     'typespec': {'datatype': float}},
    {'typ': 'AMMLStructure', 'id': 'moments_of_inertia', 'basetype': 'Series',
     'typespec': {'datatype': 'FloatArray'}},
    {'typ': 'AMMLStructure', 'id': 'angular_momentum', 'basetype': 'Series',
     'typespec': {'datatype': 'FloatArray'}},
    {'typ': 'AMMLCalculator', 'id': 'name', 'basetype': str},
    {'typ': 'AMMLCalculator', 'id': 'pinning', 'basetype': str},
    {'typ': 'AMMLCalculator', 'id': 'version', 'basetype': str},
    {'typ': 'AMMLCalculator', 'id': 'task', 'basetype': str},
    {'typ': 'AMMLCalculator', 'id': 'parameters', 'basetype': 'Table',
     'typespec': {'datatype': None}},
    {'typ': 'AMMLAlgorithm', 'id': 'name', 'basetype': str},
    {'typ': 'AMMLAlgorithm', 'id': 'parameters', 'basetype': 'Table',
     'typespec': {'datatype': None}},
    {'typ': 'AMMLProperty', 'id': 'names', 'basetype': 'Tuple',
     'typespec': {'datatype': None}},
    {'typ': 'AMMLProperty', 'id': 'calculator', 'basetype': 'AMMLCalculator',
     'typespec': {}},
    {'typ': 'AMMLProperty', 'id': 'algorithm', 'basetype': 'AMMLAlgorithm',
     'typespec': {}},
    {'typ': 'AMMLProperty', 'id': 'structure', 'basetype': 'AMMLStructure',
     'typespec': {}},
    {'typ': 'AMMLProperty', 'id': 'output_structure', 'basetype': 'AMMLStructure',
     'typespec': {}},
    {'typ': 'AMMLProperty', 'id': 'rmsd', 'basetype': 'Series',
     'typespec': {'datatype': float}},
    {'typ': 'AMMLProperty', 'id': 'forces', 'basetype': 'Series',
     'typespec': {'datatype': ('FloatArray', 'FloatArray')}},
    {'typ': 'AMMLProperty', 'id': 'dipole', 'basetype': 'Series',
     'typespec': {'datatype': ('FloatArray', 'FloatArray')}},
    {'typ': 'AMMLProperty', 'id': 'hessian', 'basetype': 'Series',
     'typespec': {'datatype': ('FloatArray', 'FloatArray')}},
    {'typ': 'AMMLProperty', 'id': 'vibrational_modes', 'basetype': 'Series',
     'typespec': {'datatype': ('FloatArray', 'FloatArray')}},
    {'typ': 'AMMLProperty', 'id': 'vibrational_energies', 'basetype': 'Series',
     'typespec': {'datatype': ('FloatSeries', 'Series')}},
    {'typ': 'AMMLProperty', 'id': 'energy_minimum', 'basetype': 'Series',
     'typespec': {'datatype': bool}},
    {'typ': 'AMMLProperty', 'id': 'transition_state', 'basetype': 'Series',
     'typespec': {'datatype': bool}},
    {'typ': 'AMMLProperty', 'id': 'energy', 'basetype': 'Series',
     'typespec': {'datatype': float}},
    {'typ': 'AMMLProperty', 'id': 'constraints', 'basetype': 'Tuple',
     'typespec': {'datatype': ('AMMLConstraint', 'AMMLConstraint')}},
    {'typ': 'AMMLProperty', 'id': 'results', 'basetype': 'Table',
     'typespec': {'datatype': None}},
    {'typ': 'AMMLProperty', 'id': 'rdf', 'basetype': 'Series',
     'typespec': {'datatype': ('FloatArray', 'FloatArray')}},
    {'typ': 'AMMLProperty', 'id': 'rdf_distance', 'basetype': 'Series',
     'typespec': {'datatype': ('FloatArray', 'FloatArray')}},
    {'typ': 'AMMLProperty', 'id': 'trajectory', 'basetype': 'Series',
     'typespec': {'datatype': ('AMMLTrajectory', 'AMMLTrajectory')}},
    {'typ': 'AMMLProperty', 'id': 'stress', 'basetype': 'Series',
     'typespec': {'datatype': ('FloatArray', 'FloatArray')}},
    {'typ': 'AMMLProperty', 'id': 'magmom', 'basetype': 'Series',
     'typespec': {'datatype': float}},
    {'typ': 'AMMLProperty', 'id': 'magmoms', 'basetype': 'Series',
     'typespec': {'datatype': ('FloatArray', 'FloatArray')}},
    {'typ': 'AMMLProperty', 'id': 'minimum_energy', 'basetype': 'Series',
     'typespec': {'datatype': float}},
    {'typ': 'AMMLProperty', 'id': 'bulk_modulus', 'basetype': 'Series',
     'typespec': {'datatype': float}},
    {'typ': 'AMMLProperty', 'id': 'optimal_volume', 'basetype': 'Series',
     'typespec': {'datatype': float}},
    {'typ': 'AMMLProperty', 'id': 'eos_volume', 'basetype': 'Series',
     'typespec': {'datatype': ('FloatArray', 'FloatArray')}},
    {'typ': 'AMMLProperty', 'id': 'eos_energy', 'basetype': 'Series',
     'typespec': {'datatype': ('FloatArray', 'FloatArray')}},
    {'typ': 'AMMLProperty', 'id': 'dos_energy', 'basetype': 'Series',
     'typespec': {'datatype': ('FloatArray', 'FloatArray')}},
    {'typ': 'AMMLProperty', 'id': 'dos', 'basetype': 'Series',
     'typespec': {'datatype': ('FloatArray', 'FloatArray')}},
    {'typ': 'AMMLProperty', 'id': 'band_structure', 'basetype': 'Series',
     'typespec': {'datatype': ('BSTable', 'Table')}},
    {'typ': 'AMMLProperty', 'id': 'activation_energy', 'basetype': 'Series',
     'typespec': {'datatype': float}},
    {'typ': 'AMMLProperty', 'id': 'reaction_energy', 'basetype': 'Series',
     'typespec': {'datatype': float}},
    {'typ': 'AMMLProperty', 'id': 'maximum_force', 'basetype': 'Series',
     'typespec': {'datatype': float}},
    {'typ': 'AMMLProperty', 'id': 'velocity', 'basetype': 'Series',
     'typespec': {'datatype': ('FloatArray', 'FloatArray')}},
    {'typ': 'AMMLProperty', 'id': 'vdf', 'basetype': 'Series',
     'typespec': {'datatype': ('FloatArray', 'FloatArray')}},
    {'typ': 'AMMLProperty', 'id': 'neighbors', 'basetype': 'Series',
     'typespec': {'datatype': ('IntArray', 'IntArray')}},
    {'typ': 'AMMLProperty', 'id': 'neighbor_offsets', 'basetype': 'Series',
     'typespec': {'datatype': ('FloatArray', 'FloatArray')}},
    {'typ': 'AMMLProperty', 'id': 'connectivity_matrix', 'basetype': 'Series',
     'typespec': {'datatype': ('IntArray', 'IntArray')}},
    {'typ': 'AMMLProperty', 'id': 'connected_components', 'basetype': 'Series',
     'typespec': {'datatype': ('IntArray', 'IntArray')}},
    {'typ': 'BSTable', 'basetype': 'Table', 'typespec': {'datatype': None}},
    {'typ': 'AMMLConstraint', 'basetype': 'AMMLConstraint', 'typespec': {}},
    {'typ': 'AMMLTrajectory', 'basetype': 'AMMLTrajectory', 'typespec': {}},
    {'typ': 'AMMLTrajectory', 'id': 'description', 'basetype': 'Table', 'typespec': {}},
    {'typ': 'AMMLTrajectory', 'id': 'structure', 'basetype': 'AMMLStructure', 'typespec': {}},
    {'typ': 'AMMLTrajectory', 'id': 'properties', 'basetype': 'Table', 'typespec': {}},
    {'typ': 'AMMLTrajectory', 'id': 'constraints', 'basetype': 'Series',
     'typespec': {'datatype': ('AMMLConstraint', 'AMMLConstraint')}},
    {'typ': 'AMMLTrajectory', 'id': 'filename', 'basetype': str, 'typespec': {}},
    {'typ': 'ChemSpecies', 'id': 'properties', 'basetype': 'Table', 'typespec': {}},
    {'typ': 'ChemSpecies', 'id': 'energy', 'basetype': 'Series',
     'typespec': {'datatype': float}},
    {'typ': 'ChemSpecies', 'id': 'enthalpy', 'basetype': 'Series',
     'typespec': {'datatype': float}},
    {'typ': 'ChemSpecies', 'id': 'entropy', 'basetype': 'Series',
     'typespec': {'datatype': float}},
    {'typ': 'ChemSpecies', 'id': 'free_energy', 'basetype': 'Series',
     'typespec': {'datatype': float}},
    {'typ': 'ChemSpecies', 'id': 'zpe', 'basetype': 'Series',
     'typespec': {'datatype': float}},
    {'typ': 'ChemSpecies', 'id': 'temperature', 'basetype': 'Series',
     'typespec': {'datatype': float}},
    {'typ': 'ChemSpecies', 'id': 'name', 'basetype': str},
    {'typ': 'ChemSpecies', 'id': 'composition', 'basetype': str},
    {'typ': 'ChemReaction', 'id': 'properties', 'basetype': 'Table', 'typespec': {}},
    {'typ': 'ChemReaction', 'id': 'energy', 'basetype': 'Series',
     'typespec': {'datatype': float}},
    {'typ': 'ChemReaction', 'id': 'enthalpy', 'basetype': 'Series',
     'typespec': {'datatype': float}},
    {'typ': 'ChemReaction', 'id': 'entropy', 'basetype': 'Series',
     'typespec': {'datatype': float}},
    {'typ': 'ChemReaction', 'id': 'free_energy', 'basetype': 'Series',
     'typespec': {'datatype': float}},
    {'typ': 'ChemReaction', 'id': 'zpe', 'basetype': 'Series',
     'typespec': {'datatype': float}},
    {'typ': 'ChemReaction', 'id': 'temperature', 'basetype': 'Series',
     'typespec': {'datatype': float}},
    {'typ': 'BoolArray', 'basetype': 'BoolArray',
     'typespec': {'datatype': bool, 'arraytype': True}},
    {'typ': 'IntArray', 'basetype': 'IntArray',
     'typespec': {'datatype': int, 'arraytype': True}},
    {'typ': 'FloatArray', 'basetype': 'FloatArray',
     'typespec': {'datatype': float, 'arraytype': True}},
    {'typ': 'ComplexArray', 'basetype': 'ComplexArray',
     'typespec': {'datatype': complex, 'arraytype': True}},
    {'typ': 'FloatSeries', 'basetype': 'Series', 'typespec': {'datatype': float}},
    {'typ': 'Series', 'basetype': 'Series', 'typespec': {'datatype': None}},
    {'typ': 'IntSubArray', 'basetype': 'IntArray',
     'typespec': {'datatype': int, 'arraytype': True}},
    {'typ': 'FloatSubArray', 'basetype': 'FloatArray',
     'typespec': {'datatype': float, 'arraytype': True}},
    {'typ': 'ComplexSubArray', 'basetype': 'ComplexArray',
     'typespec': {'datatype': complex, 'arraytype': True}},
]


def get_dtype(typ, basetype=None, id_=None):
    """Return a DType type (class)

    Args:
        typ (str): DType name
        basetype (str): the basetype of typ if id_ is None, otherwise of attribute
        id_ (str): optional name of attribute of typ, default is None

    Returns:
        the DType type or None

    Raises:
        StaticTypeError: when DType cannot be determined
    """
    for spec in specs:
        if spec['typ'] == typ and (spec['basetype'] == basetype or spec.get('id') == id_):
            if isinstance(spec['basetype'], type):
                return spec['basetype']
            if 'datatype' in spec['typespec'] and isinstance(spec['typespec']['datatype'], tuple):
                spec['typespec']['datatype'] = get_dtype(*spec['typespec']['datatype'])
            return DType(spec['basetype'], (typemap[spec['basetype']],), spec['typespec'])
    msg = f'could not find DType for type: {typ}, basetype: {basetype}, id_: {id_}'
    raise StaticTypeError(msg)
