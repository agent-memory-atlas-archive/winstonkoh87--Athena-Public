---
created: 2026-03-04
last_updated: 2026-03-04
cluster: 15
---

# Protocol 504: Problem Framing (The 55-Minute Discipline)

> **Status**: ACTIVE  
> **Priority**: ⭐⭐⭐  
> **Principle**: "If I had 60 minutes to solve a problem, I'd spend 55 defining it and 5 solving it." — Einstein  

---

## Core Axiom

Most problem-solving fails at diagnosis, not treatment. The protocol enforces a **mandatory framing phase** before any solution generation begins.

**Anti-Pattern**: Jumping straight to "how do I fix this?" before answering "what exactly is broken and why?"

---

## The 5-Gate Framework

### Gate 1: Stated vs Actual Problem

```
Stated Problem:   [What the user/client says is wrong]
Actual Problem:   [What the evidence shows is wrong]

Diagnostic Questions:
├─ "If I magically solved [stated problem], would the situation actually improve?"
├─ "When did this problem NOT exist? What changed?"
├─ "Who benefits from this problem remaining unsolved?"
└─ "Is this a problem or a symptom of a deeper problem?"

Output: Problem Statement v1 (may differ from stated problem)
```

### Gate 2: Constraint Enumeration

```
Hard Constraints (Physics — cannot be changed):
├─ Time:     [deadline, sequence dependencies]
├─ Capital:  [budget, runway, opportunity cost]
├─ Physics:  [laws, material limits, latency]
└─ Legal:    [regulations, contracts, obligations]

Soft Constraints (Policy — can be changed with effort):
├─ Org:      [team structure, approval chains]
├─ Cultural: [norms, expectations, status quo bias]
├─ Technical:[current stack, existing architecture]
└─ Political:[stakeholder preferences, power dynamics]

Key Question: "Which soft constraints are masquerading as hard constraints?"
→ These are the highest-leverage intervention points.
```

### Gate 3: Stakeholder Mapping

```
For each stakeholder:
├─ Who:          [name/role]
├─ Wants:        [stated goal]
├─ Actually Optimizes For: [revealed preference — observe actions, not words]
├─ Loses If Solved: [what do they sacrifice?]
└─ Veto Power:   [can they block the solution?]

Conflict Detection:
├─ Stakeholder A wants X, Stakeholder B wants ¬X → Zero-sum
├─ Resolution: Reframe as non-zero-sum OR pick a side
└─ If irreconcilable → Flag as design constraint, not bug
```

### Gate 4: Root Cause Isolation (5 Whys + Inversion)

```
Forward Chain (5 Whys):
├─ Why 1: [surface reason]
├─ Why 2: [mechanism behind it]
├─ Why 3: [structural cause]
├─ Why 4: [systemic cause]
└─ Why 5: [root cause / invariant]

Inversion (What Would Have To Be True):
├─ "For this problem to NOT exist, what would need to be true?"
├─ "Which of those conditions can we create?"
└─ "Which are impossible?" → These define the solution space boundary.

Output: Root Cause Statement + Solution Space Boundary
```

### Gate 5: Problem Statement Lock

```
Final Problem Statement (Template):

CONTEXT:  [situation and relevant history]
PROBLEM:  [root cause, not symptom]
SCOPE:    [what's in / what's out]
CONSTRAINTS: [hard only — soft constraints listed as levers]
SUCCESS:  [measurable exit criteria — how do we know it's solved?]
ANTI-GOALS: [what we explicitly do NOT want to optimize for]

Validation:
├─ Can someone unfamiliar with the context understand it? (Clarity)
├─ Does it match the root cause, not the stated problem? (Accuracy)
├─ Are the success criteria measurable? (Testability)
└─ Would solving this ACTUALLY improve the situation? (Relevance)

If any validation fails → Loop back to Gate 1.
```

---

## Timing Heuristic

| Problem Complexity | Framing Time | Solution Time | Ratio |
|---|---|---|---|
| SNIPER (Λ < 10) | 2 min | 3 min | 1:1.5 |
| STANDARD (Λ 10-30) | 15 min | 10 min | 1.5:1 |
| ULTRA (Λ > 30) | 55 min | 5 min | 11:1 |

> The higher the stakes, the more time goes to framing. Never invert this ratio.

---

## Co-Activation

- **Upstream**: Triggered by problem/challenge detection
- **Downstream**: Feeds into P505 (Graph of Thought) for solution exploration
- **Cluster**: #15 Problem-Solving Engine

---

## Cross-References

- [Protocol 115: First Principles Deconstruction](../decision/115-first-principles-deconstruction.md)
- [Protocol 505: Graph of Thought](505-graph-of-thought.md)
- [Protocol 506: GTO Execution Plan](506-gto-execution-plan.md)

---

## Tagging

# protocol #reasoning #problem-solving #framing #diagnosis #55-minutes
