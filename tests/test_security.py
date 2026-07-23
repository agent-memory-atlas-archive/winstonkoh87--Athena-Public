#!/usr/bin/env python3
"""
test_security.py
================
Regression tests for the CVE-2025-69872 diskcache hardening and the
demo-mode secret redaction fix.

Run: pytest tests/test_security.py -v
"""

import stat


class TestSecurityModule:
    """athena.core.security — CVE-2025-69872 diskcache hardening."""

    def test_imports_without_dspy(self):
        """The module must import even though dspy is not a dependency.

        Regression: the old module hard-imported dspy at top level, so any
        import of athena.core.security crashed with ModuleNotFoundError and the
        CVE mitigation never ran.
        """
        import athena.core.security as sec

        assert callable(sec.apply_diskcache_hardening)
        assert callable(sec.patch_dspy_cache_security)  # back-compat alias

    def test_hardening_returns_summary_and_never_raises(self):
        from athena.core.security import apply_diskcache_hardening

        summary = apply_diskcache_hardening()
        assert isinstance(summary, dict)
        assert isinstance(summary.get("dirs_hardened"), list)
        assert "dspy_patched" in summary

    def test_harden_dir_sets_0700(self, tmp_path):
        from athena.core.security import _harden_dir

        target = tmp_path / "cache"
        target.mkdir()
        target.chmod(0o755)

        assert _harden_dir(target) is True
        assert stat.S_IMODE(target.stat().st_mode) == 0o700
        assert _harden_dir(tmp_path / "missing") is False


class TestRedaction:
    """athena.core.permissions.redact — mask VALUES, not just labels."""

    def _engine(self):
        from athena.core.permissions import PermissionEngine

        engine = PermissionEngine.__new__(PermissionEngine)
        engine.demo_mode = True
        engine.audit_log = []
        engine._state_path = None
        engine._granular = None
        return engine

    def test_redact_masks_secret_values(self):
        """Regression: old redact() left the actual key in cleartext, masking
        only its label (``[REDACTED]=sk-...``)."""
        engine = self._engine()

        # Assemble credential-shaped fixtures at runtime so no literal secret
        # sits in source (keeps the privacy gate / secret scanners happy).
        secret = "sk-" + "ant-" + ("A1b2C3d4" * 3)
        out = engine.redact("ANTHROPIC_API_KEY=" + secret)
        assert secret not in out, "raw API key leaked through redaction"
        assert "[REDACTED]" in out

        jwt = ".".join(["eyJ" + "raWQi0", "eyJ" + "zdWIiO", "Zm9vYmFy"])
        out_jwt = engine.redact("SUPABASE_KEY: " + jwt)
        assert jwt not in out_jwt

    def test_redact_noop_when_mode_off(self):
        engine = self._engine()
        engine.demo_mode = False
        content = "ANTHROPIC_API_KEY=" + ("sk-" + "test" + "1234" * 4)
        assert engine.redact(content) == content
