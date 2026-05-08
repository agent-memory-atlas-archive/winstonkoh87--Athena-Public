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

### External Verification Mandate (Hard Rule)

> **MANDATORY**: Every STANDARD/ULTRA response (Λ ≥ 10) MUST invoke at least ONE external tool before generating output. "External" means anything outside the model's own weights — Exocortex, web search, file reads, MCP calls, grep, or command execution all qualify.
>
> **Rationale**: Training data is stale. The Exocortex holds 1800+ sessions of lived experience. The web holds current facts. Responding from internal knowledge alone when external tools are available is **lazy** and produces lower-quality output.
>
> **Enforcement**:
> - SNIPER queries (Λ < 10): Exempt. Direct answers allowed.
> - STANDARD queries (Λ 10-30): Minimum 1 tool call (Exocortex OR web search OR file read).
> - ULTRA queries (Λ > 30): Minimum 2 tool calls from different sources (e.g., Exocortex + web search, or file read + web search).
> - **Violation**: Responding to a STANDARD/ULTRA query with zero tool calls is an anti-pattern equivalent to ignoring the user's own history and the live state of the world.

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

### Tools (Full Arsenal — All Workflows)

| Tool | When |
|------|------|
| **Exocortex** (`smart_search.py` / `mcp_athena_smart_search`) | **Every STANDARD/ULTRA query.** Searches 1800+ session logs, case studies, protocols, and personal knowledge. This is the user's extended memory. |
| `search_web` | Real-time facts, pricing, documentation, current events. **Training data is stale — always prefer live search.** |
| `read_url_content` | Fast extraction from URLs (docs, articles, references) |
| Browser sub-agent | Visual verification, JS-rendered pages, interactive web content, UI testing |
| `quicksave.py` | After output — save session facts |
| `grep_search` | Exact pattern matching in workspace files |
| MCP Servers | Supabase (database), GitKraken (git ops), Athena (memory system) |
| `generate_image` | Asset generation (never placeholders) |
| Command execution | Scripts, builds, data processing, system operations |

**Mandatory Exocortex Search Triggers** — if ANY of these appear in the query, search FIRST:
- **Names/People**: ANY person mentioned → search their name for relationship history, past interactions
- **Past Decisions**: "Last time...", "What did I decide...", "Didn't we already..." → search the topic
- **Empirical Data**: Pricing, trade history, assignment outcomes, session patterns → search for records
- **Projects/Assignments**: Any project code → search for project context
- **Protocols/Case Studies**: Any system pattern reference → search by keyword

> **Rule**: Failing to search the Exocortex when the data exists is equivalent to ignoring the user's own history. The cost of a redundant search is ~$0. The cost of a hallucinated answer when real data exists is trust erosion.

### Anti-Patterns (Global)

- ❌ Generating code based solely on training data
- ❌ Ignoring existing protocols in `.agent/skills/protocols/`
- ❌ Creating documentation-only artifacts (Action > Docs)
- ❌ Hardcoding metrics — read from source files at runtime
- ❌ Skipping `/start` boot sequence
- ❌ Modifying files owned by other agents (Protocol 413)
- ❌ **Responding from internal knowledge only** when Exocortex, web search, or MCP tools could verify, enrich, or ground the answer. If in doubt, search. The cost of a redundant search is ~$0. The cost of a hallucinated answer is trust erosion.

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
