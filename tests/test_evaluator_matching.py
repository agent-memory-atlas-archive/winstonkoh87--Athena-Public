"""
tests/test_evaluator_matching.py
================================
Unit tests verifying strict matching in evaluator.py (Audit F-03 remediation).
Guarantees:
1. Rejection of loose substring / class-token false positives (e.g. 'session_logs' matching any session log).
2. Proper exact-name and stem matching for files, case studies, protocols, and skills.
3. Negative control rejection of fabricated sources.
"""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / ".agent" / "scripts"))

from evaluator import compute_reciprocal_rank


class TestEvaluatorStrictMatching(unittest.TestCase):
    def test_class_token_rejection(self):
        # Result is a specific session log
        result = {
            "id": "Session 2026-02-09: 2026-02-09-session-01.md (Chunk 1)",
            "path": ".context/memories/session_logs/2026-02-09-session-01.md",
            "source": "session",
        }
        # Generic class token MUST NOT match
        rr = compute_reciprocal_rank([result], ["session_logs"])
        self.assertEqual(rr, 0.0)

    def test_exact_filename_and_stem_match(self):
        result = {
            "id": "Session 2026-02-09: 2026-02-09-session-01.md (Chunk 1)",
            "path": ".context/memories/session_logs/2026-02-09-session-01.md",
            "source": "session",
        }
        # Exact filename
        rr_full = compute_reciprocal_rank([result], ["2026-02-09-session-01.md"])
        self.assertEqual(rr_full, 1.0)

        # Exact stem
        rr_stem = compute_reciprocal_rank([result], ["2026-02-09-session-01"])
        self.assertEqual(rr_stem, 1.0)

    def test_skill_package_matching(self):
        result = {
            "id": "bionic-safety-net",
            "path": ".agent/skills/bionic-safety-net/SKILL.md",
            "source": "skill",
        }
        # Skill directory name matches
        rr = compute_reciprocal_rank([result], ["bionic-safety-net"])
        self.assertEqual(rr, 1.0)

        # Generic parent directory token 'skills' MUST NOT match
        rr_generic = compute_reciprocal_rank([result], ["skills"])
        self.assertEqual(rr_generic, 0.0)

    def test_negative_control_fabricated_source(self):
        result = {
            "id": "Protocol 75: 75-synthetic-parallel-reasoning",
            "path": ".agent/skills/protocols/decision/75-synthetic-parallel-reasoning.md",
            "source": "protocol",
        }
        rr_fake = compute_reciprocal_rank([result], ["fabricated_hallucinated_file.md"])
        self.assertEqual(rr_fake, 0.0)


if __name__ == "__main__":
    unittest.main()
