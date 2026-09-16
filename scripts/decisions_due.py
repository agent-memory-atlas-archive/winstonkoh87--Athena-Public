#!/usr/bin/env python3
"""
decisions_due.py — Decision Review & Calibration Deadline Reader
================================================================
Reads `.context/memory_bank/decisionLog.md` and `.context/calibration/CALIBRATION_LEDGER.md`
to surface:
1. Active CAL predictions past deadline.
2. Logged decisions past review date.
3. Dateless decisions requiring scheduling or archiving (legacy entries).

Usage:
    python3 .agent/scripts/decisions_due.py
    python3 .agent/scripts/decisions_due.py --json
    python3 .agent/scripts/decisions_due.py --brief
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONTEXT_DIR = PROJECT_ROOT / ".context"
DECISION_LOG_FILE = CONTEXT_DIR / "memory_bank" / "decisionLog.md"
CAL_LEDGER_FILE = CONTEXT_DIR / "calibration" / "CALIBRATION_LEDGER.md"


def get_current_date() -> date:
    return date.today()


def check_cal_ledger(today: date) -> list[dict[str, str]]:
    if not CAL_LEDGER_FILE.exists():
        return []

    content = CAL_LEDGER_FILE.read_text(encoding="utf-8")
    blocks = re.split(r"\n(?=###\s+CAL-)", content)
    due_items = []

    for block in blocks:
        if not block.strip().startswith("### CAL-"):
            continue

        id_match = re.search(r"###\s+(CAL-\d+)", block)
        claim_match = re.search(r"-\s+\*\*Claim\*\*:\s*(.+)", block)
        deadline_match = re.search(r"-\s+\*\*Deadline\*\*:\s*(\d{4}-\d{2}-\d{2})", block)
        outcome_match = re.search(r"-\s+\*\*Outcome\*\*:\s*(\w+)", block)

        if not id_match:
            continue

        cal_id = id_match.group(1)
        claim = claim_match.group(1).strip() if claim_match else "No claim"
        outcome = outcome_match.group(1).strip().lower() if outcome_match else "pending"

        if outcome != "pending":
            continue

        if deadline_match:
            d_str = deadline_match.group(1).strip()
            try:
                deadline_dt = datetime.strptime(d_str, "%Y-%m-%d").date()
                if deadline_dt <= today:
                    due_items.append({
                        "id": cal_id,
                        "type": "CAL_PREDICTION",
                        "deadline": d_str,
                        "description": claim[:80] + ("..." if len(claim) > 80 else ""),
                        "status": "OVERDUE" if deadline_dt < today else "DUE_TODAY",
                    })
            except ValueError:
                pass

    return due_items


def check_decision_log(today: date) -> tuple[list[dict[str, str]], int]:
    if not DECISION_LOG_FILE.exists():
        return [], 0

    content = DECISION_LOG_FILE.read_text(encoding="utf-8")
    blocks = re.split(r"\n(?=###\s+\[\d{4}-\d{2}-\d{2}\])", content)
    due_items = []
    dateless_count = 0

    for block in blocks:
        header_match = re.search(r"###\s+\[(\d{4}-\d{2}-\d{2})\]\s*(.+)", block)
        if not header_match:
            continue

        dec_date_str = header_match.group(1)
        title = header_match.group(2).strip()

        review_match = re.search(r"(?:review[_-]?date|review\s*by):\s*(\d{4}-\d{2}-\d{2})", block, re.IGNORECASE)

        if review_match:
            r_str = review_match.group(1).strip()
            try:
                r_dt = datetime.strptime(r_str, "%Y-%m-%d").date()
                if r_dt <= today:
                    due_items.append({
                        "id": f"DEC-[{dec_date_str}]",
                        "type": "DECISION_REVIEW",
                        "deadline": r_str,
                        "description": title[:80] + ("..." if len(title) > 80 else ""),
                        "status": "OVERDUE" if r_dt < today else "DUE_TODAY",
                    })
            except ValueError:
                dateless_count += 1
        else:
            dateless_count += 1

    return due_items, dateless_count


def main() -> int:
    parser = argparse.ArgumentParser(description="Athena Decision & Calibration Review Scanner")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    parser.add_argument("--brief", action="store_true", help="Output compact one-line summary")
    args = parser.parse_args()

    today = get_current_date()
    cal_due = check_cal_ledger(today)
    dec_due, dateless_count = check_decision_log(today)

    total_due = len(cal_due) + len(dec_due)

    if args.brief:
        print(f"Decisions: {total_due} due for review | {dateless_count} dateless legacy")
        return 0

    if args.json:
        data = {
            "scanned_date": str(today),
            "total_due": total_due,
            "dateless_decisions": dateless_count,
            "cal_overdue": cal_due,
            "decisions_due": dec_due,
        }
        print(json.dumps(data, indent=2))
        return 0

    print("============================================================")
    print(f"       ATHENA DECISION & CALIBRATION DUE SCANNER ({today})   ")
    print("============================================================")
    print(f"  Items Due for Review: {total_due}")
    print(f"  Dateless Decisions  : {dateless_count} (legacy un-scheduled)")
    print("------------------------------------------------------------")

    if cal_due:
        print("  CALIBRATION PREDICTIONS DUE:")
        for item in cal_due:
            print(f"    [{item['status']}] {item['id']} (Deadline: {item['deadline']}): {item['description']}")
    else:
        print("  CALIBRATION PREDICTIONS DUE: None")

    print("------------------------------------------------------------")
    if dec_due:
        print("  DECISIONS DUE FOR REVIEW:")
        for item in dec_due:
            print(f"    [{item['status']}] {item['id']} (Review: {item['deadline']}): {item['description']}")
    else:
        print("  DECISIONS DUE FOR REVIEW: None")

    print("============================================================")
    return 0


if __name__ == "__main__":
    sys.exit(main())
