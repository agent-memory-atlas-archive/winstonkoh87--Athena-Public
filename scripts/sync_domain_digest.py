#!/usr/bin/env python3
"""
Domain Digest Bridge — the "report-up" channel for a multi-domain agent
=======================================================================
A life or business runs across several repos — finance, health, a travel/ops
folder, a project journal — each its own source of truth. Pulling every one into
context by hand doesn't scale, and their state goes stale the moment you stop
looking.

This reads the state files of each external domain repo (a PARA *Area* — ongoing,
no finish line) and writes a compact, freshness-stamped DIGEST into the hub's
indexed memory (`.context/domains/<name>/`). The vector layer embeds those
digests, so a cross-cutting question retrieves current cross-domain state without
manually loading each folder.

Closes two failure modes of the hub-and-spoke:
  - Staleness   : the digest stamps SOURCE mtimes, so retrieval shows its own age.
  - Evaporation : state lands in the hub by RUNNING this (wire it into session
                  close), not by remembering to.

Design:
  - Digest = state SUMMARY (head of the state files), never raw data / dashboards.
  - Deterministic. No LLM, no network. Safe to run on every session start/close.
  - Add a domain = ONE entry in DOMAINS below. Scales to the ~5-7 canonical life
    areas (Work, Health, Finance, Relationships, Growth), not to infinity.

Edit DOMAINS to point at your own repos before use.

Usage:
    python3 sync_domain_digest.py                # all registered domains
    python3 sync_domain_digest.py --domain finance
"""

import argparse
import datetime as dt
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOMAINS_DIR = PROJECT_ROOT / ".context" / "domains"

# --- The domain registry. One entry per external life-area repo (spoke). ------
#     Point `repo` at your own domain folders; these are illustrative.
DOMAINS = [
    {
        "name": "finance",
        "label": "Personal Finance",
        "repo": Path.home() / "repos" / "finance",
        "files": ["core/CASH_POSITIONS.md", "core/BURN_RATE.md", "core/NET_POSITION.md"],
        "head": 60,
    },
    {
        "name": "travel",
        "label": "Travel / Operations",
        "repo": Path.home() / "repos" / "travel",
        "files": ["SPEC.md", "CHANGELOG.md"],
        "head": 45,
    },
]


def _mtime(p: Path) -> str:
    try:
        return dt.datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d")
    except OSError:
        return "missing"


def _head(p: Path, n: int) -> str:
    try:
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return "_(unreadable)_"
    body = "\n".join(lines[:n])
    if len(lines) > n:
        body += f"\n\n… (+{len(lines) - n} more lines — see source file)"
    return body


def build_digest(domain: dict) -> str:
    repo = domain["repo"]
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    present = [(f, repo / f) for f in domain["files"] if (repo / f).exists()]
    freshness = ", ".join(f"{Path(f).name} ({_mtime(p)})" for f, p in present) or "none"

    out = [
        "---",
        f"name: domain-digest-{domain['name']}",
        f"domain: {domain['label']}",
        f"source_repo: {repo}",
        f"generated: {now}",
        "generator: scripts/sync_domain_digest.py",
        "kind: report-up-digest",
        "---",
        "",
        f"# Domain Digest — {domain['label']}",
        "",
        "> **Report-up snapshot** of an external life-area repo (a PARA *Area*), "
        "mirrored into the hub's memory so retrieval can surface current "
        "cross-domain state without loading the folder.",
        f"> **Source**: `{repo}`",
        f"> **Digest generated**: {now}",
        f"> **Source freshness**: {freshness}",
        "> ⚠️ Snapshot, not live. If a source date above looks old, the repo may "
        "have moved on — re-run `sync_domain_digest.py`.",
        "",
    ]

    if not present:
        out.append("_No source files found — check the registry paths in "
                   "`sync_domain_digest.py`._")
        return "\n".join(out) + "\n"

    for f, p in present:
        out.append(f"## {f}  _(modified {_mtime(p)})_")
        out.append("")
        out.append(_head(p, domain["head"]))
        out.append("")
        out.append(f"↳ full source: `{p}`")
        out.append("")

    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate domain digests for the hub's memory.")
    ap.add_argument("--domain", help="only this domain (default: all registered)")
    args = ap.parse_args()

    targets = [d for d in DOMAINS if not args.domain or d["name"] == args.domain]
    if not targets:
        known = ", ".join(d["name"] for d in DOMAINS)
        print(f"No domain '{args.domain}'. Known: {known}")
        return 1

    for d in targets:
        dest_dir = DOMAINS_DIR / d["name"]
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / "DIGEST.md"
        dest.write_text(build_digest(d), encoding="utf-8")
        status = "source ok" if d["repo"].exists() else "source not found (edit DOMAINS)"
        print(f"✅ {d['name']:10s} → {dest.relative_to(PROJECT_ROOT)}  ({status})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
