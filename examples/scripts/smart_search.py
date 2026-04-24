#!/usr/bin/env python3
"""
Smart Search (Shim → SDK) with Process-Level Timeout + Grep Fallback.

Delegates to `athena.tools.search`. If the search engine hangs
(e.g., Supabase cold start), the subprocess is killed after TIMEOUT_SECONDS
and a fast grep-based fallback runs automatically.

GTO Fix: 2026-03-26 — Resolves retrieval hang bottleneck.
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path

TIMEOUT_SECONDS = 30
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()

# Paths for grep fallback
CANONICAL_PATH = PROJECT_ROOT / ".context" / "CANONICAL.md"
PROTOCOL_SUMMARIES_PATH = PROJECT_ROOT / ".context" / "PROTOCOL_SUMMARIES.md"
SESSION_LOGS_DIR = PROJECT_ROOT / ".context" / "memories" / "session_logs"
MEMORY_BANK_DIR = PROJECT_ROOT / ".context" / "memory_bank"


# Stopwords for keyword extraction
STOPWORDS = {"the", "and", "for", "is", "in", "to", "of", "a", "an", "on", "at", "by", "or", "not", "it", "be"}


def _extract_keywords(query: str) -> list[str]:
    """Split a multi-word query into individual searchable keywords."""
    return [w for w in query.split() if len(w) >= 2 and w.lower() not in STOPWORDS]


def run_grep_fallback(query: str, limit: int = 10) -> None:
    """Fast grep-based fallback when the full search engine is unavailable.
    
    Splits multi-word queries into individual keywords and greps for each,
    then merges and deduplicates results.
    """
    print(f"\n⚡ FAST FALLBACK: grep-based search for \"{query}\"", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    keywords = _extract_keywords(query)
    if not keywords:
        print("  (No searchable keywords extracted)", file=sys.stderr)
        return

    results = []
    seen = set()

    def _add_unique(tag: str, line: str):
        key = line.strip()[:80]
        if key not in seen:
            seen.add(key)
            results.append(f"[{tag}] {line.strip()}")

    # Build grep pattern: keyword1|keyword2|keyword3 (extended regex OR)
    grep_pattern = "|".join(keywords)

    # 1. Search CANONICAL.md
    if CANONICAL_PATH.exists():
        try:
            proc = subprocess.run(
                ["grep", "-i", "-E", "-n", "-m", "10", grep_pattern, str(CANONICAL_PATH)],
                capture_output=True, text=True, timeout=3,
            )
            if proc.stdout:
                for line in proc.stdout.strip().split("\n"):
                    # Score: count how many keywords hit this line
                    line_lower = line.lower()
                    hits = sum(1 for k in keywords if k.lower() in line_lower)
                    if hits >= min(2, len(keywords)):  # Require 2+ keyword overlap
                        _add_unique(f"CANONICAL({hits}/{len(keywords)})", line)
        except Exception:
            pass

    # 2. Search PROTOCOL_SUMMARIES.md
    if PROTOCOL_SUMMARIES_PATH.exists():
        try:
            proc = subprocess.run(
                ["grep", "-i", "-E", "-n", "-m", "10", grep_pattern, str(PROTOCOL_SUMMARIES_PATH)],
                capture_output=True, text=True, timeout=3,
            )
            if proc.stdout:
                for line in proc.stdout.strip().split("\n"):
                    line_lower = line.lower()
                    hits = sum(1 for k in keywords if k.lower() in line_lower)
                    if hits >= min(2, len(keywords)):
                        _add_unique(f"PROTOCOL({hits}/{len(keywords)})", line)
        except Exception:
            pass

    # 3. Search session log filenames (OR across keywords)
    if SESSION_LOGS_DIR.exists():
        for keyword in keywords[:3]:  # Limit to first 3 keywords for speed
            try:
                proc = subprocess.run(
                    ["find", str(SESSION_LOGS_DIR), "-iname", f"*{keyword.lower()}*",
                     "-type", "f"],
                    capture_output=True, text=True, timeout=3,
                )
                if proc.stdout:
                    for line in proc.stdout.strip().split("\n")[:3]:
                        if line.strip():
                            _add_unique("SESSION", Path(line).name)
            except Exception:
                pass

    # 4. Search memory_bank files
    if MEMORY_BANK_DIR.exists():
        try:
            proc = subprocess.run(
                ["grep", "-rl", "-i", "-E", "-m", "5", grep_pattern, str(MEMORY_BANK_DIR)],
                capture_output=True, text=True, timeout=3,
            )
            if proc.stdout:
                for line in proc.stdout.strip().split("\n"):
                    if line.strip():
                        _add_unique("MEMORY_BANK", Path(line).name)
        except Exception:
            pass

    # 5. Search case_studies directory
    case_studies_dir = PROJECT_ROOT / ".context" / "memories" / "case_studies"
    if case_studies_dir.exists():
        for keyword in keywords[:3]:
            try:
                proc = subprocess.run(
                    ["find", str(case_studies_dir), "-iname", f"*{keyword.lower()}*",
                     "-type", "f"],
                    capture_output=True, text=True, timeout=3,
                )
                if proc.stdout:
                    for line in proc.stdout.strip().split("\n")[:3]:
                        if line.strip():
                            _add_unique("CASE_STUDY", Path(line).name)
            except Exception:
                pass

    # Output results
    if results:
        print(f"\n🏆 FALLBACK RESULTS ({len(results[:limit])} matches):")
        for i, result in enumerate(results[:limit], 1):
            print(f"  {i}. {result}")
        print("-" * 60)
    else:
        print("  (No results found via grep fallback)", file=sys.stderr)


def run_full_search(query: str, limit: int, strict: bool, rerank: bool,
                    debug: bool, json_output: bool, include_personal: bool) -> None:
    """Run the full SDK search engine in a subprocess with a hard timeout."""
    # Build the command to run the SDK search directly
    src_path = str(PROJECT_ROOT / "src")
    cmd = [
        sys.executable, "-c",
        f"""
import sys
sys.path.insert(0, {src_path!r})
from athena.tools.search import run_search
run_search(
    query={query!r},
    limit={limit},
    strict={strict},
    rerank={rerank},
    debug={debug},
    json_output={json_output},
    include_personal={include_personal},
)
"""
    ]

    try:
        proc = subprocess.run(
            cmd,
            timeout=TIMEOUT_SECONDS,
            capture_output=False,  # Let stdout/stderr pass through
            env={**os.environ, "PYTHONPATH": src_path},
        )
        if proc.returncode != 0:
            raise RuntimeError(f"Search exited with code {proc.returncode}")
    except subprocess.TimeoutExpired:
        print(
            f"\n⚠️  Full search timed out after {TIMEOUT_SECONDS}s. "
            "Falling back to grep...",
            file=sys.stderr,
        )
        run_grep_fallback(query, limit)
    except Exception as e:
        print(f"\n⚠️  Full search failed: {e}. Falling back to grep...", file=sys.stderr)
        run_grep_fallback(query, limit)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Athena Smart Search (with timeout + fallback)")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--limit", type=int, default=10, help="Max results")
    parser.add_argument("--strict", action="store_true", help="Suppress low-confidence results")
    parser.add_argument("--rerank", action="store_true", help="Use Cross-Encoder reranking")
    parser.add_argument("--debug", action="store_true", help="Show debug signals")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument(
        "--include-personal", action="store_true",
        help="Include personal domain in results",
    )
    args = parser.parse_args()

    # Governance: Mark search as performed (best-effort)
    try:
        src_path = str(PROJECT_ROOT / "src")
        sys.path.insert(0, src_path)
        from athena.core.governance import get_governance
        get_governance().mark_search_performed(args.query)
    except Exception:
        pass  # Non-blocking

    run_full_search(
        query=args.query,
        limit=args.limit,
        strict=args.strict,
        rerank=args.rerank,
        debug=args.debug,
        json_output=args.json,
        include_personal=args.include_personal,
    )
