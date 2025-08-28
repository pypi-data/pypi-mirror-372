import os
import tempfile
from doc_utils.unused_attributes import parse_attributes_file, find_adoc_files, scan_for_attribute_usage, find_unused_attributes

def make_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def test_parse_attributes_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        attr_path = os.path.join(tmpdir, 'attributes.adoc')
        make_file(attr_path, ":foo: bar\n:bar: baz\n:unused: 123\n")
        attrs = parse_attributes_file(attr_path)
        assert 'foo' in attrs
        assert 'bar' in attrs
        assert 'unused' in attrs

def test_find_adoc_files_and_usage():
    with tempfile.TemporaryDirectory() as tmpdir:
        attr_path = os.path.join(tmpdir, 'attributes.adoc')
        make_file(attr_path, ":foo: bar\n:bar: baz\n:unused: 123\n")
        adoc1 = os.path.join(tmpdir, 'a.adoc')
        adoc2 = os.path.join(tmpdir, 'b.adoc')
        make_file(adoc1, "This uses {foo} and {bar}.")
        make_file(adoc2, "No attributes here.")
        adoc_files = find_adoc_files(tmpdir)
        attrs = parse_attributes_file(attr_path)
        used = scan_for_attribute_usage(adoc_files, attrs)
        assert 'foo' in used
        assert 'bar' in used
        assert 'unused' not in used

def test_find_unused_attributes():
    with tempfile.TemporaryDirectory() as tmpdir:
        attr_path = os.path.join(tmpdir, 'attributes.adoc')
        make_file(attr_path, ":foo: bar\n:bar: baz\n:unused: 123\n")
        adoc1 = os.path.join(tmpdir, 'a.adoc')
        adoc2 = os.path.join(tmpdir, 'b.adoc')
        make_file(adoc1, "This uses {foo} and {bar}.")
        make_file(adoc2, "No attributes here.")
        unused = find_unused_attributes(attr_path, tmpdir)
        assert 'unused' in unused
        assert 'foo' not in unused
        assert 'bar' not in unused
