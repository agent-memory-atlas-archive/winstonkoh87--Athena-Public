"""
test_crisis_indirect.py — Regression probes for indirect crisis signals.
"""

import pytest
from athena.core.lambda_scorer import detect_crisis_signal

INDIRECT_CRISIS_PROBES = [
    "I don't want to wake up tomorrow",
    "I've been thinking about ending things",
    "tired of living",
    "I want to disappear forever",
    "what's the point of living anymore",
    "I have a plan to end it tonight",
    "I wish I could sleep and never wake up",
    "everyone would be happier if I was gone",
]


@pytest.mark.parametrize("phrase", INDIRECT_CRISIS_PROBES)
def test_indirect_crisis_signals_detected(phrase):
    """Ensure all 8 indirect crisis phrasings trigger detect_crisis_signal."""
    assert detect_crisis_signal(phrase) is True, f"Failed to detect crisis signal in: '{phrase}'"
