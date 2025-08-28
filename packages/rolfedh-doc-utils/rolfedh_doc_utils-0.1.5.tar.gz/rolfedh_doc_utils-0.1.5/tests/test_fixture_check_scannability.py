# Test fixture for check_scannability.py
# Directory structure:
# test-fixture/
# ├── test1.adoc (contains long sentence and long paragraph)
# ├── test2.adoc (well-formed)
#
# Contents:
# test1.adoc: One paragraph with a very long sentence and another with many short sentences.
# test2.adoc: Short sentences and paragraphs.

import os

def setup_test_fixture_check_scannability(base_dir):
    # Create test1.adoc with a long sentence and a long paragraph
    with open(os.path.join(base_dir, 'test1.adoc'), 'w') as f:
        f.write('This is a very long sentence that should be flagged by the script because it contains way more than the allowed number of words in a single sentence, making it hard to scan and understand for most readers.\n')
        f.write('This is a short sentence. This is another short sentence. This is yet another short sentence. This is a fourth short sentence. This is a fifth short sentence. This is a sixth short sentence. This is a seventh short sentence. This is an eighth short sentence. This is a ninth short sentence. This is a tenth short sentence.\n')
    # Create test2.adoc with well-formed content
    with open(os.path.join(base_dir, 'test2.adoc'), 'w') as f:
        f.write('Short sentence. Another short sentence.\n')

# Usage:
# import tempfile
# with tempfile.TemporaryDirectory() as tmpdir:
#     setup_test_fixture_check_scannability(tmpdir)
#     # Now run check_scannability.py in tmpdir
