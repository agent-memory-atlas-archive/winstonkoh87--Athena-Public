def calculate_net_ev(
    gross_ev_r: float,
    stop_loss_pips: float,
    spread_pips: float,
    commission_pips: float,
    slippage_pips: float,
) -> tuple[float, float]:
    """
    Calculates the Net EV and the Friction Drag in 'R' units.

    gross_ev_r: Expected Value in R units (e.g., 0.10 for +10% EV)
    stop_loss_pips: The distance of the stop loss in pips (defines the size of 1R)
    spread_pips: Average spread paid per trade
    commission_pips: Commission equivalent in pips per trade
    slippage_pips: Average slippage per trade (usually on market orders/stops)
    """

    # Total friction in absolute pips
    total_friction_pips = spread_pips + commission_pips + slippage_pips

    # Convert friction pips into 'R' units.
    # Since 1R = stop_loss_pips, friction in R = total_friction / stop_loss_pips
    friction_r = total_friction_pips / stop_loss_pips

    # Net EV = Gross EV - Friction R
    net_ev_r = gross_ev_r - friction_r

    return net_ev_r, friction_r


def run_friction_simulation():
    gross_ev = 0.10  # 10% Gross EV
    # Standard Retail Forex/Index Friction
    spread = 0.5
    commission = 0.4  # ~$4-$7 per round turn lot
    slippage = 0.3  # Average slippage on SL hits

    print(f"--- FRICTION DRAG ANALYSIS (Gross EV: +{gross_ev * 100}%) ---")
    print(
        f"Fixed Costs: Spread({spread}) + Comm({commission}) + Slippage({slippage}) = {spread + commission + slippage:.1f} pips/trade\n"
    )

    print(
        f"{'Trading Style':<15} | {'Stop Loss (1R)':<15} | {'Friction (R)':<15} | {'Net EV':<10}"
    )
    print("-" * 65)

    # Scenarios based on SL size (Timeframe/Style)
    scenarios = [
        ("Hyper-Scalper", 3.0),
        ("Scalper", 5.0),
        ("Day Trader", 15.0),
        ("Swing Trader", 50.0),
        ("Macro Trader", 150.0),
    ]

    for name, sl_pips in scenarios:
        net_ev, friction = calculate_net_ev(
            gross_ev, sl_pips, spread, commission, slippage
        )
        print(
            f"{name:<15} | {sl_pips:<15.1f} | -{friction * 100:<14.1f}% | {net_ev * 100:>+5.1f}%"
        )


if __name__ == "__main__":
    run_friction_simulation()
