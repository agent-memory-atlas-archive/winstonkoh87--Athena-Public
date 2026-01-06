# 🔺 Tri-Lateral Iteration Engine

> **Protocol 171: Cross-Model Validation**  
> **Status**: Active  
> **Category**: Verification

---

## The Core Insight

> *"Confidence ≈ Σ(convergence × independence × evidence).  
> Risk lives in Δ(disagreement) and in shared blind spots."*

No single LLM is infallible. The Tri-Lateral Iteration Engine uses multiple state-of-the-art models as **adversarial peer reviewers** to catch blind spots before they become costly mistakes.

**The principle**: When independent models *converge* on the same conclusion, confidence rises—but convergence alone is not proof. Models share training data and RLHF incentives, so they can converge on the same wrong answer. **Convergence suggests confidence. Evidence confirms it.**

---

## When to Use

| Trigger | Action |
|:---|:---|
| High-stakes decision (>$10K impact) | Mandatory cross-validation |
| Quantitative analysis (NPV, probabilities) | At least 2 models |
| Novel/unfamiliar domain | 3+ models recommended |
| Contradicts prior belief | External validation required |
| Irreversible / path-dependent | Validate even if <$10K |
| High fact density (dates, laws, regulations) | Mandatory—LLMs hallucinate facts |

---

## The 3-Phase Loop

### Phase 1: Genesis (Primary Model)

Build the initial analysis with your primary model (e.g., Claude Opus for deep reasoning or Gemini for speed).

- Frame the context and hypothesis
- Generate the first complete draft
- User inspects: Is this high-stakes? If yes → **Go to Phase 2**

### Phase 2: Adversarial Audit (External Models)

Send the draft to **independent** SOTA models for red-teaming.

**Prompt template** (hardened for real critique):  
> *"Act as a hostile regulatory auditor and a pessimistic investor. Your goal is to kill this deal. Review the following analysis and list the top 3 existential risks the author ignored. Be ruthless."*

Use [LMArena](https://lmarena.ai) for free access to frontier models (Gemini, GPT, Grok, etc.).

> ⚠️ **Data Handling**: Do not send PII or confidential deal terms to public sandboxes. For sensitive work, use enterprise API accounts or internal deployments.

### Phase 2.5: Evidence Pass (Required for High-Stakes)

Models validate *reasoning*, but many errors are **fact errors** (regulations, unit economics, market size). This phase grounds the analysis in primary sources.

1. **Identify** the 5 "load-bearing assumptions" — facts the conclusion depends on
2. **Verify** each with:
   - Primary source / official document
   - Direct measurement / call / quote
   - Or mark explicitly as "unknown" + run sensitivity analysis
3. **Flag** any assumption that cannot be verified — it's a risk, not a fact

### Phase 3: Synthesis

Compare outputs and categorize:

| Pattern | Meaning | Action |
|:---|:---|:---|
| **All Converge** | High confidence | Proceed (with documented assumptions) |
| **All Diverge** | Edge case / novel territory | Human arbiter decides |
| **Partial Agreement** | Nuance required | Investigate the delta |

---

## Visual Architecture

```
╔═══════════════════════════════════════════════════════════════════════════╗
║                    TRI-LATERAL ITERATION ENGINE                           ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                           ║
║  ┌─────────────────────────────────────────────────────────────────────┐  ║
║  │  PHASE 1: GENESIS                                                   │  ║
║  │  ┌──────────────┐                                                   │  ║
║  │  │ User Query   │──────►┌──────────────────┐                        │  ║
║  │  └──────────────┘       │  Primary Model   │                        │  ║
║  │                         │  • Deep context  │                        │  ║
║  │                         │  • Full reasoning│                        │  ║
║  │                         └────────┬─────────┘                        │  ║
║  └──────────────────────────────────┼──────────────────────────────────┘  ║
║                                     ▼                                     ║
║  ┌─────────────────────────────────────────────────────────────────────┐  ║
║  │  PHASE 2: ADVERSARIAL AUDIT                                         │  ║
║  │          ┌─────────────────┐     ┌─────────────────┐                │  ║
║  │          │    Model B      │     │    Model C      │                │  ║
║  │          │ "Red team this" │     │ "What's wrong?" │                │  ║
║  │          └────────┬────────┘     └────────┬────────┘                │  ║
║  │                   └───────────┬───────────┘                         │  ║
║  │                               ▼                                     │  ║
║  │                    ┌──────────────────────┐                         │  ║
║  │                    │  Critique Synthesis  │                         │  ║
║  │                    │  • Safety gaps       │                         │  ║
║  │                    │  • Missing nuance    │                         │  ║
║  │                    │  • Wrong assumptions │                         │  ║
║  │                    └──────────┬───────────┘                         │  ║
║  └───────────────────────────────┼─────────────────────────────────────┘  ║
║                                  ▼                                        ║
║  ┌─────────────────────────────────────────────────────────────────────┐  ║
║  │  PHASE 3: SYNTHESIS                                                 │  ║
║  │                    ┌──────────────────────┐                         │  ║
║  │                    │  Convergence Check   │                         │  ║
║  │                    └──────────┬───────────┘                         │  ║
║  │              ┌────────────────┼────────────────┐                    │  ║
║  │              ▼                ▼                ▼                    │  ║
║  │     ┌────────────────┐ ┌────────────┐ ┌────────────────┐            │  ║
║  │     │ ALL CONVERGE   │ │  DIVERGE   │ │ PARTIAL AGREE  │            │  ║
║  │     │ = High Conf.   │ │ = Edge Case│ │ = Investigate  │            │  ║
║  │     └───────┬────────┘ └─────┬──────┘ └───────┬────────┘            │  ║
║  │             │                ▼                │                     │  ║
║  │             │       ┌────────────────┐        │                     │  ║
║  │             │       │ Human Arbiter  │◄───────┘                     │  ║
║  │             │       └───────┬────────┘                              │  ║
║  │             └───────────────┼───────────────────┘                   │  ║
║  └─────────────────────────────┼───────────────────────────────────────┘  ║
║                                ▼                                          ║
║  ╔═════════════════════════════════════════════════════════════════════╗  ║
║  ║  OUTPUT: Truth ≈ Σ(convergent) + Δ(divergent to investigate)        ║  ║
║  ╚═════════════════════════════════════════════════════════════════════╝  ║
╚═══════════════════════════════════════════════════════════════════════════╝

Quality = f(Primary Depth × Adversarial Diversity × Synthesis Discipline)
```

---

## Case Study: BCM Due Diligence

**Scenario**: Friend asks for $25,000 investment in a Bak Chor Mee (minced meat noodle) stall.

**Phase 1 (Claude Opus 4.5)**:

- Failure probability: 15%
- Best case probability: 20%
- Expected NPV: +$9,600

**Phase 2 (Gemini 3 Pro + Grok 4.1)**:

- Identified regulatory kill-switch (NEA license = personal to holder)
- Added operator "Living Wage" draw as priority expense
- Highlighted cash skim risk in cash-based businesses

**Phase 2.5 (Evidence Pass)**:

- Verified NEA licensing rules (primary source: NEA website)
- Confirmed hawker rental rates (primary source: NEA tender results)
- Marked "cash skim percentage" as unverifiable — ran sensitivity analysis

**Phase 3 (Synthesis)**:

- Failure probability: **40%** (+25%)
- Best case probability: **5%** (-15%)
- Expected NPV: **-$7,300** (NPV FLIPPED)

> **Model**: NPV computed over 36 months; discount rate 12%; base/best/worst scenarios  
> **Key Assumptions**: daily covers, margin, rent, wage draw, license constraint  
> **Sensitivity**: NPV flips negative if margin <X% or operator wage draw >$Y/mo

**Outcome**: Cross-validation caught **$16,900 of decision error**. Verdict changed from "marginal yes" to **"hard veto."**

---

## Anti-Patterns

| ❌ Don't | ✅ Do |
|:---|:---|
| Cherry-pick agreeing models | Use blind selection |
| Ignore disagreement | Investigate divergence |
| Only validate "risky" choices | Validate surprising confirmations too |
| Skip for "simple" decisions | Simple decisions have hidden complexity |
| Treat convergence as proof | Treat convergence as a *prior* until evidence confirms |
| Share sensitive data to public tools | Use approved/secured environments for audits |

---

## Why This Works

1. **Different Training Biases**: Claude, Gemini, and GPT have different training data and RLHF tuning. Their blind spots don't overlap perfectly.

2. **Adversarial Pressure**: Asking "what's wrong?" activates different reasoning paths than asking "is this right?"

3. **Convergence as Signal**: Independent agreement is statistically harder to fake than single-model confidence.

4. **Human Remains in Loop**: The engine doesn't decide — it surfaces the *delta* for human judgment.

### Known Limitation

> Agreement among models is not proof. Shared training data (Common Crawl, similar RLHF incentives) can create **correlated errors**. Convergence raises confidence only when claims survive external evidence checks (Phase 2.5).

---

## References

- [LMArena](https://lmarena.ai/) — Free SOTA model access for blind comparison
- [Protocol 75: Synthetic Parallel Reasoning](examples/protocols/decision/75-synthetic-parallel-reasoning.md) — Single-model multi-track reasoning

---

*This protocol was formalized December 2025 after observing consistent accuracy improvements from multi-model validation in high-stakes decisions.*
