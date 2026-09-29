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
