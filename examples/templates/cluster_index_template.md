# Cognitive Cluster Index (Template)

> **What is this?** A routing table that groups related protocols into co-activated bundles. When any protocol in a cluster is triggered, all protocols in that cluster load together — reducing routing overhead and ensuring related capabilities always fire as a unit.
>
> **How to use:** Copy this template to `.agent/CLUSTER_INDEX.md` and customize. Add clusters as your workspace grows.
>
> **Reference:** [Protocol 503: Cognitive Clusters](../protocols/architecture/503-cognitive-clusters.md)

---

## How Clusters Work

```text
WITHOUT CLUSTERS                        WITH CLUSTERS
─────────────────                       ──────────────
Query arrives                           Query arrives
  → Search 5 protocols                    → Match 1 cluster
  → Load 3 individually                   → Load 1 bundle (all 3 pre-grouped)
  → 3 tool calls, ~2,400 tokens           → 1 tool call, ~1,200 tokens
  → Hope they connect                     → Pre-connected by design
```

**Rule of thumb:** If you find yourself loading the same 2-3 protocols together repeatedly, they belong in a cluster.

---

## Starter Clusters

These 3 clusters are built from protocols included in the starter kit. They demonstrate the pattern — build your own as your domains expand.

### 1. Decision Engine 🎯

- **Protocols:** [P115 First Principles](../protocols/decision/115-first-principles-deconstruction.md) + [P75 Synthetic Parallel Reasoning](../protocols/decision/75-synthetic-parallel-reasoning.md) + [P123 Einstein Protocol](../protocols/decision/123-einstein-protocol.md) + [P121 MCDA-EEV](../protocols/decision/121-mcda-eev-framework.md)
- **Triggers:** "analyze", "which should I", "compare options", "think deep", "tradeoff"
- **Why clustered:** Every non-trivial decision benefits from decomposition (P115), multi-path reasoning (P75), forced simplification (P123), and quantified scoring (P121). Loading one without the others is like diagnosing without treating.

### 2. Research Pipeline 🔬

- **Protocols:** [P108 Semantic Search](../protocols/coding/108-semantic-search-standards.md) + [P137 Graph of Thoughts](../protocols/decision/137-graph-of-thoughts.md) + [P327 Iterative Refinement](../protocols/decision/327-iterative-refinement-loop.md)
- **Triggers:** "research", "find out", "deep dive", "rabbit hole", "what do we know about"
- **Why clustered:** Research is retrieval (P108) → structured exploration (P137) → progressive refinement (P327). They're a pipeline — the output of each is the input of the next.

### 3. Quality Gate 🛡️

- **Protocols:** [P175 TDD Workflow](../protocols/engineering/175-tdd-workflow.md) + [P99 Visual Verification](../protocols/engineering/99-visual-verification.md) + [P55 Silent Validator](../protocols/engineering/55-silent-validator.md)
- **Triggers:** "test", "verify", "QA", "does this work", "check my work"
- **Why clustered:** Testing is write tests (P175) → visually confirm (P99) → silently validate assumptions (P55). Skipping any step leaves blind spots.

---

## Co-Activation Chains

Clusters can trigger downstream clusters automatically:

```text
Decision query → #1 Decision Engine → if high stakes → #3 Quality Gate
Research query → #2 Research Pipeline → if actionable → #1 Decision Engine
```

---

## Build Your Own

### When to Create a Cluster

| Signal | Example | Action |
|:---|:---|:---|
| **Co-activation > 60%** | You always load P115 + P75 together | Merge into one cluster |
| **Shared inputs** | 3 protocols all need the same context | Merge — DRY principle |
| **Sequential dependency** | Protocol A's output feeds Protocol B | Merge into pipeline |
| **Same domain, different verbs** | `diagnose`, `classify`, `calibrate` | Merge into phased cluster |

### When NOT to Cluster

| Signal | Example | Keep Separate |
|:---|:---|:---|
| **Cross-domain** | A coding protocol + a therapy protocol | Different contexts entirely |
| **Different frequency** | One fires every session, one fires monthly | Rare items shouldn't bloat common ones |
| **Cluster > 3,000 tokens** | Too many protocols merged | Split into 2 smaller clusters |

### Template for New Clusters

```markdown
### N. [Cluster Name] [Emoji]

- **Protocols:** [P### Name](path) + [P### Name](path)
- **Triggers:** "keyword1", "keyword2", "keyword3"
- **Co-activates:** → Cluster #X when [condition]
- **Why clustered:** [One sentence explaining why these belong together]
```

---

## Metrics

Track these to validate your clustering is working:

| Metric | Target |
|:---|:---|
| Skills covered by clusters | > 80% |
| Avg. protocol loads per query | < 1.5 |
| Orphan protocols (unclustered) | < 20% |
