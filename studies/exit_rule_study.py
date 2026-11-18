"""
Exit-rule study for calendars and double diagonals (18 Nov 2026).

Read-only: reads the ledger and the signals files, writes two CSVs beside
this script. Changes nothing in the pipeline. Run from the repo root:
    python studies/exit_rule_study.py
"""
import csv
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))
from pricing import NON_MARKET_DAYS  # noqa: E402
from track_outcomes import (  # noqa: E402
    LEDGER_PATH, SIGNALS_DIR, STRUCTURE_TYPE, _entry_info_for_trade,
)

STRATS = ("short calendar", "long calendar", "double diagonal")
TARGET, STOP = 0.05, 0.10
OUT = Path(__file__).resolve().parent


def load_quotes():
    """{date: {contract: (bid, ask)}} for two-sided quotes only."""
    out = {}
    for f in sorted(SIGNALS_DIR.glob("*.csv")):
        if f.stem in NON_MARKET_DAYS:
            continue
        df = pd.read_csv(f, usecols=["contract_symbol", "bid", "ask"])
        df = df[(df.bid > 0) & (df.ask >= df.bid)]
        out[f.stem] = dict(zip(df.contract_symbol, zip(df.bid, df.ask)))
    return out


def sign(leg, credit):
    s = 1 if leg["leg_role"].startswith("short") else -1
    return s if credit else -s


def net(legs, q, credit):
    """Net price at midpoints: credit received / cost to close for credit
    trades, debit paid / current value for debit trades."""
    return sum(sign(l, credit) * (q[l["contract_symbol"]][0] + q[l["contract_symbol"]][1]) / 2 for l in legs)


def half_width(legs, q):
    return sum((q[l["contract_symbol"]][1] - q[l["contract_symbol"]][0]) / 2 for l in legs)


def path(legs, quotes, dates, entry_date, credit):
    """[(trading_days_since_entry, date, front_dte, pnl_pct, pnl_dollars, half_width)]
    for every later day on which all legs are quoted, up to front expiry."""
    q0 = quotes[entry_date]
    base = net(legs, q0, credit)
    if base <= 0:
        return base, []
    front = min(l["expiration"] for l in legs)
    i0 = dates.index(entry_date)
    out = []
    for i in range(i0 + 1, len(dates)):
        d = dates[i]
        dte = (date.fromisoformat(front) - date.fromisoformat(d)).days
        if dte < 0:
            break
        q = quotes[d]
        if not all(l["contract_symbol"] in q for l in legs):
            continue
        now = net(legs, q, credit)
        pnl = (base - now) if credit else (now - base)
        out.append((i - i0, d, dte, pnl / base, pnl, half_width(legs, q)))
    return base, out


def run_rule(p, skip_days=0, last_week=False):
    """First exit under the 5% / 10% rule, ignoring the first skip_days
    trading days. last_week: no rule at all, mark at the first priced day
    with 7 or fewer days left on the front leg."""
    for n, d, dte, pct, dollars, hw in p:
        if last_week:
            if dte <= 7:
                return ("LAST_WEEK_MARK", n, d, pct, dollars, hw)
            continue
        if n <= skip_days:
            continue
        if pct >= TARGET:
            return ("TARGET", n, d, pct, dollars, hw)
        if -pct >= STOP:
            return ("STOP", n, d, pct, dollars, hw)
    return None


def main():
    quotes = load_quotes()
    dates = sorted(quotes)
    rows = list(csv.DictReader(open(LEDGER_PATH, newline="", encoding="utf-8")))
    by_id = defaultdict(list)
    for r in rows:
        by_id[r["trade_id"]].append(r)

    trades = []
    for tid, trs in by_id.items():
        strat = trs[0]["strategy"]
        if strat not in STRATS:
            continue
        entry_date, legs = _entry_info_for_trade(trs)
        if entry_date not in quotes or not all(l["contract_symbol"] in quotes[entry_date] for l in legs):
            continue
        credit = STRUCTURE_TYPE[strat] == "credit"
        base, p = path(legs, quotes, dates, entry_date, credit)
        if base <= 0:
            continue
        q0 = quotes[entry_date]
        mids = [(q0[l["contract_symbol"]][0] + q0[l["contract_symbol"]][1]) / 2 for l in legs]
        exps = sorted({l["expiration"] for l in legs})
        t = {
            "trade_id": tid, "symbol": trs[0]["symbol"], "strategy": strat,
            "entry_date": entry_date, "ledger_status": trs[0]["outcome_status"],
            "ledger_pct": trs[0]["realized_pct"],
            "base": round(base, 4), "largest_leg": round(max(mids), 4),
            "base_share_of_largest_leg": round(base / max(mids), 4),
            "entry_half_width": round(half_width(legs, q0), 4),
            "front_dte_at_entry": (date.fromisoformat(exps[0]) - date.fromisoformat(entry_date)).days,
            "gap_days_between_legs": (date.fromisoformat(exps[-1]) - date.fromisoformat(exps[0])).days,
            "priced_days": len(p),
        }
        for label, kw in (("now", {}), ("skip2", {"skip_days": 2}), ("skip3", {"skip_days": 3}),
                          ("skip5", {"skip_days": 5}), ("lastweek", {"last_week": True})):
            r = run_rule(p, **kw)
            if r:
                t.update({f"{label}_exit": r[0], f"{label}_days": r[1], f"{label}_date": r[2],
                          f"{label}_pct": round(r[3], 4), f"{label}_dollars": round(r[4], 4),
                          f"{label}_half_width": round(r[5], 4)})
            else:
                t.update({f"{label}_exit": "", f"{label}_days": "", f"{label}_date": "",
                          f"{label}_pct": "", f"{label}_dollars": "", f"{label}_half_width": ""})
        trades.append(t)

    df = pd.DataFrame(trades)
    df.to_csv(OUT / "exit_rule_study_trades.csv", index=False)
    pd.set_option("display.width", 250, "display.max_columns", 40, "display.max_rows", 200)
    df["grp"] = df.symbol.where(df.symbol == "^SPX", "other")

    print(f"Signals days: {len(dates)} ({dates[0]} to {dates[-1]}). Trades priceable at entry: {len(df)}")
    print("\n== 0. Cross-check against the ledger (study 'now' rule vs tracker) ==")
    ex = df[df.now_exit != ""]
    led = df[df.ledger_status.isin(["HIT_TARGET", "HIT_MAX_LOSS"])]
    print("study exits:", len(ex), "| ledger target/stop:", len(led))
    m = df[(df.now_exit != "") | df.ledger_status.isin(["HIT_TARGET", "HIT_MAX_LOSS"])].copy()
    m["led"] = m.ledger_status.map({"HIT_TARGET": "TARGET", "HIT_MAX_LOSS": "STOP"}).fillna("")
    bad = m[(m.led != m.now_exit) | ((pd.to_numeric(m.ledger_pct, errors="coerce") - pd.to_numeric(m.now_pct, errors="coerce")).abs() > 0.0002)]
    print("mismatches:", len(bad))
    if len(bad):
        print(bad[["trade_id", "strategy", "ledger_status", "ledger_pct", "now_exit", "now_pct", "now_date"]].to_string())

    ex = ex.copy()
    ex["now_days"] = ex.now_days.astype(int)
    for c in ("now_pct", "now_dollars", "now_half_width"):
        ex[c] = ex[c].astype(float)

    print("\n== 1. Days from entry to exit ==")
    for (s, e), g in ex.groupby(["strategy", "now_exit"]):
        d = g.now_days
        print(f"{s:16s} {e:6s} n={len(g):3d}  within 1 day: {(d<=1).sum():3d}  2: {(d<=2).sum():3d}  5: {(d<=5).sum():3d}  median days {d.median():.0f}  max {d.max()}")
    print("-- by strategy, all exits --")
    for s, g in ex.groupby("strategy"):
        d = g.now_days
        print(f"{s:16s} n={len(g):3d}  1 day: {(d<=1).mean():.0%}  <=2: {(d<=2).mean():.0%}  <=5: {(d<=5).mean():.0%}")
    print("-- ^SPX vs other --")
    for (s, gname), g in ex.groupby(["strategy", "grp"]):
        d = g.now_days
        print(f"{s:16s} {gname:5s} n={len(g):3d}  1 day: {(d<=1).sum():3d}  <=2: {(d<=2).sum():3d}  win {(g.now_pct>0).mean():.0%}  avg {g.now_pct.mean():+.1%}  median {g.now_pct.median():+.1%}")

    print("\n== 2. Size of the base (all priceable trades) ==")
    for (s, gname), g in df.groupby(["strategy", "grp"]):
        print(f"{s:16s} {gname:5s} n={len(g):3d}  net price median ${g.base.median():.2f} (min ${g.base.min():.3f}, max ${g.base.max():.2f})  "
              f"share of largest leg median {g.base_share_of_largest_leg.median():.0%}  "
              f"5% target = ${g.base.median()*TARGET:.3f}  10% stop = ${g.base.median()*STOP:.3f}  entry half-width median ${g.entry_half_width.median():.2f}  "
              f"gap between legs median {g.gap_days_between_legs.median():.0f}d")
    print("-- net price bands, exited trades --")
    ex["band"] = pd.cut(ex.base, [0, 0.10, 0.25, 0.50, 1, 5, 1000], labels=["<=0.10", "0.10-0.25", "0.25-0.50", "0.50-1", "1-5", ">5"])
    for (s, b), g in ex.groupby(["strategy", "band"], observed=True):
        print(f"{s:16s} {str(b):10s} n={len(g):3d}  1-day exits {(g.now_days<=1).mean():.0%}  win {(g.now_pct>0).mean():.0%}  avg {g.now_pct.mean():+.1%}  worst {g.now_pct.min():+.0%}  best {g.now_pct.max():+.0%}")

    print("\n== 3. Was the exit move bigger than the quote width? ==")
    ex["inside_exit_hw"] = ex.now_dollars.abs() <= ex.now_half_width
    ex["threshold_dollars"] = ex.base * ex.now_exit.map({"TARGET": TARGET, "STOP": STOP})
    ex["threshold_inside_hw"] = ex.threshold_dollars <= ex.now_half_width
    for (s, gname), g in ex.groupby(["strategy", "grp"]):
        print(f"{s:16s} {gname:5s} n={len(g):3d}  move inside exit-day half-width: {g.inside_exit_hw.sum():3d} ({g.inside_exit_hw.mean():.0%})  "
              f"threshold itself smaller than half-width: {g.threshold_inside_hw.sum():3d} ({g.threshold_inside_hw.mean():.0%})  "
              f"median move ${g.now_dollars.abs().median():.2f} vs median half-width ${g.now_half_width.median():.2f}")
    fast = ex[ex.now_days <= 2]
    print(f"fast exits (<=2 days): {len(fast)}; move inside half-width: {fast.inside_exit_hw.sum()} ({fast.inside_exit_hw.mean():.0%}); threshold smaller than half-width: {fast.threshold_inside_hw.sum()} ({fast.threshold_inside_hw.mean():.0%})")
    print("-- result if half the quote width is paid on entry and on exit --")
    ex["pct_after_cost"] = (ex.now_dollars - ex.entry_half_width - ex.now_half_width) / ex.base
    for s, g in ex.groupby("strategy"):
        print(f"{s:16s} n={len(g):3d}  at midpoint: win {(g.now_pct>0).mean():.0%} avg {g.now_pct.mean():+.1%}   paying half width both ways: win {(g.pct_after_cost>0).mean():.0%} avg {g.pct_after_cost.mean():+.0%} median {g.pct_after_cost.median():+.0%}")

    print("\n== 4. Hold-longer replay (same trades that have exited today) ==")
    ids = set(ex.trade_id)
    sub = df[df.trade_id.isin(ids)]
    for (s, gname), g in list(sub.groupby(["strategy", "grp"])) + [((s, "ALL"), g) for s, g in sub.groupby("strategy")]:
        print(f"-- {s} / {gname} (n={len(g)}) --")
        for label in ("now", "skip2", "skip3", "skip5", "lastweek"):
            r = g[g[f"{label}_exit"] != ""]
            pct = r[f"{label}_pct"].astype(float)
            days = r[f"{label}_days"].astype(float)
            if len(r) == 0:
                print(f"   {label:9s} resolved 0/{len(g)}")
                continue
            print(f"   {label:9s} resolved {len(r):3d}/{len(g):3d}  win {(pct>0).mean():.0%}  avg {pct.mean():+.1%}  median {pct.median():+.1%}  worst {pct.min():+.0%}  best {pct.max():+.0%}  median days {days.median():.0f}")

    ex.drop(columns=["grp"]).to_csv(OUT / "exit_rule_study_exits.csv", index=False)


if __name__ == "__main__":
    main()
