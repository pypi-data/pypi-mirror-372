"""Test automatic directory discovery for archive-unused-files."""

import os
import tempfile
import pytest
from doc_utils.unused_adoc import find_scan_directories


def test_find_scan_directories_standard_structure(tmp_path):
    """Test discovery with standard directory structure."""
    
    # Create standard structure
    (tmp_path / "modules").mkdir()
    (tmp_path / "modules" / "test.adoc").write_text("= Test\n")
    
    (tmp_path / "assemblies").mkdir()
    (tmp_path / "assemblies" / "assembly.adoc").write_text("= Assembly\n")
    
    # Find directories
    dirs = find_scan_directories(str(tmp_path))
    
    # Should find both directories
    assert len(dirs) == 2
    assert any("modules" in d for d in dirs)
    assert any("assemblies" in d for d in dirs)


def test_find_scan_directories_nested_structure(tmp_path):
    """Test discovery with nested directory structure."""
    
    # Create nested structure like red-hat-insights-documentation
    downstream = tmp_path / "downstream"
    downstream.mkdir()
    
    (downstream / "modules").mkdir()
    (downstream / "modules" / "test.adoc").write_text("= Test\n")
    
    (downstream / "assemblies").mkdir()
    (downstream / "assemblies" / "assembly.adoc").write_text("= Assembly\n")
    
    # Find directories
    dirs = find_scan_directories(str(tmp_path))
    
    # Should find both nested directories
    assert len(dirs) == 2
    assert any("downstream/modules" in d or "downstream\\modules" in d for d in dirs)
    assert any("downstream/assemblies" in d or "downstream\\assemblies" in d for d in dirs)


def test_find_scan_directories_with_rn(tmp_path):
    """Test discovery includes modules/rn directory when it contains .adoc files."""
    
    # Create modules with rn subdirectory
    modules = tmp_path / "modules"
    modules.mkdir()
    (modules / "test.adoc").write_text("= Test\n")
    
    rn_dir = modules / "rn"
    rn_dir.mkdir()
    (rn_dir / "release-notes.adoc").write_text("= Release Notes\n")
    
    # Find directories
    dirs = find_scan_directories(str(tmp_path))
    
    # Should find modules and modules/rn
    assert len(dirs) == 2
    assert any("modules/rn" in d or "modules\\rn" in d for d in dirs)


def test_find_scan_directories_empty_dirs(tmp_path):
    """Test that empty directories without .adoc files are not included."""
    
    # Create directories without .adoc files
    (tmp_path / "modules").mkdir()
    (tmp_path / "assemblies").mkdir()
    
    # Find directories
    dirs = find_scan_directories(str(tmp_path))
    
    # Should find no directories since they don't contain .adoc files
    assert len(dirs) == 0


def test_find_scan_directories_with_exclusions(tmp_path):
    """Test directory discovery with exclusions."""
    
    # Create multiple module directories
    (tmp_path / "modules").mkdir()
    (tmp_path / "modules" / "test.adoc").write_text("= Test\n")
    
    archived = tmp_path / "archived"
    archived.mkdir()
    (archived / "modules").mkdir()
    (archived / "modules" / "old.adoc").write_text("= Old\n")
    
    # Find directories excluding archived
    dirs = find_scan_directories(str(tmp_path), exclude_dirs=[str(archived)])
    
    # Should only find the non-excluded modules
    assert len(dirs) == 1
    assert "archived" not in dirs[0]


def test_find_scan_directories_skips_hidden(tmp_path):
    """Test that hidden directories are skipped."""
    
    # Create visible modules
    (tmp_path / "modules").mkdir()
    (tmp_path / "modules" / "test.adoc").write_text("= Test\n")
    
    # Create hidden directory
    hidden = tmp_path / ".archive"
    hidden.mkdir()
    (hidden / "modules").mkdir()
    (hidden / "modules" / "archived.adoc").write_text("= Archived\n")
    
    # Find directories
    dirs = find_scan_directories(str(tmp_path))
    
    # Should only find visible modules
    assert len(dirs) == 1
    assert ".archive" not in dirs[0]


def test_find_scan_directories_multiple_locations(tmp_path):
    """Test discovery with modules/assemblies in multiple locations."""
    
    # Create modules in multiple places
    (tmp_path / "modules").mkdir()
    (tmp_path / "modules" / "root.adoc").write_text("= Root\n")
    
    content1 = tmp_path / "content1"
    content1.mkdir()
    (content1 / "modules").mkdir()
    (content1 / "modules" / "content1.adoc").write_text("= Content1\n")
    
    content2 = tmp_path / "content2" 
    content2.mkdir()
    (content2 / "assemblies").mkdir()
    (content2 / "assemblies" / "assembly2.adoc").write_text("= Assembly2\n")
    
    # Find directories
    dirs = find_scan_directories(str(tmp_path))
    
    # Should find all three directories
    assert len(dirs) == 3