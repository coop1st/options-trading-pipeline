"""
Verifies pipeline/compare_strategies.py's by-family, by-label, and
by-criterion aggregation math against synthetic terminal-trade fixtures.
No pytest -- run directly and inspect output.

Run: python pipeline/verify_compare_strategies.py
"""
import sys

from compare_strategies import by_criterion, by_family, by_label

ALL_OK = True


def check(label, condition):
    global ALL_OK
    print(f"{'OK' if condition else 'FAIL'}: {label}")
    ALL_OK = ALL_OK and condition


def _trade(strategy, is_win, realized_pct, selection_label=None, **criteria):
    t = {"strategy": strategy, "is_win": is_win, "realized_pct": realized_pct, "selection_label": selection_label}
    t.update(criteria)
    return t


def main():
    trades = [
        _trade("iron condor", True, 0.55, "rich_iv", iv_richness=80),
        _trade("iron condor", True, 0.40, "rich_iv", iv_richness=70),
        _trade("iron condor", False, -1.0, "no_dominant_thesis", iv_richness=20),
        _trade("iron condor", False, -0.8, "no_dominant_thesis", iv_richness=15),
        _trade("iron condor", True, 0.10, "rich_iv", iv_richness=60),
        _trade("long call", False, -0.5, "no_dominant_thesis", iv_richness=30),
        _trade("long call", False, -0.6, None),  # predates selection_label -- must be excluded from by_label; no criteria set, so it must not shift by_criterion's medians either
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

    labels = {r["selection_label"]: r for r in by_label(trades)}
    check("rich_iv label win_rate == 1.0 (3/3)", labels["rich_iv"]["win_rate"] == 1.0)
    check("no_dominant_thesis label win_rate == 0.0 (0/3)", labels["no_dominant_thesis"]["win_rate"] == 0.0)
    check("pre-selection_label trade (None) excluded from by_label entirely",
          sum(r["sample_size"] for r in labels.values()) == 6 and None not in labels)

    print("ALL_OK" if ALL_OK else "VERIFICATION_FAILED")
    if not ALL_OK:
        sys.exit(1)


if __name__ == "__main__":
    main()
