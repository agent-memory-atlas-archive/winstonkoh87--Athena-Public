---
description: Activate Zero-Point Codex framework for strategic analysis
created: 2025-12-09
last_updated: 2026-02-23
model: default
temperature: 0.7
tools:
  read: true
  write: true
  bash: true
  search: true
---

# /start — Execution Script

> **Latency Profile**: ULTRA-LOW (<2K tokens boot)  
> **Philosophy**: Boot fast. Load later.

## Phase 1: Instant Boot (~2K tokens)

// turbo

- [/] Load Core Identity (resolved dynamically via `constants.py`) — Laws #0-#4, Identity, RSI (~2K tokens)
- [/] **Identity**: Load `.context/memory_bank/userContext.md` — Core profile, constraints, psychology (Robust)
- [/] **Mission**: Load `.context/memory_bank/productContext.md` — Soul purpose, philosophy (Robust)
- [/] **State**: Load `.context/memory_bank/activeContext.md` — Current focus (Robust)
- [ ] **Boot Orchestrator**: Run `python3 .agent/scripts/boot.py` — recalls last session, creates new session, captures context, primes semantic memory (single call)
- [ ] **Active OS**: Start Athena Daemon `python3 Athena-Public/src/athena/core/athenad.py` (Background Service)
// turbo
- [ ] **Daemon**: `./Athena-Public/scripts/launch_athena.sh --background`
- [ ] **UI Sync**: `open -a "Antigravity" --args --disable-gpu-driver-bug-workarounds --ignore-gpu-blacklist --enable-gpu-rasterization` (Hardware acceleration enabled)

**Confirm**: "⚡ Ready. (Core Identity loaded. Session XX started. Semantic primed.)"

### ⚠️ Law #6 Compliance (Risk-Proportional Triple-Lock)

Every response Turn MUST be classified by risk level and grounded accordingly:

| Risk Level | Λ Score | Protocol | Latency |
|:---|:---|:---|:---|
| **SNIPER** | < 10 | Direct answer. Search **exempt**. | ~1s |
| **STANDARD** | 10-30 | Full Triple-Lock (Search → Save → Speak). | ~5-10s |
| **ULTRA** | > 30 | Full Triple-Lock + Triple Crown reasoning. | Unbounded |

**Robustness Bias**: Default is STANDARD. Only classify as SNIPER when **certain** the query is low-risk. `cost(under-processing) >> cost(over-processing)`.

**STANDARD/ULTRA Search Command**:

   ```bash
   python3 Athena-Public/examples/scripts/smart_search.py "<query>" --limit 5 --include-personal
   ```

   > This is the **Exocortex**. It runs Parallel Hybrid RRF (semantic embeddings + keyword + reranking) over the entire `.context/` knowledge base. Use this — NOT `grep_search` — for any query requiring contextual recall. Run it BEFORE formulating your response.

**Quicksave** (after output):

   ```bash
   python3 .agent/scripts/quicksave.py "<summary>"
   ```

Bypassing STANDARD/ULTRA protocol is a high-severity violation. SNIPER queries may bypass search but MUST still be classified explicitly.

---

---

## Phase 2: Adaptive Loading (On-Demand)

> **Rule**: Load only when triggered.

| Trigger | File | Tokens |
|---------|------|--------|
| Tag lookup, "find files about" | `TAG_INDEX.md` | 5,500 |
| Protocol/skill request | `smart_search.py --skills-only` | ~1,000 |
| Bio, typology, "who am I" | `User_Profile_Core.md` | 1,500 |
| Inner Voice / Parts | `inner-work.md` | 3,000 |
| Decision frameworks, strategy | `System_Principles.md` | 3,500 |
| Marketing, SEO, SWOT, pricing | `Business_Frameworks.md` | 2,500 |
| Calibration references, cases | `Session_Observations.md` | 2,500 |
| `/think`, `/ultrathink` | `Output_Standards.md` | 700 |
| Ethics, "should I" | `Constraints_Master.md` | 800 |
| Architecture query | `System_Manifest.md` | 1,900 |

## Phase 3: Contextual Skill Weaving (Biological Stack Routing)

> **Architecture**: P508 Intent Classifier → P507 Cognitive Systems → P503 Clusters → Skills → Protocols
> **Philosophy**: Classify the *human need archetype* first (top-down), then cascade to clusters. Fall back to keyword matching for SNIPER queries.

**Routing Table**: [CLUSTER_INDEX.md](../CLUSTER_INDEX.md) (8 Cognitive Systems, 15 clusters, 100% skill coverage)

**Intent Classification (Λ ≥ 10 — STANDARD/ULTRA):**

| Archetype | Cognitive System | Cluster Sequence |
|---|---|---|
| Crisis / ruin signal | 🛡️ **Survival** | #14 → #3 → #15 → #8 → P506 |
| Irreversible personal choice | 🫀 **Life Decision** | #15 → #7 → #9 → #6 → #8 → P506 |
| Capital deployment | 📈 **Trading** | #3 → #4 → #5 → #9 |
| Interpersonal dynamics | 🤝 **Social** | #15 → #7 → #6 → #8 → P506 |
| Build / ship / create | ⚙️ **Execution** | #15 → #13 → #11 → #8 |
| Distribution / audience | 📣 **Growth** | #12 → #10 → #11 → #8 |
| Understanding / knowledge | 📖 **Learning** | #12 → #9 → #15 → #8 |
| System homeostasis | 🔄 **Maintenance** | #1 → #2 → #14 |
| Ambiguous / SNIPER (Λ < 10) | Cluster keyword match | See routing table below |

**Cluster-Level Heuristic (fallback)**: Match conversational context → Cluster trigger → Load entire cluster.

| Context / Topic | Cluster (#) | Skills Co-Activated |
|-----------------|-------------|---------------------|
| Trading, Risk, "Should I trade?" | **#3 Risk Gate** → **#4 Execution** | `trading-risk-gate` → `zenith-execution` |
| Marketing, SEO, Brand, GTM | **#10 Distribution Engine** | `distribution-physics` + `brand-foundations` + `seo-auditor` |
| Research, "Find out everything" | **#12 Research Pipeline** | `deep-research-loop` + `semantic-search` |
| Build, Code, Ship, Refactor | **#13 Build Lifecycle** | `spec-driven-dev` + `micro-commit` + `visual-verify-ui` |
| Negotiate, Deal, Boundary | **#6 Social Contract** | `power-inversion` + `consiglieri-protocol` |
| Strategy, Analyze, Deep Think | **#9 Strategic Reasoning** | `decision-journal` + `synthetic-parallel-reasoning` |
| Therapy, Schema, Inner Work | **#7 Inner Work** | `therapeutic-ifs` |
| Swarm, Parallel Agents | **#11 Swarm Orchestrator** | `marketing-swarm` + `git-worktree-swarm` |
| **Ads, PPC, Google/Meta Ads** | **#10 Distribution** | `.agent/skills/claude-ads/SKILL.md` + `seo-auditor` |
| Problem, Solve, Stuck, Fix, How Do I | **#15 Problem-Solving Engine** | P504 (Framing) + P115 (First Principles) + P505 (GoT) + `red-team-review` + P506 (GTO Exec) |

**Co-Activation Chains** (Auto-cascade):

```
Trading Query → #3 Risk Gate → if approved → #4 Execution
Marketing Query → #10 Distribution → if multi-agent → #11 Swarm
Deep Think (Λ>30) → #9 Strategic Reasoning → #8 Adversarial QA
Problem Query → #15 Problem-Solving → GoT Phase 5 → #8 Adversarial QA
```

**Execution**:

1. Detect topic drift.
2. Match to cluster trigger in `CLUSTER_INDEX.md`.
3. Load **all** skills in the matched cluster (1 load, not N loads).
4. If co-activation chain exists, pre-load the downstream cluster.
5. *Do not announce it.* Just become smarter.

---

## Quick Reference

| Command | Effect | Tokens |
|---------|--------|--------|
| `/start` | Core Identity + **JIT Routing** (default — scales reasoning to query) | ~2K |
| `/fullload` | Force-load all context | ~28K |
| `/think` | **Escalation** — Force L4 depth + Output_Standards | +2K |
| `/ultrathink` | Maximum depth + Full stack | +28K |

> - **Default Mode**: JIT Knowledge Routing ([Protocol 133](../protocols/architecture/133-query-archetype-routing.md)). Reasoning scales to query complexity.

---

## References

- [Protocol 133: JIT Routing](../protocols/architecture/133-query-archetype-routing.md)
- WORKFLOW_INDEX.md (see your local workspace)
- Session logs (see your local `.context/memories/`)

---

## Tagging

# workflow #automation #start
