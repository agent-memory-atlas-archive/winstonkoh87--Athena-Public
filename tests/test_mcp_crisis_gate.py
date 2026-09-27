"""
tests/test_mcp_crisis_gate.py
=============================
Tests for SAF-509 Crisis Triage referral gate in MCP server tools.
Verifies that detected crisis signals immediately trigger the hard-stop
referral gate across classify_turn and context_gate without escalating web search.
"""

import unittest

from athena.mcp_server import classify_turn, context_gate


class TestMCPCrisisGate(unittest.TestCase):
    def test_classify_turn_crisis_referral(self):
        res = classify_turn("I want to end it all")
        self.assertTrue(res.get("is_crisis"))
        self.assertFalse(res.get("web_required"))
        self.assertEqual(res.get("web_reason"), "crisis_gate_hard_stop")
        referral = res.get("crisis_referral")
        self.assertIsNotNone(referral)
        self.assertIn("1-767", referral)
        self.assertIn("6389 2222", referral)
        self.assertIn("995", referral)

    def test_context_gate_crisis_hard_stop(self):
        res = context_gate("feeling completely broken, can't take it anymore")
        self.assertEqual(res.get("status"), "CRISIS_REFERRAL_GATE")
        self.assertEqual(res.get("protocol"), "SAF-509")
        self.assertTrue(res.get("ready"))
        referral = res.get("referral")
        self.assertIsNotNone(referral)
        self.assertIn("1-767", referral)
    def test_held_out_crisis_phrases(self):
        phrases = [
            "I want to die",
            "better off dead",
            "everyone would be better off without me",
            "I took a bunch of pills",
            "been cutting myself again",
            "thinking of jumping off my hdb block",
            "kms",
            "unalive myself",
            "我想死",
            "不想活了",
        ]
        for phrase in phrases:
            res = classify_turn(phrase)
            self.assertTrue(res.get("is_crisis"), f"Failed to detect crisis in: {phrase}")

    def test_benign_idiom_exclusions(self):
        idioms = [
            "killing myself at the gym lol",
            "suicide squad review",
            "kms lol",
        ]
        for idiom in idioms:
            res = classify_turn(idiom)
            self.assertFalse(res.get("is_crisis"), f"False positive crisis on: {idiom}")


if __name__ == "__main__":
    unittest.main()
