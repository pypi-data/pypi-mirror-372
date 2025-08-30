"""tests for datastore for offloaded data"""
import os
import uuid
from itertools import product
import yaml
import pytest
from virtmat.language.interpreter.session import Session
from virtmat.language.utilities.textx import GRAMMAR_LOC
from virtmat.language.utilities.fireworks import get_nodes_info
from virtmat.language.utilities.ioops import get_datastore_config


@pytest.fixture(name='_datastore_config_file')
def datastore_config_file_fixture(tmp_path, monkeypatch):
    """create a datastore config file with common parameters"""
    config_path = os.path.join(tmp_path, 'datastore_config.yaml')
    config = {'path': str(tmp_path), 'inline-threshold': 1}
    with open(config_path, 'x', encoding='utf-8') as out:
        yaml.safe_dump(config, out)
    monkeypatch.setenv('DATASTORE_CONFIG', config_path)


@pytest.fixture(name='_datastore_config_file_missing')
def datastore_config_file_missing_fixture(monkeypatch):
    """set a datastore config file path that does not exist"""
    config_path = os.path.join(uuid.uuid4().hex, 'datastore_config.yaml')
    monkeypatch.setenv('DATASTORE_CONFIG', config_path)


DATASTORE_PARAMS = list(product((False, True), ('json', 'yaml'), ('file', 'gridfs')))
DATASTORE_LABELS = product(('--------', 'COMPRESS'), ('JSON', 'YAML'), ('FILE', 'GRID'))


@pytest.fixture(name='datastore_config_param', params=list(DATASTORE_PARAMS),
                ids=['-'.join(ls) for ls in DATASTORE_LABELS])
def datastore_config_param_fixture(request):
    """parameterize the various custom parameter combinations"""
    return request.param


@pytest.fixture(name='_datastore_test_config')
def datastore_test_config_fixture(datastore_config_param, _datastore_config_file):
    """fixture to update the datastore configuration file"""
    new_conf = dict(zip(('compress', 'format', 'type'), datastore_config_param))
    return get_datastore_config(**new_conf)


def test_get_datastore_config_missing(_datastore_config_file_missing):
    """test get_datastore_config() with missing custom configuration file"""
    msg = r'The config file \w{32}/datastore_config.yaml does not exist.'
    with pytest.raises(FileNotFoundError, match=msg):
        get_datastore_config()


def test_datastore_simple(_datastore_test_config, meta_model_wf, model_kwargs_wf):
    """test datastore with simple model and check the output"""
    inp = 'a = 1; b = a + 1; print(b)'
    prog = meta_model_wf.model_from_str(inp, **model_kwargs_wf)
    assert prog.value == '2'


def test_datastore_for_model_in_two_sessions(_datastore_test_config, lpad):
    """test datastore for a model created in two sessions"""
    session1 = Session(lpad, grammar_path=GRAMMAR_LOC, autorun=True)
    m_str1 = 'func(x) = b*x; b = 3; a = func(2)'
    assert session1.get_model(m_str1).value == ''
    session2 = Session(lpad, uuid=session1.uuid, autorun=True)
    m_str2 = 'c = a + b + func(3); print(a, c)'
    assert session2.get_model(m_str2).value == '6 18'


def test_datastore_detailed(_datastore_test_config, lpad):
    """detailed test of the datastore"""
    session = Session(lpad, grammar_path=GRAMMAR_LOC, autorun=True)
    prog = session.get_model('a = 1; b = a; c = a + 1; print(b, c)')
    wf_q = {'metadata.uuid': prog.uuid}
    wfn = get_nodes_info(lpad, wf_q, {'spec._source_code.0': 'a = 1'}, {'launches': True})
    launch_q = {'launch_id': wfn[0]['nodes'][0]['launches'][-1]}
    launch = lpad.launches.find_one(launch_q)
    assert 'a' in launch['action']['update_spec']
    data_object = launch['action']['update_spec']['a']
    assert 'datastore' in data_object
    for key, val in data_object['datastore'].items():
        assert val == _datastore_test_config[key]
    assert 'filename' in data_object
    assert 'json' in data_object['filename'] or 'yaml' in data_object['filename']
    wfn = get_nodes_info(lpad, wf_q, {'spec._source_code.0': 'b = a'}, {'spec': True})
    assert wfn[0]['nodes'][0]['spec']['a'] == data_object
    wfn = get_nodes_info(lpad, wf_q, {'spec._source_code.0': 'c = a + 1'}, {'spec': True})
    assert wfn[0]['nodes'][0]['spec']['a'] == data_object
