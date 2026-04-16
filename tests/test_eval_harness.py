"""
tests/test_eval_harness.py — Evaluation Harness (EVA)
======================================================

Golden prompt test suite for validating Athena workspace integrity.
Each test verifies a structural invariant or protocol behavior.

This is NOT an LLM eval (no API calls). It tests the local workspace
structure, governance engine, and permission system against known-good
expectations.

Run: pytest tests/test_eval_harness.py -v

Ported from the private repo audit (Apr 2026).
"""

import re
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestStructure:
    """Workspace structural invariants."""

    def test_canonical_exists_with_sections(self):
        """CANONICAL.md exists and contains required sections."""
        canonical = PROJECT_ROOT / ".context" / "CANONICAL.md"
        assert canonical.exists(), "CANONICAL.md not found"

        content = canonical.read_text(encoding="utf-8")
        assert "Canonical Memory" in content
        assert "Last Updated" in content

    def test_protocol_naming_audit(self):
        """All protocol files should have a structured prefix.

        Valid formats:
        - Numeric prefix: 123-name.md
        - Domain prefix:  BUS-123-name.md
        """
        protocols_dir = PROJECT_ROOT / "examples" / "protocols"
        if not protocols_dir.exists():
            pytest.skip("Protocols directory not found")

        all_protocols = list(protocols_dir.rglob("*.md"))
        # Exclude README files
        all_protocols = [p for p in all_protocols if p.name != "README.md"]

        valid_prefix = re.compile(r'^([A-Z]{3}-)?[0-9]')
        no_prefix = [
            p for p in all_protocols
            if not valid_prefix.match(p.name)
        ]

        ratio = len(no_prefix) / len(all_protocols) if all_protocols else 0
        print(
            f"\n  Protocol naming: {len(all_protocols)} total, "
            f"{len(no_prefix)} without structured prefix ({ratio:.0%})"
        )
        assert ratio < 0.15, (
            f"{len(no_prefix)}/{len(all_protocols)} protocols lack structured prefix"
        )

    def test_no_committed_garbage(self):
        """No .DS_Store or log files should exist in the repo."""
        garbage = []
        for pattern in ['.DS_Store', 'athenad.log']:
            garbage.extend(PROJECT_ROOT.rglob(pattern))

        # Exclude .git directory
        garbage = [g for g in garbage if '.git' not in str(g)]
        assert len(garbage) == 0, f"Found committed garbage: {[str(g) for g in garbage]}"

    def test_no_requirements_txt(self):
        """requirements.txt files should not exist — pyproject.toml is truth."""
        req_files = list(PROJECT_ROOT.glob("requirements*.txt"))
        assert len(req_files) == 0, (
            f"Found {len(req_files)} requirements.txt files — "
            f"use pyproject.toml as single dependency source"
        )

    def test_discipline_exists(self):
        """DISCIPLINE.md exists with stop-rules."""
        discipline = PROJECT_ROOT / "docs" / "DISCIPLINE.md"
        assert discipline.exists(), "DISCIPLINE.md not found — add growth stop-rules"

        content = discipline.read_text(encoding="utf-8")
        assert "Stop-Rule" in content or "stop-rule" in content.lower()


class TestSecurity:
    """Security template integrity."""

    def test_rls_migration_exists(self):
        """RLS hardening migration should exist."""
        rls = PROJECT_ROOT / "supabase" / "migrations" / "015_rls_vector_tables.sql"
        assert rls.exists(), "015_rls_vector_tables.sql not found — vector tables are unprotected"

    def test_keychain_script_exists(self):
        """Keychain migration script should exist."""
        keychain = PROJECT_ROOT / "scripts" / "env_keychain.sh"
        assert keychain.exists(), "env_keychain.sh not found — users have no secure key storage template"

    def test_env_example_no_real_keys(self):
        """.env.example should contain only placeholder values."""
        env_example = PROJECT_ROOT / ".env.example"
        if not env_example.exists():
            pytest.skip(".env.example not found")

        content = env_example.read_text()
        # Should not contain real-looking keys
        assert "sk-" not in content, "Real OpenAI key pattern found in .env.example"
        assert "eyJ" not in content, "Real JWT pattern found in .env.example"
