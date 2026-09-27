"""
Unit tests for athena.intelligence.gto_engine.
Ensures mathematical accuracy, analytical bounds, and ASCII-only output.
"""

import json

import pytest

from athena.intelligence.gto_engine import (
    compute_eev,
    compute_half_kelly,
    compute_ruin_probability,
    main,
    run_monte_carlo_simulation,
)


def test_compute_eev_positive_asymmetry():
    res = compute_eev(mev=1000.0, eu=200.0, eo=100.0, skeptic_discount=0.15)
    # raw_ev = 1000 - 300 = 700
    # net_eev = 700 * 0.85 = 595.0
    assert res.raw_ev == 700.0
    assert res.net_eev == pytest.approx(595.0, 0.01)
    assert res.roi_percent > 50.0
    assert "APPROVE" in res.verdict


def test_compute_eev_negative():
    res = compute_eev(mev=200.0, eu=150.0, eo=100.0, skeptic_discount=0.10)
    # raw_ev = 200 - 250 = -50
    # F-04 fix: negative raw_ev is NOT discounted (losses at full face value)
    # net_eev = -50.0 (unchanged — discount only applies to positive EV)
    assert res.raw_ev == -50.0
    assert res.net_eev == -50.0
    assert "REJECT" in res.verdict


def test_compute_half_kelly_positive():
    # 60% win rate with 1.5:1 payoff
    # edge = (0.60 * 1.5) - 0.40 = 0.90 - 0.40 = 0.50
    # f* = 0.50 / 1.5 = 0.3333 (33.33%)
    # half_kelly = 0.1667 (16.67%)
    res = compute_half_kelly(win_rate=0.60, payoff_ratio=1.5, variance_drag=0.5)
    assert res.edge == pytest.approx(0.50, 0.001)
    assert res.full_kelly == pytest.approx(1.0 / 3.0, 0.001)
    assert res.half_kelly == pytest.approx(1.0 / 6.0, 0.001)
    assert "APPROVED" in res.verdict


def test_compute_half_kelly_negative():
    # 40% win rate with 1:1 payoff -> -EV
    res = compute_half_kelly(win_rate=0.40, payoff_ratio=1.0)
    assert res.edge < 0
    assert res.full_kelly == 0.0
    assert res.half_kelly == 0.0
    assert "NO BET" in res.verdict


def test_compute_ruin_probability_safe():
    # 55% win rate, 1.5:1 payoff, 1% risk per trade -> very low ruin
    res = compute_ruin_probability(
        win_rate=0.55,
        payoff_ratio=1.5,
        risk_per_trade_fraction=0.01,
        ruin_drawdown_threshold=0.50,
        trials_for_sim=2000,
        steps_for_sim=100,
    )
    assert res.analytical_ruin_prob < 0.01
    assert res.simulated_ruin_prob < 0.01
    assert "PASS" in res.verdict


def test_compute_ruin_probability_veto():
    # Negative EV or massive position size (25% risk) -> high ruin
    res = compute_ruin_probability(
        win_rate=0.45,
        payoff_ratio=1.0,
        risk_per_trade_fraction=0.25,
        ruin_drawdown_threshold=0.50,
        trials_for_sim=2000,
        steps_for_sim=100,
    )
    assert res.analytical_ruin_prob >= 0.50
    assert "VETO" in res.verdict


def test_run_monte_carlo_simulation():
    res = run_monte_carlo_simulation(
        initial_capital=10000.0,
        win_rate=0.55,
        payoff_ratio=1.5,
        risk_fraction=0.02,
        n_trials=1000,
        n_steps=50,
        seed=42,
    )
    assert res.n_trials == 1000
    assert res.ci_99_lower <= res.ci_95_lower
    assert res.ci_95_lower <= res.median_final_capital
    assert res.median_final_capital <= res.ci_95_upper
    assert res.ci_95_upper <= res.ci_99_upper
    assert 0.0 <= res.mean_max_drawdown_pct <= 100.0


def test_cli_json_and_ascii_no_latex(monkeypatch, capsys):
    # Test JSON mode
    exit_code = main(["--action", "eev", "--mev", "1000", "--eu", "200", "--eo", "100", "--json"])
    assert exit_code == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["net_eev"] == 595.0

    # Test ASCII table mode (assert no LaTeX delimiters)
    exit_code = main(["--action", "monte-carlo", "--trials", "100", "--steps", "20"])
    assert exit_code == 0
    captured = capsys.readouterr()
    output_text = captured.out
    assert "MONTE CARLO TRAJECTORY SIMULATION" in output_text
    assert "$" not in output_text.replace("S$", "")  # Only S$ allowed, no bare $ math delimiters
    assert "$$" not in output_text
    assert "\\(" not in output_text
    assert "\\[" not in output_text


def test_compute_mcda_stable_winner():
    from athena.intelligence.gto_engine import compute_mcda

    candidates = ["Option A", "Option B"]
    criteria = ["Speed", "Cost", "Quality"]
    weights = [0.4, 0.3, 0.3]
    scores = {
        "Option A": [5, 5, 5],
        "Option B": [1, 2, 1],
    }
    veto_floors = {"Speed": 1.0, "Cost": 1.0, "Quality": 1.0}
    res = compute_mcda(candidates, criteria, weights, scores, veto_floors=veto_floors)
    assert res.winner == "Option A"
    assert res.is_stable is True
    assert "ROBUST" in res.stability_verdict
    assert "RECOMMENDED (SCORED)" in res.verdict
    assert len(res.perturbation_flips) == 0


def test_compute_mcda_unstable_tie():
    from athena.intelligence.gto_engine import compute_mcda

    candidates = ["Tech Sales", "Cloud/SRE", "AML Compliance", "Commercial Brokerage"]
    criteria = ["C1", "C2", "C3", "C4", "C5"]
    weights = [0.2, 0.2, 0.2, 0.2, 0.2]
    scores = {
        "Tech Sales": [4, 4, 3, 3, 3],
        "Cloud/SRE": [3, 4, 4, 3, 3],
        "AML Compliance": [3, 3, 4, 4, 3],
        "Commercial Brokerage": [5, 4, 2, 4, 2],
    }
    res = compute_mcda(candidates, criteria, weights, scores)
    assert res.is_stable is False
    assert "UNSTABLE" in res.stability_verdict
    assert "ROUTE TO PATH D" in res.verdict
    assert len(res.perturbation_flips) > 0


def test_cli_mcda_json_and_ascii(capsys):
    mcda_data = {
        "candidates": ["Option A", "Option B"],
        "criteria": ["Speed", "Cost"],
        "weights": [0.6, 0.4],
        "scores": {
            "Option A": [5, 3],
            "Option B": [2, 4],
        },
    }
    json_str = json.dumps(mcda_data)

    # Test ASCII output
    exit_code = main(["--action", "mcda", "--mcda-json", json_str])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "MULTIPLE-CRITERIA DECISION ANALYSIS (MCDA) BUNDLE" in captured.out
    assert "Top Candidate             : Option A" in captured.out

    # Test JSON output
    exit_code = main(["--action", "mcda", "--mcda-json", json_str, "--json"])
    assert exit_code == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["winner"] == "Option A"


def test_mcda_veto_blocks_ruinous_winner():
    from athena.intelligence.gto_engine import compute_mcda

    candidates = ["ILLEGAL_BUT_LUCRATIVE", "LEGAL_DEFENSIVE"]
    criteria = ["Profit", "Speed", "MarketShare", "Regulatory"]
    weights = [0.25, 0.25, 0.25, 0.25]
    scores = {
        "ILLEGAL_BUT_LUCRATIVE": [10.0, 10.0, 10.0, 0.0],
        "LEGAL_DEFENSIVE": [6.0, 6.0, 6.0, 10.0],
    }
    veto_floors = {"Regulatory": 1.0}

    res = compute_mcda(candidates, criteria, weights, scores, veto_floors=veto_floors)
    assert res.winner == "LEGAL_DEFENSIVE"
    assert "ILLEGAL_BUT_LUCRATIVE" in res.vetoed_candidates
    assert res.veto_screen_applied is True
    assert res.is_stable is True
    assert "SOLE FEASIBLE PATH" in res.verdict
    assert "Breached Regulatory floor" in res.vetoed_candidates["ILLEGAL_BUT_LUCRATIVE"][0]


def test_mcda_all_candidates_vetoed():
    from athena.intelligence.gto_engine import compute_mcda

    candidates = ["Bad A", "Bad B"]
    criteria = ["Safety", "Budget"]
    weights = [0.5, 0.5]
    scores = {
        "Bad A": [0.0, 5.0],
        "Bad B": [5.0, 0.0],
    }
    veto_floors = {"Safety": 1.0, "Budget": 1.0}

    res = compute_mcda(candidates, criteria, weights, scores, veto_floors=veto_floors)
    assert res.winner == "NONE"
    assert res.is_stable is False
    assert "INFEASIBLE" in res.stability_verdict
    assert "NO FEASIBLE PATH" in res.verdict
    assert len(res.vetoed_candidates) == 2


def test_mcda_dominant_winner_is_stable():
    from athena.intelligence.gto_engine import compute_mcda

    candidates = ["Superior", "Inferior"]
    criteria = ["C1", "C2", "C3"]
    weights = [0.34, 0.33, 0.33]
    scores = {
        "Superior": [5.0, 5.0, 5.0],
        "Inferior": [4.9, 4.9, 4.9],  # strictly inferior, margin is ~2.04% < 5%
    }
    veto_floors = {"C1": 1.0, "C2": 1.0, "C3": 1.0}

    res = compute_mcda(candidates, criteria, weights, scores, veto_floors=veto_floors)
    assert res.winner == "Superior"
    assert res.is_stable is True
    assert "ROBUST" in res.stability_verdict
    assert "RECOMMENDED (SCORED)" in res.verdict
    assert any("strictly dominates" in obs for obs in res.pairwise_dominance)


def test_mcda_single_criterion_stable():
    from athena.intelligence.gto_engine import compute_mcda

    candidates = ["Option A", "Option B"]
    criteria = ["SingleScore"]
    weights = [1.0]
    scores = {
        "Option A": [9.4],
        "Option B": [9.0],  # 4.44% margin, strictly dominant
    }
    veto_floors = {"SingleScore": 1.0}

    res = compute_mcda(candidates, criteria, weights, scores, veto_floors=veto_floors)
    assert res.winner == "Option A"
    assert res.is_stable is True
    assert "ROBUST" in res.stability_verdict
    assert "RECOMMENDED (SCORED)" in res.verdict


def test_mcda_no_screen_is_advisory_only():
    from athena.intelligence.gto_engine import compute_mcda

    candidates = ["Option A", "Option B"]
    criteria = ["Speed", "Cost"]
    weights = [0.6, 0.4]
    scores = {
        "Option A": [5, 5],
        "Option B": [2, 2],
    }
    # No veto_floors passed
    res = compute_mcda(candidates, criteria, weights, scores)
    assert res.winner == "Option A"
    assert res.is_stable is True
    assert res.veto_screen_applied is False
    assert "ADVISORY ONLY (NO VETO SCREEN)" in res.verdict
    assert "DECISION LOCKED" not in res.verdict


def test_ruin_result_violates_law1():
    from athena.intelligence.gto_engine import compute_ruin_probability

    # Safe: win_rate=0.60, payoff=1.5, risk=0.02 -> ruin < 1%
    safe_res = compute_ruin_probability(win_rate=0.60, payoff_ratio=1.5, risk_per_trade_fraction=0.02)
    assert safe_res.violates_law1 is False
    assert "Law #1 Violation (>5% Ruin)  : NO (Ergodic)" in safe_res.to_ascii_table()

    # Dangerous: win_rate=0.45, payoff=1.0, risk=0.10 -> ruin > 5%
    ruin_res = compute_ruin_probability(win_rate=0.45, payoff_ratio=1.0, risk_per_trade_fraction=0.10)
    assert ruin_res.violates_law1 is True
    assert "Law #1 Violation (>5% Ruin)  : YES (HARD VETO)" in ruin_res.to_ascii_table()


def test_gto_screen_without_floors_raises():
    from athena.intelligence.gto_engine import VetoFloorRequired, gto_screen

    candidates = ["PathA_Ruin40pct", "PathB_Safe"]
    criteria = ["Speed", "Robustness"]
    weights = [0.8, 0.2]
    scores = {
        "PathA_Ruin40pct": [9.0, 1.0],
        "PathB_Safe": [5.0, 8.0],
    }

    # Calling gto_screen without veto floors MUST raise VetoFloorRequired (fail-closed)
    with pytest.raises(VetoFloorRequired, match="fail-closed and requires active veto_floors"):
        gto_screen(candidates, criteria, weights, scores)

    # Calling with empty dict must also raise
    with pytest.raises(VetoFloorRequired):
        gto_screen(candidates, criteria, weights, scores, veto_floors={})


def test_gto_screen_with_veto_floors_enforces_veto():
    from athena.intelligence.gto_engine import gto_screen

    candidates = ["PathA_Ruin40pct", "PathB_Safe"]
    criteria = ["Speed", "Robustness"]
    weights = [0.8, 0.2]
    scores = {
        "PathA_Ruin40pct": [9.0, 1.0],
        "PathB_Safe": [5.0, 8.0],
    }

    # With veto floor on Robustness >= 5.0, PathA is vetoed despite higher raw composite score
    res = gto_screen(
        candidates,
        criteria,
        weights,
        scores,
        veto_floors={"Robustness": 5.0},
    )
    assert res.winner == "PathB_Safe"
    assert res.veto_screen_applied is True
    assert "PathA_Ruin40pct" in res.vetoed_candidates
    assert any("Breached Robustness floor" in b for b in res.vetoed_candidates["PathA_Ruin40pct"])


def test_derive_ruin_floors_and_gto_screen():
    from athena.intelligence.gto_engine import derive_ruin_floors, gto_screen

    candidates = ["PathA_Ruin40pct", "PathB_Safe"]
    criteria = ["Speed", "Robustness"]
    weights = [0.8, 0.2]
    scores = {
        "PathA_Ruin40pct": [9.0, 1.0],
        "PathB_Safe": [5.0, 8.0],
    }
    ruin_inputs = {
        "PathA_Ruin40pct": {"win_rate": 0.45, "payoff_ratio": 1.0, "risk_per_trade_fraction": 0.10},
        "PathB_Safe": {"win_rate": 0.60, "payoff_ratio": 1.5, "risk_per_trade_fraction": 0.02},
    }

    # derive_ruin_floors produces floor on Robustness
    floors = derive_ruin_floors(candidates, ruin_inputs, target_criterion="Robustness", floor_value=5.0)
    assert floors == {"Robustness": 5.0}

    # gto_screen auto-derives from ruin_inputs and vetoes PathA
    res = gto_screen(
        candidates,
        criteria,
        weights,
        scores,
        ruin_inputs=ruin_inputs,
        ruin_criterion="Robustness",
        ruin_floor=5.0,
    )
    assert res.winner == "PathB_Safe"
    assert res.veto_screen_applied is True
    assert "PathA_Ruin40pct" in res.vetoed_candidates


def test_cli_require_veto():
    from athena.intelligence.gto_engine import main

    mcda_data = {
        "candidates": ["PathA", "PathB"],
        "criteria": ["Speed", "Robustness"],
        "weights": [0.8, 0.2],
        "scores": {"PathA": [9.0, 1.0], "PathB": [5.0, 8.0]},
    }

    # Without --require-veto, exits 0 (advisory mode)
    exit_code = main(["--action", "mcda", "--mcda-json", json.dumps(mcda_data)])
    assert exit_code == 0

    # With --require-veto but no veto_floors, exits non-zero (fail-closed)
    exit_code_fail = main(["--action", "mcda", "--require-veto", "--mcda-json", json.dumps(mcda_data)])
    assert exit_code_fail != 0

    # With --require-veto and veto_floors, exits 0
    mcda_data_with_veto = dict(mcda_data, veto_floors={"Robustness": 5.0})
    exit_code_vetoed = main(["--action", "mcda", "--require-veto", "--mcda-json", json.dumps(mcda_data_with_veto)])
    assert exit_code_vetoed == 0



