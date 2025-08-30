"""Custom classes for the AMML objects"""
import importlib
import inspect
import itertools
from dataclasses import dataclass
from functools import cached_property
from copy import deepcopy
import numpy
import pandas
import pint_pandas
from pint_pandas import PintType
import ase
import ase.constraints
from ase.io import write, jsonio
from ase.geometry import wrap_positions
from ase.calculators.singlepoint import SinglePointCalculator
from ase.calculators.calculator import all_changes
from ase.io.trajectory import TrajectoryReader
from virtmat.language.utilities.ase_handlers import get_ase_property
from virtmat.language.utilities.ase_params import spec, check_params_types
from virtmat.language.utilities.ase_params import get_params_units, check_params_units
from virtmat.language.utilities.ase_params import get_params_magnitudes
from virtmat.language.utilities.errors import RuntimeValueError, PropertyError
from virtmat.language.utilities.errors import ConvergenceError
from virtmat.language.utilities.errors import StructureInputError
from virtmat.language.utilities.units import ureg, get_pint_series
from virtmat.language.utilities.lists import list_flatten
from virtmat.language.utilities.formatters import formatter
from virtmat.language.utilities.ioops import get_uuid_filename

pint_pandas.pint_array.DEFAULT_SUBDTYPE = None


def get_structure_dataframe(atoms):
    """create a structure dataframe from an ASE Atoms object"""
    lunit = pint_pandas.PintType('angstrom')
    munit = pint_pandas.PintType('amu')
    punit = pint_pandas.PintType('( amu * eV ) ** (1/2)')
    tunit = pint_pandas.PintType('dimensionless')

    symb = pandas.Series(atoms.get_chemical_symbols(), name='symbols')
    post = atoms.get_positions().transpose()
    posx = pandas.Series(pint_pandas.PintArray(post[0], dtype=lunit), name='x')
    posy = pandas.Series(pint_pandas.PintArray(post[1], dtype=lunit), name='y')
    posz = pandas.Series(pint_pandas.PintArray(post[2], dtype=lunit), name='z')
    momt = atoms.get_momenta().transpose()
    momx = pandas.Series(pint_pandas.PintArray(momt[0], dtype=punit), name='px')
    momy = pandas.Series(pint_pandas.PintArray(momt[1], dtype=punit), name='py')
    momz = pandas.Series(pint_pandas.PintArray(momt[2], dtype=punit), name='pz')
    tags = pandas.Series(pint_pandas.PintArray(atoms.get_tags(), dtype=tunit), name='tags')
    mass = pandas.Series(pint_pandas.PintArray(atoms.get_masses(), dtype=munit), name='masses')

    atoms_cols = [symb, posx, posy, posz, momx, momy, momz, mass, tags]
    atoms_df = pandas.concat(atoms_cols, axis=1)
    cell = ureg.Quantity(atoms.get_cell().array, 'angstrom')
    struct_cols = [{'atoms': atoms_df, 'cell': cell, 'pbc': atoms.get_pbc()}]
    return pandas.DataFrame(struct_cols)


def get_calculator_dataframe(ase_calc):  # not covered
    """create a calculator dataframe from an ASE Calculator object"""
    parameters = jsonio.decode(jsonio.encode(ase_calc.parameters))
    units = get_params_units(ase_calc.name.lower(), parameters)
    calc_params = {}
    for par, val in parameters.items():
        if isinstance(val, (bool, str)) or val is None:
            calc_params[par] = val
        elif isinstance(val, (int, float)):
            calc_params[par] = ureg.Quantity(val, units[par])
        elif isinstance(val, (tuple, list)):
            if all(isinstance(v, (bool, str)) for v in list_flatten(val)):
                calc_params[par] = numpy.array(val)
            else:
                assert all(isinstance(v, (int, float)) for v in list_flatten(val))
                assert units[par] is not None
                calc_params[par] = ureg.Quantity(numpy.array(val), units[par])
        elif isinstance(val, numpy.ndarray):
            if numpy.issubdtype(val.dtype, numpy.number):
                assert units[par] is not None
                calc_params[par] = ureg.Quantity(val, units[par])
            else:
                npdtypes = (numpy.bool_, numpy.str_)
                assert any(numpy.issubdtype(val.dtype, t) for t in npdtypes)
                assert units[par] is None
                calc_params[par] = val
        else:
            raise TypeError('unknown type in calculator parameters')
    return pandas.DataFrame([calc_params])


def merge_structures(structs):
    """create one AMML structure from an iterable of AMML structures"""
    struct_df = pandas.concat([s.tab for s in structs], ignore_index=True)
    return AMMLStructure(struct_df, structs[0].name)


def merge_calculators(calcs):
    """create one AMML calculator from an iterable of AMML calculators"""
    calc_df = pandas.concat([c.parameters for c in calcs], ignore_index=True)
    calc_name = calcs[0].name
    calc_pinning = calcs[0].pinning
    calc_version = calcs[0].version
    return Calculator(calc_name, calc_df, calc_pinning, calc_version)


def merge_algorithms(algos):  # not covered
    """create one AMML algorithm from an iterable of AMML algorithms"""
    algo_df = pandas.concat([a.parameters for a in algos], ignore_index=True)
    algo_name = algos[0].name
    algo_mt1 = algos[0].many_to_one
    return Algorithm(algo_name, algo_df, algo_mt1)


class AMMLObject:
    """base class for all AMML objects"""


class AMMLIterableObject(AMMLObject):
    """base class for all iterable AMML objects"""

    def __init__(self, iterobj):
        assert isinstance(iterobj, pandas.DataFrame)
        self.iterobj = iterobj

    def __getitem__(self, key):
        if isinstance(key, int):
            dfr = self.iterobj.iloc[[key]]
            return tuple(next(dfr.itertuples(index=False, name=None)))
        raise TypeError('unknown key type')  # not covered

    def reset_index(self, *args, **kwargs):
        """resets the index of properties table"""
        inplace = kwargs.get('inplace')
        kwargs['inplace'] = True
        self.iterobj.reset_index(*args, **kwargs)
        if inplace:  # not covered
            return None
        return self

    def dropna(self):
        """drop non-defined values from props dataframe"""
        obj = deepcopy(self)
        obj.iterobj.dropna(inplace=True)
        return obj

    def iterrows(self):
        """return an iterator over props dataframe rows"""
        return self.iterobj.iterrows()


class AMMLStructure(AMMLIterableObject):
    """"custom AMML Structure class"""
    intrinsics = ('name', 'kinetic_energy', 'temperature', 'distance_matrix',
                  'chemical_formula', 'number_of_atoms', 'cell_volume',
                  'center_of_mass', 'radius_of_gyration', 'moments_of_inertia',
                  'angular_momentum')

    def __init__(self, tab, name=None):
        if 'pbc' in tab and 'cell' not in tab:  # not covered
            for pbc in tab['pbc'].values:
                if any(pbc):
                    raise RuntimeValueError('cell must be specified with pbc')
        self.name = name
        self.tab = tab
        super().__init__(self.tab)

    def __getitem__(self, key):
        if isinstance(key, str):
            if key in self.intrinsics:
                return getattr(self, key)
            return self.tab[key]
        if isinstance(key, slice):
            return self.__class__(self.tab[key], self.name)
        return super().__getitem__(key)

    def __len__(self):
        return len(self.tab)

    @cached_property
    def kinetic_energy(self):
        """get the kinetic energy of the nuclei"""
        kin = self.to_ase().apply(lambda x: x.get_kinetic_energy())
        return pandas.Series(kin, dtype=PintType('eV'), name='kinetic_energy')

    @cached_property
    def temperature(self):
        """get the temperature"""
        temp = self.to_ase().apply(lambda x: x.get_temperature())
        return pandas.Series(temp, dtype=PintType('kelvin'), name='temperature')

    @cached_property
    def distance_matrix(self):
        """get the matrix of interatomic distances (distance matrix)"""
        dis = self.to_ase().apply(lambda x: x.get_all_distances(mic=True))
        return pandas.Series(dis, dtype=PintType('angstrom'), name='distance_matrix')

    @cached_property
    def chemical_formula(self):
        """get chemical formula as a string based on the chemical symbols"""
        chem_formula = self.to_ase().apply(lambda x: x.get_chemical_formula())
        return pandas.Series(chem_formula, name='chemical_formula')

    @cached_property
    def number_of_atoms(self):
        """get number of atoms"""
        natoms = self.to_ase().apply(len)
        return pandas.Series(natoms, name='number_of_atoms')

    @cached_property
    def cell_volume(self):
        """get volume of the unit cell"""
        try:
            vol = self.to_ase().apply(lambda x: x.get_volume())
        except ValueError as err:  # not covered
            if 'volume not defined' in str(err):
                raise RuntimeValueError(str(err)) from err
            raise err
        return pandas.Series(vol, dtype=PintType('angstrom**3'), name='cell_volume')

    @cached_property
    def center_of_mass(self):
        """get the center of mass"""
        com = self.to_ase().apply(lambda x: x.get_center_of_mass())
        return pandas.Series(com, dtype=PintType('angstrom'), name='center_of_mass')

    @cached_property
    def radius_of_gyration(self):
        """get the radius of gyration"""
        def rogf(pos):
            centroid = numpy.mean(pos, axis=0)
            norm_sqr = (numpy.linalg.norm(pos-centroid, axis=1))**2
            return numpy.sqrt(numpy.mean(norm_sqr, axis=0))
        rog = self.to_ase().apply(lambda x: rogf(x.get_positions()))
        return pandas.Series(rog, dtype=PintType('angstrom'), name='radius_of_gyration')

    @cached_property
    def moments_of_inertia(self):
        """get the moments of inertia along the principal axes"""
        moi = self.to_ase().apply(lambda x: x.get_moments_of_inertia())
        unit = 'amu * angstrom**2'
        return pandas.Series(moi, dtype=PintType(unit), name='moments_of_inertia')

    @cached_property
    def angular_momentum(self):
        """get the total angular momentum with respect to the center of mass"""
        ang = self.to_ase().apply(lambda x: x.get_angular_momentum())
        unit = '( amu * eV ) ** (1/2) * angstrom'
        return pandas.Series(ang, dtype=PintType(unit), name='angular_momentum')

    def to_own_file(self, filename):
        """store series of ase.Atoms objects to a file in supported format"""
        write(images=self.to_ase(), filename=filename)

    def to_ase(self):
        """create a series of ase.Atoms objects from a structure dataframe"""
        dfr_ase = self.get_ase_atoms_dataframe()
        series = dfr_ase.apply(lambda row: ase.Atoms(**row.to_dict()), axis=1)
        return series.rename(self.name, inplace=True)

    def get_ase_atoms_dataframe(self):
        """return a unitless atoms dataframe from a structure dataframe with units"""
        dfr = self.tab
        dfr_ase = pandas.DataFrame()
        dfr_ase['symbols'] = dfr['atoms'].apply(lambda x: x.symbols.to_numpy())
        if 'cell' in dfr:
            dfr_ase['cell'] = dfr['cell'].apply(lambda x: x.to('angstrom').magnitude)
        else:
            dfr_ase[['cell']] = None

        dfr_ase['pbc'] = dfr['pbc'].to_numpy() if 'pbc' in dfr else None

        def xyz2pos(atoms):
            xcoord = get_pint_series(atoms['x']).pint.to('angstrom').values.data
            ycoord = get_pint_series(atoms['y']).pint.to('angstrom').values.data
            zcoord = get_pint_series(atoms['z']).pint.to('angstrom').values.data
            return numpy.array([xcoord, ycoord, zcoord]).transpose()

        def pxpypz2momenta(atoms):
            if 'px' not in atoms:
                return None
            units = '( amu * eV ) ** (1/2)'
            xcoord = get_pint_series(atoms['px']).pint.to(units).values.data
            ycoord = get_pint_series(atoms['py']).pint.to(units).values.data
            zcoord = get_pint_series(atoms['pz']).pint.to(units).values.data
            return numpy.array([xcoord, ycoord, zcoord]).transpose()

        dfr_ase['positions'] = dfr['atoms'].apply(xyz2pos)
        dfr_ase['momenta'] = dfr['atoms'].apply(pxpypz2momenta)
        dfr_ase['tags'] = dfr['atoms'].apply(lambda x: x.tags.to_numpy() if 'tags' in x else None)
        return dfr_ase

    @classmethod
    def from_ase(cls, atoms, name=None):
        """create an AMML object from an ASE Atoms object"""
        if isinstance(atoms, ase.Atoms):
            return cls(get_structure_dataframe(atoms), name)
        assert isinstance(atoms, (list, tuple, pandas.Series))
        atoms_dfs = [get_structure_dataframe(a) for a in atoms]
        return cls(pandas.concat(atoms_dfs, ignore_index=True), name)

    @classmethod
    def from_ase_file(cls, filename):
        """create an AMML Structure object from a file in an ASE-supported format"""
        try:
            structs = ase.io.read(filename, index=':')
        except Exception as err:  # broad exception due to ase.io.read  # not covered
            raise StructureInputError(f'{err.__class__.__name__}: {str(err)}') from err
        struct_dfs = [get_structure_dataframe(s) for s in structs]
        return cls(pandas.concat(struct_dfs, ignore_index=True))

    @classmethod
    def from_series(cls, series):
        """create an AMML Structure object from series of Structure objects"""
        tabs = (s.tab for s in series)
        tab = pandas.concat(tabs, axis='index', ignore_index=True)
        return cls(tab, name=series[0].name)


class AMMLMethod(AMMLIterableObject):
    """base class for AMML Calculator and Algorithm classes"""
    def __init__(self, name, parameters):
        self.name = name
        self.parameters = parameters
        if self.parameters is None or len(self.parameters) == 0:
            p_spec = spec[self.name]['params']
            par_def = {k: v['default'] for k, v in p_spec.items() if 'default' in v}
            assert len(par_def) > 0
            self.parameters = pandas.DataFrame([par_def])
        else:
            check_params_types(self.name, self.parameters)
            check_params_units(self.name, self.parameters)
        self.props = spec[self.name].get('properties') or []
        super().__init__(self.parameters)

    def __getitem__(self, key):
        if isinstance(key, str):
            if key in ('name', 'parameters'):
                return getattr(self, key)
            return self.parameters[key]
        if (isinstance(key, slice) or
           (isinstance(key, pandas.Series) and key.dtype is numpy.dtype(bool)) or
           (isinstance(key, (list, tuple)) and all(isinstance(s, str) for s in key))):
            obj = deepcopy(self)
            obj.parameters = obj.parameters[key]
            return obj
        return super().__getitem__(key)


class Calculator(AMMLMethod):
    """custom AMML Calculator class"""
    def __init__(self, name, parameters, pinning=None, version=None, task=None):
        super().__init__(name, parameters)
        self.pinning = pinning
        self.version = version
        self.task = task
        self.check_task_parameters()

    def __getitem__(self, key):
        if isinstance(key, str):
            if key in ('pinning', 'version', 'task'):
                return getattr(self, key)
        return super().__getitem__(key)

    def to_ase(self):
        """create a series of ASE Calculator objects"""
        mod = __import__(spec[self.name]['module'], {}, None, [spec[self.name]['class']])
        calc_class = getattr(mod, spec[self.name]['class'])
        calc_list = []
        for _, row in self.parameters.iterrows():
            calc_params = dict(row)
            calc_list.append(calc_class(**get_params_magnitudes(calc_params, self.name)))
        return pandas.Series(calc_list, name='calc')

    @classmethod
    def from_ase(cls, ase_calc):  # not covered
        """create an AMML Calculator object from an ASE Calculator object"""
        return cls(ase_calc.name.lower(), get_calculator_dataframe(ase_calc))

    def check_task_parameters(self):
        """check whether parameters are compatible with task"""
        if self.task is None:
            return
        assert self.task in spec[self.name]['tasks']
        for par, func in spec[self.name]['tasks'][self.task].items():
            list_ = pandas.DataFrame(self.parameters).to_dict(orient='records')
            for dct in list_:  # pylint: disable=not-an-iterable
                val = dct.get(par)
                msg = (f'Parameter {par}: {formatter(val)} inconsistent with task'
                       f' \"{self.task}\"')
                if not func(val):
                    raise RuntimeValueError(msg)

    def requires_dof(self):
        """determine whether the calculator requires changes of degrees of freedom"""
        if self.task is not None:
            return self.task != 'single point'
        return None

    def run(self, struct, constrs=None, properties=None):
        """runner for objects with length 1"""
        assert len(struct.tab) == len(self.parameters) == 1
        calc_ase = self.to_ase()[0]
        struct_ase = ase.Atoms(struct.to_ase()[0])
        struct_ase.constraints = constrs
        calc_args = [struct_ase]
        # due to turbomole and free_electrons calcs
        calculate_spec = inspect.getfullargspec(calc_ase.calculate)
        if len(calculate_spec.args) == 4:
            if calculate_spec.defaults is None or len(calculate_spec.defaults) < 3:
                calc_args.extend([properties or [], all_changes])  # not covered
        calc_ase.calculate(*calc_args)
        if hasattr(calc_ase, 'converged'):
            if not calc_ase.converged:  # not covered
                raise ConvergenceError(f'calculation with {self.name} did not converge')
        return calc_ase


class Algorithm(AMMLMethod):
    """custom AMML Algorithm class"""
    def __init__(self, name, parameters, many_to_one=False):
        super().__init__(name, parameters)
        self.many_to_one = many_to_one
        module = importlib.import_module(spec[self.name]['module'])
        self._class = getattr(module, spec[self.name]['class'])
        self.params = {k: [] for k in ('class', 'run')}
        param_spec = spec[self.name]['params']
        par_def = {k: v.get('default') for k, v in param_spec.items()}
        par_mth = {k: v.get('method') for k, v in param_spec.items()}
        for _, row in self.parameters.iterrows():
            params = {}
            params.update(par_def)
            params.update(dict(row))
            params = get_params_magnitudes(params, self.name)
            if params.get('trajectory'):
                params['trajectory'] = get_uuid_filename(extension='traj')
            if params.get('logfile'):
                params['logfile'] = get_uuid_filename(extension='log')
            for tp in ('class', 'run'):
                pars = {k: v for k, v in params.items() if par_mth[k] == tp}
                if 'interval' in pars:
                    pars['loginterval'] = pars.pop('interval')
                self.params[tp].append(pars)

    def run(self, struct, calc=None, constrs=None, properties=None):
        """the algorithm runner, process objects with length 1"""
        assert len(self.params['class']) == len(self.params['run']) == 1
        atoms_list = struct.to_ase().to_list()
        for atoms in atoms_list:
            atoms.constraints = constrs
        if self.many_to_one:
            struct_ase = atoms_list
        else:
            assert len(struct.tab) == 1
            struct_ase = atoms_list[0]
        if calc is not None:
            assert len(calc.parameters) == 1
            calc_ase = calc.to_ase()[0]
            if self.many_to_one:
                for atoms in struct_ase:
                    atoms.calc = calc_ase
            else:
                struct_ase.calc = calc_ase
        with self._class(struct_ase, **self.params['class'][0]) as algo_obj:
            converged = algo_obj.run(**self.params['run'][0])
        if not converged:  # not covered
            raise ConvergenceError(f'calculation with {self.name} did not converge')
        results = {'output_structure': struct_ase, 'algo': algo_obj}
        if calc is not None:
            if self.many_to_one:
                results['output_structure'] = pandas.Series(algo_obj.results['final_images'])
            else:
                struct_ase.calc.calculate(struct_ase, properties or [], all_changes)
                results['calc'] = struct_ase.calc
        return results


class Property(AMMLIterableObject):
    """custom AMML Property class"""

    def __init__(self, names, structure, calculator=None, algorithm=None,
                 constraints=None, results=None):
        assert isinstance(names, list)
        self.names = names
        self.structure = structure
        self.calculator = calculator
        self.algorithm = algorithm
        if constraints:
            if not all(len(c.fixed) == len(a) for c in constraints for a in structure.tab.atoms):
                msg = ('The list of fixed/non-fixed atoms in constraints and '
                       'atoms in structure have different lengths')
                raise RuntimeValueError(msg)  # not covered
            self.constraints = constraints
        else:
            self.constraints = []
        self.dof_vector, self.dof_number = self.get_dof()
        if self.calculator:
            self.requires_dof = self.calculator.requires_dof()
            if self.requires_dof is not None:
                if self.requires_dof and self.dof_number == 0:  # not covered
                    msg = 'All degrees of freedom frozen. Hint: check task and constraints.'
                    raise RuntimeValueError(msg)

        self.results = results if results is not None else self.get_results()
        super().__init__(self.results)

    def __getitem__(self, key):
        keys = ('names', 'calculator', 'structure', 'algorithm', 'constraints',
                'results')
        if isinstance(key, str):
            if key in keys:
                return getattr(self, key)
            if key == 'output_structure':
                return AMMLStructure.from_series(self.results.output_structure)
            try:
                return getattr(self.results, key)
            except AttributeError as err:  # not covered
                raise PropertyError(f'property "{key}" not available') from err
        if isinstance(key, slice):
            struct = merge_structures(self.results.structure[key])
            if self.calculator:
                calc = merge_calculators(self.results.calculator[key])
            else:  # not covered
                assert all(c is None for c in self.results.calculator[key])
                calc = None
            if self.algorithm:
                algo = merge_algorithms(self.results.algorithm[key])  # not covered
            else:
                assert all(a is None for a in self.results.algorithm[key])
                algo = None
            return self.__class__(self.names, struct, calculator=calc,
                                  algorithm=algo, constraints=self.constraints,
                                  results=self.results[key])
        return super().__getitem__(key)

    def get_dof(self):
        """return the non-frozen nuclear degrees of freedom"""
        atoms = self.structure[0:1].to_ase()[0]
        if self.constraints:
            new_pos = numpy.array(atoms.positions)
            for ind, (pbc, vec) in enumerate(zip(atoms.pbc, atoms.cell)):
                if pbc:
                    new_pos += 0.9*vec
                else:
                    new_pos[:, ind] += 0.9
            wrap_positions(new_pos, atoms.cell, atoms.pbc)
            for constr in self.constraints:
                for constr_ in constr.to_ase():
                    constr_.adjust_positions(atoms, new_pos)
            epsilon = numpy.finfo(numpy.float64).eps
            dof = numpy.abs(atoms.positions-new_pos) > epsilon
        else:
            dof = numpy.full((len(atoms), 3), True)
        return dof, numpy.sum(dof)

    def get_results_df(self):
        """create a dataframe for results, populate with struct, calc, algo"""
        calc_it = self.calculator or [None]
        algo_it = self.algorithm or [None]
        if self.algorithm and self.algorithm.many_to_one:
            stru_it = [self.structure]
        else:
            stru_it = self.structure

        def gen_func():
            columns_iter = itertools.product(calc_it, algo_it, stru_it)
            for calc, algo, struct in columns_iter:
                if calc is None:
                    calc_amml = None
                else:
                    calc_ = self.calculator
                    calc_df = pandas.DataFrame([dict(zip(calc_.parameters, calc))])
                    calc_amml = Calculator(parameters=calc_df, name=calc_.name,
                                           pinning=calc_.pinning, version=calc_.version)
                if algo is None:
                    algo_amml = None
                else:
                    algo_df = pandas.DataFrame([dict(zip(self.algorithm.parameters, algo))])
                    algo_amml = Algorithm(self.algorithm.name, algo_df, self.algorithm.many_to_one)

                if self.algorithm and self.algorithm.many_to_one:
                    struct_amml = struct
                else:
                    struct_df = pandas.DataFrame([dict(zip(self.structure.tab, struct))])
                    struct_amml = AMMLStructure(struct_df, self.structure.name)
                yield struct_amml, calc_amml, algo_amml
        columns = ['structure', 'calculator', 'algorithm']
        return pandas.DataFrame(gen_func(), columns=columns)

    def get_results(self):
        """create a dataframe with properties calculated using ASE"""
        df = self.get_results_df()
        constrs = []
        for constr in self.constraints:
            constrs.extend(constr.to_ase())

        def apply_algo(struct, calc, algo):
            if self.calculator:
                return algo.run(struct, calc, constrs=constrs)
            return algo.run(struct, constrs=constrs)

        def apply_calc(struct, calc, _):
            return calc.run(struct, constrs=constrs, properties=self.names)

        def apply_func(df, func):
            return func(df.structure, df.calculator, df.algorithm)

        def get_struct_from_calc(calc):
            return AMMLStructure.from_ase(calc.get_atoms(), self.structure.name)

        def get_struct_from_algo(dct):
            return AMMLStructure.from_ase(dct['output_structure'], self.structure.name)

        if self.algorithm:
            df['results'] = df.apply(lambda x: apply_func(x, apply_algo), axis=1)
            df['output_structure'] = df['results'].apply(get_struct_from_algo)
            for prop in self.names:
                if prop in self.algorithm.props:
                    method = self.algorithm.name
                else:
                    assert self.calculator and prop in self.calculator.props
                    method = self.calculator.name
                df[prop] = get_ase_property(method, prop, df['results'])
            df.drop(columns=['results'], inplace=True)
        else:
            assert self.calculator
            df['calc'] = df.apply(lambda x: apply_func(x, apply_calc), axis=1)
            df['results'] = df['calc'].apply(lambda x: {'calc': x})
            df['output_structure'] = df['calc'].apply(get_struct_from_calc)
            for prop in self.names:
                df[prop] = get_ase_property(self.calculator.name, prop, df['results'])
            df.drop(columns=['calc', 'results'], inplace=True)
        return df


class Constraint(AMMLObject):
    """custom AMML Constraint class"""
    ase_name_map = {'FixAtoms': 'FixedAtoms', 'FixedLine': 'FixedLine',
                    'FixedPlane': 'FixedPlane', 'FixScaled': 'FixScaled'}

    def __init__(self, name, **kwargs):
        assert name in self.ase_name_map.values()
        self.name = name
        self.kwargs = kwargs
        self.fixed = kwargs.get('fixed')
        self.indices = self.fixed[self.fixed].index.values
        self.direction = kwargs.get('direction')
        self.mask = kwargs.get('mask')

    def to_ase(self):
        """return ASE constraint objects"""
        if self.name == 'FixedAtoms':
            return [ase.constraints.FixAtoms(indices=self.indices)]
        if self.name == 'FixScaled':  # not covered
            return [ase.constraints.FixScaled(self.indices, mask=self.mask)]
        direc = self.direction.magnitude
        if self.name == 'FixedLine':
            return [ase.constraints.FixedLine(self.indices, direction=direc)]
        assert self.name == 'FixedPlane'
        return [ase.constraints.FixedPlane(self.indices, direction=direc)]

    @classmethod
    def from_ase(cls, constr, natoms):
        """convert an ASE constraint object into AMML constraint"""
        constr_name = cls.ase_name_map[constr.__class__.__name__]
        indices = constr.get_indices()
        fixed = pandas.Series((i in indices for i in range(natoms)), name='fixed')
        if isinstance(constr, ase.constraints.FixScaled):  # not covered
            return cls(constr_name, fixed=fixed, mask=constr.mask)
        if isinstance(constr, ase.constraints.FixAtoms):
            return cls(constr_name, fixed=fixed)
        assert isinstance(constr, (ase.constraints.FixedLine, ase.constraints.FixedPlane))
        return cls(constr_name, fixed=fixed, direction=ureg.Quantity(constr.dir))


@dataclass
class Trajectory(AMMLObject):
    """custom AMML trajectory class"""
    description: pandas.DataFrame = None
    structure: AMMLStructure = None
    properties: pandas.DataFrame = None
    constraints: pandas.Series = None
    filename: str = None

    @classmethod
    def from_file(cls, filename, name=None):
        """create an AMML Trajectory object from an ASE trajectory file"""
        with TrajectoryReader(filename) as traj:
            ase_desc = traj.description
            ase_structs = list(traj)
            ase_constrs = traj.constraints
        assert isinstance(ase_constrs, str)  # constraints in trajectory are JSON strings
        ase_constrs = [ase.constraints.dict2constraint(c) for c in jsonio.decode(ase_constrs)]
        return cls.from_ase(ase_desc, ase_structs, [ase_constrs]*len(ase_structs), filename, name)

    @classmethod
    def from_ase(cls, ase_desc, ase_structs, ase_constrs, filename=None, name=None):
        """create an AMML Trajectory object from a description, list of atoms objects,
           and list of constraints"""
        for atoms in ase_structs:
            assert hasattr(atoms, 'calc')
            assert isinstance(atoms.calc, SinglePointCalculator)
        structure = AMMLStructure.from_ase(ase_structs, name=name)
        description = pandas.DataFrame()
        if ase_desc is not None:
            description['type'] = pandas.Series(ase_desc['type'])
            if 'optimizer' in ase_desc:
                algo = description['optimizer'] = ase_desc['optimizer']
            elif 'md-type' in ase_desc:  # not covered
                algo = description['md-type'] = ase_desc['md-type']
            params = {k: v for k, v in ase_desc.items() if k in spec[algo]['params']}
            for ukey, uval in get_params_units(algo, params).items():
                if uval is not None:
                    mag = numpy.nan if ase_desc[ukey] is None else ase_desc[ukey]
                    description[ukey] = ureg.Quantity(mag, uval)
                else:  # not covered
                    description[ukey] = ase_desc[ukey]
        results = [{'calc': a.calc} for a in ase_structs]
        properties = pandas.DataFrame()
        for key in ase_structs[0].calc.export_properties().keys():
            properties[key] = get_ase_property('SinglePointCalculator', key, results)
        ase_natoms = [len(a) for a in ase_structs]
        assert len(set(ase_natoms)) == 1
        constrs = [[Constraint.from_ase(c, ase_natoms[0]) for c in cs] for cs in ase_constrs]
        constraints = pandas.Series(constrs, name='constraints')
        return cls(description, structure, properties, constraints, filename)

    def __getitem__(self, key):
        if isinstance(key, int):
            props = self.properties.iloc[[key]].itertuples(index=False, name=None)
            return tuple((*self.structure[key], *props))
        if isinstance(key, str):
            return getattr(self, key)
        if isinstance(key, slice):
            return self.__class__(self.description, self.structure[key],
                                  self.properties.iloc[key], self.constraints[key],
                                  self.filename)
        raise TypeError(f'unknown key type {type(key)}')  # not covered
