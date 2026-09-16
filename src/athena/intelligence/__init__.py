"""
athena.intelligence
===================

Intelligence and strategic reasoning modules for Athena.
Includes deterministic GTO computation engine and sentinel monitoring.
"""

from athena.intelligence.gto_engine import (
    EEVResult,
    KellyResult,
    MCDAResult,
    MonteCarloResult,
    RuinResult,
    compute_eev,
    compute_half_kelly,
    compute_mcda,
    compute_ruin_probability,
    mcda_score,
    run_monte_carlo_simulation,
)
from athena.intelligence.sentinel import (
    check_boot_sentinel,
    check_shutdown_sentinel,
    update_active_context,
)

__all__ = [
    "EEVResult",
    "KellyResult",
    "MCDAResult",
    "MonteCarloResult",
    "RuinResult",
    "compute_eev",
    "compute_half_kelly",
    "compute_mcda",
    "compute_ruin_probability",
    "mcda_score",
    "run_monte_carlo_simulation",
    "check_boot_sentinel",
    "check_shutdown_sentinel",
    "update_active_context",
]
