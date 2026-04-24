---
description: Read-only workspace diagnostics + structured debugging protocol
created: 2025-12-18
last_updated: 2026-03-21
---
# /diagnose v2.0 — Workspace Diagnostics & Debugging

> **Latency Profile**: MEDIUM (~3-5 min scan, variable debug)
> **Philosophy**: "See everything. Investigate before fixing."
> **Use Case**: Quick health check OR structured root-cause debugging.
> **Steal Source**: Iron Law + 3-Strike Gate from [garrytan/gstack `/investigate`](https://github.com/garrytan/gstack) (CS-544)

> [!IMPORTANT]
> ## Iron Law (v2.0)
> **NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST.**
> Fixing symptoms creates whack-a-mole debugging. Every fix that doesn't address root cause makes the next bug harder to find. Find the root cause, then fix it.

---

## Phase 0: Dependency Check (~5s)

// turbo

```bash
python3 -c "from supabase import create_client; print('✅ Supabase SDK OK')" 2>/dev/null || echo '⚠️ Missing supabase - run: pip install supabase'
```

> **Gate**: If dependencies missing, warn but continue.

---

## Phase 1-3: Parallel Diagnostics (~60s)

> **Goal**: Run all read-only scans. Use orchestrator for fastest execution.

// turbo

```bash
python3 .agent/scripts/diagnose.py
```

**What it runs**:

1. Dependency check (supabase, dotenv)
2. Batch audit (orphans, links)
3. Structure map
4. Echo chamber check

**Analysis** (from logs):

- **Orphans**: `/tmp/diag_batch.log`
- **Structure**: `/tmp/diag_structure.log`
- **Secrets**: `/tmp/diag_secrets.log`
- **Protocol Usage**: `/tmp/diag_protocols.log`

---

## Phase 4: Echo Chamber Check (~10s)

> **Goal**: Detect if AI is just agreeing with everything.

// turbo

```bash
DISAGREE_COUNT=$(grep -rciE "actually|incorrect|disagree|not quite|I'd push back" .context/memories/session_logs/*.md 2>/dev/null | tail -10 | awk -F: '{s+=$2} END {print s+0}')
echo "🔍 Disagreement signals in last 10 sessions: $DISAGREE_COUNT"
if [ "$DISAGREE_COUNT" -lt 3 ]; then
  echo "⚠️ ECHO CHAMBER RISK: <3 disagreements detected. Challenge more."
else
  echo "✅ Healthy dialectic: $DISAGREE_COUNT disagreement signals."
fi
```

---

## Phase 5: Fragility Audit (~2 min)

> **Goal**: Identify single points of failure.
> **Mode**: `// manual`

**Checklist**:

1. **Script Dependencies**: Which scripts break the workflow if they fail?
2. **File Dependencies**: Which files, if deleted, cause cascading failures?
3. **Knowledge Concentration**: Is critical knowledge in only ONE file?
4. **External Dependencies**: Which workflows require external APIs?

---

## Phase 6: Deep Validity Audit (Capped: 15 min)

> **Goal**: Verify key claims. No hallucinations.
> **Mode**: `// manual` — **TIME CAPPED**

1. **Extract** Max 3 claims from recent sessions.
2. **Verify** via `/search` (Max 5 mins per claim).
3. If inaccurate → **DEBUNK & CORRECT**.

---

## Output Summary

> **Rule**: No commits. Report only.

**Confirm**: "✅ /diagnose complete. [X] issues found. [Y] require remediation."

---

## Phase 7: Root Cause Investigation (Active Debugging)

> **Trigger:** `/diagnose` finds an issue, OR user reports a specific bug/error.
> **Mode:** Active — this phase reads AND traces code paths.

1. **Collect symptoms:** Read error messages, stack traces, reproduction steps. If insufficient, ask ONE question at a time.
2. **Read the code:** Trace the code path from symptom back to potential causes. Grep for all references.
3. **Check recent changes:**
   ```bash
   git log --oneline -20 -- <affected-files>
   ```
   Was this working before? What changed? Regression = root cause is in the diff.
4. **Reproduce:** Can you trigger deterministically? If not, gather more evidence.

**Output:** `Root cause hypothesis: [specific, testable claim about what is wrong and why]`

---

## Phase 8: Pattern Analysis

Before fixing, check known pattern signatures:

| Pattern | Signature | Where to Look |
|---------|-----------|---------------|
| Race condition | Intermittent, timing-dependent | Concurrent access to shared state |
| Nil/null propagation | TypeError, KeyError | Missing guards on optional values |
| State corruption | Inconsistent data, partial updates | Transactions, callbacks |
| Integration failure | Timeout, unexpected response | External API calls, service boundaries |
| Configuration drift | Works locally, fails elsewhere | Env vars, feature flags |
| Stale cache | Shows old data | Redis, browser, CDN |
| Path/import error | ModuleNotFoundError | Moved files, circular imports |
| Context drift | AI generates wrong output | Stale CANONICAL, outdated protocol |

Also check:
- `TECH_DEBT.md` for related known issues
- `git log` for prior fixes in same area — **recurring bugs in same files = architectural smell**

---

## Phase 9: Hypothesis Testing (3-Strike Gate)

> **Source:** Adapted from [garrytan/gstack `/investigate`](https://github.com/garrytan/gstack) (CS-544)

Before writing ANY fix, verify your hypothesis:

1. **Confirm:** Add temporary log/assertion at suspected root cause. Run reproduction. Does evidence match?
2. **If wrong:** Return to Phase 7. Gather more evidence. **Do not guess.**
3. **3-Strike Rule:** If 3 hypotheses fail, **STOP**. Escalate:

```
⚠️ 3 hypotheses tested, none confirmed.
This may be an architectural issue rather than a simple bug.

Options:
A) Continue investigating — new hypothesis: [describe]
B) Escalate for human review — needs someone who knows the system
C) Add logging/instrumentation and catch it next occurrence
```

### Red Flags — STOP and Return to Phase 7

> **Source:** Expanded from [obra/superpowers](https://github.com/obra/superpowers) (CS-547)

If you catch yourself thinking any of these, **STOP. Return to Phase 7:**

- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "I don't fully understand but this might work"
- "It's probably X, let me fix that"
- Proposing solutions before tracing data flow
- Each fix reveals new problem in different place
- "One more fix attempt" (when already tried 2+)
- "Add multiple changes, run tests" (can't isolate what worked)
- "Skip the test, I'll manually verify"
- 3+ fixes failed → question the architecture, not the code

### User Signal Detection

Watch for these redirections — they mean your approach is wrong:

| User Says | Means |
|-----------|-------|
| "Is that not happening?" | You assumed without verifying |
| "Will it show us...?" | You should have added evidence gathering |
| "Stop guessing" | Proposing fixes without understanding |
| "We're stuck?" (frustrated) | Your approach isn't working |

**When you see these:** STOP. Return to Phase 7.

### Common Rationalizations

| Excuse | Reality |
|--------|--------|
| "Issue is simple, don't need process" | Simple issues have root causes too. Process is fast for simple bugs. |
| "Emergency, no time for process" | Systematic debugging is FASTER than guess-and-check thrashing. |
| "Just try this first, then investigate" | First fix sets the pattern. Do it right from the start. |
| "I see the problem, let me fix it" | Seeing symptoms ≠ understanding root cause. |
| "Multiple fixes at once saves time" | Can't isolate what worked. Causes new bugs. |
| "I'll write test after confirming fix works" | Untested fixes don't stick. Test first proves it. |
| "One more fix attempt" (after 2+) | 3+ failures = architectural problem. Question pattern, don't fix again. |
| "Reference too long, I'll adapt" | Partial understanding guarantees bugs. Read completely. |

---

## Phase 10: Fix & Verify

> **Gate:** Only enter after Phase 9 confirms root cause hypothesis.

1. **Fix:** Apply the minimum change that addresses root cause.
2. **Verify:** Run reproduction — does the fix resolve the symptom?
3. **Regression check:** Does the fix break anything else?
4. **Document:** Note what was wrong and why in the session log.

---

## Quick Reference

| Command | Effect | Time |
|---------|--------|------|
| `/diagnose` | Read-only diagnostics (Phases 0-6) | ~3-5 min |
| `/diagnose debug` | Full protocol (Phases 0-10) | Variable |
| `/refactor` | Full optimization (calls /diagnose first) | ~10-15 min |
| `/audit` | Cross-model validation | ~5 min |

---

## Tagging

`#workflow` `#automation` `#diagnostics` `#debugging` `#iron-law` `#v2.0`
