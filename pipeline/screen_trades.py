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
from pathlib import Path

import pandas as pd

from atr import refresh_atr_if_stale
from config import (
    ACCOUNT_EQUITY, CALENDAR_LONG_PREMIUM_MAX, CALENDAR_LONG_PREMIUM_MIN,
    CALENDAR_MIN_FRONT_DAYS, CALENDAR_SHORT_DISCOUNT, CONDOR_DELTA_MAX, CONDOR_DELTA_MIN,
    CONDOR_MAX_DTE, CONDOR_MIN_DTE, EQUITY_MIN_DAILY_VOLUME, MAX_LOSS_PCT_PER_TRADE,
    MIN_OPEN_INTEREST, MIN_VOLUME, PROJECT_DIR, TAIL_HEDGE_PRIORITY, TOP_N_CANDIDATES,
    UNIT_MAX_DELTA, UNIT_MAX_PRICE, VERTICAL_DELTA_BAND, VERTICAL_MAX_DTE, VERTICAL_MIN_DTE,
    VERTICAL_SPREAD_WIDTHS,
)
from db import get_atr_row, get_term_structure_spread_history, init_db
from directional_bias import fetch_directional_bias
from scoring import score_candidate
from strategy_rules import (
    build_calendars, build_directional_longs, build_double_diagonals,
    build_iron_condors, build_vertical_credit_spreads,
)

# ^VIX (added to the watchlist in cloud/fetch_options_snapshot.py purely
# to feed build_units_reminder below) is excluded from every
# strategy-family builder -- not for scope discipline, but because VIX
# options are cash-settled and price off VIX FUTURES, not spot VIX
# (income-strategies.md SS6's flash-crash case study), while this
# pipeline's Black-Scholes Greeks are computed against spot
# underlying_price, so any delta/candidate this pipeline would build on
# ^VIX is unreliable by the books' own logic. SPY/VXX/UVXY don't have
# this problem (their options are standard American-style, spot-priced
# ETP options) and ^SPX doesn't either (Bittman explicitly recommends
# SPX for income strategies, income-strategies.md SS1 -- its index
# options are conventionally modeled off spot, unlike VIX's
# futures-tracking quirk) -- both remain eligible for normal screening.
STRATEGY_SCREENING_EXCLUSIONS = {"^VIX"}

SIGNALS_DIR = PROJECT_DIR / "data" / "github_sync" / "signals"
LEDGER_PATH = PROJECT_DIR / "data" / "github_sync" / "options_ledger" / "options_recommendation_ledger.csv"
LEDGER_COLS = ["symbol", "company_name", "trade_id", "strategy", "leg_role"]
SCORE_COLS = [
    "composite_score", "iv_richness", "skew_quality", "risk_reward",
    "pop_proxy", "term_structure", "liquidity", "directional_alignment",
]
OUTCOME_COLS = ["outcome_status", "outcome_date", "realized_pct"]


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
    signals = signals[~signals["symbol"].isin(STRATEGY_SCREENING_EXCLUSIONS)]

    candidates = []
    candidates += build_vertical_credit_spreads(
        signals, snapshot_date, bias, VERTICAL_MIN_DTE, VERTICAL_MAX_DTE,
        VERTICAL_DELTA_BAND, VERTICAL_SPREAD_WIDTHS, EQUITY_MIN_DAILY_VOLUME,
    )
    candidates += build_iron_condors(
        signals, snapshot_date, get_atr, CONDOR_MIN_DTE, CONDOR_MAX_DTE, CONDOR_DELTA_MIN, CONDOR_DELTA_MAX, bias,
    )
    candidates += build_directional_longs(signals, bias, EQUITY_MIN_DAILY_VOLUME)
    candidates += build_calendars(
        signals, snapshot_date, get_term_history, CALENDAR_MIN_FRONT_DAYS,
        CALENDAR_LONG_PREMIUM_MIN, CALENDAR_LONG_PREMIUM_MAX, CALENDAR_SHORT_DISCOUNT, bias,
    )
    candidates += build_double_diagonals(
        signals, snapshot_date, get_term_history, CALENDAR_MIN_FRONT_DAYS,
        CALENDAR_LONG_PREMIUM_MIN, CONDOR_DELTA_MIN, CONDOR_DELTA_MAX, bias,
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

    existing_rows, existing_cols = [], []
    if LEDGER_PATH.exists():
        with open(LEDGER_PATH, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            existing_cols = [c for c in (reader.fieldnames or []) if c not in LEDGER_COLS + SCORE_COLS + ["suggested_contracts"] + OUTCOME_COLS]
            all_prior_rows = list(reader)
        # Re-running the orchestrator for a snapshot_date it already
        # published (e.g. a manual re-run, or a retriggered routine)
        # must REPLACE that date's trade rows, not accumulate duplicates
        # alongside them -- trade_id is namespaced "{snapshot_date}-...",
        # so drop any prior row whose trade_id belongs to today's date
        # before appending today's freshly-built rows.
        existing_rows = [r for r in all_prior_rows if not r["trade_id"].startswith(f"{snapshot_date}-")]

    header = LEDGER_COLS + sorted(set(existing_cols) | date_cols_seen) + SCORE_COLS + ["suggested_contracts"] + OUTCOME_COLS
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LEDGER_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        for row in existing_rows:
            writer.writerow({c: row.get(c, "") for c in header})
        for row in rows:
            writer.writerow({c: row.get(c, "") for c in header})

    return len(rows)


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

    units_reminder = build_units_reminder(signals)
    print(f"Units reminder: {units_reminder}")

    status = commit_and_push([LEDGER_PATH], f"Options recommendations: {snapshot_date} ({len(ranked)} candidates)")
    print(f"Publish status: {status}")
    return {"status": status, "date": snapshot_date, "candidates": len(ranked), "units_reminder": units_reminder}


if __name__ == "__main__":
    init_db()
    print(run_screen_trades())
