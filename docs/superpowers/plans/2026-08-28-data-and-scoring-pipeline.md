# Data & Scoring Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the options data pipeline end-to-end: a cloud-side GitHub Actions job that snapshots options chains 3x/trading day, a local nightly script that merges those snapshots, computes Greeks and IV/skew reads, and publishes a daily "signals" export, and a Claude Code cloud routine that reads the signals and emails a diagnostic summary (a placeholder for sub-project 3's real trade-selection logic, which doesn't exist yet).

**Architecture:** Mirrors the sibling Stocks project's cloud/local split. `cloud/fetch_options_snapshot.py` runs on `ubuntu-latest` via GitHub Actions (no local machine needed), reads the watchlist live from the Stocks project's public ledger, fetches options chains via yfinance, and commits a dated CSV. `pipeline/merge_and_score.py` runs locally whenever the PC is next on: pulls the day's snapshots, upserts them into a gitignored SQLite `options.db`, computes Black-Scholes Greeks (`pipeline/greeks.py`) and liquidity/skew reads, and publishes `data/github_sync/signals/{date}.csv`. A Claude Code scheduled routine reads that file nightly and drafts a Gmail summary, with an explicit staleness check as the safety net for "the local merge didn't run."

**Tech Stack:** Python 3.12 (cloud) / whatever the local machine has (local), pandas, scipy (Black-Scholes), yfinance, requests, truststore, SQLite, GitHub Actions, Claude Code cloud routines (`RemoteTrigger`/`/schedule`), Gmail MCP connector.

**Spec:** `docs/superpowers/specs/2026-08-26-data-and-scoring-pipeline-design.md`

## Global Constraints

- Norton antivirus's TLS inspection breaks strict SSL validation for Python HTTPS calls **on this local machine only** — reuse `Projects/Stocks/pipeline/config.py`'s exact `truststore` + `CURL_CA_BUNDLE` fix verbatim in the local pipeline's `config.py`. Confirmed **not needed** cloud-side (GitHub Actions runners have no such problem).
- Cloud fetch script paces requests ~1.5s between symbols; a rate-limited or failed individual symbol is skipped and logged, never a job failure. A failure fetching the watchlist itself (source A) **is** a job failure — there's nothing to snapshot without a symbol list.
- Options chains are fetched for all expirations within `MAX_DTE_DAYS = 75` of today.
- Liquidity filter thresholds: `MIN_VOLUME = 10`, `MIN_OPEN_INTEREST = 50` — a contract below either is excluded from the signals export.
- Risk-free rate is a fixed constant, `RISK_FREE_RATE = 0.05` (resolves the spec's open question — Bittman ch.4 shows a 2-point rate change moves a 90-day ATM call by only ~0.24, so a live Treasury-rate fetch isn't worth the complexity yet).
- Underlying price for Greeks is fetched during the cloud snapshot (component B), via `Ticker.history(period="1d")["Close"]` — the same Close-column access pattern already proven working in `Projects/Stocks/cloud/daytrade_shortlist.py` — and carried through as a column on every contract row, so the local merge script (component C) never needs its own Yahoo Finance call.
- No new local Python dependency beyond `pandas`, `scipy`, `truststore`, `requests` (all already used by the sibling Stocks project). `yfinance` is only needed cloud-side.
- This repo has no pytest suite — every script is verified by running it directly (against real data, or against a known-good property check) and inspecting output, matching the Stocks project's established convention.
- The repo is public (`coop1st/options-trading-pipeline`), so GitHub Actions minutes are free and unlimited on standard hosted runners.

---

## File Structure

- **Create** `pipeline/config.py` — paths, the Norton-TLS-inspection fix (copied from `Projects/Stocks/pipeline/config.py`), and the shared constants (`RISK_FREE_RATE`, `MIN_VOLUME`, `MIN_OPEN_INTEREST`, `SKEW_DELTA_TARGET`).
- **Create** `pipeline/greeks.py` — standard Black-Scholes pricing and Greeks (delta, gamma, theta, vega, rho), pure functions with no I/O.
- **Create** `pipeline/verify_greeks.py` — standalone verification script checking `greeks.py`'s output against the put-call-parity invariants documented in the `options-playbook` skill.
- **Create** `pipeline/db.py` — SQLite schema (`options_chains`, `merge_log`, `atm_iv_history`) and upsert/query helpers.
- **Create** `pipeline/merge_and_score.py` — component C: git pull, merge new snapshot CSVs into the DB, compute Greeks/liquidity/skew, publish `data/github_sync/signals/{date}.csv`, commit + push.
- **Create** `pipeline/requirements.txt` — `yfinance`, `requests`, `pandas`, `scipy`, `truststore`.
- **Create** `cloud/fetch_options_snapshot.py` — component B: self-contained (no imports from the rest of this repo, matching the Stocks project's `cloud/*.py` convention), reads the Stocks ledger, fetches options chains, writes a dated snapshot CSV.
- **Create** `.github/workflows/options-snapshot-fetch.yml` — triggers `fetch_options_snapshot.py` 3x/trading day plus `workflow_dispatch`, commits the result.
- **Deployment steps** (not files): seed GitHub with the first real snapshot and signals export by running the scripts manually once; create the cloud routine; verify it end-to-end with a manual trigger.
- **Explicitly not built in this plan**: the options recommendation ledger (component E) and the playbook rule-application step inside the cloud routine (component D step 3) — both depend on sub-project 3 (the strategy/screening engine), which doesn't exist yet. The cloud routine built here (Task 8) does the staleness check and a diagnostic summary email only. See "Not done here" at the end of this plan.

---

### Task 1: Local pipeline scaffolding

**Files:**
- Create: `pipeline/config.py`
- Create: `pipeline/requirements.txt`
- Test: manual run (import check)

**Interfaces:**
- Produces: `PROJECT_DIR`, `DB_PATH`, `RISK_FREE_RATE`, `MIN_VOLUME`, `MIN_OPEN_INTEREST`, `SKEW_DELTA_TARGET`, `MAX_DTE_DAYS` — consumed by every later local-pipeline task.

- [ ] **Step 1: Write `pipeline/requirements.txt`**

```
yfinance
requests
pandas
scipy
truststore
```

- [ ] **Step 2: Write `pipeline/config.py`**

```python
"""Shared configuration for the options data pipeline."""
import os
import sys
from pathlib import Path

# Norton antivirus on this machine does TLS inspection that breaks strict
# OpenSSL certificate validation for Python HTTPS calls. Routing through the
# OS-native validator instead avoids that mismatch without weakening
# certificate validation -- this is strictly "trust what Windows already
# trusts," not "skip verification." Safe to call unconditionally; a no-op
# if nothing intercepts traffic on a given machine. Verbatim copy of the
# fix already proven in Projects/Stocks/pipeline/config.py:1-62 -- see that
# file's comments for the full explanation of why each piece is needed.
import truststore

truststore.inject_into_ssl()

PIPELINE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = PIPELINE_DIR.parent
DB_PATH = PROJECT_DIR / "data" / "db" / "options.db"


def _ensure_curl_cffi_trusts_os_certs():
    """truststore above only patches Python's stdlib ssl module -- yfinance's
    cookie/crumb auth step goes through curl_cffi instead, which bundles its
    own separate TLS stack. curl_cffi (like real curl) honors the
    CURL_CA_BUNDLE env var, so fix it the same way: export Windows' trusted
    root/CA stores to a PEM file and point CURL_CA_BUNDLE at it. Regenerated
    on every import rather than cached. Respects an existing CURL_CA_BUNDLE
    if the environment already sets one. No-op on non-Windows or if nothing
    intercepts traffic here."""
    if sys.platform != "win32" or os.environ.get("CURL_CA_BUNDLE"):
        return
    import base64
    import ssl

    bundle_path = PROJECT_DIR / "data" / "cache" / "curl_cffi_ca_bundle.pem"
    try:
        bundle_path.parent.mkdir(parents=True, exist_ok=True)
        with open(bundle_path, "w") as f:
            for storename in ("ROOT", "CA"):
                for cert_der, _encoding, _trust in ssl.enum_certificates(storename):
                    b64 = base64.b64encode(cert_der).decode("ascii")
                    f.write("-----BEGIN CERTIFICATE-----\n")
                    for i in range(0, len(b64), 64):
                        f.write(b64[i:i + 64] + "\n")
                    f.write("-----END CERTIFICATE-----\n")
        os.environ["CURL_CA_BUNDLE"] = str(bundle_path)
    except OSError:
        pass  # best-effort -- curl_cffi calls just fail the same way they did before


_ensure_curl_cffi_trusts_os_certs()

# Black-Scholes risk-free rate: fixed constant per the pipeline design
# spec's resolved open question (Bittman ch.4 shows a 2-point rate change
# moves a 90-day ATM call by only ~0.24, so a fixed reasonable constant is
# fine rather than fetching a live Treasury rate).
RISK_FREE_RATE = 0.05

# Liquidity filter thresholds (component C step 5) -- a contract below
# either is excluded from the signals export.
MIN_VOLUME = 10
MIN_OPEN_INTEREST = 50

# Delta target for the skew reads (component C step 6) -- matches the
# options-playbook skill's own recommendation (greeks-and-volatility.md
# SS4.2) to track skew by delta rather than %-OTM.
SKEW_DELTA_TARGET = 0.25

# Cloud fetch (component B): only expirations within this many days out.
MAX_DTE_DAYS = 75
```

- [ ] **Step 3: Verify it imports cleanly**

```bash
cd pipeline
python -c "import config; print(config.DB_PATH, config.RISK_FREE_RATE)"
```

Expected: prints the resolved `data\db\options.db` path and `0.05`, no exceptions (confirms the SSL fix doesn't itself error out even on a machine where nothing intercepts traffic).

- [ ] **Step 4: Commit**

```bash
git add pipeline/config.py pipeline/requirements.txt
git commit -m "Add pipeline scaffolding: config, constants, requirements"
```

---

### Task 2: Black-Scholes Greeks module

**Files:**
- Create: `pipeline/greeks.py`
- Create: `pipeline/verify_greeks.py`
- Test: `pipeline/verify_greeks.py` (this repo's manual-verification convention, not pytest)

**Interfaces:**
- Consumes: nothing (pure math, no repo imports beyond `scipy.stats.norm`).
- Produces: `compute_greeks(underlying_price, strike, days_to_expiration, iv, option_type, risk_free_rate) -> dict` with keys `delta`, `gamma`, `theta` (per calendar day), `vega` (per 1 IV percentage point), `rho` (per 1 rate percentage point). Consumed by Task 6's `merge_and_score.py`.

- [ ] **Step 1: Write the failing verification script first**

```python
"""
Verifies pipeline/greeks.py against the put-call-parity invariants
.claude/skills/options-playbook/references/greeks-and-volatility.md SS1
states as always-true rules (not against hardcoded numeric reference
values -- more robust, and directly traceable to a cited source). This
repo has no pytest suite; every script here is verified by running it
directly and inspecting output, same convention as
Projects/Stocks/model/_rsi_pairwise_test.py.

Run: python pipeline/verify_greeks.py
"""
import sys

from greeks import compute_greeks

TOLERANCE = 0.005

# (underlying_price, strike, days_to_expiration, iv, risk_free_rate) --
# a spread of ITM/ATM/OTM cases so the invariants are checked across
# moneyness levels, not just at-the-money.
CASES = [
    (100, 100, 30, 0.25, 0.05),   # ATM, short-dated
    (100, 100, 365, 0.20, 0.05),  # ATM, 1yr
    (100, 80, 45, 0.30, 0.05),    # call ITM / put OTM
    (100, 120, 45, 0.30, 0.05),   # call OTM / put ITM
]


def check(label, condition):
    print(f"{'OK' if condition else 'FAIL'}: {label}")
    return condition


def main():
    all_ok = True
    for S, K, days, iv, r in CASES:
        call = compute_greeks(S, K, days, iv, "call", r)
        put = compute_greeks(S, K, days, iv, "put", r)
        label = f"S={S} K={K} days={days} iv={iv}"

        # SS1.1: "|call delta| + |put delta| ~= 1.00 always"
        all_ok &= check(f"[{label}] call_delta - put_delta ~= 1.0",
                         abs((call["delta"] - put["delta"]) - 1.0) < TOLERANCE)
        # SS1.2: "same-strike call/put gammas are (nearly) equal"
        all_ok &= check(f"[{label}] call_gamma ~= put_gamma",
                         abs(call["gamma"] - put["gamma"]) < TOLERANCE)
        # SS1.3: "same-strike call/put vegas are equal"
        all_ok &= check(f"[{label}] call_vega ~= put_vega",
                         abs(call["vega"] - put["vega"]) < TOLERANCE)
        # SS1.1: "call deltas are always positive... put deltas are always negative"
        all_ok &= check(f"[{label}] call_delta > 0", call["delta"] > 0)
        all_ok &= check(f"[{label}] put_delta < 0", put["delta"] < 0)
        # SS1.2: "gammas are always positive for both calls and puts"
        all_ok &= check(f"[{label}] gamma > 0", call["gamma"] > 0)
        # SS1.3: "vegas are always positive for both calls and puts"
        all_ok &= check(f"[{label}] vega > 0", call["vega"] > 0)
        # SS1.5: "rho is positive for calls, negative for puts"
        all_ok &= check(f"[{label}] call_rho > 0", call["rho"] > 0)
        all_ok &= check(f"[{label}] put_rho < 0", put["rho"] < 0)

    print("ALL_OK" if all_ok else "VERIFICATION_FAILED")
    if not all_ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run it to verify it fails (greeks.py doesn't exist yet)**

```bash
cd pipeline
python verify_greeks.py
```

Expected: `ModuleNotFoundError: No module named 'greeks'`.

- [ ] **Step 3: Write `pipeline/greeks.py`**

```python
"""Black-Scholes option pricing and Greeks (component C step 4).

Standard (non-dividend-paying) Black-Scholes, matching the four inputs the
pipeline design spec calls for: underlying price, strike, days to
expiration, and an implied-volatility assumption (Yahoo's own
impliedVolatility, per contract), plus a fixed risk-free rate
(config.RISK_FREE_RATE). Sign conventions and definitions match
.claude/skills/options-playbook/references/greeks-and-volatility.md SS1 --
that reference gives the conceptual grounding (why each Greek behaves as
it does) but not the closed-form equations themselves, so the formulas
below are the standard Black-Scholes/Merton closed forms.
"""
import math

from scipy.stats import norm


def _d1_d2(underlying_price, strike, years_to_expiration, iv, risk_free_rate):
    sqrt_t = math.sqrt(years_to_expiration)
    d1 = (
        math.log(underlying_price / strike)
        + (risk_free_rate + 0.5 * iv ** 2) * years_to_expiration
    ) / (iv * sqrt_t)
    d2 = d1 - iv * sqrt_t
    return d1, d2


def compute_greeks(underlying_price, strike, days_to_expiration, iv, option_type, risk_free_rate):
    """Returns a dict with delta, gamma, theta (per calendar day), vega
    (per 1 IV percentage point), and rho (per 1 rate percentage point).
    option_type: 'call' or 'put'. Returns all-None values if inputs are
    degenerate (zero/negative DTE or IV -- can't price a contract with no
    time value or no volatility assumption)."""
    if underlying_price is None or strike is None or days_to_expiration is None:
        return {"delta": None, "gamma": None, "theta": None, "vega": None, "rho": None}
    if days_to_expiration <= 0 or iv is None or iv <= 0:
        return {"delta": None, "gamma": None, "theta": None, "vega": None, "rho": None}

    years_to_expiration = days_to_expiration / 365.0
    d1, d2 = _d1_d2(underlying_price, strike, years_to_expiration, iv, risk_free_rate)
    sqrt_t = math.sqrt(years_to_expiration)
    discount = math.exp(-risk_free_rate * years_to_expiration)
    pdf_d1 = norm.pdf(d1)

    gamma = pdf_d1 / (underlying_price * iv * sqrt_t)
    vega = underlying_price * pdf_d1 * sqrt_t / 100.0  # per 1 IV percentage point

    if option_type == "call":
        delta = norm.cdf(d1)
        theta_annual = (
            -(underlying_price * pdf_d1 * iv) / (2 * sqrt_t)
            - risk_free_rate * strike * discount * norm.cdf(d2)
        )
        rho = strike * years_to_expiration * discount * norm.cdf(d2) / 100.0
    elif option_type == "put":
        delta = norm.cdf(d1) - 1
        theta_annual = (
            -(underlying_price * pdf_d1 * iv) / (2 * sqrt_t)
            + risk_free_rate * strike * discount * norm.cdf(-d2)
        )
        rho = -strike * years_to_expiration * discount * norm.cdf(-d2) / 100.0
    else:
        raise ValueError(f"option_type must be 'call' or 'put', got {option_type!r}")

    return {
        "delta": delta,
        "gamma": gamma,
        # per calendar day, matching Bittman's "one day is most common
        # among professionals" convention (greeks-and-volatility.md SS1.4)
        "theta": theta_annual / 365.0,
        "vega": vega,
        "rho": rho,
    }
```

- [ ] **Step 4: Run the verification script and confirm it passes**

```bash
cd pipeline
python verify_greeks.py
```

Expected: every line prints `OK:`, final line `ALL_OK`.

- [ ] **Step 5: Commit**

```bash
git add pipeline/greeks.py pipeline/verify_greeks.py
git commit -m "Add Black-Scholes Greeks module with put-call-parity verification"
```

---

### Task 3: SQLite schema and upsert helpers

**Files:**
- Create: `pipeline/db.py`
- Test: manual run (schema init + roundtrip check)

**Interfaces:**
- Consumes: `config.DB_PATH` (Task 1).
- Produces: `init_db()`, `is_merged(snapshot_file) -> bool`, `mark_merged(snapshot_file, n_rows)`, `upsert_options_chain(rows)`, `upsert_atm_iv_history(rows)`, `get_atm_iv_history(symbol, expiration, before_date, window_days=90) -> list[float]`, `get_latest_snapshot_rows(snapshot_date) -> (list[dict], str|None)` — all consumed by Task 6's `merge_and_score.py`.

- [ ] **Step 1: Write `pipeline/db.py`**

```python
"""SQLite schema and connection helper for the options data pipeline."""
import sqlite3
from contextlib import contextmanager

from config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS options_chains (
    symbol TEXT NOT NULL,
    snapshot_date TEXT NOT NULL,
    session TEXT NOT NULL,
    expiration TEXT NOT NULL,
    contract_symbol TEXT NOT NULL,
    type TEXT NOT NULL,
    strike REAL,
    last_price REAL,
    bid REAL,
    ask REAL,
    volume INTEGER,
    open_interest INTEGER,
    implied_volatility REAL,
    in_the_money INTEGER,
    last_trade_date TEXT,
    underlying_price REAL,
    PRIMARY KEY (contract_symbol, snapshot_date, session)
);
CREATE INDEX IF NOT EXISTS idx_options_symbol_date ON options_chains(symbol, snapshot_date);

CREATE TABLE IF NOT EXISTS merge_log (
    snapshot_file TEXT PRIMARY KEY,
    merged_at TEXT,
    rows INTEGER
);

CREATE TABLE IF NOT EXISTS atm_iv_history (
    symbol TEXT NOT NULL,
    expiration TEXT NOT NULL,
    snapshot_date TEXT NOT NULL,
    atm_iv REAL,
    PRIMARY KEY (symbol, expiration, snapshot_date)
);
"""


@contextmanager
def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_connection() as conn:
        conn.executescript(SCHEMA)


def is_merged(snapshot_file):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT 1 FROM merge_log WHERE snapshot_file = ?", (snapshot_file,)
        ).fetchone()
        return row is not None


def mark_merged(snapshot_file, n_rows):
    with get_connection() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO merge_log (snapshot_file, merged_at, rows) "
            "VALUES (?, datetime('now'), ?)",
            (snapshot_file, n_rows),
        )


def upsert_options_chain(rows):
    """rows: iterable of dicts with symbol, snapshot_date, session,
    expiration, contract_symbol, type, strike, last_price, bid, ask,
    volume, open_interest, implied_volatility, in_the_money,
    last_trade_date, underlying_price"""
    with get_connection() as conn:
        conn.executemany(
            """
            INSERT INTO options_chains (
                symbol, snapshot_date, session, expiration, contract_symbol,
                type, strike, last_price, bid, ask, volume, open_interest,
                implied_volatility, in_the_money, last_trade_date, underlying_price
            ) VALUES (
                :symbol, :snapshot_date, :session, :expiration, :contract_symbol,
                :type, :strike, :last_price, :bid, :ask, :volume, :open_interest,
                :implied_volatility, :in_the_money, :last_trade_date, :underlying_price
            )
            ON CONFLICT(contract_symbol, snapshot_date, session) DO UPDATE SET
                last_price=excluded.last_price, bid=excluded.bid, ask=excluded.ask,
                volume=excluded.volume, open_interest=excluded.open_interest,
                implied_volatility=excluded.implied_volatility,
                in_the_money=excluded.in_the_money,
                last_trade_date=excluded.last_trade_date,
                underlying_price=excluded.underlying_price
            """,
            rows,
        )


def upsert_atm_iv_history(rows):
    """rows: iterable of dicts with symbol, expiration, snapshot_date, atm_iv"""
    with get_connection() as conn:
        conn.executemany(
            """
            INSERT INTO atm_iv_history (symbol, expiration, snapshot_date, atm_iv)
            VALUES (:symbol, :expiration, :snapshot_date, :atm_iv)
            ON CONFLICT(symbol, expiration, snapshot_date) DO UPDATE SET
                atm_iv=excluded.atm_iv
            """,
            rows,
        )


def get_atm_iv_history(symbol, expiration, before_date, window_days=90):
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT atm_iv FROM atm_iv_history
            WHERE symbol = ? AND expiration = ? AND snapshot_date < ?
            AND snapshot_date >= date(?, ?)
            """,
            (symbol, expiration, before_date, before_date, f"-{window_days} days"),
        ).fetchall()
        return [r[0] for r in rows if r[0] is not None]


def get_latest_snapshot_rows(snapshot_date):
    """Returns (rows, session) for the most complete session captured that
    day, preferring close > mid > open -- if a symbol was only captured
    during an earlier session (e.g. skipped during 'close' due to a
    rate-limit), it's simply absent from that day's signals export rather
    than merged across sessions. Returns ([], None) if nothing was merged
    for that date yet."""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        for session in ("close", "mid", "open"):
            rows = conn.execute(
                "SELECT * FROM options_chains WHERE snapshot_date = ? AND session = ?",
                (snapshot_date, session),
            ).fetchall()
            if rows:
                return [dict(r) for r in rows], session
        return [], None
```

- [ ] **Step 2: Run a roundtrip check against a scratch DB**

```bash
cd pipeline
python -c "
import db
db.init_db()
db.upsert_options_chain([{
    'symbol': 'AAPL', 'snapshot_date': '2026-08-28', 'session': 'close',
    'expiration': '2026-09-25', 'contract_symbol': 'AAPL260925C00200000',
    'type': 'call', 'strike': 200.0, 'last_price': 5.2, 'bid': 5.1, 'ask': 5.3,
    'volume': 120, 'open_interest': 500, 'implied_volatility': 0.28,
    'in_the_money': 0, 'last_trade_date': '2026-08-28 20:00:00', 'underlying_price': 202.5,
}])
db.mark_merged('2026-08-28_close.csv', 1)
rows, session = db.get_latest_snapshot_rows('2026-08-28')
print('merged:', db.is_merged('2026-08-28_close.csv'), 'session:', session, 'rows:', len(rows))
"
```

Expected: `merged: True session: close rows: 1`. This writes to the real `data/db/options.db` path — fine, since Task 6's real run will upsert into the same table with `ON CONFLICT` semantics, so this scratch row is harmlessly overwritten by real data later. Delete `data/db/options.db` afterward if a clean slate is preferred before Task 7's real deploy.

- [ ] **Step 3: Commit**

```bash
git add pipeline/db.py
git commit -m "Add SQLite schema and upsert helpers for the options pipeline"
```

---

### Task 4: Cloud options-snapshot fetch script (component B)

**Files:**
- Create: `cloud/fetch_options_snapshot.py`
- Test: manual run against real Yahoo Finance / GitHub data (local machine, before deploying to Actions)

**Interfaces:**
- Consumes (live HTTP, not imports): the Stocks project's public `stock_price_ledger.csv`.
- Produces: `data/github_sync/options_snapshots/{date}_{session}.csv`, columns `symbol, expiration, contract_symbol, strike, type, last_price, bid, ask, volume, open_interest, implied_volatility, in_the_money, last_trade_date, underlying_price`. Consumed by Task 6's `merge_and_score.py` (via the DB, after Task 5's workflow commits it) and by Task 7's deploy.

- [ ] **Step 1: Write the script**

```python
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
```

- [ ] **Step 2: Run it locally against real data**

```bash
cd "C:\Users\coope\Claude_Work\Projects\Options Trading"
python cloud/fetch_options_snapshot.py close
```

Expected: batch-progress lines every 20 symbols, then a `SNAPSHOT_READY session=close rows=N symbols_ok=M/T skipped=[...]` line, and `data/github_sync/options_snapshots/{today}_close.csv` populated. `skipped` should be a small fraction of the watchlist (illiquid/delisted symbols with no options chain are expected; a large fraction skipped signals a real problem, e.g. the Norton TLS fix not applying here since this script deliberately skips `pipeline/config.py` — if most symbols fail, run `python -c "import truststore; truststore.inject_into_ssl()"` before this script as a one-off local workaround, or set `YF_DISABLE_CURL_CFFI=1` first, since this local test doesn't need the cloud-only assumption that no SSL fix is required).

- [ ] **Step 3: Commit**

```bash
git add cloud/fetch_options_snapshot.py
git commit -m "Add cloud-side options-chain snapshot fetcher"
```

---

### Task 5: GitHub Actions workflow for the cloud fetch

**Files:**
- Create: `.github/workflows/options-snapshot-fetch.yml`

**Interfaces:**
- Consumes: `cloud/fetch_options_snapshot.py` (Task 4), `pipeline/requirements.txt` (Task 1).

- [ ] **Step 1: Write the workflow**

```yaml
name: Options snapshot fetch

# Runs entirely in the cloud -- no local machine needed. Fetches options
# chains for the current watchlist 3x per trading day (open/mid/close) and
# commits the result as a small dated CSV. The local merge script
# (pipeline/merge_and_score.py) picks this up later, whenever that machine
# is next on.

on:
  schedule:
    # UTC times below assume EDT (UTC-4); expect ~1hr drift once EST
    # (UTC-5) begins in November -- a few minutes either side of
    # open/mid/close doesn't materially change the snapshot's value, same
    # reasoning the Stocks project's weekly-price-fetch.yml already uses.
    - cron: "35 13 * * 1-5"  # ~9:35am ET market open
    - cron: "30 16 * * 1-5"  # ~12:30pm ET midday
    - cron: "55 19 * * 1-5"  # ~3:55pm ET market close
  workflow_dispatch:
    inputs:
      session:
        description: "Session to fetch (open, mid, close)"
        required: true
        default: "close"

permissions:
  contents: write

jobs:
  fetch:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: pip install -r pipeline/requirements.txt

      - name: Determine session
        id: session
        run: |
          if [ "${{ github.event_name }}" = "workflow_dispatch" ]; then
            echo "session=${{ github.event.inputs.session }}" >> "$GITHUB_OUTPUT"
          elif [ "${{ github.event.schedule }}" = "35 13 * * 1-5" ]; then
            echo "session=open" >> "$GITHUB_OUTPUT"
          elif [ "${{ github.event.schedule }}" = "30 16 * * 1-5" ]; then
            echo "session=mid" >> "$GITHUB_OUTPUT"
          else
            echo "session=close" >> "$GITHUB_OUTPUT"
          fi

      - name: Fetch options snapshot
        run: python cloud/fetch_options_snapshot.py ${{ steps.session.outputs.session }}

      - name: Commit and push
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add data/github_sync/options_snapshots/
          if git diff --cached --quiet; then
            echo "No changes to commit"
          else
            git commit -m "Options snapshot: ${{ steps.session.outputs.session }} $(date -u +%Y-%m-%d)"
            git push
          fi
```

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/options-snapshot-fetch.yml
git commit -m "Add GitHub Actions workflow for 3x/day options snapshot fetch"
```

- [ ] **Step 3: Push and verify one manual run**

```bash
git push
```

Then trigger it manually: `gh workflow run options-snapshot-fetch.yml -f session=close` (or via the Actions tab). Confirm the run succeeds and a new file appears under `data/github_sync/options_snapshots/` in the repo — this is the first real cloud-fetched snapshot and doubles as Task 7's cloud-side seed data.

```bash
gh run list --workflow=options-snapshot-fetch.yml --limit 1
```

Expected: `completed success`.

---

### Task 6: Local merge + compute script (component C)

**Files:**
- Create: `pipeline/merge_and_score.py`
- Test: manual run against real merged data (after Task 5's first snapshot exists)

**Interfaces:**
- Consumes: `config.PROJECT_DIR`, `config.RISK_FREE_RATE`, `config.MIN_VOLUME`, `config.MIN_OPEN_INTEREST`, `config.SKEW_DELTA_TARGET` (Task 1); `db.init_db`, `db.is_merged`, `db.mark_merged`, `db.upsert_options_chain`, `db.upsert_atm_iv_history`, `db.get_atm_iv_history`, `db.get_latest_snapshot_rows` (Task 3); `greeks.compute_greeks` (Task 2).
- Produces: `data/github_sync/signals/{date}.csv`, columns `symbol, expiration, contract_symbol, type, strike, last_price, bid, ask, volume, open_interest, implied_volatility, underlying_price, delta, gamma, theta, vega, rho, atm_iv, atm_iv_90d_percentile, skew_put_pct_of_atm, skew_call_pct_of_atm`. Consumed by Task 8's cloud routine.

- [ ] **Step 1: Write the script**

```python
"""
Local nightly merge + compute (component C). Runs on the user's own PC
whenever it's next on overnight -- not scheduled via GitHub Actions or a
cloud routine.

1. git pull to get the day's raw snapshots.
2. Upsert every not-yet-merged data/github_sync/options_snapshots/*.csv
   into data/db/options.db (tracked via merge_log so re-running is a
   harmless no-op, mirroring Projects/Stocks/pipeline/pull_github_updates.py's
   convention).
3. Compute Greeks, liquidity flags, and IV/skew reads for today's most
   complete snapshot session.
4. Write data/github_sync/signals/{date}.csv and commit + push.

Run from the repo root: `python pipeline/merge_and_score.py`
"""
import subprocess
from datetime import date

import pandas as pd

from config import MIN_OPEN_INTEREST, MIN_VOLUME, PROJECT_DIR, RISK_FREE_RATE, SKEW_DELTA_TARGET
from db import (
    get_atm_iv_history,
    get_latest_snapshot_rows,
    init_db,
    is_merged,
    mark_merged,
    upsert_atm_iv_history,
    upsert_options_chain,
)
from greeks import compute_greeks

SNAPSHOTS_DIR = PROJECT_DIR / "data" / "github_sync" / "options_snapshots"
SIGNALS_DIR = PROJECT_DIR / "data" / "github_sync" / "signals"


def git_pull():
    result = subprocess.run(
        ["git", "pull"], cwd=PROJECT_DIR, capture_output=True, text=True, timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git pull failed: {result.stderr}")
    return result.stdout.strip()


def merge_new_snapshots():
    if not SNAPSHOTS_DIR.exists():
        return {"files": 0, "rows": 0}

    merged_files, total_rows = 0, 0
    for f in sorted(SNAPSHOTS_DIR.glob("*.csv")):
        if is_merged(f.name):
            continue
        df = pd.read_csv(f)
        if df.empty:
            mark_merged(f.name, 0)
            continue
        stem_date, session = f.stem.rsplit("_", 1)
        df["snapshot_date"] = stem_date
        df["session"] = session
        upsert_options_chain(df.to_dict("records"))
        mark_merged(f.name, len(df))
        merged_files += 1
        total_rows += len(df)
    return {"files": merged_files, "rows": total_rows}


def _atm_iv(group, underlying_price):
    """Average of the call and put implied_volatility at the strike
    closest to underlying_price, for one (symbol, expiration) group."""
    nearest = group.iloc[(group["strike"] - underlying_price).abs().argsort()[:1]]
    if nearest.empty:
        return None
    at_strike = group[group["strike"] == nearest["strike"].iloc[0]]
    ivs = at_strike["implied_volatility"].dropna()
    return float(ivs.mean()) if not ivs.empty else None


def compute_signals(rows, snapshot_date):
    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame()

    # Greeks (component C step 4)
    greek_cols = {"delta": [], "gamma": [], "theta": [], "vega": [], "rho": []}
    for _, r in df.iterrows():
        days_to_exp = (date.fromisoformat(r["expiration"]) - date.fromisoformat(snapshot_date)).days
        g = compute_greeks(
            r["underlying_price"], r["strike"], days_to_exp,
            r["implied_volatility"], r["type"], RISK_FREE_RATE,
        )
        for k in greek_cols:
            greek_cols[k].append(g[k])
    for k, v in greek_cols.items():
        df[k] = v

    # Liquidity flags (component C step 5)
    df["low_liquidity"] = (df["volume"] < MIN_VOLUME) | (df["open_interest"] < MIN_OPEN_INTEREST)

    # IV / skew reads (component C step 6)
    df["atm_iv"] = None
    df["atm_iv_90d_percentile"] = None
    df["skew_put_pct_of_atm"] = None
    df["skew_call_pct_of_atm"] = None
    history_rows = []

    for (symbol, expiration), group in df.groupby(["symbol", "expiration"]):
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

        for opt_type, col in (("put", "skew_put_pct_of_atm"), ("call", "skew_call_pct_of_atm")):
            side = group[(group["type"] == opt_type) & group["delta"].notna()]
            if side.empty or not atm_iv:
                continue
            closest = side.iloc[(side["delta"].abs() - SKEW_DELTA_TARGET).abs().argsort()[:1]]
            otm_iv = closest["implied_volatility"].iloc[0]
            df.loc[closest.index, col] = round(100 * otm_iv / atm_iv, 1)

    if history_rows:
        upsert_atm_iv_history(history_rows)

    signals = df[~df["low_liquidity"]].copy()
    out_cols = [
        "symbol", "expiration", "contract_symbol", "type", "strike",
        "last_price", "bid", "ask", "volume", "open_interest",
        "implied_volatility", "underlying_price",
        "delta", "gamma", "theta", "vega", "rho",
        "atm_iv", "atm_iv_90d_percentile",
        "skew_put_pct_of_atm", "skew_call_pct_of_atm",
    ]
    return signals[out_cols].sort_values(["symbol", "expiration", "type", "strike"])


def commit_and_push(paths, message):
    paths = [str(p) for p in paths]
    subprocess.run(["git", "add", *paths], cwd=PROJECT_DIR, check=True, timeout=60)
    diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=PROJECT_DIR, timeout=30)
    if diff.returncode == 0:
        return "no_changes"
    subprocess.run(["git", "commit", "-m", message], cwd=PROJECT_DIR, check=True, timeout=60)
    subprocess.run(["git", "push"], cwd=PROJECT_DIR, check=True, timeout=120)
    return "pushed"


def run_merge_and_score():
    print("Pulling latest from GitHub...")
    print(git_pull())

    print("Merging new snapshot files...")
    merge_result = merge_new_snapshots()
    print(f"Merged {merge_result['rows']} rows from {merge_result['files']} new file(s)")

    today_str = date.today().isoformat()
    rows, session = get_latest_snapshot_rows(today_str)
    if not rows:
        print(f"No snapshot rows for {today_str} yet -- nothing to score")
        return {"status": "no_data", "date": today_str}

    print(f"Scoring {len(rows)} contracts from today's '{session}' session...")
    signals = compute_signals(rows, today_str)

    SIGNALS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = SIGNALS_DIR / f"{today_str}.csv"
    signals.to_csv(out_path, index=False)
    print(f"Wrote {len(signals)} signal rows to {out_path}")

    status = commit_and_push([out_path], f"Options signals: {today_str} ({len(signals)} contracts)")
    print(f"Publish status: {status}")
    return {"status": status, "date": today_str, "rows": len(signals)}


if __name__ == "__main__":
    init_db()
    print(run_merge_and_score())
```

- [ ] **Step 2: Run it against the real merged data (after Task 5 has produced a real snapshot)**

```bash
cd "C:\Users\coope\Claude_Work\Projects\Options Trading"
python pipeline/merge_and_score.py
```

Expected: `git pull` output, `Merged N rows from 1 new file(s)`, `Scoring N contracts from today's 'close' session...`, `Wrote M signal rows to ...`, ending `{'status': 'pushed', 'date': '...', 'rows': M}` (or `'no_changes'` if run twice in a row with nothing new).

- [ ] **Step 3: Spot-check the signals export**

```bash
python -c "
import pandas as pd
from datetime import date
df = pd.read_csv(f'data/github_sync/signals/{date.today().isoformat()}.csv')
print(df.shape)
print(df[['symbol','type','strike','delta','gamma','theta','vega','atm_iv']].head(10))
print('null deltas:', df['delta'].isna().sum(), 'of', len(df))
"
```

Expected: a populated DataFrame; `delta` in `[-1, 1]`, `gamma`/`vega` non-negative for the sampled rows; a small number of null Greeks is acceptable (degenerate cases, e.g. zero IV from Yahoo) but not a large fraction.

- [ ] **Step 4: Commit**

```bash
git add pipeline/merge_and_score.py
git commit -m "Add local nightly merge + Greeks/liquidity/skew scoring script"
```

---

### Task 7: Deploy — confirm the cloud/local round trip is live

**Files:** none (deployment step, not a code change — Task 5's manual workflow run and Task 6's manual local run already produced real data; this task just confirms the full loop and pushes anything outstanding)

- [ ] **Step 1: Confirm local and remote are in sync**

```bash
git push
git log --oneline -8
git ls-remote --heads origin main
```

Expected: local `main` and `origin/main` point to the same commit; the log shows the snapshot-fetch workflow's commit, `merge_and_score.py`'s signals commit, and every task commit from Tasks 1-6.

- [ ] **Step 2: Confirm the signals file the cloud routine (Task 8) will read is actually on GitHub**

```bash
python -c "
import requests
r = requests.get('https://raw.githubusercontent.com/coop1st/options-trading-pipeline/main/data/github_sync/signals/$(python -c \"from datetime import date; print(date.today().isoformat())\").csv', timeout=30)
print(r.status_code, len(r.text), 'bytes')
"
```

Expected: `200`, a non-trivial byte count. If `404`, `git push` hasn't landed on GitHub yet, or Task 6 wrote a different filename than expected — check `data/github_sync/signals/` locally against what's on `github.com/coop1st/options-trading-pipeline`.

---

### Task 8: Create and verify the cloud routine (component D — staleness check + diagnostic placeholder)

**Files:** none (this is a `RemoteTrigger` API call, not a repo file — the routine's prompt is defined here in the plan and passed directly to the API)

**Scope note:** the spec's component D step 3 (apply the `options-playbook` skill's entry/risk rules to generate real trade candidates) is sub-project 3's job, not built yet. This task builds everything else D needs: the staleness check (the safety net for "the local merge script didn't run last night" — the exact problem that prompted this whole plan) and a diagnostic summary email in place of real trade recommendations.

- [ ] **Step 1: Look up an existing environment_id to reuse (or confirm none is required)**

```
RemoteTrigger action=list
```

Check whether any existing routine's `job_config.ccr.environment_id` is reusable for this repo, or whether omitting `environment_id` (letting the platform use the account default) is acceptable. Don't guess a value from a different project's routine — confirm it here first.

- [ ] **Step 2: Generate a fresh UUID for the routine's initial event**

```bash
python -c "import uuid; print(str(uuid.uuid4()))"
```

- [ ] **Step 3: Create the recurring routine**

Call `RemoteTrigger` with `action: "create"`:

```json
{
  "name": "Options signals check (nightly)",
  "cron_expression": "30 1 * * 2-6",
  "enabled": true,
  "job_config": {
    "ccr": {
      "session_context": {
        "model": "claude-sonnet-5",
        "sources": [{"git_repository": {"url": "https://github.com/coop1st/options-trading-pipeline"}}],
        "allowed_tools": ["Bash", "Read", "Glob", "mcp__Gmail__create_draft"]
      },
      "events": [{"data": {
        "uuid": "<fresh UUID from Step 2>",
        "session_id": "",
        "type": "user",
        "parent_tool_use_id": null,
        "message": {"role": "user", "content": "<PROMPT -- see below>"}
      }}]
    }
  }
}
```

`cron_expression` explanation: `30 1 * * 2-6` fires at 01:30 UTC on UTC-Tue through UTC-Sat, which is ~2:30am Irish time in IST (matching `HANDOVER.md`'s stated target) and lands after every one of Monday-Friday's closes (Tuesday's fire reports on Monday's close, ..., Saturday's fire reports on Friday's close), mirroring how the Stocks project's day-trade routine schedule was derived. Add `environment_id` under `ccr` if Step 1 found one worth reusing.

The prompt (fill in as the `message.content` string above):

```
You are running the nightly options-signals check for the
coop1st/options-trading-pipeline repo, already cloned into your working
directory.

1. Find the most recent file matching data/github_sync/signals/*.csv
   (filenames are ISO dates -- the alphabetically last one is the latest).
   If no such file exists at all, treat that the same as "missing" below.

2. Staleness check: parse the found file's date from its filename and
   compare it to today's date. If the file is missing, or its date is more
   than 1 calendar day older than the most recent weekday, draft a short
   Gmail email to kcoopercscs@gmail.com using the create_draft tool,
   subject "Options signals -- automation alert", body stating the latest
   date found (or "none found") and that the local nightly merge script
   appears not to have run. Stop here -- do not proceed to step 3.

3. Otherwise, read the signals CSV (columns: symbol, expiration,
   contract_symbol, type, strike, last_price, bid, ask, volume,
   open_interest, implied_volatility, underlying_price, delta, gamma,
   theta, vega, rho, atm_iv, atm_iv_90d_percentile, skew_put_pct_of_atm,
   skew_call_pct_of_atm). The strategy/screening engine that turns these
   signals into concrete trade recommendations is a separate, not-yet-built
   sub-project -- so for now, draft (do NOT send) a short diagnostic Gmail
   email to kcoopercscs@gmail.com, subject "Options signals -- {today's
   date}", stating explicitly that this is a placeholder summary and not
   trade recommendations, then reporting: total contract count, count of
   distinct underlying symbols represented, and two short lists of up to 5
   symbols each (by their highest-atm_iv_90d_percentile contract) -- one
   list for the highest atm_iv_90d_percentile values (richest relative to
   their own recent history) and one for the lowest (cheapest).
```

- [ ] **Step 4: Relay the created routine's URL and confirmed run time**

The `RemoteTrigger create` response includes a summary line with the server-parsed schedule and the routine's `https://claude.ai/code/routines/{id}` URL — relay both.

- [ ] **Step 5: Manually trigger one verification run**

```
RemoteTrigger action=run trigger_id=<id from Step 3's response>
```

- [ ] **Step 6: Check the run log and the resulting Gmail draft**

```
RemoteTrigger action=list_runs trigger_id=<id>
RemoteTrigger action=get_run_log session_id=<id from list_runs>
```

Expected: `result: success`, no tool-permission errors. Then check Gmail for the new draft and confirm it reads sensibly (states the placeholder caveat, has plausible-looking counts and symbol lists). If the log shows a Gmail tool-permission/not-found error, fix the `allowed_tools` entry via `RemoteTrigger action=update` with the corrected tool name and repeat Steps 5-6.

---

## Not done here

- **Sub-project 3 (Strategy/Screening Engine)**: applying the `options-playbook` skill's actual entry/risk rules to the signals export to produce real trade candidates. Task 8's routine drafts a diagnostic placeholder email instead — swapping in real trade selection is a prompt/logic change to that routine (via `RemoteTrigger action=update`), not a re-architecture.
- **Component E (options recommendation ledger)**: `data/github_sync/options_ledger/options_recommendation_ledger.csv`, per the spec's wide-format `rec:`/`tgt:` column-pair schema. Nothing to append to it until sub-project 3 produces real recommendations, so it isn't created here — sub-project 3's plan should create it, following the exact column schema already specified in this plan's source spec.
- **Tightening the GitHub Actions cron times and the routine's cron** once real data confirms how soon after each session Yahoo's chain data is reliably complete — same category of deferred empirical tuning the Stocks project's day-trade automation plan used a conservative default for.

## Self-Review Notes

- **Spec coverage**: component A (watchlist) — read live inside Task 4's script, no separate file, per spec. Component B — Tasks 4-5. Component C — Tasks 2, 3, 6. Component D — Task 8, scoped to the staleness check + placeholder (component D step 3 explicitly deferred by the spec itself to sub-project 3). Component E — explicitly deferred, see "Not done here."
- **Open questions resolved**: risk-free rate fixed at `0.05` (Task 1); underlying price fetched during the cloud snapshot via the already-proven `.history()["Close"]` pattern rather than a separate local call (Task 4), both matching the spec's stated resolution criteria.
- **Type/interface consistency checked**: `compute_greeks()`'s five-key return dict (Task 2) matches exactly how `merge_and_score.py` unpacks it (Task 6); `db.py`'s function names and parameters (Task 3) match every call site in `merge_and_score.py` (Task 6) verbatim.
