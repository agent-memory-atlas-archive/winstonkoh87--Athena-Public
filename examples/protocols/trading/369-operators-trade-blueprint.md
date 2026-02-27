# Protocol 369: The Operator's Trade Blueprint

> **Status**: Active
> **Core Thesis**: Structure the trade around the operator's psychology, not the spreadsheet's optimum. EEV > MEV.
> **Dependencies**: [Protocol 367](367-high-wr-supremacy.md) (High WR Supremacy), [Protocol 368](368-trade-structure-levers.md) (5 Levers of Trade Structure)
> **Last Updated**: 2026-02-28

## Philosophy

A trade setup is not a single decision. It is the simultaneous configuration of **5 structural levers**, each presenting a binary trade-off between **Efficiency** (optimized for best-case) and **Robustness** (survivable in worst-case).

You cannot maximize all 5 levers simultaneously. The operator must consciously choose which side of the Pareto frontier each lever sits on, based on:

1. Their **specific edge** (Direction vs Timing vs Mean Reversion).
2. Their **psychological architecture** (drawdown tolerance, temporal stress capacity).
3. Their **capital constraints** (bankroll, frequency requirements).

> **The Anti-Fragile Synthesis**: "The only way to 'have both' is temporal separation: Build robustness first (survive), then layer efficiency (optimise). You earn the right to be efficient by first being robust."

---

## The 5 Levers: Operator Configuration

### Lever 1: Stop Loss — WIDE (Robust)

| Parameter | Setting |
|---|---|
| **Preference** | Wide SL (structural invalidation level) |
| **Rationale** | Maximizes Win Rate by surviving market noise |
| **Cost Accepted** | Lower ROI per trade (smaller lot sizes due to wider risk distance) |
| **The Efficiency Trap** | Watching a setup perfectly touch entry and run to target, wishing for tighter SL + heavier size. **Accept this opportunity cost.** |

**Math**: `Position Size = Risk Capital / SL Distance`. Wider SL = fewer lots = lower absolute dollar wins per trade.

**Constraint**: If a tighter SL is used alternatively, position size must be reduced proportionally. Do not combine tight SL + aggressive sizing.

---

### Lever 2: Position Size — HALF-KELLY (Structured)

| Parameter | Setting |
|---|---|
| **Preference** | Half-Kelly fractional sizing |
| **Rationale** | WR is high (~90%) but not 100%. Full Kelly on a wide SL creates catastrophic single-loss exposure |
| **Cost Accepted** | Sub-optimal compounding speed vs Full Kelly |

**The Hidden Bomb**: A wide SL + aggressive sizing is only survivable if the **absolute dollar pain** of a single loss doesn't trigger manual override. At Half-Kelly on a $1K bankroll, a single loss = ~$200. This must be psychologically negligible.

**Kelly Calculation** (90% WR, 0.2 RR):

| Metric | Value |
|---|---|
| Full Kelly | 40% |
| Half-Kelly | **20%** |
| Risk per trade ($1K bankroll) | $200 |
| EV per trade | $8 (8%) |

---

### Lever 3: Layering — FLAT (Default) / MARTINGALE (Conditional)

| Scenario | Layering | Rationale |
|---|---|---|
| **Very light drawdown expected** | **Single Layer** (all positions upfront) | No need to distribute; capture full participation immediately |
| **Light-to-medium drawdown expected** (Default) | **Flat Layering** (scale in evenly) | Accumulates more layers; guarantees meaningful position even if market reverses early in the zone |
| **Deep drawdown expected** | **Martingale Layering** | Saves heaviest allocation for worst price; pulls average entry toward the extreme |

**Key Insight**: By layering trades at all, robustness is already integrated into the structure. Flat layering in a medium drawdown zone optimizes for **participation**—ensuring that even if only 30% of the entry zone is filled before reversal, enough volume is deployed to make the win meaningful. Martingale risks leaving the operator under-deployed on early reversals.

---

### Lever 4: Bullets — TWO BULLETS (Robust)

| Parameter | Setting |
|---|---|
| **Preference** | 2 Bullets |
| **Rationale** | Psychological comfort of not being fully committed while in drawdown; ability to re-calibrate after initial entry |
| **Cost Accepted** | Lower per-bullet ROI; idle capital on Bullet 2 until trigger |

**Bullet 2 Trigger Rule (Structured Discretion)**:

> Bullet 2 fires at **≥20% of SL zone consumed**, thesis intact.
> Bullet 2 is **prohibited** below 20% zone consumed.
> Bullet 2 is **cancelled** if the original thesis is invalidated at any point.

*Example*: On a 100-pip SL, Bullet 2 activates when price has retraced ≥20 pips against the entry.

**Allocation**:

- **Bullet 1**: Initial entry (Flat). The reconnaissance.
- **Bullet 2**: Deployed at trigger. The reinforcement.

---

### Lever 5: Take Profit — SCALE OUT + TRAIL (Hybrid)

| Parameter | Setting |
|---|---|
| **Preference** | Scale out early at T1; trail remainder to T2+ |
| **Rationale** | Locks in High WR (collapses Variance Drag). Trails capture fat right tail |
| **Cost Accepted** | Lower MEV (Mathematical Expected Value) vs holding full size to T2 |

**The EEV vs MEV Trade-off**:

- **MEV** (Mathematical Expected Value): Holding 100% to maximum target. Optimal on a spreadsheet; destroys the human psyche in reality.
- **EEV** (Emotional/Economic Expected Value): Scaling out early pays an immediate dividend for being correct. It funds the **Dignity Premium**—the psychological capital required to hold the trailing portion risk-free.

> **The Operator's Choice**: Robustness of the Operator (EEV) > Efficiency of the Math (MEV).

**The Compounding Cost**: Scaling out reduces blended RR per trade. Over 125+ trades, even small differences (0.15R avg vs 0.25R avg) compound significantly. This cost must be monitored empirically via the trade journal. The bet is that the compounding cost of scaling out is **less than** the compounding cost of psychological blowups from holding full size.

---

## The BCG Trade Classification (80/16/4 Rule)

The base system is a volume grinder. But not all trades are equal. The trailing portion of Lever 5 serves as the **classification mechanism**:

| Classification | Frequency | Avg Win | Role |
|---|---|---|---|
| **Cash Cow** (80%) | ~100 trades | 0.2R ($20) | The engine. Bread and butter. Boring. Consistent. |
| **Question Mark** (16%) | ~20 trades | 0.5–1R ($50–100) | Thesis remains strong; trail held longer than usual |
| **Super-Star** (4%) | ~5 trades | 2R+ ($200+) | Rare confluence of direction + timing + momentum. **Do not scale out the trail.** |

**The Mechanism**: When you scale out at T1, you lock in the Cash Cow. The trailing portion is your *option* on whether this trade is a Question Mark or Super-Star. If it dies after T1, you still banked the win. If it runs, the trail classifies it for you.

**Critical Discipline**: The 4% Super-Star trades make the quarter. You **must not** scale out the trailing portion on these setups. The entire framework depends on letting the right tail of the distribution do its work.

### Projected EV Distribution (125 Trades, $1K Bankroll)

| Component | Calculation | Dollar EV |
|---|---|---|
| Cash Cow Wins (100 × 90% WR) | 90 × $20 | $1,800 |
| Question Mark Wins (20 × 90% WR) | 18 × $75 | $1,350 |
| Super-Star Wins (5 × 90% WR) | 4.5 × $200 | $900 |
| Total Losses (~13 trades) | 13 × -$100 | -$1,300 |
| **Net EV** | | **~$2,750** |

The base EV ($8 × 125 = $1,000) is the floor. The BCG classification + trail captures the right tail, potentially **2.7x the base expectation**.

---

## Operational Constraints

| Constraint | Rule |
|---|---|
| **Max Trade Duration** | 24 hours. Positions are not held overnight unless structurally justified. |
| **Law #1 Compliance** | No single trade can risk irreversible ruin. Half-Kelly is the hard cap. |
| **Edge Decay Monitoring** | At 8% EV per trade, even a 5% WR decay (90% → 85%) flips the system negative. The trade journal is non-negotiable. |
| **Discipline > Brilliance** | Missing trades costs more than bad trades. The system is powered by frequency and consistency, not single heroic calls. |

---

## The Operator's Mandate (Decision Tree)

```
START: New Setup Identified
  │
  ├─ Expected Drawdown?
  │   ├─ Very Light → Single Layer, 1 Bullet
  │   ├─ Light-Medium → Flat Layering, 2 Bullets (DEFAULT)
  │   └─ Deep → Martingale Layering, 2 Bullets
  │
  ├─ Size via Half-Kelly (WR × RR inputs)
  │
  ├─ Set Wide SL at Structural Invalidation
  │
  ├─ Bullet 2 Trigger: ≥20% SL zone consumed, thesis intact
  │
  └─ TP Structure:
      ├─ Scale out at T1 (lock Cash Cow WR)
      └─ Trail remainder
          ├─ Dies after T1 → Cash Cow ✓
          ├─ Runs to T2 → Question Mark ✓
          └─ Runs beyond T2 → Super-Star ✓ (DO NOT SCALE OUT)
```

---

## References

- [Protocol 367: High Win-Rate Supremacy](367-high-wr-supremacy.md)
- [Protocol 368: The 5 Levers of Trade Structure](368-trade-structure-levers.md)
- [Skill: Efficiency vs Robustness](file:///Users/winstonkoh/Project Athena/.agent/skills/efficiency-robustness/SKILL.md)
- [Skill: Kelly Mandate](file:///Users/winstonkoh/Project Athena/.agent/skills/kelly-mandate/SKILL.md)

## Tagging

# trading #structure #protocol #psychology #kelly #levers #BCG #EEV #MEV
