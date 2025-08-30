"""test compatibility checks"""
import re
import uuid
import logging
import pytest
from virtmat.language.interpreter.session import Session
from virtmat.language.utilities.textx import GRAMMAR_LOC, GrammarString
from virtmat.language.utilities.compatibility import CompatibilityError


def test_detect_duplicate_compat_version(caplog, meta_model_wf, model_kwargs_wf):
    """test duplicate detection with compatible grammar version"""
    var1 = 'v' + uuid.uuid4().hex
    var2 = 'v' + uuid.uuid4().hex
    prog = f'{var1} = 2 [m]; f(x) = x**2; {var2} = f({var1}); print({var2})'
    model_kwargs_wf['grammar_str'] = GrammarString(GRAMMAR_LOC).string
    model_kwargs_wf['source_code'] = prog
    model_kwargs_wf['detect_duplicates'] = True
    meta_model_wf.model_from_str(prog, **model_kwargs_wf)
    with caplog.at_level(logging.INFO):
        meta_model_wf.model_from_str(prog, **model_kwargs_wf)
    assert "Duplicate found!" in caplog.text


def test_detect_duplicate_incompat_version(caplog, meta_model_wf, model_kwargs_wf):
    """test duplicate detection with incompatible grammar version"""
    var1 = 'v' + uuid.uuid4().hex
    var2 = 'v' + uuid.uuid4().hex
    prog = f'{var1} = 2 [m]; f(x) = x**2; {var2} = f({var1}); print({var2})'
    g_str = GrammarString(GRAMMAR_LOC).string
    regex = re.compile(r'\/\*\s*grammar version\s+(\d+)\s*\*\/', re.MULTILINE)
    g_str_ = re.sub(regex, lambda x: x.group(0).replace(x.group(1), '0'), g_str)
    model_kwargs_wf['grammar_str'] = g_str_
    model_kwargs_wf['source_code'] = prog
    model_kwargs_wf['detect_duplicates'] = True
    meta_model_wf.model_from_str(prog, **model_kwargs_wf)
    model_kwargs_wf['grammar_str'] = g_str
    with caplog.at_level(logging.INFO):
        meta_model_wf.model_from_str(prog, **model_kwargs_wf)
    assert "Duplicate found!" not in caplog.text


def test_submodel_reuse_incompat_version(lpad, meta_model_wf, model_kwargs_wf):
    """test submodel reuse with incompatible grammar version"""
    prog_1 = 'a = 1'
    g_str = GrammarString(GRAMMAR_LOC).string
    regex = re.compile(r'\/\*\s*grammar version\s+(\d+)\s*\*\/', re.MULTILINE)
    g_str_ = re.sub(regex, lambda x: x.group(0).replace(x.group(1), '0'), g_str)
    model_kwargs_wf['grammar_str'] = g_str_
    model_kwargs_wf['source_code'] = prog_1
    m_uuid = meta_model_wf.model_from_str(prog_1, **model_kwargs_wf).uuid
    msg = 'Provided grammar has version 0 but the supported versions are'
    with pytest.raises(CompatibilityError, match=msg):
        Session(lpad, grammar_path=GRAMMAR_LOC, model_str=f'b = 1; c = a@{m_uuid}-b')
