"""Tests for hook_meta_awareness_gate.py v3 — structural trigger classes T1-T5.

Covers: per-class positives across >=6 domains, the 12 golden historical cases
(known-answer reads from the corpus), negative controls (routine ops must not
fire), and the T4-only negative-guard suppression rule.
"""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

HOOK_PATH = Path(__file__).resolve().parents[1] / ".agent" / "scripts" / "hook_meta_awareness_gate.py"

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
    "should I post this take on EDMW?",
    "thinking of inviting my coursemate to the wedding",
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
    "am i being pryce about this?",
])
def test_t3_verdict_fires(prompt):
    assert "T3-VERDICT" in fired(prompt)


# --------------------------------------------------------------- T4 RESOURCE
@pytest.mark.parametrize("prompt", [
    "should I buy the Cornell air fryer at the promo price?",
    "is the ETB worth it at $130?",
    "should I subscribe to TradingView premium?",
    "should I book the Genting trip for the poker series?",
    "is this a fair price for the FlexSim job?",
])
def test_t4_resource_fires(prompt):
    assert "T4-RESOURCE" in fired(prompt)


# ------------------------------------------------------------------- T5 FELT
@pytest.mark.parametrize("prompt", [
    "I feel like the market has to bounce here",
    "it seems like they respect me now",
    "obviously she wants me there",
    "my gut says this dip is the bottom",
    "felt like we really connected at the gym",
])
def test_t5_felt_fires(prompt):
    assert len(fired(prompt)) > 0  # T5 or co-fired class


# ------------------------------------------------- Golden historical cases
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


def test_golden_pass_rate():
    hits = sum(1 for p in GOLDEN.values() if fired(p))
    assert hits >= 10, f"golden fire rate {hits}/12 below plan threshold"


# --------------------------------------------------------- Negative controls
@pytest.mark.parametrize("prompt", [
    "reconcile the June statement against Myfxbook",
    "rebuild the Excel tracker and sync balances to v3.25.0",
    "compile the case study index",
    "fix the failing pytest in test_boot.py",
    "update the changelog for v9.9.7",
    "list the files in .agent/skills",
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
        input=json.dumps({"prompt": "should I post this on EDMW?"}),
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


def test_mcp_meta_awareness_check_parity():
    """Verify FastMCP tool returns correct injection payload."""
    from athena.mcp_server import meta_awareness_check

    # FastMCP 2.x wraps @mcp.tool functions in a FunctionTool object whose
    # underlying callable is exposed as `.fn`. Fall back to the object itself so
    # the test survives a FastMCP API change in either direction.
    check = getattr(meta_awareness_check, "fn", meta_awareness_check)

    res = check("should I post this on EDMW?")
    assert "T2-OUTBOUND" in res["fired"]
    assert res["injection"] is not None
    assert "META-AWARENESS GATE" in res["injection"]

    res_clean = check("fix the failing pytest in test_boot.py")
    assert res_clean["fired"] == []
    assert res_clean["injection"] is None


def test_governance_skip_auditor():
    """Verify check_governance_skip.py runs without error."""
    script_path = Path(__file__).resolve().parents[1] / ".agent" / "scripts" / "check_governance_skip.py"
    ok = subprocess.run(
        [sys.executable, str(script_path), "--days", "7"],
        capture_output=True, text=True,
    )
    assert ok.returncode == 0
    assert "Governance Telemetry Audit" in ok.stdout

