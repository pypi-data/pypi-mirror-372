# doc_utils/file_utils.py

import os
import zipfile
from datetime import datetime


def collect_files(scan_dirs, extensions, exclude_dirs=None, exclude_files=None):
    """
    Recursively collect files with given extensions from scan_dirs, excluding symlinks, exclude_dirs, and exclude_files.
    Returns a list of normalized file paths.
    """
    exclude_dirs = set(os.path.abspath(os.path.normpath(d)) for d in (exclude_dirs or []))
    exclude_files = set(os.path.abspath(os.path.normpath(f)) for f in (exclude_files or []))
    found_files = []
    for base_dir in scan_dirs:
        for root, dirs, files in os.walk(base_dir):
            abs_root = os.path.abspath(root)
            # Check if current root directory should be excluded
            if abs_root in exclude_dirs:
                dirs[:] = []  # Skip this directory entirely
                continue
            # Exclude directories by absolute path and check for any parent directory exclusions
            new_dirs = []
            for d in dirs:
                dir_path = os.path.join(root, d)
                abs_dir_path = os.path.abspath(dir_path)
                if not os.path.islink(dir_path) and abs_dir_path not in exclude_dirs:
                    # Also check if any parent of this directory is excluded
                    excluded = False
                    for exclude_dir in exclude_dirs:
                        if abs_dir_path.startswith(exclude_dir + os.sep) or abs_dir_path == exclude_dir:
                            excluded = True
                            break
                    if not excluded:
                        new_dirs.append(d)
            dirs[:] = new_dirs

            for f in files:
                file_path = os.path.normpath(os.path.join(root, f))
                abs_file_path = os.path.abspath(file_path)
                if os.path.islink(file_path):
                    continue
                if abs_file_path in exclude_files:
                    continue
                if os.path.splitext(f)[1].lower() in extensions:
                    found_files.append(file_path)
    return list(dict.fromkeys(found_files))


def parse_exclude_list_file(exclude_list_path):
    """
    Parse an exclusion list file and return lists of directories and files to exclude.
    
    Args:
        exclude_list_path: Path to file containing paths to exclude (one per line)
        
    Returns:
        tuple: (exclude_dirs, exclude_files) lists
    """
    exclude_dirs = []
    exclude_files = []
    
    if exclude_list_path and os.path.exists(exclude_list_path):
        with open(exclude_list_path, 'r', encoding='utf-8') as excl:
            for line in excl:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if os.path.isdir(line):
                    exclude_dirs.append(line)
                else:
                    exclude_files.append(line)
    
    return exclude_dirs, exclude_files


def write_manifest_and_archive(unused_files, archive_dir, manifest_prefix, archive_prefix, archive=False):
    """
    Write a manifest of unused files and optionally archive and delete them.
    Returns the manifest path and (if archive=True) the archive path.
    """
    if not unused_files:
        print("No unused files found. No manifest or ZIP archive created.")
        return None, None
    now = datetime.now()
    datetime_str = now.strftime('%Y-%m-%d_%H%M%S')
    output_file = f'{manifest_prefix}-{datetime_str}.txt'
    os.makedirs(archive_dir, exist_ok=True)
    manifest_path = os.path.join(archive_dir, output_file)
    with open(manifest_path, 'w') as f:
        for file in unused_files:
            print(file)
            f.write(file + '\n')
    archive_path = None
    if archive:
        archive_path = os.path.join(archive_dir, f"{archive_prefix}-{datetime_str}.zip")
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in unused_files:
                arcname = os.path.relpath(file)
                print(f"Archiving: {file} -> {archive_path} ({arcname})")
                zipf.write(file, arcname)
                os.remove(file)
    return manifest_path, archive_path
