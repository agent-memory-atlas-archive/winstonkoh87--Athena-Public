#!/usr/bin/env python3
"""
stop_governance_gate.py — Antigravity Stop Lifecycle Governance Gate
===================================================================

Enforces:
1. Law #6 External Verification Mandate (Triple-Lock):
   Substantive turns (STANDARD/ULTRA) MUST invoke at least one external tool
   (context_gate, smart_search, search_web, view_file, grep_search, run_command)
   before emitting a final answer.
2. Epistemic Grounding Gate:
   Universal-negative claims ('never made', 'does not exist') require verified web search.

Antigravity Stop Hook Contract:
  Input (stdin): JSON object with transcriptPath, terminationReason, etc.
  Output (stdout): {"decision": "allow"} or {"decision": "continue", "reason": "..."}
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Trivial/conversational phrases exempt from the verification mandate
TRIVIAL_PATTERNS = [
    r"^(hi|hello|hey|yo|morning|afternoon|evening)\b",
    r"^(thanks|thank you|ty|cheers|got it|noted|ok|okay|cool|nice|good)\b",
    r"^(yes|no|proceed|continue|agree|approved|lgtm|looks good)\b",
    r"^(bye|goodbye|cya|see you)\b",
]

UNIVERSAL_NEGATIVE_PATTERNS = [
    r"\b(?:has\s+)?never\s+(?:been\s+)?(?:made|manufactured|produced|released|shipped|created|sold|launched)\b",
    r"\b(?:does\s+not|doesn'?t|did\s+not|didn'?t)\s+exist\b",
    r"\bno\s+such\s+(?:model|product|device|version|watch|shoe|car|service|tool|item|edition|feature|release)\b",
    r"\bis\s+not\s+a\s+real\s+(?:model|product|device|version|watch|shoe|car|service|tool|item|edition)\b",
    r"\bhas\s+never\s+existed\b",
]

EXTERNAL_TOOL_NAMES = {
    "context_gate", "smart_search", "search_web", "quicksave",
    "view_file", "grep_search", "find_by_name", "list_dir",
    "run_command", "call_mcp_tool", "read_url_content",
    "meta_awareness_check", "governance_status", "agentic_search",
}


def is_trivial_query(query: str) -> bool:
    """Check if a user prompt is trivial conversational banter (SNIPER-exempt)."""
    cleaned = query.strip().lower()
    if not cleaned:
        return True

    words = cleaned.split()
    if len(words) <= 4:
        for pat in TRIVIAL_PATTERNS:
            if re.search(pat, cleaned):
                return True

    return False


def clean_prompt_content(raw_content: str) -> str:
    """Strip Antigravity XML tags from raw prompt content."""
    text = raw_content
    text = re.sub(r"<ADDITIONAL_METADATA>[\s\S]*?</ADDITIONAL_METADATA>", "", text)
    text = re.sub(r"<USER_SETTINGS_CHANGE>[\s\S]*?</USER_SETTINGS_CHANGE>", "", text)
    text = re.sub(r"<SYSTEM_MESSAGE>[\s\S]*?</SYSTEM_MESSAGE>", "", text)
    m = re.search(r"<USER_REQUEST>([\s\S]*?)</USER_REQUEST>", text)
    if m:
        return m.group(1).strip()
    return text.strip()


def evaluate_turn_governance(transcript_path: str) -> dict[str, str]:
    """Inspect the latest turn in transcript.jsonl for governance compliance."""
    path = Path(transcript_path)
    if not path.exists():
        return {"decision": "allow"}

    steps: list[dict[str, Any]] = []
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        steps.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    except Exception:
        return {"decision": "allow"}

    if not steps:
        return {"decision": "allow"}

    # Find the index of the most recent USER_INPUT
    last_user_idx = -1
    last_user_content = ""
    for i, step in enumerate(steps):
        if step.get("type") == "USER_INPUT":
            last_user_idx = i
            last_user_content = step.get("content", "")

    if last_user_idx == -1:
        return {"decision": "allow"}

    cleaned_user_prompt = clean_prompt_content(last_user_content)

    # Evaluate risk tier using lambda_scorer (Phase C1)
    try:
        sys.path.insert(0, str(REPO_ROOT / "src"))
        from athena.core.lambda_scorer import compute_lambda
        lambda_info = compute_lambda(cleaned_user_prompt)
        if lambda_info["tier"] == "SNIPER":
            return {"decision": "allow"}
    except Exception:
        if is_trivial_query(cleaned_user_prompt):
            return {"decision": "allow"}

    # Inspect all steps following the last USER_INPUT
    turn_steps = steps[last_user_idx + 1:]
    tools_called: list[str] = []
    latest_model_output = ""

    for s in turn_steps:
        # Check tool calls
        t_calls = s.get("tool_calls", [])
        if isinstance(t_calls, list):
            for tc in t_calls:
                if isinstance(tc, dict):
                    name = tc.get("name", "")
                    if name:
                        tools_called.append(name)

        # Check content for model output
        if s.get("source") == "MODEL" and s.get("type") == "PLANNER_RESPONSE":
            content = s.get("content", "")
            if content:
                latest_model_output += "\n" + content

    # Check 1: Did the agent call ANY external verification tool?
    external_called = any(t in EXTERNAL_TOOL_NAMES for t in tools_called)

    if not external_called:
        return {
            "decision": "continue",
            "reason": (
                "STOP BLOCKED by Law #6 Triple-Lock Gate: You attempted to complete a "
                "substantive turn without external verification. You MUST execute context_gate(query) "
                "or an external verification tool before concluding this turn."
            ),
        }

    # Check 2: Did the agent emit an ungrounded universal negative?
    if latest_model_output:
        has_negative_claim = any(
            re.search(pat, latest_model_output, re.IGNORECASE)
            for pat in UNIVERSAL_NEGATIVE_PATTERNS
        )
        if has_negative_claim:
            web_verified = (
                "search_web" in tools_called
                or "context_gate" in tools_called
                or "read_url_content" in tools_called
            )
            if not web_verified:
                return {
                    "decision": "continue",
                    "reason": (
                        "STOP BLOCKED by Epistemic Grounding Gate: You asserted a universal-negative "
                        "claim ('does not exist' / 'never made') without live web verification. "
                        "Verify via search_web() or rephrase with calibrated epistemic uncertainty."
                    ),
                }

    return {"decision": "allow"}


def main():
    raw_input = sys.stdin.read().strip()
    if not raw_input:
        print(json.dumps({"decision": "allow"}))
        return

    try:
        payload = json.loads(raw_input)
    except Exception:
        print(json.dumps({"decision": "allow"}))
        return

    termination_reason = payload.get("terminationReason", "")
    if termination_reason and termination_reason != "model_stop":
        print(json.dumps({"decision": "allow"}))
        return

    transcript_path = payload.get("transcriptPath", "")
    if not transcript_path:
        print(json.dumps({"decision": "allow"}))
        return

    result = evaluate_turn_governance(transcript_path)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
