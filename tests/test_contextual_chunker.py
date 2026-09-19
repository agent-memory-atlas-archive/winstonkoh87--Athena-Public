"""Tests for athena.memory.contextual_chunker."""

from athena.memory.contextual_chunker import (
    chunk_markdown_contextual,
    contextual_chunk_text,
)


def test_chunk_empty_text():
    assert chunk_markdown_contextual("", "test.md") == []
    assert chunk_markdown_contextual("   ", "test.md") == []


def test_chunk_no_headings():
    text = "This is a simple paragraph without headings."
    chunks = chunk_markdown_contextual(text, "plain.md", chunk_size=100)
    assert len(chunks) == 1
    assert chunks[0].startswith("[Doc: plain.md]\n\n")
    assert "This is a simple paragraph without headings." in chunks[0]


def test_chunk_with_hierarchy():
    text = (
        "# System Architecture\n\n"
        "Introduction to the architecture.\n\n"
        "## Memory Subsystem\n\n"
        "Details about the memory subsystem and storage.\n\n"
        "### Vector Cache\n\n"
        "Deeply nested details about vector cache performance and indexing."
    )
    chunks = chunk_markdown_contextual(text, "arch.md", chunk_size=80, overlap=20)
    assert len(chunks) >= 2
    # First chunk should contain top-level breadcrumb
    assert "[Doc: arch.md | # System Architecture]" in chunks[0]
    # Subsequent chunks should preserve nested hierarchy
    has_nested = any("Memory Subsystem" in c for c in chunks)
    assert has_nested


def test_contextual_chunk_text_wrapper():
    text = "# Title\n\nSome body text."
    chunks = contextual_chunk_text(text, "doc.md")
    assert len(chunks) == 1
    assert chunks[0].startswith("[Doc: doc.md | # Title]\n\n")
