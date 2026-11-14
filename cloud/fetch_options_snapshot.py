"""
Self-contained cloud-side options-chain snapshot fetcher (component B).

Deliberately self-contained (no imports from the rest of this repo,
matching Projects/Stocks/cloud/*.py's convention): must run correctly in
an ephemeral GitHub Actions runner that only has this repo cloned, not
pipeline/config.py's Windows-specific SSL setup or the local database.

Run from the repo root: `python cloud/fetch_options_snapshot.py <session> [--force]`
  where <session> is one of: open, mid, close

Skips (exit 0, no file written) on weekends, NYSE full-day holidays, and
when today's file for that session already exists and is non-empty.
`--force` or OPTIONS_SNAPSHOT_FORCE=1 overrides both skips (manual runs).
"""
import os
import sys
import time
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd
import requests
import yfinance as yf

LEDGER_URL = (
    "https://raw.githubusercontent.com/coop1st/stocks-research-pipeline/"
    "main/data/github_sync/daytrade_ledger/stock_price_ledger.csv"
)
MAX_DTE_DAYS = 75

# Snapshots are dated by the US market day, not the runner's UTC date: GitHub
# starts these crons hours late, and a close run finishing after 00:00 UTC
# was filed under the next day and then overwritten by that day's real close
# (lost the 2026-10-05 and 2026-10-08 closes).
MARKET_TZ = ZoneInfo("America/New_York")

# NYSE full-day closures. Without this, a holiday's crons save a stale chain
# that later gets scored as a trading day. Half-days (e.g. the day after
# Thanksgiving, Christmas Eve) are trading days and are deliberately NOT
# listed. THIS LIST NEEDS EXTENDING EACH YEAR (add 2028 before 1 Jan 2028).
NYSE_FULL_DAY_HOLIDAYS = {
    # 2026
    date(2026, 1, 1), date(2026, 1, 19), date(2026, 2, 16), date(2026, 4, 3),
    date(2026, 5, 25), date(2026, 6, 19), date(2026, 7, 3), date(2026, 9, 7),
    date(2026, 11, 26), date(2026, 12, 25),
    # 2027
    date(2027, 1, 1), date(2027, 1, 18), date(2027, 2, 15), date(2027, 3, 26),
    date(2027, 5, 31), date(2027, 6, 18), date(2027, 7, 5), date(2027, 9, 6),
    date(2027, 11, 25), date(2027, 12, 24),
}
OUT_DIR = "data/github_sync/options_snapshots"


def non_trading_reason(day):
    """Return why `day` is not an NYSE trading day, or None if it is."""
    if day.weekday() >= 5:
        return "weekend"
    if day in NYSE_FULL_DAY_HOLIDAYS:
        return "NYSE full-day holiday"
    if day.year > max(d.year for d in NYSE_FULL_DAY_HOLIDAYS):
        print(f"WARNING: NYSE_FULL_DAY_HOLIDAYS has no entries for {day.year}; extend it")
    return None

# Tail-hedge instruments for the portfolio-insurance reminder (New Data
# Prerequisites item 4) -- priority-ordered per hedge type in
# pipeline/screen_trades.py, not here; this just makes sure they're
# fetched. Never suggested by the day-trade shortlist, so they'd
# otherwise never appear in the watchlist. Existing per-symbol
# skip-and-continue handling below is the fallback mechanism itself: if
# ^SPX or ^VIX isn't fetchable via yfinance on a given day, it's simply
# absent from that day's snapshot, same as any other skipped symbol.
TAIL_HEDGE_SYMBOLS = ["^SPX", "SPY", "^VIX", "VXX", "UVXY"]
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
    args = [a for a in sys.argv[1:] if a != "--force"]
    force = "--force" in sys.argv[1:] or os.environ.get("OPTIONS_SNAPSHOT_FORCE") == "1"
    session = args[0] if args else None
    if session not in ("open", "mid", "close"):
        print("Usage: python cloud/fetch_options_snapshot.py <open|mid|close> [--force]")
        sys.exit(1)

    today = datetime.now(MARKET_TZ).date()
    out_path = f"{OUT_DIR}/{today.isoformat()}_{session}.csv"
    if not force:
        reason = non_trading_reason(today)
        if reason:
            print(f"SKIPPED: {today.isoformat()} (New York) is a {reason}; no snapshot written. Use --force to override.")
            return
        if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
            print(f"SKIPPED: {out_path} already exists and is non-empty; not overwriting. Use --force to override.")
            return

    symbols = sorted(set(fetch_watchlist()) | set(TAIL_HEDGE_SYMBOLS))  # a failure here propagates and fails the job -- no watchlist, nothing to snapshot
    print(f"Watchlist: {len(symbols)} symbols (including {len(TAIL_HEDGE_SYMBOLS)} tail-hedge instruments)")

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

    os.makedirs(OUT_DIR, exist_ok=True)
    pd.DataFrame(all_rows, columns=OUT_COLS).to_csv(out_path, index=False)

    print(
        f"SNAPSHOT_READY session={session} rows={len(all_rows)} "
        f"symbols_ok={len(symbols) - len(skipped)}/{len(symbols)} skipped={skipped}"
    )


if __name__ == "__main__":
    main()
