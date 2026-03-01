---
description: Maximum depth mode — v4.0 (Mandatory Parallel Orchestrator)
created: 2025-12-12
last_updated: 2026-03-01
---
# /ultrathink — Execution Script (v4.0)

> **Version**: 4.0 (Mandatory Parallel Execution)
> **Refactored**: 2026-03-01 (Enforcement Gate + Context Injection + Output Persistence)
> **Breaking Change**: Script execution is no longer optional. Single-pass essays are a protocol violation.

---

> [!CAUTION]
> **ENFORCEMENT CONTRACT**: If you skip the `parallel_orchestrator.py` script and write a single-pass essay, you have **FAILED** this workflow. The entire point of `/ultrathink` is that reasoning happens across **multiple independent API calls**, not inside a single LLM context window. A single LLM checking its own homework will hit a quality ceiling.

---

## When to Use

| Query Complexity | Workflow |
|------------------|----------|
| **Λ ≤ 30** | Direct answer. No workflow needed. |
| **Λ 31-60** | `/think` — Internal CoT only (no script). |
| **Λ > 60 or high-stakes** | **`/ultrathink`** — Internal CoT + mandatory parallel orchestrator. |

**Rule**: `/think` = deep reasoning within a single context window (cheap, fast).
`/ultrathink` = `/think` PLUS 4 parallel external API calls for adversarial cross-checking (expensive, slow, required).

---

## Phase 1: Prime (Context Gathering)

1. **Semantic Search** (MANDATORY):

    ```bash
    python3 scripts/smart_search.py "<extract keywords from query>" --limit 5
    ```

    - Capture the top results. These become the `--context-file` input for Phase 2.

2. **Internal CoT** (MANDATORY):
    Before dispatching the orchestrator, perform the Deep Thought Protocol internally:
    - [ ] **Deconstruct**: Break request into atomic axioms.
    - [ ] **Lateral Prism**: Generate 3 distinct angles (e.g., Domain View, Risk View, First Principles View).
    - [ ] **Plan**: Draft step-by-step logic.
    - [ ] **Critical Review**: Hunt for hallucinations/flaws. Backtrack if found.
    - [ ] **Synthesis**: Combine the lateral views into a preliminary hypothesis.

3. **Build Context File** (MANDATORY):
    Write a context file to `/tmp/ultrathink_context.md` containing:
    - The preliminary hypothesis from step 2
    - Relevant semantic search results from step 1
    - Any active session state or user constraints that apply

---

## Phase 2: Execute (Parallel Orchestrator)

> [!IMPORTANT]
> **This step is NOT optional.** You MUST run the script below. Do NOT simulate it.

```bash
python3 scripts/parallel_orchestrator.py "<the user's query>" \
  --context-file /tmp/ultrathink_context.md \
  --output .context/state/ultrathink/ultrathink_$(date +%Y%m%d_%H%M%S).md \
  --json
```

**What the script does**:

1. Dispatches 4 parallel Gemini API calls (Domain Expert, Adversarial Skeptic, Cross-Domain Pattern Matcher, Zero-Point First Principles)
2. Synthesizes the 4 track outputs into a unified analysis
3. Runs an Adversarial Convergence Gate (score 0-100)
4. If score < 85, iterates up to 3 times with critique feedback
5. Saves final output to the `--output` file

**Wait for the script to finish.** Read the output file.

---

## Phase 3: Deposit (Synthesis & Persistence)

1. **Read the output file** from Phase 2.
2. **Present to user**: Format the synthesis into a clean, structured response. Include:
   - The convergence score and number of iterations
   - Key points of agreement across tracks
   - Resolved conflicts
   - Risk integration from the Adversarial track
   - Final recommendation with confidence level
3. **Log**: Save the exchange for future reference.
4. **Auto-Document**: If the analysis produced a novel insight or framework, file it as a case study or protocol.

---

## Stability Controls (v4.0)

| Trigger | Action |
|---------|--------|
| **Convergence Score ≥ 85** | **OUTPUT**. (Adversarial Gate Passed) |
| **Iterations > 3** | **HALT**. (Cost Cap) |
| **Ruin Risk Detected** | **ESCALATE**. (Track B Veto — present risk to user immediately) |
| **Script fails to execute** | **REPORT**. (Do NOT simulate. Tell user the script failed and why.) |

---

## Tagging

`#workflow` `#safety` `#ultrathink` `#v4.0` `#parallel-orchestrator` `#mandatory-execution`
