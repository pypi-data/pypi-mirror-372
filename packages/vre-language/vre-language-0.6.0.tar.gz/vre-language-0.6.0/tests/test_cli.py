"""test the command-line interface (texts)"""
import os
import re
import sys
import uuid
import subprocess as sp
import pytest
from fireworks.fw_config import LAUNCHPAD_LOC
from virtmat.language.cli import run_model, run_session, version
from virtmat.language.interpreter.session import Session
from virtmat.language.utilities.textx import GRAMMAR_LOC, GrammarString


@pytest.fixture(name='model_file')
def model_file_fixture(tmp_path):
    """prepare a model file as a fixture"""
    path = os.path.join(tmp_path, 'model.vm')
    model = "a = 1; print(a)"
    with open(path, 'w', encoding='utf-8') as ifile:
        ifile.write(model)
    return path


@pytest.fixture(name='lpad_file')
def lpad_file_fixture(tmp_path, lpad):
    """launchpad file as fixture"""
    path = os.path.join(tmp_path, 'launchpad.yaml')
    lpad.to_file(path)
    return path


def test_script_direct_call_parse_clargs(capsys):
    """directly call the parse_clargs() function otherwise not covered"""
    msg = 'the following arguments are required: -f/--model-file'
    with pytest.raises(SystemExit, match='2'):
        run_model.parse_clargs()
    assert msg in capsys.readouterr().err


def test_session_direct_call_parse_clargs():
    """directly call the parse_clargs() function otherwise not covered"""
    if len(sys.argv) > 1:
        with pytest.raises(SystemExit, match='2'):
            run_session.parse_clargs()
    else:
        run_session.parse_clargs()


def test_texts_version():
    """test texts version flag"""
    command = ['texts', '--version']
    with sp.Popen(command, stdout=sp.PIPE, shell=False) as proc:
        assert proc.stdout.read().decode() == version.VERSION + '\n'


def test_texts_script_instant(model_file):
    """test texts script cli tool in instant evaluation mode"""
    command = ['texts', 'script', '-f', model_file]
    with sp.Popen(command, stdout=sp.PIPE, shell=False) as proc:
        assert proc.stdout.read().decode() == "program output: >>>\n1\n<<<\n"


def test_texts_script_deferred(model_file):
    """test texts script cli tool in deferred evaluation mode"""
    command = ['texts', 'script', '-f', model_file, '-m', 'deferred']
    with sp.Popen(command, stdout=sp.PIPE, shell=False) as proc:
        assert proc.stdout.read().decode() == "program output: >>>\n1\n<<<\n"


def test_texts_script_workflow(model_file, lpad_file):
    """test texts script cli tool in workflow evaluation mode"""
    command = ['texts', 'script', '-f', model_file, '-m', 'workflow',
               '-l', lpad_file, '-r']
    with sp.Popen(command, stdout=sp.PIPE, shell=False) as proc:
        assert "program output: >>>\n1\n<<<\n" in proc.stdout.read().decode()


def test_texts_script_show_model(model_file):
    """test texts script cli tool with the --show-model option"""
    command = ['texts', 'script', '-f', model_file, '--show-model']
    with sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE, shell=False) as proc:
        assert proc.stdout.read().decode() == ''
        assert proc.stderr.read().decode() == ''


def test_texts_script_no_interpreter(model_file):
    """test texts script cli tool with the --no-interpreter option"""
    command = ['texts', 'script', '-f', model_file, '--no-interpreter']
    with sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE, shell=False) as proc:
        assert proc.stdout.read().decode() == ''
        assert proc.stderr.read().decode() == ''


def test_texts_session(lpad_file, _res_config_loc):
    """test texts session cli tool"""
    model = 'a = 1; print(a)\n%exit'
    command = ['texts', 'session', '-l', lpad_file, '-r']
    with sp.Popen(command, stdout=sp.PIPE, stdin=sp.PIPE, shell=False) as proc:
        stdout = proc.communicate(input=model.encode())[0]
        assert 'Output > 1' in stdout.decode()


def test_texts_session_expression(lpad_file, _res_config_loc):
    """test texts session cli tool with expression"""
    model = 'a = 1 \n a + 1 \n %exit'
    command = ['texts', 'session', '-l', lpad_file, '-r']
    with sp.Popen(command, stdout=sp.PIPE, stdin=sp.PIPE, shell=False) as proc:
        stdout = proc.communicate(input=model.encode())[0]
        assert 'Output > 2' in stdout.decode()


def test_texts_session_magics(lpad_file, _res_config_loc):
    """test texts session cli tool with magics"""
    model = ('%uuid \n %sleep \n %new \n %start \n %stop \n %hist \n %vary \n'
             '%tag \n %help \n %exit')
    command = ['texts', 'session', '-l', lpad_file, '-r']
    with sp.Popen(command, stdin=sp.PIPE, stderr=sp.PIPE, shell=False) as proc:
        _, stderr = proc.communicate(input=model.encode())
    msg = ('Warning: Session running in a shell not connected to a terminal\n'
           'Welcome to textS/textM. Type %help for some help.')
    assert stderr.decode().strip() == msg


def test_texts_session_magics_async(lpad_file, _res_config_loc):
    """test texts session cli tool with magics in async evaluation"""
    model = '%sleep \n %sleep 10 \n %new \n %hist \n %exit'
    command = ['texts', 'session', '-l', lpad_file, '-r', '-a']
    with sp.Popen(command, stdin=sp.PIPE, stderr=sp.PIPE, shell=False) as proc:
        _, stderr = proc.communicate(input=model.encode())
    msg = ('Warning: Session running in a shell not connected to a terminal\n'
           'Welcome to textS/textM. Type %help for some help.')
    assert stderr.decode().strip() == msg


def test_texts_session_rerun(lpad_file, _res_config_loc):
    """test texts session rerun magic"""
    model = 'a = 1; print(a)\n%rerun a\n%rerun b\n%exit'
    command = ['texts', 'session', '-l', lpad_file, '-r']
    with sp.Popen(command, stdin=sp.PIPE, stderr=sp.PIPE, shell=False) as proc:
        stderr = proc.communicate(input=model.encode())[1].decode()
    assert 'Variable update error: Variable b not found in the model.' in stderr


def test_texts_session_rerun_invalid_state(lpad_file, _res_config_loc):
    """test texts session rerun magic"""
    model = 'a = 1\n%rerun a\n%exit'
    command = ['texts', 'session', '-l', lpad_file]
    with sp.Popen(command, stdin=sp.PIPE, stderr=sp.PIPE, shell=False) as proc:
        stderr = proc.communicate(input=model.encode())[1].decode()
    assert 'State of variable a not allowed: WAITING' in stderr


def test_texts_session_cancel(lpad_file, _res_config_loc):
    """test texts session cancel magic"""
    model = 'a = 1; print(a)\n%cancel a\n%cancel b\n%exit'
    command = ['texts', 'session', '-l', lpad_file, '-r']
    with sp.Popen(command, stdin=sp.PIPE, stderr=sp.PIPE, shell=False) as proc:
        stderr = proc.communicate(input=model.encode())[1].decode()
    assert 'Variable update error: Variable b not found in the model.' in stderr


def test_texts_session_switch_model(lpad, lpad_file, _res_config_loc):
    """test texts session switch model uuid"""
    model_uuid = Session(lpad, grammar_path=GRAMMAR_LOC, create_new=True).uuid
    for flag in (['-r'], ['-r', '-a']):
        command = ['texts', 'session', '-l', lpad_file] + flag
        model = f'%uuid {model_uuid}\n%uuid\n%uuid {model_uuid}\n%exit'
        with sp.Popen(command, stdin=sp.PIPE, stdout=sp.PIPE, shell=False) as proc:
            stdout = proc.communicate(input=model.encode())[0].decode()
        assert model_uuid in stdout
        fake_uuid = '45f5f9a390b94359974661b55f5585af'
        model = f'%uuid {fake_uuid}\n%exit'
        with sp.Popen(command, stdin=sp.PIPE, stderr=sp.PIPE, shell=False) as proc:
            stderr = proc.communicate(input=model.encode())[1].decode()
        assert f'Model not found: uuid {fake_uuid}' in stderr


def test_texts_session_tag_and_search_model(lpad_file, _res_config_loc):
    """test model tagging and searching in tags section"""
    model = "tag ((doping: 'Fe'), ('active site': 'M5'), (n: (5, 7)))\n%tag"
    command = ['texts', 'session', '-l', lpad_file]
    with sp.Popen(command, stdin=sp.PIPE, stdout=sp.PIPE, shell=False) as proc:
        stdout = proc.communicate(input=model.encode())[0].decode()
    assert "((doping: 'Fe'), ('active site': 'M5'), (n: (5, 7)))" in stdout
    model = "%find ((tags: (('~doping': (('$in': ('Fe', 'Co'))) )) ))"
    with sp.Popen(command, stdin=sp.PIPE, stdout=sp.PIPE, shell=False) as proc:
        stdout, _ = proc.communicate(input=model.encode())
    assert 'Model UUID' in stdout.decode()
    model = "%find {tags: {'~active site': {'$in': ('M1', 'M5')}}}"
    with sp.Popen(command, stdin=sp.PIPE, stdout=sp.PIPE, shell=False) as proc:
        stdout, _ = proc.communicate(input=model.encode())
    assert 'Model UUID' in stdout.decode()


def test_texts_session_tag_and_search_model_errors(lpad_file, _res_config_loc):
    """test model tagging and searching with errors"""
    model = "tag ((doping: 'Fe', 'Co'), ('active site': 'M5', 'M2'))"
    command = ['texts', 'session', '-l', lpad_file]
    with sp.Popen(command, stdin=sp.PIPE, stderr=sp.PIPE, shell=False) as proc:
        stderr = proc.communicate(input=model.encode())[1].decode()
    assert 'Tag err' in stderr
    assert 'tag table must have only one row' in stderr
    model = "%find (('~doping': (('$in': ('Fe', 'Co'))) ))"
    with sp.Popen(command, stdin=sp.PIPE, stderr=sp.PIPE, shell=False) as proc:
        stderr = proc.communicate(input=model.encode())[1].decode()
    assert 'Query error: query must include tags, meta or data keys' in stderr


def test_texts_session_search_model_data(lpad_file, _res_config_loc):
    """test model searching in data section"""
    var_a = 'a_' + uuid.uuid4().hex
    model = f"{var_a} = '{var_a}'; b = {var_a}; print(b)\n"
    model += "%find {data: {'~"
    model += var_a
    model += "': {'$exists': true}}}\n%exit"
    command = ['texts', 'session', '-l', lpad_file, '-r']
    with sp.Popen(command, stdin=sp.PIPE, stdout=sp.PIPE, shell=False) as proc:
        stdout = proc.communicate(input=model.encode())[0].decode()
    assert var_a in stdout
    assert 'COM' in stdout


def test_texts_session_search_model_tags_load_one(lpad_file, _res_config_loc):
    """test searching models in tags section and load one"""
    model = "tag ((doping: 'Fe'), ('active site': 'M5'))"
    command = ['texts', 'session', '-l', lpad_file]
    with sp.Popen(command, stdin=sp.PIPE, shell=False) as proc:
        proc.communicate(input=model.encode())
    model = "%find {tags: {'~doping': {'$in': ('Fe', 'Co')}}} load one"
    with sp.Popen(command, stdin=sp.PIPE, stdout=sp.PIPE, shell=False) as proc:
        stdout = proc.communicate(input=model.encode())[0].decode()
    assert "uuids: '" in stdout


def test_texts_session_search_model_meta(lpad, lpad_file, _res_config_loc):
    """test searching models in tags section and load one"""
    session = Session(lpad, grammar_path=GRAMMAR_LOC, create_new=True,
                      autorun=True)
    session.get_model("tag ((doping: 'Fe'), ('active site': 'M5'))")
    command = ['texts', 'session',  '-r', '-l', lpad_file]
    model = "%find {meta: {'state': 'COMPLETED'}}"
    with sp.Popen(command, stdin=sp.PIPE, stdout=sp.PIPE, shell=False) as proc:
        stdout = proc.communicate(input=model.encode())[0].decode()
    assert 'COM' in stdout
    assert session.uuid in stdout


def test_texts_session_search_model_tags_mongodb_error(lpad_file, _res_config_loc):
    """test searching models in tags section and load one"""
    command = ['texts', 'session', '-l', lpad_file]
    model = "%find {'tags': {'~doping': {'$in': ('Fe', 'Co'), 'blah': 1}}}"
    with sp.Popen(command, stdin=sp.PIPE, stderr=sp.PIPE, shell=False) as proc:
        stderr = proc.communicate(input=model.encode())[1].decode()
    assert 'pymongo.errors.OperationFailure: unknown operator: blah' in stderr


def test_texts_find_containing_series(lpad_file, _res_config_loc):
    """test searching models with query containing series"""
    command = ['texts', 'session', '-l', lpad_file]
    model = "%find ((meta: (state: 'FIZZLED')))"
    with sp.Popen(command, stdin=sp.PIPE, stderr=sp.PIPE, shell=False) as proc:
        stderr = proc.communicate(input=model.encode())[1].decode()
    msg = "Query error: unsupported type for query/tag: <class 'pandas.core.series.Series'>"
    assert msg in stderr


def test_texts_with_resources(lpad_file, _res_config_loc):
    """test texts session with resource specifications"""
    command = ['texts', 'session', '-l', lpad_file]
    model = 'a = 1 on 2 cores for 1.0 [hours]'
    with sp.Popen(command, stdin=sp.PIPE, stderr=sp.PIPE, shell=False) as proc:
        stderr = proc.communicate(input=model.encode())[1].decode().strip()
    msg = ('Warning: Session running in a shell not connected to a terminal\n'
           'Welcome to textS/textM. Type %help for some help.')
    assert stderr == msg


def test_texts_session_logfile(lpad_file, _res_config_loc, tmp_path):
    """test texts session with logging redirected to a file"""
    filename = os.path.join(tmp_path, 'texts.log')
    command = ['texts', 'session', '-l', lpad_file, '--enable-logging', '--logfile',
               filename]
    with sp.Popen(command, stdin=sp.PIPE, stderr=sp.PIPE, shell=False) as proc:
        stderr = proc.communicate(input='%exit'.encode())[1].decode()
    msg = 'Warning: Session running in a shell not connected to a terminal'
    assert msg in stderr


def test_texts_session_help(lpad_file, _res_config_loc):
    """test texts session with the %help magic"""
    command = ['texts', 'session', '-l', lpad_file]
    with sp.Popen(command, stdin=sp.PIPE, stdout=sp.PIPE, shell=False) as proc:
        stdout = proc.communicate(input='%help'.encode())[0].decode()
    assert '%exit, %bye, %close, %quit' in stdout


def test_texts_script_no_warnings(model_file):
    """test texts script cli tool with no warnings"""
    command = ['texts', 'script', '-f', model_file, '-r', '-m', 'deferred', '-w']
    with sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE, shell=False) as proc:
        assert proc.stdout.read().decode().strip() == 'program output: >>>\n1\n<<<'
        assert proc.stderr.read().decode() == ''


def test_texts_script_show_model_deferred_mode(model_file):
    """test texts script cli tool with the --show-model option in deferred mode"""
    command = ['texts', 'script', '-f', model_file, '--show-model', '-m', 'deferred']
    msg = 'Warning: switching to instant mode due to argument show-model'
    with sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE, shell=False) as proc:
        assert proc.stdout.read().decode() == ''
        assert msg in proc.stderr.read().decode()


def test_texts_script_no_interpreter_deferred_mode(model_file):
    """test texts script cli tool with the --no-interpreter option in deferred mode"""
    command = ['texts', 'script', '-f', model_file, '--no-interpreter', '-m', 'deferred']
    msg = 'Warning: switching to instant mode due to argument no-interpreter'
    with sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE, shell=False) as proc:
        assert proc.stdout.read().decode() == ''
        assert msg in proc.stderr.read().decode()


def test_texts_script_incompatible_grammar_instant_mode(model_file, tmp_path):
    """tests texts with incompatible grammar"""
    g_str = GrammarString(GRAMMAR_LOC).string
    regex = re.compile(r'\/\*\s*grammar version\s+(\d+)\s*\*\/', re.MULTILINE)
    g_str_ = re.sub(regex, lambda x: x.group(0).replace(x.group(1), '0'), g_str)
    g_path = os.path.join(tmp_path, 'wrong_grammar.tx')
    with open(g_path, 'w', encoding='utf-8') as ofile:
        ofile.write(g_str_)
    command = ['texts', 'script', '-f', model_file, '-g', g_path, '-m', 'instant']
    msg = 'Compatibility error: Provided grammar has version 0 but the supported'
    with sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE, shell=False) as proc:
        assert proc.stdout.read().decode() == ''
        assert msg in proc.stderr.read().decode()


def test_texts_session_traceback_logging_level_debug(lpad_file, _res_config_loc):
    """test texts session with error traceback at debug logging level"""
    command = ['texts', 'session', '-l', lpad_file, '--enable-logging',
               '--logging-level', 'DEBUG']
    with sp.Popen(command, stdin=sp.PIPE, stderr=sp.PIPE, shell=False) as proc:
        stderr = proc.communicate(input='print(a)'.encode())[1].decode()
    assert 'Traceback (most recent call last)' in stderr
    assert 'textx.exceptions.TextXSemanticError:' in stderr


@pytest.mark.skipif(LAUNCHPAD_LOC is not None,
                    reason='launchpad exists outside of test environment')
def test_texts_missing_launchpad(_res_config_loc, model_file):
    """test texts with missing launchpad file"""
    commands = (['texts', 'script', '-m', 'workflow', '-f', model_file],
                ['texts', 'session'])
    for command in commands:
        with sp.Popen(command, stdin=sp.PIPE, stderr=sp.PIPE, shell=False) as proc:
            stderr = proc.communicate(input=''.encode())[1].decode()
        msg = ('Configuration error: Neither default Launchpad file configured nor '
               'custom Launchpad file is specified.')
        assert msg in stderr
