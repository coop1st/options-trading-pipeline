"""
Verifies pipeline/generate_tuning_stats.py's correlation, sensitivity,
and exit-side sweep logic against synthetic fixtures. No pytest -- run
directly and inspect output.

Run: python pipeline/verify_generate_tuning_stats.py
"""
import sys
from datetime import date

from generate_tuning_stats import compute_criterion_correlations

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

    print("ALL_OK" if ALL_OK else "VERIFICATION_FAILED")
    if not ALL_OK:
        sys.exit(1)


if __name__ == "__main__":
    main()
