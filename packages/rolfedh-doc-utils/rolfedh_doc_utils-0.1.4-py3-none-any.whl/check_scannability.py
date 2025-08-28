"""
Scannability Checker for AsciiDoc Files

This script analyzes AsciiDoc (`.adoc`) files in the current directory to detect scannability issues that affect readability.

- Flags sentences that exceed 22 words (default, adjustable with -s)
- Flags paragraphs with more than 3 sentences (default, adjustable with -p)
- Excludes code blocks (delimited by ----, ...., or [source] blocks) from analysis

When using -o, the script prints the path to the report file; it does not attempt to open the file automatically. 

For full documentation, see check_scannability.md in this directory.
"""

import os
import sys
import argparse
from datetime import datetime
from doc_utils.scannability import check_scannability
from doc_utils.file_utils import collect_files, parse_exclude_list_file

BASE_SENTENCE_WORD_LIMIT = 22
BASE_PARAGRAPH_SENTENCE_LIMIT = 3

def print_help():
    print(__doc__)

def main():
    # Manual check for -h or --help to display the full docstring
    if '-h' in sys.argv or '--help' in sys.argv:
        print_help()
        sys.exit(0)

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-s', '--max-sentence-length', type=int, default=0, help='Extra words allowed per sentence (default: 0, base: 22)')
    parser.add_argument('-p', '--max-paragraph-sentences', type=int, default=0, help='Extra sentences allowed per paragraph (default: 0, base: 3)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output (show all files, even those without issues)')
    parser.add_argument('-o', '--output', action='store_true', help='Output the report to a timestamped txt file in your home directory')
    parser.add_argument('--exclude-dir', action='append', default=[], help='Directory to exclude (can be used multiple times).')
    parser.add_argument('--exclude-file', action='append', default=[], help='File to exclude (can be used multiple times).')
    parser.add_argument('--exclude-list', type=str, help='Path to a file containing directories or files to exclude, one per line.')
    # Do not add -h/--help to argparse, handled manually above
    args = parser.parse_args()

    exclude_dirs = list(args.exclude_dir)
    exclude_files = list(args.exclude_file)
    
    if args.exclude_list:
        list_dirs, list_files = parse_exclude_list_file(args.exclude_list)
        exclude_dirs.extend(list_dirs)
        exclude_files.extend(list_files)
    adoc_files = collect_files(['.'], {'.adoc'}, exclude_dirs, exclude_files)
    sentence_word_limit = BASE_SENTENCE_WORD_LIMIT + args.max_sentence_length
    paragraph_sentence_limit = BASE_PARAGRAPH_SENTENCE_LIMIT + args.max_paragraph_sentences
    long_sentences, long_paragraphs = check_scannability(
        adoc_files,
        max_sentence_length=sentence_word_limit,
        max_paragraph_sentences=paragraph_sentence_limit
    )
    # Build a report per file
    report_lines = []
    issues_by_file = {}
    for file, line, sent in long_sentences:
        issues_by_file.setdefault(file, []).append(f"Line {line}: Sentence exceeds {sentence_word_limit} words: {sent}")
    for file, line, count in long_paragraphs:
        issues_by_file.setdefault(file, []).append(f"Line {line}: Paragraph exceeds {paragraph_sentence_limit} sentences ({count} sentences)")
    for adoc in adoc_files:
        issues = issues_by_file.get(adoc, [])
        if issues or args.verbose:
            report_lines.append("")  # Blank line above each filename
            report_lines.append(f"{adoc}:")
            if issues:
                for issue in issues:
                    report_lines.append("  " + issue)
            else:
                report_lines.append("  No scannability issues found.")

    output = "\n".join(report_lines)
    if args.output:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        home_dir = os.path.expanduser("~")
        filename = os.path.join(home_dir, f"{timestamp}.txt")
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pwd = os.getcwd()
        cmd = "python3 " + " ".join([sys.argv[0]] + sys.argv[1:])
        metadata = [
            "Scannability Report",
            "",
            f"Purpose: This report lists scannability issues in .adoc files in the current directory.",
            f"Directory: {pwd}",
            f"Date and Time: {now_str}",
            f"Sentence length limit: {sentence_word_limit} words (22 plus -s/--max-sentence-length {args.max_sentence_length})",
            f"Paragraph sentence limit: {paragraph_sentence_limit} sentences (3 plus -p/--max-paragraph-sentences {args.max_paragraph_sentences})",
            "See check_scannability.md for usage instructions and examples.",
            f"Command: {cmd}",
            "",
            "------------------------------------------------------------",
            "",
        ]
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(metadata))
            f.write(output.lstrip() + "\n")
        print(f"Report written to: {filename}")
    else:
        if output:
            print(output.lstrip())

if __name__ == "__main__":
    main()
