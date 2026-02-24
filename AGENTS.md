# AGENTS.md — Athena Workspace

> **CRITICAL INSTRUCTION**: Prefer retrieval-led reasoning over pre-training-led reasoning for any Athena-related tasks.

This file provides persistent context to any AI coding agent working in this workspace. The information below is available on every turn without needing to be explicitly requested.

---

## Docs Index (Compressed)

```text
[Athena Docs Index]|root: .
|IMPORTANT: Always consult authoritative files before relying on training data.
|.framework/v8.2-stable/modules:{Core_Identity.md,Output_Standards.md}
|.framework/README.md
|.agent/workflows:{start.md,end.md,plan.md,audit.md,research.md,refactor.md,brief.md,ultrathink.md,steal.md,diagnose.md,416-agent-swarm.md,release-public.md,preset.md}
|.agent/skills/protocols:{000-ultimate-auditor.md,137-graph-of-thoughts.md,139-decentralized-command.md,+300 more in subdirs}
|.context:{project_state.md,CANONICAL.md,TAG_INDEX.md,PROTOCOL_SUMMARIES.md,KNOWLEDGE_GRAPH.md,TECH_DEBT.md}
|docs:{ARCHITECTURE.md,SEMANTIC_SEARCH.md,GETTING_STARTED.md,YOUR_FIRST_SESSION.md,MANIFESTO.md,ABOUT_ME.md,FAQ.md}
```

---

## Key Workflows (Slash Commands)

| Command | File | Purpose |
|:--------|:-----|:--------|
| `/start` | `.agent/workflows/start.md` | Boot the agent session |
| `/end` | `.agent/workflows/end.md` | Close session, file insights |
| `/plan` | `.agent/workflows/plan.md` | Create implementation plan |
| `/audit` | `.agent/workflows/audit.md` | Zero-blind-spot workspace audit |
| `/research` | `.agent/workflows/research.md` | Deep research workflow |
| `/refactor` | `.agent/workflows/refactor.md` | Code refactoring protocol |
| `/ultrathink` | `.agent/workflows/ultrathink.md` | Extended reasoning mode |
| `/steal` | `.agent/workflows/steal.md` | Pattern extraction from repos |
| `/diagnose` | `.agent/workflows/diagnose.md` | Troubleshooting workflow |
| `/416-agent-swarm` | `.agent/workflows/416-agent-swarm.md` | Parallel agent orchestration |

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

| Skill | Invoke When... | Path |
| :---- | :------------- | :--- |
| `moltbook` | User mentions posting to Moltbook, social network for agents | `.agent/skills/moltbook/SKILL.md` |
| `fantasy-framework-detection` | User describes romantic encounter, asks "what does X mean?", inflated probability estimates | `.agent/skills/fantasy-framework-detection/SKILL.md` |
| `moltbook-registry` | User needs to verify agent identity, lookup other agents | `.agent/skills/moltbook-registry/SKILL.md` |

**Full skill metadata**: Each skill contains 5W1H fields (Who, What, When, Where, Why, How) in its frontmatter. Read the SKILL.md before invoking.

---

## Retrieval Strategy

When working on any task in this workspace:

1. **Check `.context/project_state.md`** for current priorities
2. **Grep `.context/TAG_INDEX.md`** for topic → file mappings
3. **Read authoritative files** before generating code
4. **Consult `.context/PROTOCOL_SUMMARIES.md`** for protocol overviews

---

## Anti-Patterns (Avoid)

- ❌ Generating code based solely on training data
- ❌ Ignoring existing protocols/patterns in `.agent/skills/protocols/`
- ❌ Skipping `/start` boot sequence
- ❌ Not filing insights on `/end`

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

- **Framework**: v8.2-stable
- **Last Updated**: 2026-02-21
- **Pattern Source**: Vercel "AGENTS.md vs Skills" Research + OpenClaw Multi-Agent Safety Rules
