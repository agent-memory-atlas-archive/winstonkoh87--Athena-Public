"""
Unit tests for .agent/scripts/verify_canon_citations.py (T3.1).
Ensures title matching, proximity check, and section ref filtering.
"""

import sys
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
AGENT_SCRIPTS_DIR = Path(__file__).resolve().parent.parent / ".agent" / "scripts"
for d in (SCRIPTS_DIR, AGENT_SCRIPTS_DIR):
    if d.exists() and str(d) not in sys.path:
        sys.path.insert(0, str(d))

from verify_canon_citations import (
    check_text_citations,
    extract_distinctive_words,
    is_canonical_citation,
)


class TestVerifyCanonCitations(unittest.TestCase):
    def test_extract_distinctive_words(self):
        title = 'The Ousen Protocol & The "Thank You" Armor (Mature Institutional Statecraft)'
        words = extract_distinctive_words(title)
        self.assertIn("ousen", words)
        self.assertIn("thank", words)
        self.assertIn("armor", words)
        self.assertIn("institutional", words)
        self.assertNotIn("protocol", words)
        self.assertNotIn("the", words)

    def test_is_canonical_citation_proximity_and_links(self):
        # M11: Proximity check keeps CANONICAL citations and rejects non-CANONICAL ones
        line_canonical_link = "[`CANONICAL.md` §419](file:///.context/CANONICAL.md#L419)"
        self.assertTrue(is_canonical_citation(line_canonical_link, line_canonical_link.index("§419"), line_canonical_link.index("§419") + 4))

        line_cs_link = "[CS-680 §4](file:///.context/memories/case_studies/CS-680.md#L98)"
        self.assertFalse(is_canonical_citation(line_cs_link, line_cs_link.index("§4"), line_cs_link.index("§4") + 2))

        line_plain_near = "As noted in CANONICAL §419, this holds."
        self.assertTrue(is_canonical_citation(line_plain_near, line_plain_near.index("§419"), line_plain_near.index("§419") + 4))

        line_plain_far = "See DEC-500 §4D for details on defection."
        self.assertFalse(is_canonical_citation(line_plain_far, line_plain_far.index("§4"), line_plain_far.index("§4") + 2))

    def test_probe_a2_excerpt_findings(self):
        excerpt = (
            "3. **Strict Liability Over Mens Rea ([`CANONICAL.md` §434](file:///.context/CANONICAL.md); S1225)**: "
            "Never litigate unobservable internal intentions (Mens Rea). Athena weights stated claims at **5%** "
            "and observable scoreboard physics at **95%**.\n"
            "1. **The Narrow Waist Invariant & The Off-Equilibrium Trap ([`CANONICAL.md` §419](file:///.context/CANONICAL.md#L419) "
            "/ [CS-680 §4](file:///.context/memories/case_studies/CS-680.md#L98-L130))\n"
        )
        mock_canonical_lines = [""] * 435
        mock_canonical_lines[419] = "| **The Narrow Waist Invariant & The Off-Equilibrium Trap** | Details | (S1207) |"
        mock_canonical_lines[434] = '| **The Ousen Protocol & The "Thank You" Armor (Mature Institutional Statecraft)** | Details | (S1216) |'
        findings = check_text_citations(excerpt, canonical_lines=mock_canonical_lines, filename="ag_excerpt.md")
        # Expect exactly 2 reported citations: §434 and §419 (CS-680 §4 must NOT be reported)
        self.assertEqual(len(findings), 2)

        # §434 must be MISMATCH (kills M10)
        f434 = next(f for f in findings if f["cited_line"] == 434)
        self.assertEqual(f434["status"], "MISMATCH")
        self.assertIn("citing line does not match title", f434["message"])

        # §419 must be VALID
        f419 = next(f for f in findings if f["cited_line"] == 419)
        self.assertEqual(f419["status"], "VALID")

        # §4 must not be in findings (kills M11)
        self.assertFalse(any(f["cited_line"] == 4 for f in findings))


if __name__ == "__main__":
    unittest.main()
