# Top 10 Protocols (MCDA Ranked)

> **Last Updated**: 5 February 2026  
> **Methodology**: Multi-Criteria Decision Analysis (MCDA)  
> **Criteria**: Portability (25%) | Depth (25%) | Applicability (25%) | Ruin Prevention (25%)

These are the 10 most impactful protocols from the Athena framework, ranked by their ability to improve AI reasoning and user outcomes across any domain.

---

## The Rankings

| Rank | Protocol | Score | Category | One-Liner |
|------|----------|-------|----------|-----------|
| **1** | [Protocol 75: Synthetic Parallel Reasoning](../examples/protocols/decision/75-synthetic-parallel-reasoning.md) | **4.75** | Decision | 4-track reasoning: Domain + Adversarial + Cross-Domain + Zero-Point |
| **2** | [Protocol 115: First Principles Deconstruction](../examples/protocols/decision/115-first-principles-deconstruction.md) | **4.50** | Decision | 55/5 Rule — 11x more time on problem definition than solution |
| **3** | [Protocol 140: Base Rate Audit](../examples/protocols/decision/140-base-rate-audit.md) | **4.50** | Decision | Detect nonsense by comparing claims against statistical baselines |
| **4** | [Protocol 52: Deep Research Loop](../examples/protocols/research/52-deep-research-loop.md) | **4.25** | Research | Causal chain research with gap identification and exhaustiveness checks |
| **5** | [Protocol 96: Latency Indicator (Λ)](../examples/protocols/architecture/96-latency-indicator.md) | **4.25** | Architecture | Self-reported cognitive effort score (Λ+1 to Λ+100) |
| **6** | [Protocol 110: Zero-Point Protocol](../examples/protocols/meta/110-zero-point-protocol.md) | **4.00** | Meta | L7 principle generation — from player → designer → field |
| **7** | [Protocol 133: Query Archetype Routing](../examples/protocols/architecture/133-query-archetype-routing.md) | **4.00** | Architecture | JIT knowledge loading based on query complexity |
| **8** | [Protocol 44: Micro-Commit Protocol](../examples/protocols/engineering/44-micro-commit-protocol.md) | **3.75** | Engineering | Commit every 15 minutes to prevent context loss |
| **9** | [Protocol 28: 3-Second Override](../examples/protocols/engineering/28-three-second-override.md) | **3.75** | Engineering | Break execution immediately when something feels wrong |
| **10** | [Protocol 168: Context-Driven Development](../examples/protocols/architecture/168-context-driven-development.md) | **3.75** | Architecture | Code with embedded context (living documentation) |

---

## MCDA Scoring Breakdown

### Criteria Definitions

| Criterion | Weight | 5 (Best) | 1 (Worst) |
|-----------|--------|----------|-----------|
| **Portability** | 25% | Works in any LLM immediately | Requires Athena SDK |
| **Depth** | 25% | Universal principle (cross-domain) | Narrow tactic (single use) |
| **Applicability** | 25% | Invoked daily | Invoked rarely |
| **Ruin Prevention** | 25% | Directly prevents catastrophic failure | No safety mechanism |

### Top 3 Detailed Scores

| Protocol | Portability | Depth | Applicability | Ruin Prevention | **Total** |
|----------|-------------|-------|---------------|-----------------|-----------|
| **75: Synthetic Parallel Reasoning** | 5 | 5 | 4 | 5 | **4.75** |
| **115: First Principles** | 5 | 5 | 4 | 4 | **4.50** |
| **140: Base Rate Audit** | 5 | 4 | 5 | 4 | **4.50** |

---

## How to Use These Protocols

### For ChatGPT / Claude / Gemini Users

1. **Copy** the protocol markdown file.
2. **Paste** into your conversation as system instructions or context.
3. The AI will adopt the reasoning framework immediately.

### For Athena Users

These protocols are already loaded via `SKILL_INDEX.md`. Invoke by name:

- `/think` → Triggers Protocol 75
- `/research` → Triggers Protocol 52

---

## Cross-References

- [Full Protocol Library](../examples/protocols/) — All 68 protocols
- [Architecture Overview](./ARCHITECTURE.md) — System design
- [Getting Started](./GETTING_STARTED.md) — Setup guide
