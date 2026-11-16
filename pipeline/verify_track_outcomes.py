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
        _leg("short call", 1.20, "TEST260601C00110000"),
        _leg("long call", 0.40, "TEST260601C00120000"),
        _leg("short put", 1.10, "TEST260601P00090000"),
        _leg("long put", 0.30, "TEST260601P00080000"),
    ]
    hit_target_prices = {
        "TEST260601C00110000": 0.30, "TEST260601C00120000": 0.10,
        "TEST260601P00090000": 0.25, "TEST260601P00080000": 0.05,
    }  # cost_to_close = (0.30-0.10)+(0.25-0.05) = 0.40 -> profit_pct = (1.60-0.40)/1.60 = 0.75 >= 0.55
    status, out_date, pct = evaluate_trade(
        "iron condor", condor_legs, {"2026-05-01": hit_target_prices}, date(2026, 5, 1),
    )
    check("condor hits target at 75% captured", status == "HIT_TARGET" and pct > 0.55)

    max_loss_prices = {
        "TEST260601C00110000": 5.00, "TEST260601C00120000": 0.05,
        "TEST260601P00090000": 0.05, "TEST260601P00080000": 0.01,
    }  # cost_to_close = (5.00-0.05)+(0.05-0.01) = 4.99 -> loss = 4.99-1.60=3.39 >= 1.60 credit
    status, out_date, pct = evaluate_trade(
        "iron condor", condor_legs, {"2026-05-01": max_loss_prices}, date(2026, 5, 1),
    )
    check("condor hits max loss", status == "HIT_MAX_LOSS")

    time_exit_prices = {
        "TEST260601C00110000": 1.00, "TEST260601C00120000": 0.35,
        "TEST260601P00090000": 0.90, "TEST260601P00080000": 0.25,
    }  # cost_to_close = (1.00-0.35)+(0.90-0.25) = 1.30 -> profit_pct = (1.60-1.30)/1.60 = 0.1875, neither target nor max-loss
    status, out_date, pct = evaluate_trade(
        "iron condor", condor_legs, {"2026-05-02": time_exit_prices}, date(2026, 5, 2),
    )
    # 2026-06-01 expiration, 2026-05-02 is 30 days out -- exactly the TIME_EXIT boundary
    check("condor time-exits at 30 DTE with no target/stop hit", status == "TIME_EXIT")

    # Vertical put credit spread: width=5, credit = 1.50-0.60=0.90.
    vert_legs = [
        _leg("short put", 1.50, "TEST260601P00095000"),
        _leg("long put", 0.60, "TEST260601P00090000"),
    ]
    vert_target_prices = {"TEST260601P00095000": 0.70, "TEST260601P00090000": 0.20}
    # cost_to_close = 0.70-0.20=0.50 -> profit_pct=(0.90-0.50)/0.90=0.44 >= 0.10
    status, _, _ = evaluate_trade("vertical put credit spread", vert_legs, {"2026-05-15": vert_target_prices}, date(2026, 5, 15))
    check("vertical spread hits 10% target", status == "HIT_TARGET")

    vert_max_loss_prices = {"TEST260601P00095000": 5.00, "TEST260601P00090000": 0.00}
    # cost_to_close = 5.00-0.00=5.00 == width(5) -> max loss
    status, _, _ = evaluate_trade("vertical put credit spread", vert_legs, {"2026-05-15": vert_max_loss_prices}, date(2026, 5, 15))
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

    # Sub-project 5: evaluator_overrides must actually change behavior
    # (the sweep depends on this), and must not affect the default path.
    # Premium paid = 3.00; price 4.80 = 160% of premium (ratio 1.6).
    status, _, _ = evaluate_trade(
        "long call", long_call_legs, {"2026-03-01": {"TEST260601C00100000": 4.80}}, date(2026, 3, 1),
    )
    check("default thresholds: 160% of premium hits neither target nor stop yet", status == "OPEN")
    status, _, _ = evaluate_trade(
        "long call", long_call_legs, {"2026-03-01": {"TEST260601C00100000": 4.80}}, date(2026, 3, 1),
        evaluator_overrides={"target_pct": 1.5},
    )
    check("overridden target_pct=1.5: same 160% now hits HIT_TARGET", status == "HIT_TARGET")

    # Gap-skip: a date with missing pricing for one leg must be skipped,
    # not treated as a signal -- evaluation resumes on the next date.
    gapped_history = {
        "2026-05-10": {"TEST260601P00095000": 1.40},  # long leg missing this day -- must be skipped
        "2026-05-12": vert_target_prices,  # complete data, target should fire here
    }
    status, out_date, _ = evaluate_trade("vertical put credit spread", vert_legs, gapped_history, date(2026, 5, 12))
    check("gap day skipped, target fires on the next complete date", status == "HIT_TARGET" and out_date == "2026-05-12")

    # UNRESOLVED_AT_EXPIRATION: expiration (2026-06-01) has passed and NO
    # date ever had complete pricing for both legs.
    status, _, pct = evaluate_trade("vertical put credit spread", vert_legs, {}, date(2026, 7, 1))
    check("no data at all + expiration passed -> UNRESOLVED_AT_EXPIRATION", status == "UNRESOLVED_AT_EXPIRATION" and pct is None)

    # Still OPEN: expiration (2026-06-01) hasn't passed yet, no data yet.
    status, _, _ = evaluate_trade("vertical put credit spread", vert_legs, {}, date(2026, 4, 1))
    check("no data yet, expiration in the future -> OPEN", status == "OPEN")

    # Snapshots dated before entry must be ignored: a pre-entry price that
    # would hit max loss must not resolve a trade recommended later.
    pre_entry_history = {"2026-05-01": vert_max_loss_prices, "2026-05-15": vert_target_prices}
    status, out_date, _ = evaluate_trade("vertical put credit spread", vert_legs, pre_entry_history,
                                         date(2026, 5, 15), entry_date="2026-05-10")
    check("pre-entry snapshot ignored -> resolves on post-entry date only",
          status == "HIT_TARGET" and out_date == "2026-05-15")
    status, _, _ = evaluate_trade("vertical put credit spread", vert_legs, {"2026-05-10": vert_max_loss_prices},
                                  date(2026, 5, 12), entry_date="2026-05-10")
    check("entry-day snapshot itself ignored -> OPEN", status == "OPEN")

    # Pricing rule (pricing.py, 2026-11-16): a contract is priced on a day
    # only if it traded that day AND has a real bid and ask, and its price
    # is the bid/ask midpoint. Rebuilds the real DECK case from the audit:
    # on 15 Oct the long leg traded (2.80) but the short leg still showed
    # 14 Oct's 3.58 -- valued naively on last prices that is a -286% "max
    # loss"; under the rule the day is simply not priced.
    import pandas as pd
    import pricing
    import screen_trades
    from track_outcomes import priced_entry_legs

    short_c, long_c = "DECK261030P00080000", "DECK261120P00080000"
    cols = ["contract_symbol", "last_price", "bid", "ask", "last_trade_date"]
    day = lambda rows: pd.DataFrame(rows, columns=cols)
    files = {
        "2026-10-14": day([(short_c, 3.58, 3.00, 3.20, "2026-10-14 19:55:01+00:00"),
                           (long_c, 4.00, 3.60, 4.00, "2026-10-14 18:02:44+00:00")]),
        "2026-10-15": day([(short_c, 3.58, 1.75, 2.95, "2026-10-14 19:55:01+00:00"),
                           (long_c, 2.80, 2.60, 3.00, "2026-10-15 15:10:09+00:00")]),
        "2026-10-23": day([(short_c, 1.25, 1.10, 1.50, "2026-10-23 17:20:00+00:00"),
                           (long_c, 2.95, 2.65, 2.95, "2026-10-23 19:40:00+00:00")]),
    }
    mids = {d: pricing.price_lookup(df, d) for d, df in files.items()}
    check("price is the bid/ask midpoint, not the last trade",
          mids["2026-10-14"] == {short_c: 3.10, long_c: 3.80})
    check("a contract that did not trade that day is not priced", short_c not in mids["2026-10-15"])
    no_bid = day([(short_c, 1.0, 0.0, 1.2, "2026-10-23 17:20:00+00:00")])
    check("a contract with no bid is not priced", pricing.price_lookup(no_bid, "2026-10-23") == {})
    crossed = day([(short_c, 1.0, 1.3, 1.2, "2026-10-23 17:20:00+00:00")])
    check("a crossed quote (ask below bid) is not priced", pricing.price_lookup(crossed, "2026-10-23") == {})
    check("a non-market-day copy prices nothing", pricing.price_lookup(files["2026-10-14"], "2026-10-17") == {})

    ledger_legs = [_leg("short put", 3.58, short_c), _leg("long put", 4.00, long_c)]  # last prices, as recorded
    entry_legs = priced_entry_legs("long calendar", ledger_legs, mids, "2026-10-14")
    check("entry is re-priced at the entry day's midpoints (debit 0.70, not the recorded 0.42)",
          entry_legs is not None and [l["entry_price"] for l in entry_legs] == [3.10, 3.80])
    status, out_date, pct = evaluate_trade("long calendar", entry_legs, mids, date(2026, 10, 26), entry_date="2026-10-14")
    check("the stale-leg day is skipped; the result comes from the next fully priced day, at midpoints",
          status == "HIT_TARGET" and out_date == "2026-10-23" and abs(pct - (1.50 - 0.70) / 0.70) < 1e-9)
    naive = {d: dict(zip(df["contract_symbol"], df["last_price"])) for d, df in files.items()}
    status, out_date, pct = evaluate_trade("long calendar", ledger_legs, naive, date(2026, 10, 26), entry_date="2026-10-14")
    check("(control) on last prices the same data gives the false max loss on 15 Oct",
          status == "HIT_MAX_LOSS" and out_date == "2026-10-15")
    check("entry not priceable when a leg did not trade on the entry day",
          priced_entry_legs("long calendar", ledger_legs, {"2026-10-14": {long_c: 3.80}}, "2026-10-14") is None)
    check("entry not priceable when the midpoints give no positive net price",
          priced_entry_legs("long calendar", ledger_legs, {"2026-10-14": {short_c: 3.80, long_c: 3.80}}, "2026-10-14") is None)
    check("entry not priceable when the entry day has no file", priced_entry_legs("long calendar", ledger_legs, {}, "2026-10-14") is None)

    view = pricing.as_trade_prices(files["2026-10-15"], "2026-10-15")
    check("screening sees only priced contracts, with the midpoint in the price field and the last trade kept aside",
          list(view["contract_symbol"]) == [long_c] and list(view["last_price"]) == [2.80]
          and list(view["last_trade_price"]) == [2.80] and list(view[pricing.MID_COL]) == [2.80])
    view14 = pricing.as_trade_prices(files["2026-10-14"], "2026-10-14").set_index("contract_symbol")
    check("...midpoint replaces a last price that sat outside the quote",
          view14.loc[short_c, "last_price"] == 3.10 and view14.loc[short_c, "last_trade_price"] == 3.58)

    print("ALL_OK" if ALL_OK else "VERIFICATION_FAILED")
    if not ALL_OK:
        sys.exit(1)


if __name__ == "__main__":
    main()
