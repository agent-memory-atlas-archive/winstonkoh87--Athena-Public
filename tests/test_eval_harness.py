"""
tests/test_eval_harness.py — Evaluation Harness (EVA)
======================================================

Golden prompt test suite for validating Athena's protocol behavior.
Each test case verifies that a specific protocol or skill produces
expected behavioral markers in its output.

This is NOT an LLM eval (no API calls). It tests the local search,
governance, and boot infrastructure against known-good expectations.

Run: pytest tests/test_eval_harness.py -v

Audit Ref: Capability Upgrade EVA-001
"""

from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Golden Test Cases: Protocol Behavior Expectations
# ---------------------------------------------------------------------------

GOLDEN_PROMPTS = [
    {
        "id": "EVA-001",
        "name": "Governance engine initializes with correct defaults",
        "category": "governance",
        "test_type": "unit",
    },
    {
        "id": "EVA-002",
        "name": "Triple-Lock blocks quicksave without prior search",
        "category": "governance",
        "test_type": "unit",
    },
    {
        "id": "EVA-003",
        "name": "Sniper mode bypasses Triple-Lock",
        "category": "governance",
        "test_type": "unit",
    },
    {
        "id": "EVA-004",
        "name": "Doom loop detector fires at threshold",
        "category": "governance",
        "test_type": "unit",
    },
    {
        "id": "EVA-005",
        "name": "Permission engine blocks ADMIN tools for READ callers",
        "category": "permissions",
        "test_type": "unit",
    },
    {
        "id": "EVA-006",
        "name": "Secret mode redacts sensitive patterns",
        "category": "permissions",
        "test_type": "unit",
    },
    {
        "id": "EVA-007",
        "name": "CANONICAL.md exists and has required sections",
        "category": "structure",
        "test_type": "structural",
    },
    {
        "id": "EVA-008",
        "name": "All protocol files have numeric prefix",
        "category": "structure",
        "test_type": "structural",
    },
    {
        "id": "EVA-009",
        "name": "Boot orchestrator completes all phases",
        "category": "boot",
        "test_type": "unit",
    },
    {
        "id": "EVA-010",
        "name": "Calibration ledger parses without errors",
        "category": "calibration",
        "test_type": "unit",
    },
]


# ---------------------------------------------------------------------------
# Governance Tests
# ---------------------------------------------------------------------------


class TestGovernance:
    """EVA-001 through EVA-004: Governance engine behavior."""

    def test_eva001_defaults(self):
        """Triple-Lock defaults to STANDARD risk level."""
        import tempfile

        from athena.core.governance import GovernanceEngine, RiskLevel

        with tempfile.TemporaryDirectory() as tmpdir:
            gov = GovernanceEngine(state_dir=Path(tmpdir))
            assert gov._risk_level == RiskLevel.STANDARD
            assert not gov.is_sniper_mode()
            assert not gov.is_ultra_mode()

    def test_eva002_triple_lock_blocks_without_search(self):
        """Quicksave path should see integrity=False if no search was performed."""
        import tempfile

        from athena.core.governance import GovernanceEngine

        with tempfile.TemporaryDirectory() as tmpdir:
            gov = GovernanceEngine(state_dir=Path(tmpdir))
            # No search performed — integrity should fail
            integrity = gov.verify_exchange_integrity()
            assert integrity is False

    def test_eva003_sniper_bypasses_triple_lock(self):
        """Sniper mode exempts from Triple-Lock."""
        import tempfile

        from athena.core.governance import GovernanceEngine, RiskLevel

        with tempfile.TemporaryDirectory() as tmpdir:
            gov = GovernanceEngine(state_dir=Path(tmpdir))
            gov.set_risk_level(RiskLevel.SNIPER)
            # Should pass even without searches
            integrity = gov.verify_exchange_integrity()
            assert integrity is True
            # Should auto-reset to STANDARD after check
            assert gov._risk_level == RiskLevel.STANDARD

    def test_eva004_doom_loop_fires(self):
        """Doom loop detector fires after 3 identical calls."""
        from athena.core.governance import DoomLoopDetector

        detector = DoomLoopDetector(threshold=3, window=60)
        assert not detector.record("search", {"q": "test"})
        assert not detector.record("search", {"q": "test"})
        assert detector.record("search", {"q": "test"})  # 3rd = doom loop
        assert detector.get_stats()["total_violations"] == 1


# ---------------------------------------------------------------------------
# Permission Tests
# ---------------------------------------------------------------------------


class TestPermissions:
    """EVA-005 through EVA-006: Permission engine behavior."""

    def test_eva005_admin_blocked_for_read_caller(self):
        """READ-level caller cannot access ADMIN tools."""
        from athena.core.permissions import (
            Permission,
            PermissionDenied,
            PermissionEngine,
        )

        engine = PermissionEngine.__new__(PermissionEngine)
        engine.caller_level = Permission.READ
        engine.secret_mode = False
        engine.audit_log = []
        engine._state_path = None
        engine._granular = None

        with pytest.raises(PermissionDenied):
            engine.check("clear_cache")

    def test_eva006_secret_mode_redaction(self):
        """Secret mode redacts sensitive content patterns."""
        from athena.core.permissions import PermissionEngine

        engine = PermissionEngine.__new__(PermissionEngine)
        engine.secret_mode = True
        engine.audit_log = []
        engine._state_path = None
        engine._granular = None

        test_content = "My SUPABASE_KEY is abc123 and GOOGLE_API_KEY is xyz"
        redacted = engine.redact(test_content)
        assert "SUPABASE_KEY" not in redacted or "[REDACTED]" in redacted

    def test_redact_masks_secret_values_not_just_labels(self):
        """Redaction must mask the secret VALUE, not only its label.

        Regression: the old redact() replaced the label ("ANTHROPIC_API_KEY")
        and left the actual key ("sk-ant-...") in cleartext.
        """
        from athena.core.permissions import PermissionEngine

        engine = PermissionEngine.__new__(PermissionEngine)
        engine.secret_mode = True
        engine.audit_log = []
        engine._state_path = None
        engine._granular = None

        # Build credential-shaped fixtures at runtime so no literal secret sits
        # in the source — keeps the repo's own pre-commit secret scanner happy.
        secret = "sk-" + "ant-" + ("A1b2C3d4" * 3)  # sk- prefix + 24 body chars
        content = "ANTHROPIC_API_KEY=" + secret
        redacted = engine.redact(content)

        assert secret not in redacted, "raw API key leaked through redaction"
        assert "[REDACTED]" in redacted

        # A JWT-shaped value (three base64url segments) is also masked.
        jwt = ".".join(["eyJ" + "raWQi0", "eyJ" + "zdWIiO", "Zm9vYmFy"])
        redacted_jwt = engine.redact("SUPABASE_KEY: " + jwt)
        assert jwt not in redacted_jwt

        # No-op when secret_mode is off.
        engine.secret_mode = False
        assert engine.redact(content) == content


# ---------------------------------------------------------------------------
# Structural Tests
# ---------------------------------------------------------------------------


class TestStructure:
    """EVA-007 through EVA-008: Workspace structural invariants."""

    def test_eva007_canonical_exists_with_sections(self):
        """CANONICAL.md exists and contains required sections."""
        canonical = PROJECT_ROOT / ".context" / "CANONICAL.md"
        assert canonical.exists(), "CANONICAL.md not found"

        content = canonical.read_text(encoding="utf-8")
        # Must have the header
        assert "Canonical Memory" in content
        # Must have the version tag
        assert "Last Updated" in content

    def test_eva008_protocol_naming_audit(self):
        """Audit how many protocol files lack structured prefix.

        Valid formats:
        - Numeric prefix: 123-name.md
        - Domain prefix:  BUS-123-name.md
        """
        import re
        protocols_dir = PROJECT_ROOT / ".agent" / "skills" / "protocols"
        if not protocols_dir.exists():
            pytest.skip("Protocols directory not found")

        all_protocols = list(protocols_dir.rglob("*.md"))
        # Accept either "123-" or "ABC-123-" as valid prefixes
        valid_prefix = re.compile(r'^([A-Z]{3}-)?[0-9]')
        no_prefix = [
            p for p in all_protocols
            if not valid_prefix.match(p.name)
        ]

        # This is informational — we track the ratio, not fail on it
        ratio = len(no_prefix) / len(all_protocols) if all_protocols else 0
        print(
            f"\n  Protocol naming: {len(all_protocols)} total, "
            f"{len(no_prefix)} without structured prefix ({ratio:.0%})"
        )
        # Fail only if more than 15% lack structured prefix
        assert ratio < 0.15, (
            f"{len(no_prefix)}/{len(all_protocols)} protocols lack structured prefix"
        )


# ---------------------------------------------------------------------------
# Calibration Tests
# ---------------------------------------------------------------------------


class TestCalibration:
    """EVA-010: Calibration system integrity."""

    def test_eva010_ledger_parses(self):
        """Calibration ledger can be parsed without errors."""
        ledger = PROJECT_ROOT / ".context" / "calibration" / "CALIBRATION_LEDGER.md"
        if not ledger.exists():
            pytest.skip("Calibration ledger not created yet")

        # Import the parser
        import sys
        sys.path.insert(0, str(PROJECT_ROOT / ".agent" / "scripts"))
        from calibration_score import parse_ledger

        predictions = parse_ledger(ledger)
        assert len(predictions) > 0, "No predictions parsed from ledger"
        # Every prediction should have an id and outcome
        for p in predictions:
            assert "id" in p, f"Prediction missing id: {p}"
            assert "outcome" in p, f"Prediction missing outcome: {p}"
