"""
Protocol 330: EEV Three-Line Model Visualization
Generates the Economic Expected Value chart for the TOTO CS-A case study.

Shows:
- MEV (Mathematical Expected Value) — fixed negative slope
- UEV (Utility Expected Value) — spike, decay, crash
- EEV (Economic Expected Value) — sum of MEV + UEV
- Limit Point at ~$16 where EEV = 0

Usage:
    python3 generate_eev_chart.py

Output:
    Saves to same directory as: eev_three_line_model.png
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ═══════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════

OUTPUT_DIR = Path(__file__).parent
TICKET_COST = 1.0  # $1 per TOTO ticket
HOUSE_EDGE = 0.46  # 46% house edge (only 54% enters prize pool)
MAX_SPEND = 50  # X-axis max (dollars spent on tickets)
LIMIT_POINT = 16  # EEV = 0 at $16 (from protocol analysis)

# ═══════════════════════════════════════════════════════════════
# Mathematical Models
# ═══════════════════════════════════════════════════════════════

x = np.linspace(0.1, MAX_SPEND, 500)  # Avoid x=0 for log

# --- MEV: Mathematical Expected Value ---
# Linear negative slope: you lose 46 cents per dollar played
mev = -HOUSE_EDGE * x

# --- UEV: Utility Expected Value ---
# Phase 1 (0-1): Spike — acquiring the option gives near-peak utility
# Phase 2 (1-10): Slow decay — diminishing marginal fantasy
# Phase 3 (10+): Crash — anxiety, regret, cash drag
#
# Model: UEV = A * ln(x + 1) * exp(-B * x)
# This creates a sharp spike near x=1, then exponential decay
A = 11.0  # Amplitude (calibrated to make EEV=0 at ~$16)
B = 0.09  # Decay rate
uev = A * np.log(x + 1) * np.exp(-B * x)

# --- EEV: Economic Expected Value ---
eev = mev + uev

# Find the actual zero crossing for annotation
zero_idx = np.argmin(np.abs(eev))
actual_limit = x[zero_idx]

# ═══════════════════════════════════════════════════════════════
# Plotting
# ═══════════════════════════════════════════════════════════════

plt.style.use("dark_background")
fig, ax = plt.subplots(figsize=(14, 8))

# --- Lines ---
ax.plot(
    x,
    mev,
    color="#FF4444",
    linewidth=2.5,
    label="MEV (Math Expected Value)",
    linestyle="--",
    alpha=0.85,
)
ax.plot(
    x,
    uev,
    color="#44AAFF",
    linewidth=2.5,
    label="UEV (Utility Expected Value)",
    linestyle="-.",
    alpha=0.85,
)
ax.plot(
    x,
    eev,
    color="#00FF88",
    linewidth=3.5,
    label="EEV (Economic Expected Value)",
    zorder=5,
)

# --- Zero line ---
ax.axhline(y=0, color="white", linewidth=0.8, linestyle="-", alpha=0.4)

# --- Fill regions ---
# Green fill where EEV > 0 (rational zone)
ax.fill_between(
    x,
    eev,
    0,
    where=(eev > 0),
    color="#00FF88",
    alpha=0.12,
    label="Rational Zone (EEV > 0)",
)
# Red fill where EEV < 0 (irrational zone)
ax.fill_between(
    x,
    eev,
    0,
    where=(eev < 0),
    color="#FF4444",
    alpha=0.12,
    label="Wealth Destruction (EEV < 0)",
)

# --- Limit Point marker ---
ax.plot(
    actual_limit,
    0,
    "o",
    color="#FFD700",
    markersize=14,
    zorder=10,
    markeredgecolor="white",
    markeredgewidth=2,
)

# --- Limit Point annotation ---
ax.annotate(
    f"LIMIT POINT\nEEV = 0 at ${actual_limit:.0f}",
    xy=(actual_limit, 0),
    xytext=(actual_limit + 8, 3.5),
    fontsize=13,
    fontweight="bold",
    color="#FFD700",
    arrowprops=dict(
        facecolor="#FFD700",
        edgecolor="#FFD700",
        shrink=0.05,
        width=2,
        headwidth=10,
    ),
    bbox=dict(boxstyle="round,pad=0.5", fc="black", ec="#FFD700", lw=2, alpha=0.9),
)

# --- Phase annotations ---
# Phase 1: The Spike
ax.annotate(
    "Phase 1\nTHE SPIKE\n(Option acquired)",
    xy=(1.5, uev[7]),
    xytext=(6, uev[7] + 2),
    fontsize=9,
    color="#44AAFF",
    alpha=0.9,
    arrowprops=dict(
        facecolor="#44AAFF", edgecolor="#44AAFF", shrink=0.05, width=1, headwidth=6
    ),
    bbox=dict(boxstyle="round,pad=0.3", fc="black", ec="#44AAFF", lw=1.5, alpha=0.8),
)

# Phase 3: The Crash
ax.annotate(
    "Phase 3\nTHE CRASH\n(Anxiety + Regret)",
    xy=(35, uev[345]),
    xytext=(38, uev[345] + 2.5),
    fontsize=9,
    color="#FF6666",
    alpha=0.9,
    arrowprops=dict(
        facecolor="#FF6666", edgecolor="#FF6666", shrink=0.05, width=1, headwidth=6
    ),
    bbox=dict(boxstyle="round,pad=0.3", fc="black", ec="#FF6666", lw=1.5, alpha=0.8),
)

# --- Zone labels ---
ax.text(
    5,
    4.5,
    "RATIONAL",
    fontsize=14,
    fontweight="bold",
    color="#00FF88",
    alpha=0.7,
    ha="center",
)
ax.text(
    35,
    -6,
    "WEALTH\nDESTRUCTION",
    fontsize=14,
    fontweight="bold",
    color="#FF4444",
    alpha=0.7,
    ha="center",
)

# --- Title and labels ---
ax.set_title(
    "Protocol 330: The EEV Three-Line Model\nSingapore TOTO $12M Draw — CS-A",
    fontsize=18,
    fontweight="bold",
    color="white",
    pad=20,
)
ax.set_xlabel(
    "Total Spend on Lottery Tickets ($)", fontsize=13, color="#AAAAAA", labelpad=10
)
ax.set_ylabel("Expected Value ($/draw)", fontsize=13, color="#AAAAAA", labelpad=10)

# --- Legend ---
legend = ax.legend(
    loc="lower left",
    fontsize=10,
    framealpha=0.8,
    edgecolor="#555555",
    fancybox=True,
)
legend.get_frame().set_facecolor("black")

# --- Grid ---
ax.grid(True, alpha=0.15, linestyle="--")
ax.set_xlim(0, MAX_SPEND)
ax.set_ylim(-25, max(uev) + 5)

# --- X-axis markers ---
ax.set_xticks([0, 1, 5, 10, 16, 20, 30, 40, 50])
ax.set_xticklabels(
    ["$0", "$1", "$5", "$10", "$16", "$20", "$30", "$40", "$50"],
    fontsize=10,
    color="white",
)

# ═══════════════════════════════════════════════════════════════
# Save
# ═══════════════════════════════════════════════════════════════

output_path = OUTPUT_DIR.parent / "protocols" / "decision" / "eev_three_line_model.png"
plt.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="black")
plt.close()

print(f"✅ EEV Three-Line Model saved to: {output_path}")
print(f"   Limit Point: ${actual_limit:.0f} (EEV = 0)")
print(f"   MEV at limit: ${mev[zero_idx]:.2f}")
print(f"   UEV at limit: ${uev[zero_idx]:.2f}")
