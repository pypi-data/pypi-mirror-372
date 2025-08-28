# Test fixture for archive_unused_images.py

# Directory structure:
# test-fixture/
# ├── images/
# │   ├── used1.png
# │   ├── used2.jpg
# │   ├── unused1.png
# │   └── unused2.jpg
# ├── docs/
# │   ├── referenced.adoc
# │   └── orphan.adoc
# └── archive/  (should be empty before test)

# Contents:
# images/used1.png      (empty file, referenced)
# images/used2.jpg      (empty file, referenced)
# images/unused1.png    (empty file, NOT referenced)
# images/unused2.jpg    (empty file, NOT referenced)
# docs/referenced.adoc  (references used1.png and used2.jpg)
# docs/orphan.adoc      (does not reference any images)

import os

def setup_test_fixture(base_dir):
    os.makedirs(os.path.join(base_dir, 'images'), exist_ok=True)
    os.makedirs(os.path.join(base_dir, 'docs'), exist_ok=True)
    os.makedirs(os.path.join(base_dir, 'archive'), exist_ok=True)
    # Create image files
    for fname in ['used1.png', 'used2.jpg', 'unused1.png', 'unused2.jpg']:
        with open(os.path.join(base_dir, 'images', fname), 'wb') as f:
            f.write(b'')
    # Create AsciiDoc file that references two images
    with open(os.path.join(base_dir, 'docs', 'referenced.adoc'), 'w') as f:
        f.write('image::../images/used1.png[]\n')
        f.write('image::../images/used2.jpg[]\n')
    # Create an orphan AsciiDoc file
    with open(os.path.join(base_dir, 'docs', 'orphan.adoc'), 'w') as f:
        f.write('This file does not reference any images.\n')

# Usage:
# import tempfile
# with tempfile.TemporaryDirectory() as tmpdir:
#     setup_test_fixture(tmpdir)
#     # Now run archive_unused_images.py in tmpdir
