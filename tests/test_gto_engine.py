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
    # net_eev = -50 * 0.9 = -45.0
    assert res.raw_ev == -50.0
    assert res.net_eev == -45.0
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
    res = compute_mcda(candidates, criteria, weights, scores)
    assert res.winner == "Option A"
    assert res.is_stable is True
    assert "ROBUST" in res.stability_verdict
    assert "COMMIT PRIMARY TO 'Option A'" in res.verdict
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
    import json
    from athena.intelligence.gto_engine import main

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

