"""
Reads the Stocks project's weekly ratings ledger for each symbol's latest
bullish/bearish tilt (strategy-engine spec, Component Detail sections A
and C). Cross-repo read via raw.githubusercontent.com, same pattern as
cloud/fetch_options_snapshot.py's fetch_watchlist() -- this ledger lives
in the separate stocks-research-pipeline repo, not this one.
"""
from io import StringIO

import pandas as pd
import requests

RATINGS_LEDGER_URL = (
    "https://raw.githubusercontent.com/coop1st/stocks-research-pipeline/"
    "main/data/github_sync/weekly_ratings_ledger/stock_rating_ledger.csv"
)


def _latest_week_column(columns):
    date_cols = [c for c in columns if c not in ("symbol", "company_name")]
    return sorted(date_cols)[-1] if date_cols else None


def fetch_directional_bias():
    """Returns {symbol: 'bullish'|'bearish'} for every symbol whose most
    recent week column holds a STRONG BUY or STRONG SELL rating. A
    symbol absent from this dict has no strong tilt (neutral) -- per the
    spec's error-handling convention, that's the normal "no signal" case
    for a given day, not a failure."""
    resp = requests.get(RATINGS_LEDGER_URL, timeout=30)
    resp.raise_for_status()
    df = pd.read_csv(StringIO(resp.text))

    latest_col = _latest_week_column(df.columns)
    if latest_col is None:
        return {}

    bias = {}
    for _, row in df.iterrows():
        cell = row.get(latest_col)
        if not isinstance(cell, str) or "/" not in cell:
            continue
        rating = cell.split("/")[0]
        if rating == "STRONG BUY":
            bias[row["symbol"]] = "bullish"
        elif rating == "STRONG SELL":
            bias[row["symbol"]] = "bearish"
    return bias


if __name__ == "__main__":
    bias = fetch_directional_bias()
    print(f"{len(bias)} symbols with a strong tilt")
    print(dict(list(bias.items())[:10]))
