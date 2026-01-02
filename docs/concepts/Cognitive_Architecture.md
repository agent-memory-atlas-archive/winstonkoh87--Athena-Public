# Concept: Cognitive Architecture

> **Purpose**: Overview of the psychological principles underlying AI-human collaboration.  
> **Domain**: Human-AI Interaction Design

---

## 1. The Bionic Model

AI-human collaboration works best when modeled as a **bionic unit**—human cognition + AI reasoning integrated as one workflow.

```
┌─────────────────────────────────────────┐
│            BIONIC UNIT                  │
├─────────────────────────────────────────┤
│  Human: Strategy, Intent, Judgment      │
│  AI: Execution, Pattern Detection, Speed│
└─────────────────────────────────────────┘
```

## 2. Key Cognitive Principles

### 2.1 Revealed Preference Protocol

**Law #3**: Actions > Words. Observable behavior is weighted 10x over stated preference.

| Signal Type | Trust Weight |
|-------------|--------------|
| Costly signals (time/money invested) | High |
| Cheap talk (promises, intentions) | Low |

### 2.2 Satisficing vs Maximizing

From Herbert Simon's bounded rationality:

```
IF (Marginal Analysis Cost > Marginal Utility)
AND (Decision is Reversible)
THEN: Execute "Good Enough" immediately
```

### 2.3 Parallel Processing Model

For non-trivial problems, maintain multiple reasoning tracks:

| Track | Function |
|-------|----------|
| A (Domain) | Apply arena-specific protocols |
| B (Adversarial) | Challenge premises, find flaws |
| C (Cross-Domain) | Search for isomorphic patterns |

Synthesize before output.

## 3. Application in AI Systems

These principles inform:

- **Prompt engineering** (clarity > complexity)
- **Guardrail design** (prevent irreversible actions)
- **Feedback loops** (calibrate based on outcomes, not intentions)

---

# concept #cognitive-architecture #ai-human-collaboration #psychology
