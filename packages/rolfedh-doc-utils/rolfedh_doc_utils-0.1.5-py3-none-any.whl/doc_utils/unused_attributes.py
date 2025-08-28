"""
Module for finding unused AsciiDoc attributes.

Functions:
- parse_attributes_file: Parse attribute names from an attributes.adoc file.
- find_adoc_files: Recursively find all .adoc files in a directory (ignoring symlinks).
- scan_for_attribute_usage: Find which attributes are used in a set of .adoc files.
- find_unused_attributes: Main function to return unused attributes.
"""

import os
import re
from typing import Set, List

def parse_attributes_file(attr_file: str) -> Set[str]:
    attributes = set()
    with open(attr_file, 'r', encoding='utf-8') as f:
        for line in f:
            match = re.match(r'^:([\w-]+):', line.strip())
            if match:
                attributes.add(match.group(1))
    return attributes

def find_adoc_files(root_dir: str) -> List[str]:
    adoc_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir, followlinks=False):
        for fname in filenames:
            if fname.endswith('.adoc'):
                full_path = os.path.join(dirpath, fname)
                if not os.path.islink(full_path):
                    adoc_files.append(full_path)
    return adoc_files

def scan_for_attribute_usage(adoc_files: List[str], attributes: Set[str]) -> Set[str]:
    used = set()
    attr_pattern = re.compile(r'\{([\w-]+)\}')
    for file in adoc_files:
        with open(file, 'r', encoding='utf-8') as f:
            for line in f:
                for match in attr_pattern.findall(line):
                    if match in attributes:
                        used.add(match)
    return used

def find_unused_attributes(attr_file: str, adoc_root: str = '.') -> List[str]:
    attributes = parse_attributes_file(attr_file)
    adoc_files = find_adoc_files(adoc_root)
    used = scan_for_attribute_usage(adoc_files, attributes)
    unused = sorted(attributes - used)
    return unused
