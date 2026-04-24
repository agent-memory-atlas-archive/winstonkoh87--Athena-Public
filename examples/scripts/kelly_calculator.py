def calculate_kelly(win_rate: float, ev: float) -> tuple[float, float, float]:
    """
    Calculates the RR and Kelly parameters for a given Win Rate and fixed EV.
    Formula for EV: EV = (WR * RR) - (LR * 1)
    Rearranged for RR: RR = (EV + LR) / WR

    Formula for Full Kelly %: K = WR - (LR / RR)
    """
    loss_rate = 1.0 - win_rate

    # Calculate required RR to achieve the target EV
    rr = (ev + loss_rate) / win_rate

    # Calculate Full Kelly fraction
    full_kelly_pct = win_rate - (loss_rate / rr)

    # Calculate Half Kelly fraction
    half_kelly_pct = full_kelly_pct / 2.0

    return rr, full_kelly_pct, half_kelly_pct


def run_sensitivity_analysis():
    target_ev = 0.05  # 5% EV per trade

    print(
        f"--- KELLY CRITERION SENSITIVITY ANALYSIS (Fixed +{target_ev * 100}% EV) ---"
    )
    print(
        f"{'Win Rate':>10} | {'Req. R:R':>10} | {'Full Kelly':>12} | {'Half-Kelly (Safe Limit)':>25}"
    )
    print("-" * 65)

    # Test a range of win rates from 10% to 90% in 5% increments
    win_rates = [x / 100.0 for x in range(10, 95, 5)]

    for wr in win_rates:
        rr, full_k, half_k = calculate_kelly(wr, target_ev)
        print(
            f"{wr * 100:>9.0f}% | {rr:>10.2f} | {full_k * 100:>11.2f}% | {half_k * 100:>24.2f}%"
        )


if __name__ == "__main__":
    run_sensitivity_analysis()
