# doc_utils/unused_adoc.py

import os
import re
from .file_utils import collect_files, write_manifest_and_archive
from .topic_map_parser import detect_repo_type, get_all_topic_map_references

def find_unused_adoc(scan_dirs, archive_dir, archive=False, exclude_dirs=None, exclude_files=None):
    # Print safety warning
    print("\n⚠️  SAFETY: Work in a git branch! Run without --archive first to preview.\n")
    
    # Detect repository type
    repo_type = detect_repo_type()
    print(f"Detected repository type: {repo_type}")
    
    # Collect all .adoc files in scan directories
    asciidoc_files = collect_files(scan_dirs, {'.adoc'}, exclude_dirs, exclude_files)
    
    # Track which files are referenced
    referenced_files = set()
    
    if repo_type == 'topic_map':
        # For OpenShift-docs style repos, get references from topic maps
        topic_references = get_all_topic_map_references()
        # Convert to basenames for comparison
        referenced_files.update(os.path.basename(ref) for ref in topic_references)
    
    # Always scan for include:: directives in all .adoc files
    include_pattern = re.compile(r'include::(.+?)\[')
    adoc_files = collect_files(['.'], {'.adoc'}, exclude_dirs, exclude_files)
    
    for file_path in adoc_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                includes = include_pattern.findall(content)
                # Extract just the filename from the include path
                for include in includes:
                    # Handle both relative and absolute includes
                    include_basename = os.path.basename(include)
                    referenced_files.add(include_basename)
        except Exception as e:
            print(f"Warning: could not read {file_path}: {e}")
    
    # Find unused files by comparing basenames
    unused_files = [f for f in asciidoc_files if os.path.basename(f) not in referenced_files]
    unused_files = list(dict.fromkeys(unused_files))  # Remove duplicates
    
    print(f"Found {len(unused_files)} unused files out of {len(asciidoc_files)} total files in scan directories")
    
    return write_manifest_and_archive(
        unused_files, archive_dir, 'to-archive', 'to-archive', archive=archive
    )
