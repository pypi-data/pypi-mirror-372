"""various utility and handler functions for ASE"""
import math
import pandas
import numpy
import pint
import pint_pandas
from pint_pandas import PintType
import ase
from virtmat.language.utilities.errors import PropertyError
from virtmat.language.utilities.units import ureg
from . import amml

pint_pandas.pint_array.DEFAULT_SUBDTYPE = None

EC_ANG = 'elementary_charge * angstrom'
EC_BOHR = 'elementary_charge * bohr'
EV_PER_ANG = 'eV / angstrom'


def tm_dipole_handler(results):  # not covered
    """handler function for the electric dipole moment"""
    res = []
    for result in results:
        dct = result['calc'].results['electric dipole moment']
        magnitude = dct['absolute value']['value']
        units = dct['absolute value']['units'].lower()
        assert units == 'debye'
        ref = ureg.Quantity(magnitude, units)
        assert dct['vector']['units'] == 'a.u.'
        vec = ureg.Quantity(dct['vector']['array'], EC_BOHR)
        test = pint.Quantity(numpy.linalg.norm(vec.to('D').magnitude), vec.to('D').units)
        assert math.isclose(test.magnitude, ref.magnitude, rel_tol=0.001)
        res.append(vec)
    return pandas.Series(res)


def vasp_vibrational_energies_handler(results):  # not covered
    """retrieve vibrational energies from normal modes"""
    dtype = pint_pandas.PintType('eV')
    data = []
    for result in results:
        vib_ene_real = result['calc'].read_vib_freq()[0]  # returns in meV
        vib_ene_real = numpy.array(vib_ene_real)*1.0e-3
        data.append(pandas.Series(vib_ene_real, name='vibrational_energies', dtype=dtype))
    return pandas.Series(data)


def vasp_energy_minimum_handler(results):  # not covered
    """determine an energy minimum from normal modes"""
    data = []
    for result in results:
        data.append(len(result['calc'].read_vib_freq()[1]) == 0)
    return pandas.Series(data)


def vasp_transition_state_handler(results):  # not covered
    """determine a transition state from normal modes"""
    data = []
    for result in results:
        data.append(len(result['calc'].read_vib_freq()[1]) == 1)
    return pandas.Series(data)


def vasp_trajectory_handler(results):  # not covered
    """retrieve trajectory from vasprun.xml file created by VASP calculator"""
    data = []
    for _ in results:
        images = ase.io.read('vasprun.xml', index=':')
        constraints = [image.constraints for image in images]
        data.append(amml.Trajectory.from_ase(None, images, constraints))
    return pandas.Series(data)


def generic_trajectory_handler(results):
    """retrieve trajectory from a trajectory file created by an algorithm"""
    data = []
    for result in results:
        writer = result['algo'].trajectory
        if writer is None:
            raise PropertyError('property "trajectory" not available')
        data.append(amml.Trajectory.from_file(writer.filename))
    return pandas.Series(data)


def tm_vibrational_energies_handler(results):  # not covered
    """retrieve vibrational energies from normal modes"""
    dtype = pint_pandas.PintType('eV')
    data = []
    for result in results:
        vibspec = result['calc'].results['vibrational spectrum']
        vib_ene = []
        for eigenvalue in vibspec:
            if eigenvalue['irreducible representation']:
                assert eigenvalue['frequency']['units'] == 'cm^-1'
                fact = ase.units.invcm
                if eigenvalue['frequency']['value'] > 0.0:
                    vib_ene.append(eigenvalue['frequency']['value']*fact)
        data.append(pandas.Series(vib_ene, name='vibrational_energies', dtype=dtype))
    return pandas.Series(data)


def tm_energy_minimum_handler(results):  # not covered
    """determine an energy minimum from normal modes"""
    data = []
    for result in results:
        vibspec = result['calc'].results['vibrational spectrum']
        real = True
        for eigenvalue in vibspec:
            if eigenvalue['irreducible representation']:
                if eigenvalue['frequency']['value'] < 0.0:
                    real = False
                    break
        data.append(real)
    return pandas.Series(data)


def tm_transition_state_handler(results):  # not covered
    """determine a transition state from normal modes"""
    data = []
    for result in results:
        vibspec = result['calc'].results['vibrational spectrum']
        im = []
        for eigenvalue in vibspec:
            if eigenvalue['irreducible representation']:
                im.append(eigenvalue['frequency']['value'] < 0.0)
        data.append(sum(im) == 1)
    return pandas.Series(data)


def generic_band_structure_handler(results):
    """retrieve band structure and convert to series of dataframes"""
    lst = []
    for result in results:
        dct = result['algo'].results['band_structure']
        dct_ = {}
        assert isinstance(dct['energies'], numpy.ndarray)
        assert isinstance(dct['reference'], float)
        dct_['energies'] = ureg.Quantity(dct['energies'], 'eV')
        dct_['reference'] = ureg.Quantity(dct['reference'], 'eV')
        bp = dct['path']
        sp = {k: [ureg.Quantity(v, 'angstrom**-1')] for k, v in bp.special_points.items()}
        band_path = {'cell': [ureg.Quantity(bp.cell.array, 'angstrom')],
                     'path': [bp.path],
                     'kpts': [ureg.Quantity(bp.kpts, 'angstrom**-1')],
                     'special_points': [pandas.DataFrame.from_dict(sp)]}
        dct_['band_path'] = pandas.DataFrame.from_dict(band_path)
        lst.append(pandas.DataFrame([dct_]))
    return pandas.Series(lst)


ase_p_df = pandas.DataFrame([
  {
   'method': 'SinglePointCalculator',
   'property': 'energy',
   'handler': lambda x: pandas.Series((i['calc'].export_properties()['energy'] for i in x),
                                      dtype=PintType('eV'))
  },
  {
   'method': 'SinglePointCalculator',
   'property': 'natoms',
   'handler': lambda x: pandas.Series((ureg.Quantity(i['calc'].export_properties()['natoms'])
                                      for i in x))
  },
  {
   'method': 'SinglePointCalculator',
   'property': 'forces',
   'handler': lambda x: pandas.Series(ureg.Quantity(f['calc'].export_properties()['forces'],
                                                    EV_PER_ANG) for f in x)
  },
  {
   'method': 'SinglePointCalculator',
   'property': 'energies',
   'handler': lambda x: pandas.Series(ureg.Quantity(e['calc'].export_properties()['energies'],
                                                    'eV') for e in x)
  },
  {
   'method': 'SinglePointCalculator',
   'property': 'free_energy',
   'handler': lambda x: pandas.Series((i['calc'].export_properties()['free_energy'] for i in x),
                                      dtype=PintType('eV'))
  },
  {
   'method': 'SinglePointCalculator',
   'property': 'stress',
   'handler': lambda x: pandas.Series(ureg.Quantity(f['calc'].export_properties()['stress'],
                                                    'eV / angstrom**3') for f in x)
  },
  {
   'method': 'SinglePointCalculator',
   'property': 'stresses',
   'handler': lambda x: pandas.Series(ureg.Quantity(f['calc'].export_properties()['stresses'],
                                                    'eV / angstrom**3') for f in x)
  },
  {
   'method': 'BFGS',
   'property': 'trajectory',
   'handler': generic_trajectory_handler
  },
  {
   'method': 'LBFGS',
   'property': 'trajectory',
   'handler': generic_trajectory_handler
  },
  {
   'method': 'LBFGSLineSearch',
   'property': 'trajectory',
   'handler': generic_trajectory_handler
  },
  {
   'method': 'QuasiNewton',
   'property': 'trajectory',
   'handler': generic_trajectory_handler
  },
  {
   'method': 'BFGSLineSearch',
   'property': 'trajectory',
   'handler': generic_trajectory_handler
  },
  {
   'method': 'GPMin',
   'property': 'trajectory',
   'handler': generic_trajectory_handler
  },
  {
   'method': 'FIRE',
   'property': 'trajectory',
   'handler': generic_trajectory_handler
  },
  {
   'method': 'MDMin',
   'property': 'trajectory',
   'handler': generic_trajectory_handler
  },
  {
   'method': 'VelocityVerlet',
   'property': 'trajectory',
   'handler': generic_trajectory_handler
  },
  {
   'method': 'Langevin',
   'property': 'trajectory',
   'handler': generic_trajectory_handler
  },
  {
   'method': 'NPT',
   'property': 'trajectory',
   'handler': generic_trajectory_handler
  },
  {
   'method': 'Andersen',
   'property': 'trajectory',
   'handler': generic_trajectory_handler
  },
  {
   'method': 'NVTBerendsen',
   'property': 'trajectory',
   'handler': generic_trajectory_handler
  },
  {
   'method': 'NPTBerendsen',
   'property': 'trajectory',
   'handler': generic_trajectory_handler
  },
  {
   'method': 'RMSD',
   'property': 'rmsd',
   'handler': lambda x: pandas.Series((i['algo'].results['rmsd'] for i in x),
                                      dtype=PintType('angstrom'))
  },
  {
   'method': 'RDF',
   'property': 'rdf',
   'handler': lambda x: pandas.Series(ureg.Quantity(i['algo'].results['rdf']) for i in x)
  },
  {
   'method': 'RDF',
   'property': 'rdf_distance',
   'handler': lambda x: pandas.Series(ureg.Quantity(i['algo'].results['rdf_distance'],
                                                    'angstrom') for i in x)
  },
  {
   'method': 'VelocityDistribution',
   'property': 'vdf',
   'handler': lambda x: pandas.Series(ureg.Quantity(i['algo'].results['vdf']) for i in x)
  },
  {
   'method': 'VelocityDistribution',
   'property': 'velocity',
   'handler': lambda x: pandas.Series(ureg.Quantity(i['algo'].results['velocity'],
                                                    '(eV / amu) ** (1/2)') for i in x)
  },
  {
   'method': 'EquationOfState',
   'property': 'minimum_energy',
   'handler': lambda x: pandas.Series(ureg.Quantity(i['algo'].results['minimum_energy'],
                                                    'eV') for i in x)
  },
  {
   'method': 'EquationOfState',
   'property': 'optimal_volume',
   'handler': lambda x: pandas.Series(ureg.Quantity(i['algo'].results['optimal_volume'],
                                                    'angstrom**3') for i in x)
  },
  {
   'method': 'EquationOfState',
   'property': 'bulk_modulus',
   'handler': lambda x: pandas.Series(ureg.Quantity(i['algo'].results['bulk_modulus'],
                                                    'eV/angstrom**3') for i in x)
  },
  {
   'method': 'EquationOfState',
   'property': 'eos_volume',
   'handler': lambda x: pandas.Series(ureg.Quantity(i['algo'].results['eos_volume'],
                                                    'angstrom**3') for i in x)
  },
  {
   'method': 'EquationOfState',
   'property': 'eos_energy',
   'handler': lambda x: pandas.Series(ureg.Quantity(i['algo'].results['eos_energy'],
                                                    'eV') for i in x)
  },
  {
   'method': 'DensityOfStates',
   'property': 'dos_energy',
   'handler': lambda x: pandas.Series(ureg.Quantity(i['algo'].results['dos_energy'],
                                                    'eV') for i in x)
  },
  {
   'method': 'DensityOfStates',
   'property': 'dos',
   'handler': lambda x: pandas.Series(ureg.Quantity(i['algo'].results['dos']) for i in x)
  },
  {
   'method': 'NEB',
   'property': 'trajectory',
   'handler': generic_trajectory_handler
  },
  {
   'method': 'NEB',
   'property': 'activation_energy',
   'handler': lambda x: pandas.Series(ureg.Quantity(i['algo'].results['activation_energy'],
                                                    'eV') for i in x)
  },
  {
   'method': 'NEB',
   'property': 'reaction_energy',
   'handler': lambda x: pandas.Series(ureg.Quantity(i['algo'].results['reaction_energy'],
                                                    'eV') for i in x)
  },
  {
   'method': 'NEB',
   'property': 'maximum_force',
   'handler': lambda x: pandas.Series(ureg.Quantity(i['algo'].results['maximum_force'],
                                                    'eV/angstrom') for i in x)
  },
  {
   'method': 'NEB',
   'property': 'energy',
   'handler': lambda x: pandas.Series((i['algo'].results['energy'] for i in x),
                                      dtype=PintType('eV'))
  },
  {
   'method': 'NEB',
   'property': 'forces',
   'handler': lambda x: pandas.Series((i['algo'].results['forces'] for i in x),
                                      dtype=PintType(EV_PER_ANG))
  },
  {
   'method': 'Dimer',
   'property': 'energy',
   'handler': lambda x: pandas.Series((i['algo'].atoms.get_potential_energy() for i in x),
                                      dtype=PintType('eV'))
  },
  {
   'method': 'Dimer',
   'property': 'forces',
   'handler': lambda x: pandas.Series((i['algo'].atoms.get_forces() for i in x),
                                      dtype=PintType(EV_PER_ANG))
  },
  {
   'method': 'Dimer',
   'property': 'trajectory',
   'handler': generic_trajectory_handler
  },
  {
   'method': 'Vibrations',
   'property': 'hessian',
   'handler': lambda x: pandas.Series((ureg.Quantity(i['algo'].results['hessian'],
                                       'eV / angstrom**2') for i in x))
  },
  {
   'method': 'Vibrations',
   'property': 'vibrational_modes',
   'handler': lambda x: pandas.Series((ureg.Quantity(i['algo'].results['eigen_modes'],
                                       'angstrom') for i in x))
  },
  {
   'method': 'Vibrations',
   'property': 'vibrational_energies',
   'handler': lambda x: pandas.Series(pandas.Series(i['algo'].results['eigen_real'],
                                      dtype=PintType('eV'), name='vibrational_energies') for i in x)
  },
  {
   'method': 'Vibrations',
   'property': 'transition_state',
   'handler': lambda x: pandas.Series(i['algo'].results['transition_state'] for i in x)
  },
  {
   'method': 'Vibrations',
   'property': 'energy_minimum',
   'handler': lambda x: pandas.Series(i['algo'].results['energy_minimum'] for i in x)
  },
  {
   'method': 'NeighborList',
   'property': 'neighbors',
   'handler': lambda x: pandas.Series(tuple(ureg.Quantity(j)
                                      for j in i['algo'].results['neighbors'])
                                      for i in x)
  },
  {
   'method': 'NeighborList',
   'property': 'neighbor_offsets',
   'handler': lambda x: pandas.Series(tuple(ureg.Quantity(j, 'angstrom')
                                      for j in i['algo'].results['neighbor_offsets'])
                                      for i in x)
  },
  {
   'method': 'NeighborList',
   'property': 'connectivity_matrix',
   'handler': lambda x: pandas.Series(ureg.Quantity(i['algo'].results['connectivity_matrix'])
                                      for i in x)
  },
  {
   'method': 'NeighborList',
   'property': 'connected_components',
   'handler': lambda x: pandas.Series(ureg.Quantity(i['algo'].results['connected_components'])
                                      for i in x)
  },
  {
   'method': 'lj',
   'property': 'energy',
   'handler': lambda x: pandas.Series((i['calc'].results['energy'] for i in x),
                                      dtype=PintType('eV'))
  },
  {
   'method': 'lj',
   'property': 'forces',
   'handler': lambda x: pandas.Series(ureg.Quantity(i['calc'].results['forces'],
                                                    EV_PER_ANG) for i in x)
  },
  {
   'method': 'emt',
   'property': 'energy',
   'handler': lambda x: pandas.Series((i['calc'].results['energy'] for i in x),
                                      dtype=PintType('eV'))
  },
  {
   'method': 'emt',
   'property': 'forces',
   'handler': lambda x: pandas.Series(ureg.Quantity(i['calc'].results['forces'],
                                                    EV_PER_ANG) for i in x)
  },
  {
   'method': 'emt',
   'property': 'stress',
   'handler': lambda x: pandas.Series(ureg.Quantity(i['calc'].results['stress'],
                                                    'eV / angstrom **3') for i in x)
  },
  {
   'method': 'free_electrons',
   'property': 'energy',
   'handler': lambda x: pandas.Series((i['calc'].results['energy'] for i in x),
                                      dtype=PintType('eV'))
  },
  {
   'method': 'BandStructure',
   'property': 'band_structure',
   'handler': generic_band_structure_handler
  },
  {
   'method': 'vasp',
   'property': 'energy',
   'handler': lambda x: pandas.Series((i['calc'].results['energy'] for i in x),
                                      dtype=PintType('eV'))
  },
  {
   'method': 'vasp',
   'property': 'dipole',
   'handler': lambda x: pandas.Series(ureg.Quantity(i['calc'].results['dipole'],
                                                    EC_ANG) for i in x)
  },
  {
   'method': 'vasp',
   'property': 'forces',
   'handler': lambda x: pandas.Series(ureg.Quantity(i['calc'].results['forces'],
                                                    EV_PER_ANG) for i in x)
  },
  {
   'method': 'vasp',
   'property': 'stress',
   'handler': lambda x: pandas.Series(ureg.Quantity(i['calc'].results['stress'],
                                                    'eV / angstrom**3') for i in x)
  },
  {
   'method': 'vasp',
   'property': 'vibrational_energies',
   'handler': vasp_vibrational_energies_handler
  },
  {
   'method': 'vasp',
   'property': 'energy_minimum',
   'handler': vasp_energy_minimum_handler
  },
  {
   'method': 'vasp',
   'property': 'transition_state',
   'handler': vasp_transition_state_handler
  },
  {
   'method': 'vasp',
   'property': 'trajectory',
   'handler': vasp_trajectory_handler
  },
  {
   'method': 'vasp',
   'property': 'magmom',
   'handler': lambda x: pandas.Series(ureg.Quantity(c['calc'].get_magnetic_moment()) for c in x)
  },
  {
   'method': 'vasp',
   'property': 'magmoms',
   'handler': lambda x: pandas.Series(ureg.Quantity(c['calc'].get_magnetic_moments()) for c in x)
  },
  {
   'method': 'turbomole',
   'property': 'energy',
   'handler': lambda x: pandas.Series((i['calc'].results['total energy'] for i in x),
                                      dtype=PintType('eV'))
  },
  {
   'method': 'turbomole',
   'property': 'dipole',
   'handler': tm_dipole_handler,
  },
  {
   'method': 'turbomole',
   'property': 'forces',
   'handler': lambda x: pandas.Series(-ureg.Quantity(i['calc'].results['energy gradient'],
                                                     EV_PER_ANG) for i in x)
  },
  {
   'method': 'turbomole',
   'property': 'vibrational_energies',
   'handler': tm_vibrational_energies_handler
  },
  {
   'method': 'turbomole',
   'property': 'energy_minimum',
   'handler': tm_energy_minimum_handler
  },
  {
   'method': 'turbomole',
   'property': 'transition_state',
   'handler': tm_transition_state_handler
  },
])


def get_ase_property(method, prop_name, results):
    """call a property handler and return series of property values"""
    dfr = ase_p_df[(ase_p_df['method'] == method) & (ase_p_df['property'] == prop_name)]
    msg = f'no property "{prop_name}" found for method "{method}"'
    if len(dfr['handler']) == 0:
        raise PropertyError(msg)
    return next(iter(dfr['handler']))(results)
