# Adaptive Graph of Thoughts (AGoT) — Research Archive

> **Source**: Gemini Deep Research output (2026-03-11)
> **Primary Paper**: Pandey et al. (2025), arXiv:2502.05078
> **Purpose**: Reference for Protocol 75 v5.0 implementation

---

## Core Algorithm

AGoT recursively decomposes complex queries into a dynamic DAG of interdependent reasoning steps.
Each node is assessed for complexity; complex nodes spawn nested sub-graphs.

```
AGoT_Solve(query, depth, parent_context):
  1. Generate decomposition strategy for this layer
  2. Decompose query into N subproblems (max_new_tasks)
  3. For each subproblem (concurrently):
     a. Resolve via LLM
     b. If COMPLEX and depth < max_depth → recurse AGoT_Solve()
     c. If SIMPLE → evaluate directly
  4. Synthesize all resolved nodes into final answer
  5. Self-terminate on quality threshold or max_depth
```

**Default configuration** (from reference implementation):

- `max_depth = 1` (1 level of recursive nesting)
- `max_layers = 3` (3 layers per graph level)
- `max_new_tasks = 3` (3 subproblems per decomposition)

---

## Key Findings

| Finding | Detail |
|:--------|:-------|
| **Performance** | +46.2% accuracy on GPQA vs input-output baseline |
| **No fine-tuning needed** | Prompt-only + Python orchestration |
| **Controller is Python** | Meta-reasoning is deterministic code, not LLM |
| **BFS + recursive DFS** | Breadth-first across layers, depth-first into complex nodes |
| **Typical call count** | 10-20 LLM calls (moderate), 50-120 (max with 4 tracks) |
| **Diminishing returns** | Quality scales logarithmically with depth beyond defaults |

---

## RouteGoT (March 2026, arXiv:2603.05818)

Critical cost optimization: node-adaptive routing.

- +8.1pp accuracy over baseline AGoT
- 79.1% token reduction
- Lightweight models for complexity classification + leaf evaluation
- Heavy models reserved for strategy + synthesis

---

## Integration Architecture for Athena

```
Query → Λ Router
├─ Λ ≤ 20:  CoT (unchanged)
├─ Λ 21-40: AGoT-lite (depth=0, layers=2, tasks=3)
├─ Λ 41-60: AGoT-full (depth=1, layers=3, tasks=4)
└─ Λ > 60:  AGoT + 4-track personas (depth=2, layers=4)
    ├─ Track A: Domain Expert → internal AGoT sub-graph
    ├─ Track B: Adversarial → internal AGoT sub-graph
    ├─ Track C: Cross-Domain → internal AGoT sub-graph
    ├─ Track D: First Principles → internal AGoT sub-graph
    └─ Adaptive Convergence Gate (variable threshold)
```

Convergence gate adapts threshold by inter-track agreement:

- High consensus (>0.8): threshold = 70
- Partial consensus (>0.5): threshold = 85
- Disagreement (<0.5): threshold = 90 + reconciliation round

---

## Key Papers

1. **Pandey et al. (2025)** — AGoT: arXiv:2502.05078
2. **Liu et al. (2026)** — RouteGoT: arXiv:2603.05818
3. **Besta et al. (2024)** — GoT: arXiv:2308.09687 (AAAI 2024)
4. **Yao et al. (2023)** — ToT: arXiv:2305.10601 (NeurIPS 2023)
5. **Wei et al. (2022)** — CoT: arXiv:2201.11903
6. **Radha et al. (2024)** — AIoT: arXiv:2409.12618
7. **Wu et al. (2026)** — LogicGraph: arXiv:2602.21044
