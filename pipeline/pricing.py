"""
The one place that decides what an option contract is "worth" on a day.

Rule (owner's decisions, 2026-11-16; the project's own operationalization,
not a book rule):

1. A contract is priced on a day only if it TRADED that day
   (last_trade_date falls on the snapshot date) AND has a real two-sided
   quote (bid > 0 and ask >= bid). Anything else is "not priced that day".
2. Its price is the bid/ask MIDPOINT -- for entries and for exits alike.

Why not last_price: it is the contract's most recent trade, whenever that
was. An audit found multi-leg trades being valued with one leg's price
from today and another's from an earlier day, producing results that
never existed in the market, and last_price sitting outside the bid/ask
for a third of contracts.

Why the midpoint, and what it assumes: the owner chose "exact midpoint"
over the alternatives. It assumes every leg fills halfway between bid and
ask, which a real order often will not get. Measured on this ledger, the
calendar trades are profitable at the midpoint and unprofitable once half
the bid-ask width is paid, so results built on this rule are an upper
bound for calendars. (The only fill convention the source books give is
Bittman ch.9's for a one-to-one vertical spread -- one leg at the touch,
the other at the midpoint; see the playbook's market-making-techniques.md
section 6. The books give none for calendars.)

Both screening (screen_trades.py: what a trade costs to enter) and
outcome tracking (track_outcomes.py: what it is worth later) use this
module, so an entry and its later valuation are always on the same basis.
"""
import pandas as pd

MID_COL = "mid_price"


def priced_contracts(df, snapshot_date):
    """The rows of a signals/snapshot frame that are priced on
    snapshot_date under the rule above, with a MID_COL column added.
    Needs columns: last_trade_date, bid, ask."""
    traded_on = df["last_trade_date"].astype(str).str[:10]
    bid = pd.to_numeric(df["bid"], errors="coerce")
    ask = pd.to_numeric(df["ask"], errors="coerce")
    ok = (traded_on == snapshot_date) & (bid > 0) & (ask >= bid)
    out = df[ok].copy()
    out[MID_COL] = ((bid[ok] + ask[ok]) / 2).round(4)
    return out


def price_lookup(df, snapshot_date):
    """{contract_symbol: midpoint} for the contracts priced that day."""
    p = priced_contracts(df, snapshot_date)
    return dict(zip(p["contract_symbol"], p[MID_COL]))


def as_trade_prices(df, snapshot_date):
    """priced_contracts, with the midpoint also written over last_price.

    The strategy builders and the scorer read a contract's price from the
    `last_price` field everywhere (credits, debits, max loss, premium
    bands, the ledger's rec: cells). Feeding them this frame switches all
    of that to the midpoint in one place, rather than editing every
    formula. The real last trade is kept in `last_trade_price`."""
    out = priced_contracts(df, snapshot_date)
    out["last_trade_price"] = out["last_price"]
    out["last_price"] = out[MID_COL]
    return out
