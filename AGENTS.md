# AGENTS.md — Athena Workspace

> **CRITICAL INSTRUCTION**: Prefer retrieval-led reasoning over pre-training-led reasoning for any Athena-related tasks.

This file provides persistent context to any AI coding agent working in this workspace. The information below is available on every turn without needing to be explicitly requested.

---

## Docs Index (Compressed)

> **Canonical counts live in `.agent/config/CAPS.json`** — if numbers in this file diverge, CAPS wins.

```text
[Athena Docs Index]|root: .
|IMPORTANT: Always consult authoritative files before relying on training data.
|.framework/v8.2-stable/modules:{Core_Identity.md,Output_Standards.md,System_Principles.md,Operating_Principles.md,Design_DNA.md}
|.agent/workflows (22):{start.md,end.md,do.md,plan.md,research.md,ultrathink.md,diagnose.md,...}
|examples/workflows (47):{ultrastart.md,ultraend.md,audit.md,battleplan.md,minmax.md,project.md,dream.md,...}
|examples/protocols (169 published examples across 21 categories):{architecture/,decision/,engineering/,quality/,trading/,safety/,...}
|examples/skills (41):{coding/spec-driven-dev,research/deep-research-loop,quality/red-team-review,...}
|.context:{CANONICAL.md,PROTOCOL_SUMMARIES.md,PROTOCOL_HEATMAP.md}
|docs:{ARCHITECTURE.md,SEMANTIC_SEARCH.md,GETTING_STARTED.md,YOUR_FIRST_SESSION.md,FAQ.md}
```

---

## Key Workflows (Slash Commands)

| Command | File | Purpose |
|:--------|:-----|:--------|
| **`/do`** | **`.agent/workflows/do.md`** | **Universal entry point — auto-detects intent and routes** |
| `/start` | `.agent/workflows/start.md` | Boot the agent session |
| `/end` | `.agent/workflows/end.md` | Close session, file insights |
| `/tutorial` | `examples/workflows/tutorial.md` | Guided first-session walkthrough |
| `/ultrastart` | `examples/workflows/ultrastart.md` | System-2 deep boot (~20K tokens) |
| `/ultraend` | `examples/workflows/ultraend.md` | System-2 deep close (synthesis) |
| `/plan` | `.agent/workflows/plan.md` | Create implementation plan |
| `/audit` | `examples/workflows/audit.md` | Zero-blind-spot workspace audit |
| `/research` | `.agent/workflows/research.md` | Deep research workflow |
| `/ultrathink` | `.agent/workflows/ultrathink.md` | Extended reasoning mode |
| `/steal` | `examples/workflows/steal.md` | Pattern extraction from repos |
| `/diagnose` | `examples/workflows/diagnose.md` | Troubleshooting workflow |
| `/fix` | `examples/workflows/fix.md` | Analyze test failures, propose fixes |
| `/minmax` | `examples/workflows/minmax.md` | Token Economy Mode — maximize quality/token |
| `/battleplan` | `examples/workflows/battleplan.md` | Pre-execution battle planning (7 phases) |
| `/project` | `examples/workflows/project.md` | Multi-project switchboard |
| `/dream` | `examples/workflows/dream.md` | Background memory consolidation daemon |
| `/416-agent-swarm` | `examples/workflows/416-agent-swarm.md` | Parallel agent orchestration |
| `/vibe` | `examples/workflows/vibe.md` | Vibe engineering mode — build fast, iterate |
| `/gto` | `examples/workflows/gto.md` | Game-Theory Optimal problem-solving |
| `/save` | `examples/workflows/save.md` | Mid-session checkpoint |
| `/fresh` | `examples/workflows/fresh.md` | Soft Reset — close + reboot |

---

## Core Modules (Load Order)

1. **Core_Identity.md** — Laws #0-6, Committee of Seats
2. **Output_Standards.md** — Formatting, reasoning depth, artifacts
3. **System_Principles.md** — Operational rules, anti-patterns
4. **Operating_Principles.md** — Day-to-day behaviors
5. **Design_DNA.md** — Default aesthetic parameters

---

## Skills Index (5W1H Compliant)

> **IMPORTANT**: Check trigger conditions BEFORE invoking any skill.
> Skills with `context_trigger` frontmatter are **conditional** — dormant until matching files/topics/projects activate them. See [Protocol 530](examples/protocols/architecture/ARC-530-conditional-skill-activation.md).

### Always-On Skills

| Skill | Invoke When... | Path |
| :---- | :------------- | :--- |
| `spec-driven-dev` | User wants to build something — interrogate requirements before coding | `examples/skills/coding/spec-driven-dev/SKILL.md` |
| `deep-research-loop` | User needs multi-source research with structured synthesis | `examples/skills/research/deep-research-loop/SKILL.md` |
| `red-team-review` | User wants adversarial QA on any artifact or plan | `examples/skills/quality/red-team-review/SKILL.md` |
| `context-compactor` | Context window is filling up — compress to stay within token limits | `examples/skills/workflow/context-compactor/SKILL.md` |
| `skill-compiler` | Novel task solved → auto-draft new SKILL.md (Hermes steal) | `examples/skills/workflow/skill-compiler/SKILL.md` |
| `daemon-loop` | Autonomous recurring tasks, background agents, scheduled workflows | `examples/skills/workflow/daemon-loop/SKILL.md` |
| `semantic-search` | Searching Athena's memory/knowledge base (Exocortex embeddings) | `examples/skills/research/semantic-search/SKILL.md` |
| `data-analysis` | Large data dumps (JSON, CSV, Parquet) — DuckDB-powered analytics | `examples/skills/research/data-analysis/SKILL.md` |

### Uber-Skills (Umbrella Consolidations)

> **NEW (2026-05-11)**: 6 Uber-Skills retroactively compiled from 1,900+ sessions. These are dense umbrella consolidations that absorb multiple existing skills/protocols. They auto-trigger on broad domain keywords.

| Skill | Activates On | Absorbs |
|:----- |:------------ |:------- |
| `bionic-decision-engine` | Any "Should I?" question, pricing, tradeoffs, resource allocation | 46 decision + 24 strategy protocols |
| `structural-trading-gate` | Trading, poker, sizing, bankroll, drawdown, commission | trading-risk-gate + zenith-execution + trade-journal-analyzer |
| `sovereign-economics-engine` | Client, pricing, business model, distribution, SEO, content | client-pricing + distribution-physics + brand-foundations |
| `social-physics-filter` | Relationships, boundaries, frustration, IFS, schema work | therapeutic-ifs + consiglieri-protocol |
| `agentic-code-orchestrator` | Code, refactor, data dump, dashboard, academic delivery | data-analysis + spec-driven-dev + statistical-analysis |
| `bionic-safety-net` | Health, finance, burnout, ruin, emergency, circuit breaker | circuit-breaker |

**Full skill metadata**: Each skill contains 5W1H fields (Who, What, When, Where, Why, How) in its frontmatter. Read the SKILL.md before invoking.

---

## Retrieval Strategy

When working on any task in this workspace:

1. **Check `.context/CANONICAL.md`** — materialized view of active facts (Tier 1: universal laws and identity truths)
2. **Load `.context/CANONICAL_TIER2.md`** — when query matches trading, business, psychology, content, architecture, or geo domains
3. **Load `.context/CANONICAL_TIER3.md`** — on explicit request or Exocortex search hit only
4. **Consult `.context/PROTOCOL_SUMMARIES.md`** — protocol overviews and discovery
5. **Consult `.context/PROTOCOL_HEATMAP.md`** — protocol usage frequency and health
6. **Read authoritative files** before generating code from training data

> **Retired indexes**: `TAG_INDEX.md` and `project_state.md` are deprecated. Use `PROTOCOL_SUMMARIES.md` for protocol discovery and `CANONICAL.md` for project state.

---

## Anti-Patterns (Avoid)

- ❌ Generating code based solely on training data
- ❌ Ignoring existing protocols/patterns in `.agent/skills/protocols/`
- ❌ Skipping `/start` boot sequence
- ❌ Not filing insights on `/end`
- ❌ **Responding from internal knowledge alone** when tools are available. Use Exocortex (`mcp_athena_smart_search`), `search_web`, `read_url_content`, MCP servers, `grep_search`, browser sub-agent, and command execution to ground every non-trivial response. Training data is stale — live tools are not.
- ❌ **Fixing a guard without showing it fail** — see *Red Run or It Didn't Happen* below.

### Red Run or It Didn't Happen (hard rule for guard fixes)

> Any change that claims to fix a check, test, gate, linter, or CI step MUST
> include the guard **failing** on the pre-fix state, then passing on the fixed
> state. Put both in the commit message.

If you cannot make it go red, you have not found the guard's edge — you have
found its blind spot, and the fix is aimed at the wrong thing.

This exists because the same failure recurred four times across three separate
agents in one day (2026-07-24/25), each time producing a true-but-misleading
green:

| Guard | Went green by | What it still could not catch |
|:---|:---|:---|
| `sync_version.py` in CI | running the **writer**, which exits 0 always | any version drift |
| `sync_version.py --check` | covering **3 files that already agreed** | drift in 11 other surfaces |
| `test_verify_chunk_integrity` | `assert isinstance(res, bool)` | integrity being broken |
| `test_golden_cases_fire` | `assert len(fired(p)) > 0` | any change in *which* class fires |
| `privacy_scan.py` blocklist | the file **excluding itself** from the scan | 25 disclosures in its own config |

The shared shape: **optimizing the indicator instead of the property.** Green CI,
closed alert, "all consistent", N passed — each statement true, each misleading.
The red run is the cheapest available proof that the indicator is still wired to
the property.

Corollaries:

- **Mutation over assertion count.** Break the thing the guard protects and
  watch it fail. A test that survives the mutation is decoration.
- **A narrowed scope is a silent cap.** If a check covers a subset, it must say
  what it covered and fail on anything undeclared — never print a claim broader
  than what it verified.
- **A skip is not a pass.** Converting an assertion to `pytest.skip` removes the
  guard. Skip on an explicit, named condition, and assert on the other branch.
- **Renaming to clear a static-analysis alert is a dismissal, not a fix.** Do it
  if the name is genuinely wrong, but record it as a false positive rather than
  letting the ledger read "fixed".

### External Verification Mandate

> **MANDATORY (ALL sessions)**: Every non-trivial response MUST invoke at least ONE external tool before generating output. "External" = anything outside the model's weights (Exocortex, web search, file reads, MCP, grep, commands).
>
> The Exocortex indexes **1,900+ sessions** of lived experience. Web search provides real-time facts. Responding without consulting these when they could enrich or verify the answer is equivalent to ignoring the user's own history and the current state of the world.
>
> **Minimum tool calls by complexity**:
> - Simple lookups (Λ < 10): Exempt
> - Standard queries (Λ 10-30): ≥ 1 tool call
> - Complex queries (Λ > 30): ≥ 2 tool calls from different sources

---

## Multi-Agent Safety (Protocol 413)

When multiple AI agents work in this repository simultaneously:

- **Never** `git stash` create/apply/drop — assumes other agents have WIP
- **Never** switch branches or modify worktrees without explicit request
- **Always** `git pull --rebase` before pushing
- **Commit only your changes** — when you see unrecognized files from other agents, ignore them
- **Lint/format diffs** that are formatting-only: auto-resolve without asking
- **Focus reports on your edits** — avoid guardrail disclaimers unless truly blocked

The rules above are the essential subset of Protocol 413 (Multi-Agent Coordination). Customize in `.framework/v8.2-stable/modules/Core_Identity.md`.

---

## Version

- **Framework**: v8.2-stable (frozen as of 2026-02-01 — reference-only, not runtime-loaded)
- **System**: v9.9.8 (public release; see .agent/config/CAPS.json)
- **Last Updated**: 2026-07-22
- **Canonical Counts**: `.agent/config/CAPS.json` (single source of truth)
- **Pattern Source**: Vercel "AGENTS.md vs Skills" Research + OpenClaw Multi-Agent Safety Rules + Claude Code Source Architecture (2026-03-31) + Hermes Agent Steal (NousResearch/hermes-agent, 2026-05-11: skill-compiler, curator lifecycle model) + Karpathy CLAUDE.md Steal (r/ClaudeCode, 2026-06-01: Ask-Don't-Assume, Flag-Uncertainty, Codebase-Documentation-Sync)
