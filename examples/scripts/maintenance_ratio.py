#!/usr/bin/env python3
"""
Athena Maintenance-vs-Output Commit Ratio (Advisory)
=====================================================
Classifies recent commits by conventional-commit prefix + scope and reports the
share of self-maintenance work vs operator-output work.  Filed as TD-045
(external audit 2026-06-10, F02).

Classification (reconciled with .agent/hooks/commit-msg, 2026-09-12):
    OUTPUT      = feat, fix          (changes what the system does for the operator)
    MAINTENANCE = chore, docs, refactor, style, test, ci, … (self-maintenance)
    BOOKKEEPING = scope(session|checkpoint|ultraend)  (logging heartbeats — neutral)
    UNLABELED   = no conventional prefix detected

The maintenance ratio is computed over ACTIVE work only (maintenance + output).
Bookkeeping commits are excluded from both numerator and denominator so that
high-frequency session closes do not inflate the maintenance share.

Usage:
    python3 maintenance_ratio.py                # last 30 days
    python3 maintenance_ratio.py --days 7       # weekly audit window
    python3 maintenance_ratio.py --verbose      # list the output commits
    python3 maintenance_ratio.py --gate --quiet # commit-msg hook (exit 1 if >70%)
"""

import argparse
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

OUTPUT_PREFIXES = {"feat", "fix"}
# Conventional commit regex extracting prefix and optional scope: type(scope)!: subject
CONVENTIONAL_RE = re.compile(r"^([a-z]+)(?:\(([a-z0-9_.-]+)\))?!?:\s*(.*)")
# Scopes that represent logging heartbeats / session receipts rather than self-maintenance.
# Reconciled with .agent/hooks/commit-msg: case "$SCOPE" in session|checkpoint|ultraend)
BOOKKEEPING_SCOPES = {"session", "checkpoint", "ultraend"}

# Advisory threshold per TD-045: sustained >70% maintenance while I8 is
# stalled means the next GTO sweep should yield to revenue work.
ADVISORY_THRESHOLD = 0.70


def collect_commits(days: int) -> list[tuple[str, str]]:
    """Return (hash, subject) pairs for the window, newest first."""
    result = subprocess.run(
        ["git", "log", f"--since={days} days ago", "--pretty=format:%h\t%s"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return [
        tuple(line.split("\t", 1))
        for line in result.stdout.splitlines()
        if "\t" in line
    ]


def classify(subject: str) -> str:
    match = CONVENTIONAL_RE.match(subject)
    if not match:
        return "unlabeled"
    prefix, scope, _ = match.groups()
    if prefix in OUTPUT_PREFIXES:
        return "output"
    if scope in BOOKKEEPING_SCOPES:
        return "bookkeeping"
    return "maintenance"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--days", type=int, default=30, help="lookback window (default 30)")
    parser.add_argument("--verbose", action="store_true", help="list output commits")
    parser.add_argument("--gate", action="store_true",
                        help="exit 1 when maintenance share exceeds the threshold (commit-msg hook)")
    parser.add_argument("--quiet", action="store_true", help="suppress the report (hook use)")
    args = parser.parse_args()

    try:
        commits = collect_commits(args.days)
    except Exception as exc:  # never let the gate's own failure block a commit
        if not args.quiet:
            print(f"maintenance_ratio: could not read git log ({exc})", file=sys.stderr)
        return 0  # fail-open: exit 1 must mean a genuine breach, nothing else
    if not commits:
        if not args.quiet:
            print(f"No commits in the last {args.days} days.")
        return 0

    buckets = Counter(classify(subject) for _, subject in commits)
    total = len(commits)
    active_total = buckets["maintenance"] + buckets["output"]
    maintenance_share = buckets["maintenance"] / active_total if active_total > 0 else 0.0
    output_share = buckets["output"] / active_total if active_total > 0 else 0.0

    if not args.quiet:
        classified_total = active_total + buckets["bookkeeping"]
        unclassified_share = buckets["unlabeled"] / total if total > 0 else 0.0
        print(f"📊 Commit ratio — last {args.days} days ({total} total commits, {classified_total}/{total} classified)")
        print(f"   Active Work: {active_total}/{total} commits ({active_total / total:.0%})")
        print(f"   ├─ Maintenance: {buckets['maintenance']:>4}  ({maintenance_share:.0%} of active, {buckets['maintenance'] / total:.0%} of total)")
        print(f"   └─ Output:      {buckets['output']:>4}  ({output_share:.0%} of active, {buckets['output'] / total:.0%} of total)")
        if buckets["bookkeeping"]:
            print(f"   Bookkeeping:    {buckets['bookkeeping']:>4}  ({buckets['bookkeeping'] / total:.0%} of total) [session closes/checkpoints]")
        if buckets["unlabeled"]:
            print(f"   Unlabeled:      {buckets['unlabeled']:>4}  ({unclassified_share:.0%} of total)")

        if maintenance_share > ADVISORY_THRESHOLD and active_total > 0:
            print(
                f"\nℹ️  Maintenance share above {ADVISORY_THRESHOLD:.0%} (TD-045 advisory): "
                "if this holds 2 consecutive weeks while I8 is stalled, defer the next "
                "GTO sweep in favor of revenue work."
            )

        if args.verbose:
            output_commits = [
                (sha, subject)
                for sha, subject in commits
                if classify(subject) == "output"
            ]
            print(f"\nOutput commits ({len(output_commits)}):")
            for sha, subject in output_commits:
                print(f"   {sha}  {subject}")

    # --gate: non-zero exit so the commit-msg hook can block a maintenance commit.
    if args.gate and maintenance_share > ADVISORY_THRESHOLD and active_total > 0:
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
