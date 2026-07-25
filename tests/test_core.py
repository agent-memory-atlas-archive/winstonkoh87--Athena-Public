#!/usr/bin/env python3
"""
test_core.py
============
Pytest tests for athena.core modules.
Covers: config, cache, governance - the critical foundation.

Run: pytest tests/test_core.py -v
"""

from pathlib import Path


class TestConfigModule:
    """Tests for athena.core.config path discovery."""

    def test_project_root_exists(self):
        """PROJECT_ROOT should point to a valid directory."""
        from athena.core.config import PROJECT_ROOT

        assert PROJECT_ROOT.exists(), "PROJECT_ROOT not found"
        assert (PROJECT_ROOT / "pyproject.toml").exists(), "Missing pyproject.toml"

    def test_agent_dir_exists(self):
        """AGENT_DIR should exist."""
        from athena.core.config import AGENT_DIR

        assert AGENT_DIR.exists(), ".agent directory not found"

    def test_sessions_dir_matches_distribution(self):
        """Session logs must be present privately and absent publicly.

        This was a hard assertion, then became two unconditional pytest.skip
        calls — which meant it could no longer fail anywhere, including in the
        private workspace where a broken SESSIONS_DIR is a real defect. Both
        branches now assert.
        """
        from athena.core.config import PROJECT_ROOT, SESSIONS_DIR

        # The privacy blocklist ships only with the public distribution — it
        # exists to guard the public boundary, so the private workspace has no
        # copy. That makes it a reliable distribution marker.
        is_public = (PROJECT_ROOT / ".github" / "privacy_blocklist.txt").exists()
        md_files = list(SESSIONS_DIR.glob("*.md")) if SESSIONS_DIR.exists() else []

        if is_public:
            assert not md_files, (
                f"public distribution is shipping {len(md_files)} session log(s) "
                f"from {SESSIONS_DIR} — these are private by policy"
            )
            return

        assert SESSIONS_DIR.exists(), "Session logs directory not found"
        assert md_files, "No session logs found"

    def test_core_dirs_mapping(self):
        """CORE_DIRS should have valid path mappings."""
        from athena.core.config import CORE_DIRS

        assert "sessions" in CORE_DIRS
        assert "protocols" in CORE_DIRS
        assert isinstance(CORE_DIRS["sessions"], Path)


class TestGovernanceModule:
    """Tests for athena.core.governance compliance tracking."""

    def test_governance_import(self):
        """Governance module should import without errors."""
        from athena.core import governance

        assert hasattr(governance, "__file__")


class TestCacheModule:
    """Tests for athena.core.cache semantic caching."""

    def test_cache_import(self):
        """Cache module should import without errors."""
        from athena.core import cache

        assert hasattr(cache, "__file__")


class TestVectorsModule:
    """Tests for athena.memory.vectors embedding functions."""

    def test_embedding_model_constant(self):
        """Embedding model should be gemini-embedding-001 (3072 dims)."""
        # Read the source to verify model
        import inspect

        from athena.memory import vectors

        source = inspect.getsource(vectors.get_embedding)
        assert "gemini-embedding-001" in source, "Expected gemini-embedding-001 model"

    def test_search_wrappers_exist(self):
        """All 12 search wrappers should be defined."""
        from athena.memory import vectors

        required = [
            "search_sessions",
            "search_case_studies",
            "search_protocols",
            "search_capabilities",
            "search_playbooks",
            "search_references",
            "search_frameworks",
            "search_workflows",
            "search_system_docs",
            "search_user_profile",
            "search_entities",
            "search_insights",
        ]
        for func_name in required:
            assert hasattr(vectors, func_name), f"Missing search wrapper: {func_name}"


class TestSecurityModule:
    """Tests for athena.core.security (CVE-2025-69872 diskcache hardening)."""

    def test_imports_without_dspy(self):
        """The module must import even though dspy is not a dependency.

        Regression: the old module hard-imported dspy at top level, so any
        import of athena.core.security crashed with ModuleNotFoundError.
        """
        import athena.core.security as sec

        assert callable(sec.apply_diskcache_hardening)
        # Back-compat alias retained for older callers.
        assert callable(sec.patch_dspy_cache_security)

    def test_hardening_returns_summary_and_never_raises(self):
        """apply_diskcache_hardening returns a summary dict without raising."""
        from athena.core.security import apply_diskcache_hardening

        summary = apply_diskcache_hardening()
        assert isinstance(summary, dict)
        assert "dirs_hardened" in summary
        assert isinstance(summary["dirs_hardened"], list)
        assert "dspy_patched" in summary

    def test_harden_dir_sets_0700(self, tmp_path):
        """_harden_dir restricts a real directory to owner-only (0700)."""
        import stat

        from athena.core.security import _harden_dir

        target = tmp_path / "cache"
        target.mkdir()
        target.chmod(0o755)

        assert _harden_dir(target) is True
        mode = stat.S_IMODE(target.stat().st_mode)
        assert mode == 0o700
        # Non-existent directory is a no-op, not an error.
        assert _harden_dir(tmp_path / "missing") is False


class TestIntegration:
    """Integration tests for cross-module functionality."""

    def test_config_import_chain(self):
        """Config should be importable from vectors via SDK path."""
        from athena.memory.vectors import get_embedding

        assert callable(get_embedding)
