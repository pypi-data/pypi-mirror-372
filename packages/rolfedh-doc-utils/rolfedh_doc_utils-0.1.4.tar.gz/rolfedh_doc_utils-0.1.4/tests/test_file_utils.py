import os
import tempfile
import zipfile
from datetime import datetime
import pytest
from doc_utils.file_utils import collect_files, write_manifest_and_archive


class TestCollectFiles:
    """Test cases for the collect_files function."""
    
    def test_collect_files_basic(self):
        """Test basic file collection with extensions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            test_files = [
                'file1.adoc',
                'file2.adoc',
                'file3.txt',
                'subdir/file4.adoc',
                'subdir/file5.md'
            ]
            
            for file_path in test_files:
                full_path = os.path.join(tmpdir, file_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, 'w') as f:
                    f.write('test content')
            
            # Collect .adoc files
            found = collect_files([tmpdir], {'.adoc'})
            found_names = [os.path.basename(f) for f in found]
            
            assert len(found) == 3
            assert 'file1.adoc' in found_names
            assert 'file2.adoc' in found_names
            assert 'file4.adoc' in found_names
            assert 'file3.txt' not in found_names
    
    def test_collect_files_multiple_extensions(self):
        """Test collecting files with multiple extensions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_files = ['a.png', 'b.jpg', 'c.gif', 'd.txt']
            
            for file_name in test_files:
                with open(os.path.join(tmpdir, file_name), 'w') as f:
                    f.write('test')
            
            found = collect_files([tmpdir], {'.png', '.jpg', '.gif'})
            found_names = [os.path.basename(f) for f in found]
            
            assert len(found) == 3
            assert 'd.txt' not in found_names
    
    def test_exclude_directories(self):
        """Test directory exclusion."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create directory structure
            os.makedirs(os.path.join(tmpdir, 'include', 'subdir'))
            os.makedirs(os.path.join(tmpdir, 'exclude', 'subdir'))
            
            # Create files
            files = [
                'include/file1.adoc',
                'include/subdir/file2.adoc',
                'exclude/file3.adoc',
                'exclude/subdir/file4.adoc'
            ]
            
            for file_path in files:
                with open(os.path.join(tmpdir, file_path), 'w') as f:
                    f.write('test')
            
            # Exclude the 'exclude' directory
            exclude_dir = os.path.join(tmpdir, 'exclude')
            found = collect_files([tmpdir], {'.adoc'}, exclude_dirs=[exclude_dir])
            found_names = [os.path.relpath(f, tmpdir) for f in found]
            
            assert len(found) == 2
            assert 'include/file1.adoc' in found_names
            assert 'include/subdir/file2.adoc' in found_names
            assert 'exclude/file3.adoc' not in found_names
            assert 'exclude/subdir/file4.adoc' not in found_names
    
    def test_exclude_files(self):
        """Test file exclusion."""
        with tempfile.TemporaryDirectory() as tmpdir:
            files = ['keep1.adoc', 'keep2.adoc', 'exclude1.adoc', 'exclude2.adoc']
            
            for file_name in files:
                with open(os.path.join(tmpdir, file_name), 'w') as f:
                    f.write('test')
            
            exclude_files = [
                os.path.join(tmpdir, 'exclude1.adoc'),
                os.path.join(tmpdir, 'exclude2.adoc')
            ]
            
            found = collect_files([tmpdir], {'.adoc'}, exclude_files=exclude_files)
            found_names = [os.path.basename(f) for f in found]
            
            assert len(found) == 2
            assert 'keep1.adoc' in found_names
            assert 'keep2.adoc' in found_names
            assert 'exclude1.adoc' not in found_names
    
    def test_symlink_handling(self):
        """Test that symlinks are properly excluded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a real file
            real_file = os.path.join(tmpdir, 'real.adoc')
            with open(real_file, 'w') as f:
                f.write('real content')
            
            # Create a real directory with a file
            real_dir = os.path.join(tmpdir, 'realdir')
            os.makedirs(real_dir)
            with open(os.path.join(real_dir, 'file.adoc'), 'w') as f:
                f.write('test')
            
            # Create symlinks
            link_file = os.path.join(tmpdir, 'link.adoc')
            link_dir = os.path.join(tmpdir, 'linkdir')
            
            os.symlink(real_file, link_file)
            os.symlink(real_dir, link_dir)
            
            found = collect_files([tmpdir], {'.adoc'})
            found_names = [os.path.basename(f) for f in found]
            
            # Should find real files but not symlinks
            assert 'real.adoc' in found_names
            assert 'link.adoc' not in found_names
            # Should not traverse symlinked directories
            assert len([f for f in found if 'linkdir' in f]) == 0
    
    def test_parent_directory_exclusion(self):
        """Test that excluding a parent directory excludes all subdirectories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create nested directory structure
            dirs = [
                'parent',
                'parent/child1',
                'parent/child1/grandchild',
                'parent/child2',
                'other'
            ]
            
            for d in dirs:
                os.makedirs(os.path.join(tmpdir, d))
                with open(os.path.join(tmpdir, d, 'file.adoc'), 'w') as f:
                    f.write('test')
            
            # Exclude parent directory
            exclude_dir = os.path.join(tmpdir, 'parent')
            found = collect_files([tmpdir], {'.adoc'}, exclude_dirs=[exclude_dir])
            
            # Should only find file in 'other' directory
            assert len(found) == 1
            assert 'other' in found[0]
    
    def test_case_insensitive_extensions(self):
        """Test that file extensions are matched case-insensitively."""
        with tempfile.TemporaryDirectory() as tmpdir:
            files = ['lower.png', 'UPPER.PNG', 'Mixed.PnG']
            
            for file_name in files:
                with open(os.path.join(tmpdir, file_name), 'w') as f:
                    f.write('test')
            
            found = collect_files([tmpdir], {'.png'})
            assert len(found) == 3
    
    def test_multiple_scan_dirs(self):
        """Test scanning multiple directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create two separate directories
            dir1 = os.path.join(tmpdir, 'dir1')
            dir2 = os.path.join(tmpdir, 'dir2')
            os.makedirs(dir1)
            os.makedirs(dir2)
            
            # Add files to each
            with open(os.path.join(dir1, 'file1.adoc'), 'w') as f:
                f.write('test')
            with open(os.path.join(dir2, 'file2.adoc'), 'w') as f:
                f.write('test')
            
            found = collect_files([dir1, dir2], {'.adoc'})
            found_names = [os.path.basename(f) for f in found]
            
            assert len(found) == 2
            assert 'file1.adoc' in found_names
            assert 'file2.adoc' in found_names
    
    def test_no_duplicates(self):
        """Test that duplicate files are removed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a file
            file_path = os.path.join(tmpdir, 'file.adoc')
            with open(file_path, 'w') as f:
                f.write('test')
            
            # Scan the same directory twice
            found = collect_files([tmpdir, tmpdir], {'.adoc'})
            
            # Should only have one result
            assert len(found) == 1


class TestWriteManifestAndArchive:
    """Test cases for the write_manifest_and_archive function."""
    
    def test_write_manifest_only(self):
        """Test writing manifest without archiving."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            test_files = []
            for i in range(3):
                file_path = os.path.join(tmpdir, f'file{i}.txt')
                with open(file_path, 'w') as f:
                    f.write(f'content {i}')
                test_files.append(file_path)
            
            archive_dir = os.path.join(tmpdir, 'archive')
            
            # Write manifest only
            manifest_path, archive_path = write_manifest_and_archive(
                test_files, archive_dir, 'manifest', 'archive', archive=False
            )
            
            assert manifest_path is not None
            assert archive_path is None
            assert os.path.exists(manifest_path)
            
            # Check manifest content
            with open(manifest_path, 'r') as f:
                lines = f.read().strip().split('\n')
            assert len(lines) == 3
            
            # Files should still exist
            for file_path in test_files:
                assert os.path.exists(file_path)
    
    def test_write_manifest_and_archive(self):
        """Test writing manifest and creating archive."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            test_files = []
            for i in range(3):
                file_path = os.path.join(tmpdir, f'file{i}.txt')
                with open(file_path, 'w') as f:
                    f.write(f'content {i}')
                test_files.append(file_path)
            
            archive_dir = os.path.join(tmpdir, 'archive')
            
            # Write manifest and archive
            manifest_path, archive_path = write_manifest_and_archive(
                test_files, archive_dir, 'manifest', 'archive', archive=True
            )
            
            assert manifest_path is not None
            assert archive_path is not None
            assert os.path.exists(manifest_path)
            assert os.path.exists(archive_path)
            
            # Files should be deleted after archiving
            for file_path in test_files:
                assert not os.path.exists(file_path)
            
            # Check archive content
            with zipfile.ZipFile(archive_path, 'r') as zf:
                archived_files = zf.namelist()
            assert len(archived_files) == 3
    
    def test_empty_file_list(self):
        """Test handling empty file list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            archive_dir = os.path.join(tmpdir, 'archive')
            
            manifest_path, archive_path = write_manifest_and_archive(
                [], archive_dir, 'manifest', 'archive', archive=False
            )
            
            assert manifest_path is None
            assert archive_path is None
    
    def test_manifest_filename_format(self):
        """Test that manifest filename follows expected format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, 'test.txt')
            with open(test_file, 'w') as f:
                f.write('test')
            
            archive_dir = os.path.join(tmpdir, 'archive')
            
            manifest_path, _ = write_manifest_and_archive(
                [test_file], archive_dir, 'test-manifest', 'archive', archive=False
            )
            
            manifest_name = os.path.basename(manifest_path)
            assert manifest_name.startswith('test-manifest-')
            assert manifest_name.endswith('.txt')
            # Check date format
            assert len(manifest_name) == len('test-manifest-YYYY-MM-DD_HHMMSS.txt')
    
    def test_archive_preserves_relative_paths(self):
        """Test that archive preserves relative directory structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create nested file structure
            subdir = os.path.join(tmpdir, 'subdir', 'nested')
            os.makedirs(subdir)
            
            file1 = os.path.join(tmpdir, 'file1.txt')
            file2 = os.path.join(subdir, 'file2.txt')
            
            with open(file1, 'w') as f:
                f.write('content1')
            with open(file2, 'w') as f:
                f.write('content2')
            
            archive_dir = os.path.join(tmpdir, 'archive')
            
            # Change to tmpdir to test relative paths
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            
            try:
                # Use relative paths
                rel_file1 = os.path.relpath(file1, tmpdir)
                rel_file2 = os.path.relpath(file2, tmpdir)
                
                _, archive_path = write_manifest_and_archive(
                    [rel_file1, rel_file2], archive_dir, 'manifest', 'archive', archive=True
                )
                
                # Check archive structure
                with zipfile.ZipFile(archive_path, 'r') as zf:
                    archived_files = sorted(zf.namelist())
                
                assert len(archived_files) == 2
                assert archived_files[0] == 'file1.txt'
                assert archived_files[1] == os.path.join('subdir', 'nested', 'file2.txt')
            finally:
                os.chdir(original_cwd)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])