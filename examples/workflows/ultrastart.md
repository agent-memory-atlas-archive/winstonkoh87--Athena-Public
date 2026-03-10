---
description: Deep boot for cognitive/computationally intensive work. System-2 counterpart to /start.
created: 2026-03-10
last_updated: 2026-03-10
model: default
temperature: 0.7
tools:
  read: true
  write: true
  bash: true
  search: true
---

# /ultrastart — Deep Context Boot (System-2)

> **Latency Profile**: HIGH (~10-15s boot)  
> **Token Budget**: ≤20K tokens  
> **Philosophy**: Load deep. Reason once.  
> **Use When**: `/ultrathink`, complex multi-domain analysis, architectural decisions, deep research.

> [!IMPORTANT]
> This is NOT the default boot. Use `/start` for general work.
> `/ultrastart` trades speed for epistemic depth. Only invoke when the session
> demands maximum context alignment before reasoning begins.

---

## Token Budget Allocation

| Phase | Content | Budget | Purpose |
|:------|:--------|:-------|:--------|
| 1. Absolute Law | `Core_Identity.md` | ~6.8K | Full laws, identity, RSI, constraints |
| 2. Materialized Truth | `CANONICAL.md` + `PROJECTS.md` | ~6.7K | All active decisions, frameworks, pipeline |
| 3. Recent State | `activeContext.md` (last checkpoint) | ~1K | Current focus, active tasks, system status |
| 4. Semantic Bridge | `smart_search.py` → top 5-7 results | ~5.5K | Task-specific protocols, case studies, skills |
| **Total** | | **≤20K** | |

> **Design Rationale**: Phases 1-3 are *identity-constant* (same every boot). Phase 4 is
> *task-variable* — it's the only phase that changes based on what you're about to do.
> This is where the budget is most valuable, so it gets the largest flexible allocation.

---

## Phase 1: Absolute Law (~6.8K tokens)

// turbo

Load the **complete** `Core_Identity.md`:

```
.framework/v8.2-stable/modules/Core_Identity.md
```

This gives you:

- All 9 Laws (immutable constraints)
- Full identity architecture (not just the header)
- RSI (Recursive Self-Improvement) protocol
- Output standards and communication contract
- The complete risk taxonomy (SNIPER / STANDARD / ULTRA)

**Gate**: If `Core_Identity.md` fails to load → **ABORT**. Do not proceed with partial identity.

---

## Phase 2: Materialized Truth (~6.7K tokens)

// turbo

Load **both** files in parallel:

```
.context/CANONICAL.md
.context/PROJECTS.md
```

This gives you:

- **CANONICAL**: System metrics, Core Laws, all active architectural decisions, strategic frameworks, key references
- **PROJECTS**: Active project switchboard — which projects are live, their status, and current priority

**Gate**: If `CANONICAL.md` fails to load → **WARN** user but continue (degrade gracefully — you still have Core_Identity).

---

## Phase 3: Recent State (~1K tokens)

// turbo

Load `activeContext.md` with the **same surgical extraction** as `/start`:

1. **Header block**: Current Focus + Active Tasks + System Status (up to first `---`)
2. **Last `[[ S__` checkpoint block**: Most recent session summary
3. **Any unclosed session**: If a session wasn't properly closed, include it

> **Why not 3 full sessions?** Recency ≠ Relevance. Yesterday's Carousell pricing session
> is noise when you're doing `/ultrathink` on trading risk. The Semantic Bridge (Phase 4)
> will pull relevant past context *by topic*, not by calendar date.

---

## Phase 4: Semantic Bridge (~5.5K tokens)

This is the **key differentiator** between `/start` (identity-only) and `/ultrastart` (task-aligned).

### Step 1: Determine the Session Objective

The objective is resolved in this priority order:

1. **Explicit**: User provided it inline → `/ultrastart "fixing the trading risk constraints"`
2. **Inferred**: No inline objective → scan `activeContext.md` header for "Current Focus" field
3. **Project-based**: No focus found → use the highest-priority active project from `PROJECTS.md`
4. **Fallback**: Nothing found → **ASK** the user: "What's the objective for this deep session?"

### Step 2: Semantic Search

// turbo

```bash
python3 .agent/scripts/smart_search.py "<resolved objective>" --limit 7 
```

### Step 3: Inject Results

Read the search results. For each result:

- If it's a **protocol** → load the full protocol file
- If it's a **case study** → load the summary section only (not the full narrative)
- If it's a **session log** → load the `@decided` and `@learned` blocks only

**Hard Cap**: Stop loading when cumulative Phase 4 content reaches ~5.5K tokens.
If search returns fewer relevant results, the remaining budget is *not* wasted on filler —
it stays empty. Dense signal > padded context.

---

## Boot Confirmation

After all 4 phases complete, output:

```
🧠 Deep Boot Complete.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Phase 1] Core Identity    ✅  (~6.8K tokens)
[Phase 2] Canonical + Projects  ✅  (~6.7K tokens)
[Phase 3] Recent State     ✅  (~1K tokens)
[Phase 4] Semantic Bridge   ✅  (~X.XK tokens)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total: ~XXK / 20K budget
Objective: "<resolved objective>"
Loaded: <N> protocols, <N> case studies, <N> session insights

⚡ System-2 mode active. All responses default to STANDARD or ULTRA.
```

> **Note**: In `/ultrastart` mode, the SNIPER exemption from Law #6 is **disabled**.
> Every response goes through the full Triple-Lock. If you wanted fast, you'd use `/start`.

---

## Complexity Gate (Safety Valve)

If the user's first query after `/ultrastart` has Λ ≤ 15:

> ⚠️ "This query looks lightweight (Λ = X). You're in deep boot mode — this is
> optimized for complex tasks. Continue here, or switch to `/start` for faster responses?"

This prevents the 20K token cost from being wasted on a simple lookup.

---

## Stability Controls

| Trigger | Action |
|---------|--------|
| `Core_Identity.md` load fails | **ABORT** boot. Report error. |
| `CANONICAL.md` load fails | **WARN** and continue (graceful degradation). |
| `smart_search.py` fails or returns 0 results | Skip Phase 4. Boot with Phases 1-3 only (~14.5K). |
| Context window > 80% after boot | **Do NOT** load Phase 4. Cap at Phases 1-3. |
| User says `/start` after `/ultrastart` | Compact to `/start` footprint (purge Phases 1-2 full loads). |

---

## Tagging

`#workflow` `#boot` `#ultrastart` `#system-2` `#deep-context` `#20k-budget`
