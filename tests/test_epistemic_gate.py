"""
tests.test_epistemic_gate
=========================
Regression and unit tests for the Epistemic Grounding Gate (TD-070).
Verifies:
1. Universal-negative claims are detected accurately.
2. Benign conversational negatives do NOT trigger false positives.
3. Ungrounded universal negatives are blocked (exit 2 / returns False).
4. Grounded universal negatives or calibrated statements are allowed (exit 0 / returns True).
5. Red Run: Demonstrates pre-fix failure (exit 2) and post-fix pass.
"""

import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[1]
GATE_SCRIPT = REPO_ROOT / ".agent" / "scripts" / "hook_epistemic_gate.py"

from athena.mcp_server import context_gate, search_web


class TestEpistemicGate(unittest.TestCase):
    def setUp(self):
        from athena.core.permissions import get_permissions
        self.perms = get_permissions()
        self.original_secret = self.perms.secret_mode
        self.perms.secret_mode = False

    def tearDown(self):
        self.perms.secret_mode = self.original_secret

    def test_detect_universal_negative_claims(self):
        """Universal-negative claim patterns must be detected."""
        sys.path.insert(0, str(REPO_ROOT / ".agent" / "scripts"))
        from hook_epistemic_gate import detect_negative_claims

        # Target incident pattern
        claims = [
            "Garmin has never made a Forerunner 570.",
            "Garmin never produced this watch model.",
            "The model does not exist anywhere.",
            "There is no such product in their line.",
            "That is not a real watch.",
            "Such a device never existed.",
        ]
        for c in claims:
            matches = detect_negative_claims(c)
            self.assertTrue(len(matches) > 0, f"Failed to detect negative claim in: {c}")

    def test_benign_exceptions_not_detected(self):
        """Benign conversational idioms must not trigger false positives."""
        sys.path.insert(0, str(REPO_ROOT / ".agent" / "scripts"))
        from hook_epistemic_gate import detect_negative_claims

        benign = [
            "There is no need to panic about this issue.",
            "There is no doubt that training is progressing well.",
            "There is no problem with the workout schedule.",
            "The directory does not exist yet.",
            "The file does not exist in the root folder.",
        ]
        for b in benign:
            matches = detect_negative_claims(b)
            self.assertEqual(len(matches), 0, f"False positive triggered for: {b}")

    def test_ungrounded_claim_blocked(self):
        """Ungrounded negative claim returns False with error message."""
        sys.path.insert(0, str(REPO_ROOT / ".agent" / "scripts"))
        from hook_epistemic_gate import verify_text

        with tempfile.NamedTemporaryFile("w+", delete=False) as tmp:
            tmp.write("")  # empty invocations file
            tmp.flush()
            allowed, errors = verify_text(
                "Garmin has never made a Forerunner 570.",
                force_grounded=False,
                invocations_path=Path(tmp.name),
            )
            self.assertFalse(allowed)
            self.assertTrue(len(errors) > 0)
            self.assertIn("Universal-negative claim detected", errors[0])

    def test_grounded_claim_allowed(self):
        """Grounded claim with recent successful web search is allowed."""
        sys.path.insert(0, str(REPO_ROOT / ".agent" / "scripts"))
        from hook_epistemic_gate import verify_text

        with tempfile.NamedTemporaryFile("w+", delete=False) as tmp:
            entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "type": "web_search",
                "grounding_status": "ok",
                "query": "Garmin Forerunner 570",
            }
            tmp.write(json.dumps(entry) + "\n")
            tmp.flush()
            allowed, errors = verify_text(
                "Garmin has never made a Forerunner 570.",
                force_grounded=False,
                invocations_path=Path(tmp.name),
            )
            self.assertTrue(allowed)
            self.assertEqual(len(errors), 0)

    def test_failed_tool_search_does_not_count_as_grounding(self):
        """A tool_error web search does NOT permit a universal-negative claim."""
        sys.path.insert(0, str(REPO_ROOT / ".agent" / "scripts"))
        from hook_epistemic_gate import verify_text

        with tempfile.NamedTemporaryFile("w+", delete=False) as tmp:
            entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "type": "web_search",
                "grounding_status": "tool_error",
                "query": "Garmin Forerunner 570",
            }
            tmp.write(json.dumps(entry) + "\n")
            tmp.flush()
            allowed, errors = verify_text(
                "Garmin has never made a Forerunner 570.",
                force_grounded=False,
                invocations_path=Path(tmp.name),
            )
            self.assertFalse(allowed)
            self.assertTrue(len(errors) > 0)

    def test_red_run_cli_blocks_and_passes(self):
        """Red Run demonstration:
        1. Ungrounded negative claim exits with code 2 (RED).
        2. Force-grounded claim exits with code 0 (GREEN).
        """
        with tempfile.NamedTemporaryFile("w+", delete=False) as tmp:
            tmp.write("")
            tmp.flush()

            # 1. Pre-fix / Ungrounded state -> RED (exit 2)
            cmd_red = [
                sys.executable,
                str(GATE_SCRIPT),
                "--text",
                "Garmin has never made a Forerunner 570.",
                "--invocations-file",
                tmp.name,
            ]
            res_red = subprocess.run(cmd_red, capture_output=True, text=True)
            self.assertEqual(res_red.returncode, 2, "Ungrounded negative claim must exit with code 2")
            self.assertIn("Output Verifier Blocked Completion", res_red.stderr)

            # 2. Fixed / Grounded state -> GREEN (exit 0)
            cmd_green = [
                sys.executable,
                str(GATE_SCRIPT),
                "--text",
                "Garmin has never made a Forerunner 570.",
                "--force-grounded",
            ]
            res_green = subprocess.run(cmd_green, capture_output=True, text=True)
            self.assertEqual(res_green.returncode, 0, "Grounded claim must exit with code 0")

    def test_mcp_search_web_tool(self):
        """mcp_server.search_web must be callable, gated, and return grounding_status."""
        with patch("athena.tools.web_providers.web_search") as mock_ws:
            from athena.tools.web_providers import WebResult
            mock_ws.return_value = (
                [WebResult("Title", "Snippet", "https://example.com", "2026-09-12T00:00:00Z", "serper", 0)],
                {"provider": "serper", "degraded": False, "grounding_status": "ok", "errors": []},
            )
            res = search_web("test query", limit=1)
            self.assertEqual(res["grounding_status"], "ok")
            self.assertEqual(len(res["results"]), 1)
            self.assertEqual(res["results"][0]["title"], "Title")

    def test_mcp_context_gate_includes_epistemic_directive(self):
        """mcp_server.context_gate must include epistemic gate directive."""
        with patch("athena.tools.search.run_search"):
            res = context_gate("Check Garmin watch", limit=2)
            self.assertIn("EPISTEMIC GATE", res["directive"])
            self.assertIn("grounding_status", res)


if __name__ == "__main__":
    unittest.main()
