"""
tests for chemistry objects and operations
"""
import pytest
from textx import get_children_of_type
from textx.exceptions import TextXError
from virtmat.language.utilities.errors import StaticTypeError, StaticValueError
from virtmat.language.utilities.errors import RuntimeValueError
from virtmat.language.utilities.warnings import TextSUserWarning
from virtmat.language.utilities.formatters import formatter


def test_chem_species(meta_model, model_kwargs):
    """test chemical species"""
    inp = ("c = 'H2'; H2 = Species H2, composition: c ((energy: 1.) [eV],"
           "(zpe: 0.270) [eV]); print(H2); print(H2.properties);"
           "print(H2.composition)")
    ref = ("Species H2, composition: 'H2' ((energy: 1.0) [electron_volt], (zpe: "
           "0.27) [electron_volt], (enthalpy: 1.27) [electron_volt])\n"
           "((energy: 1.0) [electron_volt], (zpe: 0.27) [electron_volt], "
           "(enthalpy: 1.27) [electron_volt])\n'H2'")
    assert meta_model.model_from_str(inp, **model_kwargs).value == ref


def test_species_composition_ref_wrong_type(meta_model, model_kwargs):
    """check species composition reference of wrong type"""
    inp = 'c = true; H2 = Species H2, composition: c'
    msg = 'species composition must be of string type'
    with pytest.raises(TextXError, match=msg) as err:
        meta_model.model_from_str(inp, **model_kwargs)
    assert isinstance(err.value.__cause__, StaticTypeError)


def test_chemistry_chem_reaction(meta_model, model_kwargs):
    """test chemical reactions and chemical species"""
    inp = (
        "h2o_energy = 0. [eV];"
        "h2_energy  = 0. [eV];"
        "orr_free = -4.916 [eV];"
        "orr = Reaction 2 H2 + O2 = 2 H2O: ((temperature: 298.15) [K]);"
        "H2O = Species H2O ("
        "    (energy: h2o_energy),"
        "    (entropy: 2.1669e-3) [eV/K],"
        "    (zpe: 0.558) [eV],"
        "    (temperature: 298.15) [K]"
        ");"
        "H2 = Species H2 ("
        "    (energy: h2_energy),"
        "    (zpe: 0.270) [eV],"
        "    (entropy: 1.3613e-3) [eV/K],"
        "    (temperature: 298.15) [K]"
        ");"
        "O2 = Species O2 ("
        "    (free_energy: 2.*H2O.free_energy[0] - 2.*H2.free_energy[0] - orr_free),"
        "    (entropy: 2.1370e-3) [eV/K],"
        "    (zpe: 0.098) [eV],"
        "    (temperature: 298.15) [K]"
        ");"
        "orr_free_energy_correct = orr.free_energy[0] == orr_free"
    )
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    assert next(v for v in var_list if v.name == 'orr_free_energy_correct').value


def test_chemistry_property_table(meta_model, model_kwargs):
    """test property table from chemical reactions and chemical species"""
    inp = (
        "H2O = Species H2O ("
        "   (free_energy: -14.739080832009071, -14.994145508249682) [eV],"
        "   (temperature: 500., 600.) [K]);"
        "water_props = H2O.properties;"
        "q1 = water_props select free_energy where column:temperature == 500. [K];"
        "q2 = water_props where column:free_energy < -14.8 [eV];"
        "MO = Species MO; M = Species M; H2 = Species H2;"
        "R1 = Reaction MO + H2 = M + H2O : ("
        "   (free_energy: -1., -2.) [eV],"
        "   (temperature: 500., 600.) [K]);"
        "q3 = R1.properties where column:temperature > 550 [kelvin];"
        "print(q1, q2, q3)"
    )
    ref = ("((free_energy: -14.739080832009071) [electron_volt]) ((free_energy: "
           "-14.994145508249682) [electron_volt], (temperature: 600.0) [kelvin])"
           " ((free_energy: -2.0) [electron_volt], (temperature: 600.0) [kelvin])")
    prog = meta_model.model_from_str(inp, **model_kwargs)
    assert prog.value == ref


def test_reaction_not_balanced(meta_model, model_kwargs):
    """test reaction equation that is not balanced"""
    inp = ("r = Reaction H2 + O2 -> H2O;"
           "H2O = Species H2O, composition: 'H2O';"
           "H2 = Species H2, composition: 'H2';"
           "O2 = Species O2, composition: 'O2'")
    msg = 'Reaction equation is not balanced.'
    with pytest.raises(TextXError, match=msg) as err:
        meta_model.model_from_str(inp, **model_kwargs)
    assert isinstance(err.value.__cause__, StaticValueError)


def test_reaction_not_balanced_composition_ref(meta_model, model_kwargs):
    """check reaction equation not balanced with composition reference"""
    inp = ("water_comp = 'H3O'; r = Reaction 2 H2 + O2 -> 2 H2O;"
           "H2O = Species H2O, composition: water_comp;"
           "H2 = Species H2, composition: 'H2';"
           "O2 = Species O2, composition: 'O2'")
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    with pytest.raises(TextXError, match='Reaction equation is not balanced.') as err:
        _ = next(v for v in var_list if v.name == 'r').value
    assert isinstance(err.value.__cause__, RuntimeValueError)


def test_reaction_balance_check_skipped(meta_model, model_kwargs):
    """test when the reaction equation balance check is skipped"""
    inp = ("r = Reaction 2 H2 + O2 -> 2 H2O; H2O = Species H2O;"
           "H2 = Species H2, composition: 'H2'; O2 = Species O2, composition: 'O2'")
    msg = 'reaction balance check skipped due to missing composition'
    with pytest.warns(TextSUserWarning, match=msg):
        meta_model.model_from_str(inp, **model_kwargs)


def test_chem_species_iterable(meta_model, model_kwargs):
    """test chemical species used as iterable"""
    inp = ('w = Species H2O ((free_energy: -14.739080832009071, -14.994145508249682) [eV],'
           '(temperature: 500., 600.) [K]);'
           'w_ = w select free_energy where column:temperature == 500. [K]')
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    ref = 'Species H2O ((free_energy: -14.739080832009071) [electron_volt])'
    assert formatter(next(v for v in var_list if v.name == 'w_').value) == ref


def test_chem_species_iterable_filter_map_reduce(meta_model, model_kwargs):
    """test chemical species used as iterable in filter, map and reduce"""
    inp = ('w = Species H2O ((free_energy: -14.739080832009071, -14.994145508249682) [eV],'
           '(temperature: 500., 600.) [K]); max(x, y) = if(y > x, y, x);'
           'w_f = filter((x: x.temperature == 500.0 [K]), w);'
           'w_m = map((x: {free_energy: x.free_energy}), w_f);'
           'w_r = reduce((x, y: {temperature: max(x.temperature, y.temperature)}), w)')
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    w_f_ref = ('Species H2O ((free_energy: -14.739080832009071) [electron_volt], '
               '(temperature: 500.0) [kelvin])')
    w_m_ref = '((free_energy: -14.739080832009071) [electron_volt])'
    w_r_ref = '((temperature: 600.0) [kelvin])'
    assert formatter(next(v for v in var_list if v.name == 'w_f').value) == w_f_ref
    assert formatter(next(v for v in var_list if v.name == 'w_m').value) == w_m_ref
    assert formatter(next(v for v in var_list if v.name == 'w_r').value) == w_r_ref


ORR_INP = (
  'use exp, log from numpy;'
  'temperature = 298.15 [K];'
  'kB = 1 [boltzmann_constant];'
  'zpe_f(vib_ener) = 0.5*sum(vib_ener);'
  'beta = 1.0/(kB*temperature);'
  'exp_hob(ene) = exp(-ene*beta);'
  'entr(ene, exp_hob) = ene * beta * exp_hob / (1.0-exp_hob) - log(1.0-exp_hob);'
  'vib_entr_f(vib_energies) = kB * sum(map(entr, vib_energies, map(exp_hob, vib_energies)));'
  'energy_    = -153.78488212 [electron_volt];'
  'energy_O   = -160.02030190 [electron_volt];'
  'energy_OH  = -163.59352476 [electron_volt];'
  'energy_OOH = -167.86220067 [electron_volt];'
  'vib_ener_O = (vibrational_energies: 0.055954544, 0.045046768, 0.044947491) [electron_volt];'
  'vib_ener_OH = (vibrational_energies: 0.449608408, 0.067996806, 0.06709252600000001,'
  '               0.042573099999999996, 0.021048982, 0.02020558) [electron_volt];'
  'vib_ener_OOH = (vibrational_energies: 0.448162632, 0.142670432, 0.042869318999999996,'
  '                0.042677173000000006, 0.039394802, 0.028062200000000002,'
  '                0.017229372000000003, 0.0059731129999999995, 0.002726201) [electron_volt];'
  'H2O = Species H2O ((energy: -14.22696993) [electron_volt], (zpe: 0.558) [eV],'
  '      (entropy: 2.1669e-3) [eV/K], (temperature: temperature));'
  'H2 = Species H2 ((energy: -6.75996823) [electron_volt], (zpe: 0.270) [eV],'
  '      (entropy: 1.3613e-3) [eV/K], (temperature: temperature));'
  'O2 = Species O2 ('
  '    (free_energy: 2.*H2O.free_energy[0] - 2.*H2.free_energy[0] + 4.916 [eV]),'
  '    (zpe: 0.098) [eV], (entropy: 2.1370e-3) [eV/K], (temperature: temperature));'
  'M = Species M ((energy: energy_ ), (zpe: 0.0) [eV], (entropy: 0.0) [eV/K],'
  '               (temperature: temperature));'
  'MO = Species MO ((energy: energy_O), (zpe: zpe_f(vib_ener_O)),'
  '                 (entropy: vib_entr_f(vib_ener_O)), (temperature: temperature));'
  'MOH = Species MOH ((energy: energy_OH), (zpe: zpe_f(vib_ener_OH)),'
  '                   (entropy: vib_entr_f(vib_ener_OH)), (temperature: temperature));'
  'MOOH = Species MOOH ((energy: energy_OOH), (zpe: zpe_f(vib_ener_OOH)),'
  '       (entropy: vib_entr_f(vib_ener_OOH)), (temperature: temperature));'
  'orr1 = Reaction M + O2 + 0.5 H2 = MOOH;'
  'orr2 = Reaction MOOH + 0.5 H2 = MO + H2O;'
  'orr3 = Reaction MO + 0.5 H2 = MOH;'
  'orr4 = Reaction MOH + 0.5 H2 = M + H2O;'
  'view waterfall((reactions: orr1, orr2, orr3, orr4), "oer");'
  'view waterfall((reactions: orr1, orr2, orr3, orr4), "orr")'
)


def test_reaction_waterfall_diagaram(meta_model, model_kwargs_no_display):
    """test constructing and viewing waterfall diagram"""
    inp = ORR_INP
    prog = meta_model.model_from_str(inp, **model_kwargs_no_display)
    _ = prog.value
