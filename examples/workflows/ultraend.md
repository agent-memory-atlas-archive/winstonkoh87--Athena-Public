---
description: Deep close for cognitive/computationally intensive sessions. System-2 counterpart to /end.
created: 2026-03-10
last_updated: 2026-03-10
model: default
temperature: 0.5
tools:
  read: true
  write: true
  bash: true
  search: true
---

# /ultraend — Deep Session Close (System-2)

> **Latency Profile**: HIGH (~2-3 min)
> **Token Budget**: ≤5K synthesis output
> **Philosophy**: Extract maximum learning value. Close once, close right.
> **Use When**: After `/ultrastart` sessions, 5+ decision sessions, weekly reviews, or any session with high insight density.

> [!IMPORTANT]
> This is NOT the default close. Use `/end` for general sessions.
> `/ultraend` trades speed for epistemic depth. Only invoke when the session
> generated enough signal to justify deep synthesis.

---

## Activation Gate

**Auto-suggest `/ultraend`** when ANY of these are true:

| Trigger | Why |
|:--------|:----|
| Session opened with `/ultrastart` | Symmetrical pairing — deep boot deserves deep close |
| 5+ decisions made this session | High decision density = high extraction value |
| New frameworks/axioms discovered | Must propagate to CANONICAL before context is lost |
| Session Λ total ≥ 200 | Heavy cognitive session — lots of signal to compress |
| User explicitly requests | Direct invocation |

If NONE are true → default to `/end`. Don't burn tokens on shallow sessions.

---

## Phase 0: Standard Close (Inherit from /end)

Execute **all steps from `/end` Phase 1B** first:

1. ✅ Write Session Log file
2. ✅ Append Checkpoint to `activeContext.md`
3. ✅ Canonical Check (conditional)
4. ✅ Decision Log Gate
5. ✅ Update Project Switchboard (MANDATORY)
6. ✅ Context Hygiene Gate

> [!TIP]
> Phase 0 is just `/end`. Everything that follows is ADDITIVE.
> If `/ultraend` fails mid-synthesis, you still have a clean `/end` close.

---

## Phase 1: Cross-Session Pattern Scan (~60s)

**What**: Scan the last 5 session logs for recurring themes, unresolved threads, and behavioral patterns.

### Step 1: Load Recent Sessions

```bash
ls -1t .context/memories/session_logs/ | head -5
```

Read the `@decided` and `@pending` blocks from each.

### Step 2: Pattern Detection

Ask yourself these 4 questions:

1. **Recurring Topics**: What theme appeared in 3+ of the last 5 sessions? (Signal: user obsession or unresolved problem)
2. **Orphaned Pendings**: What appeared in `@pending` 3+ sessions ago but never moved to `@decided`? (Signal: stuck or deprioritized)
3. **Decision Reversals**: Did any `@decided` item in this session contradict a previous `@decided`? (Signal: learning or drift)
4. **Velocity Trend**: Are sessions getting more productive (higher Λ/session) or less? (Signal: system health)

### Step 3: File Pattern Report

If any patterns detected, append to session log under a new section:

```markdown
## Cross-Session Patterns

- **Recurring**: [theme] appeared in sessions [N, N-1, N-3]
- **Orphaned**: [pending item] has been pending since session [N-4]
- **Reversal**: [decision] reversed from session [N-2]
- **Velocity**: [trend direction] over last 5 sessions
```

---

## Phase 2: CANONICAL Deep Reconciliation (~60s)

**What**: `/end` does a conditional check ("did this session touch CANONICAL?"). `/ultraend` does a **mandatory deep scan**.

### Step 1: Load CANONICAL.md

Read the full Strategic Frameworks table.

### Step 2: Reconciliation Questions

For each insight from this session:

1. **Is it already in CANONICAL?** → Skip
2. **Does it contradict something in CANONICAL?** → **UPDATE CANONICAL** (truth evolved)
3. **Is it a new framework worth preserving?** → **ADD to CANONICAL**
4. **Is it session-specific noise?** → Skip (not every insight is canonical)

### Step 3: Framework Bundling Check

> **Key Question**: Do the insights from this session form a coherent, named framework?

If 3+ related insights emerged in one session, they may constitute a new **named framework** worth bundling:

- Give it a name (e.g., "Distribution Physics", "Context-Dependence Thesis")
- Write a one-liner that captures the core principle
- Add to CANONICAL Strategic Frameworks

If insights are isolated, file individually.

---

## Phase 3: Reflexion Archive (~30s)

**What**: Explicit post-mortem. What went well, what didn't, what to repeat/avoid.

### Step 1: Ask These 3 Questions

1. **What worked?** — What approach, tool, or decision produced outsized value this session?
2. **What didn't?** — Where did I waste time, backtrack, or produce low-value output?
3. **What's the counterfactual?** — If I could redo this session, what one thing would I change?

### Step 2: File to Session Log

Append to the session log:

```markdown
## Reflexion

- **Worked**: [approach/decision that worked well]
- **Didn't**: [waste/backtrack/mistake]
- **Counterfactual**: [what I'd change if I could redo this session]
```

### Step 3: Anti-Pattern Filing

If the "Didn't" reveals a **repeatable anti-pattern** (not a one-off mistake):

- Check if it already exists in the relevant skill's anti-pattern list
- If new → add it with the real case and fix
- If existing → update the case count

---

## Phase 4: Strategic Portfolio Review (~30s)

**What**: Zoom out. Are we working on the right things?

### Step 1: Load PROJECTS.md

### Step 2: Ask These Questions

1. **Priority Alignment**: Is the highest-EV project getting the most sessions? If not, why?
2. **Stale Projects**: Any project that hasn't been touched in 7+ days? Should it be parked or killed?
3. **Pipeline Health**: Is the ratio of Internal:External projects healthy?
4. **Next Session Suggestion**: Based on everything above, what should the NEXT session focus on?

### Step 3: Update PROJECTS.md

- Advance or regress phases based on findings
- Park stale projects
- Update `Last triaged` timestamp

### Step 4: Seed Next Session

Add to the checkpoint `@pending`:

```
@seeded: [Suggested next session focus based on portfolio review]
```

This gives `/start` or `/ultrastart` a head start on context loading.

---

## Phase 5: Shutdown Orchestrator

```bash
python3 .agent/scripts/shutdown.py
```

Same as `/end` — session compilation, git commit, compliance report.

---

## Output Template

After all phases complete:

```
🧠 Deep Close Complete.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Phase 0] Standard Close      ✅
[Phase 1] Cross-Session Scan  ✅  [N patterns detected]
[Phase 2] CANONICAL Reconcile ✅  [N updates, N new frameworks]
[Phase 3] Reflexion Archive   ✅  [N anti-patterns filed]
[Phase 4] Strategic Review    ✅  [Next: "<seeded focus>"]
[Phase 5] Shutdown            ✅
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Session closed. Time: [HH:MM SGT]
```

---

## Failure Recovery

| Failure | Action |
|:--------|:-------|
| Phase 0 (/end) fails | Fix Phase 0 first. Do not proceed to synthesis. |
| Phase 1-4 fails mid-synthesis | Phase 0 already ran — session is safely closed. Report which synthesis phase failed. |
| `shutdown.py` fails | Fallback: `git add -A && git commit -m "session close" --no-verify`. |
| 2 consecutive failures | **Circuit Breaker**. Stop. Report root cause. |

---

## Quick Reference

| Close Type | Latency | When |
|:-----------|:--------|:-----|
| `/end` (admin) | ~60s | Most sessions |
| `/ultraend` (deep) | ~2-3 min | After /ultrastart, 5+ decisions, weekly reviews |

---

## References

- `/end` — Standard close (Phase 0 source)
- `/ultrastart` — Symmetric deep boot counterpart
- `/save` — Mid-session checkpoint

---

## Tagging

`#workflow` `#automation` `#ultraend` `#system-2` `#deep-synthesis`
