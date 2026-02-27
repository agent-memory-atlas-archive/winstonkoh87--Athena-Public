---
created: 2026-02-02
last_updated: 2026-02-28
version: 3.0
origin: Session 05 (Blackjack Probability Analysis), Session 32 (GTO EEV Formalization), Session 33 (Friedman-Savage Red Team)
dependencies: [Law #1, Protocol 193 (Ergodicity Check), Protocol 180 (Utility Function Analysis)]
tags: [decision, utility, risk, gambling, speculation, rationality, gto, eev, limit-point, friedman-savage, prospect-theory]
note: "Merged from Protocol 330 + Protocol 331 (2026-02-28)"
---

# Protocol 330: Economic Expected Value (EEV) — Unified Framework

> **Purpose**: Integrate quantitative (financial) and qualitative (experiential) returns into a single GTO decision metric.
> **Prime Directive**: Law #1 (No Ruin) — Veto any action with >5% Risk of Ruin, regardless of E(EV).
> **Core Theorem**: Economic EV = Math EV + Utility EV. The optimal investment Limit Point occurs where EEV = 0.
> **Academic Lineage**: Bernoulli (1738) → von Neumann & Morgenstern (1944) → Friedman & Savage (1948) → Kahneman & Tversky (1979)
> **Related**: [Protocol 001: Law of Ruin], [Protocol 193: Ergodicity Check], [Protocol 180: Utility Function Analysis], [Protocol 245: Value Trinity]

---

## 1. Core Concept: Why Math EV Is Insufficient

### The Problem with Mathematical EV

The standard decision model under uncertainty is **Mathematical Expected Value (Math EV)**:

```
Math EV = [P(Win) × Payout] - [P(Lose) × Cost]
```

**The Flaw**: Math EV treats all dollars as linear. It assumes losing $1 hurts exactly 12,000,000× less than losing $12M. In reality, the subjective value of money is **non-linear** — a fact established by Daniel Bernoulli in 1738.

### The Correct Framework: Economic Expected Value (EEV)

EEV introduces a **utility function** U(x) that captures the subjective, non-linear value of money:

```
EEV = [P(Win) × U(Gain)] - [P(Lose) × U(Cost)]
```

> **Key Distinction**: Math EV answers *"What is the expected dollar return?"* EEV answers *"What is the expected change in my life quality?"*

### The Friedman-Savage Utility Function (1948)

> **Citation**: Friedman, M. & Savage, L.J. (1948). "The Utility Analysis of Choices Involving Risk." *Journal of Political Economy*, 56(4), 279–304.

Standard economic theory assumes a **concave** utility function (diminishing marginal utility of wealth), which predicts that rational agents should *never* buy lottery tickets. Yet millions of people simultaneously buy lottery tickets (risk-seeking) and insurance (risk-averse).

Friedman & Savage resolved this paradox with a **double-inflection utility function**:

- **Concave** at low wealth (risk-averse: buy insurance)
- **Convex** at a middle range (risk-seeking: buy lottery tickets for a chance to jump to a higher wealth class)
- **Concave** again at high wealth (risk-averse: protect existing wealth)

**This is the theoretical foundation of EEV.** The lottery ticket is not "irrational." It is a rational response to the convex segment of the utility curve — the desire to make a **phase transition** from one wealth class to another.

> **Important**: This is NOT the same as standard concave utility theory. Under pure concave utility, lotteries are always irrational. The Friedman-Savage model explains *why* people rationally seek both insurance and lottery exposure.

---

## 2. The Formula

$$E(EV) = E(V) + E(U) - E(O)$$

| Symbol | Name | Definition |
|:---|:---|:---|
| **E(V)** | Expected Financial Value | Net monetary return per time unit ($/hr) |
| **E(U)** | Expected Utility Value | Hedonic/experiential value converted to $/hr |
| **E(O)** | Expected Opportunity Cost | Value of the next-best alternative use of time ($/hr) |

---

## 3. The Three-Line EEV Model

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

## 4. Step-by-Step Calculation

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

## 5. Decision Matrix

| Step | Check | Action |
|:---|:---|:---|
| **1. Law #1 Veto** | RoR > 5%? | ❌ **REJECT** (No exceptions) |
| **2. Variance Tax** | High variance activity? | Add **10% stress tax** to E(V) |
| **3. E(EV) Calculation** | E(EV) < 0? | ❌ **REJECT** |
| **4. E(EV) Calculation** | E(EV) = 0? | ⚖️ **NEUTRAL** (Indifferent) |
| **5. E(EV) Calculation** | E(EV) > 0 AND RoR ≤ 5%? | ✅ **ACCEPT** |

---

## 6. Safety Patches

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

## 7. Guardrails & Kill Switches

### 7.1 Kill Switches (Protocol-Level Abort)

**ABANDON this framework immediately if:**

1. **Actual Liquid Net Worth drops by >10%** in a single month while following this protocol.
   - *Indicates*: RoR calculation was flawed or variance is unmanageable.

2. **Post-activity regret consistently exceeds pre-activity anticipation.**
   - *Indicates*: E(U) is chronically mis-estimated.

3. **E(U) becomes the dominant swing variable in >80% of decisions.**
   - *Indicates*: Framework is being gamed to rationalize bad decisions.

### 7.2 The Sorites Paradox (Threshold Creep Prevention)

> **The Problem**: If U($1) ≈ 0, then U($2) ≈ 0, then U($5) ≈ 0... by induction, any amount approaches zero disutility. This is the [Sorites Paradox](https://en.wikipedia.org/wiki/Sorites_paradox) of utility, and it leads to the exact System 12 ($924) behavior this framework was designed to prevent.

**Hard Boundary**: EEV-positive lottery play is capped at **$1 per draw, maximum 1 ticket per draw.** Any amount above this exits the convex segment of the Friedman-Savage curve and enters the concave region where losses carry real disutility. This is not a sliding scale; it is a binary gate.

### 7.3 The Compounding Opportunity Cost (The Skeptic's Fix)

> **The Attack**: $1/draw × 2 draws/week × 40 years = $4,160 principal. At 7% compound, this equals ~$22,000 in lost returns. This is not "zero."

**Mitigation (The "Found Money" Rule)**: The lottery ticket should be funded exclusively from **windfall or passive yield** (e.g., credit card cashback, staking rewards, pocket change). Never from labor income or investable capital. This preserves the "zero disutility" premise by ensuring the money was never part of the compounding base.

### 7.4 The Addiction Firewall (The Victim's Shield)

> **The Attack**: This framework gives intellectual cover to gambling addicts. "Structurally rational" becomes the first brick in a relapse pathway.

**Hard Rule**: If any of the following are true, this protocol is **automatically voided**:

- Buying >1 ticket per draw
- Spending >$10/month on lottery across all games
- Using the word "rational" to justify increased stake sizes
- Feeling disappointment (not indifference) upon losing

If disappointment is present, U(Cost) ≠ 0, and the EEV framework no longer applies. The activity has crossed from speculation into gambling pathology.

### 7.5 The Regressive Tax Acknowledgment

> **Citation**: Studies consistently show that lower-income individuals spend a disproportionately larger share of income on lottery tickets. For these individuals, U($1) may NOT be zero — it represents a higher fraction of disposable income with genuine opportunity cost.

**Scope Limitation**: This protocol's "+EEV" conclusion applies only to individuals for whom the ticket cost is genuinely negligible relative to net worth and income. **It is not universal.** For individuals at the lower end of the wealth distribution, the standard concave utility framework applies, and lottery participation is -EEV.

---

## 8. Quick Decision Gates

### The EEV Boundary Test (Asymmetric Bets)

Before committing capital to any asymmetric bet, run this test:

| Question | Yes → | No → |
|----------|-------|------|
| Is the cost genuinely **utility-invisible** to me? | Proceed to next | **Stop. This is gambling.** |
| Is the upside a **phase transition** (different wealth class)? | Proceed to next | Math EV applies instead |
| Is the cost funded from **found money / yield**? | Proceed to next | Reframe or abstain |
| Can I feel **complete indifference** if I lose? | **+EEV. Execute.** | U(Cost) ≠ 0. **Abstain.** |

### The Volatility Gate (Trading)

| Question | Yes → | No → |
|----------|-------|------|
| Is my SL **outside** the noise band (≥ 1× ATR/BB width)? | Proceed | **Do not trade.** |
| Can my bankroll sustain this SL at **Half-Kelly sizing**? | Proceed | Reduce position or abstain |
| Does this SL represent **< 5% of bankroll** after position sizing? | **+EEV. Execute.** | **Undercapitalized. Do not trade.** |

---

## 9. Case Studies

| Case Study | Application | Limit Point |
|:---|:---|:---|
| **CS-A: TOTO EEV Convergence** | Lottery ticket purchase for median SG earner ($5.5K/mth) | $16 (EEV = 0) |
| **CS-B: BTCUSD Tight Stop Loss** | Structure > thesis: SL inside noise band = -EEV | N/A (binary: trade/don't trade) |
| **CS-C: Ultimatum Game Dignity Tax** | Rejecting unfair offers despite +MEV | ~30% offer (Dignity Cost = Monetary Gain) |
| **CS-D: Entertainment Blackjack** | Micro-stakes during dead time | E(EV) = +$2.38/hr |

### CS-A: The $12M TOTO Draw (The Rational Lottery)

**Setup:**

- **Game**: Singapore TOTO 6/49 (Hong Bao Draw, 27 Feb 2026)
- **Odds of Group 1**: 1 in 13,983,816 — C(49,6) ([Source: Singapore Pools](https://www.singaporepools.com.sg))
- **Ticket cost**: $1 SGD (Ordinary Entry)
- **House edge**: ~46% (only 54% of sales enter the prize pool; [Source: DollarsAndSense.sg](https://dollarsandsense.sg))
- **Historical adjusted EV per ticket**: ~$0.54 ([Source: DollarsAndSense.sg analysis](https://dollarsandsense.sg))

**Math EV (Negative):**

```
EV = $0.54 - $1.00 = -$0.46 per ticket
```

Mathematically, you lose 46 cents for every dollar played. A "bad bet" by linear analysis.

**EEV Analysis (Friedman-Savage Framework):**

The utility function is **convex** at this segment of the wealth curve (middle income → financial sovereignty):

- **U(Lose $1)**: Negligible. For a working adult with positive net worth, $1 does not alter any life outcome, decision surface, or opportunity set.
- **U(Win $12M)**: Discontinuous phase transition — financial sovereignty, exit optionality, generational security. The utility gain is not 12M× the cost; it occupies a fundamentally different region of the utility curve.

```
EEV = [1/13.9M × U(phase transition)] - [~1.0 × U(negligible)]
    = [Small positive] - [~0]
    = Positive
```

**The Insurance Analogy (Kahneman & Tversky, 1979):**

Both insurance and lottery tickets are negative Math EV. Both are positive EEV:

| Product | Math EV | EEV | Mechanism |
|---------|---------|-----|-----------|
| **Insurance** | Negative | Positive | You pay a premium to avoid catastrophic loss (left tail) |
| **$1 TOTO ticket** | Negative | Positive | You pay a premium to access a phase transition (right tail) |

> **Citation**: Kahneman, D. & Tversky, A. (1979). "Prospect Theory: An Analysis of Decision under Risk." *Econometrica*, 47(2), 157–185. — Prospect theory adds that people systematically **overweight** small probabilities, which further explains lottery appeal beyond pure utility calculus.

---

### CS-B: The Tight Stop Loss Trap (BTCUSD 1H)

**Setup (Observed: 22 Feb 2026):**

- **Bankroll**: $10,000
- **Setup**: Long entry near Bollinger Band boundary (~$68,200)
- **Bollinger Band width (observed)**: ~$1,100 ($68,481 upper – $67,375 lower)
- **Proposed SL**: $500

**Why This Is -EEV (Even With a Valid Thesis):**

By setting SL = $500 inside a noise band of $1,100:

- The stop is placed **inside normal volatility**. The market routinely moves $1,100 within the BB range without any change in structural value.
- **P(Stop-Out by Noise)** becomes disproportionately high — the thesis never gets a chance to play out.
- **U($500 loss)**: At 5% of bankroll, this carries real financial weight and psychological cost (the "Dignity Premium").

**Result**: A structurally valid thesis (+Math EV setup) is converted into a -EEV gamble by inadequate structure.

**The Volatility Gate Rule (Correct Approach):**

> **Rule**: Do not define risk by "percentage of account." Define risk by **market physics** (volatility / noise width).

```
Minimum Viable SL = f(Noise Width, Timeframe)
If Bankroll < 3 × Noise Width → DO NOT TRADE (undercapitalized)
```

For this specific setup:

- **Required SL** ≥ $1,100 (1× BB width, minimum)
- **Conservative SL** = $1,500–$1,650 (1.5× BB width)
- **Kelly-adjusted position size**: At $1,500 SL on a $10K bankroll (15% risk), **the position must be reduced** to respect the Kelly Criterion:

```
Kelly % = (WR × RR - (1 - WR)) / RR
Half-Kelly = Kelly% / 2  (standard conservative adjustment)
```

If your edge yields Kelly = 10%, then Half-Kelly = 5%, and your maximum position = **$500 risk** — which means you need to **trade a smaller position** with the $1,500 SL width, not a full position with a $500 SL width.

> **The Pivot**: *"I will not trade this setup because I cannot afford the stop loss required to let the thesis play out."* — This is the highest EEV decision a trader can make.

---

### CS-C: The Ultimatum Game (Why MEV Breaks)

MEV predicts: Accept any offer > $0 (even 0.1%).
Reality: Offers below ~30% are rejected by the majority.

**EEV Explanation**: Accepting an insulting offer generates severe **negative UEV** (humiliation, loss of dignity). At the ~30% threshold, the monetary gain from MEV exactly equals the dignity cost from UEV. Below 30%, EEV < 0 → Reject. Above 30%, EEV > 0 → Accept.

This is structurally identical to the TOTO Limit Point — both are solved by finding where $E(V) + E(U) = 0$.

---

### CS-D: Entertainment Blackjack

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

## 10. The Barbell Maximizer (Optimization Strategy)

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

## 11. Key Insights

1. **Humans maximize Utility, not Dollars.** The math of E(V) ignores the joy of playing.
2. **Subjective Utility must be constrained** to prevent rationalization (Skeptic's Discount).
3. **Opportunity Cost is often zero** during rest blocks, commuting, or low-energy states.
4. **Law #1 is non-negotiable.** Even a massively positive E(EV) is rejected if RoR > 5%.
5. **Sample Size matters.** In +EV systems, P(Profit) increases with $N$. In -EV systems, P(Ruin) increases with $N$.
6. **MEV alone cannot solve human games.** The Ultimatum Game, lottery purchases, and insurance are all -MEV but +EEV decisions.
7. **The Limit Point is the operational boundary.** Every dollar past the EEV = 0 intersection is pure wealth destruction.
8. **UEV peaks instantly.** The derivative dy/dx = 0 occurs at the point of option acquisition, not at higher spend levels.

---

## 12. Summary

| Framework | What It Says | When to Use |
|-----------|-------------|-------------|
| **Math EV** | Linear dollar expectation | Repeated, high-frequency bets where law of large numbers applies |
| **EEV (Friedman-Savage)** | Utility-weighted expectation across the wealth curve | One-shot or rare asymmetric bets where the utility function is non-linear |
| **Prospect Theory (K&T)** | People overweight small probabilities | Explains *why* people buy lottery tickets — use as a bias check, not a justification |

> **The Golden Rule**: A bet is +EEV only when the cost occupies the **concave floor** of your utility curve (invisible loss) AND the gain occupies the **convex inflection** (phase transition). The moment either condition breaks, Math EV governs, and the house wins.

---

## References

- [Protocol 193: Ergodicity Check](../decision/193-ergodicity-check.md)
- [Protocol 180: Utility Function Analysis](../decision/180-utility-function-analysis.md)
- [Protocol 245: Value Trinity](../decision/245-value-trinity.md)
- [Core Identity: Law #1](../../framework/Core_Identity.md)
- Friedman, M. & Savage, L.J. (1948). "The Utility Analysis of Choices Involving Risk." *Journal of Political Economy*, 56(4), 279–304.
- Kahneman, D. & Tversky, A. (1979). "Prospect Theory: An Analysis of Decision under Risk." *Econometrica*, 47(2), 157–185.
- Bernoulli, D. (1738). "Specimen Theoriae Novae de Mensura Sortis." *Commentarii Academiae Scientiarum Imperialis Petropolitanae*, 5, 175–192.

---

# decision #utility #risk #gambling #speculation #rationality #gto #eev #limit-point #friedman-savage #prospect-theory
