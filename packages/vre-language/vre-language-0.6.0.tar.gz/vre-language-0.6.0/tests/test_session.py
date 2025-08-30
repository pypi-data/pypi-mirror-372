"""test the session class"""
import os
import time
import logging
import uuid
import yaml
import pytest
from textx import get_children_of_type
from textx.exceptions import TextXError
from virtmat.middleware.exceptions import ConfigurationException
from virtmat.language.interpreter.session import Session
from virtmat.language.interpreter.workflow_executor import NonCompletedException
from virtmat.language.utilities.errors import error_handler, ModelNotFoundError
from virtmat.language.utilities.errors import VaryError, ReuseError, TagError
from virtmat.language.utilities.errors import ConfigurationError, StaticValueError
from virtmat.language.utilities.warnings import TextSUserWarning
from virtmat.language.utilities.textx import GRAMMAR_LOC
from virtmat.language.utilities.formatters import formatter
from virtmat.language.utilities.fireworks import get_model_history


def test_session_model_from_scratch_from_empty_model_str(lpad):
    """start a new session with a new model and empty model string"""
    session = Session(lpad, uuid=None, grammar_path=GRAMMAR_LOC,
                      model_str='', autorun=True)
    assert session.model is None
    assert session.get_model() is None
    assert session.get_model_str(session.uuid) == ''
    assert session.uuid is None


def test_session_model_from_scratch_from_model_str_comments_blanks(lpad):
    """start a new session with a new model with only comments and blanks"""
    session = Session(lpad, uuid=None, grammar_path=GRAMMAR_LOC,
                      model_str=' ', autorun=True)
    assert session.model is None
    assert session.get_model() is None
    assert session.get_model_str(session.uuid) == ''
    assert session.uuid is None
    assert session.get_model('# comment; """long comment"""') is None
    assert session.get_model_str(session.uuid) == ''
    assert session.uuid is None


def test_session_model_from_scratch_from_empty_model_str_get_model_empty(lpad):
    """start a new session with a new model and empty model string and call
       get_model() with an empty string"""
    session = Session(lpad, uuid=None, grammar_path=GRAMMAR_LOC,
                      model_str='', autorun=True)
    assert session.model is None
    assert session.get_model('') is None
    assert session.get_model_str(session.uuid) == ''
    assert session.uuid is None


def test_session_model_from_scratch_from_none_model_str_get_model_none(lpad):
    """start a new session with a new model and None model string and call
       get_model() with None model string"""
    session = Session(lpad, uuid=None, grammar_path=GRAMMAR_LOC, autorun=True)
    assert session.model is None
    assert session.get_model() is None
    assert session.get_model_str(session.uuid) == ''
    assert session.uuid is None


def test_session_model_from_scratch_from_none_model_str(lpad):
    """start a new session with a new model and None model string and call
       get_model() with None model string"""
    session = Session(lpad, uuid=None, grammar_path=GRAMMAR_LOC, autorun=True)
    assert session.model is None
    assert session.get_model('a = 1; print(a)').value == '1'
    assert session.get_model_str(session.uuid) == 'a = 1'
    assert session.uuid is not None
    assert session.get_model() is session.get_model()  # model not reinstantiated


def test_session_model_from_scratch_from_empty_model_extend(lpad):
    """start a new session with a new model and empty model string; extend the
       model twice in the same session"""
    session = Session(lpad, uuid=None, grammar_path=GRAMMAR_LOC,
                      model_str='', autorun=True)
    assert session.model is None
    assert session.get_model() is None
    assert session.get_model('a = 1').value == ''
    assert session.get_model('print(a)').value == '1'
    assert session.get_model_str(session.uuid) == 'a = 1'
    assert session.uuid is not None


def test_session_model_from_scratch_from_model_str_novar(lpad):
    """a session with a new model without variables; then extend the model in
       the same session with a model without variables"""
    session = Session(lpad, uuid=None, grammar_path=GRAMMAR_LOC,
                      model_str='print(1)', autorun=True)
    assert session.model is not None
    assert session.get_model().value == '1'
    assert session.get_model('print(2)').value == '2'
    assert session.uuid is not None


def test_session_model_from_scratch_from_model_str_no_autorun(lpad):
    """a session with a new model with a variable; then extend the model with a
       print statement with autorun deactivated"""
    session = Session(lpad, uuid=None, grammar_path=GRAMMAR_LOC,
                      model_str='a = 1', autorun=False)
    assert session.model is not None
    assert session.get_model().value == ''
    assert session.get_model('print(a)').value == 'n.c.'
    assert session.uuid is not None


def test_session_model_from_scratch_from_model_str_autorun(lpad):
    """"a session with a new model; extend the model twice with autorun"""
    session = Session(lpad, uuid=None, grammar_path=GRAMMAR_LOC,
                      model_str='a = 1', autorun=True)
    assert session.get_model().value == ''
    assert session.get_model('print(a)').value == '1'
    assert session.get_model('b = a + 2; print(b)').value == '3'
    assert session.uuid is not None


def test_session_model_from_scratch_from_model_str_single_import(lpad):
    """a session with a new model with just an import and then extend with an
       import reference"""
    session = Session(lpad, uuid=None, grammar_path=GRAMMAR_LOC,
                      model_str='use math.pi', autorun=True)
    assert session.get_model('print(pi)').value[0:8] == '3.141592'


def test_session_model_from_scratch_with_non_callable_import_reference(lpad):
    """a session with an empty model extended with a non-callable import and
       then with a reference to the import"""
    session = Session(lpad, grammar_path=GRAMMAR_LOC, autorun=True)
    assert session.get_model('use math.pi').value == ''
    assert session.get_model('a = pi').value == ''
    assert session.get_model('print(a)').value[0:8] == '3.141592'


def test_session_model_from_scratch_with_callable_import_reference(lpad):
    """a session with an empty model extended with a callable import and
       then with a call of the imported function"""
    session = Session(lpad, grammar_path=GRAMMAR_LOC, autorun=True)
    assert session.get_model('use math.exp').value == ''
    assert session.get_model('print(exp(0))').value == '1.0'


def test_session_model_from_scratch_from_model_str_single_function_def(lpad):
    """a session with a new model with just a function definition and then
       extended with a function call"""
    session = Session(lpad, uuid=None, grammar_path=GRAMMAR_LOC,
                      model_str='f(x) = 2*x', autorun=True)
    assert session.get_model('print(f(1))').value == '2'


def test_session_model_from_scratch_with_reference_function_def(lpad):
    """a session with an empty model extended with a function definition and
       then with a function call"""
    session = Session(lpad, grammar_path=GRAMMAR_LOC, autorun=True)
    assert session.get_model('f(x) = 2*x').value == ''
    assert session.get_model('print(f(1))').value == '2'


def test_session_model_from_scratch_from_model_str_import(lpad):
    """a session with a new model with an import and two import references;
       then extend twice with further references"""
    session = Session(lpad, uuid=None, grammar_path=GRAMMAR_LOC,
                      model_str='use math.pi; print(pi); a = pi', autorun=True)
    pi_ref = pytest.approx(3.141592653589793)
    assert float(session.get_model().value) == pi_ref
    assert float(session.get_model('print(a)').value) == pi_ref
    assert float(session.get_model('print(pi)').value) == pi_ref


def test_session_model_from_scratch_from_model_str_function_def(lpad):
    """a session with a new model with a function def and two references; then
       extend twice with two references"""
    session = Session(lpad, uuid=None, grammar_path=GRAMMAR_LOC,
                      model_str='f(x) = 2*x; a = f(1)', autorun=True)
    assert session.get_model('print(f(2))').value == '4'
    assert session.get_model('print(a)').value == '2'


def test_session_model_from_scratch_from_model_str_tuple(lpad):
    """a session with a new model with tuple, then extend with a reference"""
    session = Session(lpad, uuid=None, grammar_path=GRAMMAR_LOC,
                      model_str='c = (1, 2); a = c[0]; b = c[1]', autorun=True)
    assert session.get_model('print(a, b)').value == '1 2'


def test_session_model_with_no_uuid_and_no_grammar(lpad):
    """a session with neither uuid nor grammar provided"""
    msg = 'grammar must be provided if uuid not provided'
    with pytest.raises(ValueError, match=msg):
        Session(lpad)


def test_session_model_with_invalid_uuid(lpad):
    """a session with an invalid uuid, i.e. no model exists with the uuid"""
    uuid_str = 'f28d2b5668e94dd8844b726a54f54aa2'
    with pytest.raises(ModelNotFoundError, match=f'uuid {uuid_str}'):
        Session(lpad, uuid=uuid_str)


def test_session_model_with_uuid_and_grammar(lpad):
    """a session with both uuid and grammar provided"""
    old_session = Session(lpad, grammar_path=GRAMMAR_LOC, model_str='a = 1')
    assert old_session.uuid is not None
    msg = 'provided grammar ignored in favor of grammar from provided uuid'
    with pytest.warns(TextSUserWarning, match=msg):
        Session(lpad, uuid=old_session.uuid, grammar_path=GRAMMAR_LOC)


def test_develop_a_model_in_two_sessions(lpad):
    """open a session with a model from scratch and then extend the same model
       in a second session"""
    m_str1 = 'func(x) = b*x; b = 3; a = func(2)'
    session1 = Session(lpad, grammar_path=GRAMMAR_LOC, model_str=m_str1)
    assert session1.model is not None
    assert session1.model.value == ''
    assert session1.get_model().value == ''
    session2 = Session(lpad, uuid=session1.uuid, autorun=True)
    assert session2.model is not None
    assert session2.model is session2.get_model()
    assert session2.get_model() is session2.get_model()
    assert session2.get_model().value == ''
    m_str2 = 'c = a + b + func(3); print(a, c)'
    assert session2.get_model(m_str2).value == '6 18'


def test_model_with_no_reference_in_extension_model(lpad):
    """extend a model with a model containing no reference"""
    session = Session(lpad, grammar_path=GRAMMAR_LOC, model_str='a = 1')
    session.get_model('b = 2')
    assert session.get_model('print(a, b)').value == 'n.c. n.c.'


def test_extend_with_a_model_with_random_order_of_references(lpad):
    """extend a model with a model with random order of references"""
    session = Session(lpad, grammar_path=GRAMMAR_LOC, model_str='a = 1', autorun=True)
    session.get_model('b = c; c = a')
    assert session.get_model('print(a, b, c)').value == '1 1 1'


def test_extend_model_with_large_extension(lpad):
    """test the new algorithm to append new nodes for large extensions"""
    model_1 = 'c = 1'
    model_2 = 'a = c; q = b; b = a; print(q)'
    session_1 = Session(lpad, grammar_path=GRAMMAR_LOC, model_str=model_1)
    session_2 = Session(lpad, uuid=session_1.uuid, autorun=True, model_str=model_2)
    assert session_2.model.value == '1'


def test_extend_model_with_object_to(lpad, tmp_path):
    """test model extension including an export (object_to) statement"""
    path = os.path.join(tmp_path, 'export.yaml')
    session = Session(lpad, grammar_path=GRAMMAR_LOC, model_str='a = true')
    Session(lpad, uuid=session.uuid, autorun=True, model_str=f"a to file \'{path}\'")
    with open(path, 'r', encoding='utf-8') as ifile:
        data = yaml.safe_load(ifile)
    assert data is True


def test_error_handler_static_errors(lpad, capsys):
    """test the domain specific error handler for static errors"""
    session = Session(lpad, grammar_path=GRAMMAR_LOC, autorun=False)
    error_handler(session.get_model)('a = b()')
    err_msg = 'Unknown object: None:1:5\nUnknown object "b" of class "Function"\n'
    std_err = capsys.readouterr().err
    assert std_err == err_msg
    error_handler(session.get_model)(';')
    err_msg = ("Syntax error: None:1:1 --> *; <--\nExpected '#.*$' or 'use' or "
               "ID or 'print' or 'view' or 'vary' or 'tag' or EOF\n")
    std_err = capsys.readouterr().err
    assert std_err == err_msg


def test_error_handler_runtime_errors(lpad, capsys):
    """test the domain specific error handler for runtime errors"""
    session = Session(lpad, grammar_path=GRAMMAR_LOC, autorun=True)
    model = session.get_model('a = 4*(2*1 - 3/0); print(a)')
    capsys.readouterr()
    error_handler(lambda: model.value)()
    err_msg = 'division by zero'
    assert err_msg in capsys.readouterr().err
    model = session.get_model('b = 1 [m] > 20 [sec]; print(b)')
    capsys.readouterr()
    error_handler(lambda: model.value)()
    err_msg = ("Dimensionality error: None:1:19 --> b = 1 [m] > 20 [sec] <--\n"
               "Cannot convert from 'meter' ([length]) to 'second' ([time])\n")
    assert capsys.readouterr().err == err_msg


def test_error_handler_runtime_ancestor_error(lpad, capsys):
    """test the domain specific error handler for ancestor runtime errors"""
    session = Session(lpad, grammar_path=GRAMMAR_LOC, autorun=True)
    model = session.get_model('a = 1/0; b = a; print(b)')
    capsys.readouterr()
    error_handler(lambda: model.value)()
    std_err = capsys.readouterr().err
    assert 'Ancestor evaluation error: None:' in std_err
    assert '--> b = a <--\n' in std_err
    assert 'Evaluation of b not possible due to failed ancestors: a\n' in std_err


def test_execution_in_unique_launchdir(lpad, _res_config_loc):
    """test execution in unique launchdir"""
    session = Session(lpad, grammar_path=GRAMMAR_LOC, autorun=True,
                      unique_launchdir=True)
    assert session.get_model('a = 1; b = a; print(b)').value == '1'


def test_execution_on_demand(lpad, _res_config_loc):
    """test execution on demand"""
    session = Session(lpad, grammar_path=GRAMMAR_LOC, autorun=True,
                      on_demand=True, sleep_time=1)
    model = session.get_model('a = 1; b = a; c = 2; print(b)')
    var_objs = get_children_of_type('Variable', model)
    assert next(v.value for v in var_objs if v.name == 'a') == 1
    assert next(v.value for v in var_objs if v.name == 'b') == 1
    with pytest.raises(TextXError) as err_info:
        next(v.value for v in var_objs if v.name == 'c')
    assert isinstance(err_info.value.__cause__, NonCompletedException)
    model = session.get_model('print(a, b, c)')
    assert next(v.value for v in var_objs if v.name == 'a') == 1
    assert next(v.value for v in var_objs if v.name == 'b') == 1
    assert next(v.value for v in var_objs if v.name == 'c') == 2


def test_asynchronous_execution(lpad, _res_config_loc):
    """test asynchronous execution using WFEngine"""
    session = Session(lpad, grammar_path=GRAMMAR_LOC, autorun=True,
                      async_run=True, sleep_time=1, unique_launchdir=False)
    session.stop_runner()
    assert session.get_model('a = 1; print(a)').value == 'n.c.'
    session.start_runner()
    time.sleep(2)
    assert session.get_model('print(a)').value == '1'
    session.stop_runner()
    assert session.get_model('b = true').value == ''
    time.sleep(2)
    assert session.get_model('print(b)').value == 'n.c.'
    session.start_runner()
    time.sleep(2)
    assert session.get_model('print(b)').value == 'true'
    session.stop_runner()


def test_asynchronous_execution_on_demand(lpad, _res_config_loc):
    """test asynchronous execution on demand using WFEngine"""
    session = Session(lpad, grammar_path=GRAMMAR_LOC, autorun=True,
                      async_run=True, on_demand=True, sleep_time=1,
                      unique_launchdir=False)
    session.stop_runner()
    assert session.get_model('a = 1; b = a; c = 2; print(b)').value == 'n.c.'
    session.start_runner()
    time.sleep(2)
    session.stop_runner()
    assert session.get_model('print(a, b, c)').value == '1 1 n.c.'
    session.start_runner()
    time.sleep(2)
    assert session.get_model('print(a, b, c)').value == '1 1 2'
    session.stop_runner()


def test_asynchronous_execution_without_resconfig(lpad, _res_config_fake):
    """test asynchronous execution on demand without resconfig"""
    with pytest.raises(ConfigurationException):
        Session(lpad, grammar_path=GRAMMAR_LOC, autorun=False, async_run=True,
                on_demand=True, sleep_time=1)


def test_basic_session_with_resconfig(lpad, _res_config_loc):
    """test a session with resconfig"""
    session = Session(lpad, grammar_path=GRAMMAR_LOC)
    assert session.get_model('a = 1').worker_name == 'test_w'


def test_model_name_list_used_in_interactive_sessions(lpad):
    """test model property name_list used in interactive sessions"""
    session = Session(lpad, grammar_path=GRAMMAR_LOC, model_str='a = 1')
    assert 'a' in session.model.name_list
    mod2 = session.get_model('b = a; use math.pi; f(x) = 2*x')
    assert all(n in mod2.name_list for n in ['a', 'b', 'pi', 'f'])


def test_duplicate_detection_model_twice(lpad, caplog):
    """test duplicate detection for a model instantiated twice"""
    var1 = 'v' + uuid.uuid4().hex
    var2 = 'v' + uuid.uuid4().hex
    prog = f'{var1} = 2 [m]; f(x) = x**2; {var2} = f({var1}); print({var2})'
    session_1 = Session(lpad, uuid=None, grammar_path=GRAMMAR_LOC,
                        model_str=prog, autorun=True, detect_duplicates=True)
    assert session_1.get_model().value == '4 [meter ** 2]'
    with caplog.at_level(logging.INFO):
        session_2 = Session(lpad, uuid=None, grammar_path=GRAMMAR_LOC,
                            model_str=prog, autorun=True, detect_duplicates=True)
    assert "Duplicate found!" in caplog.text
    assert session_2.get_model().value == '4 [meter ** 2]'


def test_vary_from_scratch(lpad):
    """test vary statement in a model from scratch"""
    session = Session(lpad, uuid=None, grammar_path=GRAMMAR_LOC, model_str=None,
                      autorun=True)
    assert session.get_model('vary ((a: 1, 2)); print(a)').value == '1'


def test_vary_from_non_varied_new_vars(lpad):
    """test vary statement in an extension of a non-varied model"""
    session = Session(lpad, uuid=None, grammar_path=GRAMMAR_LOC, autorun=True,
                      model_str='b = 1')
    session.process_models('vary ((a: 1, 2)); print(a)')
    assert session.models[0].value == '1'
    assert session.models[1].value == '2'


def test_vary_from_non_varied_new_vars_two_sessions(lpad):
    """test vary statement in an extension of a non-varied model in a new session"""
    session_1 = Session(lpad, uuid=None, grammar_path=GRAMMAR_LOC, autorun=True,
                        model_str='b = 1')
    session_2 = Session(lpad, uuid=session_1.uuid, grammar_path=GRAMMAR_LOC,
                        autorun=True, model_str='vary ((a: 1, 2)); print(a)')
    assert session_2.models[0].value == '1'
    assert session_2.models[1].value == '2'


def test_vary_from_varied_new_vars(lpad):
    """test vary statement in an extension of a varied model"""
    session = Session(lpad, uuid=None, grammar_path=GRAMMAR_LOC, autorun=True,
                      model_str='vary ((a: 1, 2))')
    session.process_models('vary ((b: true, false)); print(a, b)')
    assert session.models[0].value == '1 true'
    assert session.models[1].value == '1 false'
    assert session.models[2].value == '2 true'
    assert session.models[3].value == '2 false'


def test_vary_from_varied_new_vars_two_sessions(lpad):
    """test vary statement in an extension of a varied model in a new session"""
    session_1 = Session(lpad, uuid=None, grammar_path=GRAMMAR_LOC, autorun=True,
                        model_str='vary ((a: 1, 2))')
    session_2 = Session(lpad, uuid=session_1.uuid, grammar_path=GRAMMAR_LOC, autorun=True,
                        model_str='vary ((b: true, false)); print(a, b)')
    assert session_2.models[0].value == '1 true'
    assert session_2.models[1].value == '1 false'
    assert session_2.models[2].value == '2 true'
    assert session_2.models[3].value == '2 false'


def test_extend_varied_model(lpad):
    """test a non-varied extension of a varied model"""
    session = Session(lpad, uuid=None, grammar_path=GRAMMAR_LOC, autorun=True,
                      model_str='vary ((a: 1, 2))')
    session.process_models('b = true; print(a, b)')
    assert session.models[0].value == '1 true'
    assert session.models[1].value == '2 true'


def test_extend_varied_model_in_new_session(lpad):
    """test a non-varied extension of a varied model in a new session"""
    session_1 = Session(lpad, uuid=None, grammar_path=GRAMMAR_LOC, autorun=True,
                        model_str='vary ((a: 1, 2))')
    session_2 = Session(lpad, uuid=session_1.uuid, grammar_path=GRAMMAR_LOC,
                        autorun=True, model_str='b = true; print(a, b)')
    assert session_2.models[0].value == '1 true'
    assert session_2.models[1].value == '2 true'


def test_extend_varied_model_old_vars(lpad):
    """test a varied extension of a varied model with new values of old vars"""
    session = Session(lpad, uuid=None, grammar_path=GRAMMAR_LOC, autorun=True,
                      model_str='vary ((a: 1, 2)); b = a**2')
    session.process_models('vary((a: 3, 4)); print(b)')
    assert session.models[2].value == '9'
    assert session.models[3].value == '16'


def test_vary_new_and_old_vars(lpad):
    """test a varied extension with both old and new vars"""
    session = Session(lpad, uuid=None, grammar_path=GRAMMAR_LOC, autorun=True,
                      model_str='vary ((a: 1, 2)); b = a**2')
    msg = 'either existing or new variables allowed in vary, not both'
    with pytest.raises(VaryError, match=msg):
        session.process_models('vary((a: 3, 4), (c: true, false)); print(b)')


def test_vary_old_vars_incomplete(lpad):
    """test a varied extension with incomplete tuple of old variables"""
    session = Session(lpad, uuid=None, grammar_path=GRAMMAR_LOC, autorun=True,
                      model_str='vary ((a: 1, 2), (b: 0, 1)); c = a + b')
    msg = "missing variables in vary: {'b'}"
    with pytest.raises(VaryError, match=msg):
        session.process_models('vary((a: 3, 4)); print(c)')


def test_vary_old_vars_complete(lpad):
    """test a varied extension with a complete set of old vary vars"""
    session = Session(lpad, uuid=None, grammar_path=GRAMMAR_LOC, autorun=True,
                      model_str='vary ((a: 1, 2)); b = 1; c = a + b')
    session.process_models('vary((a: 3, 4)); print(c)')
    assert session.models[0].value == '2'
    assert session.models[1].value == '3'
    assert session.models[2].value == '4'
    assert session.models[3].value == '5'


def test_vary_old_vars_extra_vars(lpad):
    """test a varied extension with a set of old vary vars and extra vars"""
    session = Session(lpad, uuid=None, grammar_path=GRAMMAR_LOC, autorun=True,
                      model_str='vary ((a: 1, 2)); b = 1; c = a + b')
    session.process_models('vary((a: 1, 2), (b: 2, 2)); print(c)')
    assert session.models[0].value == '2'
    assert session.models[1].value == '3'
    assert session.models[2].value == '3'
    assert session.models[3].value == '4'
    assert formatter(session.get_vary_df()['a']) == '(a: 1, 2, 1, 2)'
    assert formatter(session.get_vary_df()['b']) == '(b: 1, 1, 2, 2)'


def test_vary_old_vars_extra_vars_only(lpad):
    """test a varied extension with extra vars only"""
    session = Session(lpad, uuid=None, grammar_path=GRAMMAR_LOC, autorun=True,
                      model_str='a = 1')
    session.process_models('vary ((a: 2, 3)); print(a)')
    assert session.models[0].value == '1'
    assert session.models[1].value == '2'
    assert session.models[2].value == '3'
    assert formatter(session.get_vary_df()['a']) == '(a: 1, 2, 3)'


def test_vary_old_vars_extra_vars_non_literals(lpad):
    """test a varied extension with non-vary variables with non-literal params"""
    session = Session(lpad, uuid=None, grammar_path=GRAMMAR_LOC, autorun=True,
                      model_str='a = 1; b = 1; c = a + b')
    msg = 'only literals may be used in vary statements'
    with pytest.raises(VaryError, match=msg):
        session.process_models('vary((c: 0, 1)); print(c)')


def test_vary_new_vars_non_literals(lpad):
    """test invalid use of non-literals in vary statement"""
    msg = 'only literals may be used in vary statements'
    with pytest.raises(VaryError, match=msg):
        Session(lpad, uuid=None, grammar_path=GRAMMAR_LOC,
                model_str='vary ((a: 1 + b, 2 + b)); b = 1')


def test_vary_old_vars_type_mismatch(lpad):
    """test vary statement with mismatching types"""
    prog = 'vary ((a: 1, 2))'
    session = Session(lpad, grammar_path=GRAMMAR_LOC, model_str=prog)
    with pytest.raises(VaryError, match='type mismatch in vary'):
        session.process_models('vary((a: false))')


def test_vary_old_vars_units_mismatch(lpad):
    """test vary statement with mismatching units"""
    prog = 'vary ((a: 1, 2) [m])'
    session = Session(lpad, grammar_path=GRAMMAR_LOC, model_str=prog)
    msg = 'mismatching units for a: centimeter vs. meter'
    with pytest.raises(VaryError, match=msg):
        session.process_models('vary((a: 1)[cm])')


def test_vary_with_pint_type_series(lpad):
    """test vary with series of pint type (floating point quantities)"""
    session = Session(lpad, grammar_path=GRAMMAR_LOC, autorun=True, model_str='a = 1.0')
    session.process_models('vary((a: 2.0, 3.0)); print(a)')
    assert session.models[0].value == '1.0'
    assert session.models[1].value == '2.0'
    assert session.models[2].value == '3.0'
    assert formatter(session.get_vary_df()['a']) == '(a: 1.0, 2.0, 3.0)'


def test_submodel_reuse_simplest(lpad):
    """test submodel reuse - the simplest case"""
    prog_1 = 'a = 1'
    session_1 = Session(lpad, grammar_path=GRAMMAR_LOC, model_str=prog_1)
    prog_2 = f'b = 1; c = a@{session_1.uuid}-b; print(c)'
    session_2 = Session(lpad, grammar_path=GRAMMAR_LOC, model_str=prog_2, autorun=True)
    assert session_2.get_model().value == '0'


def test_submodel_reuse_create_new(lpad):
    """test submodel reuse with create_new"""
    session_1 = Session(lpad, grammar_path=GRAMMAR_LOC, model_str='a = 1')
    session_2 = Session(lpad, grammar_path=GRAMMAR_LOC, create_new=True, autorun=True)
    prog_2 = f'b = 1; c = a@{session_1.uuid}-b; print(c)'
    assert session_2.get_model(prog_2).value == '0'


def test_submodel_reuse_create_new_persistent_model_2(lpad):
    """test submodel reuse with create_new and with pesistent model 2"""
    session_1 = Session(lpad, grammar_path=GRAMMAR_LOC, model_str='a = 1')
    session_2 = Session(lpad, grammar_path=GRAMMAR_LOC, create_new=True, autorun=True)
    session_2.get_model('b = 1')
    assert session_2.get_model(f'c = a@{session_1.uuid}-b; print(c)').value == '0'


def test_submodel_reuse_invalid_uuid(lpad):
    """test submodel reuse with invalid uuid"""
    uuid_str = 'f28d2b5668e94dd8844b726a54f54aa2'
    with pytest.raises(ModelNotFoundError, match=f'uuid {uuid_str}'):
        Session(lpad, grammar_path=GRAMMAR_LOC, model_str='b = a@'+uuid_str)


def test_submodel_reuse_invalid_variable(lpad):
    """test submodel reuse with non-existing variable"""
    session = Session(lpad, grammar_path=GRAMMAR_LOC, model_str='a = 1')
    msg = f'reference c@{session.uuid} could not be resolved'
    with pytest.raises(ReuseError, match=msg):
        Session(lpad, grammar_path=GRAMMAR_LOC, model_str='b = c@'+session.uuid)


def test_submodel_reuse_name_conflicts_source(lpad):
    """test submodel reuse with name conflicts between source models"""
    session_1 = Session(lpad, grammar_path=GRAMMAR_LOC, model_str='a = 1')
    session_2 = Session(lpad, grammar_path=GRAMMAR_LOC, model_str='a = 1')
    msg = 'name conflicts between source models: {\'a\'}'
    prog = f'b = a@{session_1.uuid} + a@{session_2.uuid}'
    with pytest.raises(ReuseError, match=msg):
        Session(lpad, grammar_path=GRAMMAR_LOC, model_str=prog)


def test_submodel_reuse_name_conflicts_source_target(lpad):
    """test submodel reuse with name conflicts between source and target models"""
    session_1 = Session(lpad, grammar_path=GRAMMAR_LOC, model_str='a = 1')
    session_2 = Session(lpad, grammar_path=GRAMMAR_LOC, model_str='a = 1')
    msg = 'name conflicts between source and target models: {\'a\'}'
    with pytest.raises(ReuseError, match=msg):
        session_2.process_models(f'a = 1; b = a@{session_1.uuid}')


def test_session_with_io_nodes(lpad):
    """test session with io in persistent model"""
    prog_inp = 'a = 2; a to file "a.yaml"'
    session_1 = Session(lpad, grammar_path=GRAMMAR_LOC, model_str=prog_inp)
    Session(lpad, grammar_path=GRAMMAR_LOC, uuid=session_1.uuid, create_new=True)


def test_session_tagging_model(lpad):
    """test tagging a model"""
    inp = ("tag ((keywords: ('monolayer', 'bifunctional mechanism')), "
           "(doping: 'Fe'), ('active site': 'M5'))")
    session = Session(lpad, grammar_path=GRAMMAR_LOC, model_str=inp)
    session.get_model()


def test_session_tagging_row_error(lpad):
    """test tagging a model with row error"""
    inp = "tag ((doping: 'Fe', 'Co'), ('active site': 'M5', 'M2'))"
    msg = 'tag table must have only one row'
    with pytest.raises(TextXError, match=msg) as err:
        Session(lpad, grammar_path=GRAMMAR_LOC, model_str=inp)
    assert isinstance(err.value.__cause__, TagError)
    inp = "tag ((doping: 'Fe', 'Co'), ('active site': 'M5'))"
    msg = 'Table columns must have one size but 2 sizes were found'
    with pytest.raises(TextXError, match=msg) as err:
        Session(lpad, grammar_path=GRAMMAR_LOC, model_str=inp)
    assert isinstance(err.value.__cause__, StaticValueError)


def test_session_switch_to_model_without_grammar(lpad, meta_model_wf, model_kwargs_wf):
    """test switching to a model without grammar"""
    model = meta_model_wf.model_from_str('a = 1', **model_kwargs_wf)
    msg = 'invalid / missing grammar in model with uuid'
    with pytest.raises(ConfigurationError, match=msg):
        Session(lpad, uuid=model.uuid, model_str='print(a)')


def test_session_model_history(lpad):
    """test the model history magic in a session"""
    inp = 'a = 1; print(a)'
    session = Session(lpad, grammar_path=GRAMMAR_LOC, model_str=inp, autorun=True)
    session.start_runner()
    assert session.get_model(uuid=session.uuid).value == '1'
    assert 'COMPLETED' in str(get_model_history(lpad, uuid=session.uuid))
    assert 'a = 1' in str(get_model_history(lpad, uuid=session.uuid))
    session.stop_runner()


def test_session_archived_model_completed_launch(lpad):
    """test an archived model with a completed launch in a session"""
    inp = 'a = 1; print(a)'
    session = Session(lpad, grammar_path=GRAMMAR_LOC, model_str=inp, autorun=True)
    session.start_runner()
    assert session.get_model(uuid=session.uuid).value == '1'
    assert 'COMPLETED' in str(get_model_history(lpad, uuid=session.uuid))
    lpad.archive_wf(lpad.get_wf_ids({'metadata.uuid': session.uuid})[0])
    assert 'ARCHIVED' in str(get_model_history(lpad, uuid=session.uuid))
    assert session.get_model('print(a)').value == '1'


def test_session_archived_model_not_completed_launch(lpad):
    """test an archived model with a not completed launch in a session"""
    session = Session(lpad, grammar_path=GRAMMAR_LOC, model_str='a = 1; print(a)')
    assert session.get_model(uuid=session.uuid).value == 'n.c.'
    lpad.archive_wf(lpad.get_wf_ids({'metadata.uuid': session.uuid})[0])
    assert 'ARCHIVED' in str(get_model_history(lpad, uuid=session.uuid))
    assert session.get_model('print(a)').value == 'n.c.'


def test_session_evaluate_lazy_on_demand(lpad):
    """test lazy on-demand evaluation"""
    inp = "f = true; g = 2; print(if(not (false and f), 1, g), (2*g,))"
    session1 = Session(lpad, grammar_path=GRAMMAR_LOC, on_demand=True,
                       autorun=True,  model_str=inp)
    assert session1.get_model().value == '1 (4,)'
    session2 = Session(lpad, uuid=session1.uuid, autorun=False)
    assert session2.get_model('print(f)').value == 'n.c.'


def test_session_evaluate_lazy_on_demand_nc_expr_false(lpad):
    """test lazy on-demand evaluation nc expr and false branch"""
    inp = "f = true; g = 2; h = 3; print(if(not f, 1, g), if(true, 1, h))"
    session1 = Session(lpad, grammar_path=GRAMMAR_LOC, on_demand=True,
                       autorun=True,  model_str=inp)
    assert session1.get_model().value == 'n.c. 1'
    assert session1.get_model('print(if(not f, 1, g))').value == '2'
    session2 = Session(lpad, uuid=session1.uuid, autorun=False)
    assert session2.get_model('print(h)').value == 'n.c.'


def test_session_asynchronous_evaluation_with_mongomock(lpad, _res_config_loc,
                                                        _mongomock_setup):
    """test refusing asynchronous evaluation with mongomock"""
    msg = 'launcher thread cannot be used with Mongomock'
    with pytest.raises(ConfigurationException, match=msg):
        Session(lpad, grammar_path=GRAMMAR_LOC, autorun=True, async_run=True)
