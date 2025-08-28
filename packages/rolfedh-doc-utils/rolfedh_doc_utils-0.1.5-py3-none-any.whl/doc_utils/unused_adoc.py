# doc_utils/unused_adoc.py

import os
import re
from .file_utils import collect_files, write_manifest_and_archive
from .topic_map_parser import detect_repo_type, get_all_topic_map_references

def find_scan_directories(base_path='.', exclude_dirs=None):
    """
    Automatically find all 'modules' and 'assemblies' directories in the repository.
    
    Returns a list of paths to scan.
    """
    scan_dirs = []
    exclude_dirs = exclude_dirs or []
    
    for root, dirs, files in os.walk(base_path):
        # Skip symbolic links to prevent issues
        dirs[:] = [d for d in dirs if not os.path.islink(os.path.join(root, d))]
        
        # Skip excluded directories
        for exclude_dir in exclude_dirs:
            abs_exclude = os.path.abspath(exclude_dir)
            if os.path.abspath(root).startswith(abs_exclude):
                dirs[:] = []  # Don't descend into excluded directories
                break
        
        # Skip hidden directories and common non-content directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'build', 'dist', 'target']]
        
        # Look for modules and assemblies directories
        for d in dirs:
            if d in ['modules', 'assemblies']:
                dir_path = os.path.join(root, d)
                # Check if this directory or any subdirectory contains .adoc files
                has_adoc = False
                for subroot, subdirs, subfiles in os.walk(dir_path):
                    # Skip symbolic links
                    subdirs[:] = [sd for sd in subdirs if not os.path.islink(os.path.join(subroot, sd))]
                    if any(f.endswith('.adoc') for f in subfiles):
                        has_adoc = True
                        break
                if has_adoc:
                    scan_dirs.append(dir_path)
    
    # Also check for modules/rn pattern if modules exists
    modules_dirs = [d for d in scan_dirs if os.path.basename(d) == 'modules']
    for modules_dir in modules_dirs:
        rn_dir = os.path.join(modules_dir, 'rn')
        if os.path.isdir(rn_dir):
            # Check if rn directory or subdirectories contain .adoc files
            has_adoc = False
            for subroot, subdirs, subfiles in os.walk(rn_dir):
                subdirs[:] = [sd for sd in subdirs if not os.path.islink(os.path.join(subroot, sd))]
                if any(f.endswith('.adoc') for f in subfiles):
                    has_adoc = True
                    break
            if has_adoc:
                scan_dirs.append(rn_dir)
    
    return scan_dirs

def find_unused_adoc(scan_dirs=None, archive_dir='./archive', archive=False, exclude_dirs=None, exclude_files=None):
    # Print safety warning
    print("\n⚠️  SAFETY: Work in a git branch! Run without --archive first to preview.\n")
    
    # If no scan_dirs provided, auto-discover them
    if not scan_dirs:
        scan_dirs = find_scan_directories(exclude_dirs=exclude_dirs)
        if scan_dirs:
            print(f"Auto-discovered directories to scan:")
            for dir_path in sorted(scan_dirs):
                print(f"  - {dir_path}")
        else:
            print("No 'modules' or 'assemblies' directories found containing .adoc files.")
            print("Please run this tool from your documentation repository root.")
            return
    
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
