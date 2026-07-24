"""
Tests for SafeCrossEncoder and chunk verification (src/athena/tools/reranker.py & memory/sync.py).
"""

from athena.tools.reranker import SafeCrossEncoder
from athena.memory.sync import verify_chunk_integrity
from athena.core.models import SearchResult

def test_safe_cross_encoder_empty():
    encoder = SafeCrossEncoder()
    res, fallback = encoder.rerank("test query", [], top_k=5)
    assert res == []
    assert fallback is False

def test_safe_cross_encoder_fallback():
    encoder = SafeCrossEncoder()
    dummy_doc = SearchResult(id="1", content="Sample content", title="Title", file_path="sample.md")
    res, fallback = encoder.rerank("test query", [dummy_doc], top_k=5)
    assert len(res) == 1

def test_verify_chunk_integrity():
    res = verify_chunk_integrity(expected_min_ratio=0.1)
    assert isinstance(res, bool)
