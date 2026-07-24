"""
test_governance.py — MC/DC Tests for the Athena Governance Engine
=================================================================
Tests DoomLoopDetector, RiskLevel, and GovernanceEngine with
Modified Condition/Decision Coverage (MC/DC) per DO-178C standard.

MC/DC Requirement: Every boolean sub-condition in a compound decision
must be proven to independently affect the final outcome.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from athena.core.governance import (
    DEFAULT_RISK_LEVEL,
    DoomLoopDetector,
    GovernanceEngine,
    RiskLevel,
)

# ─────────────────────────────────────────────────────────────────────
# DoomLoopDetector Tests
# ─────────────────────────────────────────────────────────────────────


class TestDoomLoopDetector(unittest.TestCase):
    """Tests for infinite retry loop detection with deterministic time control."""

    def setUp(self):
        self.detector = DoomLoopDetector(threshold=3, window=60)

    def test_no_doom_loop_below_threshold(self):
        """Two identical calls should NOT trigger detection (threshold=3)."""
        self.assertFalse(self.detector.record("search", {"q": "test"}))
        self.assertFalse(self.detector.record("search", {"q": "test"}))

    def test_doom_loop_at_threshold(self):
        """Third identical call should trigger detection (threshold=3)."""
        self.detector.record("search", {"q": "test"})
        self.detector.record("search", {"q": "test"})
        self.assertTrue(self.detector.record("search", {"q": "test"}))

    def test_different_args_no_doom_loop(self):
        """Same tool but different args should NOT trigger detection."""
        self.detector.record("search", {"q": "query1"})
        self.detector.record("search", {"q": "query2"})
        self.assertFalse(self.detector.record("search", {"q": "query3"}))

    def test_different_tools_no_doom_loop(self):
        """Different tools with same args should NOT trigger detection."""
        self.detector.record("search", {"q": "test"})
        self.detector.record("web_search", {"q": "test"})
        self.assertFalse(self.detector.record("quicksave", {"q": "test"}))

    @patch("athena.core.governance.time")
    def test_window_expiry_clears_history(self, mock_time):
        """Calls outside the time window should be pruned and not count."""
        # Time 0: two calls
        mock_time.time.return_value = 1000.0
        self.detector.record("search", {"q": "test"})
        self.detector.record("search", {"q": "test"})

        # Time 61: outside the 60s window — history pruned
        mock_time.time.return_value = 1061.0
        # This is now the 1st call in the window, should NOT trigger
        self.assertFalse(self.detector.record("search", {"q": "test"}))

    @patch("athena.core.governance.time")
    def test_window_within_bounds_still_detects(self, mock_time):
        """Calls within the time window should still be counted."""
        mock_time.time.return_value = 1000.0
        self.detector.record("search", {"q": "test"})

        mock_time.time.return_value = 1030.0
        self.detector.record("search", {"q": "test"})

        mock_time.time.return_value = 1059.0  # Still within 60s window
        self.assertTrue(self.detector.record("search", {"q": "test"}))

    def test_reset_clears_all_state(self):
        """reset() should clear history so subsequent calls don't trigger."""
        self.detector.record("search", {"q": "test"})
        self.detector.record("search", {"q": "test"})
        self.detector.reset()
        # After reset, this should be the "first" call
        self.assertFalse(self.detector.record("search", {"q": "test"}))

    def test_get_stats_tracks_violations(self):
        """Violations counter should increment on each doom loop detection."""
        # Trigger one violation
        self.detector.record("search", {"q": "test"})
        self.detector.record("search", {"q": "test"})
        self.detector.record("search", {"q": "test"})  # Violation #1

        stats = self.detector.get_stats()
        self.assertEqual(stats["total_violations"], 1)
        self.assertEqual(stats["threshold"], 3)
        self.assertEqual(stats["window_seconds"], 60)

    def test_none_args_handled(self):
        """None args should hash consistently and detect loops."""
        self.detector.record("tool", None)
        self.detector.record("tool", None)
        self.assertTrue(self.detector.record("tool", None))

    def test_complex_args_deterministic_hash(self):
        """Complex nested args should produce consistent hashes."""
        args = {"nested": {"key": [1, 2, 3]}, "flag": True}
        self.detector.record("tool", args)
        self.detector.record("tool", args)
        self.assertTrue(self.detector.record("tool", args))


# ─────────────────────────────────────────────────────────────────────
# GovernanceEngine MC/DC Tests — verify_exchange_integrity
# ─────────────────────────────────────────────────────────────────────


class TestTripleLockMCDC(unittest.TestCase):
    """
    MC/DC (Modified Condition/Decision Coverage) for verify_exchange_integrity.

    The decision is: integrity = semantic AND web
    With SNIPER mode as a bypass.

    MC/DC requires each sub-condition independently affects the result:
    1. semantic=True,  web=False → False (web is the sole cause)
    2. semantic=False, web=True  → False (semantic is the sole cause)
    3. semantic=True,  web=True  → True  (both required)
    4. SNIPER mode              → True  (bypass, regardless of searches)
    """

    def setUp(self):
        import tempfile

        self.tmpdir = tempfile.mkdtemp()
        self.engine = GovernanceEngine(state_dir=Path(self.tmpdir))

    # MC/DC Case 1: web_done alone flips the result
    def test_semantic_only_fails(self):
        """With only semantic search done, integrity fails (web is the sole cause)."""
        self.engine.set_risk_level(RiskLevel.STANDARD)
        self.engine.mark_search_performed("test query")
        # web NOT performed
        result = self.engine.verify_exchange_integrity()
        self.assertFalse(result)

    # MC/DC Case 2: semantic alone flips the result
    def test_web_only_fails(self):
        """With only web search done, integrity fails (semantic is the sole cause)."""
        self.engine.set_risk_level(RiskLevel.STANDARD)
        # semantic NOT performed
        self.engine.mark_web_search_performed("test query")
        result = self.engine.verify_exchange_integrity()
        self.assertFalse(result)

    # MC/DC Case 3: both required
    def test_both_searches_pass(self):
        """With both searches done, integrity passes."""
        self.engine.set_risk_level(RiskLevel.STANDARD)
        self.engine.mark_search_performed("test query")
        self.engine.mark_web_search_performed("test query")
        result = self.engine.verify_exchange_integrity()
        self.assertTrue(result)

    # MC/DC Case 4: SNIPER bypass
    def test_sniper_bypasses_triple_lock(self):
        """SNIPER mode always returns True, regardless of search state."""
        self.engine.set_risk_level(RiskLevel.SNIPER)
        # Neither search performed
        result = self.engine.verify_exchange_integrity()
        self.assertTrue(result)

    def test_neither_search_fails(self):
        """With no searches done at all, integrity fails."""
        self.engine.set_risk_level(RiskLevel.STANDARD)
        result = self.engine.verify_exchange_integrity()
        self.assertFalse(result)

    def test_ultra_requires_both_searches(self):
        """ULTRA mode also requires both searches (same as STANDARD)."""
        self.engine.set_risk_level(RiskLevel.ULTRA)
        self.engine.mark_search_performed("strategy query")
        # web NOT performed
        result = self.engine.verify_exchange_integrity()
        self.assertFalse(result)

    def test_ultra_passes_with_both(self):
        """ULTRA mode passes when both searches are done."""
        self.engine.set_risk_level(RiskLevel.ULTRA)
        self.engine.mark_search_performed("strategy query")
        self.engine.mark_web_search_performed("strategy query")
        result = self.engine.verify_exchange_integrity()
        self.assertTrue(result)


# ─────────────────────────────────────────────────────────────────────
# GovernanceEngine — State Reset and Integrity Score
# ─────────────────────────────────────────────────────────────────────


class TestGovernanceStateReset(unittest.TestCase):
    """Verify that verify_exchange_integrity resets state after each check."""

    def setUp(self):
        import tempfile

        self.tmpdir = tempfile.mkdtemp()
        self.engine = GovernanceEngine(state_dir=Path(self.tmpdir))

    def test_state_resets_after_verify(self):
        """After verify, search flags should be reset to False."""
        self.engine.mark_search_performed("q")
        self.engine.mark_web_search_performed("q")
        self.engine.verify_exchange_integrity()

        # Second verify (without new searches) should fail
        result = self.engine.verify_exchange_integrity()
        self.assertFalse(result)

    def test_risk_level_resets_to_default(self):
        """After verify, risk level should reset to DEFAULT_RISK_LEVEL (STANDARD)."""
        self.engine.set_risk_level(RiskLevel.SNIPER)
        self.engine.verify_exchange_integrity()

        # Risk level should have reset
        self.assertEqual(self.engine._risk_level, DEFAULT_RISK_LEVEL)
        self.assertFalse(self.engine.is_sniper_mode())


class TestIntegrityScore(unittest.TestCase):
    """Tests for get_integrity_score — non-destructive read of compliance state."""

    def setUp(self):
        import tempfile

        self.tmpdir = tempfile.mkdtemp()
        self.engine = GovernanceEngine(state_dir=Path(self.tmpdir))

    def test_score_1_when_compliant(self):
        """Score is 1.0 when both searches have been performed."""
        self.engine.mark_search_performed("q")
        self.engine.mark_web_search_performed("q")
        self.assertEqual(self.engine.get_integrity_score(), 1.0)

    def test_score_0_when_noncompliant(self):
        """Score is 0.0 when searches are incomplete."""
        self.engine.mark_search_performed("q")
        # web NOT performed
        self.assertEqual(self.engine.get_integrity_score(), 0.0)

    def test_score_1_for_sniper(self):
        """Score is 1.0 in SNIPER mode regardless of search state."""
        self.engine.set_risk_level(RiskLevel.SNIPER)
        self.assertEqual(self.engine.get_integrity_score(), 1.0)


class TestGovernanceDoomLoopIntegration(unittest.TestCase):
    """Integration: GovernanceEngine.record_tool_call delegates to DoomLoopDetector."""

    def setUp(self):
        import tempfile

        self.tmpdir = tempfile.mkdtemp()
        self.engine = GovernanceEngine(state_dir=Path(self.tmpdir))

    def test_tool_call_delegation(self):
        """record_tool_call should detect doom loops via the internal detector."""
        self.assertFalse(self.engine.record_tool_call("search", {"q": "test"}))
        self.assertFalse(self.engine.record_tool_call("search", {"q": "test"}))
        self.assertTrue(self.engine.record_tool_call("search", {"q": "test"}))

    def test_doom_loop_stats_in_status(self):
        """get_status should include doom loop statistics."""
        # Trigger a violation
        self.engine.record_tool_call("search", {"q": "x"})
        self.engine.record_tool_call("search", {"q": "x"})
        self.engine.record_tool_call("search", {"q": "x"})

        status = self.engine.get_status()
        self.assertIn("doom_loop", status)
        self.assertEqual(status["doom_loop"]["total_violations"], 1)


if __name__ == "__main__":
    unittest.main()
