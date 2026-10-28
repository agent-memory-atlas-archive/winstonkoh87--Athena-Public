"""Tests that PersistentEmbeddingCache gracefully handles SQLite corruption, disk errors, or malformed state."""

import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

from athena.memory.vectors import PersistentEmbeddingCache


def test_embedding_cache_handles_corrupt_database_on_get():
    """When the SQLite cache database is malformed or corrupted, get() must return None (cache miss) instead of crashing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "corrupt.db"

        cache = PersistentEmbeddingCache.__new__(PersistentEmbeddingCache)
        cache.legacy_json = Path(tmpdir) / "dummy.json"
        cache.db_path = db_path
        cache.lock = MagicMock()
        cache.lock.__enter__.return_value = None
        cache.lock.__exit__.return_value = None
        mock_conn = MagicMock()
        mock_conn.execute.side_effect = sqlite3.DatabaseError("database disk image is malformed")
        cache._conn = mock_conn

        # In pre-fix state, cache.get() will raise sqlite3.DatabaseError
        # In post-fix state, it must return None gracefully
        result = cache.get("test_hash")
        assert result is None


def test_embedding_cache_handles_corrupt_database_on_set():
    """When SQLite fails on set(), it must not crash the caller."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "corrupt.db"
        cache = PersistentEmbeddingCache.__new__(PersistentEmbeddingCache)
        cache.legacy_json = Path(tmpdir) / "dummy.json"
        cache.db_path = db_path
        cache.lock = MagicMock()
        cache.lock.__enter__.return_value = None
        cache.lock.__exit__.return_value = None
        mock_conn = MagicMock()
        mock_conn.execute.side_effect = sqlite3.DatabaseError("database disk image is malformed")
        cache._conn = mock_conn

        # In pre-fix state, cache.set() will raise sqlite3.DatabaseError
        # In post-fix state, it must catch and not raise
        cache.set("test_hash", [0.1, 0.2, 0.3])


def test_cache_key_includes_model_task_and_dims():
    """F-03 regression test: Cache key must namespace model, task_type, and dims."""
    from athena.memory.vectors import _hash_text

    h_query = _hash_text("alpha", model="gemini-embedding-001", task_type="RETRIEVAL_QUERY", dims=3072)
    h_doc = _hash_text("alpha", model="gemini-embedding-001", task_type="RETRIEVAL_DOCUMENT", dims=3072)
    h_diff_model = _hash_text("alpha", model="gemini-embedding-002", task_type="RETRIEVAL_QUERY", dims=3072)
    h_diff_dims = _hash_text("alpha", model="gemini-embedding-001", task_type="RETRIEVAL_QUERY", dims=1536)

    assert h_query != h_doc, "RETRIEVAL_QUERY and RETRIEVAL_DOCUMENT must produce distinct cache hashes!"
    assert h_query != h_diff_model, "Different models must produce distinct cache hashes!"
    assert h_query != h_diff_dims, "Different dimensions must produce distinct cache hashes!"
    assert len(h_query) == 64, "Expected SHA-256 (64 hex characters) hash"

