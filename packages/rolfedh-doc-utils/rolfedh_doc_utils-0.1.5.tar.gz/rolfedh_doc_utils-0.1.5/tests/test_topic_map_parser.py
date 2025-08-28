import pytest
import os
import tempfile
import yaml
from doc_utils.topic_map_parser import (
    detect_repo_type, 
    extract_files_from_topic_map,
    process_topic_group,
    get_all_topic_map_references
)


class TestDetectRepoType:
    def test_detect_topic_map_repo(self):
        """Test detection of OpenShift-docs style repository with topic maps."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create _topic_maps directory with a .yml file
            topic_maps_dir = os.path.join(tmpdir, '_topic_maps')
            os.makedirs(topic_maps_dir)
            
            # Create a sample topic map file
            topic_map_file = os.path.join(topic_maps_dir, '_topic_map.yml')
            with open(topic_map_file, 'w') as f:
                f.write("---\nName: Test\nDir: test\n")
            
            assert detect_repo_type(tmpdir) == 'topic_map'
    
    def test_detect_master_adoc_repo(self):
        """Test detection of traditional repository with master.adoc files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a master.adoc file
            master_file = os.path.join(tmpdir, 'master.adoc')
            with open(master_file, 'w') as f:
                f.write("= Master Document\n")
            
            assert detect_repo_type(tmpdir) == 'master_adoc'
    
    def test_detect_unknown_repo(self):
        """Test detection returns 'unknown' for unrecognized repository structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Empty directory
            assert detect_repo_type(tmpdir) == 'unknown'


class TestExtractFilesFromTopicMap:
    def test_extract_simple_topic_map(self):
        """Test extracting files from a simple topic map."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("""---
Name: Overview
Dir: welcome
Topics:
- Name: Welcome
  File: index
- Name: Introduction
  File: intro
""")
            f.flush()
            
            try:
                files = extract_files_from_topic_map(f.name)
                assert 'welcome/index.adoc' in files
                assert 'welcome/intro.adoc' in files
                assert len(files) == 2
            finally:
                os.unlink(f.name)
    
    def test_extract_nested_topic_map(self):
        """Test extracting files from a topic map with nested topics."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("""---
Name: Architecture
Dir: architecture
Topics:
- Name: Overview
  File: index
- Name: Components
  Dir: components
  Topics:
    - Name: API Server
      File: api-server
    - Name: Controller
      File: controller
""")
            f.flush()
            
            try:
                files = extract_files_from_topic_map(f.name)
                assert 'architecture/index.adoc' in files
                assert 'architecture/components/api-server.adoc' in files
                assert 'architecture/components/controller.adoc' in files
                assert len(files) == 3
            finally:
                os.unlink(f.name)
    
    def test_extract_multiple_documents(self):
        """Test extracting files from a YAML file with multiple documents."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("""---
Name: Overview
Dir: welcome
Topics:
- Name: Welcome
  File: index
---
Name: Installation
Dir: install
Topics:
- Name: Quick Start
  File: quickstart
""")
            f.flush()
            
            try:
                files = extract_files_from_topic_map(f.name)
                assert 'welcome/index.adoc' in files
                assert 'install/quickstart.adoc' in files
                assert len(files) == 2
            finally:
                os.unlink(f.name)


class TestProcessTopicGroup:
    def test_process_simple_group(self):
        """Test processing a simple topic group."""
        group = {
            'Name': 'Test Group',
            'Dir': 'test',
            'Topics': [
                {'Name': 'Topic 1', 'File': 'topic1'},
                {'Name': 'Topic 2', 'File': 'topic2'}
            ]
        }
        
        referenced_files = set()
        process_topic_group(group, referenced_files)
        
        assert 'test/topic1.adoc' in referenced_files
        assert 'test/topic2.adoc' in referenced_files
    
    def test_process_group_with_parent_dir(self):
        """Test processing a topic group with a parent directory."""
        group = {
            'Name': 'Subgroup',
            'Dir': 'sub',
            'Topics': [
                {'Name': 'Topic', 'File': 'topic'}
            ]
        }
        
        referenced_files = set()
        process_topic_group(group, referenced_files, parent_dir='parent')
        
        assert 'parent/sub/topic.adoc' in referenced_files


class TestGetAllTopicMapReferences:
    def test_get_all_references(self):
        """Test getting all references from all topic maps."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create _topic_maps directory
            topic_maps_dir = os.path.join(tmpdir, '_topic_maps')
            os.makedirs(topic_maps_dir)
            
            # Create first topic map
            topic_map1 = os.path.join(topic_maps_dir, 'map1.yml')
            with open(topic_map1, 'w') as f:
                f.write("""---
Name: Group1
Dir: group1
Topics:
- Name: Topic1
  File: topic1
""")
            
            # Create second topic map
            topic_map2 = os.path.join(topic_maps_dir, 'map2.yml')
            with open(topic_map2, 'w') as f:
                f.write("""---
Name: Group2
Dir: group2
Topics:
- Name: Topic2
  File: topic2
""")
            
            references = get_all_topic_map_references(tmpdir)
            assert 'group1/topic1.adoc' in references
            assert 'group2/topic2.adoc' in references
            assert len(references) == 2