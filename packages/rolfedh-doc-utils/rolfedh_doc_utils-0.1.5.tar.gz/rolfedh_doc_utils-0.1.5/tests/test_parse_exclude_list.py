import os
import tempfile
import pytest
from doc_utils.file_utils import parse_exclude_list_file


def test_parse_exclude_list_file():
    """Test parsing of exclusion list files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test directories and files
        test_dir = os.path.join(tmpdir, 'test_dir')
        os.makedirs(test_dir)
        
        test_file = os.path.join(tmpdir, 'test_file.txt')
        with open(test_file, 'w') as f:
            f.write('test')
        
        # Create exclusion list file
        exclude_list = os.path.join(tmpdir, 'exclude.txt')
        with open(exclude_list, 'w') as f:
            f.write(f"""# This is a comment
{test_dir}
{test_file}
# Another comment
/nonexistent/path.txt

""")
        
        # Test parsing
        dirs, files = parse_exclude_list_file(exclude_list)
        
        assert test_dir in dirs
        assert test_file not in dirs
        assert test_file in files
        assert '/nonexistent/path.txt' in files
        assert len(dirs) == 1
        assert len(files) == 2


def test_parse_exclude_list_nonexistent():
    """Test parsing with nonexistent file."""
    dirs, files = parse_exclude_list_file('/nonexistent/file.txt')
    assert dirs == []
    assert files == []


def test_parse_exclude_list_empty():
    """Test parsing empty file."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("")
        temp_path = f.name
    
    try:
        dirs, files = parse_exclude_list_file(temp_path)
        assert dirs == []
        assert files == []
    finally:
        os.unlink(temp_path)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])