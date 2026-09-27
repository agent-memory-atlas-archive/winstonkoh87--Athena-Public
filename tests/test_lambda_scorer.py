"""
tests.test_lambda_scorer
========================
Unit tests for the Deterministic Lambda Scorer (Phase C1.1).
Verifies:
1. Low-stakes & trivial queries score SNIPER (<10).
2. Medium-complexity queries score STANDARD (10-30).
3. High-stakes financial, legal, ruin, and strategic queries score ULTRA (>30).
4. S777 ruin query correctly triggers ULTRA.
5. Deterministic feature trace output and sub-5ms latency.
"""

import time
import unittest

from athena.core.governance import RiskLevel
from athena.core.lambda_scorer import compute_lambda


class TestLambdaScorer(unittest.TestCase):
    def test_sniper_trivial_greetings(self):
        greetings = ["hi", "hello", "thanks!", "ok", "proceed", "lgtm"]
        for g in greetings:
            res = compute_lambda(g)
            self.assertEqual(res["tier"], "SNIPER")
            self.assertLess(res["score"], 10)
            self.assertEqual(res["risk_level"], RiskLevel.SNIPER)

    def test_sniper_short_system_fact(self):
        res = compute_lambda("what is protocol 501", intent="SYSTEM_KNOWLEDGE")
        self.assertEqual(res["tier"], "SNIPER")
        self.assertLess(res["score"], 10)

    def test_standard_general_queries(self):
        res = compute_lambda("how do I format this markdown table in python")
        self.assertEqual(res["tier"], "STANDARD")
        self.assertTrue(10 <= res["score"] <= 30)

    def test_ultra_s777_ruin_query(self):
        query = "audit my FX trading drawdown with -S,300 guillotine firewall and short-gamma exposure"
        res = compute_lambda(query, web_required=True)
        self.assertEqual(res["tier"], "ULTRA")
        self.assertGreater(res["score"], 30)
        feature_names = [f["name"] for f in res["features"]]
        self.assertIn("ruin_risk", feature_names)

    def test_ultra_financial_and_contract_signing(self):
        query = "should I sign this client contract for S$1,500 with liability indemnity clause?"
        res = compute_lambda(query)
        self.assertEqual(res["tier"], "ULTRA")
        self.assertGreater(res["score"], 30)
        feature_names = [f["name"] for f in res["features"]]
        self.assertIn("currency_amount", feature_names)
        self.assertIn("irreversible_action", feature_names)

    def test_ultra_social_high_stakes(self):
        query = "invite coursemate to elder brother wedding banquet with S$300 ang-bao"
        res = compute_lambda(query)
        self.assertEqual(res["tier"], "ULTRA")
        self.assertGreater(res["score"], 30)

    def test_crisis_detection_referral_gate(self):
        crisis_queries = [
            "I want to end it all",
            "feeling suicidal today",
            "complete broken can't take it anymore",
            "no point in living",
        ]
        for q in crisis_queries:
            res = compute_lambda(q)
            self.assertTrue(res.get("is_crisis"), f"Expected is_crisis=True for '{q}'")
            referral = res.get("crisis_referral")
            self.assertIsNotNone(referral, f"Expected crisis_referral for '{q}'")
            self.assertIn("1-767", referral)
            self.assertIn("6389 2222", referral)
            self.assertIn("995", referral)
            self.assertIn("Athena is an AI assistant, not a clinician", referral)

    def test_audit_classifier_misses(self):
        # 1. Past-tense job exit
        res1 = compute_lambda("handed in my notice")
        self.assertGreaterEqual(res1["score"], 30)
        feat_names1 = [f["name"] for f in res1["features"]]
        self.assertIn("job_exit_paraphrase", feat_names1)

        # 2. All-in ruin risk
        res2 = compute_lambda("sell everything and go all in")
        self.assertGreaterEqual(res2["score"], 30)
        feat_names2 = [f["name"] for f in res2["features"]]
        self.assertIn("all_in_ruin_risk", feat_names2)

        # 3. Career exit
        res3 = compute_lambda("leaving my job to trade full time")
        self.assertGreaterEqual(res3["score"], 30)
        feat_names3 = [f["name"] for f in res3["features"]]
        self.assertIn("career_exit", feat_names3)

        # 4. Bare large number
        res4 = compute_lambda("200000")
        feat_names4 = [f["name"] for f in res4["features"]]
        self.assertIn("large_bare_number", feat_names4)

    def test_latency_performance(self):
        query = "audit my FX trading drawdown with -S,300 guillotine firewall and short-gamma exposure"
        start = time.perf_counter()
        for _ in range(200):
            compute_lambda(query, web_required=True)
        elapsed_ms = (time.perf_counter() - start) * 1000 / 200
        self.assertLess(elapsed_ms, 5.0)


if __name__ == "__main__":
    unittest.main()

