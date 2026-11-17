"""
Merge + score (component C). Runs unattended in GitHub Actions straight
after each close snapshot lands (.github/workflows/score-and-screen.yml),
and still runs by hand on the PC as a fallback.

1. git pull to get the latest raw snapshots.
2. Load the published IV/skew history (data/github_sync/iv_history/) into
   the database, so a machine starting from an empty database -- a cloud
   runner -- has everything scoring needs.
3. Work out every trading day that has a snapshot but no signals file yet
   (not just the newest), and for each, oldest first: merge that day's
   snapshot into the database, compute Greeks, liquidity flags and IV/skew
   reads, write data/github_sync/signals/{date}.csv and that day's
   iv_history file.
4. Commit + push.

Scoring every unscored day -- rather than only the newest -- is what
stops a missed night from losing that day for good: the next run picks
it up. (Before 2026-11-16 only the newest day was scored, and two thirds
of all trading days were lost.)

Run from the repo root: `python pipeline/merge_and_score.py [--rescore-all]`
"""
import sys
from datetime import date, datetime
from zoneinfo import ZoneInfo

import pandas as pd

import iv_history
from config import (
    ATM_MAX_MONEYNESS_GAP, ATM_MAX_TRADE_AGE_DAYS, ATM_STRIKES_USED,
    MIN_OPEN_INTEREST, MIN_VOLUME, PROJECT_DIR, RISK_FREE_RATE, SKEW_DELTA_TARGET,
)
from db import (
    delete_history_for_date,
    get_atm_iv_history,
    get_snapshot_rows,
    init_db,
    is_merged,
    mark_merged,
    upsert_atm_iv_history,
    upsert_options_chain,
    upsert_skew_history,
)
from greeks import compute_greeks
from publish import commit_and_push, git_pull

SNAPSHOTS_DIR = PROJECT_DIR / "data" / "github_sync" / "options_snapshots"
SIGNALS_DIR = PROJECT_DIR / "data" / "github_sync" / "signals"
TIMES_DIR = PROJECT_DIR / "data" / "github_sync" / "snapshot_times"
SESSION_PREFERENCE = ("close", "preclose", "mid", "open")
MARKET_TZ = ZoneInfo("America/New_York")
WELL_TIMED_FROM, WELL_TIMED_TO = 9.75, 17.0  # New York clock hours


def snapshot_sessions():
    """{date_str: set of sessions} for every snapshot CSV in the repo."""
    sessions = {}
    if SNAPSHOTS_DIR.exists():
        for f in SNAPSHOTS_DIR.glob("*.csv"):
            stem_date, session = f.stem.rsplit("_", 1)
            sessions.setdefault(stem_date, set()).add(session)
    return sessions


def capture_times():
    """{(date_str, session): aware UTC datetime} from
    data/github_sync/snapshot_times/{date}_{session}.txt -- when each
    snapshot was really captured. The files' names only say which cron
    asked for them; GitHub starts those crons hours late, so a "close"
    file is typically captured 2.5-5.5 hours after the close."""
    times = {}
    if TIMES_DIR.exists():
        for f in TIMES_DIR.glob("*.txt"):
            try:
                stem_date, session = f.stem.rsplit("_", 1)
                times[(stem_date, session)] = datetime.fromisoformat(f.read_text(encoding="utf-8").strip())
            except ValueError:
                continue
    return times


def best_quoted_session(snapshot_date, sessions, times):
    """Which of a day's snapshots to price from.

    Quotes are only good while the market is open or just after: measured
    on Oct-Nov 2026, snapshots captured during market hours or within an
    hour of the close had a real bid and ask on 86% of liquid contracts,
    6-7% wide; later captures were 15-17% wide and some had lost half
    their quotes. So: among the snapshots captured ON the trading day
    between 09:45 and 17:00 New York, take the one captured closest to
    the 16:00 close -- but one captured in the last hour of trading
    (15:00 to 16:00) always beats one captured after the market shut.
    If none was in the window (or capture times are unknown), fall back
    to the old preference close > mid > open and say so.

    Why the last hour first (added 17 Nov 2026, when the close fetch began to
    be started on time at about 16:10): quotes decay quickly once
    trading stops. Measured on 17 Nov 2026, contracts with open interest
    of 100 or more: captured 15:28 New York 77% had a real two-sided
    quote, median 9% wide; 16:53, 74% and 13%; 17:27, 49% and 21%.
    Without this, a 16:10 "close" capture would sit nearer 16:00 than a
    15:10 "preclose" one and would quietly become the pricing source.
    An earlier in-hours capture (say 14:10) does NOT outrank a 16:10
    one: two hours of market movement matters more than the small loss
    of quote quality in the first minutes after the close.

    Returns (session, well_timed: bool). The window and the last-hour
    preference are the project's own operationalization of the
    measurements above, not a book rule."""
    candidates = []
    for session in sessions:
        ts = times.get((snapshot_date, session))
        if ts is None:
            continue
        ny = ts.astimezone(MARKET_TZ)
        hour = ny.hour + ny.minute / 60
        if ny.date().isoformat() == snapshot_date and WELL_TIMED_FROM <= hour <= WELL_TIMED_TO:
            last_hour = 15.0 <= hour <= 16.0
            candidates.append((not last_hour, abs(hour - 16.0), session))
    if candidates:
        return min(candidates)[2], True
    for session in SESSION_PREFERENCE:
        if session in sessions:
            return session, False
    return None, False


def select_dates_to_score(sessions_by_date, scored_dates, times=None, rescore_all=False):
    """Pure decision: which days to score now, and from which session.
    Returns [(date_str, session)], oldest first.

    WHEN a day is scored: once its close snapshot exists (the day is
    over), or -- if the close fetch failed -- once a LATER day's
    snapshots exist. The newest day is never scored before its close has
    landed, so a half-finished day is not published.

    FROM WHICH snapshot: best_quoted_session -- the one with the best
    quotes, which is usually not the one labelled "close".

    rescore_all=True returns every day, scored or not (used once after a
    change to the session rule)."""
    scored_dates = set() if rescore_all else set(scored_dates)
    times = times or {}
    newest = max(sessions_by_date) if sessions_by_date else None
    chosen = []
    for snapshot_date in sorted(sessions_by_date):
        if snapshot_date in scored_dates:
            continue
        sessions = sessions_by_date[snapshot_date]
        if "close" not in sessions and snapshot_date == newest:
            continue
        session, _well_timed = best_quoted_session(snapshot_date, sessions, times)
        if session is not None:
            chosen.append((snapshot_date, session))
    return chosen


def merge_snapshot_file(snapshot_date, session):
    """Upserts one snapshot CSV into the database (tracked via merge_log,
    so re-running is a harmless no-op). Only the files a run actually
    needs are merged -- the database is a working area, not an archive;
    the snapshot CSVs in the repo are the record. Returns rows merged."""
    f = SNAPSHOTS_DIR / f"{snapshot_date}_{session}.csv"
    if is_merged(f.name):
        return 0
    df = pd.read_csv(f)
    if df.empty:
        mark_merged(f.name, 0)
        return 0
    df["snapshot_date"] = snapshot_date
    df["session"] = session
    upsert_options_chain(df.to_dict("records"))
    mark_merged(f.name, len(df))
    return len(df)


def live_quote_flags(df, snapshot_date):
    """True for each contract whose implied volatility can be trusted as
    a reading: a real two-sided quote (bid above zero, ask above bid)
    that is not wide (the same test as the wide_spread flag: spread over
    half the ask), a positive implied volatility, and a trade within
    ATM_MAX_TRADE_AGE_DAYS calendar days of the snapshot.

    The trade-recency test is what catches a dead strike that still
    shows a quote: on 17 Nov 2026 BABA's 15-Jan-2027 87.5 call showed
    42.15 / 43.00 with the stock at 86.66 and had last traded in May
    2025. (Pricing a trade's own legs is a different matter and needs
    only the bid and ask -- pipeline/pricing.py.)"""
    bid = pd.to_numeric(df["bid"], errors="coerce")
    ask = pd.to_numeric(df["ask"], errors="coerce")
    iv = pd.to_numeric(df["implied_volatility"], errors="coerce")
    two_sided = (bid > 0) & (ask > bid)
    not_wide = ((ask - bid) / ask.where(ask > 0)) <= 0.5
    traded = pd.to_datetime(df["last_trade_date"], errors="coerce", utc=True)
    as_of = pd.Timestamp(snapshot_date, tz="UTC") + pd.Timedelta(days=1)  # end of the snapshot day
    recent = (as_of - traded) <= pd.Timedelta(days=ATM_MAX_TRADE_AGE_DAYS + 1)
    return (two_sided & not_wide.fillna(False) & (iv > 0) & recent.fillna(False)).astype(bool)


def _atm_iv(group, underlying_price):
    """The at-the-money implied volatility for one (symbol, expiration)
    group: the median, over the ATM_STRIKES_USED live strikes nearest the
    underlying price, of each strike's average call/put implied
    volatility. Only contracts flagged `live_quote` count, and no strike
    further than ATM_MAX_MONEYNESS_GAP from the underlying is used.
    Returns None when no live strike is close enough -- no reading is
    better than a wrong one (the expiry then gets no IV percentile and
    fails the gates that need one).

    Until 17 Nov 2026 this was the single nearest strike with no check
    on its quote, so one dead strike could set the whole expiry's
    reading."""
    if underlying_price is None or not underlying_price > 0:
        return None
    live = group[group["live_quote"]]
    if live.empty:
        return None
    per_strike = live.groupby("strike")["implied_volatility"].mean()
    gap = (per_strike.index.to_series() / underlying_price - 1).abs()
    nearest = gap[gap <= ATM_MAX_MONEYNESS_GAP].nsmallest(ATM_STRIKES_USED)
    if nearest.empty:
        return None
    return float(per_strike.loc[nearest.index].median())


def compute_signals(rows, snapshot_date):
    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame()

    # Greeks (component C step 4). Isolated per-row (mirrors Stocks'
    # run_stage_safely() convention per the design spec) so one malformed
    # input (e.g. a zero/negative strike, a bad date) can't crash the
    # whole run -- it falls back to None Greeks for that row instead.
    greek_cols = {"delta": [], "gamma": [], "theta": [], "vega": [], "rho": []}
    greek_failures = 0
    for _, r in df.iterrows():
        try:
            days_to_exp = (date.fromisoformat(r["expiration"]) - date.fromisoformat(snapshot_date)).days
            g = compute_greeks(
                r["underlying_price"], r["strike"], days_to_exp,
                r["implied_volatility"], r["type"], RISK_FREE_RATE,
            )
        except Exception as exc:
            greek_failures += 1
            print(f"Greeks computation failed for {r.get('contract_symbol')!r}: {exc}")
            g = {"delta": None, "gamma": None, "theta": None, "vega": None, "rho": None}
        for k in greek_cols:
            greek_cols[k].append(g[k])
    for k, v in greek_cols.items():
        df[k] = v
    if greek_failures:
        print(f"Greeks computation: {greek_failures} failed of {len(df)} rows")

    # Liquidity flags (component C step 5)
    df["low_liquidity"] = (df["volume"] < MIN_VOLUME) | (df["open_interest"] < MIN_OPEN_INTEREST)
    # Data-quality flags surfaced (but not filtered) per the exploration
    # spike's findings -- near-zero bid/ask and wide spreads make a
    # contract's IV/Greeks unreliable even when it's otherwise liquid
    # enough to pass the volume/OI filter above.
    df["zero_bid"] = df["bid"] <= 0
    ask_for_spread = df["ask"].where(df["ask"] > 0)
    spread_pct = (df["ask"] - df["bid"]) / ask_for_spread
    df["wide_spread"] = (df["bid"] > 0) & (spread_pct > 0.5).fillna(False)

    # IV / skew reads (component C step 6). Only contracts with a live
    # quote are read (live_quote_flags). This day's history rows are
    # rebuilt from scratch, so a reading that no longer qualifies does
    # not linger from an earlier scoring of the same day.
    df["live_quote"] = live_quote_flags(df, snapshot_date)
    delete_history_for_date(snapshot_date)
    df["atm_iv"] = None
    df["atm_iv_90d_percentile"] = None
    df["skew_put_pct_of_atm"] = None
    df["skew_call_pct_of_atm"] = None
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
                side = group[(group["type"] == opt_type) & group["delta"].notna() & group["live_quote"]]
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

    signals = df[~df["low_liquidity"]].copy()
    out_cols = [
        "symbol", "expiration", "contract_symbol", "type", "strike",
        "last_price", "bid", "ask", "volume", "open_interest",
        "implied_volatility", "underlying_price",
        "delta", "gamma", "theta", "vega", "rho",
        "atm_iv", "atm_iv_90d_percentile",
        "skew_put_pct_of_atm", "skew_call_pct_of_atm",
        "last_trade_date", "zero_bid", "wide_spread",
    ]
    return signals[out_cols].sort_values(["symbol", "expiration", "type", "strike"])


def scored_dates():
    return {f.stem for f in SIGNALS_DIR.glob("*.csv")} if SIGNALS_DIR.exists() else set()


def run_merge_and_score(rescore_all=False):
    print("Pulling latest from GitHub...")
    print(git_pull())

    # Days scored on this machine before iv_history/ existed get their
    # file published; then everything published is loaded, so both the PC
    # and a fresh cloud runner score against the same history.
    published = iv_history.export_missing()
    if published:
        print(f"Published IV history for {len(published)} previously scored day(s)")
    print(f"Loaded IV history for {iv_history.load_into_db()} day(s)")

    times = capture_times()
    todo = select_dates_to_score(snapshot_sessions(), scored_dates(), times, rescore_all=rescore_all)
    if not todo:
        print("Every day with a snapshot is already scored -- nothing to do")
        status = "no_changes"
        if published:
            status = commit_and_push([iv_history.IV_HISTORY_DIR], "IV history: publish previously scored days")
        return {"status": status, "scored": [], "failed": []}

    SIGNALS_DIR.mkdir(parents=True, exist_ok=True)
    scored, failed, out_paths = [], [], []
    for target_date, session in todo:
        try:
            merged = merge_snapshot_file(target_date, session)
            rows = get_snapshot_rows(target_date, session)
            if not rows:
                raise RuntimeError(f"snapshot file for the '{session}' session has no rows")
            ts = times.get((target_date, session))
            captured = ts.astimezone(MARKET_TZ).strftime("%a %H:%M New York") if ts else "time unknown"
            well_timed = best_quoted_session(target_date, {session}, times)[1]
            note = "" if well_timed else "  (NOT captured near market hours -- quotes will be thinner)"
            print(f"Scoring {len(rows)} contracts from {target_date}'s '{session}' snapshot, captured {captured} "
                  f"({merged} rows newly merged)...{note}")
            signals = compute_signals(rows, target_date)
            if signals.empty:
                raise RuntimeError("no contract passed the liquidity filter -- snapshot looks broken")
            out_path = SIGNALS_DIR / f"{target_date}.csv"
            signals.to_csv(out_path, index=False)
            out_paths.append(out_path)
            iv_history.export_date(target_date)
            scored.append((target_date, len(signals)))
            print(f"Wrote {len(signals)} signal rows to {out_path}")
        except Exception as exc:
            # One bad day must not block the others; it stays unscored and
            # is retried on the next run. The run still exits non-zero so
            # the failure is visible (a failed GitHub Actions run emails).
            failed.append(target_date)
            print(f"FAILED to score {target_date}: {exc}")

    status = "no_changes"
    if scored:
        if len(scored) == 1:
            message = f"Options signals: {scored[0][0]} ({scored[0][1]} contracts)"
        else:
            message = f"Options signals: {len(scored)} days, {scored[0][0]} to {scored[-1][0]}"
        status = commit_and_push(out_paths + [iv_history.IV_HISTORY_DIR], message)
    print(f"Publish status: {status}")
    return {"status": status, "scored": [d for d, _ in scored], "failed": failed}


if __name__ == "__main__":
    init_db()
    result = run_merge_and_score(rescore_all="--rescore-all" in sys.argv[1:])
    print(result)
    if result["failed"]:
        sys.exit(1)
