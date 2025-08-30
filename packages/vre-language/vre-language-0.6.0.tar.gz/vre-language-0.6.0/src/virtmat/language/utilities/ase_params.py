"""
definitions of ASE calculators, algorithms with their parameters with
types, units, default values and outputs with types, units and default values
"""
import numbers
import math
import types
import numpy
import pandas
import pint
from virtmat.language.utilities.errors import RuntimeTypeError, InvalidUnitError
from virtmat.language.utilities.units import ureg
from virtmat.language.utilities.ase_tasks import calc_tasks
from virtmat.language.utilities.ase_units import calc_pars as calc_pars_units
from virtmat.language.utilities.ase_types import calc_pars as calc_pars_types
from virtmat.language.utilities.ase_defaults import calc_pars as calc_pars_defaults
from virtmat.language.utilities.ase_choices import calc_pars as calc_pars_choices
from virtmat.language.utilities.types import is_numeric_scalar, is_numeric_array
from virtmat.language.utilities.types import repr_type, scalar_booltype
from virtmat.language.utilities.lists import list_apply

spec = {
  'vasp': {
    'module': 'virtmat.language.utilities.ase_wrappers',
    'class': 'Vasp',
    'modulefile': {'name': 'vasp', 'verspec': '>=5.0.0'},
    'envvars': {'VASP_COMMAND': 'vasp_std'},
    'properties': ['energy', 'dipole', 'forces', 'stress', 'vibrational_energies',
                   'energy_minimum', 'transition_state', 'trajectory', 'magmom',
                   'magmoms']
  },
  'turbomole': {
    'module': 'ase.calculators.turbomole',
    'class': 'Turbomole',
    'modulefile': {'name': 'turbomole', 'verspec': '>=7.0'},
    'properties': ['energy', 'forces', 'vibrational_energies', 'energy_minimum',
                   'transition_state', 'dipole']
  },
  'lj': {
    'module': 'ase.calculators.lj',
    'class': 'LennardJones',
    'properties': ['energy', 'forces']
  },
  'lennardjones': {
    'module': 'ase.calculators.lj',
    'class': 'LennardJones',
    'properties': ['energy', 'forces']
  },
  'emt': {
    'module': 'ase.calculators.emt',
    'class': 'EMT',
    'properties': ['energy', 'forces', 'stress']
  },
  'free_electrons': {
    'module': 'ase.calculators.test',
    'class': 'FreeElectrons',
    'properties': ['energy', 'band_structure']
  },
  'BFGS': {
    'module': 'ase.optimize',
    'class': 'BFGS',
    'requires_dof': True,
    'many_to_one': False,
    'calc_task': ['single point', None],
    'properties': ['trajectory'],
    'params': {
      'steps': {
        'default': ureg.Quantity(100000000),
        'type': numbers.Integral,
        'units': 'dimensionless',
        'method': 'run',
      },
      'maxstep': {
        'default': ureg.Quantity(0.2, 'angstrom'),
        'type': numbers.Real,
        'units': 'angstrom',
        'method': 'class',
      },
      'trajectory': {
        'default': None,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'logfile': {
        'default': None,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'interval': {
        'default': ureg.Quantity(1),
        'type': numbers.Integral,
        'units': 'dimensionless',
        'method': 'class',
      },
      'fmax': {
        'default': ureg.Quantity(0.05, 'eV / angstrom'),
        'type': numbers.Real,
        'units': 'eV / angstrom',
        'method': 'run',
      },
      'alpha': {
        'default': ureg.Quantity(70.0, 'eV * angstrom ** (-2)'),
        'type': numbers.Real,
        'units': 'eV * angstrom ** (-2)',
        'method': 'class',
      },
    }
  },
  'LBFGS': {
    'module': 'ase.optimize',
    'class': 'LBFGS',
    'requires_dof': True,
    'many_to_one': False,
    'calc_task': ['single point', None],
    'properties': ['trajectory'],
    'params': {
      'steps': {
        'default': ureg.Quantity(100000000),
        'type': numbers.Integral,
        'units': 'dimensionless',
        'method': 'run',
      },
      'maxstep': {
        'default': ureg.Quantity(0.2, 'angstrom'),
        'type': numbers.Real,
        'units': 'angstrom',
        'method': 'class',
      },
      'trajectory': {
        'default': None,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'logfile': {
        'default': None,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'interval': {
        'default': ureg.Quantity(1),
        'type': numbers.Integral,
        'units': 'dimensionless',
        'method': 'class',
      },
      'fmax': {
        'default': ureg.Quantity(0.05, 'eV / angstrom'),
        'type': numbers.Real,
        'units': 'eV / angstrom',
        'method': 'run',
      },
      'memory': {
        'default': ureg.Quantity(100),
        'type': numbers.Integral,
        'units': 'dimensionless',
        'method': 'class',
      },
      'damping': {
        'default': ureg.Quantity(1.0),
        'type': numbers.Real,
        'units': 'dimensionless',
        'method': 'class',
      },
      'alpha': {
        'default': ureg.Quantity(70.0, 'eV * angstrom ** (-2)'),
        'type': numbers.Real,
        'units': 'eV * angstrom ** (-2)',
        'method': 'class',
      },
    }
  },
  'LBFGSLineSearch': {
    'module': 'ase.optimize',
    'class': 'LBFGSLineSearch',
    'requires_dof': True,
    'many_to_one': False,
    'calc_task': ['single point', None],
    'properties': ['trajectory'],
    'params': {
      'steps': {
        'default': ureg.Quantity(100000000),
        'type': numbers.Integral,
        'units': 'dimensionless',
        'method': 'run',
      },
      'maxstep': {
        'default': ureg.Quantity(0.2, 'angstrom'),
        'type': numbers.Real,
        'units': 'angstrom',
        'method': 'class',
      },
      'trajectory': {
        'default': None,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'logfile': {
        'default': None,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'interval': {
        'default': ureg.Quantity(1),
        'type': numbers.Integral,
        'units': 'dimensionless',
        'method': 'class',
      },
      'fmax': {
        'default': ureg.Quantity(0.05, 'eV / angstrom'),
        'type': numbers.Real,
        'units': 'eV / angstrom',
        'method': 'run',
      },
      'memory': {
        'default': ureg.Quantity(100),
        'type': numbers.Integral,
        'units': 'dimensionless',
        'method': 'class',
      },
      'damping': {
        'default': ureg.Quantity(1.0),
        'type': numbers.Real,
        'units': 'dimensionless',
        'method': 'class',
      },
      'alpha': {
        'default': ureg.Quantity(70.0, 'eV * angstrom ** (-2)'),
        'type': numbers.Real,
        'units': 'eV * angstrom ** (-2)',
        'method': 'class',
      },
    }
  },
  'QuasiNewton': {
    'module': 'ase.optimize',
    'class': 'QuasiNewton',
    'requires_dof': True,
    'many_to_one': False,
    'calc_task': ['single point', None],
    'properties': ['trajectory'],
    'params': {
      'steps': {
        'default': ureg.Quantity(100000000),
        'type': numbers.Integral,
        'units': 'dimensionless',
        'method': 'run',
      },
      'maxstep': {
        'default': ureg.Quantity(0.2, 'angstrom'),
        'type': numbers.Real,
        'units': 'angstrom',
        'method': 'class',
      },
      'trajectory': {
        'default': None,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'logfile': {
        'default': None,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'interval': {
        'default': ureg.Quantity(1),
        'type': numbers.Integral,
        'units': 'dimensionless',
        'method': 'class',
      },
      'fmax': {
        'default': ureg.Quantity(0.05, 'eV / angstrom'),
        'type': numbers.Real,
        'units': 'eV / angstrom',
        'method': 'run',
      },
    }
  },
  'BFGSLineSearch': {
    'module': 'ase.optimize',
    'class': 'BFGSLineSearch',
    'requires_dof': True,
    'many_to_one': False,
    'calc_task': ['single point', None],
    'properties': ['trajectory'],
    'params': {
      'steps': {
        'default': ureg.Quantity(100000000),
        'type': numbers.Integral,
        'units': 'dimensionless',
        'method': 'run',
      },
      'maxstep': {
        'default': ureg.Quantity(0.2, 'angstrom'),
        'type': numbers.Real,
        'units': 'angstrom',
        'method': 'class',
      },
      'trajectory': {
        'default': None,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'logfile': {
        'default': None,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'interval': {
        'default': ureg.Quantity(1),
        'type': numbers.Integral,
        'units': 'dimensionless',
        'method': 'class',
      },
      'fmax': {
        'default': ureg.Quantity(0.05, 'eV / angstrom'),
        'type': numbers.Real,
        'units': 'eV / angstrom',
        'method': 'run',
      },
    }
  },
  'GPMin': {
    'module': 'ase.optimize',
    'class': 'GPMin',
    'requires_dof': True,
    'many_to_one': False,
    'calc_task': ['single point', None],
    'properties': ['trajectory'],
    'params': {
      'steps': {
        'default': ureg.Quantity(100000000),
        'type': numbers.Integral,
        'units': 'dimensionless',
        'method': 'class',
      },
      'trajectory': {
        'default': None,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'logfile': {
        'default': None,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'interval': {
        'default': ureg.Quantity(1),
        'type': numbers.Integral,
        'units': 'dimensionless',
        'method': 'class',
      },
      'fmax': {
        'default': ureg.Quantity(0.05, 'eV / angstrom'),
        'type': numbers.Real,
        'units': 'eV / angstrom',
        'method': 'run',
      },
      'prior': {
        'default': None,
        'type': object,
        'units': None,
        'method': 'class',
      },
      'kernel': {
        'default': None,
        'type': object,
        'units': None,
        'method': 'class',
      },
      'update_prior_strategy': {
        'default': 'maximum',
        'choices': ['maximum', 'init', 'average'],
        'type': str,
        'units': None,
        'method': 'class',
      },
      'update_hyperparams': {
        'default': False,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'noise': {
        'default': ureg.Quantity(0.005),
        'type': numbers.Real,
        'units': 'dimensionless',
        'method': 'class',
      },
      'weight': {
        'default': ureg.Quantity(1.0),
        'type': numbers.Real,
        'units': 'dimensionless',
        'method': 'class',
      },
      'scale': {
        'default': ureg.Quantity(0.4),
        'type': numbers.Real,
        'units': 'dimensionless',
        'method': 'class',
      },
    }
  },
  'FIRE': {
    'module': 'ase.optimize',
    'class': 'FIRE',
    'requires_dof': True,
    'many_to_one': False,
    'calc_task': ['single point', None],
    'properties': ['trajectory'],
    'params': {
      'steps': {
        'default': ureg.Quantity(100000000),
        'type': numbers.Integral,
        'units': 'dimensionless',
        'method': 'run',
      },
      'maxstep': {
        'default': ureg.Quantity(0.2, 'angstrom'),
        'type': numbers.Real,
        'units': 'angstrom',
        'method': 'class',
      },
      'trajectory': {
        'default': None,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'logfile': {
        'default': None,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'interval': {
        'default': ureg.Quantity(1),
        'type': numbers.Integral,
        'units': 'dimensionless',
        'method': 'class',
      },
      'fmax': {
        'default': ureg.Quantity(0.05, 'eV / angstrom'),
        'type': numbers.Real,
        'units': 'eV / angstrom',
        'method': 'run',
      },
      'dt': {
        'default': ureg.Quantity(0.1, 'angstrom * (amu / eV ) ** (1/2)'),
        'type': numbers.Real,
        'units': 'angstrom * (amu / eV ) ** (1/2)',
        'method': 'class',
      },
      'dtmax': {
        'default': ureg.Quantity(1.0, 'angstrom * (amu / eV ) ** (1/2)'),
        'type': numbers.Real,
        'units': 'angstrom * (amu / eV ) ** (1/2)',
        'method': 'class',
      },
      'downhill_check': {
        'default': False,
        'type': bool,
        'units': None,
        'method': 'class',
      },
    }
  },  # nb: 8 non-documented init parameters in FIRE: no explanation/no units
  'MDMin': {
    'module': 'ase.optimize',
    'class': 'MDMin',
    'requires_dof': True,
    'many_to_one': False,
    'calc_task': ['single point', None],
    'properties': ['trajectory'],
    'params': {
      'steps': {
        'default': ureg.Quantity(100000000),
        'type': numbers.Integral,
        'units': 'dimensionless',
        'method': 'run',
      },
      'maxstep': {
        'default': ureg.Quantity(0.2, 'angstrom'),
        'type': numbers.Real,
        'units': 'angstrom',
        'method': 'class',
      },
      'trajectory': {
        'default': None,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'logfile': {
        'default': None,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'interval': {
        'default': ureg.Quantity(1),
        'type': numbers.Integral,
        'units': 'dimensionless',
        'method': 'class',
      },
      'fmax': {
        'default': ureg.Quantity(0.05, 'eV / angstrom'),
        'type': numbers.Real,
        'units': 'eV / angstrom',
        'method': 'run',
      },
      'dt': {
        'default': ureg.Quantity(0.2, 'angstrom * (amu / eV ) ** (1/2)'),
        'type': numbers.Real,
        'units': 'angstrom * (amu / eV ) ** (1/2)',
        'method': 'class',
      },
    }
  },
  'RMSD': {
    'module': 'virtmat.language.utilities.ase_wrappers',
    'class': 'RMSD',
    'requires_dof': True,
    'many_to_one': None,
    'properties': ['rmsd'],
    'params': {
      'reference': {
        'type': object,  # cannot be checked, always true
        'units': None,
        'method': 'run'
      },
      'adjust': {
        'default': True,
        'type': bool,
        'units': None,
        'method': 'run'
      },
    }
  },
  'RDF': {
    'module': 'virtmat.language.utilities.ase_wrappers',
    'class': 'RDF',
    'requires_dof': False,
    'many_to_one': None,
    'properties': ['rdf_distance', 'rdf'],
    'params': {
      'rmax': {
        'default': None,
        'type': numbers.Real,
        'units': 'angstrom',
        'method': 'run'
      },
      'nbins': {
        'default': ureg.Quantity(40),
        'type': numbers.Integral,
        'units': 'dimensionless',
        'method': 'run'
      },
      'neighborlist': {
        'default': None,
        'type': pandas.DataFrame,
        'otype': 'algorithm',
        'units': None,
        'method': 'run'
      },
      'elements': {
        'default': None,
        'type': str,
        'units': None,
        'method': 'run'
      }
    }
  },
  'VelocityDistribution': {
    'module': 'virtmat.language.utilities.ase_wrappers',
    'class': 'VelocityDistribution',
    'requires_dof': False,
    'many_to_one': None,
    'properties': ['vdf', 'velocity'],
    'params': {
      'distribution': {
        'default': 'maxwell-boltzmann',  # phonon_harmonics not implemented
        'choices': ['maxwell-boltzmann', 'phonon_harmonics'],
        'type': str,
        'units': None,
        'method': 'class'
      },
      'temperature_K': {
        'type': numbers.Real,
        'units': 'kelvin',
        'method': 'class'
      },
      'force_temp': {
        'default': False,
        'type': bool,
        'units': None,
        'method': 'class'
      },
      'stationary': {
        'default': True,
        'type': bool,
        'units': None,
        'method': 'run'
      },
      'zero_rotation': {
        'default': True,
        'type': bool,
        'units': None,
        'method': 'run'
      },
      'preserve_temperature': {
        'default': True,
        'type': bool,
        'units': None,
        'method': 'run'
      },
      'nbins': {
        'default': ureg.Quantity(40),
        'type': numbers.Integral,
        'units': 'dimensionless',
        'method': 'run'
      },
    }
  },
  'EquationOfState': {
    'module': 'virtmat.language.utilities.ase_wrappers',
    'class': 'EOS',
    'requires_dof': False,
    'many_to_one': True,
    'properties': ['minimum_energy', 'optimal_volume', 'bulk_modulus',
                   'eos_volume', 'eos_energy'],
    'params': {
      'energies': {
        'default': None,
        'type': numpy.ndarray,
        'units': 'eV',
        'method': 'run'
      },
      'eos': {
        'default': 'sjeos',
        'choices': ['sjeos', 'taylor', 'murnaghan', 'birch', 'birchmurnaghan',
                    'pouriertarantola', 'vinet', 'antonschmidt', 'p3'],
        'type': str,
        'units': None,
        'method': 'run'
      },
      'filename': {
        'default': None,
        'type': str,
        'units': None,
        'method': 'run'
      }
    }
  },
  'DensityOfStates': {
    'module': 'virtmat.language.utilities.ase_wrappers',
    'class': 'DensityOfStates',
    'requires_dof': False,
    'many_to_one': False,
    'calc_task': ['single point', None],
    'properties': ['dos_energy', 'dos'],
    'params': {
      'width': {
        'default': ureg.Quantity(0.1, 'eV'),
        'type': numbers.Real,
        'units': 'eV',
        'method': 'run'
      },
      'window': {
        'default': None,
        'type': numpy.ndarray,
        'units': 'eV',
        'method': 'run'
      },
      'npts': {
        'default': ureg.Quantity(401),
        'type': numbers.Integral,
        'units': 'dimensionless',
        'method': 'run'
      },
      'spin': {
        'default': None,
        'choices': [None, 0, 1],
        'type': numbers.Integral,
        'units': 'dimensionless',
        'method': 'run'
      },
    }
  },
  'BandStructure': {
    'module': 'virtmat.language.utilities.ase_wrappers',
    'class': 'BandStructure',
    'requires_dof': False,
    'many_to_one': False,
    'calc_task': ['single point', None],
    'properties': ['band_structure'],
    'params': {
      'emin': {
        'default': None,
        'type': numbers.Real,
        'units': 'eV',
        'method': 'run'
      },
      'emax': {
        'default': None,
        'type': numbers.Real,
        'units': 'eV',
        'method': 'run'
      },
      'filename': {
        'default': None,
        'type': str,
        'units': 'None',
        'method': 'run'
      }
    }
  },
  'VelocityVerlet': {
    'module': 'ase.md.verlet',
    'class': 'VelocityVerlet',
    'requires_dof': True,
    'many_to_one': False,
    'calc_task': ['single point', None],
    'properties': ['trajectory'],
    'params': {
      'steps': {
        'default': ureg.Quantity(50),
        'type': numbers.Integral,
        'units': 'dimensionless',
        'method': 'run',
      },
      'logfile': {
        'default': None,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'trajectory': {
        'default': None,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'interval': {
        'default': ureg.Quantity(1),
        'type': numbers.Integral,
        'units': 'dimensionless',
        'method': 'class',
      },
      'timestep': {
        'type': numbers.Real,
        'units': 'angstrom * (amu / eV ) ** (1/2)',
        'method': 'class',
      },
    }
  },
  'Langevin': {
    'module': 'ase.md.langevin',
    'class': 'Langevin',
    'requires_dof': True,
    'many_to_one': False,
    'calc_task': ['single point', None],
    'properties': ['trajectory'],
    'params': {
      'steps': {
        'default': ureg.Quantity(50),
        'type': numbers.Integral,
        'units': 'dimensionless',
        'method': 'run',
      },
      'logfile': {
        'default': None,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'trajectory': {
        'default': None,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'interval': {
        'default': ureg.Quantity(1),
        'type': numbers.Integral,
        'units': 'dimensionless',
        'method': 'class',
      },
      'timestep': {
        'type': numbers.Real,
        'units': 'angstrom * (amu / eV ) ** (1/2)',
        'method': 'class',
      },
      'temperature_K': {
        'type': numbers.Real,
        'units': 'K',
        'method': 'class',
      },
      'friction': {
        'type': numbers.Real,
        'units': 'angstrom ** (-1) * (amu / eV ) ** (-1/2)',
        'method': 'class',
      },
      'fixcm': {
        'default': True,
        'type': bool,
        'units': None,
        'method': 'class',
      },
    }
  },
  'NPT': {
    'module': 'ase.md.npt',
    'class': 'NPT',
    'requires_dof': True,
    'many_to_one': False,
    'calc_task': ['single point', None],
    'properties': ['trajectory'],
    'params': {
      'steps': {
        'default': ureg.Quantity(50),
        'type': numbers.Integral,
        'units': 'dimensionless',
        'method': 'run',
      },
      'logfile': {
        'default': None,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'trajectory': {
        'default': None,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'interval': {
        'default': ureg.Quantity(1),
        'type': numbers.Integral,
        'units': 'dimensionless',
        'method': 'class',
      },
      'timestep': {
        'type': numbers.Real,
        'units': 'angstrom * (amu / eV ) ** (1/2)',
        'method': 'class',
      },
      'temperature_K': {
        'type': numbers.Real,
        'units': 'K',
        'method': 'class',
      },
      'externalstress': {
        'type': numbers.Real,
        'units': 'eV / (angstrom ** 3)',
        'method': 'class',
      },
      'ttime': {
        'type': numbers.Real,
        'units': 'angstrom * (amu / eV ) ** (1/2)',
        'method': 'class',
      },
      'pfactor': {
        'type': numbers.Real,
        'units': 'amu  / angstrom',
        'method': 'class',
      },
    }
  },
  'Andersen': {
    'module': 'ase.md.andersen',
    'class': 'Andersen',
    'requires_dof': True,
    'many_to_one': False,
    'calc_task': ['single point', None],
    'properties': ['trajectory'],
    'params': {
      'steps': {
        'default': ureg.Quantity(50),
        'type': numbers.Integral,
        'units': 'dimensionless',
        'method': 'run',
      },
      'logfile': {
        'default': None,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'trajectory': {
        'default': None,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'interval': {
        'default': ureg.Quantity(1),
        'type': numbers.Integral,
        'units': 'dimensionless',
        'method': 'class',
      },
      'timestep': {
        'type': numbers.Real,
        'units': 'angstrom * (amu / eV ) ** (1/2)',
        'method': 'class',
      },
      'temperature_K': {
        'type': numbers.Real,
        'units': 'K',
        'method': 'class',
      },
      'andersen_prob': {
        'type': numbers.Real,
        'units': 'dimensionless',
        'method': 'class',
      },
      'fixcm': {
        'default': True,
        'type': bool,
        'units': None,
        'method': 'class',
      },
    }
  },
  'NVTBerendsen': {
    'module': 'ase.md.nvtberendsen',
    'class': 'NVTBerendsen',
    'requires_dof': True,
    'many_to_one': False,
    'calc_task': ['single point', None],
    'properties': ['trajectory'],
    'params': {
      'steps': {
        'default': ureg.Quantity(50),
        'type': numbers.Integral,
        'units': 'dimensionless',
        'method': 'run',
      },
      'logfile': {
        'default': None,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'trajectory': {
        'default': None,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'interval': {
        'default': ureg.Quantity(1),
        'type': numbers.Integral,
        'units': 'dimensionless',
        'method': 'class',
      },
      'timestep': {
        'type': numbers.Real,
        'units': 'angstrom * (amu / eV ) ** (1/2)',
        'method': 'class',
      },
      'temperature_K': {
        'type': numbers.Real,
        'units': 'K',
        'method': 'class',
      },
      'taut': {
        'type': numbers.Real,
        'units': 'angstrom * (amu / eV ) ** (1/2)',
        'method': 'class',
      },
      'fixcm': {
        'default': True,
        'type': bool,
        'units': None,
        'method': 'class',
      },
    }
  },
  'NPTBerendsen': {
    'module': 'ase.md.nptberendsen',
    'class': 'NPTBerendsen',
    'requires_dof': True,
    'many_to_one': False,
    'calc_task': ['single point', None],
    'properties': ['trajectory'],
    'params': {
      'steps': {
        'default': ureg.Quantity(50),
        'type': numbers.Integral,
        'units': 'dimensionless',
        'method': 'run',
      },
      'logfile': {
        'default': None,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'trajectory': {
        'default': None,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'interval': {
        'default': ureg.Quantity(1),
        'type': numbers.Integral,
        'units': 'dimensionless',
        'method': 'class',
      },
      'timestep': {
        'type': numbers.Real,
        'units': 'angstrom * (amu / eV ) ** (1/2)',
        'method': 'class',
      },
      'temperature_K': {
        'type': numbers.Real,
        'units': 'K',
        'method': 'class',
      },
      'pressure_au': {
        'type': numbers.Real,
        'units': 'eV / (angstrom ** 3)',
        'method': 'class',
      },
      'taut': {
        'default': ureg.Quantity(0.5, 'ps'),
        'type': numbers.Real,
        'units': 'angstrom * (amu / eV ) ** (1/2)',
        'method': 'class',
      },
      'taup': {
        'default': ureg.Quantity(1.0, 'ps'),
        'type': numbers.Real,
        'units': 'angstrom * (amu / eV ) ** (1/2)',
        'method': 'class',
      },
      'compressibility_au': {
        'type': numbers.Real,
        'units': 'angstrom ** 3 / eV',
        'method': 'class',
      },
      'fixcm': {
        'default': True,
        'type': bool,
        'units': None,
        'method': 'class',
      },
    }
  },
  'NEB': {
    'module': 'virtmat.language.utilities.ase_wrappers',
    'class': 'NudgedElasticBand',
    'requires_dof': True,
    'many_to_one': True,
    'calc_task': ['single point', None],
    'properties': ['energy', 'forces', 'activation_energy', 'reaction_energy',
                   'maximum_force', 'trajectory'],
    'params': {
      'number_of_images': {
        'default': ureg.Quantity(3),
        'type': numbers.Integral,
        'units': 'dimensionless',
        'method': 'class',
      },
      'trajectory': {
        'default': True,
        'choices': [True],
        'type': bool,
        'units': None,
        'method': 'run',
      },
      'logfile': {
        'default': None,
        'type': bool,
        'units': None,
        'method': 'run',
      },
      'interpolate_method': {
        'default': 'linear',
        'choices': ['linear', 'idpp'],
        'type': str,
        'units': None,
        'method': 'class',
      },
      'interpolate_mic': {
        'default': False,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'dynamic_relaxation': {
        'default': False,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'fmax': {
        'default': ureg.Quantity(0.05, 'eV/angstrom'),
        'type': numbers.Real,
        'units': 'eV/angstrom',
        'method': 'class',
      },
      'scale_fmax': {
        'default': ureg.Quantity(0.0, '1/angstrom'),
        'type': numbers.Real,
        'units': '1/angstrom',
        'method': 'class',
      },
      'k': {
        'default': ureg.Quantity(0.1, 'eV/angstrom'),
        'type': numbers.Real,
        'units': 'eV/angstrom',
        'method': 'class',
      },
      'climb': {
        'default': False,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'remove_rotation_and_translation': {
        'default': False,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'method': {
        'default': 'aseneb',
        'choices': ['aseneb', 'improvedtangent', 'eb', 'spline', 'string'],
        'type': str,
        'units': None,
        'method': 'class',
      },
      'optimizer': {
        'type': pandas.DataFrame,
        'otype': 'algorithm',
        'units': None,
        'method': 'run',
      },
      'fit': {
        'default': False,
        'type': bool,
        'units': None,
        'method': 'run',
      },
      'filename': {
        'default': None,
        'type': str,
        'units': None,
        'method': 'run'
      }
    }
  },
  'Dimer': {
    'module': 'virtmat.language.utilities.ase_wrappers',
    'class': 'Dimer',
    'requires_dof': True,
    'many_to_one': False,
    'calc_task': ['single point', None],
    'properties': ['energy', 'forces', 'activation_energy', 'reaction_energy',
                   'maximum_force', 'trajectory'],
    'params': {
      'trajectory': {
        'default': None,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'logfile': {
        'default': None,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'eigenmode_logfile': {
        'default': None,
        'type': str,
        'units': None,
        'method': 'class',
      },
      'eigenmode_method': {
        'default': 'dimer',
        'choices': ['dimer'],
        'type': str,
        'units': None,
        'method': 'class',
      },
      'f_rot_min': {
        'default': ureg.Quantity(0.1, 'eV/angstrom'),
        'type': numbers.Real,
        'units': 'eV/angstrom',
        'method': 'class',
      },
      'f_rot_max': {
        'default': ureg.Quantity(1.0, 'eV/angstrom'),
        'type': numbers.Real,
        'units': 'eV/angstrom',
        'method': 'class',
      },
      'max_num_rot': {
        'default': ureg.Quantity(1),
        'type': numbers.Integral,
        'units': 'dimensionless',
        'method': 'class',
      },
      'trial_angle': {
        'default': ureg.Quantity(math.pi/4.0, 'radians'),
        'type': numbers.Real,
        'units': 'radians',
        'method': 'class',
      },
      'trial_trans_step': {
        'default': ureg.Quantity(0.001, 'angstrom'),
        'type': numbers.Real,
        'units': 'angstrom',
        'method': 'class',
      },
      'maximum_translation': {
        'default': ureg.Quantity(0.1, 'angstrom'),
        'type': numbers.Real,
        'units': 'angstrom',
        'method': 'class',
      },
      'cg_translation': {
        'default': True,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'use_central_forces': {
        'default': True,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'dimer_separation': {
        'default': ureg.Quantity(0.0001, 'angstrom'),
        'type': numbers.Real,
        'units': 'angstrom',
        'method': 'class',
      },
      'initial_eigenmode_method': {
        'default': 'gauss',
        'choices': ['gauss', 'displacement'],
        'type': str,
        'units': None,
        'method': 'class',
      },
      'extrapolate_forces': {
        'default': False,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'displacement_method': {
        'default': 'gauss',
        'choices': ['gauss', 'vector'],
        'type': str,
        'units': None,
        'method': 'class',
      },
      'gauss_std': {
        'default': ureg.Quantity(0.1, 'angstrom'),
        'type': numbers.Real,
        'units': 'angstrom',
        'method': 'class',
      },
      'order': {
        'default': ureg.Quantity(1),
        'type': numbers.Integral,
        'units': 'dimensionless',
        'method': 'class',
      },
      'mask': {
        'default': None,
        'type': numpy.ndarray,
        'units': None,
        'method': 'class',
      },
      'displacement_center': {
          'default': None,
          'type': numpy.ndarray,
          'units': 'angstrom',
          'method': 'class'
      },
      'displacement_radius': {
          'default': None,
          'type': numbers.Real,
          'units': 'angstrom',
          'method': 'class'
      },
      'number_of_displacement_atoms': {
          'default': None,
          'type': numbers.Integral,
          'units': 'dimensionless',
          'method': 'class'
      },
      'target': {
        'default': None,
        'type': object,  # cannot be checked, always true
        'units': None,
        'method': 'class',
      },
      'fmax': {
        'default': ureg.Quantity(0.05, 'eV / angstrom'),
        'type': numbers.Real,
        'units': 'eV / angstrom',
        'method': 'run',
      },
    }
  },
  'Vibrations': {
    'module': 'virtmat.language.utilities.ase_wrappers',
    'class': 'VibrationsWrapper',
    'requires_dof': True,
    'many_to_one': False,
    'calc_task': ['single point', None],
    'properties': ['hessian', 'vibrational_energies', 'vibrational_modes',
                   'energy_minimum', 'transition_state'],
    'params': {
      'delta': {
        'default': ureg.Quantity(0.01, 'angstrom'),
        'type': numbers.Real,
        'units': 'angstrom',
        'method': 'class',
      },
      'nfree': {
        'default': ureg.Quantity(2),
        'type': numbers.Integral,
        'units': 'dimensionless',
        'method': 'class',
      },
      'method': {
        'default': 'standard',
        'choices': ['standard', 'frederiksen'],
        'type': str,
        'units': None,
        'method': 'run',
      },
      'direction': {
        'default': 'central',
        'choices': ['central', 'forward', 'backward'],
        'type': str,
        'units': None,
        'method': 'run',
      },
      'all_atoms': {
        'default': False,
        'type': bool,
        'units': None,
        'method': 'run',
      },
      'imag_tol': {
        'default': ureg.Quantity(1e-5, 'eV'),
        'type': numbers.Real,
        'units': 'eV',
        'method': 'run',
      },
    }
  },
  'NeighborList': {
    'module': 'virtmat.language.utilities.ase_wrappers',
    'class': 'NeighborListWrapper',
    'requires_dof': False,
    'many_to_one': False,
    'properties': ['neighbors', 'neighbor_offsets', 'connectivity_matrix',
                   'connected_components'],
    'params': {
      'cutoffs': {
        'default': None,
        'type': numpy.ndarray,
        'units': 'angstrom',
        'method': 'class',
      },
      'skin': {
        'default': ureg.Quantity(0.3, 'angstrom'),
        'type': numbers.Real,
        'units': 'angstrom',
        'method': 'class',
      },
      'sorted': {
        'default': False,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'self_interaction': {
        'default': True,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'bothways': {
        'default': False,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'method': {
        'default': 'quadratic',
        'choices': ['quadratic', 'linear'],
        'type': str,
        'units': None,
        'method': 'class',
      },
    }
  },
}

for calc in ('vasp', 'turbomole', 'lj', 'lennardjones', 'emt', 'free_electrons'):
    spec[calc]['params'] = {}
    spec[calc]['tasks'] = calc_tasks[calc]
    for key in calc_pars_units[calc].keys():
        _par = {'units': calc_pars_units[calc][key], 'type': calc_pars_types[calc][key]}
        if calc in calc_pars_defaults and key in calc_pars_defaults[calc]:
            _par['default'] = calc_pars_defaults[calc][key]
        if calc in calc_pars_choices and key in calc_pars_choices[calc]:
            _par['choices'] = calc_pars_choices[calc][key]
        spec[calc]['params'][key] = _par

par_units = {c: {k: v['units'] for k, v in u['params'].items()} for c, u in spec.items()}


def check_params_types(name, parameters):
    """check types of calculator and algorithm parameters (dynamic check)"""
    for par_ in parameters.columns:
        ptype = spec[name]['params'][par_]['type']
        if isinstance(ptype, tuple):
            ptype_r = ' or '.join(repr_type(t) for t in ptype)
        else:
            ptype_r = repr_type(ptype)
        msg = f'invalid parameter type in method \"{name}\": \"{par_}\" must be {ptype_r}'
        if not any(v is None for v in parameters[par_]):
            for val in parameters[par_]:
                if is_numeric_scalar(val) or is_numeric_array(val):
                    if not isinstance(val.magnitude, ptype):
                        raise RuntimeTypeError(msg)
                elif isinstance(val, scalar_booltype):
                    if isinstance(ptype, tuple):
                        if bool not in ptype:
                            raise RuntimeTypeError(msg)
                    elif ptype is not bool:
                        raise RuntimeTypeError(msg)
                elif not isinstance(val, ptype):
                    raise RuntimeTypeError(msg)


def get_par_units(name, par, val):
    """auxiliary function to get the units of a calculator parameter"""
    params = par_units[name]
    try:
        par_def = params[par]
    except KeyError as err:
        msg = f'parameter \"{par}\" has unknown units'
        raise InvalidUnitError(msg) from err
    if isinstance(par_def, types.FunctionType):
        return par_def(val)
    return par_def


def get_params_units(calc_name, params):
    """auxiliary function to get the units for a parameters dictionary"""
    units = {}
    for param, value in params.items():
        r_units = get_par_units(calc_name, param, value)
        if isinstance(r_units, list):
            r_units = [r(params) for r in r_units]
            r_units = next(r for r in r_units if r is not None)
        units[param] = r_units
    return units


def get_params_magnitudes(calc_params, calc_name):
    """converts parameters to canonical units and return their magnitudes"""

    def magnitudes_from_list(unit, value):
        return list_apply(lambda x: x.to(unit).magnitude, value)

    units = get_params_units(calc_name, calc_params)

    magnitudes = {}
    for par, val in calc_params.items():
        try:
            if isinstance(val, ureg.Quantity):
                magnitudes[par] = val.to(units[par]).magnitude
            elif isinstance(val, numpy.ndarray):
                if issubclass(val.dtype.type, (numpy.bool_, numpy.str_)):
                    magnitudes[par] = val
                else:
                    assert issubclass(val.dtype.type, numpy.object_)
                    magnitudes[par] = magnitudes_from_list(units[par], val.tolist())
            elif isinstance(val, pandas.DataFrame):
                assert issubclass(pandas.DataFrame, spec[calc_name]['params'][par]['type'])
                if len(val) == 1:
                    dct = dict(next(val.iterrows())[1])
                    if ('otype' in spec[calc_name]['params'][par] and
                       spec[calc_name]['params'][par]['otype'] == 'algorithm'):
                        if 'parameters' in dct and dct['parameters'] is not None:
                            dct_ = dict(next(dct['parameters'].iterrows())[1])
                        else:
                            dct_ = {}
                        dct['parameters'] = get_params_magnitudes(dct_, dct['name'])
                        magnitudes[par] = dct
                    else:
                        magnitudes[par] = get_params_magnitudes(dct, calc_name)
                else:
                    assert len(val) == 0
                    magnitudes[par] = {}
            else:
                magnitudes[par] = val
        except pint.DimensionalityError as err:
            msg = (f'error with units of parameter \"{par}\": '
                   f'must be [{units[par]}] instead of [{val.units}]')
            raise InvalidUnitError(msg) from err
    return magnitudes


def check_params_units(name, parameters):
    """check units of calculator and algorithm parameters (dynamic check)"""
    for _, row in parameters.iterrows():
        get_params_magnitudes(dict(row), name)
