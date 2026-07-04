# Hooks

> **Last Updated**: 5 July 2026

Deterministic scripts that run **outside** the agentic loop on specific events. Zero LLM overhead, guaranteed execution.

Inspired by [shanraisshan/claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice) hooks pattern.

## Available Hooks

| Hook | Event | What It Does |
|:-----|:------|:-------------|
| `pre_compact.py` | Before context compaction | Auto-quicksaves session knowledge before the context window is compacted, preventing knowledge loss |
| `meta_awareness_gate.py` | `UserPromptSubmit` (Claude Code) | Detects socially-loaded prompts (outbound acts, emotionally-hot inbound reads) and injects a meta-awareness gate before the model responds. The code-enforced fix for the `auto-invoke: true` fiction — see note below. |

## Why Hooks Matter: Prose Is Not a Mechanism

A skill's `auto-invoke: true` frontmatter is a *request* to the model, not a guarantee — the model can and does skip it, most often on exactly the prompts where the skill matters. If a doc says "automatically activates" and no code fires it, that claim is **agent-discretion dressed as a mechanism**. Hooks are how you convert the claim into a fact: the harness runs them on every event, regardless of model discretion.

## How Hooks Differ from Workflows

| | Workflows | Hooks |
|:--|:---------|:------|
| **Execution** | Inside the agentic loop (LLM processes) | Outside (deterministic script) |
| **Overhead** | Consumes tokens | Zero token cost |
| **Guarantee** | Best-effort (LLM may skip) | Guaranteed execution |
| **Use case** | Complex multi-step reasoning | Simple, critical automation |

## Creating Your Own Hooks

1. Create a Python script in `.agent/hooks/`
2. The script should be self-contained and fast (< 10s execution)
3. Hook into your workflow scripts to call them at the right time

### Hook Events (Conceptual)

| Event | When |
|:------|:-----|
| `PreCompact` | Before context window compaction |
| `SessionStart` | At `/start` boot |
| `SessionEnd` | At `/end` shutdown |
| `PreCommit` | Before git commit |
| `PostCommit` | After git commit |
