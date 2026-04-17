#!/usr/bin/env python3
"""
Telemetry Logger — Structured invocation tracking for evidence-based pruning.

Appends one JSONL record per workflow/skill/protocol invocation.
After 30 days of collection, analyze the data to identify unused components
for archival (bottom 40% by invocation count).

Usage (CLI):
    python3 log_invocation.py --type workflow --name do --trigger "user command" --session-id "sess-123"

Usage (Import):
    from log_invocation import log_invocation
    log_invocation("workflow", "do", trigger="user command")

Output: .athena/invocations.jsonl
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LOG_FILE = REPO_ROOT / ".athena" / "invocations.jsonl"


def log_invocation(
    inv_type: str,
    name: str,
    trigger: str = "",
    session_id: str = "",
    tokens_in: int = 0,
    tokens_out: int = 0,
    latency_ms: int = 0,
    user_reaction: str = "",
) -> dict:
    """Append one invocation record to the JSONL log."""
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "type": inv_type,
        "name": name,
        "trigger": trigger,
        "session_id": session_id,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "latency_ms": latency_ms,
        "user_reaction": user_reaction,
    }
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(record) + "\n")
    return record


def main():
    parser = argparse.ArgumentParser(description="Log a workflow/skill/protocol invocation")
    parser.add_argument("--type", required=True, choices=["workflow", "skill", "protocol"])
    parser.add_argument("--name", required=True, help="Name of the workflow/skill/protocol")
    parser.add_argument("--trigger", default="", help="What triggered the invocation")
    parser.add_argument("--session-id", default="", help="Session identifier")
    parser.add_argument("--tokens-in", type=int, default=0)
    parser.add_argument("--tokens-out", type=int, default=0)
    parser.add_argument("--latency-ms", type=int, default=0)
    parser.add_argument("--user-reaction", default="")
    args = parser.parse_args()

    record = log_invocation(
        args.type, args.name, args.trigger, args.session_id,
        args.tokens_in, args.tokens_out, args.latency_ms, args.user_reaction,
    )
    print(f"✅ Logged: {args.type}/{args.name} at {record['timestamp']}")


if __name__ == "__main__":
    main()
