#!/usr/bin/env python3
"""
Athena Maintenance-vs-Output Commit Ratio (Advisory)
=====================================================
Classifies recent commits by conventional-commit prefix and reports the
share of self-maintenance work vs operator-output work. Advisory only —
prints a report, no gate, no side effects (Suggest, Never Impose).

Classification:
    OUTPUT      = feat, fix          (changes what the system does for the operator)
    MAINTENANCE = everything else    (chore, docs, refactor, style, test, ci, ...)
    UNLABELED   = no conventional prefix detected

Usage:
    python3 maintenance_ratio.py                # last 30 days
    python3 maintenance_ratio.py --days 7       # weekly audit window
    python3 maintenance_ratio.py --verbose      # list the output commits
"""

import argparse
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

OUTPUT_PREFIXES = {"feat", "fix"}
PREFIX_RE = re.compile(r"^([a-z]+)(\(|!|:)")

# Advisory threshold: sustained >70% maintenance means the system is
# consuming more attention than it produces — meta-work should yield to output.
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
    match = PREFIX_RE.match(subject)
    if not match:
        return "unlabeled"
    return "output" if match.group(1) in OUTPUT_PREFIXES else "maintenance"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--days", type=int, default=30, help="lookback window (default 30)")
    parser.add_argument("--verbose", action="store_true", help="list output commits")
    args = parser.parse_args()

    commits = collect_commits(args.days)
    if not commits:
        print(f"No commits in the last {args.days} days.")
        return 0

    buckets = Counter(classify(subject) for _, subject in commits)
    total = len(commits)
    maintenance_share = buckets["maintenance"] / total

    print(f"📊 Commit ratio — last {args.days} days ({total} commits)")
    print(f"   Maintenance: {buckets['maintenance']:>4}  ({maintenance_share:.0%})")
    print(f"   Output:      {buckets['output']:>4}  ({buckets['output'] / total:.0%})")
    if buckets["unlabeled"]:
        print(f"   Unlabeled:   {buckets['unlabeled']:>4}  ({buckets['unlabeled'] / total:.0%})")

    if maintenance_share > ADVISORY_THRESHOLD:
        print(
            f"\nℹ️  Maintenance share above {ADVISORY_THRESHOLD:.0%} advisory: "
            "if this holds 2+ consecutive weeks, defer meta-maintenance "
            "in favor of output work."
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

    return 0


if __name__ == "__main__":
    sys.exit(main())
