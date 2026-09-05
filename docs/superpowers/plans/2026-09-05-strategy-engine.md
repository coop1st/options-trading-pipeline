# Strategy/Screening Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build sub-project 3 end-to-end: fill the four data gaps the spec identified (daily true-range/ATR, skew history, term-structure history, tail-hedge instruments), build one hard-gated candidate builder per strategy family (vertical credit spreads, iron condors, directional longs, calendars, double diagonals), a 7-criteria composite scorer, an orchestrator that ranks the top 20 and writes the options recommendation ledger with a position-sizing suggestion and a portfolio-insurance reminder, and update the nightly cloud routine to draft real recommendations instead of the current diagnostic placeholder.

**Architecture:** Mirrors sub-project 2's cloud/local split. A new daily GitHub Actions workflow fetches OHLC/true-range data and publishes a ledger; `pipeline/atr.py` refreshes a cached 14-day ATR from it weekly. `pipeline/db.py` gains `skew_history`, `atr_by_symbol`, and a term-structure query over the existing `atm_iv_history` table. `pipeline/strategy_rules.py` builds hard-gated candidates per family from the daily signals export plus the two Stocks ledgers; `pipeline/scoring.py` scores them; `pipeline/screen_trades.py` (the new orchestrator, mirroring `merge_and_score.py`'s shape) ties it all together and publishes the recommendation ledger.

**Tech Stack:** Python 3.12, pandas, requests, yfinance (cloud only), SQLite — same stack as sub-project 2, no new dependencies.

**Spec:** `docs/superpowers/specs/2026-09-05-strategy-engine-design.md`

## Global Constraints

- This repo has no pytest suite — every script is verified by running it directly and inspecting output, matching sub-project 2's convention. Verification scripts use plain `assert`/`print` checks (see `pipeline/verify_greeks.py` for the house style), not a test framework.
- Same-repo published data (this repo's own `data/github_sync/...` files) is read from the local working copy after `git pull`, exactly like `merge_and_score.py` already reads `options_snapshots/*.csv` — **not** via `raw.githubusercontent.com`. That cross-repo HTTP-fetch pattern is reserved for the two Stocks-project ledgers, which live in a different repository entirely. (This corrects one line in the spec's New Data Prerequisites §1, which suggested a raw-HTTP read for the true-range ledger; a local file read after `git pull` is simpler and matches the codebase's actual convention for own-repo data.)
- Cloud scripts under `cloud/` stay self-contained (no imports from the rest of this repo, matching `cloud/fetch_options_snapshot.py`'s existing convention) — they run on an ephemeral GitHub Actions runner with only the repo checked out.
- `MIN_VOLUME = 10`, `MIN_OPEN_INTEREST = 50` (already in `config.py`) remain the per-contract liquidity floor; this plan adds `EQUITY_MIN_DAILY_VOLUME = 50000` as the separate underlying-level liquidity floor from `directional-strategies.md` §5.
- Every hard-gate threshold below is either book-verbatim (cited inline) or an explicit implementation choice already flagged as such in the spec — none are invented here that the spec didn't already surface.
- `ACCOUNT_EQUITY` is a new fixed config constant the user edits directly (same precedent as `RISK_FREE_RATE`), not fetched from anywhere — no account-balance data source exists in this project.

---

## File Structure

- **Create** `cloud/fetch_daily_true_range.py` — self-contained daily OHLC/true-range cloud fetch (data prerequisite 1a).
- **Create** `.github/workflows/daily-true-range-fetch.yml` — daily cron for the above.
- **Create** `pipeline/atr.py` — weekly local ATR refresh from the true-range ledger (data prerequisite 1b).
- **Modify** `pipeline/db.py` — add `skew_history` table + upserts (prerequisite 2), `atr_by_symbol` table + upserts (prerequisite 1b), and a term-structure-spread query over the existing `atm_iv_history` table (prerequisite 3).
- **Modify** `pipeline/merge_and_score.py` — call the new skew-history upsert alongside the existing IV-history upsert.
- **Create** `pipeline/directional_bias.py` — reads the Stocks weekly ratings ledger for each symbol's latest bullish/bearish tilt.
- **Modify** `cloud/fetch_options_snapshot.py` — add the small fixed tail-hedge ticker set (prerequisite 4).
- **Modify** `pipeline/config.py` — new constants, added incrementally per task.
- **Create** `pipeline/strategy_rules.py` — one builder function per family (A–E), each hard-gated and book-cited.
- **Create** `pipeline/scoring.py` — the 7-criteria composite score, pure function, no I/O.
- **Create** `pipeline/screen_trades.py` — orchestrator: refreshes ATR, reads signals + both ledgers, calls every builder, scores and ranks, attaches sizing, writes the recommendation ledger plus the portfolio-insurance reminder, commits + pushes.
- **Create** `pipeline/verify_scoring.py` — manual verification script (hard-gate exclusion + per-criterion direction checks).
- **Deployment steps** (not files): run `screen_trades.py` against real data, confirm the ledger publishes; update the existing `RemoteTrigger` routine's prompt to draft real recommendations.

---

### Task 1: Daily true-range cloud fetch (data prerequisite 1a)

**Files:**
- Create: `cloud/fetch_daily_true_range.py`
- Create: `.github/workflows/daily-true-range-fetch.yml`
- Test: manual run against real data

**Interfaces:**
- Consumes (live HTTP): the Stocks project's public `stock_price_ledger.csv` (same `LEDGER_URL` as `cloud/fetch_options_snapshot.py`).
- Produces: `data/github_sync/daily_true_range/true_range_ledger.csv` — wide format: `symbol, company_name`, then one plain `YYYY-MM-DD` column per trading day (that day's true range) and one paired `close:YYYY-MM-DD` column (that day's close, so the next run can compute true range without a second fetch). Consumed by Task 3's `pipeline/atr.py`.

- [ ] **Step 1: Write the script**

```python
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

        prior_close_raw = existing.get(f"close:{sorted(k for k in existing if k.startswith('close:'))[-1][6:]}") if any(
            k.startswith("close:") for k in existing
        ) else None
        prior_close = float(prior_close_raw) if prior_close_raw not in (None, "", "nan") else None

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
    header = FIXED_COLS + [c for pair in zip(date_cols, close_cols) for c in pair]
    # date_cols and close_cols only stay zipped 1:1 once both lists share every date --
    # true for every date after this script's own first run, since it always writes
    # both columns together; append any leftovers so a partial first run still round-trips.
    header += [c for c in date_cols + close_cols if c not in header]

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    out_df = pd.DataFrame([{c: row.get(c, "") for c in header} for row in ledger.values()])
    out_df = out_df.sort_values("symbol")
    out_df.to_csv(OUT_PATH, index=False)

    print(f"TRUE_RANGE_READY date={today} symbols_ok={len(ledger) - len(skipped)}/{len(watchlist)} skipped={skipped}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run it locally against real data**

```bash
cd "C:\Users\coope\Claude_Work\Projects\Options Trading"
python cloud/fetch_daily_true_range.py
```

Expected: `TRUE_RANGE_READY date=... symbols_ok=M/T skipped=[...]` and `data/github_sync/daily_true_range/true_range_ledger.csv` populated with today's date column and `close:` column for most symbols.

- [ ] **Step 3: Write the GitHub Actions workflow**

```yaml
name: Daily true-range fetch

# Runs entirely in the cloud, once per trading day after close. Feeds
# pipeline/atr.py's weekly local ATR refresh -- mechanical fetch + a
# Wilder true-range formula, no judgment, so this is a GitHub Actions
# job (matching options-snapshot-fetch.yml's reasoning) not a Claude
# Code cloud routine.

on:
  schedule:
    - cron: "5 20 * * 1-5"  # ~4:05pm ET, after market close
  workflow_dispatch:

permissions:
  contents: write

jobs:
  fetch:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7

      - uses: actions/setup-python@v7
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: pip install -r pipeline/requirements.txt

      - name: Fetch daily true range
        run: python cloud/fetch_daily_true_range.py

      - name: Commit and push
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add data/github_sync/daily_true_range/
          if git diff --cached --quiet; then
            echo "No changes to commit"
          else
            git commit -m "Daily true range: $(date -u +%Y-%m-%d)"
            git push
          fi
```

- [ ] **Step 4: Commit, push, and verify one manual Actions run**

```bash
git add cloud/fetch_daily_true_range.py .github/workflows/daily-true-range-fetch.yml data/github_sync/daily_true_range/
git commit -m "Add daily true-range cloud fetch (ATR data prerequisite)"
git push
gh workflow run daily-true-range-fetch.yml
gh run list --workflow=daily-true-range-fetch.yml --limit 1
```

Expected: `completed success`.

---

### Task 2: `pipeline/db.py` additions — ATR, skew history, term-structure query

**Files:**
- Modify: `pipeline/db.py`
- Modify: `pipeline/config.py` (add `ATR_HISTORY_WINDOW = 14`, `ATR_REFRESH_DAYS = 7`)
- Test: manual roundtrip check

**Interfaces:**
- Produces: `get_atr_row(symbol) -> dict|None`, `upsert_atr(symbol, atr, computed_date)`, `upsert_skew_history(rows)`, `get_term_structure_spread_history(symbol, front_expiration, back_expiration, before_date, window_days=90) -> list[float]` — consumed by Task 3 (`atr.py`), Task 4 (`merge_and_score.py`), and Task 9's calendar/diagonal builders.

- [ ] **Step 1: Add the two constants to `pipeline/config.py`**

```python
# ATR refresh cadence (New Data Prerequisites item 1b) -- ATR is a
# slow-moving 14-day average, so a weekly local recompute is enough.
ATR_HISTORY_WINDOW = 14
ATR_REFRESH_DAYS = 7
```

- [ ] **Step 2: Extend `SCHEMA` in `pipeline/db.py`**

```python
CREATE TABLE IF NOT EXISTS skew_history (
    symbol TEXT NOT NULL,
    expiration TEXT NOT NULL,
    snapshot_date TEXT NOT NULL,
    skew_put_pct_of_atm REAL,
    skew_call_pct_of_atm REAL,
    PRIMARY KEY (symbol, expiration, snapshot_date)
);

CREATE TABLE IF NOT EXISTS atr_by_symbol (
    symbol TEXT PRIMARY KEY,
    atr REAL,
    computed_date TEXT
);
```

- [ ] **Step 3: Add the new functions to `pipeline/db.py`**

```python
def upsert_skew_history(rows):
    """rows: iterable of dicts with symbol, expiration, snapshot_date,
    skew_put_pct_of_atm, skew_call_pct_of_atm"""
    with get_connection() as conn:
        conn.executemany(
            """
            INSERT INTO skew_history (
                symbol, expiration, snapshot_date,
                skew_put_pct_of_atm, skew_call_pct_of_atm
            ) VALUES (
                :symbol, :expiration, :snapshot_date,
                :skew_put_pct_of_atm, :skew_call_pct_of_atm
            )
            ON CONFLICT(symbol, expiration, snapshot_date) DO UPDATE SET
                skew_put_pct_of_atm=excluded.skew_put_pct_of_atm,
                skew_call_pct_of_atm=excluded.skew_call_pct_of_atm
            """,
            rows,
        )


def get_atr_row(symbol):
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT atr, computed_date FROM atr_by_symbol WHERE symbol = ?", (symbol,)
        ).fetchone()
        return dict(row) if row else None


def upsert_atr(symbol, atr, computed_date):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO atr_by_symbol (symbol, atr, computed_date)
            VALUES (?, ?, ?)
            ON CONFLICT(symbol) DO UPDATE SET atr=excluded.atr, computed_date=excluded.computed_date
            """,
            (symbol, atr, computed_date),
        )


def get_term_structure_spread_history(symbol, front_expiration, back_expiration, before_date, window_days=90):
    """Front-minus-back ATM-IV spread on every prior date both
    expirations have a recorded atm_iv -- a query over the existing
    atm_iv_history table, not new persistence (New Data Prerequisites
    item 3)."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT f.atm_iv, b.atm_iv
            FROM atm_iv_history f
            JOIN atm_iv_history b
              ON f.symbol = b.symbol AND f.snapshot_date = b.snapshot_date
            WHERE f.symbol = ? AND f.expiration = ? AND b.expiration = ?
              AND f.snapshot_date < ? AND f.snapshot_date >= date(?, ?)
              AND f.atm_iv IS NOT NULL AND b.atm_iv IS NOT NULL
            """,
            (symbol, front_expiration, back_expiration, before_date, before_date, f"-{window_days} days"),
        ).fetchall()
        return [f - b for f, b in rows]
```

- [ ] **Step 4: Run a roundtrip check**

```bash
cd pipeline
python -c "
import db
db.init_db()
db.upsert_atr('AAPL', 3.25, '2026-09-05')
print('atr row:', db.get_atr_row('AAPL'))
db.upsert_skew_history([{'symbol':'AAPL','expiration':'2026-10-16','snapshot_date':'2026-09-05','skew_put_pct_of_atm':150.0,'skew_call_pct_of_atm':90.0}])
print('term structure history (expect []):', db.get_term_structure_spread_history('AAPL','2026-10-16','2026-11-20','2026-09-06'))
"
```

Expected: `atr row: {'atr': 3.25, 'computed_date': '2026-09-05'}` and an empty list for the term-structure query (only one expiration has history so far, the join has nothing to match).

- [ ] **Step 5: Commit**

```bash
git add pipeline/db.py pipeline/config.py
git commit -m "Add ATR, skew-history, and term-structure-query support to db.py"
```

---

### Task 3: Weekly local ATR refresh

**Files:**
- Create: `pipeline/atr.py`
- Test: manual run

**Interfaces:**
- Consumes: `config.ATR_HISTORY_WINDOW`, `config.ATR_REFRESH_DAYS`, `config.PROJECT_DIR` (Task 2); `db.get_atr_row`, `db.upsert_atr` (Task 2).
- Produces: `refresh_atr_if_stale(today=None) -> int` — consumed by Task 12's `screen_trades.py`.

- [ ] **Step 1: Write `pipeline/atr.py`**

```python
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
```

- [ ] **Step 2: Run it against real data (after Task 1's workflow has run at least once)**

```bash
cd "C:\Users\coope\Claude_Work\Projects\Options Trading"
git pull
python pipeline/atr.py
```

Expected: `Only N of 14 days...` until 14 days of history exist (this is correct, not a bug — matches the `atm_iv_90d_percentile` precedent), or `ATR refresh: M symbol(s) recomputed` once enough history has accumulated.

- [ ] **Step 3: Commit**

```bash
git add pipeline/atr.py
git commit -m "Add weekly local ATR refresh"
```

---

### Task 4: Persist skew history in `merge_and_score.py`

**Files:**
- Modify: `pipeline/merge_and_score.py`
- Test: manual run + spot-check

**Interfaces:**
- Consumes: `db.upsert_skew_history` (Task 2).

- [ ] **Step 1: Modify `compute_signals()` in `pipeline/merge_and_score.py`**

Add `upsert_skew_history` to the existing `from db import (...)` block:

```python
from db import (
    get_atm_iv_history,
    get_latest_snapshot_rows,
    get_most_recent_snapshot_date,
    init_db,
    is_merged,
    mark_merged,
    upsert_atm_iv_history,
    upsert_options_chain,
    upsert_skew_history,
)
```

Then, right after the existing `if history_rows: upsert_atm_iv_history(history_rows)` line, add a parallel skew-history collection and upsert. In the per-group loop where `skew_put_pct_of_atm`/`skew_call_pct_of_atm` are already computed, append a row to a new `skew_history_rows` list:

```python
    history_rows = []
    skew_history_rows = []
    group_failures = 0
    n_groups = 0

    for (symbol, expiration), group in df.groupby(["symbol", "expiration"]):
        n_groups += 1
        try:
            underlying_price = group["underlying_price"].iloc[0]
            atm_iv = _atm_iv(group, underlying_price)
            df.loc[group.index, "atm_iv"] = atm_iv
            if atm_iv:
                history_rows.append({
                    "symbol": symbol, "expiration": expiration,
                    "snapshot_date": snapshot_date, "atm_iv": atm_iv,
                })

            history = get_atm_iv_history(symbol, expiration, snapshot_date)
            if atm_iv is not None and len(history) >= 5:
                percentile = round(100 * sum(1 for h in history if h <= atm_iv) / len(history), 1)
                df.loc[group.index, "atm_iv_90d_percentile"] = percentile

            skew_row = {"symbol": symbol, "expiration": expiration, "snapshot_date": snapshot_date,
                        "skew_put_pct_of_atm": None, "skew_call_pct_of_atm": None}
            for opt_type, col in (("put", "skew_put_pct_of_atm"), ("call", "skew_call_pct_of_atm")):
                side = group[(group["type"] == opt_type) & group["delta"].notna()]
                if side.empty or not atm_iv:
                    continue
                closest = side.iloc[(side["delta"].abs() - SKEW_DELTA_TARGET).abs().argsort()[:1]]
                otm_iv = closest["implied_volatility"].iloc[0]
                skew_value = round(100 * otm_iv / atm_iv, 1)
                df.loc[group.index, col] = skew_value
                skew_row[col] = skew_value
            if skew_row["skew_put_pct_of_atm"] is not None or skew_row["skew_call_pct_of_atm"] is not None:
                skew_history_rows.append(skew_row)
        except Exception as exc:
            group_failures += 1
            print(f"IV/skew computation failed for {symbol!r} {expiration!r}: {exc}")
            continue

    if group_failures:
        print(f"IV/skew computation: {group_failures} failed of {n_groups} groups")

    if history_rows:
        upsert_atm_iv_history(history_rows)
    if skew_history_rows:
        upsert_skew_history(skew_history_rows)
```

This replaces the existing per-group loop body and the two upsert calls that follow it — the Greeks/liquidity sections above and the `signals = df[~df["low_liquidity"]]...` section below are unchanged.

- [ ] **Step 2: Run it against real data**

```bash
cd "C:\Users\coope\Claude_Work\Projects\Options Trading"
python pipeline/merge_and_score.py
```

Expected: same output shape as before (git pull, merge, scoring, publish), no new errors.

- [ ] **Step 3: Spot-check skew history was persisted**

```bash
cd pipeline
python -c "
import db
with db.get_connection() as conn:
    print(conn.execute('SELECT COUNT(*) FROM skew_history').fetchone())
"
```

Expected: a non-zero count.

- [ ] **Step 4: Commit**

```bash
git add pipeline/merge_and_score.py
git commit -m "Persist skew history alongside existing ATM IV history"
```

---

### Task 5: Directional bias reader

**Files:**
- Create: `pipeline/directional_bias.py`
- Test: manual run against real data

**Interfaces:**
- Produces: `fetch_directional_bias() -> dict[str, str]` (symbol → `"bullish"`/`"bearish"`, absent = neutral) — consumed by Task 6's vertical-spread builder, Task 8's directional-longs builder, and Task 12's `screen_trades.py`.

- [ ] **Step 1: Write the script**

```python
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
```

- [ ] **Step 2: Run it against real data**

```bash
cd "C:\Users\coope\Claude_Work\Projects\Options Trading"
python pipeline/directional_bias.py
```

Expected: `N symbols with a strong tilt`, a small sample dict of `{symbol: 'bullish'|'bearish'}` pairs. Cross-check a couple of entries manually against `Projects/Stocks/data/github_sync/weekly_ratings_ledger/stock_rating_ledger.csv`'s latest column.

- [ ] **Step 3: Commit**

```bash
git add pipeline/directional_bias.py
git commit -m "Add directional-bias reader for the Stocks weekly ratings ledger"
```

---

### Task 6: Tail-hedge tickers in the cloud fetch (data prerequisite 4)

**Files:**
- Modify: `cloud/fetch_options_snapshot.py`
- Test: manual run

**Interfaces:**
- Produces: `^SPX`, `SPY`, `^VIX`, `VXX`, `UVXY` now appear in `options_snapshots/*.csv` and therefore in `signals/{date}.csv` whenever their chains are fetchable — consumed by Task 13's portfolio-insurance reminder.

- [ ] **Step 1: Add the constant and merge it into the watchlist in `main()`**

```python
# Tail-hedge instruments for the portfolio-insurance reminder (New Data
# Prerequisites item 4) -- priority-ordered per hedge type in
# pipeline/screen_trades.py, not here; this just makes sure they're
# fetched. Never suggested by the day-trade shortlist, so they'd
# otherwise never appear in the watchlist. Existing per-symbol
# skip-and-continue handling below is the fallback mechanism itself: if
# ^SPX or ^VIX isn't fetchable via yfinance on a given day, it's simply
# absent from that day's snapshot, same as any other skipped symbol.
TAIL_HEDGE_SYMBOLS = ["^SPX", "SPY", "^VIX", "VXX", "UVXY"]
```

In `main()`, change:

```python
    symbols = fetch_watchlist()  # a failure here propagates and fails the job -- no watchlist, nothing to snapshot
    print(f"Watchlist: {len(symbols)} symbols")
```

to:

```python
    symbols = sorted(set(fetch_watchlist()) | set(TAIL_HEDGE_SYMBOLS))  # a failure here propagates and fails the job -- no watchlist, nothing to snapshot
    print(f"Watchlist: {len(symbols)} symbols (including {len(TAIL_HEDGE_SYMBOLS)} tail-hedge instruments)")
```

- [ ] **Step 2: Run it locally and confirm the tail-hedge symbols appear (or are cleanly skipped)**

```bash
cd "C:\Users\coope\Claude_Work\Projects\Options Trading"
python cloud/fetch_options_snapshot.py close
```

Expected: the `SNAPSHOT_READY` line's `skipped=[...]` list shows which of `^SPX`/`SPY`/`^VIX`/`VXX`/`UVXY` (if any) failed to fetch — this is expected information, not an error, per the resilient-by-construction design. At least `SPY` should typically succeed (it's an ordinary liquid ETF).

- [ ] **Step 3: Commit**

```bash
git add cloud/fetch_options_snapshot.py
git commit -m "Add tail-hedge instruments to the cloud snapshot fetch"
```

---

### Task 7: Strategy config constants + vertical credit spread builder (family A)

**Files:**
- Modify: `pipeline/config.py`
- Create: `pipeline/strategy_rules.py`
- Test: manual run against real signals data

**Interfaces:**
- Produces: `build_vertical_credit_spreads(signals, snapshot_date, bias) -> list[dict]`, plus the shared helpers `_dte`, `_nearest_by_abs_delta`, `_nearest_strike_row`, `_leg`, `_underlying_daily_volume` used by every later builder task.

- [ ] **Step 1: Add strategy-engine constants to `pipeline/config.py`**

```python
# Strategy-engine constants (docs/superpowers/specs/2026-09-05-strategy-engine-design.md)

# directional-strategies.md SS5: equity underlying-liquidity floor.
EQUITY_MIN_DAILY_VOLUME = 50000

# income-strategies.md SS3 / spreads-and-combinations.md SS1: vertical
# credit spread DTE window and delta band (band, not a fixed delta --
# strike selection is a scoring matter, not a gate).
VERTICAL_MIN_DTE = 30
VERTICAL_MAX_DTE = 60
VERTICAL_DELTA_BAND = (0.10, 0.30)
VERTICAL_SPREAD_WIDTHS = [5, 10]
```

- [ ] **Step 2: Write `pipeline/strategy_rules.py`**

```python
"""Strategy candidate builders (Component Detail, strategy-engine spec).
Each function takes one day's signals DataFrame (data/github_sync/signals/{date}.csv,
already loaded) plus whatever family-specific inputs it needs, and
returns a list of candidate dicts. Every hard gate is cited to its
source chapter in docs/superpowers/specs/2026-09-05-strategy-engine-design.md;
no threshold here is invented beyond what that spec already flags as an
explicit implementation choice.
"""
from datetime import date


def _dte(expiration, snapshot_date):
    return (date.fromisoformat(expiration) - date.fromisoformat(snapshot_date)).days


def _underlying_daily_volume(symbol_signals):
    """Proxy for directional-strategies.md SS5's underlying-level
    liquidity screen: sums today's per-contract volume across every
    strike/expiration for the symbol, since the pipeline doesn't fetch a
    separate daily-option-volume series per underlying."""
    return int(symbol_signals["volume"].sum())


def _nearest_by_abs_delta(df, target_abs_delta):
    if df.empty:
        return None
    idx = (df["delta"].abs() - target_abs_delta).abs().idxmin()
    return df.loc[idx]


def _nearest_strike_row(df, target_strike):
    if df.empty:
        return None
    idx = (df["strike"] - target_strike).abs().idxmin()
    return df.loc[idx]


def _leg(row, leg_role):
    return {
        "leg_role": leg_role,
        "contract_symbol": row["contract_symbol"],
        "strike": row["strike"],
        "expiration": row["expiration"],
        "type": row["type"],
        "delta": row["delta"],
        "last_price": row["last_price"],
        "bid": row["bid"],
        "ask": row["ask"],
        "volume": row["volume"],
        "open_interest": row["open_interest"],
        "atm_iv_90d_percentile": row["atm_iv_90d_percentile"],
        "skew_put_pct_of_atm": row["skew_put_pct_of_atm"],
        "skew_call_pct_of_atm": row["skew_call_pct_of_atm"],
        "zero_bid": row["zero_bid"],
        "wide_spread": row["wide_spread"],
    }


def build_vertical_credit_spreads(signals, snapshot_date, bias, min_dte, max_dte, delta_band, widths, min_daily_volume):
    """income-strategies.md SS3 / spreads-and-combinations.md SS1.
    Hard gates: DTE window, a bullish or bearish tilt present, underlying
    daily volume above the floor. Strike/width selection is a scoring
    matter, not a gate (both books warn against anchoring to one fixed
    delta or width) -- this builds one candidate per configured width
    around the delta band's midpoint."""
    candidates = []
    target_mid_delta = sum(delta_band) / 2

    for symbol, sym_df in signals.groupby("symbol"):
        tilt = bias.get(symbol)
        if tilt is None:
            continue  # no directional view -- this family isn't built for this symbol
        if _underlying_daily_volume(sym_df) <= min_daily_volume:
            continue

        opt_type = "put" if tilt == "bullish" else "call"
        strategy_name = f"vertical {opt_type} credit spread"

        for expiration, exp_df in sym_df[sym_df["type"] == opt_type].groupby("expiration"):
            dte = _dte(expiration, snapshot_date)
            if not (min_dte <= dte <= max_dte):
                continue

            atm_iv_row = exp_df["atm_iv"].dropna()
            this_expiration_atm_iv = float(atm_iv_row.iloc[0]) if not atm_iv_row.empty else None

            band_df = exp_df[(exp_df["delta"].abs() >= delta_band[0]) & (exp_df["delta"].abs() <= delta_band[1])]
            short_row = _nearest_by_abs_delta(band_df, target_mid_delta)
            if short_row is None:
                continue

            for width in widths:
                long_target = short_row["strike"] - width if opt_type == "put" else short_row["strike"] + width
                long_candidates = exp_df[exp_df["strike"] != short_row["strike"]]
                long_row = _nearest_strike_row(long_candidates, long_target)
                if long_row is None:
                    continue

                credit = short_row["last_price"] - long_row["last_price"]
                actual_width = abs(short_row["strike"] - long_row["strike"])
                if credit <= 0 or actual_width <= 0:
                    continue

                candidates.append({
                    "symbol": symbol,
                    "strategy": strategy_name,
                    "expiration": expiration,
                    "this_expiration_atm_iv": this_expiration_atm_iv,
                    "legs": [_leg(short_row, f"short {opt_type}"), _leg(long_row, f"long {opt_type}")],
                    "credit": credit,
                    "width": actual_width,
                    "max_loss": (actual_width - credit) * 100,
                    "short_delta": short_row["delta"],
                    "net_short": True,
                    "tilt": tilt,
                })
    return candidates
```

- [ ] **Step 3: Run it against real signals data**

```bash
cd "C:\Users\coope\Claude_Work\Projects\Options Trading"
python -c "
import pandas as pd
from datetime import date
import sys
sys.path.insert(0, 'pipeline')
from strategy_rules import build_vertical_credit_spreads
from directional_bias import fetch_directional_bias
from config import VERTICAL_MIN_DTE, VERTICAL_MAX_DTE, VERTICAL_DELTA_BAND, VERTICAL_SPREAD_WIDTHS, EQUITY_MIN_DAILY_VOLUME

today = sorted((p for p in __import__('pathlib').Path('data/github_sync/signals').glob('*.csv')))[-1]
signals = pd.read_csv(today)
snapshot_date = today.stem
bias = fetch_directional_bias()
candidates = build_vertical_credit_spreads(signals, snapshot_date, bias, VERTICAL_MIN_DTE, VERTICAL_MAX_DTE, VERTICAL_DELTA_BAND, VERTICAL_SPREAD_WIDTHS, EQUITY_MIN_DAILY_VOLUME)
print(f'{len(candidates)} vertical credit spread candidates')
if candidates:
    print(candidates[0])
"
```

Expected: a count (may be 0 if no symbol currently has both a strong tilt and enough DTE-window liquidity — inspect the printed sample if non-zero, confirming `credit > 0`, `width > 0`, and `legs` has exactly 2 entries).

- [ ] **Step 4: Commit**

```bash
git add pipeline/config.py pipeline/strategy_rules.py
git commit -m "Add strategy_rules.py with the vertical credit spread builder (family A)"
```

---

### Task 8: Iron condor builder (family B)

**Files:**
- Modify: `pipeline/config.py`
- Modify: `pipeline/strategy_rules.py`
- Test: manual run

**Interfaces:**
- Produces: `build_iron_condors(signals, snapshot_date, get_atr, min_dte, max_dte, delta_min, delta_max) -> list[dict]`.

- [ ] **Step 1: Add condor constants to `pipeline/config.py`**

```python
# income-strategies.md SS4 / spreads-and-combinations.md SS2: iron
# condor delta target and DTE window (45-75 is this spec's own
# operationalization of the book's "around 60 days," not a book number).
CONDOR_DELTA_MIN = 0.10
CONDOR_DELTA_MAX = 0.15
CONDOR_MIN_DTE = 45
CONDOR_MAX_DTE = 75
```

- [ ] **Step 2: Add `build_iron_condors` to `pipeline/strategy_rules.py`**

```python
def build_iron_condors(signals, snapshot_date, get_atr, min_dte, max_dte, delta_min, delta_max):
    """income-strategies.md SS4 / spreads-and-combinations.md SS2. Hard
    gates: delta_min-delta_max on both short strikes, min_dte-max_dte,
    and today's ATM IV > the underlying's 14-day ATR -- gated only once
    get_atr(symbol) returns a value; until then this gate is skipped for
    that symbol with a visible note, matching the atm_iv_90d_percentile
    precedent from sub-project 2."""
    candidates = []
    target_mid_delta = (delta_min + delta_max) / 2

    for symbol, sym_df in signals.groupby("symbol"):
        atr = get_atr(symbol)
        for expiration, exp_df in sym_df.groupby("expiration"):
            dte = _dte(expiration, snapshot_date)
            if not (min_dte <= dte <= max_dte):
                continue

            atm_iv_row = exp_df["atm_iv"].dropna()
            atm_iv = float(atm_iv_row.iloc[0]) if not atm_iv_row.empty else None
            if atr is None:
                print(f"{symbol}: no ATR yet -- skipping condor's IV-vs-ATR gate")
            elif atm_iv is None or atm_iv <= atr:
                continue

            calls = exp_df[exp_df["type"] == "call"]
            puts = exp_df[exp_df["type"] == "put"]
            call_band = calls[(calls["delta"] >= delta_min) & (calls["delta"] <= delta_max)]
            put_band = puts[(puts["delta"].abs() >= delta_min) & (puts["delta"].abs() <= delta_max)]
            short_call = _nearest_by_abs_delta(call_band, target_mid_delta)
            short_put = _nearest_by_abs_delta(put_band, target_mid_delta)
            if short_call is None or short_put is None:
                continue

            long_call = _nearest_strike_row(calls[calls["strike"] > short_call["strike"]], short_call["strike"] + 10)
            long_put = _nearest_strike_row(puts[puts["strike"] < short_put["strike"]], short_put["strike"] - 10)
            if long_call is None or long_put is None:
                continue

            credit = (
                short_call["last_price"] - long_call["last_price"]
                + short_put["last_price"] - long_put["last_price"]
            )
            width = min(abs(long_call["strike"] - short_call["strike"]), abs(short_put["strike"] - long_put["strike"]))
            if credit <= 0 or width <= 0:
                continue

            candidates.append({
                "symbol": symbol,
                "strategy": "iron condor",
                "expiration": expiration,
                "this_expiration_atm_iv": atm_iv,
                "legs": [
                    _leg(short_call, "short call"), _leg(long_call, "long call"),
                    _leg(short_put, "short put"), _leg(long_put, "long put"),
                ],
                "credit": credit,
                "width": width,
                "max_loss": (width - credit) * 100,
                "short_call_delta": short_call["delta"],
                "short_put_delta": short_put["delta"],
                "net_short": True,
                "tilt": None,
            })
    return candidates
```

- [ ] **Step 3: Run it against real data**

```bash
cd "C:\Users\coope\Claude_Work\Projects\Options Trading"
python -c "
import pandas as pd
from pathlib import Path
import sys
sys.path.insert(0, 'pipeline')
from strategy_rules import build_iron_condors
from db import get_atr_row
from config import CONDOR_MIN_DTE, CONDOR_MAX_DTE, CONDOR_DELTA_MIN, CONDOR_DELTA_MAX

today = sorted(Path('data/github_sync/signals').glob('*.csv'))[-1]
signals = pd.read_csv(today)
get_atr = lambda s: (get_atr_row(s) or {}).get('atr')
candidates = build_iron_condors(signals, today.stem, get_atr, CONDOR_MIN_DTE, CONDOR_MAX_DTE, CONDOR_DELTA_MIN, CONDOR_DELTA_MAX)
print(f'{len(candidates)} iron condor candidates')
if candidates:
    print(candidates[0])
"
```

Expected: a count (0 is acceptable if ATR data hasn't accumulated yet — check for the "no ATR yet" print lines); if non-zero, confirm `legs` has exactly 4 entries and `credit > 0`.

- [ ] **Step 4: Commit**

```bash
git add pipeline/config.py pipeline/strategy_rules.py
git commit -m "Add iron condor builder (family B)"
```

---

### Task 9: Directional long call/put builder (family C)

**Files:**
- Modify: `pipeline/strategy_rules.py`
- Test: manual run

**Interfaces:**
- Produces: `build_directional_longs(signals, bias, min_daily_volume) -> list[dict]`.

- [ ] **Step 1: Add `build_directional_longs` to `pipeline/strategy_rules.py`**

```python
def build_directional_longs(signals, bias, min_daily_volume):
    """directional-strategies.md SS1-2, SS5. Hard gates: a bullish or
    bearish tilt present, underlying daily volume above the floor. No
    DTE gate -- the books frame this via the three-part price/time/
    volatility forecast, not a DTE rule, so none is invented here."""
    candidates = []
    for symbol, sym_df in signals.groupby("symbol"):
        tilt = bias.get(symbol)
        if tilt is None:
            continue
        if _underlying_daily_volume(sym_df) <= min_daily_volume:
            continue

        opt_type = "call" if tilt == "bullish" else "put"
        atm_candidates = sym_df[sym_df["type"] == opt_type]
        atm_row = _nearest_by_abs_delta(atm_candidates, 0.50)
        if atm_row is None:
            continue

        atm_iv_row = sym_df[sym_df["expiration"] == atm_row["expiration"]]["atm_iv"].dropna()
        this_expiration_atm_iv = float(atm_iv_row.iloc[0]) if not atm_iv_row.empty else None

        candidates.append({
            "symbol": symbol,
            "strategy": f"long {opt_type}",
            "expiration": atm_row["expiration"],
            "this_expiration_atm_iv": this_expiration_atm_iv,
            "legs": [_leg(atm_row, f"long {opt_type}")],
            "max_loss": atm_row["last_price"] * 100,
            "net_short": False,
            "tilt": tilt,
        })
    return candidates
```

- [ ] **Step 2: Run it against real data**

```bash
cd "C:\Users\coope\Claude_Work\Projects\Options Trading"
python -c "
import pandas as pd
from pathlib import Path
import sys
sys.path.insert(0, 'pipeline')
from strategy_rules import build_directional_longs
from directional_bias import fetch_directional_bias
from config import EQUITY_MIN_DAILY_VOLUME

today = sorted(Path('data/github_sync/signals').glob('*.csv'))[-1]
signals = pd.read_csv(today)
bias = fetch_directional_bias()
candidates = build_directional_longs(signals, bias, EQUITY_MIN_DAILY_VOLUME)
print(f'{len(candidates)} directional long candidates')
if candidates:
    print(candidates[0])
"
```

Expected: a count; if non-zero, confirm `legs` has exactly 1 entry and `strategy` is `"long call"` or `"long put"` matching the symbol's tilt.

- [ ] **Step 3: Commit**

```bash
git add pipeline/strategy_rules.py
git commit -m "Add directional long call/put builder (family C)"
```

---

### Task 10: Calendar spread builder (family D)

**Files:**
- Modify: `pipeline/config.py`
- Modify: `pipeline/strategy_rules.py`
- Test: manual run

**Interfaces:**
- Produces: `build_calendars(signals, snapshot_date, get_term_structure_history, min_front_days, long_premium_min, long_premium_max, short_discount) -> list[dict]`.

- [ ] **Step 1: Add calendar constants to `pipeline/config.py`**

```python
# spreads-and-combinations.md SS4: calendar entry thresholds. 10 days is
# this spec's own operationalization of "avoid the final days before
# expiration" -- not a book number.
CALENDAR_MIN_FRONT_DAYS = 10
CALENDAR_LONG_PREMIUM_MIN = 0.10
CALENDAR_LONG_PREMIUM_MAX = 0.25
CALENDAR_SHORT_DISCOUNT = 0.10
```

- [ ] **Step 2: Add `build_calendars` to `pipeline/strategy_rules.py`**

```python
def build_calendars(signals, snapshot_date, get_term_structure_history, min_front_days, long_premium_min, long_premium_max, short_discount):
    """spreads-and-combinations.md SS4. Hard gates: front-month premium
    (>=long_premium_min, excluded above long_premium_max without manual
    review) or discount (>=short_discount) to its 'normal' relationship
    with the back month, front leg >= min_front_days from expiration,
    and enough accumulated term-structure-spread history to judge
    'normal' at all -- until then this symbol/expiration pair is skipped
    with a visible note."""
    candidates = []
    for symbol, sym_df in signals.groupby("symbol"):
        for opt_type, type_df in sym_df.groupby("type"):
            expirations = sorted(type_df["expiration"].unique())
            for i, front_exp in enumerate(expirations):
                if _dte(front_exp, snapshot_date) < min_front_days:
                    continue
                front_atm_iv_series = type_df[type_df["expiration"] == front_exp]["atm_iv"].dropna()
                if front_atm_iv_series.empty:
                    continue
                front_atm_iv = float(front_atm_iv_series.iloc[0])

                for back_exp in expirations[i + 1:]:
                    back_atm_iv_series = type_df[type_df["expiration"] == back_exp]["atm_iv"].dropna()
                    if back_atm_iv_series.empty:
                        continue
                    back_atm_iv = float(back_atm_iv_series.iloc[0])

                    history = get_term_structure_history(symbol, front_exp, back_exp)
                    if len(history) < 5:
                        print(f"{symbol} {front_exp}/{back_exp}: not enough term-structure history yet -- skipping calendar gate")
                        continue
                    normal_spread = sum(history) / len(history)
                    current_spread = front_atm_iv - back_atm_iv
                    if front_atm_iv == 0:
                        continue
                    premium = (current_spread - normal_spread) / front_atm_iv

                    if long_premium_min <= premium <= long_premium_max:
                        strategy, short_exp, long_exp = "long calendar", front_exp, back_exp
                    elif -premium >= short_discount:
                        strategy, short_exp, long_exp = "short calendar", back_exp, front_exp
                    else:
                        continue

                    strike_row = _nearest_by_abs_delta(type_df[type_df["expiration"] == front_exp], 0.50)
                    if strike_row is None:
                        continue
                    short_match = type_df[(type_df["expiration"] == short_exp) & (type_df["strike"] == strike_row["strike"])]
                    long_match = type_df[(type_df["expiration"] == long_exp) & (type_df["strike"] == strike_row["strike"])]
                    if short_match.empty or long_match.empty:
                        continue
                    short_row, long_row = short_match.iloc[0], long_match.iloc[0]

                    net_debit = long_row["last_price"] - short_row["last_price"]
                    candidates.append({
                        "symbol": symbol,
                        "strategy": strategy,
                        "expiration": front_exp,
                        "this_expiration_atm_iv": front_atm_iv,
                        "legs": [_leg(short_row, f"short {opt_type}"), _leg(long_row, f"long {opt_type}")],
                        "max_loss": abs(net_debit) * 100,
                        "premium": premium,
                        "net_short": strategy == "long calendar",
                        "tilt": None,
                    })
    return candidates
```

- [ ] **Step 3: Run it against real data**

```bash
cd "C:\Users\coope\Claude_Work\Projects\Options Trading"
python -c "
import pandas as pd
from pathlib import Path
import sys
sys.path.insert(0, 'pipeline')
from strategy_rules import build_calendars
from db import get_term_structure_spread_history
from config import CALENDAR_MIN_FRONT_DAYS, CALENDAR_LONG_PREMIUM_MIN, CALENDAR_LONG_PREMIUM_MAX, CALENDAR_SHORT_DISCOUNT

today = sorted(Path('data/github_sync/signals').glob('*.csv'))[-1]
signals = pd.read_csv(today)
get_hist = lambda sym, f, b: get_term_structure_spread_history(sym, f, b, today.stem)
candidates = build_calendars(signals, today.stem, get_hist, CALENDAR_MIN_FRONT_DAYS, CALENDAR_LONG_PREMIUM_MIN, CALENDAR_LONG_PREMIUM_MAX, CALENDAR_SHORT_DISCOUNT)
print(f'{len(candidates)} calendar candidates')
"
```

Expected: `0 calendar candidates` is the realistic near-term result (term-structure history needs 5+ accumulated days per expiration pair, which won't exist yet this soon after sub-project 2 shipped) — confirm the "not enough term-structure history yet" print lines appear instead of a silent empty result, proving the gate is being evaluated, not skipped entirely.

- [ ] **Step 4: Commit**

```bash
git add pipeline/config.py pipeline/strategy_rules.py
git commit -m "Add calendar spread builder (family D)"
```

---

### Task 11: Double diagonal builder (family E)

**Files:**
- Modify: `pipeline/strategy_rules.py`
- Test: manual run

**Interfaces:**
- Produces: `build_double_diagonals(signals, snapshot_date, get_term_structure_history, min_front_days, long_premium_min, delta_min, delta_max) -> list[dict]`.

- [ ] **Step 1: Add `build_double_diagonals` to `pipeline/strategy_rules.py`**

```python
def build_double_diagonals(signals, snapshot_date, get_term_structure_history, min_front_days, long_premium_min, delta_min, delta_max):
    """spreads-and-combinations.md SS5. Same term-structure gate as
    build_calendars (front month elevated relative to a further-out back
    month). Double diagonal only -- a single-sided diagonal has no
    book-given entry rule (spec Non-goals)."""
    candidates = []
    target_mid_delta = (delta_min + delta_max) / 2

    for symbol, sym_df in signals.groupby("symbol"):
        expirations = sorted(sym_df["expiration"].unique())
        for i, front_exp in enumerate(expirations):
            if _dte(front_exp, snapshot_date) < min_front_days:
                continue
            front_df = sym_df[sym_df["expiration"] == front_exp]
            front_atm_iv_series = front_df["atm_iv"].dropna()
            if front_atm_iv_series.empty:
                continue
            front_atm_iv = float(front_atm_iv_series.iloc[0])

            for back_exp in expirations[i + 1:]:
                back_df = sym_df[sym_df["expiration"] == back_exp]
                back_atm_iv_series = back_df["atm_iv"].dropna()
                if back_atm_iv_series.empty:
                    continue
                back_atm_iv = float(back_atm_iv_series.iloc[0])

                history = get_term_structure_history(symbol, front_exp, back_exp)
                if len(history) < 5:
                    continue
                normal_spread = sum(history) / len(history)
                if front_atm_iv == 0:
                    continue
                premium = ((front_atm_iv - back_atm_iv) - normal_spread) / front_atm_iv
                if premium < long_premium_min:
                    continue

                front_call_band = front_df[(front_df["type"] == "call") & (front_df["delta"] >= delta_min) & (front_df["delta"] <= delta_max)]
                front_put_band = front_df[(front_df["type"] == "put") & (front_df["delta"].abs() >= delta_min) & (front_df["delta"].abs() <= delta_max)]
                short_call = _nearest_by_abs_delta(front_call_band, target_mid_delta)
                short_put = _nearest_by_abs_delta(front_put_band, target_mid_delta)
                if short_call is None or short_put is None:
                    continue

                back_calls = back_df[back_df["type"] == "call"]
                back_puts = back_df[back_df["type"] == "put"]
                long_call = _nearest_strike_row(back_calls, short_call["strike"] + 10)
                long_put = _nearest_strike_row(back_puts, short_put["strike"] - 10)
                if long_call is None or long_put is None:
                    continue

                net_debit = (
                    long_call["last_price"] - short_call["last_price"]
                    + long_put["last_price"] - short_put["last_price"]
                )
                candidates.append({
                    "symbol": symbol,
                    "strategy": "double diagonal",
                    "expiration": front_exp,
                    "this_expiration_atm_iv": front_atm_iv,
                    "legs": [
                        _leg(short_call, "short call"), _leg(long_call, "long call"),
                        _leg(short_put, "short put"), _leg(long_put, "long put"),
                    ],
                    "max_loss": abs(net_debit) * 100,
                    "premium": premium,
                    "net_short": True,
                    "tilt": None,
                })
    return candidates
```

- [ ] **Step 2: Run it against real data**

```bash
cd "C:\Users\coope\Claude_Work\Projects\Options Trading"
python -c "
import pandas as pd
from pathlib import Path
import sys
sys.path.insert(0, 'pipeline')
from strategy_rules import build_double_diagonals
from db import get_term_structure_spread_history
from config import CALENDAR_MIN_FRONT_DAYS, CALENDAR_LONG_PREMIUM_MIN, CONDOR_DELTA_MIN, CONDOR_DELTA_MAX

today = sorted(Path('data/github_sync/signals').glob('*.csv'))[-1]
signals = pd.read_csv(today)
get_hist = lambda sym, f, b: get_term_structure_spread_history(sym, f, b, today.stem)
candidates = build_double_diagonals(signals, today.stem, get_hist, CALENDAR_MIN_FRONT_DAYS, CALENDAR_LONG_PREMIUM_MIN, CONDOR_DELTA_MIN, CONDOR_DELTA_MAX)
print(f'{len(candidates)} double diagonal candidates')
"
```

Expected: `0` for the same reason as Task 10 (insufficient term-structure history yet) — this is correct, not a bug.

- [ ] **Step 3: Commit**

```bash
git add pipeline/strategy_rules.py
git commit -m "Add double diagonal builder (family E)"
```

---

### Task 12: Composite scoring module

**Files:**
- Create: `pipeline/scoring.py`
- Create: `pipeline/verify_scoring.py`
- Test: `pipeline/verify_scoring.py`

**Interfaces:**
- Consumes: candidate dicts from every builder in Task 7-11 (shape: `symbol, strategy, expiration, this_expiration_atm_iv, legs, max_loss, net_short, tilt`, plus family-specific keys `credit`/`width`/`short_delta`/`short_call_delta`/`short_put_delta`/`premium`).
- Produces: `score_candidate(candidate, min_volume, min_open_interest, calendar_premium_min, calendar_premium_max, other_expirations_atm_iv=None) -> (float, dict)` — consumed by Task 13's `screen_trades.py`.

- [ ] **Step 1: Write the failing verification script first**

```python
"""
Verifies pipeline/scoring.py's composite score moves in the book-cited
direction as each of the 7 criteria's underlying input improves, and
that a candidate's score never depends on a criterion the family/data
doesn't support (those default to a neutral 50, per the strategy-engine
spec's explicit policy). No pytest in this repo -- run directly and
inspect output, same convention as verify_greeks.py.

Run: python pipeline/verify_scoring.py
"""
import sys

from scoring import score_candidate

MIN_VOLUME, MIN_OI = 10, 50
PREMIUM_MIN, PREMIUM_MAX = 0.10, 0.25


def _leg(**overrides):
    base = {
        "leg_role": "short put", "contract_symbol": "X", "strike": 100, "expiration": "2026-10-16",
        "type": "put", "delta": -0.15, "last_price": 1.0, "bid": 0.95, "ask": 1.05,
        "volume": 100, "open_interest": 200, "atm_iv_90d_percentile": 50.0,
        "skew_put_pct_of_atm": 150.0, "skew_call_pct_of_atm": 90.0,
        "zero_bid": False, "wide_spread": False,
    }
    base.update(overrides)
    return base


def check(label, condition):
    print(f"{'OK' if condition else 'FAIL'}: {label}")
    return condition


def main():
    all_ok = True

    # Criterion 1: net-short candidate should score HIGHER as IV percentile rises.
    low_iv = {"symbol": "X", "strategy": "vertical put credit spread", "expiration": "2026-10-16",
              "this_expiration_atm_iv": 0.25, "legs": [_leg(atm_iv_90d_percentile=20.0)],
              "credit": 1.0, "width": 5.0, "max_loss": 400.0, "short_delta": -0.15,
              "net_short": True, "tilt": "bullish"}
    high_iv = {**low_iv, "legs": [_leg(atm_iv_90d_percentile=80.0)]}
    score_low, _ = score_candidate(low_iv, MIN_VOLUME, MIN_OI, PREMIUM_MIN, PREMIUM_MAX)
    score_high, _ = score_candidate(high_iv, MIN_VOLUME, MIN_OI, PREMIUM_MIN, PREMIUM_MAX)
    all_ok &= check("net-short: higher IV percentile scores higher", score_high > score_low)

    # Same criterion, opposite direction for a net-long candidate (directional-strategies.md SS5).
    long_low_iv = {"symbol": "X", "strategy": "long call", "expiration": "2026-10-16",
                   "this_expiration_atm_iv": 0.25, "legs": [_leg(type="call", delta=0.50, atm_iv_90d_percentile=20.0)],
                   "max_loss": 500.0, "net_short": False, "tilt": "bullish"}
    long_high_iv = {**long_low_iv, "legs": [_leg(type="call", delta=0.50, atm_iv_90d_percentile=80.0)]}
    score_long_low, _ = score_candidate(long_low_iv, MIN_VOLUME, MIN_OI, PREMIUM_MIN, PREMIUM_MAX)
    score_long_high, _ = score_candidate(long_high_iv, MIN_VOLUME, MIN_OI, PREMIUM_MIN, PREMIUM_MAX)
    all_ok &= check("net-long: LOWER IV percentile scores higher", score_long_low > score_long_high)

    # Criterion 3: risk/reward -- higher credit/width should score higher for a vertical spread.
    low_credit = {**low_iv, "credit": 0.5}
    high_credit = {**low_iv, "credit": 2.0}
    _, breakdown_low = score_candidate(low_credit, MIN_VOLUME, MIN_OI, PREMIUM_MIN, PREMIUM_MAX)
    _, breakdown_high = score_candidate(high_credit, MIN_VOLUME, MIN_OI, PREMIUM_MIN, PREMIUM_MAX)
    all_ok &= check("higher credit/width scores higher risk_reward", breakdown_high["risk_reward"] > breakdown_low["risk_reward"])

    # Criterion 4: POP proxy -- a further-OTM (lower |delta|) short strike scores higher.
    far_otm = {**low_iv, "short_delta": -0.10}
    near_atm = {**low_iv, "short_delta": -0.30}
    _, b_far = score_candidate(far_otm, MIN_VOLUME, MIN_OI, PREMIUM_MIN, PREMIUM_MAX)
    _, b_near = score_candidate(near_atm, MIN_VOLUME, MIN_OI, PREMIUM_MIN, PREMIUM_MAX)
    all_ok &= check("further-OTM short strike scores higher pop_proxy", b_far["pop_proxy"] > b_near["pop_proxy"])

    # Criterion 6: liquidity -- higher volume/OI, no flags, scores higher.
    illiquid = {**low_iv, "legs": [_leg(volume=1, open_interest=5, zero_bid=True, wide_spread=True)]}
    liquid = {**low_iv, "legs": [_leg(volume=500, open_interest=1000)]}
    _, b_illiquid = score_candidate(illiquid, MIN_VOLUME, MIN_OI, PREMIUM_MIN, PREMIUM_MAX)
    _, b_liquid = score_candidate(liquid, MIN_VOLUME, MIN_OI, PREMIUM_MIN, PREMIUM_MAX)
    all_ok &= check("liquid legs score higher than illiquid/flagged legs", b_liquid["liquidity"] > b_illiquid["liquidity"])

    # Criterion 7: directional families need a tilt to score full marks; neutral families need the absence of one.
    _, b_directional_with_tilt = score_candidate(low_iv, MIN_VOLUME, MIN_OI, PREMIUM_MIN, PREMIUM_MAX)
    condor = {"symbol": "X", "strategy": "iron condor", "expiration": "2026-10-16",
              "this_expiration_atm_iv": 0.25, "legs": [_leg()], "credit": 1.0, "width": 5.0,
              "max_loss": 400.0, "short_call_delta": 0.12, "short_put_delta": -0.12,
              "net_short": True, "tilt": None}
    _, b_condor_neutral = score_candidate(condor, MIN_VOLUME, MIN_OI, PREMIUM_MIN, PREMIUM_MAX)
    all_ok &= check("directional family with a matching tilt scores full alignment", b_directional_with_tilt["directional_alignment"] == 100.0)
    all_ok &= check("neutral family with no tilt scores full alignment", b_condor_neutral["directional_alignment"] == 100.0)

    print("ALL_OK" if all_ok else "VERIFICATION_FAILED")
    if not all_ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run it to verify it fails (`scoring.py` doesn't exist yet)**

```bash
cd pipeline
python verify_scoring.py
```

Expected: `ModuleNotFoundError: No module named 'scoring'`.

- [ ] **Step 3: Write `pipeline/scoring.py`**

```python
"""Composite scoring (Composite Scoring section, strategy-engine spec),
pure function, no I/O, same shape as greeks.py. Each of the 7 criteria
maps to a 0-100 sub-score; family/criterion cells the books don't
support default to a neutral 50 rather than a fabricated number, per the
spec's explicit policy.
"""
NEUTRAL = 50.0

_DIRECTIONAL_FAMILIES = ("vertical put credit spread", "vertical call credit spread", "long call", "long put")


def _iv_richness(candidate):
    percentiles = [leg["atm_iv_90d_percentile"] for leg in candidate["legs"] if leg["atm_iv_90d_percentile"] is not None]
    if not percentiles:
        return NEUTRAL
    percentile = sum(percentiles) / len(percentiles)
    # income-strategies.md SS6 / directional-strategies.md SS5: net-short
    # (premium-selling) structures favor a RICH (high-percentile) sold
    # leg; net-long (directional/short-calendar) structures favor a
    # CHEAP (low-percentile) bought leg.
    return percentile if candidate["net_short"] else 100 - percentile


def _skew_quality(candidate):
    """greeks-and-volatility.md SS4.3: richest setups combine high skew
    and high ATM IV. skew_*_pct_of_atm values run roughly 80-200+
    (percent of ATM IV); dividing by 2 and capping at 100 is this
    module's own normalization choice, not a book number -- the books
    give no explicit 0-100 scale for this."""
    strategy = candidate["strategy"]
    if strategy == "vertical put credit spread":
        vals = [leg["skew_put_pct_of_atm"] for leg in candidate["legs"] if leg["skew_put_pct_of_atm"] is not None]
    elif strategy == "vertical call credit spread":
        vals = [leg["skew_call_pct_of_atm"] for leg in candidate["legs"] if leg["skew_call_pct_of_atm"] is not None]
    elif strategy == "iron condor":
        vals = [
            leg[k] for leg in candidate["legs"]
            for k in ("skew_put_pct_of_atm", "skew_call_pct_of_atm")
            if leg[k] is not None
        ]
    else:
        return NEUTRAL  # calendars/diagonals: skew "roughly nets out" (spreads-and-combinations.md SS4); directional: no computable book rule
    return min(sum(vals) / len(vals), 200.0) / 2 if vals else NEUTRAL


def _risk_reward(candidate, calendar_premium_min, calendar_premium_max):
    strategy = candidate["strategy"]
    if strategy in ("vertical put credit spread", "vertical call credit spread", "iron condor"):
        if candidate.get("width", 0) <= 0:
            return NEUTRAL
        return min(100 * candidate["credit"] / candidate["width"], 100.0)
    if strategy in ("long calendar", "short calendar", "double diagonal"):
        premium = abs(candidate.get("premium", 0))
        span = calendar_premium_max - calendar_premium_min
        if span <= 0:
            return NEUTRAL
        return max(0.0, min(100.0, 100 * (premium - calendar_premium_min) / span))
    return NEUTRAL  # directional longs: capped-risk/uncapped-reward by construction, not a comparable ratio


def _pop_proxy(candidate):
    strategy = candidate["strategy"]
    if strategy in ("vertical put credit spread", "vertical call credit spread"):
        return 100 * (1 - abs(candidate["short_delta"]))
    if strategy == "iron condor":
        avg_delta = (abs(candidate["short_call_delta"]) + abs(candidate["short_put_delta"])) / 2
        return 100 * (1 - avg_delta)
    if strategy in ("long call", "long put"):
        return 100 * abs(candidate["legs"][0]["delta"])
    return NEUTRAL  # calendars/diagonals: term-structure trades, not probability-of-success trades


def _term_structure_signal(candidate, other_expirations_atm_iv):
    if not other_expirations_atm_iv or candidate.get("this_expiration_atm_iv") is None:
        return NEUTRAL
    diff = (candidate["this_expiration_atm_iv"] - other_expirations_atm_iv) / other_expirations_atm_iv
    score = 50 + diff * 100
    score = score if candidate["net_short"] else 100 - score
    return max(0.0, min(100.0, score))


def _liquidity_gradient(candidate, min_volume, min_open_interest):
    scores = []
    for leg in candidate["legs"]:
        vol_score = min(100.0, 100 * leg["volume"] / max(min_volume, 1))
        oi_score = min(100.0, 100 * leg["open_interest"] / max(min_open_interest, 1))
        penalty = (30 if leg["zero_bid"] else 0) + (20 if leg["wide_spread"] else 0)
        scores.append(max(0.0, (vol_score + oi_score) / 2 - penalty))
    return sum(scores) / len(scores) if scores else NEUTRAL


def _directional_alignment(candidate):
    if candidate["strategy"] in _DIRECTIONAL_FAMILIES:
        return 100.0 if candidate.get("tilt") else NEUTRAL
    return 100.0 if candidate.get("tilt") is None else NEUTRAL


def score_candidate(candidate, min_volume, min_open_interest, calendar_premium_min, calendar_premium_max, other_expirations_atm_iv=None):
    """Returns (composite_score, breakdown_dict) -- the breakdown is kept
    for ledger/debugging traceability per the spec."""
    breakdown = {
        "iv_richness": _iv_richness(candidate),
        "skew_quality": _skew_quality(candidate),
        "risk_reward": _risk_reward(candidate, calendar_premium_min, calendar_premium_max),
        "pop_proxy": _pop_proxy(candidate),
        "term_structure": _term_structure_signal(candidate, other_expirations_atm_iv),
        "liquidity": _liquidity_gradient(candidate, min_volume, min_open_interest),
        "directional_alignment": _directional_alignment(candidate),
    }
    composite = sum(breakdown.values()) / len(breakdown)
    return composite, breakdown
```

- [ ] **Step 4: Run the verification script and confirm it passes**

```bash
cd pipeline
python verify_scoring.py
```

Expected: every line prints `OK:`, final line `ALL_OK`.

- [ ] **Step 5: Commit**

```bash
git add pipeline/scoring.py pipeline/verify_scoring.py
git commit -m "Add 7-criteria composite scoring module with direction-check verification"
```

---

### Task 13: Position sizing + recommendation ledger writer + orchestrator

**Files:**
- Modify: `pipeline/config.py`
- Create: `pipeline/screen_trades.py`
- Test: manual run against real data

**Interfaces:**
- Consumes: every builder from Tasks 7-11, `score_candidate` from Task 12, `fetch_directional_bias` from Task 5, `refresh_atr_if_stale`/`get_atr_row` from Tasks 2-3, `get_term_structure_spread_history` from Task 2.
- Produces: `data/github_sync/options_ledger/options_recommendation_ledger.csv` (component E, extended with `suggested_contracts`) — consumed by Task 15's routine-prompt update.

- [ ] **Step 1: Add sizing/selection constants to `pipeline/config.py`**

```python
# risk-management-and-position-sizing.md SS6 (Chen/Sebastian ch.3): 2%
# max risk per trade. ACCOUNT_EQUITY is a fixed constant the user edits
# directly (same precedent as RISK_FREE_RATE) -- no account-balance data
# source exists in this project.
ACCOUNT_EQUITY = 100000
MAX_LOSS_PCT_PER_TRADE = 0.02

# Number of ranked candidates published to the recommendation ledger.
TOP_N_CANDIDATES = 20
```

- [ ] **Step 2: Write `pipeline/screen_trades.py`**

```python
"""
Strategy/screening orchestrator (sub-project 3, component E's first
writer). Mirrors merge_and_score.py's shape: refresh prerequisites, read
today's signals + the two Stocks ledgers, build every family's
candidates, score and rank them, attach a position-sizing suggestion,
write the recommendation ledger, commit + push.

Run from the repo root: `python pipeline/screen_trades.py`
"""
import csv
import subprocess
from datetime import date
from pathlib import Path

import pandas as pd

from atr import refresh_atr_if_stale
from config import (
    ACCOUNT_EQUITY, CALENDAR_LONG_PREMIUM_MAX, CALENDAR_LONG_PREMIUM_MIN,
    CALENDAR_MIN_FRONT_DAYS, CALENDAR_SHORT_DISCOUNT, CONDOR_DELTA_MAX, CONDOR_DELTA_MIN,
    CONDOR_MAX_DTE, CONDOR_MIN_DTE, EQUITY_MIN_DAILY_VOLUME, MAX_LOSS_PCT_PER_TRADE,
    MIN_OPEN_INTEREST, MIN_VOLUME, PROJECT_DIR, TOP_N_CANDIDATES, VERTICAL_DELTA_BAND,
    VERTICAL_MAX_DTE, VERTICAL_MIN_DTE, VERTICAL_SPREAD_WIDTHS,
)
from db import get_atr_row, get_term_structure_spread_history, init_db
from directional_bias import fetch_directional_bias
from scoring import score_candidate
from strategy_rules import (
    build_calendars, build_directional_longs, build_double_diagonals,
    build_iron_condors, build_vertical_credit_spreads,
)

SIGNALS_DIR = PROJECT_DIR / "data" / "github_sync" / "signals"
LEDGER_PATH = PROJECT_DIR / "data" / "github_sync" / "options_ledger" / "options_recommendation_ledger.csv"
LEDGER_COLS = ["symbol", "company_name", "trade_id", "strategy", "leg_role"]


def git_pull():
    result = subprocess.run(["git", "pull"], cwd=PROJECT_DIR, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"git pull failed: {result.stderr}")
    return result.stdout.strip()


def latest_signals_path():
    files = sorted(SIGNALS_DIR.glob("*.csv")) if SIGNALS_DIR.exists() else []
    return files[-1] if files else None


def _other_expirations_atm_iv(signals, symbol, this_expiration):
    sym_df = signals[signals["symbol"] == symbol]
    others = sym_df[sym_df["expiration"] != this_expiration]["atm_iv"].dropna()
    return float(others.mean()) if not others.empty else None


def build_all_candidates(signals, snapshot_date, bias):
    get_atr = lambda symbol: (get_atr_row(symbol) or {}).get("atr")
    get_term_history = lambda sym, f, b: get_term_structure_spread_history(sym, f, b, snapshot_date)

    candidates = []
    candidates += build_vertical_credit_spreads(
        signals, snapshot_date, bias, VERTICAL_MIN_DTE, VERTICAL_MAX_DTE,
        VERTICAL_DELTA_BAND, VERTICAL_SPREAD_WIDTHS, EQUITY_MIN_DAILY_VOLUME,
    )
    candidates += build_iron_condors(
        signals, snapshot_date, get_atr, CONDOR_MIN_DTE, CONDOR_MAX_DTE, CONDOR_DELTA_MIN, CONDOR_DELTA_MAX,
    )
    candidates += build_directional_longs(signals, bias, EQUITY_MIN_DAILY_VOLUME)
    candidates += build_calendars(
        signals, snapshot_date, get_term_history, CALENDAR_MIN_FRONT_DAYS,
        CALENDAR_LONG_PREMIUM_MIN, CALENDAR_LONG_PREMIUM_MAX, CALENDAR_SHORT_DISCOUNT,
    )
    candidates += build_double_diagonals(
        signals, snapshot_date, get_term_history, CALENDAR_MIN_FRONT_DAYS,
        CALENDAR_LONG_PREMIUM_MIN, CONDOR_DELTA_MIN, CONDOR_DELTA_MAX,
    )

    for c in candidates:
        c["other_expirations_atm_iv"] = _other_expirations_atm_iv(signals, c["symbol"], c["expiration"])
    return candidates


def score_and_rank(candidates):
    scored = []
    for c in candidates:
        score, breakdown = score_candidate(
            c, MIN_VOLUME, MIN_OPEN_INTEREST, CALENDAR_LONG_PREMIUM_MIN, CALENDAR_LONG_PREMIUM_MAX,
            other_expirations_atm_iv=c.get("other_expirations_atm_iv"),
        )
        scored.append((score, breakdown, c))
    scored.sort(key=lambda t: t[0], reverse=True)
    return scored[:TOP_N_CANDIDATES]


def suggested_contracts(candidate):
    per_contract_max_loss = candidate.get("max_loss", 0)
    if not per_contract_max_loss or per_contract_max_loss <= 0:
        return 0
    return int((ACCOUNT_EQUITY * MAX_LOSS_PCT_PER_TRADE) // per_contract_max_loss)


def write_ledger(ranked, snapshot_date, company_names):
    rows = []
    date_cols_seen = set()
    for rank, (score, breakdown, candidate) in enumerate(ranked, start=1):
        trade_id = f"{snapshot_date}-{candidate['symbol']}-{rank}"
        contracts = suggested_contracts(candidate)
        for leg in candidate["legs"]:
            rows.append({
                "symbol": candidate["symbol"],
                "company_name": company_names.get(candidate["symbol"], ""),
                "trade_id": trade_id,
                "strategy": candidate["strategy"],
                "leg_role": leg["leg_role"],
                f"rec:{snapshot_date}": f"{leg['contract_symbol']}/{leg['last_price']}",
                "suggested_contracts": contracts,
            })
            date_cols_seen.add(f"rec:{snapshot_date}")

    existing_rows, existing_cols = [], []
    if LEDGER_PATH.exists():
        with open(LEDGER_PATH, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            existing_cols = [c for c in reader.fieldnames if c not in LEDGER_COLS + ["suggested_contracts"]]
            existing_rows = list(reader)

    header = LEDGER_COLS + sorted(set(existing_cols) | date_cols_seen) + ["suggested_contracts"]
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LEDGER_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        for row in existing_rows:
            writer.writerow({c: row.get(c, "") for c in header})
        for row in rows:
            writer.writerow({c: row.get(c, "") for c in header})

    return len(rows)


def commit_and_push(paths, message):
    paths = [str(p) for p in paths]
    subprocess.run(["git", "add", *paths], cwd=PROJECT_DIR, check=True, timeout=60)
    diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=PROJECT_DIR, timeout=30)
    if diff.returncode == 0:
        return "no_changes"
    subprocess.run(["git", "commit", "-m", message], cwd=PROJECT_DIR, check=True, timeout=60)
    subprocess.run(["git", "push"], cwd=PROJECT_DIR, check=True, timeout=120)
    return "pushed"


def run_screen_trades():
    print("Pulling latest from GitHub...")
    print(git_pull())

    refresh_atr_if_stale()

    signals_path = latest_signals_path()
    if signals_path is None:
        print("No signals file found -- nothing to screen")
        return {"status": "no_data"}

    signals = pd.read_csv(signals_path)
    snapshot_date = signals_path.stem
    print(f"Screening {len(signals)} contracts from {snapshot_date}...")

    bias = fetch_directional_bias()
    candidates = build_all_candidates(signals, snapshot_date, bias)
    print(f"{len(candidates)} candidates built across all families")

    ranked = score_and_rank(candidates)
    print(f"Top {len(ranked)} candidates selected")

    company_names = {}  # company_name isn't in signals.csv; left blank per row if unavailable
    n_rows = write_ledger(ranked, snapshot_date, company_names)
    print(f"Wrote {n_rows} leg rows to {LEDGER_PATH}")

    status = commit_and_push([LEDGER_PATH], f"Options recommendations: {snapshot_date} ({len(ranked)} candidates)")
    print(f"Publish status: {status}")
    return {"status": status, "date": snapshot_date, "candidates": len(ranked)}


if __name__ == "__main__":
    init_db()
    print(run_screen_trades())
```

- [ ] **Step 3: Run it against real data**

```bash
cd "C:\Users\coope\Claude_Work\Projects\Options Trading"
python pipeline/screen_trades.py
```

Expected: pull output, ATR refresh line, `Screening N contracts from {date}...`, a candidate count, `Top M candidates selected`, `Wrote R leg rows to ...`, ending `{'status': 'pushed', ...}` (or `'no_changes'` on a re-run with nothing new).

- [ ] **Step 4: Spot-check the ledger**

```bash
python -c "
import pandas as pd
df = pd.read_csv('data/github_sync/options_ledger/options_recommendation_ledger.csv')
print(df.shape)
print(df.head(10))
print('trade_ids:', df['trade_id'].nunique())
"
```

Expected: leg counts per `trade_id` match the strategy (2 for a vertical spread or calendar, 4 for a condor or double diagonal, 1 for a directional long), `suggested_contracts` is a non-negative integer.

- [ ] **Step 5: Commit**

```bash
git add pipeline/config.py pipeline/screen_trades.py
git commit -m "Add screen_trades.py orchestrator: score, rank, size, and publish recommendations"
```

---

### Task 14: Portfolio-insurance reminder

**Files:**
- Modify: `pipeline/config.py`
- Modify: `pipeline/screen_trades.py`
- Test: manual run

**Interfaces:**
- Produces: `build_units_reminder(signals) -> dict` — appended to `run_screen_trades()`'s return value and printed for the routine to read.

- [ ] **Step 1: Add units constants to `pipeline/config.py`**

```python
# risk-management-and-position-sizing.md SS8 (Chen/Sebastian ch.3/8/11):
# "units" -- cheap, deep-OTM tail hedges. Priority-ordered fallback
# chains per hedge type (New Data Prerequisites item 4) -- component B's
# existing skip-and-continue handling is what makes the fallback work:
# if a symbol isn't in that day's signals, it's simply not considered.
UNIT_MAX_DELTA = 0.05
UNIT_MAX_PRICE = 3.0
TAIL_HEDGE_PRIORITY = {
    "equity downside": ["^SPX", "SPY"],
    "volatility spike": ["^VIX", "VXX", "UVXY"],
}
```

- [ ] **Step 2: Add `build_units_reminder` to `pipeline/screen_trades.py`**

```python
from config import TAIL_HEDGE_PRIORITY, UNIT_MAX_DELTA, UNIT_MAX_PRICE


def _cheapest_unit(signals, symbol):
    sym_df = signals[(signals["symbol"] == symbol) & (signals["type"] == "put") & (signals["delta"].abs() < UNIT_MAX_DELTA)]
    sym_df = sym_df[sym_df["last_price"] <= UNIT_MAX_PRICE]
    if sym_df.empty:
        return None
    row = sym_df.loc[sym_df["last_price"].idxmin()]
    return {"symbol": symbol, "contract_symbol": row["contract_symbol"], "last_price": row["last_price"], "delta": row["delta"]}


def build_units_reminder(signals):
    """risk-management-and-position-sizing.md SS8: any book of premium-
    selling trades should carry a standing tail hedge. Not a scored/
    ranked candidate -- a standing reminder line, citing whichever
    tail-hedge instrument actually has usable data that day, tried in
    priority order per hedge type. If none do, the reminder still fires
    with the rule restated, per the spec's fail-loud-not-silent policy
    applied to a soft reminder."""
    examples = {}
    for hedge_type, priority_list in TAIL_HEDGE_PRIORITY.items():
        for symbol in priority_list:
            unit = _cheapest_unit(signals, symbol)
            if unit is not None:
                examples[hedge_type] = unit
                break
    return {
        "rule": "Hold 5-10% of allocated trading capital in cheap, deep-OTM SPX puts or VIX calls, bought before it's needed.",
        "examples": examples,
    }
```

Add the call in `run_screen_trades()`, right before the `return` statement:

```python
    units_reminder = build_units_reminder(signals)
    print(f"Units reminder: {units_reminder}")

    status = commit_and_push([LEDGER_PATH], f"Options recommendations: {snapshot_date} ({len(ranked)} candidates)")
    print(f"Publish status: {status}")
    return {"status": status, "date": snapshot_date, "candidates": len(ranked), "units_reminder": units_reminder}
```

- [ ] **Step 3: Run it against real data**

```bash
cd "C:\Users\coope\Claude_Work\Projects\Options Trading"
python pipeline/screen_trades.py
```

Expected: a `Units reminder: {...}` line — `examples` may be `{}` if none of the tail-hedge tickers currently qualify (delta <5%, price under the ceiling), which is a valid, expected outcome, not a bug.

- [ ] **Step 4: Commit**

```bash
git add pipeline/config.py pipeline/screen_trades.py
git commit -m "Add portfolio-insurance (units) standing reminder"
```

---

### Task 15: Deploy — confirm the full screening pipeline is live

**Files:** none (deployment step — Tasks 1-14 already produced real data; this confirms the full loop)

- [ ] **Step 1: Confirm local and remote are in sync**

```bash
cd "C:\Users\coope\Claude_Work\Projects\Options Trading"
git push
git log --oneline -15
git ls-remote --heads origin master
```

Expected: local `master` and `origin/master` point to the same commit; the log shows every task commit from Tasks 1-14.

- [ ] **Step 2: Confirm the recommendation ledger is reachable the way the cloud routine will read it**

```bash
python -c "
import requests
r = requests.get('https://raw.githubusercontent.com/coop1st/options-trading-pipeline/master/data/github_sync/options_ledger/options_recommendation_ledger.csv', timeout=30)
print(r.status_code, len(r.text), 'bytes')
"
```

Expected: `200`, a non-trivial byte count.

---

### Task 16: Update the cloud routine to draft real recommendations

**Files:** none (this is a `RemoteTrigger action=update` call against the existing routine created in sub-project 2's Task 8, not a repo file)

- [ ] **Step 1: Look up the existing routine's trigger ID**

```
RemoteTrigger action=list
```

Find the routine named "Options signals check (nightly)" (created in sub-project 2, cron `30 1 * * 2-6`) and note its `trigger_id`.

- [ ] **Step 2: Update its prompt**

Call `RemoteTrigger` with `action: "update"`, `trigger_id: "<id from Step 1>"`, replacing the existing placeholder-email prompt (step 3 of the sub-project 2 prompt) with:

```
3. Otherwise, read the signals CSV (as before) AND
   data/github_sync/options_ledger/options_recommendation_ledger.csv.
   Find every row whose trade_id starts with today's date (or, if none
   do, the most recent date present). Group rows by trade_id: each group
   is one recommended trade (its strategy, legs, and suggested_contracts
   are all in those rows). Draft (do NOT send) a Gmail email to
   kcoopercscs@gmail.com, subject "Options recommendations -- {today's
   date}", listing each recommended trade: symbol, strategy, each leg's
   contract and price (from its most recent rec: column), and
   suggested_contracts. Below the trade list, include a short
   "Portfolio insurance" section: state the standing units rule (hold
   5-10% of allocated trading capital in cheap, deep-OTM SPX puts or VIX
   calls, bought before it's needed) and, if today's signals CSV has a
   deep-OTM (delta magnitude under 0.05) put on ^SPX, SPY, ^VIX, VXX, or
   UVXY priced under $3, cite it as a concrete qualifying example
   (symbol, contract, price) -- if none qualify, state that plainly
   instead of citing an example.
```

- [ ] **Step 3: Manually trigger one verification run**

```
RemoteTrigger action=run trigger_id=<id>
```

- [ ] **Step 4: Check the run log and the resulting Gmail draft**

```
RemoteTrigger action=list_runs trigger_id=<id>
RemoteTrigger action=get_run_log session_id=<id from list_runs>
```

Expected: `result: success`, no tool-permission errors. Then check Gmail for the new draft and confirm it lists real recommended trades (not the old diagnostic-placeholder wording) with plausible strategy names, leg prices, and contract counts, plus the portfolio-insurance section.

---

## Not done here

- **Post-entry position management and exit alerting** (Card Game Value, Third-Third-Third, "Good Exits" percentage-of-margin triggers) — the recommendation ledger records entry recommendations only, per the spec's Non-goals. A future sub-project once real recommendations have tracked outcomes.
- **Sub-project 4 (strategy comparison/backtesting)** — deferred until the ledger has real history.
- **Portfolio-level diversification/correlation limits and the 6%-monthly circuit breaker** — need open-position and realized-P&L tracking this pipeline doesn't have.
- **Score weighting beyond a simple unweighted average** — flagged in the spec as an open question to revisit once the ledger has enough history.

## Self-Review Notes

- **Spec coverage**: all four New Data Prerequisites (Tasks 1-2, 2, 2, 6), all five strategy families A-E (Tasks 7-11), the 7-criteria composite score (Task 12), both confirmed extensions — position sizing and the units reminder (Tasks 13-14), the recommendation ledger writer (Task 13), and the routine prompt update (Task 16) each have a task. Error handling (per-candidate skip-and-continue, soft directional-bias-fetch failure) is embedded directly in each builder/orchestrator rather than a separate task, matching how `merge_and_score.py` embeds its own error handling inline rather than as a distinct component.
- **Placeholder scan**: no TBD/TODO; every step has real, runnable code with real file paths and real book citations. The two `ACCOUNT_EQUITY`/wing-width-style numeric choices this spec flagged as "implementation choice, not book-verbatim" (e.g., `CONDOR_MIN_DTE=45`/`CONDOR_MAX_DTE=75`, `CALENDAR_MIN_FRONT_DAYS=10`) are carried into `config.py` with the same flagging comment the spec used, not silently presented as book numbers.
- **Type/interface consistency checked**: every builder returns the same candidate-dict shape (`symbol, strategy, expiration, this_expiration_atm_iv, legs, max_loss, net_short, tilt`, plus family-specific keys), which `scoring.py`'s `score_candidate()` and `screen_trades.py`'s `suggested_contracts()`/`write_ledger()` all consume consistently; `_leg()`'s dict keys (Task 7) match exactly what `scoring.py`'s `_liquidity_gradient()`/`_skew_quality()` read (Task 12); `db.py`'s new function names (Task 2) match every call site in `atr.py` (Task 3), `merge_and_score.py` (Task 4), and `screen_trades.py` (Task 13) verbatim.
- **One spec correction carried through consistently**: the true-range ledger is read from the local working copy after `git pull`, not via `raw.githubusercontent.com` as one line of the spec suggested — reflected in the Global Constraints, Task 1's design, and Task 3's `atr.py`.
