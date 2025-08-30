"""
tests for amml data structures and operations
"""
import os
import pytest
from textx import get_children_of_type
from textx.exceptions import TextXError
from ase.calculators.calculator import CalculatorSetupError
from virtmat.language.utilities.typemap import typemap
from virtmat.language.utilities.amml import AMMLStructure
from virtmat.language.utilities.errors import StaticValueError, RuntimeValueError
from virtmat.language.utilities.errors import StaticTypeError, InvalidUnitError
from virtmat.language.utilities.errors import EvaluationError
from virtmat.language.utilities.errors import PropertyError, ConvergenceError
from virtmat.language.utilities.formatters import formatter


@pytest.fixture(name='water_yaml')
def water_yaml_fixture(tmp_path):
    """path to water.yaml file"""
    return os.path.join(tmp_path, 'water.yaml')


@pytest.fixture(name='water_cif')
def water_cif_fixture(tmp_path):
    """path to water.cif file"""
    return os.path.join(tmp_path, 'water.cif')


@pytest.fixture(name='calc_yaml')
def water_calc_fixture(tmp_path):
    """path to calc.yaml file"""
    return os.path.join(tmp_path, 'calc.yaml')


def test_amml_structure_literal(meta_model, model_kwargs, water_yaml, water_cif):
    """test AMML structure literal and I/O"""
    inp1 = ("water = Structure ("
            "          (atoms: ((symbols: 'O', 'H', 'H'),"
            "                   (x: 0., 0., 0.) [nm],"
            "                   (y: 0., 0.763239, -0.763239) [angstrom],"
            "                   (z: 0.119262, -0.477047, -0.477047) [angstrom],"
            "                   (tags: 1, 0, 0),"
            "                   (masses: 16., 1., 1.) [amu]"
            "                  )"
            "          ),"
            "          (cell: [[2., 0., 0.], [0., 2., 0.], [0., 0., 2.]] [bohr]),"
            "          (pbc: [false, false, true])"
            "        )\n"
            "water to file \'" + water_yaml + "\'\n"
            "water to file \'" + water_cif + "\'\n")
    inp2 = ("water_1 = Structure from file \'" + water_yaml + "\'\n"
            "water_2 = Structure from file \'" + water_cif + "\'")
    if 'model_instance' not in model_kwargs:
        inp1 += inp2
    prog = meta_model.model_from_str(inp1, **model_kwargs)
    if 'model_instance' in model_kwargs:
        model_kwargs['model_instance']['uuid'] = prog.uuid
        prog = meta_model.model_from_str(inp1+inp2, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    water_var = next(v for v in var_list if v.name == 'water')
    assert issubclass(water_var.type_, typemap['AMMLStructure'])
    assert isinstance(water_var.value, typemap['AMMLStructure'])
    water1_var = next(v for v in var_list if v.name == 'water_1')
    water2_var = next(v for v in var_list if v.name == 'water_2')
    assert water2_var.value['atoms'][0].symbols.tolist() == ['O', 'H', 'H']
    assert water1_var.value.name == water_var.value.name
    tab = water1_var.value.tab
    tabref = water_var.value.tab
    assert tab.atoms[0].symbols.tolist() == tabref.atoms[0].symbols.tolist()
    assert tab.atoms[0].x.tolist() == tabref.atoms[0].x.tolist()
    assert tab.atoms[0].y.tolist() == tabref.atoms[0].y.tolist()
    assert tab.atoms[0].z.tolist() == tabref.atoms[0].z.tolist()
    assert tab.atoms[0].tags.tolist() == tabref.atoms[0].tags.tolist()
    assert tab.atoms[0].masses.tolist() == tabref.atoms[0].masses.tolist()
    assert tab.cell[0].data.tolist() == tabref.cell[0].data.tolist()
    assert tab.pbc[0].data.tolist() == tabref.pbc[0].data.tolist()


def test_amml_structure_literal_missing_symbols(meta_model, model_kwargs):
    """test AMML structure literal with missing symbols"""
    inp = "s = Structure ((atoms: ((x: 0.) [nm], (y: 0.) [nm], (z: 0.) [nm])))"
    with pytest.raises(TextXError, match='missing chemical symbols') as err:
        meta_model.model_from_str(inp, **model_kwargs)
    assert isinstance(err.value.__cause__, StaticValueError)


def test_amml_structure_literal_missing_coordinates(meta_model, model_kwargs):
    """test AMML structure literal with missing coordinates"""
    inp = "s = Structure ((atoms: ((symbols: 'H', 'H'))))"
    with pytest.raises(TextXError, match='missing atomic coordinates') as err:
        meta_model.model_from_str(inp, **model_kwargs)
    assert isinstance(err.value.__cause__, StaticValueError)


def test_amml_structure_literal_wrong_units(meta_model, model_kwargs):
    """test AMML structure literal with wrong units of coordinates"""
    inp = ("s = Structure ((atoms: ((symbols: 'H'), (x: 0.) [nm],"
           "(y: 0.) [nm], (z: 0.) [s])))")
    msg = r'object must have dimensionality of \[length\]'
    with pytest.raises(TextXError, match=msg) as err:
        meta_model.model_from_str(inp, **model_kwargs)
    assert isinstance(err.value.__cause__, InvalidUnitError)


def test_amml_calculator_literal(meta_model, model_kwargs, calc_yaml):
    """test AMML calculator literal and I/O"""
    inp = ("calc = Calculator vasp ("
           "     (algo: 'Fast'),"
           "     (ediff: 1e-06) [eV],"
           "     (ediffg: -0.01) [eV/angstrom],"
           "     (encut: 400.0) [eV],"
           "     (ibrion: 2),"
           "     (icharg: 2),"
           "     (isif: 2),"
           "     (ismear: 0),"
           "     (ispin: 2),"
           "     (istart: 0),"
           "     (kpts: [5, 5, 1]),"
           "     (lcharg: false),"
           "     (lreal: 'Auto'),"
           "     (lwave: false),"
           "     (nelm: 250),"
           "     (nsw: 1500),"
           "     (potim: 0.1),"
           "     (prec: 'Normal'),"
           "     (sigma: 0.1) [eV],"
           "     (xc: 'PBE')"
           ");"
           "calc to file \'" + calc_yaml + "\'")
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    calc_var = next(v for v in var_list if v.name == 'calc')
    assert issubclass(calc_var.type_, typemap['AMMLCalculator'])
    assert isinstance(calc_var.value, typemap['AMMLCalculator'])


def test_amml_calculator_unsupported_task(meta_model, model_kwargs):
    """test calculator with unsupported task"""
    inp = 'calc = Calculator emt (), task: transition state'
    msg = 'Task \"transition state\" not supported in calculator \"emt\"'
    with pytest.raises(TextXError, match=msg) as err:
        meta_model.model_from_str(inp, **model_kwargs)
    assert isinstance(err.value.__cause__, StaticValueError)


def test_amml_calculator_missing_mandatory_parameter(meta_model, model_kwargs):
    """test calculator with missing mandatory parameter"""
    inp = 'calc = Calculator turbomole ()'
    msg = r"Mandatory parameters missing in method \"turbomole\": \(\'multiplicity\'\,\)"
    with pytest.raises(TextXError, match=msg) as err:
        meta_model.model_from_str(inp, **model_kwargs)
    assert isinstance(err.value.__cause__, StaticValueError)


def test_amml_calculator_inconsistent_parameter_task(meta_model, model_kwargs):
    """test calculator with inconsistent parameter with task"""
    inp = 'calc = Calculator vasp ((ibrion: 3)), task: micro-canonical; print(calc)'
    msg = 'Parameter ibrion: 3 inconsistent with task "micro-canonical"'
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    with pytest.raises(TextXError, match=msg) as err:
        _ = next(v for v in var_list if v.name == 'calc').value
    assert isinstance(err.value.__cause__, RuntimeValueError)


def test_amml_calculator_access_attributes(meta_model, model_kwargs):
    """test AMML calculator access to attributes"""
    inp = ("calc = Calculator vasp >= 6.1.0 ((algo: 'Fast'), (ediff: 1e-06) [eV],"
           "(ediffg: -0.01) [eV/angstrom]), task: single point; "
           "name = calc.name; version = calc.version; pinning = calc.pinning;"
           "task = calc.task; params = calc.parameters; algo = params.algo[0]")
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    assert next(v for v in var_list if v.name == 'name').value == 'vasp'
    assert next(v for v in var_list if v.name == 'task').value == 'single point'
    assert next(v for v in var_list if v.name == 'version').value == '6.1.0'
    assert next(v for v in var_list if v.name == 'pinning').value == '>='
    assert next(v for v in var_list if v.name == 'params').value['algo'][0] == 'Fast'
    assert next(v for v in var_list if v.name == 'algo').value == 'Fast'


def test_amml_calculator_iterable(meta_model, model_kwargs):
    """test AMML calculator used as iterable"""
    inp = ("calc = Calculator vasp == 5.4.4 ((lreal: true, false),"
           "(ediff: 1e-06, 1e-05) [eV], (ediffg: -0.01, -0.05) [eV/angstrom]);"
           "calc_1 = calc[1:]; lreal = calc_1.parameters.lreal[0];"
           "calc_2 = calc select ediff, ediffg where column:lreal == false;"
           "ediff = calc_2.parameters.ediff[0]")
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    assert next(v for v in var_list if v.name == 'lreal').value is False
    assert next(v for v in var_list if v.name == 'ediff').value.units == 'electron_volt'
    assert next(v for v in var_list if v.name == 'ediff').value.magnitude == pytest.approx(1e-5)


def test_amml_calculator_iterable_filter_map_reduce(meta_model, model_kwargs):
    """test AMML calculator used as iterable in filter, map and reduce"""
    inp = ("calc = Calculator vasp == 5.4.4 ((lreal: true, false),"
           "(ediff: 1e-06, 1e-05) [eV], (ediffg: -0.01, -0.05) [eV/angstrom]);"
           "c_f = filter((x: x.lreal), calc); e_f = c_f.parameters.ediff;"
           "c_m = map((x: {lreal: x.lreal, ediff: 2*x.ediff}), calc); e_m = c_m.ediff;"
           "c_r = reduce((x, y: {lreal: (x.lreal and y.lreal)}), calc); e_r = c_r.lreal")
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    e_f_ref = '(ediff: 1e-06) [electron_volt]'
    e_m_ref = '(ediff: 2e-06, 2e-05) [electron_volt]'
    e_r_ref = '(lreal: false)'
    assert formatter(next(v for v in var_list if v.name == 'e_f').value) == e_f_ref
    assert formatter(next(v for v in var_list if v.name == 'e_m').value) == e_m_ref
    assert formatter(next(v for v in var_list if v.name == 'e_r').value) == e_r_ref


def test_amml_property_literal(meta_model, model_kwargs):
    """test AMML property literal and I/O"""
    inp = ("h2o = Structure water ("
           "        (atoms: ((symbols: 'O', 'H', 'H'),"
           "                 (x: 0., 0., 0.) [nm],"
           "                 (y: 0., 0.763239, -0.763239) [angstrom],"
           "                 (z: 0.119262, -0.477047, -0.477047) [angstrom]"
           "                )"
           "        ),"
           "        (cell: [[10., 0., 0.], [0., 10., 0.], [0., 0., 10.]] [angstrom]),"
           "        (pbc: [true, true, false])"
           "      );"
           "calc = Calculator vasp >= 5.4.4 ("
           "          (algo: 'Fast'),"
           "          (ediff: 1e-06) [eV],"
           "          (ediffg: -0.005) [eV/angstrom],"
           "          (encut: 400.0) [eV],"
           "          (ibrion: 2),"
           "          (icharg: 2),"
           "          (isif: 2),"
           "          (ismear: 0),"
           "          (ispin: 2),"
           "          (istart: 0),"
           "          (kpts: [5, 5, 1]),"
           "          (lcharg: false),"
           "          (lreal: 'Auto'),"
           "          (lwave: false),"
           "          (nelm: 250),"
           "          (nsw: 1500),"
           "          (potim: 0.1),"
           "          (prec: 'Normal'),"
           "          (sigma: 0.1) [eV],"
           "          (xc: 'PBE')"
           "       );"
           "props = Property energy, forces ((structure: h2o), (calculator: calc))")
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    msg = (r'Please set either command in calculator or one of the following '
           r'environment variables \(prioritized as follows\): ASE_VASP_COMMAND, '
           r'VASP_COMMAND, VASP_SCRIPT')
    with pytest.raises(TextXError, match=msg) as err:
        _ = next(v for v in var_list if v.name == 'props').value
    assert isinstance(err.value.__cause__, CalculatorSetupError)


def test_amml_property_access_properties(meta_model, model_kwargs):
    """test access to properties in an evaluated AMML property literal"""
    inp = ("epsilon_K = 119.8 [K];"
           "kB = 1. [boltzmann_constant];"
           "calc = Calculator lj ((sigma: 3.405) [angstrom], (epsilon: epsilon_K*kB));"
           "struct = Structure fcc_Ar4 ("
           "     (atoms: ("
           "       (symbols: 'Ar', 'Ar', 'Ar', 'Ar'),"
           "       (x: 0., 2.41, 2.41, 0.) [angstrom],"
           "       (y: 0., 2.41, 0., 2.41) [angstrom],"
           "       (z: 0., 0., 2.41, 2.41) [angstrom]"
           "      )"
           "     ),"
           "     (pbc: [true, true, true]),"
           "     (cell: [[4.82, 0., 0.], [0., 4.82, 0.], [0., 0., 4.82]] [angstrom])"
           ");"
           "prop = Property energy, forces ((calculator: calc), (structure: struct));"
           "print(calc, struct);"
           "print(prop);"
           "print(prop.energy);"
           "print(prop.forces); energy = prop.energy[0]")
    prog = meta_model.model_from_str(inp, **model_kwargs)
    print(prog.value)
    var_list = get_children_of_type('Variable', prog)
    energy = next(v for v in var_list if v.name == 'energy')
    assert issubclass(energy.type_, typemap['Quantity'])
    assert isinstance(energy.value, typemap['Quantity'])
    assert energy.value.units == 'electron_volt'
    assert energy.value.magnitude == pytest.approx(-0.16027557460638842)


def test_amml_property_slicing(meta_model, model_kwargs):
    """test amml property slicing"""
    inp = ("h2o = Structure water ("
           "     (atoms: ((symbols: 'O', 'H', 'H'),"
           "       (x: 0., 0., 0.) [nm],"
           "       (y: 0., 0.763239, -0.763239) [angstrom],"
           "       (z: 0.119262, -0.477047, -0.477047) [angstrom]"
           "      )"
           "     )"
           ");"
           "calc = Calculator emt ((restart: default), (asap_cutoff: default)),"
           "                      task: single point;"
           "calc2 = Calculator emt ();"
           "props = Property energy, forces ((structure: h2o), (calculator: calc));"
           "props2 = Property energy, forces ((structure: h2o), (calculator: calc2));"
           "print(props[0]);"
           "print(props.calculator[0:1]);"
           "props_01 = props[0:1];"
           "print(props_01);"
           "print(props_01.structure);"
           "print(props_01.calculator);"
           "print(props2[0])\n")
    prog = meta_model.model_from_str(inp, **model_kwargs)
    print(prog.value)


def test_amml_constraints_properties(meta_model, model_kwargs):
    """test AMML property with AMML calculator and AMML constraints"""
    inp = ("h2o = Structure H2O ("
           "          (atoms: ((symbols: 'O', 'H', 'H'),"
           "                   (x: 6., 6.96504783, 5.87761163) [angstrom],"
           "                   (y: 6., 5.87761163, 6.96504783) [angstrom],"
           "                   (z: 6., 6.00000000, 6.00000000) [angstrom]"
           "                  )"
           "          ),"
           "          (cell: [[12., 0., 0.], [0., 12., 0.], [0., 0., 12.]] [angstrom]),"
           "          (pbc: [true, true, true])"
           ");"
           "h2 = Structure H2 ("
           "          (atoms: ((symbols: 'H', 'H'),"
           "               (x: 0., 0.) [angstrom],"
           "               (y: 0., 0.) [angstrom],"
           "               (z: 0., 1.) [angstrom]"
           "            )"
           "          ),"
           "          (cell: [[12., 0., 0.], [0., 12., 0.], [0., 0., 12.]] [angstrom]),"
           "          (pbc: [true, true, true])"
           ");"
           "calc = Calculator emt(), task: single point;"
           "calc2 = Calculator emt((asap_cutoff: default, false));"
           "plane = FixedPlane normal to [0, 0, 1] where (fix: true, true, true);"
           "props = Property energy, forces ((structure: h2o), (calculator: calc),"
           "                                 (constraints: (plane,)));"
           "props2 = Property energy, forces ((structure: h2o), (calculator: calc2),"
           "                                  (constraints: (plane,)));"
           "print(plane);"
           "print(props.structure.name, props.energy);"
           "print(props2.structure.name, props2.energy)")
    prog = meta_model.model_from_str(inp, **model_kwargs)
    print(prog.value)


def test_amml_property_inconsistent_constraints(meta_model, model_kwargs):
    """test AMML property with AMML structure and inconsistent AMML constraints"""
    inp = ("h2 = Structure H2 ("
           "          (atoms: ((symbols: 'H', 'H'),"
           "               (x: 0., 0.) [angstrom],"
           "               (y: 0., 0.) [angstrom],"
           "               (z: 0., 1.) [angstrom]"
           "            )"
           "          )"
           ");"
           "calc = Calculator emt(default);"
           "constr = FixedAtoms where (fix: true, false, false);"
           "props = Property energy ((structure: h2), (calculator: calc),"
           "                         (constraints: (constr,)))\n")
    msg = ('The list of fixed/non-fixed atoms in constraints and atoms in '
           'structure have different lengths')
    with pytest.raises(TextXError, match=msg):
        meta_model.model_from_str(inp, **model_kwargs)


def test_amml_optimizer_algorithms(meta_model, model_kwargs):
    """test AMML optimizer algorithms"""
    inp = ("algo1 = Algorithm BFGS ((fmax: 1e-4) [hartree/bohr], (logfile: true));"
           "algo2 = Algorithm LBFGS ((fmax: 1e-2) [eV/angstrom], (trajectory: true));"
           "algo3 = Algorithm GPMin ((fmax: 0.005) [hartree/bohr], (steps: 30))\n"
           "algo4 = Algorithm FIRE ((steps: 30), (trajectory: true), (interval: 2));"
           "algo5 = Algorithm QuasiNewton ((fmax: 0.05) [eV/bohr], (steps: 30))\n"
           "algo6 = Algorithm BFGSLineSearch ((fmax: 0.0001) [hartree/bohr])\n"
           "algo7 = Algorithm LBFGSLineSearch ()\n"
           "algo8 = Algorithm MDMin ((trajectory: true), (dt: 1.) [fs])")
    _ = meta_model.model_from_str(inp, **model_kwargs).value


def test_amml_optimizer_run(meta_model, model_kwargs):
    """test AMML optimizer algorithm runs"""
    inp = ("algo = Algorithm BFGS ((fmax: 1e-4) [hartree/bohr], (trajectory: true));"
           "h2o = Structure water (("
           "         atoms: ((symbols: 'O', 'H', 'H'),"
           "                 (x: 0., 0., 0.) [nm],"
           "                 (y: 0., 0.763239, -0.763239) [angstrom],"
           "                 (z: 0.119262, -0.477047, -0.477047) [angstrom])));"
           "calc = Calculator emt (), task: single point;"
           "constr = FixedAtoms where (fix: true, false, false);"
           "props = Property energy, forces, trajectory ((structure: h2o),"
           "                                             (calculator: calc),"
           "                                             (algorithm: algo),"
           "                                             (constraints: (constr,)));"
           "algo_nc = Algorithm BFGS ((fmax: 1e-5) [eV/angstrom], (steps: 1));"
           "props_nc = Property energy ((structure: h2o), (calculator: calc),"
           "                            (algorithm: algo_nc));"
           "energy = props.energy")
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    energy = next(v for v in var_list if v.name == 'energy').value[0].to('eV').magnitude
    assert energy == pytest.approx(1.8789, 1e-3)
    with pytest.raises(TextXError, match='calculation with BFGS did not converge') as err:
        _ = next(v for v in var_list if v.name == 'props_nc').value
    if model_kwargs.get('model_instance'):
        assert isinstance(err.value.__cause__, EvaluationError)
        assert isinstance(err.value.__cause__.__cause__, ConvergenceError)
    else:
        assert isinstance(err.value.__cause__, ConvergenceError)


def test_amml_md_algorithms(meta_model, model_kwargs):
    """test AMML molecular dynamics algorithms"""
    inp = ("algo1 = Algorithm VelocityVerlet ((timestep: 1) [fs], (steps: 5),"
           "                                  (trajectory: true));"
           "algo2 = Algorithm Langevin ((timestep: 1) [fs], (steps: 5),"
           "                            (temperature_K: 300.) [K], (friction: 0.05 [1/fs]),"
           "                            (trajectory: true));"
           "algo3 = Algorithm NPT ((timestep: 1) [fs], (steps: 5), (temperature_K: 300.) [K],"
           "                       (externalstress: 1) [bar], (ttime: 25) [fs],"
           "                       (pfactor: 100 [GPa] * (75 [fs])**2), (trajectory: true));"
           "algo4 = Algorithm Andersen ((timestep: 5) [fs], (steps: 100),"
           "                            (temperature_K: 300.) [K], (andersen_prob: 0.005),"
           "                            (trajectory: true));"
           "algo5 = Algorithm NVTBerendsen ((timestep: 5) [fs], (steps: 100),"
           "                                (temperature_K: 300.) [K], (taut: 100) [fs],"
           "                                (trajectory: true));"
           "algo6 = Algorithm NPTBerendsen ((timestep: 5) [fs], (steps: 100),"
           "                                (temperature_K: 300.) [K], (pressure_au: 100 [bar]),"
           "                                (compressibility_au: 4.57e-5) [1/bar],"
           "                                (trajectory: true))")
    meta_model.model_from_str(inp, **model_kwargs)


def test_amml_property_resources(meta_model_wf, model_kwargs_wf, _res_config_loc):
    """test AMML property literal resources"""
    inp = ("h2o = Structure water ("
           "        (atoms: ((symbols: 'O', 'H', 'H'),"
           "                 (x: 0., 0., 0.) [nm],"
           "                 (y: 0., 0.763239, -0.763239) [angstrom],"
           "                 (z: 0.119262, -0.477047, -0.477047) [angstrom]"
           "                )"
           "        ),"
           "        (cell: [[10., 0., 0.], [0., 10., 0.], [0., 0., 10.]] [angstrom]),"
           "        (pbc: [true, true, true])"
           "      );"
           "calc = Calculator vasp >= 5.4.4 ();"
           "prop = Property energy, forces ((structure: h2o), (calculator: calc))"
           "       on 4 cores for 0.1 [hour]")
    pre_rocket = ('module purge; module load chem/vasp/5.4.4.pl2; '
                  'export VASP_COMMAND=vasp_std')
    prog = meta_model_wf.model_from_str(inp, **model_kwargs_wf)
    var_list = get_children_of_type('Variable', prog)
    var = next(v for v in var_list if v.name == 'prop')
    fw_ids = prog.lpad.get_fw_ids({'name': var.fireworks[0].name})
    assert len(fw_ids) == 1
    fw_spec = prog.lpad.get_fw_by_id(fw_ids[0]).spec
    assert '_category' in fw_spec
    assert fw_spec['_category'] == 'batch'
    assert '_queueadapter' in fw_spec
    qadapter = fw_spec['_queueadapter']
    assert qadapter.q_name == 'test_q'
    assert qadapter['walltime'] == 6
    assert qadapter['nodes'] == 1
    assert qadapter['ntasks_per_node'] == 4
    assert qadapter['pre_rocket'] == pre_rocket


def test_output_structure(meta_model, model_kwargs):
    """test output_structure: it is an AMML Structure object"""
    inp = ("calc = Calculator emt ();"
           "h2o = Structure ((atoms: ((symbols: 'O', 'H', 'H'),"
           "(x: 0.0, 0.0, 0.0) [angstrom],"
           "(y: 0.0, 0.763239, -0.763239) [angstrom],"
           "(z: 0.119262, -0.477047, -0.477047) [angstrom])));"
           "p1 = Property energy ((calculator: calc), (structure: h2o));"
           "h2o_out = p1.output_structure;"
           "print(h2o_out)")
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    out_struct_val = next(v for v in var_list if v.name == 'h2o_out').value
    assert isinstance(out_struct_val, AMMLStructure)
    ref = ("Structure ((atoms: ((symbols: 'O', 'H', 'H'), (x: 0.0, 0.0, 0.0) [angstrom],"
           " (y: 0.0, 0.763239, -0.763239) [angstrom], (z: 0.119262, -0.477047, -0.477047)"
           " [angstrom], (px: 0.0, 0.0, 0.0) [electron_volt ** 0.5 * unified_atomic_mass_unit"
           " ** 0.5], (py: 0.0, 0.0, 0.0) [electron_volt ** 0.5 * unified_atomic_mass_unit **"
           " 0.5], (pz: 0.0, 0.0, 0.0) [electron_volt ** 0.5 * unified_atomic_mass_unit **"
           " 0.5], (masses: 15.999, 1.008, 1.008) [unified_atomic_mass_unit], (tags: 0, 0, 0)))"
           ", (cell: [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]) [angstrom],"
           " (pbc: [false, false, false]))")
    assert prog.value == ref


def test_velocity_distribution(meta_model, model_kwargs):
    """test velocity distribution algorithm"""
    inp = ("struct = Structure ((atoms: ("
           "            (symbols: 'Ar', 'Ar', 'Ar', 'Ar'), "
           "            (x: 0., 2.41, 2.41, 0.) [angstrom],"
           "            (y: 0., 2.41, 0., 2.41) [angstrom],"
           "            (z: 0., 0., 2.41, 2.41) [angstrom])));"
           "algo = Algorithm VelocityDistribution ((temperature_K: 100.) [K]);"
           "prop = Property ((algorithm: algo), (structure: struct));"
           "temp = prop.output_structure.temperature")
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    temp = next(v for v in var_list if v.name == 'temp').value[0]
    assert temp.to('kelvin').magnitude > 0.0


def test_rdf_many_to_many(meta_model, model_kwargs):
    """test rdf algorithm in many-to-many relationship with structure"""
    inp = ("h2o = Structure water ("
           "        (atoms: ((symbols: 'O', 'H', 'H'),"
           "                 (x: 0., 0., 0.) [nm],"
           "                 (y: 0., 0.763239, -0.763239) [angstrom],"
           "                 (z: 0.119262, -0.477047, -0.477047) [angstrom]"
           "                ),"
           "                ((symbols: 'O', 'H', 'H'),"
           "                 (x: 0., 0., 0.) [nm],"
           "                 (y: 0., 0.763239, -0.763239) [angstrom],"
           "                 (z: 0.119262, -0.477047, -0.477047) [angstrom]"
           "                )"
           "        ),"
           "        (cell: [4., 4., 4.] [angstrom], [4., 4., 4.][angstrom]),"
           "        (pbc: [true, true, true], [true, true, true])"
           ");"
           "algo_rdf = Algorithm RDF ((nbins: 2));"
           "prop_rdf = Property rdf, rdf_distance ((structure: h2o), (algorithm: algo_rdf));"
           "print(prop_rdf.rdf);"
           "print(prop_rdf.rdf_distance)")
    output = ("(rdf: [7.214905040899412, 0.5153503600642437], [7.214905040899412,"
              " 0.5153503600642437])\n(rdf_distance: [0.49, 1.47], [0.49, 1.47]) [angstrom]")
    prog = meta_model.model_from_str(inp, **model_kwargs)
    assert prog.value == output


def test_rdf_many_to_one(meta_model, model_kwargs):
    """test rdf algorithm in many-to-one relationship with structure"""
    inp = ("h2o = Structure water ("
           "        (atoms: ((symbols: 'O', 'H', 'H'),"
           "                 (x: 0., 0., 0.) [nm],"
           "                 (y: 0., 0.763239, -0.763239) [angstrom],"
           "                 (z: 0.119262, -0.477047, -0.477047) [angstrom]"
           "                ),"
           "                ((symbols: 'O', 'H', 'H'),"
           "                 (x: 0., 0., 0.) [nm],"
           "                 (y: 0., 0.763239, -0.763239) [angstrom],"
           "                 (z: 0.119262, -0.477047, -0.477047) [angstrom]"
           "                )"
           "        ),"
           "        (cell: [4., 4., 4.] [angstrom], [4., 4., 4.][angstrom]),"
           "        (pbc: [true, true, true], [true, true, true])"
           ");"
           "algo_rdf = Algorithm RDF, many_to_one ((nbins: 2));"
           "prop_rdf = Property rdf, rdf_distance ((structure: h2o), (algorithm: algo_rdf));"
           "print(prop_rdf.rdf);"
           "print(prop_rdf.rdf_distance)")
    output = ("(rdf: [7.214905040899412, 0.5153503600642437])\n(rdf_distance:"
              " [0.49, 1.47]) [angstrom]")
    prog = meta_model.model_from_str(inp, **model_kwargs)
    assert prog.value == output


def test_many_to_one_incorrect(meta_model, model_kwargs):
    """test algorithm with incorrect many-to-one relationship with structure"""
    inp = 'algo = Algorithm VelocityVerlet, many_to_one ((timestep: 1) [fs])'
    msg = 'Incorrect many-to-one relationship for algorithm "VelocityVerlet"'
    with pytest.raises(TextXError, match=msg) as err:
        meta_model.model_from_str(inp, **model_kwargs)
    assert isinstance(err.value.__cause__, StaticValueError)


def test_calculator_task_incorrect(meta_model, model_kwargs):
    """test algorithm with calculator task incompatible with algorithm"""
    inp = ('algo = Algorithm QuasiNewton ();'
           'calc = Calculator vasp (), task: local minimum;'
           'prop = Property energy ((calculator: calc), (algorithm: algo),'
           '                        (structure: struct));'
           'struct = Structure ((atoms: ((symbols: "H"), (x: 0.) [angstrom],'
           '                    (y: 0.) [angstrom], (z: 0.) [angstrom])))')
    msg = 'calculator task \"local minimum\" not compatible with algorithm \"QuasiNewton\"'
    with pytest.raises(TextXError, match=msg) as err:
        meta_model.model_from_str(inp, **model_kwargs)
    assert isinstance(err.value.__cause__, StaticValueError)


def test_algo_not_implemented(meta_model, model_kwargs):
    """test non-implemented algorithm"""
    with pytest.raises(TextXError, match='Algorithm "GA" is not implemented') as err:
        meta_model.model_from_str('algo = Algorithm GA ()', **model_kwargs)
    assert isinstance(err.value.__cause__, NotImplementedError)


def test_invalid_parameters_used_in_algorithm(meta_model, model_kwargs):
    """test invalid parameters used in algorithm"""
    inp = 'algo = Algorithm RDF ((blah: 4))'
    msg = r"Invalid parameters used in algorithm \"RDF\": \('blah'\,\)"
    with pytest.raises(TextXError, match=msg) as err:
        meta_model.model_from_str(inp, **model_kwargs)
    assert isinstance(err.value.__cause__, StaticValueError)


def test_mandatory_parameters_missing_in_algorithm(meta_model, model_kwargs):
    """test mandatory parameters missing in algorithm"""
    inp = 'algo = Algorithm VelocityVerlet ()'
    msg = r"Mandatory parameters missing in method \"VelocityVerlet\": \('timestep'\,\)"
    with pytest.raises(TextXError, match=msg) as err:
        meta_model.model_from_str(inp, **model_kwargs)
    assert isinstance(err.value.__cause__, StaticValueError)


def test_structure_intrinsic_properties(meta_model, model_kwargs):
    """test structure intrinsic properties"""
    inp = ("h2o = Structure H2O ("
           "        (atoms: ((symbols: 'O', 'H', 'H'),"
           "               (x: 6., 6.96504783, 5.87761163) [angstrom],"
           "               (y: 6., 5.87761163, 6.96504783) [angstrom],"
           "               (z: 6., 6.00000000, 6.00000000) [angstrom]"
           "              )"
           "        ),"
           "        (cell: [[12., 0., 0.], [0., 12., 0.], [0., 0., 12.]] [angstrom])"
           ");"
           "print(h2o.kinetic_energy);"
           "print(h2o.temperature);"
           "print(h2o.distance_matrix);"
           "print(h2o.chemical_formula);"
           "print(h2o.number_of_atoms);"
           "print(h2o.cell_volume);"
           "print(h2o.center_of_mass);"
           "print(h2o.radius_of_gyration);"
           "print(h2o.moments_of_inertia);"
           "print(h2o.angular_momentum)")
    ref = ("(kinetic_energy: 0.0) [electron_volt]\n"
           "(temperature: 0.0) [kelvin]\n"
           "(distance_matrix: [[0.0, 0.9727775836741742, 0.9727775836741742], "
           "[0.9727775836741742, 0.0, 1.5378670222554613], [0.9727775836741742,"
           " 1.5378670222554613, 0.0]]) [angstrom]\n"
           "(chemical_formula: 'H2O')\n"
           "(number_of_atoms: 3)\n"
           "(cell_volume: 1728.000000000001) [angstrom ** 3]\n"
           "(center_of_mass: [6.047149638394671, 6.047149638394671, 6.0]) [angstrom]\n"
           "(radius_of_gyration: 0.6878006359031348) [angstrom]\n"
           "(moments_of_inertia: [0.6356576901727511, 1.1919776289830035, "
           "1.8276353191557546]) [angstrom ** 2 * unified_atomic_mass_unit]\n"
           "(angular_momentum: [0.0, 0.0, 0.0]) [angstrom * electron_volt ** "
           "0.5 * unified_atomic_mass_unit ** 0.5]")
    prog = meta_model.model_from_str(inp, **model_kwargs)
    assert prog.value == ref


def test_structure_with_referenced_positions(meta_model, model_kwargs):
    """test structure with atoms table as tuple of references"""
    inp = ("epsilon_K = 119.8 [K]; kB = 1. [boltzmann_constant]; sigma = 3.405 [angstrom];"
           "h = sigma * 2**(1/2) / 2; x = map((x: x*h), (x: 0., 1., 1., 0.));"
           "y = map((y: y*h), (y: 0., 1., 0., 1.)); z = map((z: z*h), (z: 0., 0., 1., 1.));"
           "symbols = (symbols: 'Ar', 'Ar', 'Ar', 'Ar');"
           "calc = Calculator lj ((sigma: sigma) , (epsilon: epsilon_K*kB));"
           "struct = Structure fcc_Ar4 ("
           "     (atoms: Table (symbols, x, y, z)),"
           "     (pbc: [true, true, true]),"
           "     (cell: [[4.82, 0., 0.], [0., 4.82, 0.], [0., 0., 4.82]] [angstrom]));"
           "prop = Property energy, forces ((calculator: calc), (structure: struct));"
           "print(prop.structure.atoms[0].x)")
    ref = "(x: 0.0, 2.4076985899401944, 2.4076985899401944, 0.0) [angstrom]"
    assert meta_model.model_from_str(inp, **model_kwargs).value == ref


def test_structure_with_momenta(meta_model, model_kwargs):
    """test a structure with momenta"""
    inp = ("epsilon_K = 119.8 [K]; kB = 1. [boltzmann_constant]; sigma = 3.405 [angstrom];"
           "h = sigma * 2**(1/2) / 2; x = map((x: x*h), (x: 0., 1., 1., 0.));"
           "y = map((y: y*h), (y: 0., 1., 0., 1.)); z = map((z: z*h), (z: 0., 0., 1., 1.));"
           "symbols = (symbols: 'Ar', 'Ar', 'Ar', 'Ar');"
           "calc = Calculator lj ((sigma: sigma) , (epsilon: epsilon_K*kB));"
           "struct = Structure fcc_Ar4 ("
           "          (atoms: ("
           "            (symbols: 'Ar', 'Ar', 'Ar', 'Ar'),"
           "            (x: 0., 2.41, 2.41, 0.) [angstrom],"
           "            (y: 0., 2.41, 0., 2.41) [angstrom],"
           "            (z: 0., 0., 2.41, 2.41) [angstrom],"
           "            (px: 0.0, 0.0, 0.0, 0.0) [eV ** 0.5 * amu ** 0.5],"
           "            (py: 0.0, 0.0, 0.0, 0.0) [eV ** 0.5 * amu ** 0.5],"
           "            (pz: 0.0, 0.0, 0.0, 0.0) [eV ** 0.5 * amu ** 0.5])"
           "          ),"
           "     (pbc: [true, true, true]),"
           "     (cell: [[4.82, 0., 0.], [0., 4.82, 0.], [0., 0., 4.82]] [angstrom]));"
           "prop = Property energy, forces ((calculator: calc), (structure: struct));"
           "print(prop.structure.atoms[0].px)")
    ref = "(px: 0.0, 0.0, 0.0, 0.0) [electron_volt ** 0.5 * unified_atomic_mass_unit ** 0.5]"
    assert meta_model.model_from_str(inp, **model_kwargs).value == ref


def test_property_must_include_calc_or_algo(meta_model, model_kwargs):
    """test property must include calculator or algorithm"""
    inp = ("h = Structure hydrogen ((atoms: ((symbols: 'H'), (x: 0.0) [angstrom],"
           "    (y: 0.0) [angstrom], (z: 0.0) [angstrom] )));"
           "prop = Property energy ((structure: h))")
    msg = 'property must include either calculator or algorithm'
    with pytest.raises(TextXError, match=msg) as err:
        meta_model.model_from_str(inp, **model_kwargs)
    assert isinstance(err.value.__cause__, StaticValueError)


def test_property_not_available_in_algo(meta_model, model_kwargs):
    """test property not available in algorithm"""
    inp = ("h = Structure ((atoms: ((symbols: 'H'), (x: 0.0) [angstrom],"
           "    (y: 0.0) [angstrom], (z: 0.0) [angstrom])));"
           "algo = Algorithm RMSD ((reference: h));"
           "prop = Property rdf ((structure: h), (algorithm: algo))")
    msg = 'property "rdf" not available in algo "RMSD" or calc ""'
    with pytest.raises(TextXError, match=msg) as err:
        meta_model.model_from_str(inp, **model_kwargs)
    assert isinstance(err.value.__cause__, StaticValueError)


def test_property_not_available_in_algo_or_calc(meta_model, model_kwargs):
    """test property not available in algorithm or calculator"""
    inp = ("h = Structure ((atoms: ((symbols: 'H'), (x: 0.0) [angstrom],"
           "(y: 0.0) [angstrom], (z: 0.0) [angstrom]))); calc = Calculator emt ();"
           "algo = Algorithm VelocityVerlet ((timestep: 1) [fs]);"
           "prop = Property rdf ((structure: h), (algorithm: algo), (calculator: calc))")
    msg = 'property "rdf" not available in algo "VelocityVerlet" or calc "emt"'
    with pytest.raises(TextXError, match=msg) as err:
        meta_model.model_from_str(inp, **model_kwargs)
    assert isinstance(err.value.__cause__, StaticValueError)


def test_property_not_available_in_calc(meta_model, model_kwargs):
    """test property not available in calculator"""
    inp = ("h = Structure ((atoms: ((symbols: 'H'), (x: 0.0) [angstrom],"
           "(y: 0.0) [angstrom], (z: 0.0) [angstrom]))); calc = Calculator emt ();"
           "prop = Property magmoms ((structure: h), (calculator: calc))")
    msg = 'property "magmoms" not available in algo "" or calc "emt"'
    with pytest.raises(TextXError, match=msg) as err:
        meta_model.model_from_str(inp, **model_kwargs)
    assert isinstance(err.value.__cause__, StaticValueError)


def test_property_not_available_in_calculator_task(meta_model, model_kwargs):
    """test property not available in calculator task"""
    inp = ("h = Structure ((atoms: ((symbols: 'H'), (x: 0.0) [angstrom],"
           "(y: 0.0) [angstrom], (z: 0.0) [angstrom]))); calc = Calculator vasp (),"
           "task: single point;"
           "prop = Property transition_state ((structure: h), (calculator: calc))")
    msg = 'property "transition_state" not available in task "single point"'
    with pytest.raises(TextXError, match=msg) as err:
        meta_model.model_from_str(inp, **model_kwargs)
    assert isinstance(err.value.__cause__, StaticValueError)


def test_equation_of_state(meta_model, model_kwargs):
    """test equation of state algorithm"""
    inp = ("atoms = ((symbols: 'Ag'),"
           "         (x: 0.) [angstrom], (y: 0.) [angstrom], (z: 0.) [angstrom]);"
           "ag = Structure Ag ((atoms: atoms, atoms, atoms),"
           "       (pbc: [true, true, true], [true, true, true], [true, true, true]),"
           "       (cell: [[0., 1.9, 1.9], [1.9, 0., 1.9], [1.9, 1.9, 0.]] [angstrom],"
           "              [[0., 2.0, 2.0], [2.0, 0., 2.0], [2.0, 2.0, 0.]] [angstrom],"
           "              [[0., 2.1, 2.1], [2.1, 0., 2.1], [2.1, 2.1, 0.]] [angstrom]));"
           "calc = Calculator emt (), task: single point;"
           "prop_en = Property energy ((structure: ag), (calculator: calc));"
           "algo_eos = Algorithm EquationOfState, many_to_one"
           "                ((energies: prop_en.energy:array));"
           "prop_eos = Property minimum_energy, optimal_volume, bulk_modulus, eos_energy,"
           "                    eos_volume ((structure: ag), (algorithm: algo_eos));"
           "e0 = prop_eos.minimum_energy; b0 = prop_eos.bulk_modulus; v0 = prop_eos.optimal_volume")
    model = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', model)
    e0 = next(v for v in var_list if v.name == 'e0').value[0]
    assert e0.magnitude == pytest.approx(-0.002199121488192901)
    assert e0.units == 'electron_volt'
    v0 = next(v for v in var_list if v.name == 'v0').value[0]
    assert v0.magnitude == pytest.approx(16.818855657521432)
    assert v0.units == 'angstrom ** 3'
    b0 = next(v for v in var_list if v.name == 'b0').value[0]
    assert b0.magnitude == pytest.approx(0.6550203597842875)
    assert b0.units == 'electron_volt / angstrom ** 3'


def test_band_structure(meta_model, model_kwargs):
    """test band structure calculation"""
    inp = ("cu = Structure ((atoms: ((symbols: 'Cu'), (x: 0.) [angstrom], (y: 0.)"
           " [angstrom], (z: 0.) [angstrom])), (cell: [[0.0, 1.805, 1.805],"
           " [1.805, 0.0, 1.805], [1.805, 1.805, 0.0]] [angstrom]),"
           " (pbc: [true, true, true]));"
           "calc = Calculator free_electrons ((nvalence: 1), (kpts: ((path: 'GXWLGK'),"
           " (npoints: 10)))); algo = Algorithm BandStructure ();"
           "prop = Property band_structure ((structure: cu), (calculator: calc),"
           " (algorithm: algo)); bs = prop.band_structure[0].band_path[0].path")
    model = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', model)
    algo = next(v for v in var_list if v.name == 'algo').value
    algo_ref = 'Algorithm BandStructure ((emin: null), (emax: null), (filename: null))'
    assert formatter(algo) == algo_ref
    bs = next(v for v in var_list if v.name == 'bs').value
    assert formatter(bs) == "(path: 'GXWLGK')"


def test_view_amml_structure(meta_model, model_kwargs_no_display):
    """test view atomic structure"""
    inp = ("h = Structure H ((atoms: ((symbols: 'H'), (x: 0.) [angstrom],"
           " (y: 0.) [angstrom], (z: 0.) [angstrom])));"
           "view structure (h,)")
    assert meta_model.model_from_str(inp, **model_kwargs_no_display).value == ''


def test_view_amml_structure_with_constraints(meta_model, model_kwargs_no_display):
    """test view atomic structure with constraints"""
    inp = ("h = Structure H ((atoms: ((symbols: 'H'), (x: 0.) [angstrom],"
           " (y: 0.) [angstrom], (z: 0.) [angstrom])));"
           "view structure (h, (FixedAtoms where (fixed: true),))")
    assert meta_model.model_from_str(inp, **model_kwargs_no_display).value == ''


def test_view_amml_structure_wrong_par_len(meta_model, model_kwargs_no_display):
    """test view atomic structure with wrong number of parameters"""
    inp = 'view structure (1, 2, 3)'
    msg = 'view structure has maximum 2 parameters but 3 given'
    with pytest.raises(TextXError, match=msg) as err:
        meta_model.model_from_str(inp, **model_kwargs_no_display)
    assert isinstance(err.value.__cause__, StaticTypeError)


def test_view_amml_structure_wrong_first_par(meta_model, model_kwargs_no_display):
    """test view atomic structure with wrong first parameter"""
    inp = 'view structure (1, )'
    msg = 'parameter must be type AMMLStructure but is type Quantity'
    with pytest.raises(TextXError, match=msg) as err:
        meta_model.model_from_str(inp, **model_kwargs_no_display)
    assert isinstance(err.value.__cause__, StaticTypeError)


def test_view_amml_structure_wrong_second_par(meta_model, model_kwargs_no_display):
    """test view atomic structure with wrong type of second parameter"""
    inp = ("h = Structure H ((atoms: ((symbols: 'H'), (x: 0.) [angstrom],"
           " (y: 0.) [angstrom], (z: 0.) [angstrom]))); view structure (h, 1)")
    msg = 'parameter must be Tuple of constraints'
    with pytest.raises(TextXError, match=msg) as err:
        meta_model.model_from_str(inp, **model_kwargs_no_display)
    assert isinstance(err.value.__cause__, StaticTypeError)


def test_view_amml_structure_wrong_second_par_type(meta_model, model_kwargs_no_display):
    """test view atomic structure with a wrong type in second parameter"""
    inp = ("h = Structure H ((atoms: ((symbols: 'H'), (x: 0.) [angstrom],"
           " (y: 0.) [angstrom], (z: 0.) [angstrom]))); view structure (h, (1,))")
    msg = 'parameter must be type Constraint but is type Quantity'
    with pytest.raises(TextXError, match=msg) as err:
        meta_model.model_from_str(inp, **model_kwargs_no_display)
    assert isinstance(err.value.__cause__, StaticTypeError)


def test_view_equation_of_state(meta_model, model_kwargs_no_display):
    """test view equation of state"""
    inp = ("atoms = ((symbols: 'Ag'), (x: 0.) [angstrom], (y: 0.) [angstrom],"
           "(z: 0.) [angstrom]); ag = Structure Ag ((atoms: atoms, atoms, atoms),"
           " (pbc: [true, true, true], [true, true, true], [true, true, true]),"
           " (cell: [[0., 1.9, 1.9], [1.9, 0., 1.9], [1.9, 1.9, 0.]] [angstrom],"
           " [[0., 2.0, 2.0], [2.0, 0., 2.0], [2.0, 2.0, 0.]] [angstrom],"
           " [[0., 2.1, 2.1], [2.1, 0., 2.1], [2.1, 2.1, 0.]] [angstrom] ));"
           "calc = Calculator emt (), task: single point;"
           "prop = Property energy ((structure: ag), (calculator: calc));"
           "view eos (ag.cell_volume:array, prop.energy:array, 'sj')")
    assert meta_model.model_from_str(inp, **model_kwargs_no_display).value == ''


def test_view_band_structure(meta_model, model_kwargs_no_display, tmp_path):
    """test view band structure"""
    picture = os.path.join(tmp_path, 'band_structure.png')
    inp = ("cu = Structure ((atoms: ((symbols: 'Cu'), (x: 0.) [angstrom], (y: 0.)"
           " [angstrom], (z: 0.) [angstrom])), (cell: [[0.0, 1.805, 1.805], [1.805,"
           " 0.0, 1.805], [1.805, 1.805, 0.0]] [angstrom]), (pbc: [true, true, true]));"
           "calc = Calculator free_electrons ((nvalence: 1), (kpts: ((path: 'GXWLGK'),"
           f" (npoints: 200)))); algo = Algorithm BandStructure ((filename: '{picture}'));"
           "prop = Property band_structure ((structure: cu), (calculator: calc), "
           "(algorithm: algo)); view bs (prop.band_structure[0], ((emin: 0) [eV], "
           "(emax: 20) [eV]))")
    assert meta_model.model_from_str(inp, **model_kwargs_no_display).value == ''


def test_property_not_available_missing_in_prop(meta_model, model_kwargs):
    """test property not available when not requested in Property statement"""
    inp = ("h2o = Structure water ("
           "       (atoms: ((symbols: 'O', 'H', 'H'),"
           "                (x: 0., 0., 0.) [nm],"
           "                (y: 0., 0.763239, -0.763239) [angstrom],"
           "                (z: 0.119262, -0.477047, -0.477047) [angstrom])));"
           "calc = Calculator emt (), task: single point;"
           "algo = Algorithm BFGS ((trajectory: true));"
           "prop = Property energy ((structure: h2o),(calculator: calc),"
           "                        (algorithm: algo));"
           "traj = prop.trajectory; ene = prop.energy; forces = prop.forces")
    model = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', model)
    ene = next(v for v in var_list if v.name == 'ene').value[0]
    assert ene.magnitude == pytest.approx(1.8792752663147128)
    assert ene.units == 'electron_volt'
    with pytest.raises(TextXError, match='property "forces" not available') as err:
        _ = next(v for v in var_list if v.name == 'forces').value
    assert isinstance(err.value.__cause__, PropertyError)
    with pytest.raises(TextXError, match='property "trajectory" not available') as err:
        _ = next(v for v in var_list if v.name == 'traj').value
    assert isinstance(err.value.__cause__, PropertyError)


def test_property_not_available_missing_in_algo(meta_model, model_kwargs):
    """test property not available when not requested in Algorithm statement"""
    inp = ("h2o = Structure water ("
           "       (atoms: ((symbols: 'O', 'H', 'H'),"
           "                (x: 0., 0., 0.) [nm],"
           "                (y: 0., 0.763239, -0.763239) [angstrom],"
           "                (z: 0.119262, -0.477047, -0.477047) [angstrom])));"
           "calc = Calculator emt (), task: single point;"
           "algo = Algorithm BFGS ();"
           "prop = Property trajectory ((structure: h2o), (calculator: calc),"
           "                            (algorithm: algo))")
    model = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', model)
    with pytest.raises(TextXError, match='property "trajectory" not available') as err:
        _ = next(v for v in var_list if v.name == 'prop').value
    assert isinstance(err.value.__cause__, PropertyError)


def test_property_with_missing_calculator(meta_model, model_kwargs):
    """test property with missing calculator"""
    inp = ("h2o = Structure water ("
           "       (atoms: ((symbols: 'O', 'H', 'H'),"
           "                (x: 0., 0., 0.) [nm],"
           "                (y: 0., 0.763239, -0.763239) [angstrom],"
           "                (z: 0.119262, -0.477047, -0.477047) [angstrom])));"
           "algo = Algorithm VelocityVerlet ((timestep: 1.) [fs]);"
           "prop = Property trajectory ((structure: h2o), (algorithm: algo))")
    msg = 'property needs a calculator for algorithm "VelocityVerlet"'
    with pytest.raises(TextXError, match=msg) as err:
        meta_model.model_from_str(inp, **model_kwargs)
    assert isinstance(err.value.__cause__, StaticValueError)


def test_could_not_find_dtype_for_type(meta_model, model_kwargs):
    """test evaluating mistyped non-existent properties"""
    inp = "algo = Algorithm BFGS (); t = algo.blah"
    msg = "could not find DType for type: AMMLAlgorithm, basetype: None, id_: blah"
    with pytest.raises(TextXError, match=msg) as err:
        meta_model.model_from_str(inp, **model_kwargs)
    assert isinstance(err.value.__cause__, StaticTypeError)


def test_invalid_parameters_used_in_calculator(meta_model, model_kwargs):
    """test invalid parameters used in calculator"""
    inp = 'calc = Calculator emt ((blah: 4))'
    msg = r"Invalid parameters used in calculator: \('blah'\,\)"
    with pytest.raises(TextXError, match=msg) as err:
        meta_model.model_from_str(inp, **model_kwargs)
    assert isinstance(err.value.__cause__, StaticValueError)


def test_invalid_parameter_type_in_method(meta_model, model_kwargs):
    """test invalid parameter type in method"""
    inp = "calc = Calculator emt ((asap_cutoff: '4'))"
    msg = r'invalid parameter type in method "emt": "asap_cutoff" must be Boolean'
    with pytest.raises(TextXError, match=msg) as err:
        meta_model.model_from_str(inp, **model_kwargs)
    assert isinstance(err.value.__cause__, StaticTypeError)


def test_invalid_units_of_parameter(meta_model, model_kwargs):
    """test invalid units of parameters in methods"""
    inp = 'calc = Calculator free_electrons ((gridsize: 4) [meter])'
    msg = (r'error with units of parameter "gridsize": must be \[dimensionless\]'
           r' instead of \[meter\]')
    with pytest.raises(TextXError, match=msg) as err:
        meta_model.model_from_str(inp, **model_kwargs)
    assert isinstance(err.value.__cause__, InvalidUnitError)


def test_stress_tensor_property(meta_model, model_kwargs):
    """test computing the stress tensor in voigt notation"""
    inp = ("cu = Structure ((atoms: ((symbols: 'Cu'), (x: 0.) [angstrom], (y: 0.)"
           " [angstrom], (z: 0.) [angstrom])), (cell: [[0.0, 1.805, 1.805], [1.805,"
           " 0.0, 1.805], [1.805, 1.805, 0.0]] [angstrom]), (pbc: [true, true, true]));"
           "calc = Calculator emt (), task: single point;"
           "prop = Property stress ((structure: cu), (calculator: calc));"
           "stress = prop.stress")
    model = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', model)
    stress = next(v for v in var_list if v.name == 'stress')
    assert stress.value[0].units == 'electron_volt / angstrom ** 3'
    assert stress.value[0].magnitude[0] == pytest.approx(0.013619265229937932)


def test_rmsd_property(meta_model, model_kwargs):
    """test computing the rmsd of a molecule from a reference geometry"""
    inp = ("h2o = Structure ((atoms: ((symbols: 'O', 'H', 'H'), (x: 0., 0., 0.) [nm],"
           "(y: 0., 0.763239, -0.763239) [angstrom], (z: 0.119262, -0.477047, "
           "-0.477047) [angstrom]))); algo = Algorithm RMSD ((reference: h2o));"
           "prop = Property rmsd ((structure: h2o), (algorithm: algo));"
           "rmsd = prop.rmsd")
    model = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', model)
    rmsd = next(v for v in var_list if v.name == 'rmsd')
    assert rmsd.value[0].units == 'angstrom'
    assert rmsd.value[0].magnitude == pytest.approx(0)


def test_dimer_algo(meta_model, model_kwargs_no_display):
    """run a test of the dimer method and viewer"""
    inp = ("use len from builtins;"
           "initial = Structure ((atoms: ("
           " (symbols: 'Pt', 'Pt', 'Pt', 'Pt', 'Pt'),"
           " (x: 0.0, 2.77185858, 0.0, 2.77185858, 1.38592929) [angstrom],"
           " (y: 0.0, 0.0, 2.77185858, 2.77185858, 1.38592929) [angstrom],"
           " (z: 10.0, 10.0, 10.0, 10.0, 11.611) [angstrom],"
           " (tags: 1, 1, 1, 1, 0))), (cell: [[5.5437171645025325, 0.0, 0.0],"
           " [0.0, 5.5437171645025325, 0.0], [0.0, 0.0, 20.0]]) [angstrom],"
           " (pbc: [true, true, false]));"
           "calc = Calculator emt (); natoms = len(initial.atoms);"
           "fixed = map((x: x > 0), initial.atoms[0].tags); constr = FixedAtoms where fixed;"
           "prop_i = Property energy ((structure: initial), (calculator: calc));"
           "dimer = Algorithm Dimer ((trajectory: true), (eigenmode_method: 'dimer'));"
           "prop_d = Property energy, trajectory ((structure: initial), (calculator: calc),"
           "                          (algorithm: dimer), (constraints: (constr,)));"
           "act_energy = prop_d.energy[0] - prop_i.energy[0];"
           "view trajectory (prop_d.trajectory[0],)")
    model = meta_model.model_from_str(inp, **model_kwargs_no_display)
    var_list = get_children_of_type('Variable', model)
    act_energy = next(v for v in var_list if v.name == 'act_energy')
    assert act_energy.value.units == 'electron_volt'
    # assert act_energy.value.magnitude == pytest.approx(1.0366, 5e-3)  # random result
    assert model.value == ''  # trigger processing the view statement


def test_dimer_algo_displacement_vector(meta_model, model_kwargs):
    """run a test of the dimer method with displacement vector"""
    inp = ("use len from builtins;"
           "initial = Structure ((atoms: ("
           " (symbols: 'Pt', 'Pt', 'Pt', 'Pt', 'Pt'),"
           " (x: 0.0, 2.77185858, 0.0, 2.77185858, 1.38592929) [angstrom],"
           " (y: 0.0, 0.0, 2.77185858, 2.77185858, 1.38592929) [angstrom],"
           " (z: 10.0, 10.0, 10.0, 10.0, 11.611) [angstrom],"
           " (tags: 1, 1, 1, 1, 0))), (cell: [[5.5437171645025325, 0.0, 0.0],"
           " [0.0, 5.5437171645025325, 0.0], [0.0, 0.0, 20.0]]) [angstrom],"
           " (pbc: [true, true, false]));"
           "calc = Calculator emt (); natoms = len(initial.atoms);"
           "fixed = map((x: x > 0), initial.atoms[0].tags); constr = FixedAtoms where fixed;"
           "prop_i = Property energy ((structure: initial), (calculator: calc));"
           "dimer = Algorithm Dimer ((displacement_method: 'vector'), (target: initial));"
           "prop_d = Property energy ((structure: initial), (calculator: calc),"
           "                          (algorithm: dimer), (constraints: (constr,)));"
           "act_energy = prop_d.energy[0] - prop_i.energy[0]")
    model = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', model)
    act_energy = next(v for v in var_list if v.name == 'act_energy')
    assert act_energy.value.units == 'electron_volt'
    assert act_energy.value.magnitude == pytest.approx(1.0366, 5e-3)


def test_dimer_algo_missing_target(meta_model, model_kwargs):
    """run a test of the dimer method with missing target structure"""
    inp = ("initial = Structure ((atoms: ("
           " (symbols: 'Pt', 'Pt', 'Pt', 'Pt', 'Pt'),"
           " (x: 0.0, 2.77185858, 0.0, 2.77185858, 1.38592929) [angstrom],"
           " (y: 0.0, 0.0, 2.77185858, 2.77185858, 1.38592929) [angstrom],"
           " (z: 10.0, 10.0, 10.0, 10.0, 11.611) [angstrom])),"
           " (cell: [[5.5437171645025325, 0.0, 0.0], [0.0, 5.5437171645025325,"
           " 0.0], [0.0, 0.0, 20.0]]) [angstrom], (pbc: [true, true, false]));"
           "dimer = Algorithm Dimer ((displacement_method: 'vector'));"
           "prop_d = Property energy ((structure: initial), (calculator: calc),"
           " (algorithm: dimer)); calc = Calculator emt ()")
    model = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', model)
    prop_d = next(v for v in var_list if v.name == 'prop_d')
    msg = "target structure needed to calculate displacement vector"
    with pytest.raises(TextXError, match=msg) as err:
        _ = prop_d.value
    assert isinstance(err.value.__cause__, RuntimeValueError)


def test_neb_algo(meta_model, model_kwargs_no_display, tmp_path):
    """run a test of the NEB method and viewer"""
    picture = os.path.join(tmp_path, 'test_neb.png')
    inp = ("if_neb = Structure ("
           "       (atoms: ((symbols: 'Pt', 'Pt', 'Pt', 'Pt', 'Pt'),"
           "                (x: 0.0, 2.77185858, 0.0, 2.77185858, 1.38592929) [angstrom],"
           "                (y: 0.0, 0.0, 2.77185858, 2.77185858, 1.38592929) [angstrom],"
           "                (z: 10.0, 10.0, 10.0, 10.0, 11.611) [angstrom],"
           "                (tags: 1, 1, 1, 1, 0)),"
           "               ((symbols: 'Pt', 'Pt', 'Pt', 'Pt', 'Pt'),"
           "                (x: 0.0, 2.77185858, 0.0, 2.77185858, 4.15778787) [angstrom],"
           "                (y: 0.0, 0.0, 2.77185858, 2.77185858, 1.38592929) [angstrom],"
           "                (z: 10.0, 10.0, 10.0, 10.0, 11.611) [angstrom],"
           "                (tags: 1, 1, 1, 1, 0))),"
           "       (cell: [[5.5437171645025325, 0.0, 0.0], [0.0, 5.5437171645025325, 0.0],"
           "               [0.0, 0.0, 20.0]], [[5.5437171645025325, 0.0, 0.0],"
           "               [0.0, 5.5437171645025325, 0.0], [0.0, 0.0, 20.0]]) [angstrom],"
           "       (pbc: [true, true, false], [true, true, false]));"
           "mask = map((x: x > 1), if_neb.atoms[0].tags); constr = FixedAtoms where mask;"
           "neb = Algorithm NEB, many_to_one ((optimizer: ((name: 'BFGS'))),"
           f"                                 (filename: '{picture}'));"
           "prop = Property activation_energy, trajectory"
           "            ((structure: if_neb), (calculator: calc),"
           "             (algorithm: neb), (constraints: (constr,)));"
           "ae = prop.activation_energy; calc = Calculator emt ();"
           "view neb (prop.trajectory[0])")
    model = meta_model.model_from_str(inp, **model_kwargs_no_display)
    var_list = get_children_of_type('Variable', model)
    act_energy = next(v for v in var_list if v.name == 'ae')
    assert act_energy.value[0].units == 'electron_volt'
    assert act_energy.value[0].magnitude == pytest.approx(0.665, 1e-3)
    assert model.value == ''  # trigger processing the view statement


def test_dyn_neb_algo(meta_model, model_kwargs):
    """run a test of the NEB method with dynamic relaxation"""
    inp = ("if_neb = Structure ("
           "       (atoms: ((symbols: 'Pt', 'Pt', 'Pt', 'Pt', 'Pt'),"
           "                (x: 0.0, 2.77185858, 0.0, 2.77185858, 1.38592929) [angstrom],"
           "                (y: 0.0, 0.0, 2.77185858, 2.77185858, 1.38592929) [angstrom],"
           "                (z: 10.0, 10.0, 10.0, 10.0, 11.611) [angstrom],"
           "                (tags: 1, 1, 1, 1, 0)),"
           "               ((symbols: 'Pt', 'Pt', 'Pt', 'Pt', 'Pt'),"
           "                (x: 0.0, 2.77185858, 0.0, 2.77185858, 4.15778787) [angstrom],"
           "                (y: 0.0, 0.0, 2.77185858, 2.77185858, 1.38592929) [angstrom],"
           "                (z: 10.0, 10.0, 10.0, 10.0, 11.611) [angstrom],"
           "                (tags: 1, 1, 1, 1, 0))),"
           "       (cell: [[5.5437171645025325, 0.0, 0.0], [0.0, 5.5437171645025325, 0.0],"
           "               [0.0, 0.0, 20.0]], [[5.5437171645025325, 0.0, 0.0],"
           "               [0.0, 5.5437171645025325, 0.0], [0.0, 0.0, 20.0]]) [angstrom],"
           "       (pbc: [true, true, false], [true, true, false]));"
           "mask = map((x: x > 1), if_neb.atoms[0].tags); constr = FixedAtoms where mask;"
           "neb = Algorithm NEB, many_to_one ((dynamic_relaxation: true),"
           "                                  (fmax: 0.05) [eV/angstrom],"
           "                                  (scale_fmax: 0.1) [1/angstrom],"
           "                                  (optimizer: ((name: 'BFGS'))));"
           "prop = Property activation_energy, trajectory"
           "            ((structure: if_neb), (calculator: calc),"
           "             (algorithm: neb), (constraints: (constr,)));"
           "ae = prop.activation_energy; calc = Calculator emt ()")
    model = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', model)
    act_energy = next(v for v in var_list if v.name == 'ae')
    assert act_energy.value[0].units == 'electron_volt'
    assert act_energy.value[0].magnitude == pytest.approx(0.665, 1e-3)


def test_trajectory_with_fixedline_constraints(meta_model, model_kwargs):
    """test trajectory with fixedline constraints"""
    inp = ("h2 = Structure ((atoms: ((symbols: 'H', 'H'), (x: 0.0, 0.0) [angstrom],"
           "(y: 0.0, 0.0) [angstrom], (z: 0.0, 1.0) [angstrom])),"
           "(cell: [[5.0, 0.0, 0.0], [0.0, 5.0, 0.0], [0.0, 0.0, 5.0]]) [angstrom],"
           "(pbc: [true, true, true]));"
           "line = FixedLine collinear to [0, 0, 1] where (fixed: true, true);"
           "calc = Calculator emt();"
           "algo = Algorithm VelocityVerlet ((timestep: 1) [fs], (steps: 1), (trajectory: true));"
           "prop = Property trajectory ((calculator: calc), (structure: h2),"
           "                            (algorithm: algo), (constraints: (line,)));"
           "print(prop.trajectory[0].constraints);"
           "print(prop.trajectory[0][:1], prop.trajectory[0][0])")
    ref = "constraints: (FixedLine collinear to [0.0, 0.0, 1.0] where (fixed: true, true),), ("
    assert ref in meta_model.model_from_str(inp, **model_kwargs).value


def test_vibrations_algo(meta_model, model_kwargs_no_display):
    """run a test of the Vibrations algorithm"""
    inp = ("h2o = Structure H2O ("
           "     (atoms: ((symbols: 'O', 'H', 'H'),"
           "              (x: 6., 6.96504783, 5.87761163) [angstrom],"
           "              (y: 6., 5.87761163, 6.96504783) [angstrom],"
           "              (z: 6., 6.00000000, 6.00000000) [angstrom])));"
           "constr = FixedAtoms where (fix: true, false, false);"
           "calc = Calculator emt ();"
           "algo_opt = Algorithm BFGS ((fmax: 0.001) [eV/angstrom]);"
           "props_opt = Property energy, forces"
           "  ((structure: h2o),"
           "   (calculator: calc),"
           "   (algorithm: algo_opt),"
           "   (constraints: (constr,)));"
           "algo_vib = Algorithm Vibrations ();"
           "props_vib = Property hessian, vibrational_energies, vibrational_modes,"
           "                     transition_state, energy_minimum"
           "    ((structure: props_opt.output_structure),"
           "     (calculator: calc),"
           "     (algorithm: algo_vib),"
           "     (constraints: (constr,)));"
           "v_enes = props_vib.vibrational_energies;"
           "ts = props_vib.transition_state; em = props_vib.energy_minimum;"
           "view vibration (props_opt.output_structure, props_vib.hessian,"
           "                ((mode: -1), (constraints: (constr,))))")
    model = meta_model.model_from_str(inp, **model_kwargs_no_display)
    var_list = get_children_of_type('Variable', model)
    v_enes = next(v for v in var_list if v.name == 'v_enes')
    ts = next(v for v in var_list if v.name == 'ts')
    em = next(v for v in var_list if v.name == 'em')
    assert v_enes.value[0].values[-1].units == 'electron_volt'
    assert v_enes.value[0].values[-1].magnitude == pytest.approx(0.377, 1e-3)
    assert em.value[0]
    assert not ts.value[0]
    assert model.value == ''  # trigger processing the view statement


def test_neighborlist(meta_model, model_kwargs):
    """test the neighborlist algorithms"""
    inp = ("h2o = Structure water ("
           "      (atoms: ((symbols: 'O', 'H', 'H'),"
           "               (x: 0., 0., 0.) [nm],"
           "               (y: 0., 0.763239, -0.763239) [angstrom],"
           "               (z: 0.119262, -0.477047, -0.477047) [angstrom])));"
           "algo_nl = Algorithm NeighborList ((self_interaction: false),"
           "                                  (bothways: true));"
           "prop_nl = Property neighbors, neighbor_offsets, connectivity_matrix,"
           "                   connected_components ((algorithm: algo_nl), (structure: h2o));"
           "print(algo_nl); print(prop_nl.neighbors); print(prop_nl.neighbor_offsets);"
           "print(prop_nl.connectivity_matrix); print(prop_nl.connected_components)")
    model = meta_model.model_from_str(inp, **model_kwargs)
    ref = ("Algorithm NeighborList ((self_interaction: false), (bothways: true))\n"
           "(neighbors: ([1, 2], [0], [0]))\n"
           "(neighbor_offsets: ([[0, 0, 0], [0, 0, 0]] [angstrom], "
           "[[0, 0, 0]] [angstrom], [[0, 0, 0]] [angstrom]))\n"
           "(connectivity_matrix: [[0, 1, 1], [1, 0, 0], [1, 0, 0]])\n"
           "(connected_components: [0, 0, 0])")
    assert model.value == ref


def test_algorithm_invalid_string_parameter(meta_model, model_kwargs):
    """test algorithm with parameters from a list of valid choices"""
    inp = "a = Algorithm VelocityDistribution ((distribution: 'blah'), (temperature_K: 1) [K])"
    msg = (r'Parameter \"distribution\" should be one of \[\'maxwell-boltzmann\','
           r' \'phonon_harmonics\'\] but is blah')
    with pytest.raises(TextXError, match=msg) as err:
        meta_model.model_from_str(inp, **model_kwargs)
    assert isinstance(err.value.__cause__, StaticValueError)
