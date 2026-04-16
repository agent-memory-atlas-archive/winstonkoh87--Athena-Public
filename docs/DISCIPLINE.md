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

---

## Enforcement

These rules are tested automatically by the evaluation harness (`tests/test_eval_harness.py`). Violations surface as test failures, not as optional suggestions.

---

## Philosophy

> "The goal is not to accumulate protocols. The goal is to have the *right* protocols, discoverable at the *right* time."

Complexity is not a feature. Leverage is.
