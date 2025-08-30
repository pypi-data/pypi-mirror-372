"""unittests for code that is called only interactively or hard to reach"""
import os
import sys
import uuid
import types
import pytest
from fireworks import LaunchPad
from jsonschema.exceptions import ValidationError
from virtmat.language.interpreter.session import Session
from virtmat.language.utilities.textx import GrammarString, TextXCompleter
from virtmat.language.utilities.textx import display_exception
from virtmat.language.utilities.ase_handlers import get_ase_property
from virtmat.language.utilities.firetasks import FunctionTask
from virtmat.language.utilities.fireworks import get_nodes_providing, get_var_names
from virtmat.language.utilities.fireworks import object_from_file
from virtmat.language.utilities.errors import PropertyError, ObjectFromFileError
from virtmat.language.utilities.errors import CompatibilityError, error_handler
from virtmat.language.utilities.ioops import DATASTORE_CONFIG, get_uuid_filename
from virtmat.language.utilities.jupyter import in_jupyter_notebook
from virtmat.language.utilities.serializable import FWDataObject, get_serializable


@pytest.fixture(name='tab_completer')
def completer_func():
    """factory for completer objects"""
    options = ['%exit', '%bye']
    ids = ['bar', 'foo']
    return TextXCompleter(GrammarString().string, options, ids)


def test_completer(tab_completer):
    """test tab-completion"""
    assert '%exit' in tab_completer.complete('', 0)
    assert 'print' in tab_completer.complete('print', 0)
    assert '(' in tab_completer.complete('print', 0)
    assert 'print' in tab_completer.complete('print(', 0)
    assert 'print(bar' in tab_completer.matches
    tab_completer.complete('print(not ', 0)
    assert 'print(not true' in tab_completer.matches
    tab_completer.complete('a = ', 0)
    assert 'a = foo' in tab_completer.matches
    tab_completer.complete('x %%', 0)
    tab_completer.complete('%blah ', 0)
    assert tab_completer.complete('print(1)', 0) == 'print(1)'
    assert tab_completer.complete('print(a)', 0) == 'print(a)'


def test_display_exception(capsys):
    """test the display_exception() decorator function"""
    @display_exception
    def func_with_exception():
        raise RuntimeError()
    with pytest.raises(RuntimeError):
        func_with_exception()
    assert 'RuntimeError' in capsys.readouterr().err


def test_is_complete(tab_completer):
    """test is_complete() function"""
    assert tab_completer.is_complete('a = 3 +') is False
    assert tab_completer.is_complete('a = b +\n    4') is True
    assert tab_completer.is_complete('a = 3 +\n    4 +') is False
    assert tab_completer.is_complete('foo bar') is True
    assert tab_completer.is_complete('foo = bar') is True


def test_get_ase_property():
    """test get_ase_property function with exception"""
    msg = 'no property "magmoms" found for method "emt"'
    with pytest.raises(PropertyError, match=msg):
        get_ase_property('emt', 'magmoms', [])


def test_function_task_with_compatibility_exception():
    """test the FunctionTask class with a python version compatibility exception"""
    if (sys.version_info.major, sys.version_info.minor) == (3, 12):
        pytest.skip('test is written for python versions different from 3.12')
    func_str = ('gASVywAAAAAAAACMCmRpbGwuX2RpbGyUjBBfY3JlYXRlX2Z1bmN0aW9ulJOU'
                'KGgAjAxfY3JlYXRlX2NvZGWUk5QoQwCUSwBLAEsASwBLAEsDQwSXAHkAlE6F'
                'lCkpjB88aXB5dGhvbi1pbnB1dC0xMC1lNjY4NTUwMTEwZDM+lIwIPGxhbWJk'
                'YT6UaAlLAUMCgQCUaAUpKXSUUpRjX19idWlsdGluX18KX19tYWluX18KaAlO'
                'TnSUUpR9lH2UjA9fX2Fubm90YXRpb25zX1+UfZRzhpRiLg==')
    task = FunctionTask(func=func_str, inputs=[], outputs=[])
    vers = '3.12.3 (main, May 29 2024, 16:57:49) [GCC 13.3.0]'
    msg = 'This statement has been compiled with incompatible python version'
    with pytest.raises(CompatibilityError, match=msg) as err:
        task.run_task(fw_spec={'_python_version': vers})
    cause = err.value.__cause__
    assert isinstance(cause, SystemError) and 'unknown opcode' in str(cause)


def test_get_var_names(lpad):
    """test get_var_names utility function"""
    session = Session(lpad, grammar_str=GrammarString().string, model_str='a = 1')
    fw_ids = get_nodes_providing(lpad, session.uuid, 'a')
    var_names = get_var_names(lpad, fw_ids)
    assert len(var_names) == 1
    assert var_names[0] == 'a'


def test_read_from_file_exception(capsys):
    """test object_from_file() with an exception with and without handler"""
    filename = uuid.uuid4().hex
    error_handler(object_from_file)(LaunchPad, filename)
    assert f'No such file or directory: \'{filename}\'' in capsys.readouterr().err
    filename = uuid.uuid4().hex
    with pytest.raises(ObjectFromFileError, match=filename) as err:
        object_from_file(LaunchPad, filename)
    assert isinstance(err.value.__cause__, FileNotFoundError)


def test_get_uuid_filename(monkeypatch):
    """test get_uuid_filename with non-supported datastore type"""
    monkeypatch.setenv('WORKFLOW_EVALUATION_MODE', 'yes')
    DATASTORE_CONFIG['type'] = 'file'
    assert DATASTORE_CONFIG['path'] in get_uuid_filename('json')
    DATASTORE_CONFIG['type'] = None
    assert os.environ['WORKFLOW_EVALUATION_MODE'] == 'yes'
    with pytest.warns(UserWarning, match='Falling back to current working directory'):
        get_uuid_filename('json')


def test_is_jupyter_notebook(monkeypatch):
    """test is_jupyter_notebook() utility function"""
    assert in_jupyter_notebook() is False
    monkeypatch.setenv('JPY_PARENT_PID', '12345')
    assert in_jupyter_notebook() is True
    monkeypatch.delenv('JPY_PARENT_PID', raising=False)
    monkeypatch.setenv('JUPYTER_RUNTIME_DIR', '/tmp/fake_dir')
    assert in_jupyter_notebook() is True
    monkeypatch.delenv('JUPYTER_RUNTIME_DIR', raising=False)
    monkeypatch.setenv('KERNEL_ID', 'fake-kernel-id')
    assert in_jupyter_notebook() is True
    monkeypatch.delenv('KERNEL_ID', raising=False)
    monkeypatch.setenv('JPY_SESSION_NAME', 'some_session')
    assert in_jupyter_notebook() is True
    monkeypatch.delenv('JPY_SESSION_NAME', raising=False)
    monkeypatch.setitem(sys.modules, 'ipykernel', types.ModuleType('ipykernel'))
    assert in_jupyter_notebook() is True


def test_schema_validate_active(_schema_validate):
    """test that the validation is activated by validating an invalid instance"""
    dobj = FWDataObject(0, datastore={'type': None})
    msg = '0 is not valid under any of the given schemas'
    with pytest.raises(ValidationError, match=msg):
        dobj.to_dict()


def test_get_serializable_type_error():
    """test get_serializable with an unsupported type"""
    with pytest.raises(TypeError, match=r"cannot serialize \{1\} of type <class 'set'>"):
        get_serializable({1})
