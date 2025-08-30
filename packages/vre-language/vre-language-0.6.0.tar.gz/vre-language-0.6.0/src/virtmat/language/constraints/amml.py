"""checks / constraints for AMML objects"""
from textx import get_children_of_type
from virtmat.language.utilities.errors import StaticTypeError
from virtmat.language.utilities.errors import raise_exception, StaticValueError
from virtmat.language.utilities.textx import get_reference
from virtmat.language.utilities.typemap import typemap
from virtmat.language.utilities.ase_params import spec

task_properties = {
  'single point': ['energy', 'forces', 'dipole', 'stress', 'charges', 'magmom', 'magmoms'],
  'local minimum': ['energy', 'forces', 'dipole', 'stress', 'charges', 'trajectory'],
  'global minimum': ['energy', 'forces', 'dipole', 'stress', 'charges', 'trajectory'],
  'transition state': ['energy', 'forces', 'dipole', 'stress', 'charges', 'trajectory'],
  'normal modes': ['vibrational_energies', 'energy_minimum', 'transition_state'],
  'micro-canonical': ['energy', 'forces', 'dipole', 'stress', 'charges', 'trajectory'],
  'canonical': ['energy', 'forces', 'dipole', 'stress', 'charges', 'trajectory'],
  'isothermal-isobaric': ['energy', 'forces', 'dipole', 'stress', 'charges', 'trajectory'],
  'grand-canonical': ['energy', 'forces', 'dipole', 'stress', 'charges', 'trajectory']
}


def check_amml_property_processor(model, _):
    """check compatibility of properties with calculator task"""
    for obj in get_children_of_type('AMMLProperty', model):
        assert obj.calc or obj.algo
        algo = obj.algo and get_reference(obj.algo)
        calc = obj.calc and get_reference(obj.calc)
        calc_task = get_reference(obj.calc).task if obj.calc else ''
        calc_name = calc.name if calc else ''
        algo_name = algo.name if algo else ''
        if obj.algo:
            algo_obj = get_reference(obj.algo)
            if 'calc_task' in spec[algo_obj.name]:
                if not obj.calc:
                    msg = f'property needs a calculator for algorithm "{algo_obj.name}"'
                    raise_exception(obj, StaticValueError, msg)
        if algo and calc:
            algo_task = spec[algo_name].get('calc_task')
            if algo_task and calc.task not in algo_task:
                message = (f'calculator task \"{calc.task}\" not compatible with '
                           f'algorithm \"{algo.name}\"')
                raise_exception(obj, StaticValueError, message)
        for name in obj.names:
            msg = (f'property \"{name}\" not available in algo \"{algo_name}\"'
                   f' or calc \"{calc_name}\"')
            if algo and name not in spec[algo_name]['properties']:
                if not calc or name not in spec[calc_name]['properties']:
                    raise_exception(obj, StaticValueError, msg)
            if calc and name not in spec[calc_name]['properties']:
                if not algo or name not in spec[algo_name]['properties']:
                    raise_exception(obj, StaticValueError, msg)
            if not algo and calc_task and name not in task_properties[calc_task]:
                msg = f'property \"{name}\" not available in task \"{calc_task}\"'
                raise_exception(obj, StaticValueError, msg)


def check_view_amml_structure_processor(model, _):
    """check the parameters of view structure statements"""
    for obj in get_children_of_type('View', model):
        if obj.mode != 'structure':
            continue
        if len(obj.params) > 2:
            msg = f'view structure has maximum 2 parameters but {len(obj.params)} given'
            raise_exception(obj, StaticTypeError, msg)
        if obj.params[0].type_:
            if not issubclass(obj.params[0].type_, typemap['AMMLStructure']):
                msg = (f'parameter must be type {typemap["AMMLStructure"].__name__}'
                       f' but is type {obj.params[0].type_.__name__}')
                raise_exception(obj.params[0], StaticTypeError, msg)
        if len(obj.params) == 2:
            if obj.params[1].type_:
                if not issubclass(obj.params[1].type_, typemap['Tuple']):
                    msg = 'parameter must be Tuple of constraints'
                    raise_exception(obj.params[1], StaticTypeError, msg)
                for type_ in obj.params[1].type_.datatype:
                    if type_ and not issubclass(type_, typemap['AMMLConstraint']):
                        msg = (f'parameter must be type {typemap["AMMLConstraint"].__name__}'
                               f' but is type {type_.__name__}')
                        raise_exception(obj.params[1], StaticTypeError, msg)
