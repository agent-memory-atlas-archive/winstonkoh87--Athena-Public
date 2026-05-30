---
description: Universal entry point — auto-detects intent and routes to the right workflow
created: 2026-04-12
last_updated: 2026-04-12
---
# /do — Intent Router

> **Philosophy**: One command to rule them all. The user shouldn't need to memorize 60+ slash commands.
> **Stolen from**: santifer/career-ops single entry point pattern (2026-04-12)

## Trigger

User says `/do` followed by a natural language description of what they want.

```
/do research the competitor landscape for [ClientCo]
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

3. **Confirm** the detected route (one line):
   > `🎯 Routing to /research — "competitor landscape for [ClientCo]"`

4. **Execute** the matched workflow by reading its file and following its instructions.

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
