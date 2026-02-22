---
created: 2026-02-23
last_updated: 2026-02-23
---

# Protocol 331: Economic Expected Value (EEV) & Asymmetric Bets

> **Category**: Decision Making / Risk Management
> **Tags**: #utility #expected-value #probability #kelly #ergodicity
> **Related**: [Protocol 001: Law of Ruin], [Protocol 193: Ergodicity Check], [Protocol 245: Value Trinity]

## 1. Core Concept

The standard model for decision-making under uncertainty relies on **Mathematical Expected Value (Math EV)**:
`Math EV = [P(Win) × Payout] - [P(Lose) × Cost]`

**The Flaw**: Math EV assumes all dollars have equal weight (losing $1 hurts exactly 10,000 times less than losing $10,000). In reality, human utility is highly non-linear at the extremes.

The accurate decision model is **Economic Expected Value (EEV)**, which introduces a subjective utility function $U(x)$:
`EEV = [P(Win) × U(Payout)] - [P(Lose) × U(Cost)]`

> **Law of EEV**: A mathematically negative bet can be economically positive if the utility of the cost approaches zero and the utility of the payout approaches a phase transition (life-changing wealth/agency).

---

## 2. The $12M TOTO Paradox (The Rational Lottery)

Why buying exactly *one* ticket for a $12M jackpot is structurally rational, despite a 46% house edge.

* **Math EV**: `(1/13.9M × $12M) - $1.00 = -$0.14` (A mathematically bad bet).
* **Economic EV**: `[1/13.9M × U($12M)] - [~1.0 × U($1)]`

**The Utility Asymmetry**:

1. **$U(Cost)$**: For a working adult, losing $1 carries **zero disutility**. It alters no life outcomes.
2. **$U(Gain)$**: Winning $12M is not linear wealth; it is a **phase transition** (financial sovereignty, exit optionality).

Because $U(Cost)$ is functionally zero, the equation becomes `EEV = [Tiny Positive] - [0] = Positive`.

### The Behavioral Trap (When EEV Flips Negative)

If a player buys a "System 12" ticket for $924:

* $U($924)$ now carries real disutility (rent, food, investments).
* The equation flips negative. The player is no longer buying an asymmetric option; they are gambling.

---

## 3. The Tight Stop Loss Trap (The Irrational Speculation)

Why a $+EV$ trading setup becomes a guaranteed loss when the stop loss is too tight.

Consider a BTC trading setup on a $10,000 bankroll. A trader identifies a $+Math EV$ setup at the Bollinger Band boundary.

* **Stop Loss**: $500 (5% of bankroll).
* **Market Noise (Volatility)**: $1,100 wide.

**The Structural Mismatch**:

1. **$U(Cost)$**: A $500 loss carries real financial and psychological weight (The Dignity Premium).
2. **The Noise Factor**: Because the stop is placed inside the noise width, $P(Lose)$ approaches 1.0 (certainty of being stop-hunted by random volatility).

**Result**: The trader took a $+Math EV$ setup and converted it into a $-EEV$ gamble by refusing to pay the proper structural premium ($1,500) to survive the noise.

---

## 4. The Unified Rule of Asymmetric Bets

To evaluate if a bet is structurally sound, use the **EEV Boundary Test**:

1. **Speculation (+EEV)**: You identify an edge and pay the required premium (a $1,500 SL, or a $1 lottery ticket) to ensure system noise does not knock you out before the thesis plays out.
2. **Gambling (-EEV)**: You try to "get off cheap" (using a $500 SL inside market noise) or you pay too much premium on a lottery (buying $900 in tickets). You guarantee high-disutility losses.

**Execution Rule**: A decision is only structurally sound if the utility of the cost $U(Cost)$ is either **completely invisible** (the $1 ticket) or **appropriately calibrated to survive the system's baseline noise** (the $1,500 SL).
