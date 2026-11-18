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

    # An expiry result needs prices from the expiration day itself. A
    # price from days earlier is a mark, not a result (17 Nov 2026).
    # Premium 3.00, price 4.00: neither the 200% target nor the 50% stop.
    status, out_date, pct = evaluate_trade(
        "long call", long_call_legs, {"2026-05-20": {"TEST260601C00100000": 4.00}}, date(2026, 7, 1))
    check("last priced 12 days before expiry, expiry passed -> UNRESOLVED, dated at expiry, no result",
          status == "UNRESOLVED_AT_EXPIRATION" and out_date == "2026-06-01" and pct is None)
    status, out_date, pct = evaluate_trade(
        "long call", long_call_legs, {"2026-05-29": {"TEST260601C00100000": 4.00}}, date(2026, 7, 1))
    check("last priced 3 days before expiry (the Friday before a Monday expiry) -> still UNRESOLVED",
          status == "UNRESOLVED_AT_EXPIRATION" and pct is None)
    status, out_date, pct = evaluate_trade(
        "long call", long_call_legs, {"2026-06-01": {"TEST260601C00100000": 4.00}}, date(2026, 7, 1))
    check("priced on the expiration day itself -> EXPIRED_PROFIT from that day's prices",
          status == "EXPIRED_PROFIT" and out_date == "2026-06-01" and abs(pct - 1 / 3) < 1e-9)
    status, _, _ = evaluate_trade(
        "long call", long_call_legs, {"2026-05-20": {"TEST260601C00100000": 4.00}}, date(2026, 5, 25))
    check("priced earlier, expiry not yet passed -> OPEN", status == "OPEN")

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
    # if it has a real bid and ask, at the bid/ask midpoint; a trade that
    # day is not required. Rebuilds the real DECK case from the audit: on
    # 15 Oct the long leg traded (2.80) but the short leg still showed
    # 14 Oct's last price of 3.58 -- valued on last prices that is a -286%
    # "max loss"; on that day's quotes (2.35 and 2.80) it is a 36% loss
    # on a 0.70 debit -- still a stop-out, but a real one.
    import pandas as pd
    import pricing
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
    check("a quoted contract is priced even though it did not trade that day",
          mids["2026-10-15"] == {short_c: 2.35, long_c: 2.80})
    no_bid = day([(short_c, 1.0, 0.0, 1.2, "2026-10-23 17:20:00+00:00")])
    check("a contract with no bid is not priced", pricing.price_lookup(no_bid, "2026-10-23") == {})
    crossed = day([(short_c, 1.0, 1.3, 1.2, "2026-10-23 17:20:00+00:00")])
    check("a crossed quote (ask below bid) is not priced", pricing.price_lookup(crossed, "2026-10-23") == {})
    check("nothing is priced on a snapshot from a day the market was shut",
          pricing.price_lookup(files["2026-10-14"], "2026-09-07") == {})

    ledger_legs = [_leg("short put", 3.58, short_c), _leg("long put", 4.00, long_c)]  # last prices, as recorded
    entry_legs = priced_entry_legs("long calendar", ledger_legs, mids, "2026-10-14")
    check("entry is re-priced at the entry day's midpoints (debit 0.70, not the recorded 0.42)",
          entry_legs is not None and [l["entry_price"] for l in entry_legs] == [3.10, 3.80])
    status, out_date, pct = evaluate_trade("long calendar", entry_legs, mids, date(2026, 10, 26), entry_date="2026-10-14")
    check("15 Oct on quotes: value 0.45 against a 0.70 debit -- a real 36% stop-out (the stop is 10%), not -286%",
          status == "HIT_MAX_LOSS" and out_date == "2026-10-15" and abs(pct - (0.45 - 0.70) / 0.70) < 1e-9)
    no_15 = {d: v for d, v in mids.items() if d != "2026-10-15"}
    status, out_date, pct = evaluate_trade("long calendar", entry_legs, no_15, date(2026, 10, 26), entry_date="2026-10-14")
    check("a day with no quotes is skipped; the next priced day decides, at midpoints",
          status == "HIT_TARGET" and out_date == "2026-10-23" and abs(pct - (1.50 - 0.70) / 0.70) < 1e-9)
    naive = {d: dict(zip(df["contract_symbol"], df["last_price"])) for d, df in files.items()}
    status, out_date, pct = evaluate_trade("long calendar", ledger_legs, naive, date(2026, 10, 26), entry_date="2026-10-14")
    check("(control) on last prices the same data gives the false max loss on 15 Oct",
          status == "HIT_MAX_LOSS" and out_date == "2026-10-15")
    check("entry not priceable when a leg has no quote on the entry day",
          priced_entry_legs("long calendar", ledger_legs, {"2026-10-14": {long_c: 3.80}}, "2026-10-14") is None)
    check("entry not priceable when the midpoints give no positive net price",
          priced_entry_legs("long calendar", ledger_legs, {"2026-10-14": {short_c: 3.80, long_c: 3.80}}, "2026-10-14") is None)
    check("entry not priceable when the entry day has no file", priced_entry_legs("long calendar", ledger_legs, {}, "2026-10-14") is None)

    view = pricing.as_trade_prices(files["2026-10-14"], "2026-10-14").set_index("contract_symbol")
    check("screening gets the midpoint in the price field, with the last trade kept aside",
          view.loc[short_c, "last_price"] == 3.10 and view.loc[short_c, "last_trade_price"] == 3.58
          and view.loc[short_c, pricing.MID_COL] == 3.10)
    check("screening leaves out a contract with no bid",
          list(pricing.as_trade_prices(no_bid, "2026-10-23")["contract_symbol"]) == [])

    # A trade is only recommended if its legs give the net credit/debit
    # its strategy is defined by (real cases from 2026-11-16).
    import screen_trades
    cand = lambda strategy, legs: {"strategy": strategy, "legs": [{"leg_role": r, "last_price": p} for r, p in legs]}
    check("a short calendar that would cost money to put on is not recommended (HDB: 1.75 in, 1.875 out)",
          not screen_trades.has_positive_net_entry(cand("short calendar", [("short call", 1.75), ("long call", 1.875)])))
    check("a short calendar that takes in a credit is",
          screen_trades.has_positive_net_entry(cand("short calendar", [("short call", 2.145), ("long call", 1.07)])))
    check("a double diagonal put on for a net credit is not recommended (VXX)",
          not screen_trades.has_positive_net_entry(cand("double diagonal", [("short call", 0.245), ("long call", 0.27),
                                                                              ("short put", 0.25), ("long put", 0.055)])))
    check("a long calendar that costs a debit is",
          screen_trades.has_positive_net_entry(cand("long calendar", [("short put", 3.10), ("long put", 3.80)])))

    # Entry gate (2026-11-18): a calendar/diagonal whose net price is
    # smaller than the bid-ask width of its legs is not recommended.
    qcand = lambda strategy, legs: {"strategy": strategy, "legs": [
        {"leg_role": r, "last_price": (b + a) / 2, "bid": b, "ask": a} for r, b, a in legs]}
    check("a 13.20 short calendar with 1.00 of quote width passes the quote-width gate",
          screen_trades.target_clears_quote_width(qcand("short calendar", [("short call", 59.5, 60.0), ("long call", 46.3, 46.8)])))
    check("a 0.225 short calendar with 0.19 of quote width passes too (KHC 2026-11-17)",
          screen_trades.target_clears_quote_width(qcand("short calendar", [("short call", 0.74, 0.83), ("long call", 0.51, 0.61)])))
    check("a 0.075 long calendar with 0.15 of quote width does not pass (TE 2026-11-17)",
          not screen_trades.target_clears_quote_width(qcand("long calendar", [("short put", 0.25, 0.30), ("long put", 0.30, 0.40)])))
    check("the gate leaves an iron condor alone",
          screen_trades.target_clears_quote_width(qcand("iron condor", [("short call", 0.10, 0.90), ("long call", 0.05, 0.50)])))

    # Short calendar stop on estimated original margin (2026-11-18).
    from track_outcomes import short_calendar_margin
    sc = [_leg("short call", 60.0, "SPX270115C07200000"), _leg("long call", 47.0, "SPX261218C07200000")]
    m = short_calendar_margin("^SPX", sc, 7200.0)
    check("index short call calendar margin = 60 + 15% x 7200 + 47 = 1187", abs(m - 1187.0) < 1e-6)
    eq = [_leg("short put", 1.00, "KHC261218P00025000"), _leg("long put", 0.40, "KHC261127P00025000")]
    check("equity short put calendar, 1.00 out of the money: 1.00 + (20% x 26 - 1) + 0.40 = 5.60",
          abs(short_calendar_margin("KHC", eq, 26.0) - 5.60) < 1e-6)
    check("far out-of-the-money put falls back to the 10%-of-strike floor: 1.00 + 2.50 + 0.40",
          abs(short_calendar_margin("KHC", eq, 40.0) - 3.90) < 1e-6)
    check("no underlying price -> no margin estimate", short_calendar_margin("KHC", eq, None) is None)
    # credit 13.00; a 20.00 loss is 154% of the credit but under 10% of margin (118.70)
    day = lambda short_px, long_px: {"2026-12-01": {"SPX270115C07200000": short_px, "SPX261218C07200000": long_px}}
    status, _, _ = evaluate_trade("short calendar", sc, day(80.0, 47.0), date(2026, 12, 1), evaluator_overrides={"margin": m})
    check("short calendar: a loss under 10% of margin stays open", status == "OPEN")
    status, _, pct = evaluate_trade("short calendar", sc, day(180.0, 47.0), date(2026, 12, 1), evaluator_overrides={"margin": m})
    check("short calendar: a loss of 120.00 (over 10% of 1187 margin) is a stop, reported on the credit",
          status == "HIT_MAX_LOSS" and abs(pct - (-120.0 / 13.0)) < 1e-6)
    status, _, _ = evaluate_trade("short calendar", sc, day(59.0, 47.0), date(2026, 12, 1), evaluator_overrides={"margin": m})
    check("short calendar: target is still 5% of the credit", status == "HIT_TARGET")

    # Minimum profit of 5 cents before a calendar/diagonal target counts (2026-11-18).
    small = [_leg("short put", 0.30, "TEST260601P00010000"), _leg("long put", 0.70, "TEST260701P00010000")]
    one = lambda s_px, l_px: {"2026-05-01": {"TEST260601P00010000": s_px, "TEST260701P00010000": l_px}}
    status, _, _ = evaluate_trade("long calendar", small, one(0.30, 0.73), date(2026, 5, 1))
    check("long calendar: +7.5% but only 3 cents is not a target", status == "OPEN")
    status, _, _ = evaluate_trade("long calendar", small, one(0.30, 0.75), date(2026, 5, 1))
    check("long calendar: +5 cents is a target", status == "HIT_TARGET")
    small_sc = [_leg("short call", 0.80, "TEST260701C00010000"), _leg("long call", 0.50, "TEST260601C00010000")]
    one_c = lambda s_px, l_px: {"2026-05-01": {"TEST260701C00010000": s_px, "TEST260601C00010000": l_px}}
    status, _, _ = evaluate_trade("short calendar", small_sc, one_c(0.77, 0.50), date(2026, 5, 1), evaluator_overrides={"margin": 3.0})
    check("short calendar: +10% but only 3 cents is not a target", status == "OPEN")
    status, _, _ = evaluate_trade("short calendar", small_sc, one_c(0.75, 0.50), date(2026, 5, 1), evaluator_overrides={"margin": 3.0})
    check("short calendar: +5 cents is a target", status == "HIT_TARGET")

    print("ALL_OK" if ALL_OK else "VERIFICATION_FAILED")
    if not ALL_OK:
        sys.exit(1)


if __name__ == "__main__":
    main()
