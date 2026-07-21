#!/usr/bin/env python3
"""
Maintenance-vs-Output Commit Ratio
==================================
Classifies recent commits by conventional-commit prefix and reports the share
of self-maintenance work vs user-facing output. A system that spends most of its
commits grooming itself has quietly stopped shipping — this makes that visible,
and (with --gate) enforceable via the commit-msg hook.

    OUTPUT      = feat, fix          (changes what the system does for the user)
    MAINTENANCE = everything else    (chore, docs, refactor, style, test, ci, ...)
    UNLABELED   = no conventional prefix detected

Advisory by default; with --gate it exits non-zero when the ratio is breached,
so scripts/hooks/commit-msg can turn DISCIPLINE.md Rule 6 from advisory into
enforced. Advisory alone was ignored — a readout you can skip is not a control.

Usage:
    python3 maintenance_ratio.py                # last 30 days
    python3 maintenance_ratio.py --days 14      # audit window
    python3 maintenance_ratio.py --gate --quiet # exit 1 if over threshold (hook use)
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

# When maintenance share holds above this for two consecutive audit windows, the
# next commit should be output (feat/fix) or a deletion — not another sweep.
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
    maintenance_share = buckets["maintenance"] / total

    if not args.quiet:
        print(f"📊 Commit ratio — last {args.days} days ({total} commits)")
        print(f"   Maintenance: {buckets['maintenance']:>4}  ({maintenance_share:.0%})")
        print(f"   Output:      {buckets['output']:>4}  ({buckets['output'] / total:.0%})")
        if buckets["unlabeled"]:
            print(f"   Unlabeled:   {buckets['unlabeled']:>4}  ({buckets['unlabeled'] / total:.0%})")

        if maintenance_share > ADVISORY_THRESHOLD:
            print(
                f"\nℹ️  Maintenance share above {ADVISORY_THRESHOLD:.0%}: if this holds two "
                "consecutive audits, the next commit must be output (feat/fix) or a "
                "deletion — not another reorganization."
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
    if args.gate and maintenance_share > ADVISORY_THRESHOLD:
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
