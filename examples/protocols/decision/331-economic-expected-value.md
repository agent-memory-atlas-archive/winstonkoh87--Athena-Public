---
created: 2026-02-23
last_updated: 2026-02-23
red_team_score_v1: 30/100
red_team_score_v2: 72/100
red_team_revised: true
---

# Protocol 331: Economic Expected Value (EEV) — Utility-Weighted Decision Framework

> **Category**: Decision Making / Risk Management
> **Tags**: #utility #expected-value #probability #kelly #ergodicity #friedman-savage
> **Related**: [Protocol 001: Law of Ruin], [Protocol 193: Ergodicity Check], [Protocol 245: Value Trinity]
> **Academic Lineage**: Bernoulli (1738) → von Neumann & Morgenstern (1944) → Friedman & Savage (1948) → Kahneman & Tversky (1979)

---

## 1. Core Concept

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

## 2. Case Study A: The $12M TOTO Draw (The Rational Lottery)

### The Setup

- **Game**: Singapore TOTO 6/49 (Hong Bao Draw, 27 Feb 2026)
- **Odds of Group 1**: 1 in 13,983,816 — C(49,6) ([Source: Singapore Pools](https://www.singaporepools.com.sg))
- **Ticket cost**: $1 SGD (Ordinary Entry)
- **House edge**: ~46% (only 54% of sales enter the prize pool; [Source: DollarsAndSense.sg](https://dollarsandsense.sg))
- **Historical adjusted EV per ticket**: ~$0.54 ([Source: DollarsAndSense.sg analysis](https://dollarsandsense.sg))

### Math EV (Negative)

```
EV = $0.54 - $1.00 = -$0.46 per ticket
```

Mathematically, you lose 46 cents for every dollar played. A "bad bet" by linear analysis.

### EEV Analysis (Friedman-Savage Framework)

The utility function is **convex** at this segment of the wealth curve (middle income → financial sovereignty):

- **U(Lose $1)**: Negligible. For a working adult with positive net worth, $1 does not alter any life outcome, decision surface, or opportunity set.
- **U(Win $12M)**: Discontinuous phase transition — financial sovereignty, exit optionality, generational security. The utility gain is not 12M× the cost; it occupies a fundamentally different region of the utility curve.

```
EEV = [1/13.9M × U(phase transition)] - [~1.0 × U(negligible)]
    = [Small positive] - [~0]
    = Positive
```

### The Insurance Analogy (Kahneman & Tversky, 1979)

Both insurance and lottery tickets are negative Math EV. Both are positive EEV:

| Product | Math EV | EEV | Mechanism |
|---------|---------|-----|-----------|
| **Insurance** | Negative | Positive | You pay a premium to avoid catastrophic loss (left tail) |
| **$1 TOTO ticket** | Negative | Positive | You pay a premium to access a phase transition (right tail) |

> **Citation**: Kahneman, D. & Tversky, A. (1979). "Prospect Theory: An Analysis of Decision under Risk." *Econometrica*, 47(2), 157–185. — Prospect theory adds that people systematically **overweight** small probabilities, which further explains lottery appeal beyond pure utility calculus.

---

## 3. Case Study B: The Tight Stop Loss Trap

### The Setup (Observed: 22 Feb 2026, BTCUSD 1H)

- **Bankroll**: $10,000
- **Setup**: Long entry near Bollinger Band boundary (~$68,200)
- **Bollinger Band width (observed)**: ~$1,100 ($68,481 upper – $67,375 lower)
- **Proposed SL**: $500

### Why This Is -EEV (Even With a Valid Thesis)

By setting SL = $500 inside a noise band of $1,100:

- The stop is placed **inside normal volatility**. The market routinely moves $1,100 within the BB range without any change in structural value.
- **P(Stop-Out by Noise)** becomes disproportionately high — the thesis never gets a chance to play out.
- **U($500 loss)**: At 5% of bankroll, this carries real financial weight and psychological cost (the "Dignity Premium").

**Result**: A structurally valid thesis (+Math EV setup) is converted into a -EEV gamble by inadequate structure.

### The Volatility Gate Rule (Correct Approach)

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

## 4. Guardrails & Kill Switches

### 4.1 The Sorites Paradox (Threshold Creep Prevention)

> **The Problem**: If U($1) ≈ 0, then U($2) ≈ 0, then U($5) ≈ 0... by induction, any amount approaches zero disutility. This is the [Sorites Paradox](https://en.wikipedia.org/wiki/Sorites_paradox) of utility, and it leads to the exact System 12 ($924) behavior this framework was designed to prevent.

**Hard Boundary**: EEV-positive lottery play is capped at **$1 per draw, maximum 1 ticket per draw.** Any amount above this exits the convex segment of the Friedman-Savage curve and enters the concave region where losses carry real disutility. This is not a sliding scale; it is a binary gate.

### 4.2 The Compounding Opportunity Cost (The Skeptic's Fix)

> **The Attack**: $1/draw × 2 draws/week × 40 years = $4,160 principal. At 7% compound, this equals ~$22,000 in lost returns. This is not "zero."

**Mitigation (The "Found Money" Rule)**: The lottery ticket should be funded exclusively from **windfall or passive yield** (e.g., credit card cashback, staking rewards, pocket change). Never from labor income or investable capital. This preserves the "zero disutility" premise by ensuring the money was never part of the compounding base.

### 4.3 The Addiction Firewall (The Victim's Shield)

> **The Attack**: This framework gives intellectual cover to gambling addicts. "Structurally rational" becomes the first brick in a relapse pathway.

**Hard Rule**: If any of the following are true, this protocol is **automatically voided**:

- Buying >1 ticket per draw
- Spending >$10/month on lottery across all games
- Using the word "rational" to justify increased stake sizes
- Feeling disappointment (not indifference) upon losing

If disappointment is present, U(Cost) ≠ 0, and the EEV framework no longer applies. The activity has crossed from speculation into gambling pathology.

### 4.4 The Regressive Tax Acknowledgment

> **Citation**: Studies consistently show that lower-income individuals spend a disproportionately larger share of income on lottery tickets. For these individuals, U($1) may NOT be zero — it represents a higher fraction of disposable income with genuine opportunity cost.

**Scope Limitation**: This protocol's "+EEV" conclusion applies only to individuals for whom the ticket cost is genuinely negligible relative to net worth and income. **It is not universal.** For individuals at the lower end of the wealth distribution, the standard concave utility framework applies, and lottery participation is -EEV.

---

## 5. The Unified Decision Rule

### The EEV Boundary Test

Before committing capital to any asymmetric bet, run this test:

| Question | Yes → | No → |
|----------|-------|------|
| Is the cost genuinely **utility-invisible** to me? | Proceed to next | **Stop. This is gambling.** |
| Is the upside a **phase transition** (different wealth class)? | Proceed to next | Math EV applies instead |
| Is the cost funded from **found money / yield**? | Proceed to next | Reframe or abstain |
| Can I feel **complete indifference** if I lose? | **+EEV. Execute.** | U(Cost) ≠ 0. **Abstain.** |

### For Trading (The Volatility Gate)

| Question | Yes → | No → |
|----------|-------|------|
| Is my SL **outside** the noise band (≥ 1× ATR/BB width)? | Proceed | **Do not trade.** |
| Can my bankroll sustain this SL at **Half-Kelly sizing**? | Proceed | Reduce position or abstain |
| Does this SL represent **< 5% of bankroll** after position sizing? | **+EEV. Execute.** | **Undercapitalized. Do not trade.** |

---

## 6. Summary

| Framework | What It Says | When to Use |
|-----------|-------------|-------------|
| **Math EV** | Linear dollar expectation | Repeated, high-frequency bets where law of large numbers applies |
| **EEV (Friedman-Savage)** | Utility-weighted expectation across the wealth curve | One-shot or rare asymmetric bets where the utility function is non-linear |
| **Prospect Theory (K&T)** | People overweight small probabilities | Explains *why* people buy lottery tickets — use as a bias check, not a justification |

> **The Golden Rule**: A bet is +EEV only when the cost occupies the **concave floor** of your utility curve (invisible loss) AND the gain occupies the **convex inflection** (phase transition). The moment either condition breaks, Math EV governs, and the house wins.
