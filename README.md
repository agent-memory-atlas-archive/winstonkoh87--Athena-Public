<div align="center">

# Athena

**An agentic tool to compound your context over time, portable across IDEs.**

*Own the state. Rent the intelligence.* A skeleton for your AI's memory: plain Markdown on your disk, plus a session routine that turns today's work into what tomorrow's session already knows. Any model can read it. You keep it.

[![CI](https://github.com/winstonkoh87/Athena-Public/actions/workflows/ci.yml/badge.svg)](https://github.com/winstonkoh87/Athena-Public/actions/workflows/ci.yml)
[![Version](https://img.shields.io/badge/v10.0.2-10b981?style=flat-square&label=Version)](docs/CHANGELOG.md)
[![PyPI](https://img.shields.io/pypi/v/athena-agent?style=flat-square&color=10b981)](https://pypi.org/project/athena-agent/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/winstonkoh87/Athena-Public?style=flat-square&logo=github)](https://github.com/winstonkoh87/Athena-Public/stargazers)

![20-second demo: /start recalls last session → work → /end](docs/demo.gif)

[Quickstart](#quickstart) · [How It Works](#how-it-works) · [What Moves Between Tools](#what-moves-between-tools) · [Docs](docs/GETTING_STARTED.md) · [Why Athena?](docs/WHY_ATHENA.md) · [Safety](SAFETY.md)

</div>

---

## The Problem

You've spent months teaching ChatGPT how you think. Then a model update resets it, or you switch to Claude, and you're back to zero. Platform memory is opaque, locked to one provider, and stays behind when you leave.

Owning your notes doesn't fix that on its own. A folder of Markdown doesn't get smarter by sitting there. Something has to decide what gets saved, what's still true, and what the next session needs to know first.

Athena does both. The memory lives in files you own, and a fixed routine keeps them current. The model is just whoever's on shift.

| System | Builds up across sessions | Your files, any model |
|:-------|:--------------------------|:----------------------|
| **Platform memory** (ChatGPT, Claude, Gemini) | ✅ | ❌ Tied to one platform |
| **Memory stores** (MCP memory servers, vector DBs) | Save & recall; you supply the method | ✅ |
| **Athena** | ✅ | ✅ |

## Quickstart

```bash
git clone https://github.com/winstonkoh87/Athena-Public.git && cd Athena-Public
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[local]"               # lightweight — no cloud deps
athena init --ide claude                # or: antigravity, cursor, gemini, vscode, kilocode, roocode
athena doctor                           # expect 0 failures
```

Then type `/start` in your IDE's AI chat panel. Work normally. Type `/end` to save.

> **Full install** (cloud sync + reranking): `pip install -e ".[full]"`  
> See [Getting Started](docs/GETTING_STARTED.md) for Windows, advanced config, and Supabase setup.  
> Already have history elsewhere? See [Importing](docs/IMPORTING.md) for ChatGPT, Claude, or Gemini exports.

## How It Works

### The skeleton

Your workspace starts as empty bones. You add the meat by working:

```
.context/
├── memory_bank/
│   ├── userContext.md       # who you are and how you work
│   ├── productContext.md    # what you're building, and why
│   ├── activeContext.md     # where you left off: one checkpoint per session
│   └── systemPatterns.md    # approaches that keep working
├── memories/session_logs/   # one log per session, written by /end
└── CANONICAL.md             # facts you've confirmed are still true
```

### The loop

1. `/start` loads about 2K tokens: who you are, and your last checkpoint.
2. Work normally.
3. `/end` writes the session log, appends a checkpoint to `activeContext.md`, and updates `CANONICAL.md` when something you've confirmed has changed.

Session 50 starts where session 49 stopped. Short on tokens? Skip `/start` and just `/end` (~500 tokens). Planning something big? Use `/ultrastart` (~20K).

### The layers

```
┌─────────────────────────────────────────────────────┐
│  Your IDE (Claude Code / Antigravity / Cursor / …)  │
└───────────────────┬─────────────────────────────────┘
                    │ rules file (all IDEs) + hooks (Claude Code)
                    ▼
┌─────────────────────────────────────────────────────┐
│  Athena SDK                                         │
│  ├── Lifecycle: /start loads ~2K tokens, /end saves │
│  ├── Memory: session logs + canonical facts         │
│  ├── Search: hybrid (keyword + optional vectors)    │
│  └── Guardrails: ruin check, secret scan, grounding │
└───────────────────┬─────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│  Your Disk (plain Markdown — git-versioned)         │
│  └── Optional: Supabase pgvector for cloud sync     │
└─────────────────────────────────────────────────────┘
```

## What Moves Between Tools

Your memory and the `/start`–`/end` routine are Markdown, so they go wherever you go. Guardrails are different: they run as hooks, hooks are tool-specific, and today they're wired in code for Claude Code only. In other tools, the same rules exist as instructions the model is asked to follow, not code that stops it.

| Tool | `athena init --ide` writes | Memory + `/start` / `/end` | Guardrail hooks | Tested |
|:-----|:---------------------------|:---------------------------|:----------------|:-------|
| **Claude Code** | `claude` → `CLAUDE.md` | ✅ | ✅ 4 hooks | ✅ |
| **Antigravity** | `antigravity` → `AGENTS.md` | ✅ | ❌ Rules only | ✅ |
| **Cursor** | `cursor` → `.cursor/rules.md` | ✅ | ❌ Rules only | ✅ |
| **Gemini CLI** | `gemini` → `.gemini/AGENTS.md` | ✅ | ❌ Rules only | ✅ |
| **VS Code + Copilot** | `vscode` → `.vscode/settings.json` | ✅ | ❌ Rules only | ✅ |
| **Kilo Code** | `kilocode` → `.kilocode/rules/athena.md` | ✅ | ❌ Rules only | ✅ |
| **Roo Code** | `roocode` → `.roo/rules/athena.md` | ✅ | ❌ Rules only | ✅ |
| **Codex** | Untested target; reads `AGENTS.md` | 🟡 | ❌ Rules only | ❌ Untested |

The four Claude Code hooks (configured in `.claude/settings.json`): a secret scan before file reads and edits, a ruin check before shell commands, a meta-awareness gate on each prompt, and an output check (math leaks, secrets, Python syntax) before each turn ends.

### What's enforced in code vs. by prompt

> *Most AI-agent READMEs state every claim in the same confident voice. This one doesn't.*

| Claim | Status | Evidence |
|:------|:-------|:---------|
| **Storage & retrieval** — memories stored and surfaced when relevant | ✅ Shipped | Hybrid RAG with cross-encoder rerank, hardened through [production failures](docs/CHANGELOG.md) |
| **Portability** — memory and routine move across models and tools | ✅ Shipped | Plain Markdown; see [What Moves Between Tools](#what-moves-between-tools) |
| **Governed autonomy** — hooks block destructive commands and secrets | 🟡 Claude Code only | Ruin check blocks 14/16 destructive commands; 2 bypasses are [known and tracked](docs/TECH_DEBT.md). Other tools get these rules as prompts |
| **Compounding personalization** — session 500 recalls session 5 | 🟡 N=1 evidence | 1,900+ sessions by the author; no multi-user study |
| **Anti-sycophancy** — personalization doesn't silently increase agreement | 🟡 Partial mitigation | Code-enforced meta-awareness gate (Claude Code only); see [honest limits](docs/ENGINEERING_DEPTH.md) |

> **Why publish this table?** Because the failure mode of this product category is self-mythologizing — describing aspirations in the present tense. Athena's own convention ([Epistemic Status](examples/workflows/_shared.md#epistemic-status-convention-anti-self-mythologizing)) requires labeling every mechanism as `code-enforced`, `agent-discretion`, or `aspirational`. This table is that convention applied to the README.

## Measured, Not Claimed

```bash
# Run the tests yourself
pytest tests/ -v --tb=short

# Run the retrieval evaluator yourself (requires Supabase keys)
python examples/scripts/evaluator.py --gold-set .agent/eval/gold_set.json
```

| Metric | Value | Verification Command |
|:-------|:------|:---------------------|
| **Retrieval Hit@5 (Strict)** | **0.569** (37 / 65) | `python examples/scripts/evaluator.py` |
| **Retrieval MRR@5 (Strict)** | **0.472** | `python examples/scripts/evaluator.py` |
| *Retrieval Hit@5 (Lenient)* | *0.892 (deprecated)* | *Partial substring match (inflated)* |
| **Unit & Integration Tests** | 559 passed (100%) | `pytest tests/` |
| **Secret Leaks (1,248 commits)** | 0 detected | Gitleaks in CI |
| **Code Quality & Lints** | 0 ruff findings | `ruff check src/` |

> **Anti-Goodhart Invariant**: Why did our reported Hit@5 shift from 0.89 to 0.57? Lenient substring matchers count partial word overlaps as "hits," inflating benchmark scores by ~36% without improving retrieval. We killed the lenient matcher because vanity metrics mask regressions. See the full breakdown: [Anti-Goodhart Benchmarking in RAG](docs/BENCHMARKS.md#the-anti-goodhart-shift-why-we-published-lower-numbers).

## Documentation

| Doc | What it covers |
|:----|:---------------|
| [Getting Started](docs/GETTING_STARTED.md) | Install, configure, first session |
| [Your First Session](docs/YOUR_FIRST_SESSION.md) | 20-minute guided tutorial |
| [Importing](docs/IMPORTING.md) | Bring in ChatGPT, Claude or Gemini exports |
| [How It Works](docs/ARCHITECTURE.md) | Architecture and search pipeline |
| [Why Athena?](docs/WHY_ATHENA.md) | Philosophy, use cases, cost analysis |
| [Engineering Depth](docs/ENGINEERING_DEPTH.md) | Technical deep dives |
| [CLI Reference](docs/CLI.md) | All commands |
| [FAQ](docs/FAQ.md) | Common questions |
| [Safety](SAFETY.md) | Limitations and responsible use |
| [Changelog](docs/CHANGELOG.md) | Release history |

## Contributing

PRs welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

The codebase uses `ruff` for linting, `pytest` for tests, and CI must pass before merge.

---

<div align="center">

**MIT License** · [Contributing](CONTRIBUTING.md) · [Safety](SAFETY.md) · [Security](docs/SECURITY.md) · [Code of Conduct](CODE_OF_CONDUCT.md)

Built and battle-tested solo across 1,900+ sessions by [Winston Koh](https://winstonkoh87.com).

*Clone it. Boot it. Make it yours.*

</div>
