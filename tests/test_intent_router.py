"""
tests/test_intent_router.py — Regression tests for query intent routing (F-05).
"""

import pytest
from athena.tools.search import classify_query_intent


@pytest.mark.parametrize(
    "query,expected",
    [
        ("Should I take the A92 deal?", "PERSONALISED_DECISION"),
        ("what is the maximum fuse on the XAUUSD layering grid", "PERSONALISED_DECISION"),
        ("Explain protocol 509", "SYSTEM_KNOWLEDGE"),
        ("Tell me about my trades", "PERSONALISED_DECISION"),
        ("what is the statutory basis under ACRA s145(1)", "SYSTEM_KNOWLEDGE"),
        ("What is GraphRAG?", "GENERAL"),
        ("Should I use use a reranker for 50 candidates", "SYSTEM_KNOWLEDGE"),
        ("how do i calculate my runway", "PERSONALISED_DECISION"),
    ],
)
def test_intent_router_8_query_regression(query, expected):
    """Assert the 8 flagship queries from RETRIEVAL_CLAIMS_REDTEAM_2026-10-28 route correctly."""
    actual = classify_query_intent(query)
    assert actual == expected, f"Query '{query}' expected {expected}, got {actual}"
