---
protocol: 525
title: Cross-Domain Weighting
category: reasoning
version: 1.0
created: 2026-03-11
dependencies: [500, 501, 524, 330]
---

# Protocol 525: Cross-Domain Weighting

> **Purpose**: Solve multi-domain problems by decomposing, classifying, solving per-domain, weighting by conviction, and reassembling into a unified recommendation.

---

## The Problem

Real-world questions rarely sit in a single domain. "Should I buy this phone?" contains arithmetic (deterministic), warranty law (semi-deterministic), device longevity (semi-stochastic), and future pricing (stochastic) — all fused into one decision.

Naive approaches fail in two ways:
- **Averaging conviction** → lukewarm confidence everywhere (useless)
- **Defaulting to lowest conviction** → discards the high-confidence components (wasteful)

---

## The Pipeline

```
Question → [501: Decompose] → [Domain Table: Classify] → [524: Solve] → [525: Weight] → [500/330: Synthesize]
```

### Step 1: Decompose (Protocol 501)

Break the question into atomic sub-problems. Each sub-problem should be answerable independently.

### Step 2: Classify (Domain Table)

Assign each sub-problem a domain type:

| Domain | Conviction | Edge Source |
|--------|-----------|-------------|
| Deterministic | High (0.9+) | Logic, math, code |
| Semi-deterministic | Moderate (0.6-0.8) | Precedent, frameworks, assumptions |
| Semi-stochastic | Low (0.3-0.5) | Structural edge exists, noise dominates |
| Stochastic | Minimal (0.0-0.2) | No model outperforms randomness |

### Step 3: Solve Per-Domain (Protocol 524)

Each sub-problem gets solved at its appropriate conviction level:
- **Deterministic** → Single correct answer, stated with confidence
- **Semi-deterministic** → Conditional range with explicit assumptions
- **Semi-stochastic** → Precise structure, deferred probability (The Pryce Effect)
- **Stochastic** → Honest "I don't know" with boundary conditions

### Step 4: Weight and Reassemble

#### Rule 1: Conviction Weights the Recommendation

Higher-conviction components get more influence on **what to do**. Lower-conviction components get more influence on **how much to risk**.

```
Recommendation = Σ (Sub-answer × Conviction Weight)
```

High-conviction components → decide the ACTION.
Low-conviction components → decide the POSITION SIZE (exposure, hedge, risk budget).

#### Rule 2: Reversibility Override (Law #1)

Any sub-problem flagging irreversible downside gets veto power regardless of conviction:

```
IF any sub-problem has:
  P(ruin) > 5%        → HARD VETO
  Irreversible harm   → HARD VETO
  Reversible downside  → Factor into risk budget, continue
```

### Step 5: Synthesize (Protocol 500 + 330)

Output the unified recommendation using EEV (Protocol 330), not MEV:

> **Action**: [What to do — driven by high-conviction components]
> **Risk Gate**: [Key risk factor — driven by low-conviction components]
> **Veto Check**: [Law #1 status — pass/fail]

---

## Example: "Should I buy this used S24 Ultra at $650?"

| Sub-Problem | Domain | Conviction | Answer |
|------------|--------|-----------|--------|
| Is 66% off retail correct? | Deterministic | 0.95 | Yes — arithmetic verified |
| Will warranty cover dead pixel? | Semi-deterministic | 0.70 | Likely — manufacturing defect precedent favors it |
| Will phone last 3+ years? | Semi-stochastic | 0.50 | Probable — flagship SoC, but battery is wildcard |
| Will a better deal appear? | Stochastic | 0.10 | Unknown — no predictive model |

**Weighted synthesis**: Strong buy. Warranty inspection is the key risk gate. Future pricing is unknowable and therefore not actionable — excluded from decision.

**Veto check**: Max downside = $650 for a phone with a dead pixel. Reversible (resell). Law #1 passes. ✅

---

## Anti-Patterns

- ❌ Treating multi-domain questions as single-domain
- ❌ Averaging conviction across sub-problems
- ❌ Giving stochastic components equal vote to deterministic ones
- ❌ Ignoring the reversibility gate because the weighted sum looks good

---

## Related Protocols

- [Protocol 500: GTO Problem Solver](../decision/500-gto-problem-solver.md) — Final synthesis engine
- [Protocol 501: Diagnostic Engine](../decision/501-diagnostic-engine.md) — Decomposition step
- [Protocol 524: Conviction-Decisiveness Split](524-conviction-decisiveness-split.md) — Per-domain solving
- [Protocol 330: Economic Expected Value](../decision/330-economic-expected-value.md) — EEV weighting
- Core Identity: Law #1 (Ruin Veto) — Override gate
