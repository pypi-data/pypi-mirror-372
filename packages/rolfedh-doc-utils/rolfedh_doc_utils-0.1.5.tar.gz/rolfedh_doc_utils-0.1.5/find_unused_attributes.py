"""
Find Unused AsciiDoc Attributes

Scans a user-specified attributes file (e.g., attributes.adoc) for attribute definitions (e.g., :version: 1.1), then recursively scans all .adoc files in the current directory (ignoring symlinks) for usages of those attributes (e.g., {version}).

Any attribute defined but not used in any .adoc file is reported as NOT USED in both the command line output and a timestamped output file.
"""

import argparse
import os
from datetime import datetime
from doc_utils.unused_attributes import find_unused_attributes

def main():
    parser = argparse.ArgumentParser(description='Find unused AsciiDoc attributes.')
    parser.add_argument('attributes_file', help='Path to the attributes.adoc file to scan for attribute definitions.')
    parser.add_argument('-o', '--output', action='store_true', help='Write results to a timestamped txt file in your home directory.')
    args = parser.parse_args()

    unused = find_unused_attributes(args.attributes_file, '.')

    lines = [f":{attr}:  NOT USED" for attr in unused]
    output = '\n'.join(lines)

    if output:
        print('Unused attributes:')
        print(output)
    else:
        print('All attributes are used.')

    if args.output and output:
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        home_dir = os.path.expanduser('~')
        filename = os.path.join(home_dir, f'unused_attributes_{timestamp}.txt')
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('Unused attributes in ' + args.attributes_file + '\n')
            f.write(output + '\n')
        print(f'Results written to: {filename}')

if __name__ == '__main__':
    main()
