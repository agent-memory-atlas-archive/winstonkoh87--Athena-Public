"""Tests for examples/hooks/meta_awareness_gate.py v3 — structural classes T1-T5.

Covers: per-class positives across 6+ life domains, cross-domain golden cases,
negative controls (routine ops must not fire), the T4-only suppression guard,
and the hook's never-block contract.
"""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

HOOK_PATH = Path(__file__).resolve().parents[1] / "examples" / "hooks" / "meta_awareness_gate.py"

spec = importlib.util.spec_from_file_location("meta_gate", HOOK_PATH)
meta_gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(meta_gate)


def fired(prompt: str):
    return meta_gate.classify(prompt)


# ---------------------------------------------------------------- T1 INBOUND
@pytest.mark.parametrize("prompt", [
    "why would the landlord suddenly offer a discount on renewal?",
    "HR scheduled a meeting with no agenda — what does this mean?",
    "what's the real reason he took this route?",
    "she hasn't replied for three days",
    "he left me on read again",
    "am I missing something in this contract clause?",
])
def test_t1_inbound_fires(prompt):
    assert "T1-INBOUND" in fired(prompt)


# --------------------------------------------------------------- T2 OUTBOUND
@pytest.mark.parametrize("prompt", [
    "should I post this hot take publicly?",
    "thinking of inviting a coursemate to the wedding",
    "before I send this quote to the client, sanity check it",
    "I invited him to the wedding and he got very angry",  # retro decode
    "should I sign the tenancy agreement today?",
    "how will this come across if I share it in the group chat?",
])
def test_t2_outbound_fires(prompt):
    assert "T2-OUTBOUND" in fired(prompt)


# ---------------------------------------------------------------- T3 VERDICT
@pytest.mark.parametrize("prompt", [
    "is this okay that he texted my client directly?",
    "that comment she made — wasn't it inappropriate?",
    "how could he say that in front of everyone",
])
def test_t3_verdict_fires(prompt):
    assert "T3-VERDICT" in fired(prompt)


# --------------------------------------------------------------- T4 RESOURCE
@pytest.mark.parametrize("prompt", [
    "should I buy the air fryer at the promo price?",
    "is the collector's box worth it at $80?",
    "should I subscribe to the premium charting plan?",
    "should I book the casino trip for the poker series?",
    "is this a fair price for the freelance job?",
])
def test_t4_resource_fires(prompt):
    assert "T4-RESOURCE" in fired(prompt)


# ------------------------------------------------------------------- T5 FELT
@pytest.mark.parametrize("prompt", [
    "I feel like the market has to bounce here",
    "it seems like they respect me now",
    "obviously she wants me there",
    "my gut says this dip is the bottom",
    "felt like we really connected at the gym",  # adverb-tolerant pattern
])
def test_t5_felt_fires(prompt):
    assert len(fired(prompt)) > 0


# ------------------------------------------------- Cross-domain golden cases
GOLDEN = {
    "relational-inbound":  "felt like we really connected — why hasn't he texted back?",
    "wedding-invite":      "I invited a coursemate to the wedding and he got very angry, he thought he was a table filler",
    "employment-pip":      "HR put me on a PIP but says it's for my growth — what does it mean?",
    "shorted-invoice":     "the client's payment came in $20 short, am I missing something or just a mistake?",
    "public-callout":      "should I call out this coach publicly? what he did looks inappropriate",
    "travel-commit":       "should I book the casino trip for the poker series?",
    "trading-hot-streak":  "the strategy is printing — I feel like this edge is real, should I scale up?",
    "collectible-fomo":    "are these boxes worth it at $80? feels like they'll only go up",
    "consumer-promo":      "should I buy the air fryer at the promo price?",
    "tail-risk-denial":    "everyone says the volcano tour is perfectly safe, obviously nothing will happen",
    "harsh-feedback":      "the reviewer was harsh with me again — is that okay or is it just cruel?",
    "confession-timing":   "it's my last week here — should I tell her how I actually feel?",
}


@pytest.mark.parametrize("case,prompt", GOLDEN.items())
def test_golden_cases_fire(case, prompt):
    assert len(fired(prompt)) > 0, f"golden case '{case}' did not fire"


# --------------------------------------------------------- Negative controls
@pytest.mark.parametrize("prompt", [
    "reconcile the June statement against the broker report",
    "rebuild the Excel tracker and sync balances",
    "compile the index",
    "fix the failing pytest in test_boot.py",
    "update the changelog for the next release",
    "list the files in the examples directory",
])
def test_negatives_do_not_fire(prompt):
    assert fired(prompt) == []


def test_negative_guard_suppresses_t4_only():
    # Routine-ops context + a T4-only match -> suppressed by design.
    prompt = "reconcile the statement, then tell me if the surplus is worth topping up"
    assert fired(prompt) == []


# ------------------------------------------------------------ Hook contract
def test_hook_never_blocks_and_injects():
    """End-to-end: run as the harness does; malformed input exits 0 silently."""
    ok = subprocess.run(
        [sys.executable, str(HOOK_PATH)],
        input=json.dumps({"prompt": "should I post this publicly?"}),
        capture_output=True, text=True,
    )
    assert ok.returncode == 0
    assert "META-AWARENESS GATE" in ok.stdout
    assert "T2-OUTBOUND" in ok.stdout

    bad = subprocess.run(
        [sys.executable, str(HOOK_PATH)],
        input="not json", capture_output=True, text=True,
    )
    assert bad.returncode == 0
    assert bad.stdout == ""


def test_reminder_is_question_framed_and_bounded():
    text = meta_gate.REMINDER_TEMPLATE
    assert text.count("?") >= 6          # ask-don't-tell framing
    assert len(text.splitlines()) <= 18  # injection-fatigue bound
