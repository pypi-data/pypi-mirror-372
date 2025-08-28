import os
import sys
import tempfile
import subprocess
import pytest
from unittest.mock import patch, MagicMock
import zipfile

# Import the main functions from each CLI script
from find_unused_attributes import main as find_unused_attributes_main
from check_scannability import main as check_scannability_main
from archive_unused_files import main as archive_unused_files_main
from archive_unused_images import main as archive_unused_images_main


class TestFindUnusedAttributesCLI:
    """Test the find-unused-attributes CLI entry point."""
    
    def test_help_message(self):
        """Test that --help works."""
        with patch('sys.argv', ['find-unused-attributes', '--help']):
            with pytest.raises(SystemExit) as exc_info:
                find_unused_attributes_main()
            assert exc_info.value.code == 0
    
    def test_missing_required_argument(self):
        """Test error when attributes file is not provided."""
        with patch('sys.argv', ['find-unused-attributes']):
            with pytest.raises(SystemExit) as exc_info:
                find_unused_attributes_main()
            assert exc_info.value.code == 2
    
    def test_basic_functionality(self, capsys):
        """Test basic functionality of finding unused attributes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create attributes file
            attr_file = os.path.join(tmpdir, 'attributes.adoc')
            with open(attr_file, 'w') as f:
                f.write(':used-attr: value1\n:unused-attr: value2\n')
            
            # Create adoc file that uses one attribute
            doc_file = os.path.join(tmpdir, 'doc.adoc')
            with open(doc_file, 'w') as f:
                f.write('This document uses {used-attr}.')
            
            # Change to tmpdir for the test
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            
            try:
                with patch('sys.argv', ['find-unused-attributes', 'attributes.adoc']):
                    find_unused_attributes_main()
                
                captured = capsys.readouterr()
                # Check that unused attributes are reported
                assert ':unused-attr:  NOT USED' in captured.out
                # Check that used attributes are not in the output
                assert ':used-attr:' not in captured.out
            finally:
                os.chdir(original_cwd)
    
    def test_output_flag(self):
        """Test the -o/--output flag."""
        with tempfile.TemporaryDirectory() as tmpdir:
            attr_file = os.path.join(tmpdir, 'attributes.adoc')
            with open(attr_file, 'w') as f:
                f.write(':unused: value\n')
            
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            
            try:
                with patch('sys.argv', ['find-unused-attributes', 'attributes.adoc', '-o']):
                    with patch('os.path.expanduser') as mock_expanduser:
                        mock_expanduser.return_value = tmpdir
                        find_unused_attributes_main()
                
                # Check that output file was created
                output_files = [f for f in os.listdir(tmpdir) if f.startswith('unused_attributes_')]
                assert len(output_files) == 1
            finally:
                os.chdir(original_cwd)


class TestCheckScannabilityCLI:
    """Test the check-scannability CLI entry point."""
    
    def test_help_message(self):
        """Test that --help works."""
        with patch('sys.argv', ['check-scannability', '--help']):
            with pytest.raises(SystemExit) as exc_info:
                check_scannability_main()
            assert exc_info.value.code == 0
    
    def test_basic_functionality(self, capsys):
        """Test basic scannability checking."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create adoc file with long sentence
            doc_file = os.path.join(tmpdir, 'doc.adoc')
            long_sentence = ' '.join(['word'] * 30)  # 30 words, exceeds default limit
            with open(doc_file, 'w') as f:
                f.write(f'{long_sentence}.')
            
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            
            try:
                with patch('sys.argv', ['check-scannability']):
                    check_scannability_main()
                
                captured = capsys.readouterr()
                assert 'words' in captured.out
                assert 'doc.adoc' in captured.out
            finally:
                os.chdir(original_cwd)
    
    def test_custom_limits(self, capsys):
        """Test custom sentence and paragraph limits."""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc_file = os.path.join(tmpdir, 'doc.adoc')
            # Create 15-word sentence (under custom 20-word limit)
            sentence = ' '.join(['word'] * 15)
            with open(doc_file, 'w') as f:
                f.write(f'{sentence}.')
            
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            
            try:
                with patch('sys.argv', ['check-scannability', '-s', '20']):
                    check_scannability_main()
                
                captured = capsys.readouterr()
                # When there are no issues, the script produces no output
                # So we check that there's no scannability issue reported
                assert 'exceeds' not in captured.out
                assert 'words' not in captured.out
            finally:
                os.chdir(original_cwd)


class TestArchiveUnusedFilesCLI:
    """Test the archive-unused-files CLI entry point."""
    
    def test_help_message(self):
        """Test that --help works."""
        with patch('sys.argv', ['archive-unused-files', '--help']):
            with pytest.raises(SystemExit) as exc_info:
                archive_unused_files_main()
            assert exc_info.value.code == 0
    
    def test_basic_functionality(self, capsys):
        """Test finding unused files without archiving."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create directory structure
            modules_dir = os.path.join(tmpdir, 'modules')
            os.makedirs(modules_dir)
            
            # Create an unused file
            unused_file = os.path.join(modules_dir, 'unused.adoc')
            with open(unused_file, 'w') as f:
                f.write('Unused content')
            
            # Create a used file and referencing file
            used_file = os.path.join(modules_dir, 'used.adoc')
            with open(used_file, 'w') as f:
                f.write('Used content')
            
            ref_file = os.path.join(modules_dir, 'reference.adoc')
            with open(ref_file, 'w') as f:
                f.write('include::used.adoc[]')
            
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            
            try:
                with patch('sys.argv', ['archive-unused-files']):
                    archive_unused_files_main()
                
                captured = capsys.readouterr()
                # Check that unused files are found
                assert 'modules/unused.adoc' in captured.out
                # Check that used files are not in the output
                output_lines = captured.out.strip().split('\n')
                assert not any('modules/used.adoc' in line for line in output_lines)
            finally:
                os.chdir(original_cwd)
    
    def test_exclude_directory(self, capsys):
        """Test excluding directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create directory structure
            modules_dir = os.path.join(tmpdir, 'modules')
            exclude_dir = os.path.join(modules_dir, 'exclude')
            os.makedirs(exclude_dir)
            
            # Create files
            included_file = os.path.join(modules_dir, 'included.adoc')
            excluded_file = os.path.join(exclude_dir, 'excluded.adoc')
            
            with open(included_file, 'w') as f:
                f.write('content')
            with open(excluded_file, 'w') as f:
                f.write('content')
            
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            
            try:
                with patch('sys.argv', ['archive-unused-files', '--exclude-dir', './modules/exclude']):
                    archive_unused_files_main()
                
                captured = capsys.readouterr()
                assert 'included.adoc' in captured.out
                assert 'excluded.adoc' not in captured.out
            finally:
                os.chdir(original_cwd)
    
    def test_archive_flag(self):
        """Test archiving functionality."""
        with tempfile.TemporaryDirectory() as tmpdir:
            modules_dir = os.path.join(tmpdir, 'modules')
            os.makedirs(modules_dir)
            
            unused_file = os.path.join(modules_dir, 'unused.adoc')
            with open(unused_file, 'w') as f:
                f.write('Unused content')
            
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            
            try:
                with patch('sys.argv', ['archive-unused-files', '--archive']):
                    archive_unused_files_main()
                
                # Check that file was archived and deleted
                assert not os.path.exists(unused_file)
                
                # Check archive exists
                archive_dir = os.path.join(tmpdir, 'archive')
                assert os.path.exists(archive_dir)
                
                # Find the zip file
                zip_files = [f for f in os.listdir(archive_dir) if f.endswith('.zip')]
                assert len(zip_files) == 1
                
                # Verify zip contents
                with zipfile.ZipFile(os.path.join(archive_dir, zip_files[0]), 'r') as zf:
                    assert any('unused.adoc' in name for name in zf.namelist())
            finally:
                os.chdir(original_cwd)


class TestArchiveUnusedImagesCLI:
    """Test the archive-unused-images CLI entry point."""
    
    def test_help_message(self):
        """Test that --help works."""
        with patch('sys.argv', ['archive-unused-images', '--help']):
            with pytest.raises(SystemExit) as exc_info:
                archive_unused_images_main()
            assert exc_info.value.code == 0
    
    def test_basic_functionality(self, capsys):
        """Test finding unused images."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create an unused image
            unused_img = os.path.join(tmpdir, 'orphan.png')
            with open(unused_img, 'w') as f:
                f.write('fake image data')
            
            # Create a used image and referencing file
            used_img = os.path.join(tmpdir, 'referenced.png')
            with open(used_img, 'w') as f:
                f.write('fake image data')
            
            doc_file = os.path.join(tmpdir, 'doc.adoc')
            with open(doc_file, 'w') as f:
                f.write('image::referenced.png[]')
            
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            
            try:
                with patch('sys.argv', ['archive-unused-images']):
                    archive_unused_images_main()
                
                captured = capsys.readouterr()
                assert 'orphan.png' in captured.out
                assert 'referenced.png' not in captured.out
            finally:
                os.chdir(original_cwd)
    
    def test_multiple_image_formats(self, capsys):
        """Test handling multiple image formats."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create various image files
            image_files = ['test.png', 'test.jpg', 'test.jpeg', 'test.gif', 'test.svg']
            for img in image_files:
                with open(os.path.join(tmpdir, img), 'w') as f:
                    f.write('fake image')
            
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            
            try:
                with patch('sys.argv', ['archive-unused-images']):
                    archive_unused_images_main()
                
                captured = capsys.readouterr()
                # All images should be found as unused
                for img in image_files:
                    assert img in captured.out
            finally:
                os.chdir(original_cwd)


class TestCLIIntegration:
    """Integration tests for CLI commands."""
    
    def test_command_line_execution(self):
        """Test that commands can be executed from command line."""
        # This test requires the package to be installed
        # We'll test with --help which should always work
        
        commands = [
            'find-unused-attributes',
            'check-scannability',
            'archive-unused-files',
            'archive-unused-images'
        ]
        
        for cmd in commands:
            result = subprocess.run(
                [sys.executable, '-m', cmd.replace('-', '_'), '--help'],
                capture_output=True,
                text=True
            )
            assert result.returncode == 0, f"Command {cmd} failed"
            # Check that help output contains expected content
            output = result.stdout.lower()
            assert ('usage:' in output or 'help' in output or 
                   'checker' in output or 'archive' in output or 
                   'find' in output), f"Unexpected help output for {cmd}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])