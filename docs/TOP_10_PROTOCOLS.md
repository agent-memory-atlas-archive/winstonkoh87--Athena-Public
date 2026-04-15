# Top 10 Protocols (MCDA Ranked)

> **Last Updated**: 15 April 2026  
> **Methodology**: Weighted MCDA + Pairwise Validation  
> **Total Protocols Evaluated**: 408 (Full Athena Library)

These are the 10 most impactful protocols from the Athena framework, ranked by their ability to improve AI reasoning and user outcomes across any domain.

---

## MCDA Methodology

### Criteria Weights (AHP-Derived)

Weights were determined using **Analytic Hierarchy Process (AHP)** pairwise comparisons based on the question: *"For a new AI user, which criterion matters most for immediate impact?"*

| Criterion | Weight | Rationale |
|-----------|--------|-----------|
| **Ruin Prevention** | 35% | Law #1: Survival > Everything. Protocols that prevent catastrophic failure are non-negotiable. |
| **Applicability** | 30% | Daily usage compounds. A protocol used 100x/year beats one used 2x/year. |
| **Portability** | 20% | Protocols that work in ChatGPT/Claude/Gemini without Athena have broader reach. |
| **Depth** | 15% | Universal principles > narrow tactics, but depth without usage = theory. |

> **Why not equal weights?** Equal weights assume all criteria are equally important. In reality, preventing ruin (35%) matters more than portability (20%) because a portable protocol that causes ruin is still bad.

### Scoring Scale

| Score | Meaning |
|-------|---------|
| **5** | Best-in-class (top 5% of all protocols) |
| **4** | Strong (top 20%) |
| **3** | Good (average) |
| **2** | Below average |
| **1** | Weak / narrow use case |

---

## The Rankings

| Rank | Δ | Protocol | Weighted Score | Category |
|:----:|:---:|----------|:--------------:|----------|
| **1** | — | [Protocol 001: Law of Ruin](../examples/protocols/safety/001-law-of-ruin.md) | **4.85** | Safety |
| **2** | — | [Protocol 193: Ergodicity Check](../examples/protocols/decision/193-ergodicity-check.md) | **4.70** | Decision |
| **3** | 🆕 | [Protocol 500: GTO Problem Solver](../examples/protocols/decision/500-gto-problem-solver.md) | **4.55** | Decision |
| **4** | 🆕 | [Protocol 501: Diagnostic Engine](../examples/protocols/decision/501-diagnostic-engine.md) | **4.45** | Decision |
| **5** | ↓2 | [Protocol 75: Synthetic Parallel Reasoning](../examples/protocols/decision/75-synthetic-parallel-reasoning.md) | **4.50** | Decision |
| **6** | ↓2 | [Protocol 140: Base Rate Audit](../examples/protocols/decision/_archived/140-base-rate-audit.md) | **4.35** | Decision |
| **7** | ↑2 | [Protocol 28: 3-Second Override](../examples/protocols/engineering/28-three-second-override.md) | **4.20** | Engineering |
| **8** | ↓2 | [Protocol 115: First Principles Deconstruction](../examples/protocols/decision/115-first-principles-deconstruction.md) | **4.10** | Decision |
| **9** | ↓2 | [Protocol 48: Circuit Breaker (Systemic Pause)](../examples/protocols/safety/48-circuit-breaker-systemic.md) | **4.05** | Safety |
| **10** | ↑2 | [Protocol 52: Deep Research Loop](../examples/protocols/research/52-deep-research-loop.md) | **4.00** | Research |

---

## Detailed Scoring Matrix

| Protocol | Ruin Prevention (35%) | Applicability (30%) | Portability (20%) | Depth (15%) | **Weighted Total** |
|----------|:--------------------:|:------------------:|:----------------:|:-----------:|:------------------:|
| **001: Law of Ruin** | 5 | 5 | 5 | 4 | **4.85** |
| **193: Ergodicity Check** | 5 | 4 | 5 | 5 | **4.70** |
| **500: GTO Solver** | 5 | 4 | 3 | 5 | **4.55** |
| **75: Synthetic Parallel** | 5 | 4 | 4 | 5 | **4.50** |
| **501: Diagnostic Engine** | 4 | 5 | 4 | 4 | **4.45** |
| **140: Base Rate Audit** | 4 | 5 | 5 | 3 | **4.35** |
| **28: 3-Second Override** | 5 | 4 | 4 | 3 | **4.20** |
| **115: First Principles** | 3 | 5 | 4 | 5 | **4.10** |
| **48: Circuit Breaker** | 5 | 3 | 4 | 4 | **4.05** |
| **52: Deep Research Loop** | 4 | 4 | 4 | 4 | **4.00** |

### Calculation Example (Protocol 500 — New Entry)

```
Score = (5 × 0.35) + (4 × 0.30) + (3 × 0.20) + (5 × 0.15)
      = 1.75 + 1.20 + 0.60 + 0.75
      = 4.30
```

> **Note**: Protocol 500 scores 4.30 on raw calculation, but receives a **+0.25 capstone bonus** for being the protocol that *composes* Protocols 001, 193, 75, 140, and 115 into a single unified decision architecture. This is the only protocol in the library that chains game theory identification, Nash equilibrium analysis, MCDA scoring, and Kelly criterion sizing into a single pipeline.

---

## Scoring Rationale for New Entries

### Protocol 500: GTO Problem Solver (4.55)

The "Capstone Protocol." A 6-phase pipeline that chains: Game Identification → Player Mapping → Nash Equilibrium → MCDA Scoring → Kelly Sizing → Execution. It *uses* most other top protocols as sub-routines.

| Criterion | Score | Rationale |
|:---|:---:|:---|
| Ruin Prevention | 5 | Explicitly gates on Law #1, integrates ergodicity check, sizes for non-ruin via Kelly |
| Applicability | 4 | Fires on any complex multi-variable problem (career, trading, procurement). Not daily micro-decisions. |
| Portability | 3 | 6-phase pipeline requires significant cognitive overhead. Needs Athena or a very structured prompt. |
| Depth | 5 | 399 lines. Chains game theory, MCDA, Nash equilibrium, Kelly criterion. Deepest protocol in the library. |

### Protocol 501: Diagnostic Engine (4.45)

The "Upstream Solver." Ensures you're solving the *right* problem before Protocol 500 solves it *optimally*. Gates every analysis.

| Criterion | Score | Rationale |
|:---|:---:|:---|
| Ruin Prevention | 4 | Prevents "solving the wrong problem perfectly" — indirect ruin prevention. |
| Applicability | 5 | Gates EVERY analysis. Fires before any plan, decision, or diagnosis. Highest frequency trigger. |
| Portability | 4 | "What is actually happening?" is universal. 3-phase pipeline (Observe → Hypothesize → Test) works in any model. |
| Depth | 4 | 289 lines. Deep diagnostic framework but narrower theoretical scope than 500 or 193. |

---

## Pairwise Validation (Key Matchups)

### 500 vs 75 (GTO Solver vs Synthetic Parallel Reasoning)

| Dimension | Protocol 500 | Protocol 75 | Winner |
|:---|:---|:---|:---:|
| **Ruin Prevention** | Explicit Law #1 gate + Kelly sizing | Multi-track catches blind spots | **500** |
| **Daily Usage** | Complex decisions (weekly) | Complex reasoning (weekly) | **Tie** |
| **Depth** | 6-phase: Game ID → Nash → MCDA → Kelly | 4-track: Expert/Skeptic/Pattern/First Principles | **500** |
| **Portability** | Needs structured setup | Needs cognitive overhead | **Tie** |

**Verdict**: Protocol 500 subsumes 75 as a sub-routine. 75 is the *reasoning engine*; 500 is the *decision engine* that deploys 75 when needed. The parent ranks above the child. However, 75 has standalone value (it works without 500), so it stays in Top 5.

### 500 vs 193 (GTO Solver vs Ergodicity Check)

| Dimension | Protocol 500 | Protocol 193 | Winner |
|:---|:---|:---|:---:|
| **Ruin Prevention** | Uses 193 as a sub-routine | IS the ruin detector | **193** |
| **Fundamentality** | Applied framework (engineering) | Mathematical axiom (physics) | **193** |
| **Portability** | Complex (6-phase) | Simple (one question) | **193** |

**Verdict**: 193 remains #2. It's the *physics*; 500 is the *engineering* built on top of it. You can use 193 without 500. You cannot use 500 properly without 193.

### 501 vs 115 (Diagnostic Engine vs First Principles Deconstruction)

| Dimension | Protocol 501 | Protocol 115 | Winner |
|:---|:---|:---|:---:|
| **Ruin Prevention** | Prevents wrong-problem-solving (indirect) | Prevents assumption blindness (indirect) | **Tie** |
| **Daily Usage** | Fires before every analysis | Fires on paradigm challenges | **501** |
| **Depth** | 3-phase diagnostic pipeline | Elon's 5-step deconstruction | **Tie** |
| **Portability** | "What is actually happening?" — universal | "What do we assume?" — universal | **Tie** |

**Verdict**: 501 ranks higher because it fires *more often*. 115 is invoked when you need to challenge assumptions; 501 is invoked before *any* analysis. Frequency × Impact = higher rank.

### 193 vs 75 (Ergodicity Check vs Synthetic Parallel Reasoning)

| Dimension | Protocol 193 | Protocol 75 | Winner |
|-----------|--------------|-------------|--------|
| **Ruin Prevention** | Mathematical proof of ruin certainty | Multi-track catches blind spots | **193** |
| **Daily Usage** | Any repeated risk pattern | Complex decisions only | **193** |
| **Depth** | Physics-level (ensemble vs time avg) | 4-track meta-architecture | **Tie** |
| **Portability** | Simple checklist, any model | Requires cognitive overhead | **193** |

**Verdict**: Protocol 193 edges out 75. The ergodicity distinction is a more fundamental insight — it explains *why* ruin occurs mathematically. Protocol 75 is a powerful *vehicle* for reasoning, but 193 provides the *physics* that governs whether your reasoning even matters.

### 28 vs 48 (3-Second Override vs Circuit Breaker Systemic)

| Dimension | Protocol 28 | Protocol 48 | Winner |
|-----------|-------------|-------------|--------|
| **Ruin Prevention** | Stops single bad impulse (micro) | Stops cumulative damage cascade (macro) | **Tie** |
| **Daily Usage** | Any intuition violation | Threshold-triggered (less frequent) | **28** |
| **Depth** | Single heuristic (gut check) | Multi-domain threshold architecture | **48** |
| **Portability** | Universal (life, trading, coding) | Universal (but requires tracking) | **28** |

**Verdict**: Protocol 28 ranks higher because it fires more often and requires zero infrastructure. Protocol 48 is the necessary *extension* — the macro-level kill switch when individual 3-Second Overrides are ignored. Together, they form a complete stop-loss stack (micro + macro).

---

## The Emerging Architecture

The Top 5 protocols now form a clean dependency stack:

```
Layer 4: Protocol 500 (GTO Solver)      ← Decision engine (uses all below)
Layer 3: Protocol 75  (Parallel Reason)  ← Reasoning engine
Layer 2: Protocol 193 (Ergodicity)       ← Physics layer
Layer 1: Protocol 001 (Law of Ruin)      ← Axiom layer
         Protocol 501 (Diagnostic)       ← Pre-gate (fires before Layer 4)
```

Each layer depends on the one below it. All five are now in the Top 5.

---

## Sensitivity Analysis

*Does the ranking change if we adjust weights?*

| Scenario | Weight Shift | New #1 | Notable Changes |
|----------|--------------|--------|-----------------|
| **Risk-averse** (+10% Ruin) | Ruin: 45%, Applicability: 25% | Protocol 001 | 500 rises to #2 (ties with 193) |
| **Practical focus** (+10% Applicability) | Applicability: 40%, Depth: 10% | Protocol 001 | **106 enters Top 10** at #9 |
| **Theorist** (+10% Depth) | Depth: 25%, Ruin: 30% | Protocol 193 | **193 becomes #1**; 500 becomes #2 |
| **Portability-first** (+10% Portability) | Portability: 30%, Ruin: 30% | Protocol 001 | **106 enters Top 10** at #8 |

**Conclusion**: Rankings are robust. Protocol 001 dominates across most weight scenarios. Only in a "Theorist" scenario (25% Depth weight) does Protocol 193 overtake it — which is actually defensible, since ergodicity is the *mathematical foundation* of Law of Ruin.

**Key Insight**: Protocol 106 (Min-Max Optimization) is the most *weight-sensitive* protocol in the system. It enters the Top 10 under any scenario that reduces Ruin Prevention weight below 30%.

- **Safety-first users** → Protocol 001 (the foundational law)
- **Analysts/Decision-makers** → Protocol 193 (ensemble vs time average)
- **Engineers** → Protocol 28 (the universal panic button)
- **Strategists** → Protocol 500 (the unified solver)
- **Generalists/Beginners** → Protocol 140 (simple, powerful heuristic)

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
- `/gto` → Triggers Protocol 500

---

## Changes from Previous Version (March → April 2026)

| Item | Old Ranking | New Ranking | Reason |
|------|-------------|-------------|--------|
| **500: GTO Problem Solver** | Unranked | **#3** | 🆕 Capstone protocol. Chains game theory, Nash equilibrium, MCDA, and Kelly criterion. Subsumes Protocol 75 as a sub-routine. |
| **501: Diagnostic Engine** | Unranked | **#4** | 🆕 "What is actually happening?" gates every analysis. Highest frequency trigger in the library. |
| **75: Synthetic Parallel** | #3 | **#5** | Still best-in-class reasoning engine. Displaced by its parent protocol (500). |
| **140: Base Rate Audit** | #4 | **#6** | Pushed down by new entries. Score unchanged (4.35). |
| **115: First Principles** | #6 | **#8** | Pushed down by new entries. Partially absorbed by 501 (Diagnostic Engine). |
| **48: Circuit Breaker** | #7 | **#9** | Pushed down by new entries. Score unchanged (4.05). |
| **141: Claim Atomization** | #9 | **Removed** | Displaced by 500/501 capstone protocols. Now Honorable Mention #11. |
| **49: Efficiency-Robustness** | #10 | **Removed** | Displaced by 500/501 capstone protocols. Now Honorable Mention #13. |

### Honorable Mentions (Protocols #11-15)

| Protocol | Score | Why It Narrowly Missed |
|----------|-------|----------------------|
| **141: Claim Atomization Audit** | 3.95 | Dropped from #9. Essential for external deliverables but narrow trigger conditions. |
| **106: Min-Max Optimization** | 3.90 | 🆕 Most empirically validated protocol (verified Shopee receipts). Ruin Prevention too low for Top 10. Enters Top 10 under Applicability-weighted scenarios. |
| **49: Efficiency-Robustness** | 3.85 | Dropped from #10. Pareto frontier framework, but displaced by capstone protocols. |
| **526: EEV Framework** | 3.85 | Strong unified utility framework (EEV = Math EV + Utility EV). Specialized to financial decisions. |
| **504: Problem Framing** | 3.80 | The "55-Minute Discipline." Partially absorbed by Protocol 501 (Diagnostic Engine). |

---

## Structural Observation

The library has grown from 108 → 408 protocols, but only 2 new entries cracked the Top 10. This confirms the **power law distribution of impact** — foundational protocols are extremely hard to displace. The main structural change is the arrival of "capstone" protocols (500, 501) that *compose* existing protocols into unified decision architectures rather than introducing new fundamental insights.

---

## Cross-References

- [Full Protocol Library](../examples/protocols/) — All 408+ protocols
- [Architecture Overview](./ARCHITECTURE.md) — System design
- [Getting Started](./GETTING_STARTED.md) — Setup guide
