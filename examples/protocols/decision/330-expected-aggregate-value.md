---
created: 2026-02-02
last_updated: 2026-02-28
version: 2.0
origin: Session 05 (Blackjack Probability Analysis), Session 32 (GTO EEV Formalization)
dependencies: [Law #1, Protocol 193 (Ergodicity Check), Protocol 180 (Utility Function Analysis)]
tags: [decision, utility, risk, gambling, speculation, rationality, gto, eev, limit-point]
---

# Protocol 330: Expected Economic Value (EEV) Framework

> **Purpose**: Integrate quantitative (financial) and qualitative (experiential) returns into a single GTO decision metric.
> **Prime Directive**: Law #1 (No Ruin) — Veto any action with >5% Risk of Ruin, regardless of E(EV).
> **Core Theorem**: Economic EV = Math EV + Utility EV. The optimal investment Limit Point occurs where EEV = 0.

---

## 1. The Formula

$$E(EV) = E(V) + E(U) - E(O)$$

| Symbol | Name | Definition |
|:---|:---|:---|
| **E(V)** | Expected Financial Value | Net monetary return per time unit ($/hr) |
| **E(U)** | Expected Utility Value | Hedonic/experiential value converted to $/hr |
| **E(O)** | Expected Opportunity Cost | Value of the next-best alternative use of time ($/hr) |

---

## 1B. The Three-Line EEV Model (v2.0)

EEV is not a single metric — it is the **synthesis** of two independent value curves:

| Line | Name | Type | Behavior |
|:---|:---|:---|:---|
| **MEV** | Mathematical Expected Value | Pure Quantitative | Fixed negative slope. Always drags value downward. |
| **UEV** | Utility Expected Value | Pure Qualitative | Non-linear. Spikes at low spend, decays, then crashes into negative at high spend. |
| **EEV** | Economic Expected Value | Combined GTO Metric | Sum of MEV + UEV. Crosses zero at the **Limit Point**. |

### The Limit Point

The **Limit Point** is the exact dollar amount ($X) where:

$$E(EV) = E(V) + E(U) - E(O) = 0$$

- **Left of Limit Point**: EEV > 0 → Rational. Proceed.
- **At Limit Point**: EEV = 0 → Breakeven. Maximum allowable spend.
- **Right of Limit Point**: EEV < 0 → Irrational. Wealth destruction.

### The UEV Calculus (Inverted Marginal Utility)

UEV operates on three distinct phases:

1. **Phase 1 — The Spike** ($0 → $1): UEV shoots up near-vertically. The **absolute maxima** (dy/dx = 0) occurs at the moment of acquiring the option. The 1st dollar buys 99% of the psychological utility.
2. **Phase 2 — The Slow Decay** ($1 → $10): UEV slopes downwards gently. Additional spend buys marginal probability but zero additional fantasy.
3. **Phase 3 — The Crash** ($10+): UEV plummets aggressively into negative territory. Financial anxiety, buyer's remorse, and cash drag destroy the psychological premium.

> ⚠️ **Critical**: UEV does NOT scale linearly. Buying 100 lottery tickets does not generate 100x the daydream of buying 1 ticket.

---

## 2. Step-by-Step Calculation

### Step 1: Calculate E(V) — Financial Value

$$E(V) = (\text{Win Rate} \times \text{Avg Win}) - (\text{Loss Rate} \times \text{Avg Loss})$$

**Example (Blackjack $0.01 units, 300 hands/hr):**

- House Edge: -0.5%
- E(V) = -0.005 × $0.01 × 300 = **-$0.015/hr**

---

### Step 2: Calculate E(U) — Utility Value

> **Method**: Comparable Anchor + Skeptic's Discount

1. List 3 **paid** entertainment activities you **actually** buy.
2. Assign their $/hr cost.
3. Rank the target activity relative to them.
4. **Apply Skeptic's Discount**: Multiply by **0.8** (humans overestimate future enjoyment).

| Activity | Cost/hr |
|:---|:---|
| Movie | $7.50 |
| Video Game | $0.60 |
| Bar/Club | $12.50 |

**Example**: "Blackjack is slightly more fun than a video game, less fun than a movie."

- Raw Estimate: $3.00/hr
- **Skeptic's Discount**: $3.00 × 0.8 = **E(U) = $2.40/hr**

> ⚠️ **Anti-Rationalization Rule**: E(U) anchors MUST be activities you have paid for in the last 90 days. No hypotheticals.

---

### Step 3: Calculate E(O) — Opportunity Cost

> **Method**: Marginal Wage Rate + Energy Modifier

**The Energy Constraint**:
Opportunity Cost can only be claimed IF you have the **energy** to execute the alternative work RIGHT NOW.

| Energy State | E(O) Calculation |
|:---|:---|
| **High Energy** (Could work productively) | E(O) = Your hourly rate |
| **Low Energy** (Tired, need rest) | **E(O) = $0** |
| **Dead Time** (Commuting, waiting) | **E(O) = $0** |

**Example (Playing on the bus while tired):**

- E(O) = **$0/hr** (No real alternative available)

> ⚠️ **Anti-Inflation Rule**: E(O) cannot exceed your **average** hourly rate over the last 30 days, not your theoretical peak rate.

---

### Step 4: Calculate E(EV)

$$E(EV) = E(V) + E(U) - E(O)$$

**Example:**

- E(V) = -$0.02/hr
- E(U) = +$2.40/hr (after Skeptic's Discount)
- E(O) = $0.00/hr
- **E(EV) = +$2.38/hr** → ✅ Proceed

---

## 3. Decision Matrix

| Step | Check | Action |
|:---|:---|:---|
| **1. Law #1 Veto** | RoR > 5%? | ❌ **REJECT** (No exceptions) |
| **2. Variance Tax** | High variance activity? | Add **10% stress tax** to E(V) |
| **3. E(EV) Calculation** | E(EV) < 0? | ❌ **REJECT** |
| **4. E(EV) Calculation** | E(EV) = 0? | ⚖️ **NEUTRAL** (Indifferent) |
| **5. E(EV) Calculation** | E(EV) > 0 AND RoR ≤ 5%? | ✅ **ACCEPT** |

---

## 4. Required Safety Patches

### A. The Skeptic's Discount (E(U))
>
> "Multiply your initial gut feeling by **0.8**. We historically overestimate how much fun a paid activity will be."

### B. The Energy Modifier (E(O))
>
> "Opportunity Cost can only be non-zero if you have the **specific energy level** required to perform the alternative work *right now*. If you are too tired to work, E(O) = $0."

### C. The Variance Tax
>
> "If the activity has high variance (gambling, crypto, speculation), increase the cost basis in E(V) by **10%** to account for the 'Stress Tax' and emotional volatility."

### D. The Anchor Constraint (E(U))
>
> "E(U) anchors must be activities you have **actually paid for** in the last 90 days. No hypothetical comparisons."

---

## 5. Kill Switch Conditions

**ABANDON this framework immediately if:**

1. **Actual Liquid Net Worth drops by >10%** in a single month while following this protocol.
   - *Indicates*: RoR calculation was flawed or variance is unmanageable.

2. **Post-activity regret consistently exceeds pre-activity anticipation.**
   - *Indicates*: E(U) is chronically mis-estimated.

3. **E(U) becomes the dominant swing variable in >80% of decisions.**
   - *Indicates*: Framework is being gamed to rationalize bad decisions.

---

## 6. Worked Example (Entertainment Blackjack)

| Variable | Value | Notes |
|:---|:---|:---|
| **Context** | $0.01 Martingale on Natural8 | Playing for entertainment |
| **Bankroll** | $20 | Disposable "fun money" |
| **RoR** | <2% | 2,000 units = durable |
| **E(V)** | -$0.02/hr | House edge on micro-stakes |
| **E(U) Raw** | $3.00/hr | "More fun than video games" |
| **E(U) Adjusted** | $2.40/hr | Apply 0.8 Skeptic's Discount |
| **E(O)** | $0/hr | Playing during "dead time" |
| **E(EV)** | **+$2.38/hr** | ✅ Proceed |

**Verdict**: Positive E(EV). RoR is low. Law #1 satisfied. **Play for fun.**

---

## 7. Key Insights

1. **Humans maximize Utility, not Dollars.** The math of E(V) ignores the joy of playing.
2. **Subjective Utility must be constrained** to prevent rationalization (Skeptic's Discount).
3. **Opportunity Cost is often zero** during rest blocks, commuting, or low-energy states.
4. **Law #1 is non-negotiable.** Even a massively positive E(EV) is rejected if RoR > 5%.
5. **Sample Size matters.** In +EV systems, P(Profit) increases with $N$. In -EV systems, P(Ruin) increases with $N$.
6. **MEV alone cannot solve human games.** The Ultimatum Game, lottery purchases, and insurance are all -MEV but +EEV decisions.
7. **The Limit Point is the operational boundary.** Every dollar past the EEV = 0 intersection is pure wealth destruction.
8. **UEV peaks instantly.** The derivative dy/dx = 0 occurs at the point of option acquisition, not at higher spend levels.

---

## 8. The Barbell Maximizer (Optimization Strategy)

To maximize the **E(EV) Curve** over a lifetime, you must solve for **Geometric Growth** (Compound Interest) minus **Volatility Drag**.

**The Mathematical Solution**: The 90/10 Barbell.

| Component | Allocation | Role | Effect on E(EV) |
|:---|:---|:---|:---|
| **The Anchor** | 90% | Low Variance, Low Yield (Cash/Bonds) | **Survival**. Prevents Ruin (Law #1). |
| **The Convexity** | 10% | High Variance, Infinite Upside (Speculation) | **Growth**. Captures outliers. |

**Why this Maximizes E(EV):**

1. **Safety**: The Anchor ensures you never hit an absorbing barrier (Ruin).
2. **Upside**: The Convexity ensures you participate in "Black Swan" positive events.
3. **Efficiency**: It avoids the "Mediocre Middle" (Medium Risk, Capped Reward) where Volatility Drag kills compounding.

> **Directive**: Bet 10-20% on +EV/High Variance. Keep 80-90% in Safe Harbor. This is the optimal frontier.

---

## 9. Case Studies

| Case Study | Application | Limit Point |
|:---|:---|:---|
| **CS-331: TOTO EEV Convergence** | Lottery ticket purchase for median SG earner ($5.5K/mth) | $16 (EEV = 0) |
| **CS-332: Ultimatum Game Dignity Tax** | Rejecting unfair offers despite +MEV | ~30% offer (Dignity Cost = Monetary Gain) |

### The Ultimatum Game (Why MEV Breaks)

MEV predicts: Accept any offer > $0 (even 0.1%).
Reality: Offers below ~30% are rejected by the majority.

**EEV Explanation**: Accepting an insulting offer generates severe **negative UEV** (humiliation, loss of dignity). At the ~30% threshold, the monetary gain from MEV exactly equals the dignity cost from UEV. Below 30%, EEV < 0 → Reject. Above 30%, EEV > 0 → Accept.

This is structurally identical to the TOTO Limit Point — both are solved by finding where $E(V) + E(U) = 0$.

---

## References

- [Protocol 193: Ergodicity Check](../decision/193-ergodicity-check.md)
- [Protocol 180: Utility Function Analysis](../decision/180-utility-function-analysis.md)
- [Core Identity: Law #1](../../framework/Core_Identity.md)

---

# decision #utility #risk #gambling #speculation #rationality #gto #eev #limit-point
