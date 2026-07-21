# DISCIPLINE.md — Stop-Rules for Sustainable Growth

> **Purpose**: Prevent unbounded complexity growth. Every system tends toward bloat unless explicit stop-rules enforce pruning.

---

## The Five Stop-Rules

### Rule 1: No New Tech Without Removing Old Tech
Before adding a new tool, library, or service — identify what it replaces. If it replaces nothing, it's additive complexity. Justify or reject.

### Rule 2: Workflow Cap
Total active workflows must not exceed **24**. To add one, archive one. The archive is not deletion — it's accessible but not loaded.

### Rule 3: Protocol Cap
Total active protocols should stay under **500**. Beyond this, discovery degrades faster than value compounds. Merge similar protocols before creating new ones.

### Rule 4: Context Ceiling
`activeContext.md` must never exceed **80 lines**. When it does, compact the oldest entries to `sessionArchive.md`. This is the most critical stop-rule — context bloat directly degrades boot quality.

### Rule 5: Single Source of Truth
Every fact should exist in exactly **one** canonical location. If a fact appears in multiple files, designate one as truth and make the others reference it. Count discrepancies between files are a code smell.

### Rule 6: Output Over Maintenance
Track the ratio of **output** commits (`feat`/`fix` — things the system now does for the user) to **maintenance** commits (`chore`/`docs`/`refactor`/`style`/…). When maintenance exceeds **70%** of a rolling two-week window, the system is grooming its own map room instead of shipping. The next commit must be output or a deletion — not another reorganization.

> The failure mode this catches: a system that *feels* productive (commits every day) while producing nothing the user can use. Inventory is not leverage.

---

## Enforcement

> ~~These are human rules first. Automation can help after the rules are internalized.~~

**Update (April 2026)**: The "human discipline first" hypothesis was tested and **failed**. In the private workspace, all five rules were simultaneously violated within 30 days of adoption. The lesson: **aspirational rules don't survive contact with shipping pressure.**

Rules 1-3 and the Version Meta-Rule are now mechanically enforced via a `pre-commit` hook. The hook:

- **Blocks** commits if version strings diverge across `pyproject.toml`, `README.md`, `CHANGELOG.md`, and `AGENTS.md`
- **Blocks** commits if protocol count exceeds the cap (unless the commit message contains `RETIRES: <protocol_name>`)
- **Warns** if workflow count exceeds the target (hard-blocks above a ceiling)
- **Logs** any override to `decisionLog.md` for 30-day review

A reference implementation is at `scripts/hooks/pre-commit` (see below). The evaluation harness (`tests/test_eval_harness.py`) provides CI-level verification.

```bash
# Install the pre-commit hook
cp scripts/hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

### The Output-Over-Maintenance Gate (Rule 6, commit-msg)

Rule 6 shipped advisory first — `scripts/maintenance_ratio.py` printed the ratio every session. It was ignored: in the private workspace the ratio sat at **83% maintenance** while the number was dutifully generated and changed nothing. Same lesson as the version and cap rules above — **a readout you can skip is not a control.**

It is now a `commit-msg` hook that **blocks a maintenance-class commit when the trailing-14-day ratio already exceeds 70%.** Output work (`feat`/`fix`) and the session-logging heartbeat (`chore(session)`) are never gated, and a conscious `ATHENA_GATE_OVERRIDE=1` keeps it a *choice*, not a wall (see Override Protocol below). Reference implementation: `scripts/maintenance_ratio.py --gate` + `scripts/hooks/commit-msg`.

```bash
# Measure
python3 scripts/maintenance_ratio.py --days 14
# Enforce
cp scripts/hooks/commit-msg .git/hooks/commit-msg && chmod +x .git/hooks/commit-msg
```

---

## The Meta-Rule

> **No version bump without updating every public surface in the same commit.**

This prevents the most common failure mode: `pyproject.toml` says v9.8.0, `README.md` says v9.5.7, `CHANGELOG.md` has no entry. The pre-commit hook catches this automatically.

---

## Override Protocol

Overrides are allowed. But they require:
1. Writing the override rationale in `decisionLog.md`
2. Setting a review date (max 30 days) to evaluate whether the override was correct
3. Adding `DISCIPLINE_OVERRIDE` to the commit message (logged automatically)

If you override more than twice per quarter, the rules need revision — not more overrides.

---

## Philosophy

> "The goal is not to accumulate protocols. The goal is to have the *right* protocols, discoverable at the *right* time."

Complexity is not a feature. Leverage is.
