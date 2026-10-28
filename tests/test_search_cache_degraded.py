"""
test_search_cache_degraded.py — Verify degraded search results are never cached.
"""

import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import athena.core.cache
import athena.tools.search
from athena.core.cache import QueryCache
from athena.tools.search import run_search


def test_degraded_search_is_not_cached(tmp_path, capsys):
    """When vector channel fails, the degraded result must NOT be cached.
    Subsequent search must still report quality='degraded' and degraded_recall=True."""
    tmp_cache = QueryCache(cache_dir=tmp_path, ttl_hours=24)

    def failing_get_embedding(text, **kwargs):
        raise TimeoutError("Embedding fetch timed out")

    with (
        patch.object(athena.tools.search, "get_search_cache", return_value=tmp_cache),
        patch("athena.memory.vectors.get_embedding", side_effect=failing_get_embedding),
    ):
            # Call 1: Degraded search
            run_search("test query for degradation", json_output=True, limit=2)
            out1 = capsys.readouterr().out
            payload1 = json.loads(out1.strip().splitlines()[-1])
            assert payload1.get("quality") == "degraded", f"Expected degraded in call 1, got {payload1}"
            assert payload1.get("degraded_recall") is True

            # Call 2: Second run of identical query
            run_search("test query for degradation", json_output=True, limit=2)
            out2 = capsys.readouterr().out
            payload2 = json.loads(out2.strip().splitlines()[-1])

            # In unpatched code, call 2 hit cache and returned quality="hit", degraded_recall=False
            assert payload2.get("quality") == "degraded", (
                f"Call 2 was served from cache as healthy! Expected quality='degraded', got {payload2.get('quality')}"
            )
            assert payload2.get("degraded_recall") is True, (
                f"Call 2 was served from cache as healthy! Expected degraded_recall=True, got {payload2.get('degraded_recall')}"
            )


def test_athena_search_cache_off(tmp_path, capsys):
    """When ATHENA_SEARCH_CACHE=off, cache lookups and storage are bypassed."""
    tmp_cache = QueryCache(cache_dir=tmp_path, ttl_hours=24)

    with (
        patch.dict(os.environ, {"ATHENA_SEARCH_CACHE": "off"}),
        patch.object(athena.tools.search, "get_search_cache", return_value=tmp_cache),
    ):
            run_search("test cache off query", json_output=True, limit=1)
            assert len(tmp_cache._cache) == 0, "Cache should not have stored any entries when ATHENA_SEARCH_CACHE=off"


def test_collect_vectors_reports_depleted_on_quota_exhausted(capsys):
    """When EmbeddingQuotaExhausted is raised, collect_vectors must record status='depleted'."""
    from athena.memory.vectors import EmbeddingQuotaExhausted
    from athena.tools.search import collect_vectors, get_channel_health

    def quota_failing_get_embedding(text, **kwargs):
        raise EmbeddingQuotaExhausted("Aborting: 5 consecutive HTTP 429 errors. Gemini API quota exhausted — retry later.")

    with patch("athena.memory.vectors.get_embedding", side_effect=quota_failing_get_embedding):
        results = collect_vectors("test query")
        assert results == []
        health = get_channel_health()
        assert health.get("vector", {}).get("status") == "depleted"
        assert "quota exhausted" in (health.get("vector", {}).get("error") or "").lower()


def test_depleted_vector_channel_marks_degraded_and_is_not_cached(tmp_path, capsys):
    """F-01 regression test: When vector channel is depleted (HTTP 429/402),
    run_search must mark degraded_recall=True, quality='degraded', channels_failed must include 'vector',
    and result must NOT be cached.
    """
    from athena.memory.vectors import EmbeddingQuotaExhausted

    tmp_cache = QueryCache(cache_dir=tmp_path, ttl_hours=24)

    def quota_failing_get_embedding(text, **kwargs):
        raise EmbeddingQuotaExhausted("Aborting: 5 consecutive HTTP 429 errors. Gemini API quota exhausted — retry later.")

    with (
        patch.object(athena.tools.search, "get_search_cache", return_value=tmp_cache),
        patch("athena.memory.vectors.get_embedding", side_effect=quota_failing_get_embedding),
    ):
        # Call 1: Depleted search
        run_search("test query for quota depletion", json_output=True, limit=2)
        out1 = capsys.readouterr().out
        payload1 = json.loads(out1.strip().splitlines()[-1])
        assert payload1.get("degraded_recall") is True, f"Expected degraded_recall=True, got {payload1.get('degraded_recall')}"
        assert payload1.get("quality") == "degraded", f"Expected quality='degraded', got {payload1.get('quality')}"
        assert "vector" in payload1.get("channels_failed", []), f"Expected 'vector' in channels_failed, got {payload1.get('channels_failed')}"
        assert len(tmp_cache._cache) == 0, f"Expected empty cache, but {len(tmp_cache._cache)} entries were cached!"


def test_cache_invalidates_on_corpus_fingerprint_change(tmp_path, capsys):
    """F-07 regression test: Cache must invalidate when CANONICAL.md is modified."""
    tmp_cache = QueryCache(cache_dir=tmp_path, ttl_hours=24)

    with (
        patch.object(athena.tools.search, "get_search_cache", return_value=tmp_cache),
        patch("athena.tools.search.collect_vectors", return_value=[]),
    ):
        # Query 1: Initial run with current corpus
        with patch.object(athena.tools.search, "CANONICAL_PATH", tmp_path / "CANONICAL.md"):
            canonical_file = tmp_path / "CANONICAL.md"
            canonical_file.write_text("Law #1: No Ruin.")
            os.utime(canonical_file, (1000, 1000))

            run_search("corpus test query", json_output=True, limit=2)
            assert len(tmp_cache._cache) == 1, "Expected 1 cached entry after initial query"

            # Query 2: Identical query with same mtime -> Cache Hit
            run_search("corpus test query", json_output=True, limit=2)
            assert len(tmp_cache._cache) == 1

            # Modify CANONICAL.md mtime (corpus update)
            os.utime(canonical_file, (2000, 2000))

            # Query 3: Identical query with updated mtime -> New scope hash, old cache entry bypassed!
            run_search("corpus test query", json_output=True, limit=2)
            assert len(tmp_cache._cache) == 2, "Expected new cache entry under updated corpus fingerprint"



