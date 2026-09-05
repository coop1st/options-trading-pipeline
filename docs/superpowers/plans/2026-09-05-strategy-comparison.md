# Strategy Comparison & Simulated Outcome Tracking Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stop discarding the 7-criteria score breakdown, simulate each recommendation's outcome by replaying its strategy family's book-cited exit rule against later `signals.csv` snapshots, and publish a weekly digest comparing performance by strategy family and by scoring criterion.

**Architecture:** Extends the recommendation ledger with 8 score columns (persisted at write time) and 3 outcome columns (filled in later). A new `pipeline/track_outcomes.py`, running daily via GitHub Actions (no external fetch — everything it needs is already in the repo), walks every non-terminal `trade_id`'s full `signals.csv` history and applies its family's exit rule, re-scanning from entry every run so a data gap never becomes a permanent loss. A new `pipeline/compare_strategies.py`, running weekly via GitHub Actions, aggregates scoreable terminal trades by family and by criterion into a published report. A new weekly Claude Code cloud routine reads that report and drafts the digest email.

**Tech Stack:** Python 3.12, pandas, `statistics` (stdlib) — no new dependencies. Both new scripts run entirely in GitHub Actions (no yfinance, no Norton-fix needed — they only read/write repo-local CSV files and do git operations).

**Spec:** `docs/superpowers/specs/2026-09-05-strategy-comparison-design.md`

## Global Constraints

- **Report format is CSV**, resolving the spec's open question — matches every other ledger/report in this project.
- **`EXPIRED_ITM`/`EXPIRED_OTM` (from the spec) are implemented as `EXPIRED_PROFIT`/`EXPIRED_LOSS`** — a naming refinement made while writing this plan: "moneyness" is a single-option concept, and these terminal states cover multi-leg structures too, so naming them by realized sign (profit vs. loss) is accurate for every family, not just directional longs. The underlying math and trigger conditions are unchanged from the spec.
- Every leg's expiration, strike, and option type are recovered by parsing its OCC `contractSymbol` (already stored in the ledger's `rec:` column) — no new ledger column needed for this.
- `track_outcomes.py`'s core algorithm **re-scans full history from entry on every run**, never resuming from a checkpoint — a contract absent from one day's `signals.csv` is skipped, not treated as a signal, per the spec's corrected design.
- A pre-existing ledger row with no score-breakdown columns (recommended before this ships) gets blank score columns forever — no retroactive backfill — and is excluded from the by-criterion aggregation but still counted in the by-family aggregation.
- Weekly schedule: `track-outcomes.yml` runs daily at 19:00 UTC; `compare-strategies.yml` runs weekly, Sunday 20:00 UTC (after that day's `track-outcomes` run); the new routine fires Sunday 20:30 UTC (after `compare-strategies` has published).
- No pytest — every script verified by running it directly, matching this project's established convention.

---

## File Structure

- **Modify** `pipeline/config.py` — 9 new exit-rule/aggregation constants.
- **Modify** `pipeline/screen_trades.py` — `write_ledger()` extended to persist the 8-column score breakdown and initialize 3 blank outcome columns.
- **Create** `pipeline/track_outcomes.py` — OCC parsing, credit/debit helpers, one evaluator function per strategy family, the re-scan-from-entry orchestration algorithm, ledger read/write, commit + push.
- **Create** `pipeline/verify_track_outcomes.py` — synthetic fixtures covering every family's rule, the gap-skip/resume behavior, and the `UNRESOLVED_AT_EXPIRATION` fallback.
- **Create** `pipeline/compare_strategies.py` — by-family and by-criterion aggregation, report CSV writer, commit + push.
- **Create** `pipeline/verify_compare_strategies.py` — synthetic terminal-trade fixtures covering the aggregation math.
- **Create** `.github/workflows/track-outcomes.yml` — daily.
- **Create** `.github/workflows/compare-strategies.yml` — weekly.
- **Deployment step** (not a file): create the "Strategy performance digest" `RemoteTrigger` routine.

---

### Task 1: Exit-rule and aggregation config constants

**Files:**
- Modify: `pipeline/config.py`

**Interfaces:**
- Produces: `CONDOR_EXIT_TARGET_PCT`, `CONDOR_EXIT_TIME_DTE`, `VERTICAL_EXIT_TARGET_PCT`, `CALENDAR_EXIT_TARGET_PCT`, `CALENDAR_EXIT_STOP_PCT`, `DIAGONAL_EXIT_TARGET_PCT`, `DIAGONAL_EXIT_STOP_PCT`, `DIRECTIONAL_STOP_PCT`, `DIRECTIONAL_TARGET_PCT`, `MIN_TERMINAL_TRADES_FOR_STATS` — consumed by Task 3 (`track_outcomes.py`) and Task 6 (`compare_strategies.py`).

- [ ] **Step 1: Add the constants**

```python
# Exit-rule simulation thresholds (docs/superpowers/specs/2026-09-05-strategy-comparison-design.md)
CONDOR_EXIT_TARGET_PCT = 0.55
CONDOR_EXIT_TIME_DTE = 30
VERTICAL_EXIT_TARGET_PCT = 0.10
CALENDAR_EXIT_TARGET_PCT = 0.05
CALENDAR_EXIT_STOP_PCT = 0.10
DIAGONAL_EXIT_TARGET_PCT = 0.05
DIAGONAL_EXIT_STOP_PCT = 0.10
# directional-strategies.md SS6: "individually-chosen stop-loss...
# below the theoretical max loss" -- no book-given fraction, so 50%/200%
# of premium are this spec's own choice (see the design spec's rationale).
DIRECTIONAL_STOP_PCT = 0.50
DIRECTIONAL_TARGET_PCT = 2.00

# Minimum terminal trades before an aggregate stat is reported as
# meaningful rather than flagged "too few trades yet."
MIN_TERMINAL_TRADES_FOR_STATS = 5
```

- [ ] **Step 2: Verify it imports cleanly**

```bash
cd pipeline
python -c "import config; print(config.CONDOR_EXIT_TARGET_PCT, config.DIRECTIONAL_TARGET_PCT, config.MIN_TERMINAL_TRADES_FOR_STATS)"
```

Expected: `0.55 2.0 5`, no exceptions.

- [ ] **Step 3: Commit**

```bash
git add pipeline/config.py
git commit -m "Add exit-rule simulation and aggregation constants"
```

---

### Task 2: Persist the score breakdown and add outcome-tracking columns to the ledger

**Files:**
- Modify: `pipeline/screen_trades.py`
- Test: manual run against real signals data

**Interfaces:**
- Produces: the recommendation ledger now carries `composite_score, iv_richness, skew_quality, risk_reward, pop_proxy, term_structure, liquidity, directional_alignment` (populated at write time) and `outcome_status, outcome_date, realized_pct` (blank at write time) — consumed by Task 4 (`track_outcomes.py`) and Task 6 (`compare_strategies.py`).

- [ ] **Step 1: Add the two new column-name constants near `LEDGER_COLS` in `pipeline/screen_trades.py`**

```python
SCORE_COLS = [
    "composite_score", "iv_richness", "skew_quality", "risk_reward",
    "pop_proxy", "term_structure", "liquidity", "directional_alignment",
]
OUTCOME_COLS = ["outcome_status", "outcome_date", "realized_pct"]
```

- [ ] **Step 2: Modify `write_ledger()` to populate `SCORE_COLS` and initialize `OUTCOME_COLS`**

Replace the row-building loop:

```python
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
```

with:

```python
    rows = []
    date_cols_seen = set()
    for rank, (score, breakdown, candidate) in enumerate(ranked, start=1):
        trade_id = f"{snapshot_date}-{candidate['symbol']}-{rank}"
        contracts = suggested_contracts(candidate)
        for leg in candidate["legs"]:
            row = {
                "symbol": candidate["symbol"],
                "company_name": company_names.get(candidate["symbol"], ""),
                "trade_id": trade_id,
                "strategy": candidate["strategy"],
                "leg_role": leg["leg_role"],
                f"rec:{snapshot_date}": f"{leg['contract_symbol']}/{leg['last_price']}",
                "suggested_contracts": contracts,
                "composite_score": round(score, 2),
                "outcome_status": "",
                "outcome_date": "",
                "realized_pct": "",
            }
            for criterion in SCORE_COLS[1:]:  # everything but composite_score, already set above
                row[criterion] = round(breakdown[criterion], 2)
            rows.append(row)
            date_cols_seen.add(f"rec:{snapshot_date}")
```

- [ ] **Step 3: Update the header-construction line to include the new column groups**

Replace:

```python
    header = LEDGER_COLS + sorted(set(existing_cols) | date_cols_seen) + ["suggested_contracts"]
```

with:

```python
    header = LEDGER_COLS + sorted(set(existing_cols) | date_cols_seen) + SCORE_COLS + ["suggested_contracts"] + OUTCOME_COLS
```

And update the `existing_cols` exclusion list two lines above it — replace:

```python
            existing_cols = [c for c in (reader.fieldnames or []) if c not in LEDGER_COLS + ["suggested_contracts"]]
```

with:

```python
            existing_cols = [c for c in (reader.fieldnames or []) if c not in LEDGER_COLS + SCORE_COLS + ["suggested_contracts"] + OUTCOME_COLS]
```

- [ ] **Step 4: Run it against real data**

```bash
cd "C:\Users\coope\Claude_Work\Projects\Options Trading"
python pipeline/screen_trades.py
```

Expected: same output shape as before; no errors.

- [ ] **Step 5: Spot-check the new columns**

```bash
python -c "
import pandas as pd
df = pd.read_csv('data/github_sync/options_ledger/options_recommendation_ledger.csv')
print(df.columns.tolist())
print(df[['trade_id','strategy','composite_score','iv_richness','outcome_status']].head())
"
```

Expected: all 11 new column names present; `composite_score`/`iv_richness` populated with numbers for today's row(s); `outcome_status` blank.

- [ ] **Step 6: Commit**

```bash
git add pipeline/screen_trades.py
git commit -m "Persist score breakdown and add outcome-tracking columns to the ledger"
```

---

### Task 3: `track_outcomes.py` — OCC parsing, credit/debit math, per-family evaluators

**Files:**
- Create: `pipeline/track_outcomes.py`
- Create: `pipeline/verify_track_outcomes.py`
- Test: `pipeline/verify_track_outcomes.py`

**Interfaces:**
- Produces: `parse_contract(contract_symbol) -> (expiration_iso, option_type, strike)`, `evaluate_trade(strategy, legs, signals_by_date, today) -> (status, outcome_date, realized_pct)` — `legs` is a list of dicts with `leg_role, entry_price, contract_symbol, expiration, strike`; `signals_by_date` is `{date_str: {contract_symbol: last_price}}`. Consumed by Task 4's orchestration and Task 6's `compare_strategies.py` (via the `EVALUATORS`/`STRUCTURE_TYPE` dicts and terminal-status set).

- [ ] **Step 1: Write the failing verification script first**

```python
"""
Verifies pipeline/track_outcomes.py's per-family exit-rule evaluators
against the book-cited thresholds in
docs/superpowers/specs/2026-09-05-strategy-comparison-design.md, plus
the OCC-parsing helper and the gap-skip/UNRESOLVED_AT_EXPIRATION
re-scan behavior. No pytest -- run directly and inspect output.

Run: python pipeline/verify_track_outcomes.py
"""
import sys
from datetime import date

from track_outcomes import evaluate_trade, parse_contract

ALL_OK = True


def check(label, condition):
    global ALL_OK
    print(f"{'OK' if condition else 'FAIL'}: {label}")
    ALL_OK = ALL_OK and condition


def _leg(role, price, contract):
    exp, opt_type, strike = parse_contract(contract)
    return {"leg_role": role, "entry_price": price, "contract_symbol": contract, "expiration": exp, "strike": strike}


def main():
    check("parse_contract expiration/type/strike",
          parse_contract("AAPL260828C00310000") == ("2026-08-28", "call", 310.0))

    # Iron condor: entry credit = (1.20-0.40)+(1.10-0.30) = 1.60. Target
    # at 55% captured -> cost_to_close_now = 1.60*0.45 = 0.72.
    condor_legs = [
        _leg("short call", 1.20, "TEST260101C00110000"),
        _leg("long call", 0.40, "TEST260101C00120000"),
        _leg("short put", 1.10, "TEST260101P00090000"),
        _leg("long put", 0.30, "TEST260101P00080000"),
    ]
    hit_target_prices = {
        "TEST260101C00110000": 0.30, "TEST260101C00120000": 0.10,
        "TEST260101P00090000": 0.25, "TEST260101P00080000": 0.05,
    }  # cost_to_close = (0.30-0.10)+(0.25-0.05) = 0.40 -> profit_pct = (1.60-0.40)/1.60 = 0.75 >= 0.55
    status, out_date, pct = evaluate_trade(
        "iron condor", condor_legs, {"2026-01-15": hit_target_prices}, date(2026, 1, 15),
    )
    check("condor hits target at 75% captured", status == "HIT_TARGET" and pct > 0.55)

    max_loss_prices = {
        "TEST260101C00110000": 5.00, "TEST260101C00120000": 0.05,
        "TEST260101P00090000": 0.05, "TEST260101P00080000": 0.01,
    }  # cost_to_close = (5.00-0.05)+(0.05-0.01) = 4.99 -> loss = 4.99-1.60=3.39 >= 1.60 credit
    status, out_date, pct = evaluate_trade(
        "iron condor", condor_legs, {"2026-01-15": max_loss_prices}, date(2026, 1, 15),
    )
    check("condor hits max loss", status == "HIT_MAX_LOSS")

    time_exit_prices = {
        "TEST260101C00110000": 1.00, "TEST260101C00120000": 0.35,
        "TEST260101P00090000": 0.90, "TEST260101P00080000": 0.25,
    }  # cost_to_close = (1.00-0.35)+(0.90-0.25) = 1.30 -> profit_pct = (1.60-1.30)/1.60 = 0.1875, neither target nor max-loss
    status, out_date, pct = evaluate_trade(
        "iron condor", condor_legs, {"2025-12-02": time_exit_prices}, date(2025, 12, 2),
    )
    # 2026-01-01 expiration, 2025-12-02 is 30 days out -- exactly the TIME_EXIT boundary
    check("condor time-exits at 30 DTE with no target/stop hit", status == "TIME_EXIT")

    # Vertical put credit spread: width=5, credit = 1.50-0.60=0.90.
    vert_legs = [
        _leg("short put", 1.50, "TEST260101P00095000"),
        _leg("long put", 0.60, "TEST260101P00090000"),
    ]
    vert_target_prices = {"TEST260101P00095000": 0.70, "TEST260101P00090000": 0.20}
    # cost_to_close = 0.70-0.20=0.50 -> profit_pct=(0.90-0.50)/0.90=0.44 >= 0.10
    status, _, _ = evaluate_trade("vertical put credit spread", vert_legs, {"2026-01-10": vert_target_prices}, date(2026, 1, 10))
    check("vertical spread hits 10% target", status == "HIT_TARGET")

    vert_max_loss_prices = {"TEST260101P00095000": 5.00, "TEST260101P00090000": 0.00}
    # cost_to_close = 5.00-0.00=5.00 == width(5) -> max loss
    status, _, _ = evaluate_trade("vertical put credit spread", vert_legs, {"2026-01-10": vert_max_loss_prices}, date(2026, 1, 10))
    check("vertical spread hits full max loss at cost==width", status == "HIT_MAX_LOSS")

    # Long calendar: debit = long(back) - short(front) = 2.00-1.50=0.50
    calendar_legs = [
        _leg("short call", 1.50, "TEST260201C00100000"),
        _leg("long call", 2.00, "TEST260301C00100000"),
    ]
    cal_target_prices = {"TEST260201C00100000": 1.00, "TEST260301C00100000": 2.55}
    # value = 2.55-1.00=1.55 -> profit_pct=(1.55-0.50)/0.50=2.1 >= 0.05
    status, _, _ = evaluate_trade("long calendar", calendar_legs, {"2026-01-20": cal_target_prices}, date(2026, 1, 20))
    check("long calendar hits 5% target", status == "HIT_TARGET")

    # Short calendar: credit = short(back) - long(front). Reuse leg
    # shape with roles swapped to represent a short-calendar's actual
    # short=back/long=front convention.
    short_cal_legs = [
        _leg("long call", 1.50, "TEST260201C00100000"),
        _leg("short call", 2.00, "TEST260301C00100000"),
    ]
    # credit = 2.00-1.50=0.50. Stop at 10% loss: cost_to_close-credit >= 0.05
    short_cal_stop_prices = {"TEST260201C00100000": 1.00, "TEST260301C00100000": 1.60}
    # cost_to_close = short_current(1.60) - long_current(1.00) = 0.60 -> loss=0.60-0.50=0.10 >= 0.05
    status, _, _ = evaluate_trade("short calendar", short_cal_legs, {"2026-01-20": short_cal_stop_prices}, date(2026, 1, 20))
    check("short calendar hits 10% stop", status == "HIT_MAX_LOSS")

    # Long call: premium=3.00, target at 200% -> value>=6.00
    long_call_legs = [_leg("long call", 3.00, "TEST260601C00100000")]
    status, _, _ = evaluate_trade("long call", long_call_legs, {"2026-03-01": {"TEST260601C00100000": 6.50}}, date(2026, 3, 1))
    check("long call hits 200% target", status == "HIT_TARGET")
    status, _, _ = evaluate_trade("long call", long_call_legs, {"2026-03-01": {"TEST260601C00100000": 1.40}}, date(2026, 3, 1))
    check("long call hits 50% stop", status == "HIT_MAX_LOSS")

    # Gap-skip: a date with missing pricing for one leg must be skipped,
    # not treated as a signal -- evaluation resumes on the next date.
    gapped_history = {
        "2026-01-10": {"TEST260101P00095000": 1.40},  # long leg missing this day -- must be skipped
        "2026-01-12": vert_target_prices,  # complete data, target should fire here
    }
    status, out_date, _ = evaluate_trade("vertical put credit spread", vert_legs, gapped_history, date(2026, 1, 12))
    check("gap day skipped, target fires on the next complete date", status == "HIT_TARGET" and out_date == "2026-01-12")

    # UNRESOLVED_AT_EXPIRATION: expiration has passed and NO date ever
    # had complete pricing for both legs.
    status, _, pct = evaluate_trade("vertical put credit spread", vert_legs, {}, date(2026, 2, 1))
    check("no data at all + expiration passed -> UNRESOLVED_AT_EXPIRATION", status == "UNRESOLVED_AT_EXPIRATION" and pct is None)

    # Still OPEN: expiration hasn't passed, no data yet.
    status, _, _ = evaluate_trade("vertical put credit spread", vert_legs, {}, date(2025, 12, 1))
    check("no data yet, expiration in the future -> OPEN", status == "OPEN")

    print("ALL_OK" if ALL_OK else "VERIFICATION_FAILED")
    if not ALL_OK:
        sys.exit(1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run it to verify it fails (`track_outcomes.py` doesn't exist yet)**

```bash
cd pipeline
python verify_track_outcomes.py
```

Expected: `ModuleNotFoundError: No module named 'track_outcomes'`.

- [ ] **Step 3: Write `pipeline/track_outcomes.py` (this task's portion — pure logic only; ledger/signals I/O and `run_track_outcomes()` come in Task 4)**

```python
"""
Exit-rule simulator (sub-project 4). Purely reads/writes repo-local CSV
files -- no external fetch -- so this runs entirely in GitHub Actions,
decoupled from the local-PC-only cadence of
merge_and_score.py/screen_trades.py.

Terminal-status naming note: the design spec called the "ran to
expiration with no other rule triggered" states EXPIRED_ITM/EXPIRED_OTM,
borrowed from single-option moneyness language. Implemented here as
EXPIRED_PROFIT/EXPIRED_LOSS instead -- accurate for multi-leg structures
too, where "moneyness" isn't a single well-defined concept. The
underlying math and trigger conditions are unchanged from the spec.

Run from the repo root: `python pipeline/track_outcomes.py`
"""
import re
import subprocess
from datetime import date

import pandas as pd

from config import (
    CALENDAR_EXIT_STOP_PCT, CALENDAR_EXIT_TARGET_PCT, CONDOR_EXIT_TARGET_PCT,
    CONDOR_EXIT_TIME_DTE, DIAGONAL_EXIT_STOP_PCT, DIAGONAL_EXIT_TARGET_PCT,
    DIRECTIONAL_STOP_PCT, DIRECTIONAL_TARGET_PCT, PROJECT_DIR, VERTICAL_EXIT_TARGET_PCT,
)

SIGNALS_DIR = PROJECT_DIR / "data" / "github_sync" / "signals"
LEDGER_PATH = PROJECT_DIR / "data" / "github_sync" / "options_ledger" / "options_recommendation_ledger.csv"

TERMINAL_STATUSES = {
    "HIT_TARGET", "HIT_MAX_LOSS", "TIME_EXIT", "EXPIRED_PROFIT", "EXPIRED_LOSS",
    "UNRESOLVED_AT_EXPIRATION",
}
SCOREABLE_STATUSES = {"HIT_TARGET", "HIT_MAX_LOSS", "TIME_EXIT", "EXPIRED_PROFIT", "EXPIRED_LOSS"}

STRUCTURE_TYPE = {
    "iron condor": "credit",
    "vertical put credit spread": "credit",
    "vertical call credit spread": "credit",
    "short calendar": "credit",
    "long calendar": "debit",
    "double diagonal": "debit",
    "long call": "debit",
    "long put": "debit",
}

_OCC_RE = re.compile(r"^([A-Z]+)(\d{6})([CP])(\d{8})$")


def parse_contract(contract_symbol):
    """Parses an OCC contract symbol into (expiration_iso, option_type,
    strike). E.g. 'AAPL260828C00310000' -> ('2026-08-28', 'call', 310.0)."""
    m = _OCC_RE.match(contract_symbol)
    if not m:
        raise ValueError(f"Cannot parse OCC contract symbol: {contract_symbol!r}")
    _root, yymmdd, cp, strike8 = m.groups()
    expiration = f"20{yymmdd[0:2]}-{yymmdd[2:4]}-{yymmdd[4:6]}"
    option_type = "call" if cp == "C" else "put"
    strike = int(strike8) / 1000.0
    return expiration, option_type, strike


def _credit_received(legs):
    return (
        sum(l["entry_price"] for l in legs if l["leg_role"].startswith("short"))
        - sum(l["entry_price"] for l in legs if l["leg_role"].startswith("long"))
    )


def _debit_paid(legs):
    return (
        sum(l["entry_price"] for l in legs if l["leg_role"].startswith("long"))
        - sum(l["entry_price"] for l in legs if l["leg_role"].startswith("short"))
    )


def _cost_to_close_now(legs, price_lookup):
    return (
        sum(price_lookup[l["contract_symbol"]] for l in legs if l["leg_role"].startswith("short"))
        - sum(price_lookup[l["contract_symbol"]] for l in legs if l["leg_role"].startswith("long"))
    )


def _current_value_now(legs, price_lookup):
    return (
        sum(price_lookup[l["contract_symbol"]] for l in legs if l["leg_role"].startswith("long"))
        - sum(price_lookup[l["contract_symbol"]] for l in legs if l["leg_role"].startswith("short"))
    )


def _evaluate_iron_condor(legs, price_lookup, dte, width):
    credit = _credit_received(legs)
    if credit <= 0:
        return None
    cost = _cost_to_close_now(legs, price_lookup)
    profit_pct = (credit - cost) / credit
    if profit_pct >= CONDOR_EXIT_TARGET_PCT:
        return "HIT_TARGET", profit_pct
    if (cost - credit) >= credit:
        return "HIT_MAX_LOSS", profit_pct
    if dte <= CONDOR_EXIT_TIME_DTE:
        return "TIME_EXIT", profit_pct
    return None


def _evaluate_vertical_credit_spread(legs, price_lookup, dte, width):
    credit = _credit_received(legs)
    if credit <= 0:
        return None
    cost = _cost_to_close_now(legs, price_lookup)
    profit_pct = (credit - cost) / credit
    if profit_pct >= VERTICAL_EXIT_TARGET_PCT:
        return "HIT_TARGET", profit_pct
    if cost >= width:
        return "HIT_MAX_LOSS", profit_pct
    return None


def _evaluate_long_calendar(legs, price_lookup, dte, width):
    debit = _debit_paid(legs)
    if debit <= 0:
        return None
    value = _current_value_now(legs, price_lookup)
    profit_pct = (value - debit) / debit
    if profit_pct >= CALENDAR_EXIT_TARGET_PCT:
        return "HIT_TARGET", profit_pct
    if -profit_pct >= CALENDAR_EXIT_STOP_PCT:
        return "HIT_MAX_LOSS", profit_pct
    return None


def _evaluate_short_calendar(legs, price_lookup, dte, width):
    credit = _credit_received(legs)
    if credit <= 0:
        return None
    cost = _cost_to_close_now(legs, price_lookup)
    profit_pct = (credit - cost) / credit
    if profit_pct >= CALENDAR_EXIT_TARGET_PCT:
        return "HIT_TARGET", profit_pct
    if -profit_pct >= CALENDAR_EXIT_STOP_PCT:
        return "HIT_MAX_LOSS", profit_pct
    return None


def _evaluate_double_diagonal(legs, price_lookup, dte, width):
    debit = _debit_paid(legs)
    if debit <= 0:
        return None
    value = _current_value_now(legs, price_lookup)
    profit_pct = (value - debit) / debit
    if profit_pct >= DIAGONAL_EXIT_TARGET_PCT:
        return "HIT_TARGET", profit_pct
    if -profit_pct >= DIAGONAL_EXIT_STOP_PCT:
        return "HIT_MAX_LOSS", profit_pct
    return None


def _evaluate_directional_long(legs, price_lookup, dte, width):
    debit = _debit_paid(legs)
    if debit <= 0:
        return None
    value = _current_value_now(legs, price_lookup)
    ratio = value / debit
    if ratio <= DIRECTIONAL_STOP_PCT:
        return "HIT_MAX_LOSS", (value - debit) / debit
    if ratio >= DIRECTIONAL_TARGET_PCT:
        return "HIT_TARGET", (value - debit) / debit
    return None


EVALUATORS = {
    "iron condor": _evaluate_iron_condor,
    "vertical put credit spread": _evaluate_vertical_credit_spread,
    "vertical call credit spread": _evaluate_vertical_credit_spread,
    "long calendar": _evaluate_long_calendar,
    "short calendar": _evaluate_short_calendar,
    "double diagonal": _evaluate_double_diagonal,
    "long call": _evaluate_directional_long,
    "long put": _evaluate_directional_long,
}


def _expire(legs, price_lookup, structure_type):
    """Terminal fallback once DTE has reached 0 (or expiration has
    passed) without any rule firing."""
    if structure_type == "credit":
        credit = _credit_received(legs)
        if credit <= 0:
            return None
        cost = _cost_to_close_now(legs, price_lookup)
        realized_pct = (credit - cost) / credit
    else:
        debit = _debit_paid(legs)
        if debit <= 0:
            return None
        value = _current_value_now(legs, price_lookup)
        realized_pct = (value - debit) / debit
    status = "EXPIRED_PROFIT" if realized_pct >= 0 else "EXPIRED_LOSS"
    return status, realized_pct


def evaluate_trade(strategy, legs, signals_by_date, today):
    """Core re-scan-from-entry algorithm. legs: list of dicts with
    leg_role, entry_price, contract_symbol, expiration, strike.
    signals_by_date: {date_str: {contract_symbol: last_price}}. Returns
    (status, outcome_date, realized_pct); realized_pct is None for OPEN
    and UNRESOLVED_AT_EXPIRATION."""
    if strategy not in EVALUATORS:
        raise ValueError(f"No evaluator for strategy {strategy!r}")

    nearest_expiration = min(l["expiration"] for l in legs)
    width = None
    if strategy in ("vertical put credit spread", "vertical call credit spread"):
        strikes = sorted(l["strike"] for l in legs)
        width = strikes[-1] - strikes[0]

    evaluator = EVALUATORS[strategy]
    structure_type = STRUCTURE_TYPE[strategy]

    last_fully_priced_date = None
    last_price_lookup = None
    for snapshot_date in sorted(signals_by_date):
        dte = (date.fromisoformat(nearest_expiration) - date.fromisoformat(snapshot_date)).days
        if dte < 0:
            continue
        prices = signals_by_date[snapshot_date]
        if not all(l["contract_symbol"] in prices for l in legs):
            continue
        price_lookup = {l["contract_symbol"]: prices[l["contract_symbol"]] for l in legs}
        last_fully_priced_date = snapshot_date
        last_price_lookup = price_lookup

        result = evaluator(legs, price_lookup, dte, width)
        if result is not None:
            status, realized_pct = result
            return status, snapshot_date, realized_pct
        if dte == 0:
            result = _expire(legs, price_lookup, structure_type)
            if result is None:
                return "UNRESOLVED_AT_EXPIRATION", snapshot_date, None
            status, realized_pct = result
            return status, snapshot_date, realized_pct

    expiration_has_passed = date.fromisoformat(nearest_expiration) < today
    if expiration_has_passed:
        if last_price_lookup is not None:
            result = _expire(legs, last_price_lookup, structure_type)
            if result is not None:
                status, realized_pct = result
                return status, last_fully_priced_date, realized_pct
        return "UNRESOLVED_AT_EXPIRATION", today.isoformat(), None

    return "OPEN", None, None
```

- [ ] **Step 4: Run the verification script and confirm it passes**

```bash
cd pipeline
python verify_track_outcomes.py
```

Expected: every line prints `OK:`, final line `ALL_OK`.

- [ ] **Step 5: Commit**

```bash
git add pipeline/track_outcomes.py pipeline/verify_track_outcomes.py
git commit -m "Add exit-rule evaluators for all 8 strategy directions with verification"
```

---

### Task 4: `track_outcomes.py` — ledger/signals orchestration and publish

**Files:**
- Modify: `pipeline/track_outcomes.py`
- Test: manual run against real data

**Interfaces:**
- Consumes: `evaluate_trade`, `EVALUATORS`, `TERMINAL_STATUSES`, `parse_contract` (Task 3).
- Produces: `run_track_outcomes()` — updates `outcome_status`/`outcome_date`/`realized_pct` in the recommendation ledger, commits + pushes.

- [ ] **Step 1: Append the orchestration functions to `pipeline/track_outcomes.py`**

```python
import csv


def _load_all_signals():
    """{date_str: {contract_symbol: last_price}} for every signals.csv
    currently in the repo."""
    result = {}
    if not SIGNALS_DIR.exists():
        return result
    for f in sorted(SIGNALS_DIR.glob("*.csv")):
        df = pd.read_csv(f, usecols=["contract_symbol", "last_price"])
        result[f.stem] = dict(zip(df["contract_symbol"], df["last_price"]))
    return result


def _entry_info_for_trade(trade_rows):
    """trade_rows: every ledger row sharing one trade_id. Returns
    (entry_date, legs) -- legs is None if entry pricing can't be
    recovered (e.g. a malformed rec: cell)."""
    entry_date = trade_rows[0]["trade_id"][:10]
    rec_col = f"rec:{entry_date}"
    legs = []
    for row in trade_rows:
        cell = row.get(rec_col, "")
        if not cell or "/" not in cell:
            continue
        contract_symbol, price = cell.rsplit("/", 1)
        expiration, _option_type, strike = parse_contract(contract_symbol)
        legs.append({
            "leg_role": row["leg_role"],
            "entry_price": float(price),
            "contract_symbol": contract_symbol,
            "expiration": expiration,
            "strike": strike,
        })
    return entry_date, legs


def commit_and_push(paths, message):
    paths = [str(p) for p in paths]
    subprocess.run(["git", "add", *paths], cwd=PROJECT_DIR, check=True, timeout=60)
    diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=PROJECT_DIR, timeout=30)
    if diff.returncode == 0:
        return "no_changes"
    subprocess.run(["git", "commit", "-m", message], cwd=PROJECT_DIR, check=True, timeout=60)
    subprocess.run(["git", "push"], cwd=PROJECT_DIR, check=True, timeout=120)
    return "pushed"


def git_pull():
    result = subprocess.run(["git", "pull"], cwd=PROJECT_DIR, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"git pull failed: {result.stderr}")
    return result.stdout.strip()


def run_track_outcomes():
    print("Pulling latest from GitHub...")
    print(git_pull())

    if not LEDGER_PATH.exists():
        print("No recommendation ledger yet -- nothing to track")
        return {"status": "no_data"}

    with open(LEDGER_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    for col in ("outcome_status", "outcome_date", "realized_pct"):
        if col not in fieldnames:
            fieldnames.append(col)

    signals_by_date = _load_all_signals()
    today = date.today()

    by_trade_id = {}
    for row in rows:
        by_trade_id.setdefault(row["trade_id"], []).append(row)

    updated = 0
    for trade_id, trade_rows in by_trade_id.items():
        current_status = trade_rows[0].get("outcome_status", "")
        if current_status in TERMINAL_STATUSES:
            continue

        strategy = trade_rows[0]["strategy"]
        if strategy not in EVALUATORS:
            print(f"{trade_id}: unknown strategy {strategy!r} -- skipping")
            continue

        try:
            _entry_date, legs = _entry_info_for_trade(trade_rows)
            if not legs:
                print(f"{trade_id}: no recoverable entry legs -- skipping")
                continue
            status, outcome_date, realized_pct = evaluate_trade(strategy, legs, signals_by_date, today)
        except Exception as exc:
            print(f"{trade_id}: SKIPPED ({exc})")
            continue

        if status == "OPEN" and current_status == "OPEN":
            continue

        for row in trade_rows:
            row["outcome_status"] = status
            row["outcome_date"] = outcome_date or ""
            row["realized_pct"] = round(realized_pct, 4) if realized_pct is not None else ""
        updated += 1
        print(f"{trade_id}: {strategy} -> {status}")

    if updated == 0:
        print("No trade outcomes changed")
        return {"status": "no_changes", "updated": 0}

    with open(LEDGER_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({c: row.get(c, "") for c in fieldnames})

    status = commit_and_push([LEDGER_PATH], f"Track outcomes: {updated} trade(s) updated")
    print(f"Publish status: {status}")
    return {"status": status, "updated": updated}


if __name__ == "__main__":
    print(run_track_outcomes())
```

- [ ] **Step 2: Run it against real data**

```bash
cd "C:\Users\coope\Claude_Work\Projects\Options Trading"
python pipeline/track_outcomes.py
```

Expected: pull output, then either `No trade outcomes changed` (today's trade is only 1 day old — genuinely still `OPEN`, not a bug) or a status line per trade updated, ending with a `{'status': ..., 'updated': N}` dict.

- [ ] **Step 3: Spot-check no incorrect terminal status was assigned to a fresh trade**

```bash
python -c "
import pandas as pd
df = pd.read_csv('data/github_sync/options_ledger/options_recommendation_ledger.csv')
print(df[['trade_id','strategy','outcome_status','outcome_date','realized_pct']].drop_duplicates('trade_id'))
"
```

Expected: today's/yesterday's trade(s) show `outcome_status` blank or `OPEN` (correct — nowhere near their DTE-based exit windows yet).

- [ ] **Step 4: Commit**

```bash
git add pipeline/track_outcomes.py
git commit -m "Add track_outcomes.py orchestration: ledger walk, re-scan, publish"
```

---

### Task 5: Daily GitHub Actions workflow for `track_outcomes.py`

**Files:**
- Create: `.github/workflows/track-outcomes.yml`

**Interfaces:**
- Consumes: `pipeline/track_outcomes.py` (Tasks 3-4), `pipeline/requirements.txt` (already exists).

- [ ] **Step 1: Write the workflow**

```yaml
name: Track outcomes

# Runs entirely in the cloud, once per day. Replays each open
# recommendation's exit rule against the signals.csv history already in
# this repo -- no external fetch, so no local-machine dependency at all.

on:
  schedule:
    - cron: "0 19 * * *"  # once daily; timing isn't tied to market hours since this only reads already-published data
  workflow_dispatch:

permissions:
  contents: write

jobs:
  track:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7

      - uses: actions/setup-python@v7
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: pip install -r pipeline/requirements.txt

      - name: Track outcomes
        run: python pipeline/track_outcomes.py
        working-directory: .
```

- [ ] **Step 2: Fix the working directory issue — `track_outcomes.py` imports `config`/etc. via its own directory being added to `sys.path`, but the Actions runner invokes it from the repo root, same as `merge_and_score.py`'s own workflow-less local convention. Confirm this actually works the same way `cloud/fetch_options_snapshot.py` does (plain module-relative imports, script's own directory auto-added to `sys.path` by Python) by testing the exact invocation locally**

```bash
cd "C:\Users\coope\Claude_Work\Projects\Options Trading"
python pipeline/track_outcomes.py
```

Expected: same successful output as Task 4 Step 2 (this just re-confirms the exact repo-root invocation the workflow uses). Remove the redundant `working-directory: .` line from the workflow (it's the default) since this confirms it isn't needed:

```yaml
      - name: Track outcomes
        run: python pipeline/track_outcomes.py
```

- [ ] **Step 3: Commit, push, and verify one manual Actions run**

```bash
git add .github/workflows/track-outcomes.yml
git commit -m "Add daily track-outcomes GitHub Actions workflow"
git push
gh workflow run track-outcomes.yml
gh run list --workflow=track-outcomes.yml --limit 1
```

Expected (after the run completes — poll `gh run list` if `in_progress`): `completed success`.

---

### Task 6: `compare_strategies.py` — aggregation

**Files:**
- Create: `pipeline/compare_strategies.py`
- Create: `pipeline/verify_compare_strategies.py`
- Test: `pipeline/verify_compare_strategies.py`

**Interfaces:**
- Consumes: `config.MIN_TERMINAL_TRADES_FOR_STATS` (Task 1); `track_outcomes.SCOREABLE_STATUSES` (Task 3, imported).
- Produces: `by_family(trades) -> list[dict]`, `by_criterion(trades) -> list[dict]`, `run_compare_strategies()` — publishes `data/github_sync/options_ledger/strategy_performance_report.csv`.

- [ ] **Step 1: Write the failing verification script first**

```python
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
```

- [ ] **Step 2: Run it to verify it fails**

```bash
cd pipeline
python verify_compare_strategies.py
```

Expected: `ModuleNotFoundError: No module named 'compare_strategies'`.

- [ ] **Step 3: Write `pipeline/compare_strategies.py`**

```python
"""
Aggregation script (sub-project 4). Reads the recommendation ledger's
scoreable terminal-outcome rows and produces two views: performance by
strategy family, and performance by scoring criterion (above/below-
median win-rate split). Purely reads/writes repo-local files -- runs
entirely in GitHub Actions.

Run from the repo root: `python pipeline/compare_strategies.py`
"""
import csv
import statistics
import subprocess

from config import MIN_TERMINAL_TRADES_FOR_STATS, PROJECT_DIR
from track_outcomes import SCOREABLE_STATUSES

LEDGER_PATH = PROJECT_DIR / "data" / "github_sync" / "options_ledger" / "options_recommendation_ledger.csv"
REPORT_PATH = PROJECT_DIR / "data" / "github_sync" / "options_ledger" / "strategy_performance_report.csv"

WINNING_STATUSES = {"HIT_TARGET", "EXPIRED_PROFIT"}
CRITERIA = [
    "iv_richness", "skew_quality", "risk_reward", "pop_proxy",
    "term_structure", "liquidity", "directional_alignment",
]


def _load_terminal_trades():
    """One dict per trade_id (deduped across its leg rows) for every
    trade_id whose outcome_status is scoreable."""
    trades = {}
    with open(LEDGER_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("outcome_status") not in SCOREABLE_STATUSES:
                continue
            trade_id = row["trade_id"]
            if trade_id in trades:
                continue
            realized_raw = row.get("realized_pct")
            realized_pct = float(realized_raw) if realized_raw not in (None, "") else None
            is_win = row["outcome_status"] in WINNING_STATUSES or (
                row["outcome_status"] == "TIME_EXIT" and realized_pct is not None and realized_pct > 0
            )
            trade = {"strategy": row["strategy"], "realized_pct": realized_pct, "is_win": is_win}
            for c in CRITERIA:
                val = row.get(c)
                trade[c] = float(val) if val not in (None, "") else None
            trades[trade_id] = trade
    return list(trades.values())


def by_family(trades):
    families = {}
    for t in trades:
        families.setdefault(t["strategy"], []).append(t)

    rows = []
    for strategy, group in families.items():
        n = len(group)
        wins = sum(1 for t in group if t["is_win"])
        pcts = [t["realized_pct"] for t in group if t["realized_pct"] is not None]
        rows.append({
            "strategy": strategy,
            "sample_size": n,
            "win_rate": round(wins / n, 3) if n else None,
            "avg_realized_pct": round(statistics.mean(pcts), 4) if pcts else None,
            "note": "" if n >= MIN_TERMINAL_TRADES_FOR_STATS else "too few trades to be meaningful yet",
        })
    return rows


def by_criterion(trades):
    rows = []
    for criterion in CRITERIA:
        scored = [t for t in trades if t.get(criterion) is not None]
        if len(scored) < MIN_TERMINAL_TRADES_FOR_STATS:
            rows.append({
                "criterion": criterion, "sample_size": len(scored),
                "above_median_win_rate": None, "below_median_win_rate": None,
                "note": "too few trades to be meaningful yet",
            })
            continue
        median = statistics.median(t[criterion] for t in scored)
        above = [t for t in scored if t[criterion] >= median]
        below = [t for t in scored if t[criterion] < median]
        rows.append({
            "criterion": criterion,
            "sample_size": len(scored),
            "above_median_win_rate": round(sum(1 for t in above if t["is_win"]) / len(above), 3) if above else None,
            "below_median_win_rate": round(sum(1 for t in below if t["is_win"]) / len(below), 3) if below else None,
            "note": "",
        })
    return rows


def commit_and_push(paths, message):
    paths = [str(p) for p in paths]
    subprocess.run(["git", "add", *paths], cwd=PROJECT_DIR, check=True, timeout=60)
    diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=PROJECT_DIR, timeout=30)
    if diff.returncode == 0:
        return "no_changes"
    subprocess.run(["git", "commit", "-m", message], cwd=PROJECT_DIR, check=True, timeout=60)
    subprocess.run(["git", "push"], cwd=PROJECT_DIR, check=True, timeout=120)
    return "pushed"


def git_pull():
    result = subprocess.run(["git", "pull"], cwd=PROJECT_DIR, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"git pull failed: {result.stderr}")
    return result.stdout.strip()


def run_compare_strategies():
    print("Pulling latest from GitHub...")
    print(git_pull())

    if not LEDGER_PATH.exists():
        print("No recommendation ledger yet -- nothing to compare")
        return {"status": "no_data"}

    trades = _load_terminal_trades()
    print(f"{len(trades)} scoreable terminal trade(s) found")

    family_rows = by_family(trades)
    criterion_rows = by_criterion(trades)

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["section", "key", "sample_size", "win_rate_or_above_median", "avg_realized_pct_or_below_median", "note"])
        for r in family_rows:
            writer.writerow(["by_family", r["strategy"], r["sample_size"], r["win_rate"], r["avg_realized_pct"], r["note"]])
        for r in criterion_rows:
            writer.writerow(["by_criterion", r["criterion"], r["sample_size"], r["above_median_win_rate"], r["below_median_win_rate"], r["note"]])

    status = commit_and_push([REPORT_PATH], f"Strategy performance report: {len(trades)} terminal trades")
    print(f"Publish status: {status}")
    return {"status": status, "terminal_trades": len(trades)}


if __name__ == "__main__":
    print(run_compare_strategies())
```

- [ ] **Step 4: Run the verification script and confirm it passes**

```bash
cd pipeline
python verify_compare_strategies.py
```

Expected: every line prints `OK:`, final line `ALL_OK`.

- [ ] **Step 5: Run it against real data**

```bash
cd "C:\Users\coope\Claude_Work\Projects\Options Trading"
python pipeline/compare_strategies.py
```

Expected: `0 scoreable terminal trade(s) found` (correct — nothing has reached a terminal outcome yet this early), a report CSV published containing only `note: "too few trades to be meaningful yet"` rows, not fabricated numbers.

- [ ] **Step 6: Commit**

```bash
git add pipeline/compare_strategies.py pipeline/verify_compare_strategies.py
git commit -m "Add compare_strategies.py aggregation with verification"
```

---

### Task 7: Weekly GitHub Actions workflow for `compare_strategies.py`

**Files:**
- Create: `.github/workflows/compare-strategies.yml`

**Interfaces:**
- Consumes: `pipeline/compare_strategies.py` (Task 6).

- [ ] **Step 1: Write the workflow**

```yaml
name: Compare strategies

# Runs entirely in the cloud, weekly, after that day's track-outcomes
# run. Aggregates scoreable terminal trades by family and by scoring
# criterion, publishing a report the new weekly routine reads.

on:
  schedule:
    - cron: "0 20 * * 0"  # Sunday 20:00 UTC, after the 19:00 UTC daily track-outcomes run
  workflow_dispatch:

permissions:
  contents: write

jobs:
  compare:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7

      - uses: actions/setup-python@v7
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: pip install -r pipeline/requirements.txt

      - name: Compare strategies
        run: python pipeline/compare_strategies.py
```

- [ ] **Step 2: Commit, push, and verify one manual Actions run**

```bash
git add .github/workflows/compare-strategies.yml
git commit -m "Add weekly compare-strategies GitHub Actions workflow"
git push
gh workflow run compare-strategies.yml
gh run list --workflow=compare-strategies.yml --limit 1
```

Expected (poll if `in_progress`): `completed success`.

---

### Task 8: Deploy — confirm both workflows are live and in sync

**Files:** none (deployment step)

- [ ] **Step 1: Confirm local and remote are in sync**

```bash
cd "C:\Users\coope\Claude_Work\Projects\Options Trading"
git push
git log --oneline -12
git ls-remote --heads origin master
```

Expected: local `master` and `origin/master` point to the same commit; log shows every task commit from Tasks 1-7.

- [ ] **Step 2: Confirm the published report is reachable the way the new routine will read it**

```bash
python -c "
import sys
sys.path.insert(0, 'pipeline')
import config
import requests
r = requests.get('https://raw.githubusercontent.com/coop1st/options-trading-pipeline/master/data/github_sync/options_ledger/strategy_performance_report.csv', timeout=30)
print(r.status_code, len(r.text), 'bytes')
print(r.text[:300])
"
```

Expected: `200`, a non-trivial byte count showing the header row plus `by_family`/`by_criterion` rows (all `note: too few trades to be meaningful yet` at this point — correct, not a bug).

---

### Task 9: Create and verify the "Strategy performance digest" cloud routine

**Files:** none (a `RemoteTrigger` API call, not a repo file)

- [ ] **Step 1: Generate a fresh UUID for the routine's initial event**

```bash
python -c "import uuid; print(str(uuid.uuid4()))"
```

- [ ] **Step 2: Create the recurring routine**

Call `RemoteTrigger` with `action: "create"`. Reuse the existing `environment_id` (`env_017ZfNsQhAPemSDvsptSbtZr`) already confirmed working for this repo by the "Options signals check (nightly)" routine, unless `RemoteTrigger action=list` suggests otherwise:

```json
{
  "name": "Strategy performance digest (weekly)",
  "cron_expression": "30 20 * * 0",
  "enabled": true,
  "job_config": {
    "ccr": {
      "environment_id": "env_017ZfNsQhAPemSDvsptSbtZr",
      "session_context": {
        "model": "claude-sonnet-5",
        "sources": [{"git_repository": {"url": "https://github.com/coop1st/options-trading-pipeline"}}],
        "allowed_tools": ["Bash", "Read", "Glob", "mcp__Gmail__create_draft"]
      },
      "events": [{"data": {
        "uuid": "<fresh UUID from Step 1>",
        "session_id": "",
        "type": "user",
        "parent_tool_use_id": null,
        "message": {"role": "user", "content": "<PROMPT -- see below>"}
      }}]
    }
  }
}
```

`cron_expression` explanation: `30 20 * * 0` fires Sunday 20:30 UTC, 30 minutes after `compare-strategies.yml`'s 20:00 UTC run, giving it time to finish and publish.

The prompt (fill in as the `message.content` string above):

```
You are running the weekly strategy-performance digest for the
coop1st/options-trading-pipeline repo, already cloned into your working
directory. A GitHub Actions job (compare_strategies.py) runs every
Sunday and publishes
data/github_sync/options_ledger/strategy_performance_report.csv --
your job is to read it and draft a human-facing weekly email. Hard
safety requirement: never fail silently, and never invent numbers the
report doesn't contain.

1. Read data/github_sync/options_ledger/strategy_performance_report.csv
   (columns: section, key, sample_size, win_rate_or_above_median,
   avg_realized_pct_or_below_median, note). Rows with section=by_family
   show one strategy's win rate and average realized P&L percentage;
   rows with section=by_criterion show, for one of the 7 scoring
   criteria, the win rate among trades that scored above that
   criterion's median versus below it.

2. If the file is missing entirely, draft a short alert email to
   kcoopercscs@gmail.com (subject "Strategy performance digest --
   automation alert") stating the report wasn't found, and stop.

3. Otherwise, draft (do NOT send) a Gmail email to
   kcoopercscs@gmail.com, subject "Strategy performance digest --
   {today's date}", with two sections:
   - "By strategy family": for each by_family row, state the strategy
     name, sample size, win rate, and average realized P&L. For any row
     whose note says "too few trades to be meaningful yet", say so
     explicitly instead of presenting the numbers as reliable.
   - "By scoring criterion": for each by_criterion row, state whether
     trades scoring above that criterion's median won more often than
     those below it (i.e., whether the criterion appears predictive),
     again flagging low-sample-size rows explicitly rather than drawing
     a conclusion from them.

4. If every row in the report says "too few trades to be meaningful
   yet" (expected for a while after this pipeline first ships), say so
   plainly as the entire content of the email rather than padding it out
   with the sparse numbers presented as if they meant something.
```

- [ ] **Step 3: Relay the created routine's URL and confirmed run time**

The `RemoteTrigger create` response includes a summary line with the server-parsed schedule and the routine's `https://claude.ai/code/routines/{id}` URL — relay both.

- [ ] **Step 4: Manually trigger one verification run**

```
RemoteTrigger action=run trigger_id=<id from Step 2's response>
```

- [ ] **Step 5: Poll the run log until it completes**

```
RemoteTrigger action=list_runs trigger_id=<id>
RemoteTrigger action=get_run_log session_id=<id from list_runs>
```

(Repeat `get_run_log` every ~20-30 seconds until the log shows a `result:` line — matches the polling approach already used to verify the sub-project 3 routine.)

Expected: `result: success`, no tool-permission errors. Then check Gmail for the new draft and confirm it correctly states every row is currently too-few-trades-to-be-meaningful (accurate for this early state) rather than fabricating a false conclusion.

---

## Not done here

- **Re-weighting `scoring.py`** based on what this sub-project's by-criterion data eventually shows — an intentional follow-up decision, not part of this plan, per the spec's Non-goals.
- **Adjustment simulation** (kite spreads, ratio-spread adjustments, rolling) — explicitly out of scope; every simulated position runs from entry to one terminal outcome with no modeled mid-course adjustment.
- **Real fill tracking** — this whole sub-project exists specifically to avoid needing it.

## Self-Review Notes

- **Spec coverage**: the required score-breakdown persistence (Task 2), the corrected re-scan-from-entry `LOST_TO_TRACKING`→`UNRESOLVED_AT_EXPIRATION` behavior (Task 3's `evaluate_trade`, directly tested in Task 3's verify script), the long call/put exit strategy (Task 3's `_evaluate_directional_long`), all 8 strategy-direction evaluators split correctly by credit/debit structure type (Task 3), the daily/weekly GH Actions decoupling from local-PC cadence (Tasks 5, 7), and the weekly digest routine (Task 9) each have a task.
- **Placeholder scan**: no TBD/TODO; every step has real, runnable code. The `EXPIRED_ITM`/`EXPIRED_OTM` → `EXPIRED_PROFIT`/`EXPIRED_LOSS` naming change and the report-format/schedule resolutions are called out explicitly in Global Constraints as decisions made while writing this plan, not silently substituted.
- **Type/interface consistency checked**: `evaluate_trade()`'s three-tuple return shape (Task 3) is consumed identically by Task 3's own verify script and Task 4's orchestration; `EVALUATORS`/`STRUCTURE_TYPE`/`TERMINAL_STATUSES`/`SCOREABLE_STATUSES` (Task 3) are imported by name into `compare_strategies.py` (Task 6) rather than redefined, so the two scripts can't drift out of sync on what counts as "terminal" or "scoreable"; the 8 `SCORE_COLS` names added in Task 2 match exactly the 7 criteria keys `scoring.py`'s `score_candidate()` breakdown dict already uses (verified against the actual `pipeline/scoring.py` source, not from memory) plus `composite_score`.
