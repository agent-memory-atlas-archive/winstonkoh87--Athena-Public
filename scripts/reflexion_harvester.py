#!/usr/bin/env python3
"""
reflexion_harvester.py — Failure-Delta Mining for Reflexion Memory (Protocol 515)

Closes the loop that session telemetry opens. Claude Code transcripts record every
tool call and its result, including failures. The model self-corrects within a
session, but that lesson dies when the session ends — the next session re-makes the
same mistake (wrong path, wrong binary, permission retry).

This script mines the raw `~/.claude/projects/*Project-Athena*/` transcripts, finds
every FAILED tool call, correlates it with the NEXT SUCCESSFUL call of the same tool,
and treats the delta as the lesson. It emits ready-to-file [REFLEXION] entries.

Stolen idea: `headroom learn` (chopratejas/headroom). Re-implemented native, stdlib-only,
no compression layer, no prefix-cache risk, no external dependency. We take the one
genuinely novel piece — failure→fix delta persistence — and drop the rest.

Usage:
    python3 .agent/scripts/reflexion_harvester.py                 # dry-run (prints only)
    python3 .agent/scripts/reflexion_harvester.py --top 15        # show more recurring failures
    python3 .agent/scripts/reflexion_harvester.py --min-count 3   # only patterns seen 3+ times
    python3 .agent/scripts/reflexion_harvester.py --apply         # append to ledger (default: off)

Output:
    stdout report (failure taxonomy + resolved deltas + proposed REFLEXION lines)
    .agent/state/reflexion_ledger.md  (only with --apply)

Read-only by default. --apply NEVER touches MEMORY.md or CLAUDE.md (those stay
hand-curated); it writes only to the dedicated mechanical ledger.
"""

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / ".agent" / "state" / "reflexion_ledger.md"
PROJECTS_BASE = Path.home() / ".claude" / "projects"
PROJECT_GLOB = os.environ.get("ATHENA_PROJECT_GLOB", "*")  # narrow via env for multi-project ~/.claude

# Forward window (tool calls) to look for the fix after a failure, same session.
FIX_WINDOW = 15
# Min Jaccard token overlap between failed input and candidate fix to count as related.
REL_THRESHOLD = 0.18

# Volatile substrings scrubbed so recurring failures collapse into one signature.
SCRUBBERS = [
    (re.compile(r"/[^\s'\"]+"), "<PATH>"),          # absolute paths
    (re.compile(r"\b[0-9a-f]{7,40}\b"), "<HASH>"),   # git hashes / hex ids
    (re.compile(r"\bline \d+\b", re.I), "line <N>"),
    (re.compile(r":\d+\b"), ":<N>"),                  # :42 line refs
    (re.compile(r"\b\d{2,}\b"), "<N>"),               # bare multi-digit numbers
    (re.compile(r"toolu_[A-Za-z0-9]+"), "<TOOLID>"),
]


def project_dirs():
    """All Claude-history dirs for this project (main repo + any worktrees)."""
    if not PROJECTS_BASE.exists():
        return []
    return sorted(d for d in PROJECTS_BASE.glob(PROJECT_GLOB) if d.is_dir())


def iter_records(jsonl_path):
    with open(jsonl_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def content_blocks(rec):
    msg = rec.get("message")
    if not isinstance(msg, dict):
        return []
    content = msg.get("content")
    return content if isinstance(content, list) else []


def input_signature(tool, inp):
    """Human-readable one-liner of what a tool call was trying to do."""
    if not isinstance(inp, dict):
        return str(inp)[:200]
    if tool == "Bash":
        return (inp.get("command") or "").strip()
    for k in ("file_path", "path", "pattern", "url", "query", "command"):
        if inp.get(k):
            return str(inp[k]).strip()
    return json.dumps(inp, ensure_ascii=False)[:200]


# Failures that are collateral, not lessons: when one call in a parallel batch
# errors, Claude Code cancels its siblings and marks them is_error. Not a real bug.
NOISE_MARKERS = ("cancelled: parallel tool call", "interrupted by user")

# Lines that signal the *actual* error in multi-line Bash output (stdout precedes them).
ERROR_MARKERS = re.compile(
    r"(no such file|command not found|permission denied|exit code|traceback"
    r"|fatal:|error:|denied by|cannot |not a git|syntax error|: line \d+:)",
    re.I,
)


def is_real_failure(text):
    low = (text or "").lower()
    return not any(m in low for m in NOISE_MARKERS)


def scrub(text):
    out = text
    for rx, repl in SCRUBBERS:
        out = rx.sub(repl, out)
    return out.strip()


def error_line(tool, text):
    """Pick the line that actually carries the error.

    Bash mixes stdout with stderr; the error is usually a trailing line matching a
    known marker, not the first line (which is often a benign `echo` header).
    """
    lines = [ln for ln in (text or "").splitlines() if ln.strip()]
    if not lines:
        return text or ""
    if tool == "Bash":
        # "Exit code N" is a wrapper, not the error — drop it so the real stderr surfaces.
        bare_exit = re.compile(r"^exit code \d+\.?$", re.I)
        informative = [ln for ln in lines if not bare_exit.match(ln.strip())]
        pool = informative or lines
        marked = [ln for ln in informative if ERROR_MARKERS.search(ln)]
        if marked:
            return marked[-1].strip()
        return pool[-1].strip()  # stderr typically trails
    return lines[0].strip()      # Read/Edit/etc. emit a single clean message


def error_signature(tool, err_text):
    """Collapse a raw error into a stable, groupable signature."""
    text = err_text if isinstance(err_text, str) else json.dumps(err_text)
    line = error_line(tool, text)
    low = line.lower()
    # Common high-signal classes first.
    if "no such file or directory" in low or "does not exist" in low:
        return f"{tool}: file/dir does not exist"
    if "command not found" in low:
        return f"{tool}: command not found"
    if "permission" in low and "denied" in low:
        return f"{tool}: permission denied"
    if "has not been read yet" in low or "must be read" in low:
        return f"{tool}: edit/write before read"
    if "string to replace not found" in low or "no occurrences" in low:
        return f"{tool}: edit string not found"
    if "exceeds maximum allowed tokens" in low:
        return f"{tool}: output too large (needs offset/limit)"
    if "unknown skill" in low:
        return f"{tool}: unknown skill name"
    if "traceback" in low:
        return f"{tool}: python traceback"
    return f"{tool}: {scrub(line)[:80]}"


def tokens(s):
    return set(re.findall(r"[A-Za-z0-9_.\-/]+", s.lower()))


def jaccard(a, b):
    ta, tb = tokens(a), tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def delta(failed, fixed):
    """Word-level description of what changed between failed and fixed inputs.

    Word-level (not char-level) so the diff stays legible — char diffs shred words
    into fragments like `C ONICAL -> GE TS`.
    """
    if failed == fixed:
        return "identical input — a plain retry succeeded (transient/race)"
    fa, fb = failed.split(), fixed.split()
    sm = SequenceMatcher(None, fa, fb)
    removed, added = [], []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op in ("replace", "delete"):
            removed += fa[i1:i2]
        if op in ("replace", "insert"):
            added += fb[j1:j2]
    r = " ".join(removed)[:90]
    a = " ".join(added)[:90]
    if r and a:
        return f"`{r}` → `{a}`"
    if a:
        return f"added `{a}`"
    if r:
        return f"removed `{r}`"
    return "(reordered)"


def harvest():
    """Returns (failure_counter, resolved_deltas, totals)."""
    failures = Counter()              # error_signature -> count
    failure_examples = {}             # error_signature -> example input sig
    resolved = []                     # list of dicts: sig, failed, fixed, delta, tool
    total_calls = 0
    total_failures = 0
    sessions = 0

    for pdir in project_dirs():
        for jsonl in pdir.glob("*.jsonl"):
            sessions += 1
            # Pass 1: build ordered tool-call timeline + result map for this session.
            calls = []                # ordered: {id, tool, sig, idx}
            results = {}              # tool_use_id -> {is_error, text}
            for rec in iter_records(jsonl):
                for b in content_blocks(rec):
                    if not isinstance(b, dict):
                        continue
                    if b.get("type") == "tool_use":
                        calls.append({
                            "id": b.get("id"),
                            "tool": b.get("name"),
                            "sig": input_signature(b.get("name"), b.get("input")),
                            "idx": len(calls),
                        })
                    elif b.get("type") == "tool_result":
                        c = b.get("content")
                        text = c if isinstance(c, str) else json.dumps(c, ensure_ascii=False)
                        results[b.get("tool_use_id")] = {
                            "is_error": bool(b.get("is_error")),
                            "text": text,
                        }

            total_calls += len(calls)

            # Pass 2: correlate failures with the next related same-tool success.
            for i, call in enumerate(calls):
                res = results.get(call["id"])
                if not res or not res["is_error"]:
                    continue
                if not is_real_failure(res["text"]):
                    continue  # parallel-cancellation collateral, not a lesson
                total_failures += 1
                sig = error_signature(call["tool"], res["text"])
                failures[sig] += 1
                failure_examples.setdefault(sig, call["sig"])

                # find the fix
                for j in range(i + 1, min(i + 1 + FIX_WINDOW, len(calls))):
                    cand = calls[j]
                    if cand["tool"] != call["tool"]:
                        continue
                    cand_res = results.get(cand["id"])
                    if not cand_res or cand_res["is_error"]:
                        continue
                    if jaccard(call["sig"], cand["sig"]) < REL_THRESHOLD:
                        continue
                    resolved.append({
                        "tool": call["tool"],
                        "sig": sig,
                        "failed": call["sig"],
                        "fixed": cand["sig"],
                        "delta": delta(call["sig"], cand["sig"]),
                    })
                    break

    totals = {
        "sessions": sessions,
        "calls": total_calls,
        "failures": total_failures,
        "fail_rate": (total_failures / total_calls * 100) if total_calls else 0.0,
        "resolved": len(resolved),
    }
    return failures, failure_examples, resolved, totals


def reflexion_lines(failures, examples, resolved, min_count):
    """Turn recurring failure signatures into [REFLEXION] entries (P515 format).

    Where a failure was paired with a fix, the most common delta becomes the
    concrete lesson (the delta *is* the lesson). Otherwise fall back to a generic
    'verify before calling' note.
    """
    # Most common delta per signature.
    deltas_by_sig = defaultdict(Counter)
    for r in resolved:
        if r["delta"] and not r["delta"].startswith("(") and "identical" not in r["delta"]:
            deltas_by_sig[r["sig"]][r["delta"]] += 1

    lines = []
    for sig, count in failures.most_common():
        if count < min_count:
            continue
        ex = examples.get(sig, "")
        ex = (ex[:64] + "…") if len(ex) > 64 else ex
        top_delta = deltas_by_sig[sig].most_common(1)
        if top_delta:
            lesson = f"Fix seen: {top_delta[0][0]}"
        else:
            lesson = "Recurs across sessions — verify the target exists/spelling before calling."
        lines.append(
            f"[REFLEXION] What failed: {sig} (×{count}). Example: `{ex}`. {lesson}"
        )
    return lines


def main():
    ap = argparse.ArgumentParser(description="Mine Claude Code transcripts for failure→fix lessons (P515).")
    ap.add_argument("--top", type=int, default=10, help="How many recurring failure classes to show.")
    ap.add_argument("--min-count", type=int, default=2, help="Min occurrences to propose a REFLEXION entry.")
    ap.add_argument("--max-deltas", type=int, default=12, help="How many resolved failed→fix deltas to print.")
    ap.add_argument("--apply", action="store_true", help="Regenerate the reflexion ledger (idempotent).")
    ap.add_argument("--if-stale", type=int, metavar="DAYS", default=None,
                    help="With --apply: no-op if the ledger was refreshed within DAYS (for automation).")
    ap.add_argument("--quiet", action="store_true", help="Suppress the stdout report (for background runs).")
    args = ap.parse_args()

    # Self-throttle for automated callers: skip if the ledger is still fresh.
    if args.apply and args.if_stale is not None and LEDGER.exists():
        age_days = (datetime.now(timezone.utc).timestamp() - LEDGER.stat().st_mtime) / 86400
        if age_days < args.if_stale:
            if not args.quiet:
                print(f"Ledger refreshed {age_days:.1f}d ago (< {args.if_stale}d). Skipping.")
            return 0

    dirs = project_dirs()
    if not dirs:
        print(f"No transcript dirs found under {PROJECTS_BASE} matching {PROJECT_GLOB!r}.")
        return 1

    failures, examples, resolved, totals = harvest()
    lines = reflexion_lines(failures, examples, resolved, args.min_count)

    if not args.quiet:
        print("─" * 70)
        print("REFLEXION HARVEST — Claude Code failure-delta mining (P515)")
        print("─" * 70)
        print(f"Transcript dirs : {len(dirs)}")
        print(f"Sessions        : {totals['sessions']}")
        print(f"Tool calls      : {totals['calls']}")
        print(f"Failures        : {totals['failures']}  ({totals['fail_rate']:.1f}% of calls)")
        print(f"Resolved deltas : {totals['resolved']}  (failure → same-tool fix paired)")
        print()
        print(f"TOP {args.top} RECURRING FAILURE CLASSES")
        print("─" * 70)
        for sig, count in failures.most_common(args.top):
            bar = "█" * min(count, 30)
            print(f"  {count:>3} {bar}  {sig}")
        print()
        if resolved:
            print(f"RESOLVED FAILED → FIX DELTAS (showing up to {args.max_deltas})")
            print("─" * 70)
            seen = set()
            shown = 0
            for r in resolved:
                key = (r["sig"], r["delta"])
                if key in seen:
                    continue
                seen.add(key)
                print(f"  [{r['tool']}] {r['sig']}")
                print(f"      {r['delta']}")
                shown += 1
                if shown >= args.max_deltas:
                    break
            print()
        print(f"PROPOSED REFLEXION ENTRIES (failures seen ≥{args.min_count}×): {len(lines)}")
        print("─" * 70)
        for ln in lines:
            print(f"  {ln}")
        print()

    if args.apply:
        # Idempotent regenerate (like telemetry_report.py) — NOT append. Safe to
        # run every session; the ledger always reflects current cumulative lessons.
        LEDGER.parent.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        body = [
            "# Reflexion Ledger",
            "",
            "> Auto-generated by `reflexion_harvester.py` — regenerated each run, do NOT hand-edit.",
            "> Mines `~/.claude` transcripts for failed→fixed tool-call deltas (P515).",
            "> Promote durable lessons to MEMORY.md / CLAUDE.md manually.",
            "",
            f"_Last harvest: {stamp} — {totals['failures']} failures / {totals['calls']} calls "
            f"({totals['fail_rate']:.1f}%) across {totals['sessions']} sessions._",
            "",
        ]
        body += [f"- {ln}" for ln in lines] if lines else ["_(no failure class met the threshold)_"]
        LEDGER.write_text("\n".join(body) + "\n", encoding="utf-8")
        if not args.quiet:
            print(f"✅ Regenerated {LEDGER.relative_to(ROOT)} ({len(lines)} entries).")
            print("   (MEMORY.md / CLAUDE.md untouched — promote durable lessons manually.)")
    elif not args.quiet:
        print("Dry-run. Re-run with --apply to (re)generate the reflexion ledger.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
