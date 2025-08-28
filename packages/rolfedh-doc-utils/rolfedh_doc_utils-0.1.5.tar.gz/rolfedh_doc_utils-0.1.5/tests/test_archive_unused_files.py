import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
import tempfile
import shutil
import pytest
from test_fixture_archive_unused_files import setup_test_fixture_archive_unused_files
import subprocess

SCRIPT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'archive_unused_files.py'))

def run_script(args, cwd):
    result = subprocess.run([sys.executable, SCRIPT] + args, cwd=cwd, capture_output=True, text=True)
    return result

def test_archive_unused_files_basic():
    with tempfile.TemporaryDirectory() as tmpdir:
        setup_test_fixture_archive_unused_files(tmpdir)
        result = run_script([], cwd=tmpdir)
        assert 'unused1.adoc' in result.stdout
        assert 'unused2.adoc' in result.stdout
        assert 'used.adoc' not in result.stdout
        # Manifest file should be created in archive
        archive_dir = os.path.join(tmpdir, 'archive')
        manifest_files = [f for f in os.listdir(archive_dir) if f.startswith('to-archive-') and f.endswith('.txt')]
        assert manifest_files

@pytest.mark.parametrize('exclude_args,should_find', [
    (['--exclude-file', './modules/unused1.adoc'], 'unused2.adoc'),
    (['--exclude-dir', './modules'], None),
])
def test_archive_unused_files_exclusions(exclude_args, should_find):
    with tempfile.TemporaryDirectory() as tmpdir:
        setup_test_fixture_archive_unused_files(tmpdir)
        result = run_script(exclude_args, cwd=tmpdir)
        archive_dir = os.path.join(tmpdir, 'archive')
        manifest_files = [f for f in os.listdir(archive_dir) if f.startswith('to-archive-') and f.endswith('.txt')]
        assert manifest_files
        manifest_path = os.path.join(archive_dir, manifest_files[0])
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest_content = f.read()
        if should_find:
            assert should_find in manifest_content
        else:
            # If all modules are excluded, no unused files from './modules' should be present
            assert 'modules/unused1.adoc' not in manifest_content
            assert 'modules/unused2.adoc' not in manifest_content
