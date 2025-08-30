"""
tests cyclic dependencies
"""
import pytest
from virtmat.language.constraints.processors import add_constraints_processors
from virtmat.language.constraints.cyclic import CyclicDependencyError


@pytest.fixture(name='meta_model')
def fixture_metamodel(raw_meta_model):
    """parse the grammar and generate the object classes"""
    add_constraints_processors(raw_meta_model)
    return raw_meta_model


def test_zeroth_order_cyclic(meta_model):
    """test zeroth order cycic dependencies (one-node loop)"""
    inp = 'd = d + 3 \n'
    with pytest.raises(CyclicDependencyError):
        meta_model.model_from_str(inp)


def test_first_order_cyclic(meta_model):
    """test first order cycic dependencies (two-nodes loop)"""
    inp = 'f = 3 * g; g = f + 1 \n'
    with pytest.raises(CyclicDependencyError):
        meta_model.model_from_str(inp)


def test_second_order_cyclic(meta_model):
    """test second order cycic dependencies (three-nodes loop)"""
    inp = 'a = 3 + c; c = 4 * b; b = 1 / a \n'
    with pytest.raises(CyclicDependencyError):
        meta_model.model_from_str(inp)


def test_second_order_cyclic_boolean(meta_model):
    """test second order cycic dependencies with boolean variables"""
    inp = 'a = true and c; c = not b; b = false or a \n'
    with pytest.raises(CyclicDependencyError):
        meta_model.model_from_str(inp)


def test_function_zeroth_order_cyclic(meta_model):
    """test second order cycic dependencies - deepcopy fails"""
    inp = 'cube(x) = x*x*x; a = cube(2+a) \n'
    with pytest.raises(CyclicDependencyError):
        meta_model.model_from_str(inp)


def test_function_first_order_cyclic(meta_model):
    """test first order cycic dependencies - deepcopy fails"""
    inp = 'cube(x) = x*x*x; a = cube(2+b); b = a - 1 \n'
    with pytest.raises(CyclicDependencyError):
        meta_model.model_from_str(inp)


def test_if_cyclic_expr(meta_model):
    """test if function cycic dependencies in expr"""
    inp = 'b = if(c, 3, 4); c = 3 + b > 1 \n'
    with pytest.raises(CyclicDependencyError):
        meta_model.model_from_str(inp)


def test_if_cyclic_in_branch(meta_model):
    """test if function cycic dependencies in branch"""
    inp = 'b = if(false, 3, c); c = 3 + b \n'
    with pytest.raises(CyclicDependencyError):
        meta_model.model_from_str(inp)


def test_cyclic_chem_term(meta_model):
    """test cycle ChemSpecies->ChemReaction->ChemTerm->ChemSpecies"""
    inp = ('orr = Reaction 2 H2 + O2 = 2 H2O: ((free_energy: -4.916) [eV]);'
           'O2 = Species O2 ((free_energy: orr.free_energy[0]));'
           'H2O = Species H2O; H2 = Species H2\n')
    with pytest.raises(CyclicDependencyError):
        meta_model.model_from_str(inp)
