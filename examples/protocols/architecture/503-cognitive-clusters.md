---

created: 2026-02-28
last_updated: 2026-02-28
graphrag_extracted: false
---

# Protocol 503: Cognitive Clusters (Skill Architecture Pattern)

> **Created**: 2026-02-28
> **Domain**: Architecture / Meta-Cognition
> **Priority**: ⭐⭐⭐ Critical (Structural)
> **Trigger**: Skill/protocol proliferation, "too many things to load", architecture review

---

## Philosophy

> **"Don't build 10 specialists who need to call each other. Build 3 experts who already know each other's work."**

When individual protocols/skills share triggers, inputs, and domain context, maintaining them as separate units creates **routing tax** — the overhead of finding, loading, and chaining related fragments. Cognitive Clusters solve this by pre-merging co-activated knowledge into unified skills.

---

## The Pattern

```
BEFORE (Individual Protocols)          AFTER (Cognitive Cluster)
┌───────────┐                          ┌─────────────────────────┐
│ Skill A   │──triggers──▶             │                         │
│ Skill B   │──triggers──▶  routing    │   CLUSTER SKILL         │
│ Skill C   │──triggers──▶  overhead   │   Phase 1: A            │
│ Skill D   │──triggers──▶  (N calls)  │   Phase 2: B            │
│ Skill E   │──triggers──▶             │   Phase 3: C + D + E    │
└───────────┘                          │   (1 load, 0 chaining)  │
                                       └─────────────────────────┘
```

---

## The SEO Parallel (Cross-Domain Transfer)

This is the **Topic Cluster** model from SEO, applied to AI cognition:

| Concept | SEO (Google) | AI (Athena) |
|:---|:---|:---|
| **Pillar Page** | Comprehensive authority page on a topic | **Capstone Protocol** (P501, P502) |
| **Cluster Pages** | Supporting articles linked to the pillar | **Absorbed Protocols** (archived, content lives in capstone) |
| **Internal Links** | Semantic connections between pages | **Cross-references** between phases |
| **Routing** | Google spider crawls links | **Exocortex** semantic search finds cluster |
| **Authority Signal** | Single authoritative source ranks higher | **One comprehensive skill** routes faster than 5 fragments |

### Why It Works in Both Domains

Google's ranking algorithm and AI skill routing solve the **same structural problem**:

> *Given a query, retrieve the most complete, authoritative coverage with the fewest hops.*

- **SEO**: 1 pillar page with 5 sections > 5 thin pages with overlapping keywords
- **Athena**: 1 clustered skill with 5 phases > 5 individual skills with overlapping triggers

The penalty for fragmentation is identical:

- In SEO: **keyword cannibalization** (pages compete with each other, none ranks well)
- In AI: **trigger cannibalization** (skills compete for the same query, routing becomes noisy)

---

## When to Cluster

| Signal | Example | Action |
|:---|:---|:---|
| **Co-activation rate > 60%** | Asking "should I trade?" triggers 4-5 skills | Merge into lifecycle cluster |
| **Shared input parameters** | 5 skills all need Win Rate + Risk:Reward | Merge — DRY principle |
| **Sequential dependency** | Skill A's output is Skill B's input | Merge into pipeline |
| **Same domain, different verbs** | `diagnose`, `classify`, `calibrate` all in Decision domain | Merge into phased protocol |

### When NOT to Cluster

| Signal | Example | Keep Separate |
|:---|:---|:---|
| **Cross-domain** | `seo-auditor` + `trading-risk-gate` | Different contexts entirely |
| **Different activation frequency** | `circuit-breaker` (rare) + `micro-commit` (every session) | Rare skills shouldn't bloat common ones |
| **Size > 3000 tokens** | Merged skill would exceed target load size | Split into 2 clusters max |

---

## Athena's Cognitive Clusters (Live)

| Cluster | Capstone | Skills | Domain |
|:---|:---|:---|:---|
| **Diagnostic** | Protocol 501 | 1 capstone replacing 9 protocols | Decision |
| **Context Lifecycle** | Protocol 502 | 1 capstone replacing 4 protocols | Architecture |
| **Trading Risk** | `trading-risk-gate` | Pre-trade: ruin + ergodicity + WR dominance | Trading |
| **Trading Execution** | `zenith-execution` | Sizing: Kelly + SL + Monte Carlo + rebalance | Trading |
| **Trade Analytics** | `trade-journal-analyzer` | Post-trade: journal + drawdown classification | Trading |
| **Negotiation** | `power-inversion` | BATNA + commitment devices + bias detection | Business |
| **Inner Work** | `therapeutic-ifs` | Schema deconstruction + IFS therapy | Psychology |
| **Adversarial QA** | `red-team-review` | Pre-mortem + bias detection + scoring | Quality |
| **Decision Lifecycle** | `decision-journal` | Pre-decision logging + post-mortem + calibration | Decision |

---

## The Math

**Before (35 skills)**:

- Average query triggers 3.2 skills
- Each skill load = ~800 tokens + 1 tool call
- Cost per query: ~2,560 tokens + 3.2 tool calls

**After (21 skills)**:

- Average query triggers 1.4 skills
- Each skill load = ~1,200 tokens (larger but self-contained) + 1 tool call
- Cost per query: ~1,680 tokens + 1.4 tool calls
- **Savings: ~34% tokens, ~56% tool calls per query**

The larger individual skill size is offset by dramatically fewer loads — a classic **batch vs streaming** tradeoff.

---

## Cross-Domain Applications

The Cognitive Cluster pattern applies anywhere fragmented knowledge creates routing overhead:

| Domain | Fragment Problem | Cluster Solution |
|:---|:---|:---|
| **SEO** | 20 thin blog posts competing for same keyword | 1 pillar page + internal links |
| **AI Skills** | 10 skills with overlapping triggers | 3 lifecycle clusters |
| **Codebase** | 15 utility functions scattered across files | 1 module with clear API |
| **Documentation** | FAQ spread across 8 pages | 1 comprehensive guide |
| **Education** | Separate courses on related topics | Integrated curriculum |

---

## Tags

# protocol #architecture #cognitive-clusters #meta-cognition #seo-parallel #cross-domain #capstone
