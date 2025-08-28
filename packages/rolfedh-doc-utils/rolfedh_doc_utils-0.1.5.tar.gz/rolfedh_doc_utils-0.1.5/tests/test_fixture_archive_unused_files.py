# Test fixture for archive_unused_files.py
# Directory structure:
# test-fixture/
# ├── modules/
# │   ├── used.adoc
# │   ├── unused1.adoc
# │   └── unused2.adoc
# ├── assemblies/
# │   └── master.adoc (includes used.adoc)
# ├── archive/  (should be empty before test)
#
# Contents:
# modules/used.adoc      (referenced by assemblies/master.adoc)
# modules/unused1.adoc   (not referenced)
# modules/unused2.adoc   (not referenced)
# assemblies/master.adoc (includes ../modules/used.adoc)

import os

def setup_test_fixture_archive_unused_files(base_dir):
    os.makedirs(os.path.join(base_dir, 'modules'), exist_ok=True)
    os.makedirs(os.path.join(base_dir, 'assemblies'), exist_ok=True)
    os.makedirs(os.path.join(base_dir, 'archive'), exist_ok=True)
    # Create AsciiDoc files
    with open(os.path.join(base_dir, 'modules', 'used.adoc'), 'w') as f:
        f.write('This is a used module.\n')
    with open(os.path.join(base_dir, 'modules', 'unused1.adoc'), 'w') as f:
        f.write('This is an unused module.\n')
    with open(os.path.join(base_dir, 'modules', 'unused2.adoc'), 'w') as f:
        f.write('This is another unused module.\n')
    with open(os.path.join(base_dir, 'assemblies', 'master.adoc'), 'w') as f:
        f.write('include::../modules/used.adoc[]\n')

# Usage:
# import tempfile
# with tempfile.TemporaryDirectory() as tmpdir:
#     setup_test_fixture_archive_unused_files(tmpdir)
#     # Now run archive_unused_files.py in tmpdir
