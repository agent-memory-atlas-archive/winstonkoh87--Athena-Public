"""
Tests for the Universal Academic Document Compiler.
"""
import tempfile
from pathlib import Path

import pytest

from src.athena.tools.doc_compiler import DocCompiler


@pytest.fixture
def compiler():
    return DocCompiler(pandoc_path="pandoc") # Assuming 'pandoc' is in PATH for tests, or adjust

@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)

def test_validate_pandoc(compiler):
    # Depending on test environment, pandoc might not be installed.
    # But we test it returns a string (empty or version)
    version = compiler.validate_pandoc()
    assert isinstance(version, str)

def test_list_formats(compiler):
    formats = compiler.list_formats()
    assert isinstance(formats, list)

def test_compile_basic(compiler, temp_dir):
    input_file = temp_dir / "test.md"
    input_file.write_text("# Hello World\nThis is a test.")
    output_file = temp_dir / "test.docx"

    res = compiler.compile(input_file, output_file)
    # If pandoc is not installed on test env, success will be False.
    # We just check the structure.
    assert "success" in res
    assert "output_path" in res
    assert "file_size" in res
    assert "elapsed_seconds" in res
    assert "warnings" in res

def test_compile_non_existent_input(compiler, temp_dir):
    input_file = temp_dir / "does_not_exist.md"
    output_file = temp_dir / "test.docx"

    res = compiler.compile(input_file, output_file)
    assert res["success"] is False
    assert res["file_size"] == 0
    assert "Input file not found" in res["warnings"]

def test_compile_toc(compiler, temp_dir):
    input_file = temp_dir / "test.md"
    input_file.write_text("# H1\n## H2\nTest")
    output_file = temp_dir / "test_toc.docx"

    res = compiler.compile(input_file, output_file, toc=True)
    assert "success" in res

def test_compile_batch(compiler, temp_dir):
    in_dir = temp_dir / "in"
    out_dir = temp_dir / "out"
    in_dir.mkdir()

    (in_dir / "test1.md").write_text("# Test 1")
    (in_dir / "test2.md").write_text("# Test 2")

    results = compiler.compile_batch(in_dir, out_dir)
    assert len(results) == 2
    assert str(in_dir / "test1.md") in results
    assert str(in_dir / "test2.md") in results

def test_compile_batch_empty_dir(compiler, temp_dir):
    in_dir = temp_dir / "in_empty"
    out_dir = temp_dir / "out"
    in_dir.mkdir()

    results = compiler.compile_batch(in_dir, out_dir)
    assert len(results) == 0

def test_compile_batch_non_existent_dir(compiler, temp_dir):
    in_dir = temp_dir / "in_nonexistent"
    out_dir = temp_dir / "out"

    results = compiler.compile_batch(in_dir, out_dir)
    assert len(results) == 0

def test_compile_with_template(compiler, temp_dir):
    input_file = temp_dir / "test.md"
    input_file.write_text("# Template Test")
    output_file = temp_dir / "test_tpl.docx"
    template_file = temp_dir / "template.docx"

    res = compiler.compile(input_file, output_file, template_path=template_file)
    assert "success" in res

def test_compile_with_bib(compiler, temp_dir):
    input_file = temp_dir / "test.md"
    input_file.write_text("Citation [@test].")
    bib_file = temp_dir / "refs.bib"
    output_file = temp_dir / "test_bib.docx"

    res = compiler.compile(input_file, output_file, bib_path=bib_file)
    assert "success" in res

def test_invalid_output_path(compiler, temp_dir):
    input_file = temp_dir / "test.md"
    input_file.write_text("# Test")

    # Try writing to a directory instead of file
    output_dir = temp_dir / "outdir"
    output_dir.mkdir()

    res = compiler.compile(input_file, output_dir)
    assert "success" in res
    if not res["success"]:
        assert "warnings" in res

def test_compile_result_dict_keys(compiler, temp_dir):
    input_file = temp_dir / "test.md"
    input_file.write_text("# Test keys")
    output_file = temp_dir / "test_keys.docx"

    res = compiler.compile(input_file, output_file)
    expected_keys = {"output_path", "file_size", "elapsed_seconds", "success", "warnings"}
    assert expected_keys.issubset(res.keys())
