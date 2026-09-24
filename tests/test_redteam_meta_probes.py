"""
tests.test_redteam_meta_probes
==============================
Ratcheting CI gate for the meta-reasoning adversarial probe suite.

The RATCHET_FLOOR is the minimum number of probes that must pass.
It may only be raised (never lowered). This converts the red-team
audit from a one-off document into a permanent regression target.

Baseline (pre-fix):  3/20
Post-fix #1-#3:     10/20
"""

import subprocess
import sys
import unittest
from pathlib import Path

# Ratchet: pass count must NEVER decrease below this number.
# Raise it as more fixes land. Never lower it.
RATCHET_FLOOR = 20
TOTAL_PROBES = 20

ROOT = Path(__file__).resolve().parents[1]
PROBE_SCRIPT = ROOT / ".agent" / "eval" / "redteam_meta_probe.py"


class TestRedTeamMetaProbes(unittest.TestCase):
    """Ratcheting gate: the probe suite pass count must never regress."""

    def test_probe_pass_count_meets_ratchet_floor(self):
        """Run the adversarial probe suite and assert the pass count >= RATCHET_FLOOR."""
        result = subprocess.run(
            [sys.executable, str(PROBE_SCRIPT)],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, f"Probe script crashed:\n{result.stderr}")

        # Parse the summary line: "  N/20 probes passed   (M failures)"
        output = result.stdout
        for line in output.splitlines():
            if "probes passed" in line:
                parts = line.strip().split("/")
                passed = int(parts[0])
                break
        else:
            self.fail(f"Could not parse probe output:\n{output}")

        self.assertGreaterEqual(
            passed,
            RATCHET_FLOOR,
            f"RATCHET VIOLATION: {passed}/{TOTAL_PROBES} probes passed, "
            f"floor is {RATCHET_FLOOR}. A fix has regressed.",
        )

        # Report for CI visibility
        print(f"\n  Probe result: {passed}/{TOTAL_PROBES} (ratchet floor: {RATCHET_FLOOR})")


if __name__ == "__main__":
    unittest.main()
