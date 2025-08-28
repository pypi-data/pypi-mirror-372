"""
Archive Unused AsciiDoc Files

Automatically discovers and scans 'modules' and 'assemblies' directories for AsciiDoc files 
not referenced by any other AsciiDoc file in the project. Optionally archives and deletes them.

For full documentation and usage examples, see archive_unused_files.md in this directory.
"""

import argparse
from doc_utils.unused_adoc import find_unused_adoc
from doc_utils.file_utils import parse_exclude_list_file

def main():
    parser = argparse.ArgumentParser(
        description='Archive unused AsciiDoc files.',
        epilog='By default, automatically discovers all modules and assemblies directories in the repository.'
    )
    parser.add_argument('--archive', action='store_true', help='Move the files to a dated zip in the archive directory.')
    parser.add_argument('--scan-dir', action='append', default=[], help='Specific directory to scan (can be used multiple times). If not specified, auto-discovers directories.')
    parser.add_argument('--exclude-dir', action='append', default=[], help='Directory to exclude (can be used multiple times).')
    parser.add_argument('--exclude-file', action='append', default=[], help='File to exclude (can be used multiple times).')
    parser.add_argument('--exclude-list', type=str, help='Path to a file containing directories or files to exclude, one per line.')
    args = parser.parse_args()

    # Use provided scan directories or None for auto-discovery
    scan_dirs = args.scan_dir if args.scan_dir else None
    archive_dir = './archive'

    exclude_dirs = list(args.exclude_dir)
    exclude_files = list(args.exclude_file)
    
    if args.exclude_list:
        list_dirs, list_files = parse_exclude_list_file(args.exclude_list)
        exclude_dirs.extend(list_dirs)
        exclude_files.extend(list_files)

    find_unused_adoc(scan_dirs, archive_dir, args.archive, exclude_dirs, exclude_files)

if __name__ == '__main__':
    main()
