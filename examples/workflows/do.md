---
description: Universal entry point — auto-detects intent and routes to the right workflow
created: 2026-04-12
last_updated: 2026-05-31
---
# /do — Intent Router

> **Philosophy**: One command to rule them all. The user shouldn't need to memorize 60+ slash commands.
> **Stolen from**: santifer/career-ops single entry point pattern (2026-04-12)

## Trigger

User says `/do` followed by a natural language description of what they want.

```
/do research the competitor landscape for [CLIENT]
/do audit the current codebase for tech debt
/do plan the Phase 2 implementation
/do steal patterns from this repo
/do build a landing page for the consulting practice
```

## Execution Flow

0. **Pre-load** `.agent/workflows/_shared.md` — shared conventions, sources of truth, tools reference.

1. **Parse** the user's intent from the natural language input.

2. **Route** using this intent → workflow mapping:

   | Intent Signal | Workflow | Slash Command |
   |:-------------|:---------|:-------------|
   | "research", "find out", "investigate" | Deep Research | `/research` |
   | "plan", "design", "architect" | Planning | `/plan` |
   | "build", "create", "implement", "ship" | Vibe Build | `/vibe` |
   | "audit", "check", "verify", "review" | Audit | `/audit` |
   | "steal", "extract", "copy pattern" | Pattern Extraction | `/steal` |
   | "think", "analyze", "deep dive" | Deep Think | `/ultrathink` |
   | "diagnose", "debug", "fix", "why is" | Troubleshoot | `/diagnose` |
   | "refactor", "clean up", "restructure" | Refactor | `/refactor-code` |
   | "search", "find", "look up" | Web Search | `/search` |
   | "start", "boot", "initialize" | Session Start | `/start` |
   | "end", "close", "wrap up" | Session End | `/end` |
   | "save", "checkpoint" | Mid-session Save | `/save` |
   | "deploy", "publish", "push" | Deploy | `/deploy` |
   | "brief", "scope", "interview" | Pre-prompt Brief | `/brief` |
   | "spec", "specify", "requirements" | Specification | `/spec` |
   | "test", "run tests" | Test Runner | `/test` |
   | "diagram", "visualize", "draw" | Diagram | `/diagram` |
   | "project", "switch", "what am I working on" | Project Switchboard | `/project` |
   | "grill", "challenge", "stress test" | Adversarial Review | `/grill` |
   | "website", "web", "page", "ui" | Web Build | `/web-build` |
   | "brand", "identity", "logo" | Brand Generator | `/brand-generator` |
   | "daemon", "background", "loop" | Daemon Management | `/daemon` |
   | "ads", "ppc", "google ads", "meta ads" | Ads Audit | `/ads` |
   | "data", "analyze data", "csv", "json" | Data Analysis | `/analyze` |
   | "video", "youtube", "short", "reel" | Video Generation | `/video` |
   | "due diligence", "investment", "evaluate deal" | Due Diligence | `/due-diligence` |
   | "archive", "save url", "bookmark" | URL Archive | `/archive` |
   | "preset", "save config", "load config" | Preset Management | `/preset` |
   | "foresight", "predict", "position", "SOTA" | SOTA Foresight Loop | `/foresight` |

3. **Confirm** the detected route (one line):
   > `🎯 Routing to /research — "competitor landscape for [CLIENT]"`

4. **Execute** the matched workflow by reading its file and following its instructions.

## Subagent Delegation Heuristic

> **When**: After routing to a workflow, before executing. Evaluate whether the work should be done inline, parallelized, or delegated.
> **Why**: Subagents compress wall-clock time for independent tasks and keep the parent's context clean. But they add overhead for dependent work. Wrong delegation = slower, not faster.
> **Source**: Empirical patterns from S410–S412 (A30 project closure sequence).

### Decision Matrix

| Condition | Strategy | Rationale |
|:----------|:---------|:----------|
| **Independent file edits** — 2+ files with no cross-dependencies | **Spawn parallel subagents** (one per file) | Wall-clock time = slowest agent, not sum. S412: README + Architecture updated in ~90s parallel vs ~5 min sequential. |
| **Sequential work** — step N depends on step N-1's output | **Do inline** | Subagent can't start until parent finishes prior step. Overhead of launch + message passing > just doing it. |
| **Research that would clutter context** — broad codebase scan, multi-file grep, documentation survey | **Delegate to `research` subagent** | Keeps parent context clean for decision-making. Research agent returns distilled findings. |
| **Batch operations** — 50+ files need the same transform (link-fix, rename, format) | **Spawn a specialized subagent** | S411: link-fixer agent repaired 180 links across 372 files autonomously. Parent handled other tasks in parallel. |
| **Verification after edits** — check that changes are correct | **Do inline** (parent verifies subagent output) | Trust but verify. Parent runs grep/view to confirm subagent didn't introduce errors. |
| **Single file edit** — one file, one change | **Do inline** | Subagent overhead (launch + context load) > just editing the file directly. |
| **Creative/judgment-heavy work** — writing prose, making design decisions | **Do inline** | Subagents execute instructions well but don't make taste decisions. Keep judgment in the parent. |

### Subagent Prompt Rules

When spawning subagents, the prompt MUST include:

1. **Exact file path(s)** — absolute paths, no ambiguity
2. **Specific changes** — line numbers or content targets, not "update the file"
3. **Verification criteria** — how to confirm the edit is correct
4. **Scope boundary** — "Do NOT read AGENTS.md or do any boot sequence" (prevents unnecessary context loading)

### Anti-Pattern: Over-Delegation

> ❌ Don't spawn a subagent for every file in a 3-file edit. If the files are small and changes are simple, inline is faster.
> ❌ Don't spawn subagents for work that requires the parent's accumulated context (e.g., "rewrite this based on what we discussed earlier").
> ❌ Don't spawn more than 4 parallel subagents — diminishing returns on coordination overhead.

## Ambiguous Intent

If intent is unclear or maps to multiple workflows:

> "I detected multiple possible routes:
> 1. `/research` — Deep dive into the topic
> 2. `/plan` — Create an implementation plan
>
> Which fits better, or should I just go with #1?"

## No Match

If nothing matches, treat it as a direct task execution without a workflow wrapper. Just do the thing.

## Anti-Patterns

- ❌ Don't ask "which workflow would you like?" when intent is obvious
- ❌ Don't add overhead — the router should be faster than looking up the command
- ❌ Don't route trivial requests through workflows — if it's a one-liner, just answer

## Tagging

# workflow #automation #router #meta

