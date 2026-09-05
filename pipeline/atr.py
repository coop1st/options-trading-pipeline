"""
Weekly local ATR refresh from the daily true-range cloud ledger (New Data
Prerequisites item 1b, strategy-engine spec). The ledger lives in this
same repo (published by cloud/fetch_daily_true_range.py), so -- unlike
the cross-repo Stocks ledgers -- it's read from the local working copy
after a git pull, the same way merge_and_score.py reads its own
options_snapshots CSVs.
"""
from datetime import date

import pandas as pd

from config import ATR_HISTORY_WINDOW, ATR_REFRESH_DAYS, PROJECT_DIR
from db import get_atr_row, upsert_atr

LEDGER_PATH = PROJECT_DIR / "data" / "github_sync" / "daily_true_range" / "true_range_ledger.csv"


def _is_stale(computed_date_str, today):
    if computed_date_str is None:
        return True
    return (today - date.fromisoformat(computed_date_str)).days >= ATR_REFRESH_DAYS


def refresh_atr_if_stale(today=None):
    """Recomputes and caches each symbol's 14-day ATR, but only for
    symbols whose cached value is 7+ days old or missing -- ATR is a
    slow-moving average, so daily recomputation isn't needed. Returns
    the count of symbols refreshed."""
    today = today or date.today()
    if not LEDGER_PATH.exists():
        print(f"No true-range ledger at {LEDGER_PATH} yet -- skipping ATR refresh")
        return 0

    df = pd.read_csv(LEDGER_PATH)
    date_cols = sorted(c for c in df.columns if c not in ("symbol", "company_name") and not c.startswith("close:"))
    recent_cols = date_cols[-ATR_HISTORY_WINDOW:]
    if len(recent_cols) < ATR_HISTORY_WINDOW:
        print(f"Only {len(recent_cols)} of {ATR_HISTORY_WINDOW} days of true-range history so far -- ATR not yet computable")
        return 0

    refreshed = 0
    for _, row in df.iterrows():
        symbol = row["symbol"]
        existing = get_atr_row(symbol)
        if not _is_stale(existing["computed_date"] if existing else None, today):
            continue
        values = pd.to_numeric(row[recent_cols], errors="coerce").dropna()
        if len(values) < ATR_HISTORY_WINDOW:
            continue
        upsert_atr(symbol, float(values.mean()), today.isoformat())
        refreshed += 1

    print(f"ATR refresh: {refreshed} symbol(s) recomputed")
    return refreshed


if __name__ == "__main__":
    refresh_atr_if_stale()
