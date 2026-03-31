---
description: Orchestrate parallel agent swarms using worktrees
created: 2026-02-03
last_updated: 2026-03-31
---

# /swarm — Parallel Agent Orchestration

> **Purpose**: Convert linear "wait time" into parallel "build time".
> **Power Level**: High (Requires M2/M3 Chip for >2 Agents).
> **Protocol**: Protocol 409 (Worktrees) — see `.framework/` for details

---

## 1. The Swarm Architecture

Instead of 1 Agent doing A -> B -> C, we spawn 3 Agents:

- **Agent Alpha**: Frontend (React/Tailwind)
- **Agent Beta**: Backend (Python/FastAPI)
- **Agent Gamma**: QA/Tests (Pytest/Cypress)

## 2. Execution Flow

### Phase 1: The Split (Commander)

User defines the objective.
**Command**:

```bash
# Create isolated environments
.agent/scripts/parallel_session.sh create swarm-fe
.agent/scripts/parallel_session.sh create swarm-be
.agent/scripts/parallel_session.sh create swarm-qa
```

### Phase 2: The Swarm (Build)

You (The Orchestrator) assign tasks to each "Seat" (simulated or real).

> **Note**: In a single-window interface (Antigravity), we simulate this by switching Context Windows or rapidly context-switching between worktrees.
> *True Parallelism requires multiple terminal windows or the `tm` script.*

**Context Switch**:

```bash
cd ../.worktrees/session-swarm-fe
# Build Frontend...
```

### Phase 3: The Convergence (Merge)

When tasks are done, merge back to Main.

```bash
# 1. Commit in worktree
git commit -am "Feat: Frontend complete"
git push origin feature/session-swarm-fe

# 2. Merge in Main
cd ../../Athena
git merge feature/session-swarm-fe
git merge feature/session-swarm-be
```

## 3. Safety Constraints

- **Database**: All swarm agents MUST share the *same* dev database (or mocks) to ensure compatibility.
- **API Contract**: Defines the "Interface" *first*. Backend and Frontend cannot diverge.
  - *Action*: Create `api_spec.json` or `schema.prisma` in Main before splitting.

## 5. Token Budget Allocation (Per Role)

> **Source**: r/ClaudeCode thread (2026-02-27). Insight: treating all agents with one shared budget lets expensive agents (design, research) crowd out cheap ones (linting, tests). Static caps per role force right-sizing.

| Agent Role | Budget Cap | Rationale |
|:-----------|:-----------|:----------|
| **Research / Deep Analysis** | HIGH (unbounded) | Needs full-context reasoning, semantic search, multiple passes |
| **Code Generation** | MEDIUM (~50K tokens/task) | Structured output, bounded by spec |
| **Code Review / QA** | LOW (~20K tokens/task) | Diff-focused, surgical reads |
| **Docs / Formatting** | LOW (~10K tokens/task) | Template-driven, minimal reasoning |

**Rules**:

- Budget is per-task, not per-session. A research agent running 3 tasks gets 3x its cap.
- If an agent exceeds its cap mid-task, it must checkpoint progress to disk before requesting more.
- The Orchestrator (you) can override caps with explicit approval.

## 6. Coordinator Synthesis Discipline (v9.6.5)

> **Source**: Claude Code coordinator system prompt (`coordinatorMode.ts`).
> **Rule**: The Orchestrator MUST synthesize worker findings into a specific spec before delegating implementation. Lazy delegation is an anti-pattern.

### The 4-Phase Workflow

| Phase | Who | Purpose |
|-------|-----|---------|
| Research | Workers (parallel) | Investigate, find files, understand problem |
| **Synthesis** | **Orchestrator ONLY** | Read findings, understand, craft implementation spec |
| Implementation | Workers | Make targeted changes per synthesized spec |
| Verification | Workers (fresh) | Prove code works — not just confirm it exists |

### Anti-Pattern: Lazy Delegation

> **NEVER write "based on your findings" or "based on the research."**
> These phrases delegate understanding to the worker instead of doing it yourself.

```
// ❌ BAD — lazy delegation
"Based on your findings, fix the auth bug"
"The worker found an issue. Please fix it."

// ✅ GOOD — synthesized spec
"Fix the null pointer in src/auth/validate.ts:42. The user field
is undefined when sessions expire. Add a null check before user.id
access — if null, return 401 with 'Session expired'."
```

### Continue vs. Spawn Decision Matrix

| Situation | Action | Why |
|-----------|--------|-----|
| Research explored exact files needing edit | **Continue** worker | Worker already has context |
| Research was broad, impl is narrow | **Spawn fresh** | Avoid exploration noise |
| Correcting a failure | **Continue** | Worker has error context |
| Verifying another worker's code | **Spawn fresh** | Fresh eyes, no assumptions |
| Wrong approach entirely | **Spawn fresh** | Avoid anchoring on failed path |

### Concurrency Safety

- **Read-only tasks** (research) → run in parallel freely
- **Write-heavy tasks** (implementation) → one at a time per file set
- **Verification** → can run alongside implementation on different file areas

### Worker Prompt Requirements

1. Workers can't see the orchestrator's conversation — every prompt must be **self-contained**
2. Include file paths, line numbers, error messages
3. State what "done" looks like
4. Add a purpose statement: "This research will inform X — focus on Y"
5. For implementation: "Run tests and typecheck, then commit and report the hash"
6. For research: "Report findings — do not modify files"
7. For verification: "Prove the code works, don't just confirm it exists"

---

## 7. Trigger Commands

- `/swarm start <objective>` -> Initiates split
- `/swarm status` -> Lists active worktrees
- `/swarm merge` -> Auto-merges all active swarm branches

---

# workflow #swarm #parallel #productivity
