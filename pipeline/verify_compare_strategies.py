"""
Verifies pipeline/compare_strategies.py's by-family and by-criterion
aggregation math against synthetic terminal-trade fixtures. No pytest --
run directly and inspect output.

Run: python pipeline/verify_compare_strategies.py
"""
import sys

from compare_strategies import by_criterion, by_family

ALL_OK = True


def check(label, condition):
    global ALL_OK
    print(f"{'OK' if condition else 'FAIL'}: {label}")
    ALL_OK = ALL_OK and condition


def _trade(strategy, is_win, realized_pct, **criteria):
    t = {"strategy": strategy, "is_win": is_win, "realized_pct": realized_pct}
    t.update(criteria)
    return t


def main():
    trades = [
        _trade("iron condor", True, 0.55, iv_richness=80),
        _trade("iron condor", True, 0.40, iv_richness=70),
        _trade("iron condor", False, -1.0, iv_richness=20),
        _trade("iron condor", False, -0.8, iv_richness=15),
        _trade("iron condor", True, 0.10, iv_richness=60),
        _trade("long call", False, -0.5, iv_richness=30),
    ]

    families = {r["strategy"]: r for r in by_family(trades)}
    check("iron condor sample_size == 5", families["iron condor"]["sample_size"] == 5)
    check("iron condor win_rate == 0.6", abs(families["iron condor"]["win_rate"] - 0.6) < 1e-9)
    check("long call flagged too-few-trades", families["long call"]["note"] != "")

    criteria = {r["criterion"]: r for r in by_criterion(trades)}
    # Only iron condor rows have iv_richness set in this fixture (5 of them,
    # meeting MIN_TERMINAL_TRADES_FOR_STATS=5) -- median of [80,70,20,15,60] = 60.
    # Above-median (>=60): 80,70,60 -> wins True,True,True -> win_rate 1.0
    # Below-median (<60): 20,15 -> wins False,False -> win_rate 0.0
    iv_row = criteria["iv_richness"]
    check("iv_richness above-median win rate == 1.0", iv_row["above_median_win_rate"] == 1.0)
    check("iv_richness below-median win rate == 0.0", iv_row["below_median_win_rate"] == 0.0)

    other_criterion = criteria["skew_quality"]
    check("skew_quality has no scored trades -> flagged too-few-trades", other_criterion["note"] != "")

    print("ALL_OK" if ALL_OK else "VERIFICATION_FAILED")
    if not ALL_OK:
        sys.exit(1)


if __name__ == "__main__":
    main()
