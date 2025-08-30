"""default values of parameters used in ASE calculators and algorithms"""
import numpy
from virtmat.language.utilities.units import ureg
from virtmat.language.utilities.ase_units import calc_pars as calc_units

# at least one parameter default per calculator must be defined

calc_pars = {}

calc_pars['vasp'] = {k: None for k in calc_units['vasp']}

calc_pars['turbomole'] = {
    'restart': False,
    'define_str': None,
    'control_kdg': None,
    'control_input': None,
    'reset_tolerance': ureg.Quantity(1e-2, 'angstrom'),
    'automatic orbital shift': ureg.Quantity(0.1, 'eV'),
    'basis set definition': None,
    'basis set name': 'def-SV(P)',
    'closed-shell orbital shift': None,
    'damping adjustment step': None,
    'default eht atomic orbitals': None,
    'density convergence': None,
    'density functional': 'b-p',
    'energy convergence': None,
    'esp fit': None,
    # depend on 'use fermi smearing' -> maybe use lambda
    'fermi annealing factor': None,  # ureg.Quantity(0.95),
    'fermi final temperature': None,  # ureg.Quantity(300., 'kelvin'),
    'fermi homo-lumo gap criterion': None,  # ureg.Quantity(0.1, 'eV'),
    'fermi initial temperature': None,  # ureg.Quantity(300., 'kelvin'),
    'fermi stopping criterion': None,  # ureg.Quantity(0.001, 'eV'),
    #
    'force convergence': None,
    'geometry optimization iterations': None,
    'grid size': 'm3',
    'ground state': True,
    'initial damping': None,
    'initial guess': 'eht',
    'minimal damping': None,
    # 'multiplicity': None,
    'non-automatic orbital shift': False,
    'numerical hessian': None,
    'point group': 'c1',
    'ri memory': ureg.Quantity(1000, 'megabyte'),
    'rohf': None,
    'scf energy convergence': None,
    'scf iterations': 60,
    'task': 'energy',
    'title': '',
    'total charge': 0,
    'transition vector': None,
    'uhf': None,
    'use basis set library': True,
    'use dft': True,
    'use fermi smearing': False,
    'use redundant internals': False,
    'use resolution of identity': False,
}

# name 'lj' as accepted by get_calculator_class()
calc_pars['lj'] = {
    'sigma': ureg.Quantity(1.0, 'angstrom'),
    'epsilon': ureg.Quantity(1.0, 'eV'),
    'rc': None,
    'ro': None,
    'smooth': False,
}

# name 'lennardjones' as returned by lj.LennardJones().name
calc_pars['lennardjones'] = calc_pars['lj']

calc_pars['emt'] = {
    'restart': None,
    'asap_cutoff': False
}

calc_pars['free_electrons'] = {
    'restart': None,
    'kpts': ureg.Quantity(numpy.array([0, 0, 0])),
    'path': None,  # only as key in kpts
    'npoints': None,  # only as key in kpts
    'nvalence': ureg.Quantity(0),
    'nbands': ureg.Quantity(20),
    'gridsize': ureg.Quantity(7)
}
