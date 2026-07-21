# Hooks

> **Last Updated**: 15 July 2026

Deterministic scripts that run **outside** the agentic loop on specific events. Zero LLM overhead, guaranteed execution.

Inspired by [shanraisshan/claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice) hooks pattern.

## Available Hooks

| Hook | Event | What It Does |
|:-----|:------|:-------------|
| `pre_compact.py` | Before context compaction | Auto-quicksaves session knowledge before the context window is compacted, preventing knowledge loss |
| `meta_awareness_gate.py` (v3) | `UserPromptSubmit` (Claude Code) | Domain-general meta-awareness trigger. v3 classifies prompts by **act structure** — T1 inbound-narrative, T2 outbound-commit, T3 third-party-verdict, T4 resource-commitment, T5 felt-evidence — instead of per-domain keywords, so one gate covers relational, financial, consumer, institutional, and broadcast prompts. Injects a question-framed 8-step interpreter kernel (arena → prior → discriminators → sign check → receiver frame → felt≠real → payoff → agency/anti-override). The code-enforced fix for the `auto-invoke: true` fiction — see note below. Tested: `tests/test_meta_awareness_gate.py` (46 cases). |

### v3 design highlights (`meta_awareness_gate.py`)

- **Structure over keywords**: new domains extend your skill content (arena/base-rate tables), never the hook. Mechanism is fixed; domains are data.
- **Question-framed reminder**: "ask, don't tell" phrasing outperforms prohibitions at suppressing agreement bias ([arXiv:2602.23971](https://arxiv.org/abs/2602.23971)).
- **Perspective-first receiver frame**: list what the receiver *observes* (intent stripped) before judging how the act lands — the ordering shown to improve LLM perspective-taking ([SimToM, ACL 2024](https://aclanthology.org/2024.acl-long.451/)).
- **Sign symmetry**: the gate checks both misread directions — inflating (self-flattering) *and* deflating (self-degrading) — the same base-rate error with opposite signs.
- **Agency / anti-override** *(step 8)*: when the model is about to rank or advise, the kernel forces the check "am I weighting by the user's revealed preferences, or substituting my own?" — the guard that keeps partisan loyalty from curdling into paternalism. In an *advisory* frame this is also the condition shown to *strengthen* (not erode) epistemic independence under personalization ([Kelley & Riedl 2026](https://arxiv.org/abs/2603.00024)).
- **Negative guard**: routine-ops prompts (reconciliation, test runs, doc chores) suppress a T4-only fire so maintenance work isn't gated.

### The gate (wired by default in Claude Code)

The repo ships a committed root `.claude/settings.json` that wires this hook by default — **Claude Code asks you to approve it on first open** (project hooks stay untrusted until you say yes). That file contains:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      { "hooks": [ { "type": "command",
                     "command": "python3 \"$CLAUDE_PROJECT_DIR/examples/hooks/meta_awareness_gate.py\"",
                     "timeout": 5 } ] }
    ]
  }
}
```

Other IDEs (Antigravity, Cursor, Gemini CLI) have no `UserPromptSubmit` hook — there the kernel is **agent-discretion**, exactly as the README's [Validation Status](../../README.md#-validation-status--whats-proven-vs-whats-proposed) states.

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
