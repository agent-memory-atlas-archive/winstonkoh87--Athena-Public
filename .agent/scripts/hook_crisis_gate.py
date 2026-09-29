#!/usr/bin/env python3
"""
hook_crisis_gate.py — Protocol 509 Life-Safety & Crisis Gate (Code-Enforced).

Claude Code UserPromptSubmit hook.
Detects acute crisis/self-harm signals in the user's prompt and injects the
mandatory Singapore/international emergency hotline referral into the model context.

Contract:
  - NEVER blocks prompt submission (always exits 0).
  - Fast (<80ms), stdlib-only dependencies + lambda_scorer.
  - On detection: outputs <system-reminder> containing CRISIS_REFERRAL_TEXT.
"""

import json
import os
import sys
from pathlib import Path

# Resolve src directory relative to this file
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

try:
    from athena.core.lambda_scorer import CRISIS_REFERRAL_TEXT, detect_crisis_signal
except ImportError:
    # Fail-safe fallback if lambda_scorer cannot be loaded
    CRISIS_REFERRAL_TEXT = (
        "CRISIS REFERRAL MANDATE (Protocol 509):\n"
        "- SOS (Samaritans of Singapore): 1-767 (24h) or WhatsApp 9151 1767\n"  # pds:allow
        "- IMH Emergency Helpline: 6389 2222 (24h)\n"
        "- Emergency Services: 995 (SCDF) or 999 (Police)\n"
        "- International: https://findahelpline.com\n"
    )

    def detect_crisis_signal(text: str) -> bool:
        return any(
            w in text.lower()
            for w in [
                "want to die",
                "kill myself",
                "suicide",
                "unalive",
                "kms",
                "end it all",
                "better off dead",
            ]
        )


def main():
    try:
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            sys.exit(0)
        payload = json.loads(raw_input)
    except Exception:
        sys.exit(0)

    prompt = (payload.get("prompt") or "").strip()
    if not prompt:
        sys.exit(0)

    if detect_crisis_signal(prompt):
        sys.stdout.write(
            f"\n<system-reminder>\n"
            f"PROTOCOL 509 CRISIS & LIFE-SAFETY MANDATE:\n"
            f"Acute distress or self-harm signal detected. Immediately prioritize life-safety.\n"
            f"You MUST lead with this referral before any other output:\n\n"
            f"{CRISIS_REFERRAL_TEXT}\n"
            f"</system-reminder>\n"
        )

    sys.exit(0)


if __name__ == "__main__":
    main()
