"""Strategy candidate builders (Component Detail, strategy-engine spec).
Each function takes one day's signals DataFrame (data/github_sync/signals/{date}.csv,
already loaded) plus whatever family-specific inputs it needs, and
returns a list of candidate dicts. Every hard gate is cited to its
source chapter in docs/superpowers/specs/2026-09-05-strategy-engine-design.md;
no threshold here is invented beyond what that spec already flags as an
explicit implementation choice.
"""
from datetime import date


def _dte(expiration, snapshot_date):
    return (date.fromisoformat(expiration) - date.fromisoformat(snapshot_date)).days


def _underlying_daily_volume(symbol_signals):
    """Proxy for directional-strategies.md SS5's underlying-level
    liquidity screen: sums today's per-contract volume across every
    strike/expiration for the symbol, since the pipeline doesn't fetch a
    separate daily-option-volume series per underlying."""
    return int(symbol_signals["volume"].sum())


def _nearest_by_abs_delta(df, target_abs_delta):
    if df.empty:
        return None
    idx = (df["delta"].abs() - target_abs_delta).abs().idxmin()
    return df.loc[idx]


def _nearest_strike_row(df, target_strike):
    if df.empty:
        return None
    idx = (df["strike"] - target_strike).abs().idxmin()
    return df.loc[idx]


def _leg(row, leg_role):
    return {
        "leg_role": leg_role,
        "contract_symbol": row["contract_symbol"],
        "strike": row["strike"],
        "expiration": row["expiration"],
        "type": row["type"],
        "delta": row["delta"],
        "last_price": row["last_price"],
        "bid": row["bid"],
        "ask": row["ask"],
        "volume": row["volume"],
        "open_interest": row["open_interest"],
        "atm_iv_90d_percentile": row["atm_iv_90d_percentile"],
        "skew_put_pct_of_atm": row["skew_put_pct_of_atm"],
        "skew_call_pct_of_atm": row["skew_call_pct_of_atm"],
        "zero_bid": row["zero_bid"],
        "wide_spread": row["wide_spread"],
    }


def build_vertical_credit_spreads(signals, snapshot_date, bias, min_dte, max_dte, delta_band, widths, min_daily_volume):
    """income-strategies.md SS3 / spreads-and-combinations.md SS1.
    Hard gates: DTE window, a bullish or bearish tilt present, underlying
    daily volume above the floor. Strike/width selection is a scoring
    matter, not a gate (both books warn against anchoring to one fixed
    delta or width) -- this builds one candidate per configured width
    around the delta band's midpoint."""
    candidates = []
    target_mid_delta = sum(delta_band) / 2

    for symbol, sym_df in signals.groupby("symbol"):
        tilt = bias.get(symbol)
        if tilt is None:
            continue  # no directional view -- this family isn't built for this symbol
        if _underlying_daily_volume(sym_df) <= min_daily_volume:
            continue

        opt_type = "put" if tilt == "bullish" else "call"
        strategy_name = f"vertical {opt_type} credit spread"

        for expiration, exp_df in sym_df[sym_df["type"] == opt_type].groupby("expiration"):
            dte = _dte(expiration, snapshot_date)
            if not (min_dte <= dte <= max_dte):
                continue

            atm_iv_row = exp_df["atm_iv"].dropna()
            this_expiration_atm_iv = float(atm_iv_row.iloc[0]) if not atm_iv_row.empty else None

            band_df = exp_df[(exp_df["delta"].abs() >= delta_band[0]) & (exp_df["delta"].abs() <= delta_band[1])]
            short_row = _nearest_by_abs_delta(band_df, target_mid_delta)
            if short_row is None:
                continue

            for width in widths:
                long_target = short_row["strike"] - width if opt_type == "put" else short_row["strike"] + width
                long_candidates = exp_df[exp_df["strike"] != short_row["strike"]]
                long_row = _nearest_strike_row(long_candidates, long_target)
                if long_row is None:
                    continue

                credit = short_row["last_price"] - long_row["last_price"]
                actual_width = abs(short_row["strike"] - long_row["strike"])
                if credit <= 0 or actual_width <= 0:
                    continue

                candidates.append({
                    "symbol": symbol,
                    "strategy": strategy_name,
                    "expiration": expiration,
                    "this_expiration_atm_iv": this_expiration_atm_iv,
                    "legs": [_leg(short_row, f"short {opt_type}"), _leg(long_row, f"long {opt_type}")],
                    "credit": credit,
                    "width": actual_width,
                    "max_loss": (actual_width - credit) * 100,
                    "short_delta": short_row["delta"],
                    "net_short": True,
                    "tilt": tilt,
                })
    return candidates
