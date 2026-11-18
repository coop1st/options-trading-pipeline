"""Replay: gate A (net price >= full quote width of the legs) plus a profit
target of max(5% of net price, cost of trading), where cost of trading =
the legs' full bid-ask width at entry (half paid going in, half coming out).
Three rules compared: old (5% target), floor (target floor only), both (same floor on the stop too). Read-only. Run: python studies/target_floor_replay.py"""
import csv, sys
from collections import defaultdict
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline")); sys.path.insert(0, str(ROOT / "studies"))
from exit_rule_study import load_quotes, path, half_width
from track_outcomes import (LEDGER_PATH, STRUCTURE_TYPE, _entry_info_for_trade, _load_underlying_prices,
                            short_calendar_margin)
quotes = load_quotes(); dates = sorted(quotes); und = _load_underlying_prices()
by = defaultdict(list)
for r in csv.DictReader(open(LEDGER_PATH, newline="", encoding="utf-8")):
    by[r["trade_id"]].append(r)
out = []
for tid, trs in by.items():
    s = trs[0]["strategy"]
    if s not in ("short calendar", "long calendar", "double diagonal"):
        continue
    ed, legs = _entry_info_for_trade(trs)
    if ed not in quotes or not all(l["contract_symbol"] in quotes[ed] for l in legs):
        continue
    credit = STRUCTURE_TYPE[s] == "credit"
    base, p = path(legs, quotes, dates, ed, credit)
    if base <= 0:
        continue
    cost = 2 * half_width(legs, quotes[ed])
    if base < cost:
        continue  # gate A
    q = quotes[ed]
    el = [dict(l, entry_price=sum(q[l["contract_symbol"]]) / 2) for l in legs]
    stop = 0.10 * base
    if s == "short calendar":
        m = short_calendar_margin(trs[0]["symbol"], el, und.get(ed, {}).get(trs[0]["symbol"]))
        stop = 0.10 * (m or base)
    for label, tgt, stp in (("old", 0.05 * base, stop), ("floor", max(0.05 * base, cost), stop),
                            ("both", max(0.05 * base, cost), max(stop, cost))):
        res = None
        for n, d, dte, pct, dol, hw in p:
            if dol >= tgt: res = ("TARGET", n, pct, dol); break
            if -dol >= stp: res = ("STOP", n, pct, dol); break
            if dte == 0: res = ("EXPIRY", n, pct, dol); break
        out.append(dict(tid=tid, strategy=s, rule=label, base=base, cost=cost,
                        exit=res[0] if res else "OPEN", days=res[1] if res else None,
                        pct=res[2] if res else None, net_pct=(res[3] - cost) / base if res else None))
df = pd.DataFrame(out)
print("trades passing gate A:", df.tid.nunique())
for (s, rule), g in df.groupby(["strategy", "rule"]):
    r = g[g.exit != "OPEN"]
    print(f"{s:16s} {rule:5s} n={len(g):3d} {g.exit.value_counts().to_dict()}  resolved {len(r)}: "
          f"midpoint win {(r.pct>0).mean():.0%} avg {r.pct.mean():+.1%} | after cost win {(r.net_pct>0).mean():.0%} avg {r.net_pct.mean():+.1%}  median days {r.days.median():.0f}")
