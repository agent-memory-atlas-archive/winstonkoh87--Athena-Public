---
created: 2026-03-01
last_updated: 2026-03-04
description: Athena routing infrastructure — Intent Classifier (P508) → Cognitive Systems (P507) → Cognitive Clusters (P503)
---

# Athena Routing Index

> **Architecture**: Protocols → Skills → Clusters → **Cognitive Systems** → Athena
> **Reference**: [P503: Clusters](../protocols/architecture/503-cognitive-clusters.md) | [P507: Cognitive Systems](../protocols/architecture/507-cognitive-systems.md) | [P508: Intent Classifier](../protocols/architecture/508-intent-classifier.md)

---

## Cognitive Systems (Organ System Layer)

> **Rule**: For queries with Λ ≥ 10, classify at the System level FIRST, then cascade to clusters. For Λ < 10 (SNIPER), skip directly to cluster keyword matching.

| System | Archetype | Cluster Sequence | Triggers |
|---|---|---|---|
| 🛡️ **Survival** | Crisis / ruin prevention | #14 → #3 → #15 → #8 → P506 | Ruin, emergency, crisis, panic, "I lost everything" |
| 🫀 **Life Decision** | Irreversible personal choice | #15 → #7 → #9 → #6 → #8 → P506 | "Should I [irreversible]?", marriage, career pivot, health |
| 📈 **Trading** | Capital deployment | #3 → #4 → #5 → #9 | Trade, position, Kelly, drawdown, risk |
| 🤝 **Social** | Interpersonal dynamics | #15 → #7 → #6 → #8 → P506 | "How do I handle", conflict, relationship, boundary |
| ⚙️ **Execution** | Build / ship / create | #15 → #13 → #11 → #8 | Build, code, ship, implement, assignment |
| 📣 **Growth** | Distribution / audience | #12 → #10 → #11 → #8 | Launch, market, SEO, grow, distribute |
| 📖 **Learning** | Understanding / knowledge | #12 → #9 → #15 → #8 | Teach me, explain, what is, analyze concept |
| 🔄 **Maintenance** | System homeostasis | #1 → #2 → #14 | /diagnose, /audit, /end, health check |

**Priority**: Survival > Life Decision > Trading > Social > Execution > Growth > Learning > Maintenance
**Ambiguous**: Default to Problem-Solving (#15) standalone → re-classify after framing.

**Cross-System Handoffs:**

```text
Life Decision + financial → Trading System (sub-problem)
Execution + repeated failure → Survival System (circuit breaker)
Trading + emotional language → Survival → Social → Inner Work (#7)
Growth + product-market fit doubt → Life Decision (pivot)
Social + irreversible action → Life Decision System
Learning + actionable insight → Execution System
Maintenance + critical failure → Survival System
Any system + ruin signal → IMMEDIATE → Survival System
```

---

## Cluster Map

### 1. Diagnostic Engine ⚙️

- **Capstone**: Protocol 501
- **Skills**: (Self-contained — 9 protocols merged into capstone)
- **Triggers**: "diagnose", "what's wrong", "debug", "root cause", "why is this failing"
- **Domain**: Decision

### 2. Context Lifecycle 📦

- **Capstone**: Protocol 502
- **Skills**: (Self-contained — 4 protocols merged into capstone)
- **Triggers**: "context", "token budget", "compaction", "memory", "context window"
- **Domain**: Architecture

### 3. Trading Risk Gate 🛡️

- **Capstone**: `trading-risk-gate`
- **Skills**: Ruin check (Law #1) + Ergodicity audit + Win-rate dominance validation
- **Triggers**: "should I trade", "risk", "ruin", "ergodicity", "is this safe"
- **Co-activates**: → Cluster 4 (Execution) if trade is approved
- **Domain**: Trading

### 4. Trading Execution ⚡

- **Capstone**: `zenith-execution`
- **Skills**: Half-Kelly sizing + Stop-loss calc + Monte Carlo sim + Portfolio rebalancer
- **Triggers**: "position size", "how much", "Kelly", "stop loss", "rebalance"
- **Co-activates**: → Cluster 3 (Risk Gate) as prerequisite check
- **Domain**: Trading

### 5. Trade Analytics 📊

- **Capstone**: `trade-journal-analyzer`
- **Skills**: Journal pattern extraction + Drawdown classification
- **Triggers**: "trade review", "journal", "drawdown", "what went wrong", "post-trade"
- **Domain**: Trading

### 6. Social Contract & Negotiation 🤝

- **Capstone**: `power-inversion`
- **Skills**: `power-inversion` + `consiglieri-protocol`
- **Triggers**: "negotiate", "deal", "boundary", "relationship", "social contract", "BATNA", "commitment device"
- **Domain**: Business / Social

### 7. Inner Work 🧠

- **Capstone**: `therapeutic-ifs`
- **Skills**: Schema deconstruction + IFS therapy
- **Triggers**: "therapy", "inner work", "schema", "parts", "trauma", "IFS", "why do I feel"
- **Domain**: Psychology

### 8. Adversarial QA 🔴

- **Capstone**: `red-team-review`
- **Skills**: 5-phase pre-mortem + Anchoring/base-rate bias detection + Scoring
- **Triggers**: "red team", "pre-mortem", "challenge this", "devil's advocate", "stress test", "/grill"
- **Domain**: Quality

### 9. Strategic Reasoning 🎯

- **Capstone**: `decision-journal` (expanded)
- **Skills**: `decision-journal` + `synthetic-parallel-reasoning`
- **Triggers**: "analyze", "strategy", "compare options", "think deep", "tradeoff", "which should I", "/think", "/ultrathink"
- **Co-activates**: → Cluster 8 (Adversarial QA) when Λ > 30
- **Domain**: Decision

### 10. Distribution Engine 📣

- **Capstone**: `distribution-physics` (expanded)
- **Skills**: `distribution-physics` + `brand-foundations` + `seo-auditor`
- **Triggers**: "marketing", "GTM", "SEO", "brand", "positioning", "distribution", "audience", "launch"
- **Co-activates**: → Cluster 11 (Swarm Orchestrator) for multi-agent campaigns
- **Domain**: Marketing

### 11. Swarm Orchestrator 🐝

- **Capstone**: `marketing-swarm` + `git-worktree-swarm`
- **Skills**: `marketing-swarm` + `git-worktree-swarm`
- **Triggers**: "swarm", "parallel agents", "multi-agent", "worktree", "/416-agent-swarm"
- **Domain**: Architecture / Orchestration

### 12. Research Pipeline 🔬

- **Capstone**: `deep-research-loop` (expanded)
- **Skills**: `deep-research-loop` + `semantic-search`
- **Triggers**: "research", "find out", "rabbit hole", "deep dive", "what do we know about", "/research"
- **Domain**: Research

### 13. Build Lifecycle 🏗️

- **Capstone**: `spec-driven-dev` (expanded)
- **Skills**: `spec-driven-dev` + `micro-commit` + `visual-verify-ui`
- **Triggers**: "build", "implement", "code", "ship", "develop", "refactor", "/vibe"
- **Domain**: Engineering

### 14. Sovereign Safety 🚨

- **Capstone**: (Lightweight — rare activation)
- **Skills**: `circuit-breaker` + `context-compactor`
- **Triggers**: "emergency", "circuit breaker", "compact context", "cleanup", "system overload"
- **Domain**: Safety

### 15. Problem-Solving Engine 🔧

- **Capstone**: Protocol 504 (Problem Framing)
- **Skills**: P504 (Problem Framing) + P115 (First Principles) + P505 (Graph of Thought) + `red-team-review` + P506 (GTO Execution Plan)
- **Triggers**: "solve", "how do I", "problem", "stuck", "fix", "approach", "what should I do", "broken", "challenge"
- **Co-activates**: → Cluster 9 (Strategic Reasoning) if solution requires option ranking → Cluster 8 (Adversarial QA) at GoT Phase 5 → Cluster 13 (Build Lifecycle) for implementation
- **Domain**: Reasoning / Execution

---

## Routing Rules

### Co-Activation Chains

```
Trading Query → Risk Gate (#3) → if approved → Execution (#4)
Marketing Query → Distribution (#10) → if multi-agent → Swarm (#11)
Deep Think (Λ>30) → Strategic Reasoning (#9) → Adversarial QA (#8)
Build Request → Build Lifecycle (#13) → if parallel → Swarm (#11)
Problem Query → Problem-Solving (#15) → GoT Phase 5 → Adversarial QA (#8)
Problem → Solution Selected → Decision Engine (#9) for ranking
Problem → Execution Plan → Build Lifecycle (#13) for implementation
```

### Standalone Skills (Not Clustered)

*None — all active skills are clustered as of 2026-03-02 micro-pruning.*

### Activation Priority

When multiple clusters match a query, activate by **specificity** (most specific trigger wins):

1. **Exact trigger match** → Load that cluster only
2. **Multiple matches** → Load the most domain-specific cluster first
3. **Ambiguous** → Default to Cluster 9 (Strategic Reasoning) + Exocortex search

---

## Metrics

| Metric | Value |
|:---|:---|
| Total Clusters | 15 |
| Skills Covered | 22/22 (100%) |
| Orphan Skills | 0 |
| Avg. Cluster Size | 2.5 skills |
| Routing Tax Reduction | ~58% fewer tool calls vs individual loading |
