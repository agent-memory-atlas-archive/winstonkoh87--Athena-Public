#!/usr/bin/env python3
"""
quicksave.py — Session Checkpointing (Public Example)
======================================================
Appends a timestamped checkpoint to the current session log.
This is a simplified, standalone version for Athena-Public.

Usage:
    python3 scripts/core/quicksave.py "Completed OAuth integration"
    python3 scripts/core/quicksave.py "Fixed edge case" --bullets "Bug in auth" "Added test"
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

# Discover session log directory (relative to script location)
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
SESSION_LOG_DIR = PROJECT_ROOT / "session_logs"


def get_current_session_log() -> Path:
    """
    Get (or create) today's session log file.
    Follows the format: YYYY-MM-DD-session-01.md
    """
    SESSION_LOG_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")

    # Find existing session for today, or create a new one
    existing = list(SESSION_LOG_DIR.glob(f"{today}-session-*.md"))
    if existing:
        # Get the latest session file for today
        return sorted(existing, reverse=True)[0]
    else:
        # Create a new session file
        new_session = SESSION_LOG_DIR / f"{today}-session-01.md"
        new_session.write_text(f"# Session Log: {today}\n\n")
        return new_session


def append_checkpoint(session_log: Path, summary: str, bullets: list[str] = None):
    """
    Append a checkpoint entry to the session log.
    """
    timestamp = datetime.now().strftime("%H:%M")
    entry = f"\n## [{timestamp}] Checkpoint\n\n{summary}\n"

    if bullets:
        entry += "\n"
        for bullet in bullets:
            entry += f"- {bullet}\n"

    with open(session_log, "a") as f:
        f.write(entry)


def main():
    parser = argparse.ArgumentParser(
        description="Athena Quicksave — Append a checkpoint to session log"
    )
    parser.add_argument("summary", help="Summary of activity")
    parser.add_argument("--bullets", nargs="+", help="Optional bullet points for details")
    args = parser.parse_args()

    try:
        session_log = get_current_session_log()
        append_checkpoint(session_log, args.summary, args.bullets)
        print(f"✅ Quicksave [{datetime.now().strftime('%H:%M')}] → {session_log.name}")
    except Exception as e:
        print(f"❌ Quicksave failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
