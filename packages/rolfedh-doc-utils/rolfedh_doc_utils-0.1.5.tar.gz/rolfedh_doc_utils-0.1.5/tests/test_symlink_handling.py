"""Test that topic_map_parser handles symbolic links correctly without freezing."""

import os
import tempfile
import pytest
from doc_utils.topic_map_parser import detect_repo_type


def test_detect_repo_type_with_circular_symlinks(tmp_path):
    """Test that detect_repo_type doesn't freeze with circular symbolic links."""
    
    # Create a directory structure with circular symlinks
    modules_dir = tmp_path / "modules"
    modules_dir.mkdir()
    
    # Create a master.adoc file in modules
    (modules_dir / "master.adoc").write_text("= Test Doc\n")
    
    # Create a circular symlink: modules/modules -> ../modules
    circular_link = modules_dir / "modules"
    try:
        os.symlink("../../modules", str(circular_link))
    except OSError:
        pytest.skip("Cannot create symbolic links on this system")
    
    # This should not freeze - it should skip the symlink
    repo_type = detect_repo_type(str(tmp_path))
    assert repo_type == "master_adoc"


def test_detect_repo_type_with_nested_circular_symlinks(tmp_path):
    """Test detection with nested directories containing circular symlinks."""
    
    # Create nested structure
    (tmp_path / "assemblies").mkdir()
    modules_dir = tmp_path / "modules"
    modules_dir.mkdir()
    
    # Create master.adoc
    (tmp_path / "master.adoc").write_text("= Main Doc\n")
    
    # Create archive directory with circular symlinks (similar to real case)
    archive_dir = tmp_path / ".archive" / "archived-content" / "modules"
    archive_dir.mkdir(parents=True)
    
    try:
        # Create circular symlink in archive
        os.symlink("../../modules", str(archive_dir / "modules"))
    except OSError:
        pytest.skip("Cannot create symbolic links on this system")
    
    # Should detect master_adoc without freezing
    repo_type = detect_repo_type(str(tmp_path))
    assert repo_type == "master_adoc"


def test_detect_repo_type_skips_symlink_directories(tmp_path):
    """Test that symlinked directories are skipped during traversal."""
    
    # Create main directories
    real_dir = tmp_path / "real_modules"
    real_dir.mkdir()
    (real_dir / "master.adoc").write_text("= Real Master\n")
    
    # Create a symlink to real_dir
    linked_dir = tmp_path / "linked_modules"
    try:
        os.symlink(str(real_dir), str(linked_dir))
    except OSError:
        pytest.skip("Cannot create symbolic links on this system")
    
    # The function should find the master.adoc in real_dir but not traverse linked_dir
    repo_type = detect_repo_type(str(tmp_path))
    assert repo_type == "master_adoc"
    
    # Test that symlinked directories are not traversed
    only_symlink_path = tmp_path / "only_symlink_test"
    only_symlink_path.mkdir()
    
    # Create a directory outside that contains master.adoc
    external_dir = tmp_path / "external"
    external_dir.mkdir()
    (external_dir / "master.adoc").write_text("= External Master\n")
    
    # Create only a symlink to it inside our test directory
    symlinked_dir = only_symlink_path / "linked_dir"
    os.symlink(str(external_dir), str(symlinked_dir))
    
    # Should not find master.adoc since it's only accessible via symlink
    repo_type = detect_repo_type(str(only_symlink_path))
    assert repo_type == "unknown"