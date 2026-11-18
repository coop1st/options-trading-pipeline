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
import csv
import re
import subprocess
from datetime import date

import pandas as pd

from pricing import price_lookup
from config import (
    CALENDAR_EXIT_STOP_PCT, CALENDAR_EXIT_TARGET_PCT, CALENDAR_MIN_PROFIT_DOLLARS, CONDOR_EXIT_TARGET_PCT,
    CONDOR_EXIT_TIME_DTE, DIAGONAL_EXIT_STOP_PCT, DIAGONAL_EXIT_TARGET_PCT,
    DIRECTIONAL_STOP_PCT, DIRECTIONAL_TARGET_PCT, NAKED_MARGIN_MIN_RATE, NAKED_MARGIN_RATE_EQUITY,
    NAKED_MARGIN_RATE_INDEX, PROJECT_DIR, VERTICAL_EXIT_TARGET_PCT,
)

SIGNALS_DIR = PROJECT_DIR / "data" / "github_sync" / "signals"
LEDGER_PATH = PROJECT_DIR / "data" / "github_sync" / "options_ledger" / "options_recommendation_ledger.csv"

TERMINAL_STATUSES = {
    "HIT_TARGET", "HIT_MAX_LOSS", "TIME_EXIT", "EXPIRED_PROFIT", "EXPIRED_LOSS",
    "UNRESOLVED_AT_EXPIRATION", "ENTRY_NOT_PRICEABLE",
}
# ENTRY_NOT_PRICEABLE: on the entry day at least one leg had no real bid
# and ask, or the legs' midpoints gave no positive net price -- so there
# was never a real, same-moment price to enter at and no
# result can honestly be computed. Terminal, never scored. Trades
# recommended since 2026-11-17 are only built from priced contracts, so
# this status is for the older ones.
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
    if profit_pct >= CALENDAR_EXIT_TARGET_PCT and (value - debit) >= CALENDAR_MIN_PROFIT_DOLLARS:
        return "HIT_TARGET", profit_pct
    if -profit_pct >= CALENDAR_EXIT_STOP_PCT:
        return "HIT_MAX_LOSS", profit_pct
    return None


def short_calendar_margin(symbol, legs, underlying_price):
    """ESTIMATED original margin, per share, of a short calendar at entry
    -- see config.py (NAKED_MARGIN_*) for the rule and why it is the
    project's own estimate, not a book number. legs carry entry_price and
    contract_symbol. None if there is no underlying price to work from."""
    if underlying_price is None or not underlying_price > 0:
        return None
    short = next(l for l in legs if l["leg_role"].startswith("short"))
    long_ = next(l for l in legs if l["leg_role"].startswith("long"))
    _exp, option_type, strike = parse_contract(short["contract_symbol"])
    rate = NAKED_MARGIN_RATE_INDEX if symbol.startswith("^") else NAKED_MARGIN_RATE_EQUITY
    if option_type == "call":
        otm = max(0.0, strike - underlying_price)
        floor = NAKED_MARGIN_MIN_RATE * underlying_price
    else:
        otm = max(0.0, underlying_price - strike)
        floor = NAKED_MARGIN_MIN_RATE * strike
    return short["entry_price"] + max(rate * underlying_price - otm, floor) + long_["entry_price"]


def _evaluate_short_calendar(legs, price_lookup, dte, width, margin=None):
    """Target: 5% of the credit (the book's worked short calendars measure
    the gain on the price sold at). Stop: a loss of 10% of the original
    margin (Chen/Sebastian ch.9), using short_calendar_margin's estimate.
    If no margin could be estimated (margin=None) the stop falls back to
    10% of the credit, the rule in force before 2026-11-18. The result is
    still reported as a percentage of the credit, like every other
    credit trade."""
    credit = _credit_received(legs)
    if credit <= 0:
        return None
    cost = _cost_to_close_now(legs, price_lookup)
    profit_pct = (credit - cost) / credit
    if profit_pct >= CALENDAR_EXIT_TARGET_PCT and (credit - cost) >= CALENDAR_MIN_PROFIT_DOLLARS:
        return "HIT_TARGET", profit_pct
    stop_dollars = CALENDAR_EXIT_STOP_PCT * (margin if margin else credit)
    if (cost - credit) >= stop_dollars:
        return "HIT_MAX_LOSS", profit_pct
    return None


def _evaluate_double_diagonal(legs, price_lookup, dte, width):
    debit = _debit_paid(legs)
    if debit <= 0:
        return None
    value = _current_value_now(legs, price_lookup)
    profit_pct = (value - debit) / debit
    if profit_pct >= DIAGONAL_EXIT_TARGET_PCT and (value - debit) >= CALENDAR_MIN_PROFIT_DOLLARS:
        return "HIT_TARGET", profit_pct
    if -profit_pct >= DIAGONAL_EXIT_STOP_PCT:
        return "HIT_MAX_LOSS", profit_pct
    return None


def _evaluate_directional_long(legs, price_lookup, dte, width,
                                stop_pct=DIRECTIONAL_STOP_PCT, target_pct=DIRECTIONAL_TARGET_PCT):
    """stop_pct/target_pct default to the live config constants -- the
    only reason they're parameters at all is sub-project 5's exit-side
    sweep (generate_tuning_stats.py), which re-evaluates already-
    terminal trades' known price paths under alternate values. No other
    evaluator in this module takes overrides: every other family's exit
    rule is Tier 1 (book-verbatim), never swept."""
    debit = _debit_paid(legs)
    if debit <= 0:
        return None
    value = _current_value_now(legs, price_lookup)
    ratio = value / debit
    if ratio <= stop_pct:
        return "HIT_MAX_LOSS", (value - debit) / debit
    if ratio >= target_pct:
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


def evaluate_trade(strategy, legs, signals_by_date, today, evaluator_overrides=None, entry_date=None):
    """Core re-scan-from-entry algorithm. legs: list of dicts with
    leg_role, entry_price, contract_symbol, expiration, strike.
    signals_by_date: {date_str: {contract_symbol: last_price}}. Returns
    (status, outcome_date, realized_pct); realized_pct is None for OPEN
    and UNRESOLVED_AT_EXPIRATION. An EXPIRED_* result is only ever taken
    from prices on the expiration day itself; if expiration passes
    without one, the trade is UNRESOLVED_AT_EXPIRATION (dated at its
    expiration) and is never scored. evaluator_overrides (optional dict of
    kwargs) is forwarded to the evaluator -- meaningful only for
    "long call"/"long put" (see _evaluate_directional_long) and for
    "short calendar" ({"margin": ...}, the trade's estimated original
    margin -- a fact about the trade, not a swept setting); passing it
    for any other strategy will raise, since those evaluators take no
    such kwargs, by design (Tier 1 exit rules are never swept).
    entry_date (ISO str): only snapshots strictly after it are replayed --
    the entry-day file holds the entry prices themselves, and earlier
    files predate the recommendation entirely."""
    if strategy not in EVALUATORS:
        raise ValueError(f"No evaluator for strategy {strategy!r}")

    nearest_expiration = min(l["expiration"] for l in legs)
    width = None
    if strategy in ("vertical put credit spread", "vertical call credit spread"):
        strikes = sorted(l["strike"] for l in legs)
        width = strikes[-1] - strikes[0]

    evaluator = EVALUATORS[strategy]
    structure_type = STRUCTURE_TYPE[strategy]
    overrides = evaluator_overrides or {}

    for snapshot_date in sorted(signals_by_date):
        if entry_date is not None and snapshot_date <= entry_date:
            continue
        dte = (date.fromisoformat(nearest_expiration) - date.fromisoformat(snapshot_date)).days
        if dte < 0:
            continue
        prices = signals_by_date[snapshot_date]
        if not all(l["contract_symbol"] in prices for l in legs):
            continue
        price_lookup = {l["contract_symbol"]: prices[l["contract_symbol"]] for l in legs}

        result = evaluator(legs, price_lookup, dte, width, **overrides)
        if result is not None:
            status, realized_pct = result
            return status, snapshot_date, realized_pct
        if dte == 0:
            result = _expire(legs, price_lookup, structure_type)
            if result is None:
                return "UNRESOLVED_AT_EXPIRATION", snapshot_date, None
            status, realized_pct = result
            return status, snapshot_date, realized_pct

    # Expiration has passed and every leg was never priced on the
    # expiration day itself: there is no expiry result to record. Until
    # 17 Nov 2026 this fell back to the last day all legs HAD a price and
    # called that EXPIRED_PROFIT / EXPIRED_LOSS -- but that day was 3 to
    # 43 days before expiry for all six trades it ever applied to (one
    # iron condor was marked 4 days after entry), so those were early
    # marks, not results, and they counted in the win rates. Known cost:
    # a trade that genuinely runs to expiry with a leg that has no bid on
    # the last day is left unscored rather than counted as a win.
    if date.fromisoformat(nearest_expiration) < today:
        return "UNRESOLVED_AT_EXPIRATION", nearest_expiration, None

    return "OPEN", None, None


def priced_entry_legs(strategy, legs, signals_by_date, entry_date):
    """The trade's legs re-priced at the entry day's midpoints, or None if
    the entry cannot be priced under pricing.py's rule: a leg has no real
    two-sided quote that day, or the legs' midpoints give no positive net
    credit/debit (so there was no trade to enter).

    Entry and every later valuation therefore sit on the same basis. The
    price stored in the ledger's rec: cell is what was shown at the time
    (a last price for trades recommended before 2026-11-17, the midpoint
    after) and is kept as the record, but it is not used for results."""
    prices = signals_by_date.get(entry_date, {})
    if not all(l["contract_symbol"] in prices for l in legs):
        return None
    repriced = [dict(l, entry_price=prices[l["contract_symbol"]]) for l in legs]
    basis = _credit_received(repriced) if STRUCTURE_TYPE[strategy] == "credit" else _debit_paid(repriced)
    return repriced if basis > 0 else None


def _load_all_signals():
    """{date_str: {contract_symbol: midpoint}} for every signals.csv
    currently in the repo -- only contracts with a real bid and ask (see
    pricing.py). evaluate_trade skips any day on which a leg is missing,
    so an unquoted leg simply means the trade is not valued that day."""
    result = {}
    if not SIGNALS_DIR.exists():
        return result
    for f in sorted(SIGNALS_DIR.glob("*.csv")):
        df = pd.read_csv(f, usecols=["contract_symbol", "bid", "ask"])
        result[f.stem] = price_lookup(df, f.stem)
    return result


def _load_underlying_prices():
    """{date_str: {symbol: underlying_price}} from every signals file."""
    result = {}
    if not SIGNALS_DIR.exists():
        return result
    for f in sorted(SIGNALS_DIR.glob("*.csv")):
        df = pd.read_csv(f, usecols=["symbol", "underlying_price"]).dropna()
        result[f.stem] = df.groupby("symbol")["underlying_price"].first().to_dict()
    return result


def _entry_info_for_trade(trade_rows):
    """trade_rows: every ledger row sharing one trade_id. Returns
    (entry_date, legs) -- legs is [] if entry pricing can't be recovered
    (e.g. a malformed rec: cell)."""
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


def git_pull():
    result = subprocess.run(["git", "pull"], cwd=PROJECT_DIR, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"git pull failed: {result.stderr}")
    return result.stdout.strip()


def commit_and_push(paths, message):
    paths = [str(p) for p in paths]
    subprocess.run(["git", "add", *paths], cwd=PROJECT_DIR, check=True, timeout=60)
    diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=PROJECT_DIR, timeout=30)
    if diff.returncode == 0:
        return "no_changes"
    subprocess.run(["git", "commit", "-m", message], cwd=PROJECT_DIR, check=True, timeout=60)
    subprocess.run(["git", "push"], cwd=PROJECT_DIR, check=True, timeout=120)
    return "pushed"


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
    underlying_by_date = _load_underlying_prices()
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
            entry_date, legs = _entry_info_for_trade(trade_rows)
            if not legs:
                print(f"{trade_id}: no recoverable entry legs -- skipping")
                continue
            entry_legs = priced_entry_legs(strategy, legs, signals_by_date, entry_date)
            if entry_legs is None:
                status, outcome_date, realized_pct = "ENTRY_NOT_PRICEABLE", entry_date, None
            else:
                overrides = None
                if strategy == "short calendar":
                    symbol = trade_rows[0]["symbol"]
                    margin = short_calendar_margin(symbol, entry_legs, underlying_by_date.get(entry_date, {}).get(symbol))
                    if margin is None:
                        print(f"{trade_id}: no underlying price on {entry_date} -- stop measured on the credit instead of margin")
                    overrides = {"margin": margin}
                status, outcome_date, realized_pct = evaluate_trade(strategy, entry_legs, signals_by_date, today,
                                                                    evaluator_overrides=overrides, entry_date=entry_date)
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
