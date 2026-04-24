---
description: Quarterly pruning review for CANONICAL.md — surface stale entries, archive or revalidate
---

# /audit-canonical — Canonical Pruning Workflow

> **Cadence**: Quarterly (Jan/Apr/Jul/Oct) or when entry count exceeds 400.
> **Time**: ~15-20 minutes.
> **Policy Source**: Red-Team Audit v4.3 (2026-04-01)

// turbo-all

---

## Step 1: Count Current Entries

Count the total number of data rows in Sections 3 (Active Decisions) and 4 (Strategic Frameworks) of `CANONICAL.md`.

```
grep -c "^|" .context/CANONICAL.md
```

Report: `X entries total. Ceiling: 400. Status: [UNDER/OVER]`

---

## Step 2: Identify Stale Entries

Scan Section 4 (Strategic Frameworks) for entries that reference sessions, dates, or case studies older than 6 months from today.

**Staleness heuristic:**
- Entry references a session from >6 months ago AND has no recent cross-reference in active projects
- Entry describes a market condition that may have changed (pricing, platforms, tools)
- Entry duplicates or is superseded by a newer entry

For each candidate, output:

| # | Entry Name | Original Date | Status | Recommendation |
|---|-----------|--------------|--------|----------------|
| 1 | [name] | [date] | 🔴 >6mo | ARCHIVE / KEEP / UPDATE |

---

## Step 3: User Review

Present the stale entry list to the user. For each entry:
- **ARCHIVE**: Move to `CANONICAL_ARCHIVE.md` with date and reason
- **KEEP**: Re-validate and note "Reviewed [date]" mentally (entry stays)
- **UPDATE**: Modify the entry to reflect current state, then KEEP

**Rule**: User has final say. Do NOT auto-archive without confirmation.

---

## Step 4: Execute Pruning

For each ARCHIVE decision:
1. Copy the full entry row to `CANONICAL_ARCHIVE.md` table
2. Remove the row from `CANONICAL.md`
3. Update `last_updated` date in CANONICAL.md frontmatter

---

## Step 5: Report

Output summary:

```
Canonical Audit Complete
========================
Date: [today]
Before: [X] entries
Archived: [Y] entries
Updated: [Z] entries
After: [X-Y] entries
Ceiling: 350
Next review: [+3 months]
```

---

## Anti-Patterns

- ❌ Auto-archiving without user confirmation
- ❌ Archiving Core Laws (Section 2) or User Profile Truths (Section 5) — these are immutable
- ❌ Deleting entries entirely — always archive to `CANONICAL_ARCHIVE.md`
- ❌ Skipping the review when entry count is under 350 — staleness matters regardless of count
