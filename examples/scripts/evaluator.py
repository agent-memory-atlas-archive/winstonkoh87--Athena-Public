#!/usr/bin/env python3
"""
evaluator.py — Athena Search Quality Evaluator
================================================
Measures search quality using a golden query set and MRR@K.

Metrics:
    - MRR@5 (Mean Reciprocal Rank at 5): Primary metric.
    - Hit@5: % of queries where at least one expected source appears in top 5.
    - Coverage: % of expected sources found across all results.

Usage:
    python3 .agent/scripts/evaluator.py                  # Full eval
    python3 .agent/scripts/evaluator.py --category system # Filter by category
    python3 .agent/scripts/evaluator.py --verbose         # Show per-query detail
    python3 .agent/scripts/evaluator.py --baseline        # Save current run as baseline
    python3 .agent/scripts/evaluator.py --compare         # Compare against baseline
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Path setup
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SDK_PATH = PROJECT_ROOT / "src"
sys.path.insert(0, str(SDK_PATH))

# Re-exec into a capable interpreter BEFORE measuring anything. An eval run on a
# degraded stack produces numbers that look like a retrieval regression and are
# not one — that is precisely how TD-064 accumulated six unexplained runs.
sys.path.insert(0, str(Path(__file__).parent))
from _venv_bootstrap import ensure_deps  # noqa: E402

_MISSING_DEPS = ensure_deps(PROJECT_ROOT)

# Load environment
try:
    from dotenv import load_dotenv

    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    # Without dotenv the Supabase/Gemini credentials never reach the process and
    # the vector channel dies silently. Never let this pass unremarked.
    print(
        "   ⚠️  python-dotenv missing — .env not loaded; vector retrieval will fail.",
        file=sys.stderr,
    )

GOLDEN_QUERIES_PATH = PROJECT_ROOT / ".agent" / "eval" / "golden_queries.json"
BASELINE_PATH = PROJECT_ROOT / ".agent" / "eval" / "baseline.json"
RESULTS_DIR = PROJECT_ROOT / ".agent" / "eval" / "results"


def load_golden_queries(category: str | None = None) -> list[dict]:
    """Load and optionally filter golden queries."""
    with open(GOLDEN_QUERIES_PATH) as f:
        queries = json.load(f)
    if category:
        queries = [q for q in queries if q.get("category") == category]
    return queries


def run_single_query(query: str, limit: int = 5, rerank: bool = False) -> tuple[list[dict], float]:
    """Run a single search query and return structured results and elapsed time."""
    import io
    import time

    from athena.tools.search import run_search

    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = buffer = io.StringIO()
    sys.stderr = io.StringIO()  # Suppress stderr warnings too

    start = time.time()
    try:
        run_search(query=query, limit=limit, rerank=rerank, json_output=True)
        output = buffer.getvalue()
    except Exception:
        # TimeoutError, connection errors, etc. — return empty results
        output = ""
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr

    elapsed = time.time() - start

    try:
        parsed = json.loads(output) if output.strip() else {}
        # run_search returns {"results": [...], "suppressed": ...}
        if isinstance(parsed, dict):
            return parsed.get("results", []), elapsed
        elif isinstance(parsed, list):
            return parsed, elapsed
        return [], elapsed
    except json.JSONDecodeError:
        return [], elapsed


def _extract_source_identifiers(result: dict) -> set[str]:
    """
    Extract exact source identifiers from a search result.
    Enforces strict matching: filename, stem, and specific artifact names.
    Prohibits loose substring matching and generic type tokens (e.g. 'session', 'case').
    """
    import re

    identifiers = set()
    result_id = result.get("id", "")
    source = result.get("source", "")
    path = result.get("path", "")

    # Clean chunk suffixes like " (Chunk 1)"
    if result_id:
        clean_id = re.sub(r"\s*\(Chunk \d+\)\s*$", "", result_id.strip())
        identifiers.add(clean_id.lower())

        if ": " in clean_id:
            file_part = clean_id.split(": ", 1)[1].strip()
            identifiers.add(file_part.lower())
            identifiers.add(Path(file_part).name.lower())
            identifiers.add(Path(file_part).stem.lower())
        elif ":" in clean_id:
            token = clean_id.split(":")[0].strip().lower()
            if token in ("canonical", "framework", "profile"):
                identifiers.add(token)

    if path:
        p = Path(path)
        identifiers.add(p.name.lower())
        identifiers.add(p.stem.lower())
        # For skill packages named */SKILL.md, register the skill package directory name
        if p.name.lower() == "skill.md":
            identifiers.add(p.parent.name.lower())

    if source:
        identifiers.add(source.lower())

    return identifiers


def compute_reciprocal_rank(
    results: list[dict], expected_sources: list[str], k: int = 5
) -> float:
    """
    Compute Reciprocal Rank: 1/rank of first relevant result.
    Returns 0 if no relevant result in top-K.
    Enforces strict exact-name / stem matching against expected sources.
    """
    for i, result in enumerate(results[:k]):
        identifiers = _extract_source_identifiers(result)

        for expected in expected_sources:
            expected_lower = expected.lower().strip()
            expected_stem = Path(expected_lower).stem

            # Strict exact match: expected filename or stem must exactly equal an extracted identifier
            if expected_lower in identifiers or expected_stem in identifiers:
                return 1.0 / (i + 1)
    return 0.0


def compute_hit(results: list[dict], expected_sources: list[str], k: int = 5) -> bool:
    """True if any expected source appears in top-K results."""
    return compute_reciprocal_rank(results, expected_sources, k) > 0


def compute_coverage(results: list[dict], expected_sources: list[str]) -> float:
    """Fraction of expected sources found anywhere in results."""
    if not expected_sources:
        return 1.0

    found = 0
    all_identifiers = set()
    for result in results:
        all_identifiers.update(_extract_source_identifiers(result))

    for expected in expected_sources:
        expected_lower = expected.lower()
        expected_stem = Path(expected_lower).stem
        for ident in all_identifiers:
            if (
                expected_lower in ident
                or ident in expected_lower
                or expected_stem in ident
            ):
                found += 1
                break

    return found / len(expected_sources)


def run_evaluation(
    category: str | None = None,
    verbose: bool = False,
    k: int = 5,
    rerank: bool = False,
) -> dict:
    """Run full evaluation and return metrics."""
    queries = load_golden_queries(category)

    if not queries:
        print("❌ No golden queries found.")
        return {}

    print("\n🔍 ATHENA SEARCH EVALUATOR")
    print(f"{'─' * 50}")
    print(f"   Golden Queries: {len(queries)}")
    if category:
        print(f"   Category: {category}")
    print(f"   K: {k}")
    if rerank:
        print("   Reranking: Enabled")
    print(f"{'─' * 50}\n")

    rr_scores = []
    hit_scores = []
    coverage_scores = []
    per_query = []
    total_time = 0

    from concurrent.futures import ThreadPoolExecutor

    results_futures = []
    with ThreadPoolExecutor(max_workers=1) as executor:
        for gq in queries:
            results_futures.append(
                (gq, executor.submit(run_single_query, gq["query"], limit=k, rerank=rerank))
            )

    for i, (gq, future) in enumerate(results_futures):
        qid = gq["id"]
        query = gq["query"]
        expected = gq["expected_sources"]

        results, elapsed = future.result()
        total_time += elapsed

        rr = compute_reciprocal_rank(results, expected, k)
        hit = compute_hit(results, expected, k)
        cov = compute_coverage(results, expected)

        rr_scores.append(rr)
        hit_scores.append(1.0 if hit else 0.0)
        coverage_scores.append(cov)

        entry = {
            "id": qid,
            "query": query,
            "expected": expected,
            "rr": rr,
            "hit": hit,
            "coverage": cov,
            "latency_ms": round(elapsed * 1000),
            "num_results": len(results),
            "top_sources": [
                (r.get("id", "") or r.get("source", "") or r.get("path", ""))
                for r in results[:k]
            ],
        }
        per_query.append(entry)

        # Progress indicator
        status = "✅" if hit else "❌"
        if verbose:
            print(
                f'   {status} [{qid}] "{query}" → RR={rr:.2f} Cov={cov:.0%} ({elapsed * 1000:.0f}ms)'
            )
            if not hit:
                print(f"      Expected: {expected}")
                print(f"      Got: {entry['top_sources'][:3]}")
        else:
            # Compact progress
            sys.stdout.write(status)
            sys.stdout.flush()

    if not verbose:
        print()  # Newline after progress dots

    # Compute aggregate metrics
    mrr = sum(rr_scores) / len(rr_scores) if rr_scores else 0
    hit_rate = sum(hit_scores) / len(hit_scores) if hit_scores else 0
    avg_coverage = sum(coverage_scores) / len(coverage_scores) if coverage_scores else 0
    avg_latency = (total_time / len(queries)) * 1000 if queries else 0

    metrics = {
        "mrr_at_k": round(mrr, 4),
        "hit_rate_at_k": round(hit_rate, 4),
        "avg_coverage": round(avg_coverage, 4),
        "avg_latency_ms": round(avg_latency),
        "total_queries": len(queries),
        "k": k,
        "category": category,
        "timestamp": datetime.now().isoformat(),
        "per_query": per_query,
    }

    # Display summary
    print(f"\n{'═' * 50}")
    print("   📊 RESULTS")
    print(f"{'═' * 50}")

    mrr_color = "\033[92m" if mrr >= 0.7 else "\033[93m" if mrr >= 0.5 else "\033[91m"
    hit_color = (
        "\033[92m" if hit_rate >= 0.7 else "\033[93m" if hit_rate >= 0.5 else "\033[91m"
    )
    reset = "\033[0m"

    print(
        f"   MRR@{k}:        {mrr_color}{mrr:.4f}{reset}  {'✅ PASS' if mrr >= 0.7 else '⚠️  BELOW TARGET (0.7)'}"
    )
    print(f"   Hit@{k}:        {hit_color}{hit_rate:.0%}{reset}")
    print(f"   Avg Coverage: {avg_coverage:.0%}")
    print(f"   Avg Latency:  {avg_latency:.0f}ms")
    print(f"   Total Time:   {total_time:.1f}s")
    print(f"{'═' * 50}")

    # Per-category breakdown
    categories = set(gq["category"] for gq in queries)
    if len(categories) > 1:
        print("\n   📁 BY CATEGORY:")
        for cat in sorted(categories):
            cat_rrs = [
                pq["rr"]
                for pq in per_query
                if queries[[q["id"] for q in queries].index(pq["id"])]["category"]
                == cat
            ]
            cat_mrr = sum(cat_rrs) / len(cat_rrs) if cat_rrs else 0
            cat_icon = "✅" if cat_mrr >= 0.7 else "⚠️ " if cat_mrr >= 0.5 else "❌"
            print(f"      {cat_icon} {cat:12s} MRR={cat_mrr:.3f} (n={len(cat_rrs)})")

    # Worst performers
    worst = sorted(per_query, key=lambda x: x["rr"])[:5]
    print("\n   🔻 WORST 5 QUERIES:")
    for w in worst:
        print(f'      [{w["id"]}] RR={w["rr"]:.2f} "{w["query"][:40]}"')

    return metrics


def save_baseline(metrics: dict):
    """Save current metrics as baseline."""
    BASELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(BASELINE_PATH, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"\n💾 Baseline saved → {BASELINE_PATH.name}")


def compare_baseline(metrics: dict):
    """Compare current metrics against saved baseline."""
    if not BASELINE_PATH.exists():
        print("\n⚠️  No baseline found. Run with --baseline first.")
        return

    with open(BASELINE_PATH) as f:
        baseline = json.load(f)

    print(f"\n{'═' * 50}")
    print("   📈 COMPARISON vs BASELINE")
    print(f"   Baseline: {baseline.get('timestamp', 'unknown')}")
    print(f"{'═' * 50}")

    for key in ["mrr_at_k", "hit_rate_at_k", "avg_coverage", "avg_latency_ms"]:
        old = baseline.get(key, 0)
        new = metrics.get(key, 0)
        diff = new - old

        if key == "avg_latency_ms":
            # Lower is better for latency
            arrow = "⬇️ " if diff < 0 else "⬆️ " if diff > 0 else "  "
            color = "\033[92m" if diff <= 0 else "\033[91m"
        else:
            arrow = "⬆️ " if diff > 0 else "⬇️ " if diff < 0 else "  "
            color = "\033[92m" if diff >= 0 else "\033[91m"

        reset = "\033[0m"
        print(
            f"   {arrow} {key:18s}: {old:.4f} → {color}{new:.4f}{reset} ({diff:+.4f})"
        )

    print(f"{'═' * 50}")


def save_results(metrics: dict):
    """Save detailed results for tracking over time."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    outfile = RESULTS_DIR / f"eval_{timestamp}.json"
    with open(outfile, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"📄 Results saved → {outfile.name}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Athena Search Evaluator")
    parser.add_argument("--category", type=str, help="Filter by category")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show per-query details"
    )
    parser.add_argument(
        "--baseline", action="store_true", help="Save current run as baseline"
    )
    parser.add_argument(
        "--compare", action="store_true", help="Compare against baseline"
    )
    parser.add_argument(
        "--k", type=int, default=5, help="Top-K for evaluation (default 5)"
    )
    parser.add_argument(
        "--rerank", dest="rerank", action="store_true", default=True,
        help="Enable Cross-Encoder Reranker (default: on — measures the production path)"
    )
    parser.add_argument(
        "--no-rerank", dest="rerank", action="store_false",
        help="Disable reranker (legacy metric comparison)"
    )
    args = parser.parse_args()

    metrics = run_evaluation(
        category=args.category,
        verbose=args.verbose,
        k=args.k,
        rerank=args.rerank,
    )

    if not metrics:
        sys.exit(1)

    # Always save results
    save_results(metrics)

    if args.baseline:
        save_baseline(metrics)

    if args.compare:
        compare_baseline(metrics)


if __name__ == "__main__":
    main()
