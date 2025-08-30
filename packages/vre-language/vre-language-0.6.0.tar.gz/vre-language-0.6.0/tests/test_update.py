"""test the variable update feature"""
import pytest
from textx.exceptions import TextXError
from virtmat.language.interpreter.session import Session
from virtmat.language.utilities.errors import UpdateError
from virtmat.language.utilities.textx import GRAMMAR_LOC
from virtmat.language.utilities.fireworks import cancel_vars


def test_update_variable_model_from_scratch(meta_model_wf, model_kwargs_wf):
    """test update of one variable in a model from scratch"""
    inp = 'a = 1; b = a + 1; b := a - 1; print(b)'
    assert meta_model_wf.model_from_str(inp, **model_kwargs_wf).value == '0'


def test_update_variable_descendant_from_scratch(meta_model_wf, model_kwargs_wf):
    """test update of a variable descendant in a model form scratch"""
    inp = 'a = 1; b = a + 1; a := 2; print(b)'
    assert meta_model_wf.model_from_str(inp, **model_kwargs_wf).value == '3'


def test_update_variable_extension_model(lpad):
    """test update of one variable in an extension model"""
    session = Session(lpad, grammar_path=GRAMMAR_LOC, model_str='a = 1; b = a + 1', autorun=True)
    assert session.get_model('print(b)').value == '2'
    session = Session(lpad, uuid=session.uuid, model_str='b := a - 1', autorun=True)
    assert session.get_model('print(b)').value == '0'


def test_update_variable_descendant_extension_model(lpad):
    """test update of a variable descendant in an extension model"""
    session = Session(lpad, grammar_path=GRAMMAR_LOC, model_str='a = 1; b = a + 1', autorun=True)
    assert session.get_model('print(b)').value == '2'
    session = Session(lpad, uuid=session.uuid, model_str='a := 2', autorun=True)
    assert session.get_model('print(b)').value == '3'


def test_update_variable_iterable_property_function_call(lpad):
    """test update of a variable with iterable property and funciton call"""
    inp1 = 'f(x) = x; t = ((s: 1, 2, 3)); d = map((x: x**3), t.s)'
    session = Session(lpad, grammar_path=GRAMMAR_LOC, model_str=inp1, autorun=True)
    assert session.get_model('print(d)').value == '(d: 1, 8, 27)'
    inp2 = 'd := f(t.s)'
    session = Session(lpad, uuid=session.uuid, model_str=inp2, autorun=True)
    assert session.get_model('print(d)').value == '(s: 1, 2, 3)'
    inp3 = 'd := 2 + t.s[2]'
    session = Session(lpad, uuid=session.uuid, model_str=inp3, autorun=True)
    assert session.get_model('print(d)').value == '5'
    inp4 = 'd := map((x: x**3), t.s)'
    session = Session(lpad, uuid=session.uuid, model_str=inp4, autorun=True)
    assert session.get_model('print(d)').value == '(d: 1, 8, 27)'


def test_update_model_multiple_updates(meta_model_wf, model_kwargs_wf):
    """test update with multiple update statements"""
    inp = 'c = 2; c := 3; c := 1'
    msg = r"Multiple updates of variables: \['c'\]"
    with pytest.raises(TextXError, match=msg) as err:
        meta_model_wf.model_from_str(inp, **model_kwargs_wf)
    assert isinstance(err.value.__cause__, UpdateError)


def test_update_variable_invalid_reference(meta_model_wf, model_kwargs_wf):
    """test update with invalid reference"""
    inp = 'a = 1; b = a + 1; c = 1; c := 3 - b'
    msg = r"Invalid or missing references: \['b'\]"
    with pytest.raises(TextXError, match=msg) as err:
        meta_model_wf.model_from_str(inp, **model_kwargs_wf)
    assert isinstance(err.value.__cause__, UpdateError)


def test_update_variable_missing_reference(meta_model_wf, model_kwargs_wf):
    """test update with missing reference"""
    inp = 'a = 1; b = a + 1; b := 2'
    msg = r"Invalid or missing references: \['a'\]"
    with pytest.raises(TextXError, match=msg) as err:
        meta_model_wf.model_from_str(inp, **model_kwargs_wf)
    assert isinstance(err.value.__cause__, UpdateError)


def test_update_variable_non_workflow_mode(meta_model_instant):
    """test variable update in non-workflow mode"""
    inp = 'a = 1; b = a + 1; b := a - 1; print(b)'
    msg = 'Variables can be updated in workflow mode only.'
    with pytest.raises(TextXError, match=msg) as err:
        meta_model_instant.model_from_str(inp)
    assert isinstance(err.value.__cause__, UpdateError)


def test_update_variable_in_vary_table(lpad):
    """test updating a variable that is varied in the model group"""
    session = Session(lpad, uuid=None, grammar_path=GRAMMAR_LOC)
    session.get_model('vary ((a: 1, 2))')
    msg = r'Cannot update \"a\" which is varied in a model group'
    with pytest.raises(TextXError, match=msg) as err:
        session.get_model('a := 3')
    assert isinstance(err.value.__cause__, UpdateError)


def test_update_variable_in_model_group(lpad):
    """test updating a variable in a model group"""
    session = Session(lpad, uuid=None, grammar_path=GRAMMAR_LOC, autorun=True)
    session.process_models('vary ((a: 1, 2)); b = 2*a; print(b)')
    assert session.models[0].value == '2'
    assert session.models[1].value == '4'
    session.process_models('b := 3*a; print(b)')
    assert session.models[0].value == '3'
    assert session.models[1].value == '6'


def test_update_fizzled_variable(lpad):
    """test updating variable in fizzled state"""
    session = Session(lpad, uuid=None, grammar_path=GRAMMAR_LOC, autorun=True)
    assert session.get_model('a = 1 / 0; print(a)').value == ''
    assert session.get_model('a := 1 / 1; print(a)').value == '1.0'


def test_update_defused_variable(lpad):
    """test updating variable in defused state"""
    session = Session(lpad, uuid=None, grammar_path=GRAMMAR_LOC, autorun=True)
    assert session.get_model('a = 1/0; print(a)').value == ''
    cancel_vars(lpad, session.uuid, ['a'])
    session.get_model('a := 2')
    assert session.get_model('print(a)').value == '2'


def test_update_paused_variable(lpad):
    """test updating variable in paused state"""
    session = Session(lpad, uuid=None, grammar_path=GRAMMAR_LOC, model_str='a = 1')
    cancel_vars(lpad, session.uuid, ['a'])
    session.start_runner()
    session.get_model('a := 2')
    assert session.get_model('print(a)').value == '2'


def test_update_archived_variable(lpad):
    """test updating variable in archived state"""
    session = Session(lpad, uuid=None, grammar_path=GRAMMAR_LOC, model_str='a = 1')
    lpad.archive_wf(lpad.get_wf_ids({'metadata.uuid': session.uuid})[0])
    msg = 'Cannot update variable in ARCHIVED state.'
    with pytest.raises(UpdateError, match=msg):
        session.get_model('a := 2')
