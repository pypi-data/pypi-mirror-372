import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tempfile
import pytest
from test_fixture_check_scannability import setup_test_fixture_check_scannability
import subprocess

SCRIPT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'check_scannability.py'))

def run_script(args, cwd):
    result = subprocess.run([sys.executable, SCRIPT] + args, cwd=cwd, capture_output=True, text=True)
    return result

def test_check_scannability_basic():
    with tempfile.TemporaryDirectory() as tmpdir:
        setup_test_fixture_check_scannability(tmpdir)
        result = run_script([], cwd=tmpdir)
        # Should flag the long sentence and long paragraph in test1.adoc
        assert 'Sentence exceeds' in result.stdout or 'Paragraph exceeds' in result.stdout
        # Should not flag test2.adoc
        assert 'test2.adoc' not in result.stderr

@pytest.mark.parametrize('args,should_flag', [
    (['--max-sentence-length', '10'], True),
    (['--max-paragraph-sentences', '3'], True),
])
def test_check_scannability_custom_limits(args, should_flag):
    with tempfile.TemporaryDirectory() as tmpdir:
        setup_test_fixture_check_scannability(tmpdir)
        result = run_script(args, cwd=tmpdir)
        if should_flag:
            assert 'Sentence exceeds' in result.stdout or 'Paragraph exceeds' in result.stdout

def test_check_scannability_short_options():
    with tempfile.TemporaryDirectory() as tmpdir:
        setup_test_fixture_check_scannability(tmpdir)
        # Use short options -s and -p
        result = run_script(['-s', '10', '-p', '2'], cwd=tmpdir)
        assert 'Sentence exceeds' in result.stdout or 'Paragraph exceeds' in result.stdout

def test_check_scannability_defaults():
    with tempfile.TemporaryDirectory() as tmpdir:
        setup_test_fixture_check_scannability(tmpdir)
        # No options: should use 22 and 3 as limits
        result = run_script([], cwd=tmpdir)
        # Should flag the long sentence and long paragraph in test1.adoc
        assert 'Sentence exceeds' in result.stdout or 'Paragraph exceeds' in result.stdout

def test_check_scannability_help():
    result = run_script(['-h'], cwd=os.getcwd())
    assert 'Scannability Checker' in result.stdout or 'usage' in result.stdout
