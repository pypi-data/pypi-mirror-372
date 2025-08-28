# doc_utils/unused_images.py

import os
import re
from .file_utils import collect_files, write_manifest_and_archive

IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.svg'}

def find_unused_images(scan_dirs, archive_dir, archive=False, exclude_dirs=None, exclude_files=None):
    # Print safety warning
    print("\n⚠️  SAFETY: Work in a git branch! Run without --archive first to preview.\n")
    
    image_files = collect_files(scan_dirs, IMAGE_EXTENSIONS, exclude_dirs, exclude_files)
    adoc_files = collect_files(['.'], {'.adoc'}, exclude_dirs, exclude_files)
    referenced_images = set()
    image_ref_pattern = re.compile(r'(?i)image::([^\[]+)[\[]|image:([^\[]+)[\[]|"([^"\s]+\.(?:png|jpg|jpeg|gif|svg))"')
    for adoc_file in adoc_files:
        try:
            with open(adoc_file, 'r', encoding='utf-8') as f:
                content = f.read()
                for match in image_ref_pattern.findall(content):
                    for group in match:
                        if group:
                            referenced_images.add(os.path.basename(group))
        except Exception as e:
            print(f"Warning: could not read {adoc_file}: {e}")
    unused_images = [f for f in image_files if os.path.basename(f) not in referenced_images]
    unused_images = list(dict.fromkeys(unused_images))
    return write_manifest_and_archive(
        unused_images, archive_dir, 'unused-images', 'unused-images', archive=archive
    )
