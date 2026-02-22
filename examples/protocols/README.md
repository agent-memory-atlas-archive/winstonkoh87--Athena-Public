# Athena Protocols

> [!NOTE]
> **These are reference implementations from a production AI-agent system (1,100+ sessions).**
>
> Use them to understand the *pattern* — not as prescriptions. Your protocols will reflect your own context, domain, and decision history.
>
> See [Creating Your Own Protocols](#creating-new-protocols) to build yours.

**109 protocols across 13 categories** — battle-tested thinking patterns that standardize how an AI agent reasons.

## Featured Protocols

| ID | Name | Category | Purpose |
|----|------|----------|---------|
| **38** | Synthetic Deep Think | Decision | Multi-layered reasoning with parallel evaluation |
| **47** | BS Detection | Pattern Detection | Systematic identification of unsound reasoning |
| **49** | Efficiency-Robustness Tradeoff | Decision | Navigate speed vs resilience decisions |
| **77** | Adaptive Latency | Architecture | Scale reasoning depth to query complexity |
| **111** | Premise Audit | Decision | Validate assumptions before building on them |
| **130** | Vibe Coding | Engineering | Iterative UI development by "feel" |
| **171** | Cross-Model Validation | Verification | Multi-model consensus checking |
| **193** | Ergodicity Check | Decision | Distinguish time-average from ensemble-average risks |
| **240** | Context Engineering | Engineering | Manage context window efficiently |
| **408** | Autonomous Contribution Engine | Workflow | Transform user insights into contributions |
| **416** | Agent Swarm | Workflow | Parallel multi-agent orchestration |

---

## Categories

### 🧭 Decision (28 protocols)

Decision frameworks, reasoning patterns, multi-criteria analysis, risk assessment, ergodicity, commitment devices.

[Browse Decision Protocols →](decision/)

### 🏗️ Architecture (12 protocols)

System design, token management, context handling, latency architecture, recovery patterns.

[Browse Architecture Protocols →](architecture/)

### ⚙️ Engineering (19 protocols)

Code patterns, TDD, vibe coding, git workflows, context compaction, infrastructure.

[Browse Engineering Protocols →](engineering/)

### 📋 Workflow (17 protocols)

Agentic loops, multi-agent coordination, JIT context, handoff protocols, iteration patterns.

[Browse Workflow Protocols →](workflow/)

### 🔍 Pattern Detection (10 protocols)

Analytical heuristics — BS detection, AI slop detection, form-substance gaps, cynical baseline.

[Browse Pattern Detection Protocols →](pattern-detection/)

### 🧠 Meta (8 protocols)

Protocols about protocols — red team reviews, devil's advocate, self-improvement, auditing.

[Browse Meta Protocols →](meta/)

### 🛡️ Safety (6 protocols)

Risk management, circuit breakers, governance, anti-karason, honesty protocol.

[Browse Safety Protocols →](safety/)

### 🎯 Strategy (6 protocols)

Competitive positioning, min-max optimization, value trinity, ecosystem analysis.

[Browse Strategy Protocols →](strategy/)

### 💻 Coding (5 protocols)

Spec-driven development, semantic search standards, structured decoding, project scaffolding.

[Browse Coding Protocols →](coding/)

### 🔬 Research (3 protocols)

Deep investigation, cyborg methodology, agentic absorption.

[Browse Research Protocols →](research/)

### 🧪 Verification (3 protocols)

Claim atomization, cross-model validation, neuro-symbolic verification.

[Browse Verification Protocols →](verification/)

### 🧩 Reasoning (3 protocols)

Deep thinking, re-reading strategies, senior-principal review.

[Browse Reasoning Protocols →](reasoning/)

### 💾 Memory (3 protocols)

Semantic compression, graph memory architecture, compaction.

[Browse Memory Protocols →](memory/)

---

## Protocol Format

Each protocol follows this structure:

```markdown
---
id: 77
name: Adaptive Latency Architecture
category: architecture
status: active
---

# Protocol 77: Adaptive Latency Architecture

## Purpose
[What problem this solves]

## When to Use
[Trigger conditions]

## Implementation
[Step-by-step process]

## Examples
[Concrete usage examples]
```

## Creating New Protocols

Use the [protocol template](../templates/protocol_template.md) to create new protocols.

Assign the next available ID and add an entry to this index.
