"""
Self-contained daily OHLC/true-range cloud fetch (New Data Prerequisites
item 1a, strategy-engine spec). Self-contained (no imports from the rest
of this repo, matching cloud/fetch_options_snapshot.py's convention):
must run correctly on an ephemeral GitHub Actions runner.

True range per Welles Wilder's formula (greeks-and-volatility.md SS3):
greatest of (high-low), |high - prior close|, |low - prior close|. Prior
close is read from this ledger's own most recent close:YYYY-MM-DD column
(this repo's own file, already checked out) -- the very first run for a
symbol has no prior close on file, so it falls back to high-low alone,
which self-corrects the next day.

Run from the repo root: `python cloud/fetch_daily_true_range.py`
"""
import os
from datetime import date
from io import StringIO

import pandas as pd
import requests
import yfinance as yf

LEDGER_URL = (
    "https://raw.githubusercontent.com/coop1st/stocks-research-pipeline/"
    "main/data/github_sync/daytrade_ledger/stock_price_ledger.csv"
)
OUT_PATH = "data/github_sync/daily_true_range/true_range_ledger.csv"
FIXED_COLS = ["symbol", "company_name"]


def fetch_watchlist():
    resp = requests.get(LEDGER_URL, timeout=30)
    resp.raise_for_status()
    df = pd.read_csv(StringIO(resp.text))
    return df[["symbol", "company_name"]].drop_duplicates("symbol")


def load_ledger():
    if not os.path.exists(OUT_PATH):
        return {}
    df = pd.read_csv(OUT_PATH, dtype=str)
    return {row["symbol"]: row.to_dict() for _, row in df.iterrows()}


def _prior_close(existing):
    close_keys = sorted(k for k in existing if k.startswith("close:"))
    if not close_keys:
        return None
    raw = existing.get(close_keys[-1])
    return float(raw) if raw not in (None, "", "nan") else None


def _true_range(symbol, prior_close):
    hist = yf.Ticker(symbol).history(period="5d")
    if hist.empty:
        return None, None
    last = hist.iloc[-1]
    high, low, close = float(last["High"]), float(last["Low"]), float(last["Close"])
    candidates = [high - low]
    if prior_close is not None:
        candidates.append(abs(high - prior_close))
        candidates.append(abs(low - prior_close))
    return max(candidates), close


def main():
    today = date.today().isoformat()
    watchlist = fetch_watchlist()
    ledger = load_ledger()

    skipped = []
    for _, row in watchlist.iterrows():
        symbol = row["symbol"]
        existing = ledger.get(symbol, {c: "" for c in FIXED_COLS})
        existing["symbol"] = symbol
        existing["company_name"] = row["company_name"]

        prior_close = _prior_close(existing)
        try:
            tr, close = _true_range(symbol, prior_close)
        except Exception as e:
            print(f"{symbol}: SKIPPED ({e})")
            skipped.append(symbol)
            continue
        if tr is None:
            skipped.append(symbol)
            continue

        existing[today] = round(tr, 4)
        existing[f"close:{today}"] = round(close, 4)
        ledger[symbol] = existing

    all_cols = set()
    for row in ledger.values():
        all_cols.update(row.keys())
    date_cols = sorted(c for c in all_cols if c not in FIXED_COLS and not c.startswith("close:"))
    close_cols = sorted(c for c in all_cols if c.startswith("close:"))
    header = FIXED_COLS + date_cols + close_cols

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    out_df = pd.DataFrame([{c: row.get(c, "") for c in header} for row in ledger.values()], columns=header)
    if not out_df.empty:
        out_df = out_df.sort_values("symbol")
    out_df.to_csv(OUT_PATH, index=False)

    print(f"TRUE_RANGE_READY date={today} symbols_ok={len(ledger) - len(skipped)}/{len(watchlist)} skipped={skipped}")


if __name__ == "__main__":
    main()
