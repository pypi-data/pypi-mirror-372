import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
import tempfile
import shutil
import pytest
from test_fixture_archive_unused_images import setup_test_fixture
import subprocess

SCRIPT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'archive_unused_images.py'))

def run_script(args, cwd):
    result = subprocess.run([sys.executable, SCRIPT] + args, cwd=cwd, capture_output=True, text=True)
    return result

def test_archive_unused_images_basic():
    with tempfile.TemporaryDirectory() as tmpdir:
        setup_test_fixture(tmpdir)
        result = run_script([], cwd=tmpdir)
        # Check that unused images are found
        assert 'images/unused1.png' in result.stdout
        assert 'images/unused2.jpg' in result.stdout
        # Check that used images are not in the output
        # Split by lines to avoid substring matching issues
        output_lines = result.stdout.strip().split('\n')
        assert not any('images/used1.png' in line for line in output_lines)
        assert not any('images/used2.jpg' in line for line in output_lines)
        # Manifest file should be created in archive
        archive_dir = os.path.join(tmpdir, 'archive')
        manifest_files = [f for f in os.listdir(archive_dir) if f.startswith('unused-images-') and f.endswith('.txt')]
        assert manifest_files

@pytest.mark.parametrize('exclude_args,should_find', [
    (['--exclude-file', './images/unused1.png'], 'unused2.jpg'),
    (['--exclude-dir', './images'], None),
])
def test_archive_unused_images_exclusions(exclude_args, should_find):
    with tempfile.TemporaryDirectory() as tmpdir:
        setup_test_fixture(tmpdir)
        result = run_script(exclude_args, cwd=tmpdir)
        if should_find:
            assert should_find in result.stdout
        else:
            # If all images are excluded, no unused images from './images' should be present
            assert 'images/unused1.png' not in result.stdout
            assert 'images/unused2.jpg' not in result.stdout
