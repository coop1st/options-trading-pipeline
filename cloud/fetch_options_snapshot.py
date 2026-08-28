"""
Self-contained cloud-side options-chain snapshot fetcher (component B).

Deliberately self-contained (no imports from the rest of this repo,
matching Projects/Stocks/cloud/*.py's convention): must run correctly in
an ephemeral GitHub Actions runner that only has this repo cloned, not
pipeline/config.py's Windows-specific SSL setup or the local database.

Run from the repo root: `python cloud/fetch_options_snapshot.py <session>`
  where <session> is one of: open, mid, close
"""
import os
import sys
import time
from datetime import date, timedelta

import pandas as pd
import requests
import yfinance as yf

LEDGER_URL = (
    "https://raw.githubusercontent.com/coop1st/stocks-research-pipeline/"
    "main/data/github_sync/daytrade_ledger/stock_price_ledger.csv"
)
MAX_DTE_DAYS = 75
PACE_SECONDS = 1.5
OUT_COLS = [
    "symbol", "expiration", "contract_symbol", "strike", "type",
    "last_price", "bid", "ask", "volume", "open_interest",
    "implied_volatility", "in_the_money", "last_trade_date", "underlying_price",
]


def fetch_watchlist():
    resp = requests.get(LEDGER_URL, timeout=30)
    resp.raise_for_status()
    from io import StringIO
    df = pd.read_csv(StringIO(resp.text))
    return sorted(df["symbol"].dropna().unique().tolist())


def _underlying_price(ticker):
    hist = ticker.history(period="1d")
    if hist.empty:
        return None
    return float(hist["Close"].iloc[-1])


def _rows_for_symbol(symbol, today):
    rows = []
    ticker = yf.Ticker(symbol)
    underlying_price = _underlying_price(ticker)
    if underlying_price is None:
        print(f"{symbol}: no underlying price, skipping")
        return rows

    expirations = ticker.options
    cutoff = today + timedelta(days=MAX_DTE_DAYS)
    for exp_str in expirations:
        exp_date = date.fromisoformat(exp_str)
        if exp_date > cutoff:
            continue
        chain = ticker.option_chain(exp_str)
        for opt_type, df in (("call", chain.calls), ("put", chain.puts)):
            for _, r in df.iterrows():
                rows.append({
                    "symbol": symbol,
                    "expiration": exp_str,
                    "contract_symbol": r["contractSymbol"],
                    "strike": r["strike"],
                    "type": opt_type,
                    "last_price": r["lastPrice"],
                    "bid": r["bid"],
                    "ask": r["ask"],
                    "volume": int(r["volume"]) if pd.notna(r["volume"]) else 0,
                    "open_interest": int(r["openInterest"]) if pd.notna(r["openInterest"]) else 0,
                    "implied_volatility": r["impliedVolatility"],
                    "in_the_money": bool(r["inTheMoney"]),
                    "last_trade_date": str(r["lastTradeDate"]),
                    "underlying_price": underlying_price,
                })
    return rows


def main():
    session = sys.argv[1] if len(sys.argv) > 1 else None
    if session not in ("open", "mid", "close"):
        print("Usage: python cloud/fetch_options_snapshot.py <open|mid|close>")
        sys.exit(1)

    today = date.today()
    symbols = fetch_watchlist()  # a failure here propagates and fails the job -- no watchlist, nothing to snapshot
    print(f"Watchlist: {len(symbols)} symbols")

    all_rows = []
    skipped = []
    for i, symbol in enumerate(symbols):
        try:
            rows = _rows_for_symbol(symbol, today)
            if rows:
                all_rows.extend(rows)
            else:
                skipped.append(symbol)
        except Exception as e:
            print(f"{symbol}: SKIPPED ({e})")
            skipped.append(symbol)
        time.sleep(PACE_SECONDS)
        if (i + 1) % 20 == 0:
            print(f"...{i + 1}/{len(symbols)} symbols processed, {len(all_rows)} rows so far")

    out_dir = "data/github_sync/options_snapshots"
    os.makedirs(out_dir, exist_ok=True)
    out_path = f"{out_dir}/{today.isoformat()}_{session}.csv"
    pd.DataFrame(all_rows, columns=OUT_COLS).to_csv(out_path, index=False)

    print(
        f"SNAPSHOT_READY session={session} rows={len(all_rows)} "
        f"symbols_ok={len(symbols) - len(skipped)}/{len(symbols)} skipped={skipped}"
    )


if __name__ == "__main__":
    main()
