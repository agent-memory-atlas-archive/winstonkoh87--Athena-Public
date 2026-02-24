# Multi-Model Strategy Guide

> **Last Updated**: 22 February 2026

Athena is model-agnostic — your memory, protocols, and governance persist across any LLM. This means you can use **different models for different tasks** and get the best of each.

This guide provides a practical model routing strategy for users with access to multiple models (e.g., via [Antigravity](https://antigravity.google/), or by switching between IDEs).

---

## Recommended Models & Cost

Athena is **free and open source**. You only pay for your AI subscription. But to get the most out of Athena's structured reasoning, governance protocols, and multi-step workflows — **use frontier (SOTA) models**.

| Plan | Cost | What You Get |
|:-----|:-----|:-------------|
| Claude Pro / Google AI Pro | ~$20/mo | Full access to frontier models. Best value for most users. |
| Claude Max / Google AI Ultra | $200–250/mo | Extended usage limits for power users (8+ hrs/day). |

> [!IMPORTANT]
> **This is a long-term investment, not a cost.** Frontier models dramatically increase your output quality and consistency. Athena's protocols — governance, reasoning depth, structured workflows — are designed for models that can follow complex multi-step instructions. Smaller/free models may struggle to follow them consistently.

**Recommended frontier models for Athena:**

| Model | Strengths | Best Used For |
|:------|:---------|:-------------|
| **Claude Opus 4.6** | Deep reasoning, code quality, nuanced analysis | Coding, architecture, verification |
| **Gemini 3.1 Pro** | Broad knowledge, fast synthesis, strong planning | General work, research, planning |
| **Gemini 3 Flash** | Speed, low cost | Session management (`/start`, `/end`), quick lookups |
| **GPT-5.3** | Alternative perspective, good at creative tasks | Trilateral tiebreaker, creative work |

> [!TIP]
> **The cheapest path to full Athena capability is a single $20/mo subscription** (Claude Pro or Google AI Pro). You don't need multiple subscriptions — one frontier model handles everything. Multiple subs unlock the trilateral feedback loop for high-stakes decisions.

---

## The Routing Table

| Task Type | Recommended Tier | Why |
|:----------|:----------------|:----|
| **Session Management** (`/start`, `/end`, `/save`) | ⚡ Fast (e.g., Gemini Flash) | Mechanical execution, low reasoning needed. Save your premium tokens. |
| **Coding & Implementation** | 🔥 Frontier (e.g., Claude Opus, Gemini Pro) | Code quality scales directly with model capability. |
| **Planning & Architecture** | 🔥 Frontier | Design decisions compound — invest the best reasoning here. |
| **General Chat & Q&A** | 🧠 Strong (e.g., Gemini Pro) | Good enough for most queries. Toggle to Frontier for depth. |
| **Research & Deep Analysis** | 🔥 Frontier | Synthesis quality degrades significantly with weaker models. |
| **Creative & Brainstorming** | 🧠 Strong or 🔥 Frontier | Use Strong for volume generation, Frontier for quality refinement. |
| **Verification & Code Review** | 🔥 Frontier (different model) | Use a *different* model than the one that wrote the code. Fresh eyes catch more bugs. |
| **Quick Lookups & Formatting** | ⚡ Fast | Don't waste Frontier tokens on "reformat this table." |

---

## The Trilateral Feedback Loop

When two models disagree on a significant decision, bring in a third:

```
Model A (e.g., Gemini 3.1 Pro) →  Opinion 1
Model B (e.g., Claude Opus)    →  Opinion 2
                                    ↓
                              Conflict detected?
                                    ↓
Model C (e.g., GPT-5.3, Llama) →  Tiebreaker / Synthesis
```

**When to trigger**:

- Architecture decisions with long-term consequences
- Risk assessments where models disagree on severity
- Strategy choices where both options seem equally valid
- Any decision where the cost of being wrong is high

**When NOT to trigger**:

- Style preferences (just pick one)
- Low-stakes choices (not worth the tokens)
- When one model's answer is clearly more grounded

---

## Cost Optimization

The key insight: **most of your session is NOT frontier-level work.**

| Session Phase | % of Tokens | Model Tier | Cost Impact |
|:-------------|:-----------|:-----------|:------------|
| `/start` boot | ~5% | ⚡ Fast | Minimal |
| Exploration & chat | ~40% | 🧠 Strong | Moderate |
| Core reasoning & coding | ~40% | 🔥 Frontier | Highest |
| `/end` shutdown | ~5% | ⚡ Fast | Minimal |
| Verification | ~10% | 🔥 Frontier (alt) | Moderate |

By routing only the high-value 40% to Frontier models, you can cut effective costs by ~50% while maintaining output quality where it matters.

---

## Model Switching in Practice

### In Antigravity / Multi-Model IDEs

Most modern agentic IDEs let you switch models mid-session:

1. **Start your session** with a Fast model (`/start`, boot scripts)
2. **Switch to Frontier** when you hit complex work (coding, architecture, analysis)
3. **Switch back to Strong/Fast** for routine tasks (formatting, file ops, simple Q&A)
4. **End your session** with Fast (`/end`, shutdown scripts)

### Cross-IDE Validation

For the trilateral loop, you can also use different IDEs entirely:

1. **Primary IDE** (e.g., Antigravity with Gemini 3.1 Pro) — first opinion
2. **Secondary IDE** (e.g., Claude Code with Opus) — second opinion
3. **Tiebreaker** (e.g., ChatGPT, Copilot) — third opinion if needed

Athena's Markdown-based memory means all three IDEs can read the same context.

---

## Anti-Patterns

| ❌ Don't | ✅ Do Instead |
|:---------|:-------------|
| Use Frontier for `/start` and `/end` | Use Fast — it's mechanical work |
| Use Fast for architecture decisions | Use Frontier — design compounds |
| Use one model for everything | Route by task type |
| Skip verification entirely | Use a different model to review critical code |
| Run trilateral loop on every question | Reserve it for high-stakes disagreements |

---

## Quick Reference Card

```
/start, /end, /save       →  ⚡ Fast (Gemini Flash)
Coding, web dev, apps      →  🔥 Frontier (Claude Opus / Gemini 3.1 Pro)
Planning, architecture     →  🔥 Frontier (never Fast)
General chat, Q&A          →  🧠 Strong (Gemini 3.1 Pro), toggle Frontier for depth
Research, deep analysis    →  🔥 Frontier
Verification, code review  →  🔥 Frontier (DIFFERENT model than author)
Conflict resolution        →  🌐 Trilateral Loop (3rd model as tiebreaker)
Quick lookups, formatting  →  ⚡ Fast
```

---

## Further Reading

- [TIPS.md](TIPS.md) — General tips for getting the most out of Athena
- [ARCHITECTURE.md](ARCHITECTURE.md) — How Athena's model-agnostic design works
- [BENCHMARKS.md](BENCHMARKS.md) — Token usage and performance data

---

> *The model is the engine. You choose which gear to drive in.*
