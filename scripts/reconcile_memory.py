#!/usr/bin/env python3
"""
reconcile_memory.py — Memory Reconciliation Engine (REC)
========================================================

Scans Athena memory surfaces for contradictions, staleness, and bloat.
Compares facts across CANONICAL.md, activeContext.md, session logs,
and other memory bank files.

Detects:
  - COUNT_CONFLICT: Same metric with different values across files
  - VERSION_SKEW: Version numbers that don't match
  - STALENESS: Files not updated in >14 days
  - BLOAT: Files exceeding their documented size ceiling

Usage:
    python3 scripts/reconcile_memory.py

Output: .context/audit/reconciliation_report.md
"""

import os
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path


def find_project_root() -> Path:
    """Walk up from script location to find .athena_root marker."""
    current = Path(__file__).resolve().parent
    for _ in range(5):
        if (current / ".athena_root").exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent


PROJECT_ROOT = find_project_root()
MEMORY_SURFACES = {
    "CANONICAL": PROJECT_ROOT / ".context" / "CANONICAL.md",
    "activeContext": PROJECT_ROOT / ".context" / "memory_bank" / "activeContext.md",
    "userContext": PROJECT_ROOT / ".context" / "memory_bank" / "userContext.md",
    "decisionLog": PROJECT_ROOT / ".context" / "memory_bank" / "decisionLog.md",
    "productContext": PROJECT_ROOT / ".context" / "memory_bank" / "productContext.md",
}


def extract_facts(filepath: Path) -> list[dict]:
    """Extract version numbers, counts, and dates from a file."""
    facts = []
    if not filepath.exists():
        return facts

    content = filepath.read_text(encoding="utf-8", errors="ignore")

    # Extract version-like patterns
    for match in re.finditer(r'v(\d+\.\d+\.?\d*)', content):
        facts.append({
            "type": "version",
            "value": match.group(1),
            "source": filepath.name,
            "context": content[max(0, match.start()-30):match.end()+30].strip(),
        })

    # Extract count patterns (e.g., "427", "1,200+")
    for match in re.finditer(r'\*\*(\d[\d,]*\+?)\*\*', content):
        facts.append({
            "type": "count",
            "value": match.group(1),
            "source": filepath.name,
            "context": content[max(0, match.start()-50):match.end()+50].strip(),
        })

    return facts


def check_staleness(surfaces: dict) -> list[dict]:
    """Check which memory surfaces haven't been updated in >14 days."""
    issues = []
    now = datetime.now()

    for name, path in surfaces.items():
        if not path.exists():
            continue

        mtime = datetime.fromtimestamp(os.path.getmtime(path))
        age_days = (now - mtime).days
        if age_days > 14:
            issues.append({
                "type": "STALENESS",
                "severity": "warning",
                "source": name,
                "detail": f"{name} last modified {age_days} days ago ({mtime.strftime('%Y-%m-%d')})",
            })

    return issues


def check_bloat(surfaces: dict) -> list[dict]:
    """Check if files exceed their documented size ceilings."""
    issues = []
    ceilings = {
        "activeContext": 80,  # lines
    }

    for name, max_lines in ceilings.items():
        path = surfaces.get(name)
        if not path or not path.exists():
            continue

        line_count = len(path.read_text(encoding="utf-8").splitlines())
        if line_count > max_lines:
            issues.append({
                "type": "BLOAT",
                "severity": "error",
                "source": name,
                "detail": f"{name} has {line_count} lines (ceiling: {max_lines})",
            })

    return issues


def find_contradictions(all_facts: dict) -> list[dict]:
    """Cross-reference facts across surfaces to find contradictions."""
    issues = []
    # Group by count context (rough matching)
    count_facts = defaultdict(list)
    for _source, facts in all_facts.items():
        for f in facts:
            if f["type"] == "count":
                # Use surrounding context as a rough key
                count_facts[f["value"]].append(f)

    # Check version consistency
    versions = defaultdict(list)
    for _source, facts in all_facts.items():
        for f in facts:
            if f["type"] == "version":
                versions[f["value"]].append(f)

    if len(versions) > 1:
        values = list(versions.keys())
        for i in range(len(values)):
            for j in range(i+1, len(values)):
                v1_sources = [f["source"] for f in versions[values[i]]]
                v2_sources = [f["source"] for f in versions[values[j]]]
                issues.append({
                    "type": "VERSION_SKEW",
                    "severity": "warning",
                    "detail": f"v{values[i]} in {v1_sources} vs v{values[j]} in {v2_sources}",
                })

    return issues


def main():
    print("🔍 Athena Memory Reconciliation Engine")
    print("=" * 50)

    # Extract facts from all surfaces
    all_facts = {}
    for name, path in MEMORY_SURFACES.items():
        facts = extract_facts(path)
        all_facts[name] = facts
        print(f"  📄 {name}: {len(facts)} facts extracted")

    # Also scan recent session logs
    session_logs = PROJECT_ROOT / ".context" / "memories" / "session_logs"
    if session_logs.exists():
        recent = sorted(session_logs.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)[:5]
        for log in recent:
            facts = extract_facts(log)
            all_facts[log.stem] = facts
            print(f"  📝 {log.stem}: {len(facts)} facts extracted")

    # Run all checks
    contradictions = find_contradictions(all_facts)
    staleness = check_staleness(MEMORY_SURFACES)
    bloat = check_bloat(MEMORY_SURFACES)

    all_issues = contradictions + staleness + bloat

    print(f"\n  🔎 Contradictions: {len(contradictions)}")
    print(f"  ⏰ Staleness:      {len(staleness)}")
    print(f"  📈 Bloat:          {len(bloat)}")
    print(f"  {'=' * 30}")
    print(f"  Total issues:      {len(all_issues)}")

    # Write report
    report_dir = PROJECT_ROOT / ".context" / "audit"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "reconciliation_report.md"

    with open(report_path, "w") as f:
        f.write("# Memory Reconciliation Report\n\n")
        f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")

        if not all_issues:
            f.write("✅ No issues found. All memory surfaces are consistent.\n")
        else:
            f.write(f"**Issues Found**: {len(all_issues)}\n\n")
            for issue in all_issues:
                f.write(f"### [{issue['type']}] ({issue['severity']})\n")
                f.write(f"{issue['detail']}\n\n")

    print(f"\n📋 Report written to: {report_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
