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
