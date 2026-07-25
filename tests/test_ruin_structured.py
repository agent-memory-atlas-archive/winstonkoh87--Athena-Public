"""
Tests for StructuredRuinCheck (src/athena/core/ruin_structured.py).
"""

from pathlib import Path

from athena.core.ruin_structured import StructuredRuinCheck


def test_safe_commands():
    checker = StructuredRuinCheck(Path("."))
    allowed, flags = checker.check_command("git status")
    assert allowed is True
    assert len(flags) == 0

def test_destructive_context_delete():
    checker = StructuredRuinCheck(Path("."))
    allowed, flags = checker.check_command("rm -rf .context")
    assert allowed is False
    assert "targets_context_memory" in flags

def test_destructive_agent_delete():
    checker = StructuredRuinCheck(Path("."))
    allowed, flags = checker.check_command("rm -r -f .agent/config")
    assert allowed is False
    assert "targets_agent_config" in flags

def test_root_directory_delete():
    checker = StructuredRuinCheck(Path("."))
    allowed, flags = checker.check_command("rm -rf /")
    assert allowed is False
    assert "targets_root_directory" in flags
