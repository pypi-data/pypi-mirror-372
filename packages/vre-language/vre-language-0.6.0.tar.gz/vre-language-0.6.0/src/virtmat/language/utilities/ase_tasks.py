"""task and corresponding properties used in ASE calculators"""

calc_tasks = {}

calc_tasks['vasp'] = {
  'single point': {'ibrion': lambda x: x in [-1, None], 'nsw': lambda x: x in [-1, 0, None]},
  'local minimum': {'ibrion': lambda x: x in [1, 2, 3]},
  'transition state': {'ibrion': lambda x: x in [40, 44]},
  'normal modes': {'ibrion': lambda x: x in [5, 6, 7, 8]},
  'micro-canonical': {'ibrion': lambda x: x == 0, 'potim': lambda x: x is not None,
                      'nsw': lambda x: x is not None, 'mdalgo': lambda x: x == 0,
                      'smass': lambda x: x == -3, 'andersen_prob': lambda x: x == 0.0},
  'canonical': {'ibrion': lambda x: x == 0, 'potim': lambda x: x is not None,
                'nsw': lambda x: x is not None, 'mdalgo': lambda x: x in [1, 2, 3, 4, 5, 13],
                'isif': lambda x: x == 2},
  'isothermal-isobaric': {'ibrion': lambda x: x == 0, 'potim': lambda x: x is not None,
                          'nsw': lambda x: x is not None, 'mdalgo': lambda x: x == 3,
                          'isif': lambda x: x == 3}
}

calc_tasks['turbomole'] = {
  'single point': {'task': lambda x: x in ['energy', 'gradient']},
  'local minimum': {'task': lambda x: x == 'optimize'},
  'transition state': {'task': lambda x: x == 'optimize'},
  'normal modes': {'task': lambda x: x == 'frequencies'},
}

calc_tasks['lj'] = {
  'single point': {}
}

calc_tasks['lennardjones'] = calc_tasks['lj']

calc_tasks['emt'] = {
  'single point': {}
}

calc_tasks['free_electrons'] = {
  'single point': {}
}
