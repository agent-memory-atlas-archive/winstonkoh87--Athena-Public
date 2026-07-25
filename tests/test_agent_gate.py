"""
Tests for Universal AgentGate (src/athena/core/gate.py & gate_meta.py).
"""

from pathlib import Path

from athena.core.gate import AgentGate
from athena.core.gate_meta import classify


def test_meta_awareness_classification():
    assert "T1-INBOUND" in classify("why did they send this text?")
    assert "T2-OUTBOUND" in classify("should I post this on Twitter?")
    assert "T3-VERDICT" in classify("is this inappropriate, right?")
    assert "T4-RESOURCE" in classify("should I buy this expensive setup?")
    assert "T5-FELT" in classify("i feel like the market is about to pump")

def test_negative_suppression():
    # Routine ops should not trigger T4 resource gate
    assert classify("reconcile the balance sheet tracker") == []

def test_agent_gate_prompt_interception():
    gate = AgentGate(Path("."))
    reminder = gate.intercept_prompt("why did they post this announcement?")
    assert reminder is not None
    assert "<system-reminder>" in reminder
    assert "META-AWARENESS GATE" in reminder

def test_agent_gate_tool_interception():
    gate = AgentGate(Path("."))
    # Safe command
    allowed, reason = gate.intercept_tool("run_command", {"command": "ls -la"})
    assert allowed is True
    assert reason is None

    # Dangerous command
    allowed, reason = gate.intercept_tool("run_command", {"command": "rm -rf .context"})
    assert allowed is False
    assert "Vetoed by StructuredRuinCheck" in reason
