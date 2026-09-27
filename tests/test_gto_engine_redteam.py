"""
Red-Team Mutation Tests for athena.intelligence.gto_engine
==========================================================

These tests verify that the safety-critical bugs identified in the
2026-09-26 Decision System Red-Team Audit are fixed.

RED-RUN RULE: Each test MUST fail on the pre-fix code and pass after
remediation. The commit message must show both states.

Findings covered:
  F-01 (Critical): MCDA veto gate fails open on unknown keys
  F-04 (High):     EEV skeptic discount halves losses
  F-05 (High):     MCDA accepts NaN and negative weights
  F-03 (High):     Monte Carlo mislabels and parameter validation
"""


import pytest

from athena.intelligence.gto_engine import (
    compute_eev,
    compute_mcda,
    run_monte_carlo_simulation,
)

# ===================================================================
# F-01 (Critical): Veto gate must fail-closed on unknown keys
# ===================================================================

class TestF01_VetoFailClosed:
    """A veto floor with a key not matching any scored criterion must
    raise an error, not silently pass all candidates."""

    def test_unknown_veto_key_raises(self):
        """Veto key 'Legal' not in criteria ['EV'] must raise, not silently pass."""
        with pytest.raises(ValueError, match="[Vv]eto.*not.*criter|[Uu]nknown.*veto|not a scored criterion"):
            compute_mcda(
                candidates=["A", "B"],
                criteria=["EV"],
                weights=[1.0],
                scores={"A": [8.0], "B": [6.0]},
                veto_floors={"Legal": 1.0},  # 'Legal' is not a criterion
            )

    def test_typo_veto_key_raises(self):
        """Typo 'Spped' for criterion 'Speed' must raise, not silently pass."""
        with pytest.raises(ValueError, match="[Vv]eto|[Uu]nknown|not a scored criterion"):
            compute_mcda(
                candidates=["A", "B"],
                criteria=["Speed", "Cost"],
                weights=[0.5, 0.5],
                scores={"A": [8.0, 5.0], "B": [6.0, 7.0]},
                veto_floors={"Spped": 3.0, "Cost": 2.0},  # 'Spped' typo
            )

    def test_empty_veto_floors_dict_raises(self):
        """An empty veto_floors dict signals intent to screen but screens
        nothing. Must raise rather than mark veto_screen_applied=True."""
        with pytest.raises(ValueError, match="[Ee]mpty.*veto|[Vv]eto.*empty|at least one"):
            compute_mcda(
                candidates=["A"],
                criteria=["EV"],
                weights=[1.0],
                scores={"A": [5.0]},
                veto_floors={},
            )

    def test_valid_veto_key_still_works(self):
        """Regression: valid veto keys must still function normally."""
        res = compute_mcda(
            candidates=["Good", "Bad"],
            criteria=["Profit", "Legal"],
            weights=[0.5, 0.5],
            scores={"Good": [7.0, 8.0], "Bad": [9.0, 0.5]},
            veto_floors={"Legal": 1.0},
        )
        assert "Bad" in res.vetoed_candidates
        assert res.winner == "Good"
        assert res.veto_screen_applied is True


# ===================================================================
# F-04 (High): EEV skeptic discount must not shrink losses
# ===================================================================

class TestF04_EEVSkepticDiscount:
    """The skeptic discount should make positive outcomes more conservative,
    not make negative outcomes look smaller."""

    def test_negative_ev_not_reduced_by_discount(self):
        """A negative raw_ev should NOT be made less negative by the discount.
        MEV=100, eu=50, eo=1000 => raw_ev=-950. With 50% discount, the old
        code returned -475 (halving the loss). Fixed code must return
        net_eev <= raw_ev (i.e. at least as negative, or equal)."""
        res = compute_eev(mev=100.0, eu=50.0, eo=1000.0, skeptic_discount=0.50)
        assert res.raw_ev == -950.0
        # The discount must NOT make the loss look smaller
        assert res.net_eev <= res.raw_ev, (
            f"Skeptic discount shrank a loss: net_eev={res.net_eev} > raw_ev={res.raw_ev}. "
            f"This makes negative-EV traps look safer than they are."
        )

    def test_positive_ev_is_discounted_normally(self):
        """Regression: positive raw_ev should still be reduced by the discount."""
        res = compute_eev(mev=1000.0, eu=200.0, eo=100.0, skeptic_discount=0.15)
        assert res.raw_ev == 700.0
        # Positive EV should be discounted (made smaller)
        assert res.net_eev < res.raw_ev
        assert res.net_eev == pytest.approx(595.0, abs=0.01)

    def test_zero_ev_unchanged_by_discount(self):
        """Zero raw_ev should remain zero regardless of discount."""
        res = compute_eev(mev=300.0, eu=200.0, eo=100.0, skeptic_discount=0.50)
        assert res.raw_ev == 0.0
        assert res.net_eev == 0.0


# ===================================================================
# F-05 (High): MCDA must reject NaN and negative weights
# ===================================================================

class TestF05_MCDAInputValidation:
    """MCDA must reject invalid numerical inputs that produce
    nonsensical results."""

    def test_nan_weight_raises(self):
        """NaN weight must be rejected, not silently produce NaN scores."""
        with pytest.raises((ValueError, TypeError)):
            compute_mcda(
                candidates=["A", "B"],
                criteria=["Speed", "Cost"],
                weights=[float("nan"), 0.5],
                scores={"A": [5, 5], "B": [3, 3]},
            )

    def test_negative_weight_raises(self):
        """Negative weights are not valid preference intensities."""
        with pytest.raises(ValueError, match="[Nn]egative|[Nn]on-negative|positive"):
            compute_mcda(
                candidates=["A", "B"],
                criteria=["Speed", "Cost"],
                weights=[1.0, -0.2],
                scores={"A": [5, 5], "B": [3, 3]},
            )

    def test_inf_weight_raises(self):
        """Infinite weight must be rejected."""
        with pytest.raises((ValueError, TypeError)):
            compute_mcda(
                candidates=["A", "B"],
                criteria=["Speed", "Cost"],
                weights=[float("inf"), 0.5],
                scores={"A": [5, 5], "B": [3, 3]},
            )

    def test_nan_score_raises(self):
        """NaN in score matrix must be rejected."""
        with pytest.raises((ValueError, TypeError)):
            compute_mcda(
                candidates=["A", "B"],
                criteria=["Speed"],
                weights=[1.0],
                scores={"A": [float("nan")], "B": [3.0]},
            )

    def test_inf_score_raises(self):
        """Infinite score must be rejected."""
        with pytest.raises((ValueError, TypeError)):
            compute_mcda(
                candidates=["A", "B"],
                criteria=["Speed"],
                weights=[1.0],
                scores={"A": [float("inf")], "B": [3.0]},
            )

    def test_duplicate_candidates_raises(self):
        """Duplicate candidate names must be rejected."""
        with pytest.raises(ValueError, match="[Dd]uplicate"):
            compute_mcda(
                candidates=["A", "A"],
                criteria=["Speed"],
                weights=[1.0],
                scores={"A": [5.0]},
            )

    def test_duplicate_criteria_raises(self):
        """Duplicate criteria names must be rejected."""
        with pytest.raises(ValueError, match="[Dd]uplicate"):
            compute_mcda(
                candidates=["A"],
                criteria=["Speed", "Speed"],
                weights=[0.5, 0.5],
                scores={"A": [5.0, 5.0]},
            )


# ===================================================================
# F-03 (High): Monte Carlo parameter validation
# ===================================================================

class TestF03_MonteCarloValidation:
    """Monte Carlo must validate inputs and not produce results
    from nonsensical parameters."""

    def test_zero_trials_raises(self):
        """Zero trials must be rejected (would divide by zero)."""
        with pytest.raises(ValueError, match="[Tt]rial|positive"):
            run_monte_carlo_simulation(
                initial_capital=10000.0,
                win_rate=0.55,
                payoff_ratio=1.5,
                risk_fraction=0.02,
                n_trials=0,
                n_steps=50,
            )

    def test_negative_capital_raises(self):
        """Negative initial capital must be rejected."""
        with pytest.raises(ValueError, match="[Cc]apital|positive"):
            run_monte_carlo_simulation(
                initial_capital=-1000.0,
                win_rate=0.55,
                payoff_ratio=1.5,
                risk_fraction=0.02,
                n_trials=100,
                n_steps=50,
            )

    def test_invalid_win_rate_raises(self):
        """Win rate outside [0,1] must be rejected."""
        with pytest.raises(ValueError, match="[Ww]in.*rate|probability|0.*1"):
            run_monte_carlo_simulation(
                initial_capital=10000.0,
                win_rate=1.5,
                payoff_ratio=1.5,
                risk_fraction=0.02,
                n_trials=100,
                n_steps=50,
            )

    def test_nan_risk_fraction_raises(self):
        """NaN risk fraction must be rejected."""
        with pytest.raises((ValueError, TypeError)):
            run_monte_carlo_simulation(
                initial_capital=10000.0,
                win_rate=0.55,
                payoff_ratio=1.5,
                risk_fraction=float("nan"),
                n_trials=100,
                n_steps=50,
            )
