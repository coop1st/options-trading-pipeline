"""
Verifies the 17 Oct 2026 strategy-builder fixes:
1. an iron condor's max loss uses the WIDER wing (true max loss of an
   asymmetric condor), not the narrower one;
2. no candidate mixes option roots (^SPX's AM-settled SPX and
   PM-settled SPXW series share expiration dates but settle differently);
3. a spread whose credit >= its width (only possible from stale
   last_price prints) is rejected as impossible;
4. score_and_rank never publishes a candidate sized at 0 contracts.
No pytest in this repo -- run directly and inspect output, same
convention as verify_greeks.py.

Run: python pipeline/verify_strategy_rules.py
"""
import re
import sys

import pandas as pd

import screen_trades
from strategy_rules import (
    build_calendars, build_double_diagonals, build_iron_condors, build_vertical_credit_spreads,
)

SNAPSHOT = "2026-10-16"
EXP = "2026-12-18"
EXP2 = "2027-01-15"


def _row(root, exp, opt_type, strike, delta, price, symbol="^SPX"):
    yymmdd = exp[2:4] + exp[5:7] + exp[8:10]
    return {
        "symbol": symbol, "contract_symbol": f"{root}{yymmdd}{opt_type[0].upper()}{int(strike * 1000):08d}",
        "expiration": exp, "type": opt_type, "strike": float(strike), "delta": delta,
        "last_price": price, "bid": price - 0.05, "ask": price + 0.05, "volume": 500, "open_interest": 1000,
        "atm_iv": 0.20, "atm_iv_90d_percentile": 50.0, "skew_put_pct_of_atm": 150.0,
        "skew_call_pct_of_atm": 90.0, "zero_bid": False, "wide_spread": False,
    }


def _roots(candidate):
    return {re.match(r"^([A-Z]+)\d", leg["contract_symbol"]).group(1) for leg in candidate["legs"]}


def check(label, condition):
    print(f"{'OK' if condition else 'FAIL'}: {label}")
    return condition


def condor_chain(put_wing_strike, long_put_price=1.0):
    # short call 110 (d .12), long call 120; short put 90 (d -.12), long put at put_wing_strike
    return pd.DataFrame([
        _row("TEST", EXP, "call", 110, 0.12, 2.0, "TEST"),
        _row("TEST", EXP, "call", 120, 0.05, 1.0, "TEST"),
        _row("TEST", EXP, "put", 90, -0.12, 2.0, "TEST"),
        _row("TEST", EXP, "put", put_wing_strike, -0.04, long_put_price, "TEST"),
    ])


def main():
    ok = True
    no_atr = lambda s: None

    # 1. asymmetric condor: call wing 10, put wing 40, credit 2.0 -> max loss (40 - 2) * 100
    c = build_iron_condors(condor_chain(50), SNAPSHOT, no_atr, 45, 75, 0.10, 0.15, {})
    ok &= check("asymmetric condor built", len(c) == 1)
    if c:
        ok &= check(f"condor max_loss uses wider wing (got {c[0]['max_loss']}, want 3800)",
                    abs(c[0]["max_loss"] - 3800) < 1e-6)

    # 3. stale long-put print: put spread 90/80 'collects' 2.0 - (-...) -> credit 12 on a 10-wide condor
    c = build_iron_condors(condor_chain(80, long_put_price=-9.0), SNAPSHOT, no_atr, 45, 75, 0.10, 0.15, {})
    ok &= check("condor with credit >= width rejected", c == [])
    stale_vertical = pd.DataFrame([
        _row("TEST", EXP, "put", 90, -0.20, 12.0, "TEST"),
        _row("TEST", EXP, "put", 85, -0.10, 1.0, "TEST"),
    ])
    v = build_vertical_credit_spreads(stale_vertical, SNAPSHOT, {"TEST": "bullish"}, 30, 75, (0.15, 0.25), [5], 0)
    ok &= check("vertical with credit >= width rejected", v == [])

    # 2. ^SPX chain with both roots on one expiration: SPXW short strikes, SPX wings nearest the target
    mixed = pd.DataFrame([
        _row("SPXW", EXP, "call", 8200, 0.12, 16.0), _row("SPX", EXP, "call", 8210, 0.11, 14.5),
        _row("SPXW", EXP, "call", 8250, 0.09, 12.0),
        _row("SPXW", EXP, "put", 7000, -0.12, 55.0), _row("SPX", EXP, "put", 6990, -0.12, 52.0),
        _row("SPXW", EXP, "put", 6950, -0.10, 45.0),
    ])
    c = build_iron_condors(mixed, SNAPSHOT, no_atr, 45, 75, 0.10, 0.15, {})
    ok &= check("condors built from the mixed chain", len(c) >= 1)
    ok &= check("no condor mixes SPX and SPXW", all(len(_roots(x)) == 1 for x in c))
    v = build_vertical_credit_spreads(mixed, SNAPSHOT, {"^SPX": "bullish"}, 30, 75, (0.10, 0.15), [10], 0)
    ok &= check("verticals built from the mixed chain", len(v) >= 1)
    ok &= check("no vertical mixes SPX and SPXW", all(len(_roots(x)) == 1 for x in v))

    two_month = pd.concat([mixed, pd.DataFrame([
        # SPX rows first at the SPXW strikes, so a root-blind first-match lookup picks the wrong series
        _row("SPX", EXP2, "call", 8200, 0.20, 41.0), _row("SPXW", EXP2, "call", 8200, 0.20, 42.0),
        _row("SPX", EXP2, "put", 7000, -0.20, 81.0), _row("SPXW", EXP2, "put", 7000, -0.20, 82.0),
        _row("SPX", EXP2, "call", 8210, 0.20, 40.0), _row("SPX", EXP2, "put", 6990, -0.20, 80.0),
        _row("SPX", EXP2, "call", 8260, 0.18, 35.0), _row("SPXW", EXP2, "put", 6940, -0.17, 70.0),
    ])], ignore_index=True)
    history = lambda s, f, b: [0.0] * 5
    two_month.loc[two_month["expiration"] == EXP, "atm_iv"] = 0.30  # front IV elevated -> long calendar / diagonal
    cal = build_calendars(two_month, SNAPSHOT, history, 10, 0.10, 0.50, 0.10, {})
    ok &= check("calendars built from the mixed chain", len(cal) >= 1)
    ok &= check("no calendar mixes SPX and SPXW", all(len(_roots(x)) == 1 for x in cal))
    dd = build_double_diagonals(two_month, SNAPSHOT, history, 10, 0.10, 0.10, 0.15, {})
    ok &= check("double diagonals built from the mixed chain", len(dd) >= 1)
    ok &= check("no double diagonal mixes SPX and SPXW", all(len(_roots(x)) == 1 for x in dd))

    # 4. score_and_rank drops candidates too big to size at the 2% limit
    real_score = screen_trades.score_candidate
    screen_trades.score_candidate = lambda c, *a, **k: (c["fake_score"], {})
    try:
        cands = [{"fake_score": 90, "max_loss": 999999.0}, {"fake_score": 80, "max_loss": 500.0},
                 {"fake_score": 70, "max_loss": -100.0}]
        ranked = screen_trades.score_and_rank(cands)
    finally:
        screen_trades.score_candidate = real_score
    ok &= check(f"only the sizable candidate is ranked (got {[t[0] for t in ranked]})",
                [t[0] for t in ranked] == [80])

    print("\nALL OK" if ok else "\nSOME CHECKS FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
