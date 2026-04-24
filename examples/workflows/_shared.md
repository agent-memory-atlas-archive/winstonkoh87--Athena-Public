<!-- ============================================================
     SHARED WORKFLOW CONTEXT — Auto-loaded before every workflow.

     This file contains system rules, sources of truth, and
     shared conventions that ALL workflows inherit.

     DO NOT put user-specific data here.
     User identity → User_Profile_Core.md
     User state    → activeContext.md
     User config   → CANONICAL.md
     ============================================================ -->

# Workflow Shared Context

> **Purpose**: Loaded implicitly by any workflow. Reduces duplication across 60+ workflows.
> **Stolen from**: santifer/career-ops `modes/_shared.md` (2026-04-12)
> **Rule**: User customizations in framework modules override defaults here.

---

## Sources of Truth (Load Order)

| Priority | File | When |
|----------|------|------|
| 1 | `.context/memory_bank/activeContext.md` | ALWAYS (current state, active tasks, session thread) |
| 2 | `.context/CANONICAL.md` | ALWAYS (immutable decisions, frameworks, metrics) |
| 3 | `.context/memory_bank/userContext.md` | On identity / psychology / personal-history queries |
| 4 | `.context/PROJECTS.md` | On project / pipeline / "what am I working on" queries |
| 5 | `.context/PROTOCOL_SUMMARIES.md` or `PROTOCOL_HEATMAP.md` | On protocol discovery / file lookup (supersedes retired `TAG_INDEX.md`) |
| 6 | `.context/CASE_STUDY_INDEX.md` | On case-study / precedent lookup |
| 7 | `.context/TECH_DEBT.md` | Before proposing new work, to avoid compounding debt |

### Divergence Resolution (when sources conflict)

Precedence (strongest first):

1. **CANONICAL.md** wins over session logs, case studies, and anything in `.context/memories/`.
2. **activeContext.md** wins over CANONICAL.md **only** for transient session state (active task, in-flight decision). For durable facts, CANONICAL wins.
3. **userContext.md** wins over CANONICAL.md for identity / psychology claims that are user-owned.
4. **DATA_CONTRACT.md** wins over everything for ownership / write-boundary questions.
5. If two files in the same priority tier disagree → raise to the user, do not silently pick one.

### Inventory Counts

Canonical counts (protocols, skills, workflows, scripts) live in `.agent/config/CAPS.json`. Do not trust narrative counts in KNOWLEDGE_GRAPH.md or ARCHITECTURE.md if they diverge from CAPS — CAPS is regenerated from `recount_rules` on demand.

**RULE: CANONICAL.md is the materialized view. If it conflicts with session logs, CANONICAL wins.**
**RULE: activeContext.md checkpoint is the session thread. Never reconstruct state from memory — load the latest checkpoint.**
**RULE: Retired indexes (`project_state.md` at root, `TAG_INDEX.md`) are superseded — do not search for or rely on them.**

---

## Shared Conventions

### Artifact Naming
- Protocols: `NNN-kebab-case.md` (e.g., `528-execution-enforcement.md`)
- Workflows: `kebab-case.md` (e.g., `steal.md`)
- Skills: `kebab-case/SKILL.md` (e.g., `daemon-loop/SKILL.md`)
- Session logs: `YYYY-MM-DD-session-description.md`
- Case studies: `CS-NNN-kebab-case.md`

### Output Quality
- No corporate-speak ("leverage", "synergy", "robust", "seamless")
- Prefer specifics over abstractions
- Cite sources or mark "internal estimate" (Law #5)
- One-session-one-feature (§234)

### Tools (Common)

| Tool | When |
|------|------|
| Exocortex (`smart_search.py`) | Contextual recall (STANDARD/ULTRA queries) |
| `quicksave.py` | After output — save session facts |
| `grep_search` | Exact pattern matching in files |
| Browser sub-agent | Visual verification, web interaction |
| `generate_image` | Asset generation (never placeholders) |

### Anti-Patterns (Global)

- ❌ Generating code based solely on training data
- ❌ Ignoring existing protocols in `.agent/skills/protocols/`
- ❌ Creating documentation-only artifacts (Action > Docs)
- ❌ Hardcoding metrics — read from source files at runtime
- ❌ Skipping `/start` boot sequence
- ❌ Modifying files owned by other agents (Protocol 413)

### Risk Classification (Law #6)

| Level | Λ Score | Protocol |
|:------|:--------|:---------|
| **SNIPER** | < 10 | Direct answer. Search exempt. |
| **STANDARD** | 10-30 | Full Triple-Lock. |
| **ULTRA** | > 30 | Full Triple-Lock + deep reasoning. |

Default = STANDARD. Only SNIPER when **certain** the query is low-risk.

---

> **Integration Note**: This file is **mandatory pre-load** for all workflows.
> Wired into runtime via `AGENTS.md § Workflow Execution` and `/do` Step 0.
> Any agent executing a workflow MUST load this file first.
