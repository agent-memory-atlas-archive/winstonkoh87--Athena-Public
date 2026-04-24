---
description: Structured planning protocol for tasks (Plan -> Pre-Mortem -> Verification)
created: 2026-01-06
last_updated: 2026-03-21
---
# Protocol: Structured Task Planning

This workflow enforces a "measure twice, cut once" approach.

## 0. Completeness Principle (Boil the Lake)

> **Source:** Adapted from [garrytan/gstack](https://github.com/garrytan/gstack) (CS-544)

AI-assisted work makes the marginal cost of completeness near-zero. When presenting options:

- If Option A is the complete implementation and Option B is a shortcut that saves modest effort — **always recommend A**. "Good enough" is wrong when "complete" costs minutes more.
- **Lake vs Ocean:** A "lake" is boilable (100% coverage for a module, full feature, all edge cases). An "ocean" is not (rewriting an entire system, multi-quarter migration). **Recommend boiling lakes. Flag oceans as out of scope.**
- **Rate each option:** Add `Completeness: X/10` to every alternative presented.
  - **10** = complete implementation (all edge cases, full coverage)
  - **7** = covers happy path but skips some edges
  - **3** = shortcut that defers significant work
- If both options are 8+, pick higher. If one is ≤5, flag it.

## 0.5 Deployment Tier (Size Before You Start)

> **Source:** Adapted from [msitarzewski/agency-agents NEXUS](https://github.com/msitarzewski/agency-agents) (CS-546)

Before planning, classify the task tier to calibrate depth:

| Tier | Timeline | Scope | Planning Depth |
|------|----------|-------|----------------|
| **Micro** | 1-5 days | Bug fix, single-feature, audit | 1-paragraph plan in chat |
| **Sprint** | 2-6 weeks | Feature build, MVP, multi-file refactor | Full `implementation_plan.md` |
| **Full** | Months+ | Architecture change, new system, migration | Full plan + pre-mortem + alternatives |

**Rule:** If unsure between tiers, size UP (Sprint → Full). Under-planning costs more than over-planning. Micro tasks can skip to Step 1 (Triage).

## 1. Triage: Complexity Check

**ASK:** Is this a "Heavy" or "Lite" task?

* **Lite Task**: Simple bugs, typos, minor UI tweaks ( < 15 mins).
  * **Action**: Write a 1-paragraph summary in the chat.
  * **Proceed**: Go directly to execution.
  * ⚠️ **Even Lite tasks need a stated approach.** "This is too simple to need a design" is the anti-pattern — unexamined assumptions cause the most wasted work on "simple" tasks. The design can be one sentence, but it must exist and be approved. *(CS-547)*
* **Heavy Task**: New features, refactors, architecture changes, high-risk migrations.
  * **Action**: Proceed to Step 2 (Full Protocol).

## 2. Analysis & Mode Switch (Heavy Only)

1. **Stop and Analyze**: Do not rush. Read the user's request and context carefully.
2. **Enter PLANNING Mode**: Use `task_boundary` to switch to `PLANNING` mode.
3. **Check Knowledge**: Check if there are existing Knowledge Items (KIs) or protocols relevant to this task.

## 3. Generate Implementation Plan (Heavy Only)

Create or update `implementation_plan.md`. **MANDATORY:** Apply **Protocol 272 (Harness Engineering)**.
Do not just describe *what* to do. Define the parameters that make the solution inevitable.

```markdown
# [Task Name]

## Goal & Harness (The Box)
> **Protocol 272**: Define the constraints so tightly that execution is trivial.
- **The Constraint Box**: Hard limits (Tech stack, performance, specific styles).
- **The Input**: Starting state (File A, Variable B).
- **The Output**: Exact definition of done (JSON Schema, UI Screenshot, Passing Test).

## User Review Required
Document anything that requires user review or clarification.

## Proposed Changes
List the specific actions or file edits. Group by component/file.
- [Filename]
    - [Action: Create/Edit/Delete]
    - [Details: what changes?]

## Alternatives (MANDATORY for Heavy Tasks)

> **Completeness Principle:** Always include Completeness Score.

At least 2 approaches. One must be "minimal viable" (fastest), one must be "ideal architecture" (best long-term).

| Approach | Summary | Effort | Risk | Completeness |
|----------|---------|--------|------|--------------|
| A: [Name] | [1-2 sentences] | S/M/L | Low/Med/High | X/10 |
| B: [Name] | [1-2 sentences] | S/M/L | Low/Med/High | X/10 |

**RECOMMENDATION:** Choose [X] because [one-line reason].

## Pre-Mortem & Troubleshooting
**Failure Analysis:**
- Point of Failure 1: [What could go wrong?] -> [How to prevent/fix?]
- Point of Failure 2: ...

## Verification Plan
**How will we know it worked?**
- [ ] Command to run: `...`
- [ ] Manual check: ...
```

## 4. Initialize Task Tracking (Heavy Only)

Create or update `task.md` with a granular checklist using IDs.

## 5. Review (Heavy Only)

**STOP.** Do not proceed to execution yet.

* Ask the user to review the plan.
* Only switch to `EXECUTION` mode after approval.

## 6. Deviation Handling

**IF** the plan fails mid-execution:

1. **STOP**. Do not blindly retry more than once.
2. **Report**: Tell the user what failed and why.
3. **Update**: Propose a modified plan.
4. **Confirm**: Wait for user approval before diverting.

---
**Trigger:** When the user says `/plan` or "Make a plan", run this workflow.
