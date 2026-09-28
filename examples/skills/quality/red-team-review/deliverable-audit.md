---
name: red-team-review/deliverable-audit
description: "Deliverable Audit mode for red-team-review: isolated fresh-context audit of a built artefact against the brief, with executed lenses L1-L6, evidence-only findings, red-run fixes and stop/oscillation rules. Loaded via the skill's Mode Routing; no context_trigger of its own."
epistemic_status: agent-discretion
---

# Deliverable Audit Mode (red-team-review)

> **Loaded by** `red-team-review` when the target is a **built artefact** that someone will receive or mark: an assignment docx/PDF, report, slides, notebook, code output, or client handoff folder. It is not for arguments or plans; those go to the Strategic Matrix.
> **Epistemic status**: `agent-discretion`. Nothing enforces this. The orchestrating agent has to choose to run it.
> **Origin**: Academic database schema and normalisation deliverable (2026-09-28). Three red-team rounds had signed off 18/18 green. A fresh-context audit then found:
> - 12 of 14 Q3a headings naming the wrong relation, introduced by an earlier audit fix
> - an ERD whose label badges hid its own connector lines
> - an identifier the brief explicitly forbids
> - client guides pointing to files that had moved five days earlier

**Core rule: cut the auditor off from the work's history, not from the spec. Then make it run things, not just read them.**

## Step 0: Build the isolation packet

Copy the packet into a fresh directory **outside the project repo**. Physical isolation beats "please don't read X".

| Include | Exclude |
|:--|:--|
| Brief or question paper, rubric, blank template | The answer key or solution summary (it comes from the same pipeline, so it's a circular oracle) |
| Course materials that define conventions (seminar slides, style guide) | CHANGELOG, earlier audit reports, fix lists (they anchor the auditor on old findings) |
| Raw source data the answers must match | Any "verified", "N/N green" or "100% complete" claims |
| The **final built file**, byte-identical to what the marker receives | Generator scripts and intermediate files on the first pass (the rendered output is what gets marked) |
| A listing of the delivery folder (`ls -R`) plus the handoff docs | The author's session and chat logs |

**Auditor model:** where possible, use a different model family from the one that built the work (Gemini-built work gets a Claude audit, and vice versa). Shared training means shared blind spots. Independent lenses can run as parallel isolated subagents.

## Step 1: Fresh hunt (a round = a declared set of lenses)

Each round states which lenses it ran, and must include at least one lens the previous round didn't use.

| Lens | Method (run things; don't just read) | Sample catch |
|:--|:--|:--|
| **L1 Spec compliance** | List every instruction in the brief, including format rules and "do not" clauses. Map each one to where the artefact satisfies it. | "Without adding any identifier" vs an invented `mutationID`. Q1b's required constraint format missing across the 18-relation schema. |
| **L2 Built artefact** | Open the final file the way the marker will. Parse the docx XML (a docx is a ZIP; never grep it) or render the PDF. Check headings against the content under them, leftover placeholders, images, stray highlights. | 12/14 Q3a headings named the wrong relation. |
| **L3 Execution** | Rerun the code, SQL and notebooks. Regenerate assets and diff them against what's embedded. | The SQL matched the key row for row. L3 also proves what's right. |
| **L4 Data cross-check** | Check each answer against the raw source rows, including NULLs and edge-case rows. | `stepNumber` is NULL for SMP007, yet it's part of the candidate key. |
| **L5 Cross-file and inventory** | Compare the handoff docs and answer key with the artefact, and with the actual folder listing. | Guides named files that had moved to `Archive/`. "17 entities" vs 18. |
| **L6 Marker's read** | Mark it with the rubric as the marker would. What do they notice in the first 60 seconds? Where do marks drop? | The ERD relationship used as Q1b's worked example rendered as broken dashes. |

**Finding format** (no evidence means no finding):

`[SEV] ID · lens · location (file > section/table/line) · evidence (command + output, or exact quote) · what the marker sees · marks at risk · fix hint`

Severity means marks (or users) at risk, not how hard the fix is. End every report with **COVERAGE**: what was checked, what wasn't, and why. A narrowed scope must say so.

## Step 2: Triage (context comes back in here)

The owner, or an agent with full context, accepts or rejects each finding. **Rejections need evidence too.** "Invalid per current state" is not evidence. Log the reason for every rejection.

## Step 3: Fix with a red run

For each accepted finding:
1. Write a check against the **built artefact** that fails right now.
2. Fix it through the pipeline. Never hand-edit generated outputs.
3. Rebuild and confirm the check passes.
4. Put both runs in the commit message.

Check the *property* (each heading matches its table), not the *indicator* (the placeholder is gone).

## Step 4: Regression (not an audit)

Rerun every check after every rebuild. A regression pass never counts as an audit round.

## Step 5: Next round, or stop

- A new round means a new fresh context, a new packet, and at least one new lens.
- **Stop** when a round using a new lens finds only LOW or cosmetic items.
- **Oscillation:** if a round reverses an earlier round's fix (A to B to A), halt and escalate it as a decision, with both arguments laid out. For example, in a database normalisation audit, Q2c's MVD placement flipped from #7 to #2 and back to #7. The working answer was neither.
- **Reviewing a claimed "done":** diff every ticked item against the artefact. Ticking an item by rewording the flagged defect is the most common false pass.

## Anti-patterns (observed in deliverable audits)

| Pattern | What happened | Counter |
|:--|:--|:--|
| Indicator instead of property | Placeholders replaced passed, but the fix itself mislabelled 12/14 headings | Step 3 property checks |
| Regression check called an audit | Round 3's "18/18 green" was a re-check of round 1's list | Keep Step 4 separate from Step 1 |
| Checking the generator, not the render | The ERD data said `identifying: True`, but the PNG showed broken dashes (a label badge covered the line) | L2 on the image itself |
| Answer key as oracle | `mutationID` was "justified" instead of removed | L1 against the brief, with the key excluded |
| Syncing doc content, never the inventory | Guides were updated 4 times after a folder move; the file list was never checked | L5 with `ls` |
| Ticking by rewording | "FD5 + residual" ticked; the hand-wave was reworded and cited the wrong theorem | Step 5 diff |

## Scope

This mode covers correctness, spec compliance and delivery integrity. It does not cover making process evidence (chat logs, screenshots, timestamps, document metadata) look authentic.

## Auditor prompt (paste in along with the packet)

```text
You are auditing a finished deliverable before it reaches a marker. You have only
the files in this folder: [list]. Do not look for or ask for other context.

Hunt for defects that cost marks. Run these lenses: [e.g. L1, L2, L5].
Run things rather than just reading them: open the built file's internals, rerun
any code or SQL, check answers against the raw data, and confirm that every file
the handoff docs name actually exists.

Report each finding as:
[SEV] ID · lens · location · evidence (command + output, or exact quote) ·
what the marker sees · marks at risk · fix hint
No evidence, no finding. Empty categories are fine; don't invent issues.
End with COVERAGE: what you checked, what you did not, and why.
```

Cross-model handoff format: [WFL-247](../../../protocols/workflow/WFL-247-red-team-handoff.md). Pipeline hook: [academic-delivery](../../workflow/academic-delivery/SKILL.md) Step 7.5.
