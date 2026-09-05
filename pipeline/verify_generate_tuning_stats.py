"""
Verifies pipeline/generate_tuning_stats.py's correlation, sensitivity,
and exit-side sweep logic against synthetic fixtures. No pytest -- run
directly and inspect output.

Run: python pipeline/verify_generate_tuning_stats.py
"""
import sys
from datetime import date

from generate_tuning_stats import compute_criterion_correlations, compute_weight_sensitivity, sweep_directional_thresholds

ALL_OK = True


def check(label, condition):
    global ALL_OK
    print(f"{'OK' if condition else 'FAIL'}: {label}")
    ALL_OK = ALL_OK and condition


def _trade(realized_pct, **criteria):
    t = {"realized_pct": realized_pct}
    t.update(criteria)
    return t


def main():
    # Perfectly monotonic relationship: iv_richness strongly predicts realized_pct.
    monotonic_trades = [_trade(i * 0.1, iv_richness=i * 10.0) for i in range(1, 10)]
    corr = compute_criterion_correlations(monotonic_trades)
    check("perfectly monotonic criterion -> correlation near 1.0", corr["iv_richness"]["correlation"] > 0.99)
    check("perfectly monotonic criterion -> n == 9", corr["iv_richness"]["n"] == 9)

    # Constant criterion (no variation) -> undefined correlation, not a crash.
    constant_trades = [_trade(i * 0.1, skew_quality=50.0) for i in range(1, 10)]
    corr2 = compute_criterion_correlations(constant_trades)
    check("constant criterion -> correlation is None, not a crash", corr2["skew_quality"]["correlation"] is None)

    # Too few paired observations -> None, not a fabricated number.
    sparse_trades = [_trade(0.5, risk_reward=80.0)]
    corr3 = compute_criterion_correlations(sparse_trades)
    check("fewer than 3 pairs -> correlation is None", corr3["risk_reward"]["correlation"] is None)

    # Weight sensitivity: a criterion that strongly predicts realized_pct
    # should show improved correlation when its weight is doubled.
    strong_trades = [
        {"realized_pct": i * 0.1, "iv_richness": i * 10.0, "skew_quality": 50.0,
         "risk_reward": 50.0, "pop_proxy": 50.0, "term_structure": 50.0,
         "liquidity": 50.0, "directional_alignment": 50.0}
        for i in range(1, 10)
    ]
    sensitivity = compute_weight_sensitivity(strong_trades)
    check("doubling a strongly-predictive criterion's weight improves (or holds) correlation",
          sensitivity["iv_richness"]["doubled_weight_correlation"] >= sensitivity["iv_richness"]["baseline_correlation"])
    check("halving a strongly-predictive criterion's weight worsens (or holds) correlation",
          sensitivity["iv_richness"]["halved_weight_correlation"] <= sensitivity["iv_richness"]["baseline_correlation"])

    # Exit-side sweep: a known synthetic long-call price path should
    # pick out whichever grid point performs best against it.
    long_call_legs = {"trade-1": ("long call", [
        {"leg_role": "long call", "entry_price": 3.00, "contract_symbol": "TEST260601C00100000",
         "expiration": "2026-06-01", "strike": 100.0},
    ])}
    # Real price hits 160% of premium (4.80) -- a target_pct of 1.5
    # should show a win here; the default 2.0 would not.
    signals_by_date = {"2026-03-01": {"TEST260601C00100000": 4.80}}
    sweep = sweep_directional_thresholds(long_call_legs, [0.50], [1.5, 2.0], signals_by_date, date(2026, 3, 1))
    check("lower target_pct grid point captures a win the default would miss",
          sweep[(0.50, 1.5)]["win_rate"] == 1.0)
    check("higher (default) target_pct grid point shows no win yet for the same trade",
          sweep[(0.50, 2.0)]["win_rate"] in (0.0, None))

    print("ALL_OK" if ALL_OK else "VERIFICATION_FAILED")
    if not ALL_OK:
        sys.exit(1)


if __name__ == "__main__":
    main()
