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


def build_iron_condors(signals, snapshot_date, get_atr, min_dte, max_dte, delta_min, delta_max):
    """income-strategies.md SS4 / spreads-and-combinations.md SS2. Hard
    gates: delta_min-delta_max on both short strikes, min_dte-max_dte,
    and today's ATM IV > the underlying's 14-day ATR -- gated only once
    get_atr(symbol) returns a value; until then this gate is skipped for
    that symbol with a visible note, matching the atm_iv_90d_percentile
    precedent from sub-project 2."""
    candidates = []
    target_mid_delta = (delta_min + delta_max) / 2

    for symbol, sym_df in signals.groupby("symbol"):
        atr = get_atr(symbol)
        for expiration, exp_df in sym_df.groupby("expiration"):
            dte = _dte(expiration, snapshot_date)
            if not (min_dte <= dte <= max_dte):
                continue

            atm_iv_row = exp_df["atm_iv"].dropna()
            atm_iv = float(atm_iv_row.iloc[0]) if not atm_iv_row.empty else None
            if atr is None:
                print(f"{symbol}: no ATR yet -- skipping condor's IV-vs-ATR gate")
            elif atm_iv is None or atm_iv <= atr:
                continue

            calls = exp_df[exp_df["type"] == "call"]
            puts = exp_df[exp_df["type"] == "put"]
            call_band = calls[(calls["delta"] >= delta_min) & (calls["delta"] <= delta_max)]
            put_band = puts[(puts["delta"].abs() >= delta_min) & (puts["delta"].abs() <= delta_max)]
            short_call = _nearest_by_abs_delta(call_band, target_mid_delta)
            short_put = _nearest_by_abs_delta(put_band, target_mid_delta)
            if short_call is None or short_put is None:
                continue

            long_call = _nearest_strike_row(calls[calls["strike"] > short_call["strike"]], short_call["strike"] + 10)
            long_put = _nearest_strike_row(puts[puts["strike"] < short_put["strike"]], short_put["strike"] - 10)
            if long_call is None or long_put is None:
                continue

            credit = (
                short_call["last_price"] - long_call["last_price"]
                + short_put["last_price"] - long_put["last_price"]
            )
            width = min(abs(long_call["strike"] - short_call["strike"]), abs(short_put["strike"] - long_put["strike"]))
            if credit <= 0 or width <= 0:
                continue

            candidates.append({
                "symbol": symbol,
                "strategy": "iron condor",
                "expiration": expiration,
                "this_expiration_atm_iv": atm_iv,
                "legs": [
                    _leg(short_call, "short call"), _leg(long_call, "long call"),
                    _leg(short_put, "short put"), _leg(long_put, "long put"),
                ],
                "credit": credit,
                "width": width,
                "max_loss": (width - credit) * 100,
                "short_call_delta": short_call["delta"],
                "short_put_delta": short_put["delta"],
                "net_short": True,
                "tilt": None,
            })
    return candidates


def build_directional_longs(signals, bias, min_daily_volume):
    """directional-strategies.md SS1-2, SS5. Hard gates: a bullish or
    bearish tilt present, underlying daily volume above the floor. No
    DTE gate -- the books frame this via the three-part price/time/
    volatility forecast, not a DTE rule, so none is invented here."""
    candidates = []
    for symbol, sym_df in signals.groupby("symbol"):
        tilt = bias.get(symbol)
        if tilt is None:
            continue
        if _underlying_daily_volume(sym_df) <= min_daily_volume:
            continue

        opt_type = "call" if tilt == "bullish" else "put"
        atm_candidates = sym_df[sym_df["type"] == opt_type]
        atm_row = _nearest_by_abs_delta(atm_candidates, 0.50)
        if atm_row is None:
            continue

        atm_iv_row = sym_df[sym_df["expiration"] == atm_row["expiration"]]["atm_iv"].dropna()
        this_expiration_atm_iv = float(atm_iv_row.iloc[0]) if not atm_iv_row.empty else None

        candidates.append({
            "symbol": symbol,
            "strategy": f"long {opt_type}",
            "expiration": atm_row["expiration"],
            "this_expiration_atm_iv": this_expiration_atm_iv,
            "legs": [_leg(atm_row, f"long {opt_type}")],
            "max_loss": atm_row["last_price"] * 100,
            "net_short": False,
            "tilt": tilt,
        })
    return candidates


def build_calendars(signals, snapshot_date, get_term_structure_history, min_front_days, long_premium_min, long_premium_max, short_discount):
    """spreads-and-combinations.md SS4. Hard gates: front-month premium
    (>=long_premium_min, excluded above long_premium_max without manual
    review) or discount (>=short_discount) to its 'normal' relationship
    with the back month, front leg >= min_front_days from expiration,
    and enough accumulated term-structure-spread history to judge
    'normal' at all -- until then this symbol/expiration pair is skipped
    with a visible note."""
    candidates = []
    for symbol, sym_df in signals.groupby("symbol"):
        for opt_type, type_df in sym_df.groupby("type"):
            expirations = sorted(type_df["expiration"].unique())
            for i, front_exp in enumerate(expirations):
                if _dte(front_exp, snapshot_date) < min_front_days:
                    continue
                front_atm_iv_series = type_df[type_df["expiration"] == front_exp]["atm_iv"].dropna()
                if front_atm_iv_series.empty:
                    continue
                front_atm_iv = float(front_atm_iv_series.iloc[0])

                for back_exp in expirations[i + 1:]:
                    back_atm_iv_series = type_df[type_df["expiration"] == back_exp]["atm_iv"].dropna()
                    if back_atm_iv_series.empty:
                        continue
                    back_atm_iv = float(back_atm_iv_series.iloc[0])

                    history = get_term_structure_history(symbol, front_exp, back_exp)
                    if len(history) < 5:
                        print(f"{symbol} {front_exp}/{back_exp}: not enough term-structure history yet -- skipping calendar gate")
                        continue
                    normal_spread = sum(history) / len(history)
                    current_spread = front_atm_iv - back_atm_iv
                    if front_atm_iv == 0:
                        continue
                    premium = (current_spread - normal_spread) / front_atm_iv

                    if long_premium_min <= premium <= long_premium_max:
                        strategy, short_exp, long_exp = "long calendar", front_exp, back_exp
                    elif -premium >= short_discount:
                        strategy, short_exp, long_exp = "short calendar", back_exp, front_exp
                    else:
                        continue

                    strike_row = _nearest_by_abs_delta(type_df[type_df["expiration"] == front_exp], 0.50)
                    if strike_row is None:
                        continue
                    short_match = type_df[(type_df["expiration"] == short_exp) & (type_df["strike"] == strike_row["strike"])]
                    long_match = type_df[(type_df["expiration"] == long_exp) & (type_df["strike"] == strike_row["strike"])]
                    if short_match.empty or long_match.empty:
                        continue
                    short_row, long_row = short_match.iloc[0], long_match.iloc[0]

                    net_debit = long_row["last_price"] - short_row["last_price"]
                    candidates.append({
                        "symbol": symbol,
                        "strategy": strategy,
                        "expiration": front_exp,
                        "this_expiration_atm_iv": front_atm_iv,
                        "legs": [_leg(short_row, f"short {opt_type}"), _leg(long_row, f"long {opt_type}")],
                        "max_loss": abs(net_debit) * 100,
                        "premium": premium,
                        "net_short": strategy == "long calendar",
                        "tilt": None,
                    })
    return candidates


def build_double_diagonals(signals, snapshot_date, get_term_structure_history, min_front_days, long_premium_min, delta_min, delta_max):
    """spreads-and-combinations.md SS5. Same term-structure gate as
    build_calendars (front month elevated relative to a further-out back
    month). Double diagonal only -- a single-sided diagonal has no
    book-given entry rule (spec Non-goals)."""
    candidates = []
    target_mid_delta = (delta_min + delta_max) / 2

    for symbol, sym_df in signals.groupby("symbol"):
        expirations = sorted(sym_df["expiration"].unique())
        for i, front_exp in enumerate(expirations):
            if _dte(front_exp, snapshot_date) < min_front_days:
                continue
            front_df = sym_df[sym_df["expiration"] == front_exp]
            front_atm_iv_series = front_df["atm_iv"].dropna()
            if front_atm_iv_series.empty:
                continue
            front_atm_iv = float(front_atm_iv_series.iloc[0])

            for back_exp in expirations[i + 1:]:
                back_df = sym_df[sym_df["expiration"] == back_exp]
                back_atm_iv_series = back_df["atm_iv"].dropna()
                if back_atm_iv_series.empty:
                    continue
                back_atm_iv = float(back_atm_iv_series.iloc[0])

                history = get_term_structure_history(symbol, front_exp, back_exp)
                if len(history) < 5:
                    continue
                normal_spread = sum(history) / len(history)
                if front_atm_iv == 0:
                    continue
                premium = ((front_atm_iv - back_atm_iv) - normal_spread) / front_atm_iv
                if premium < long_premium_min:
                    continue

                front_call_band = front_df[(front_df["type"] == "call") & (front_df["delta"] >= delta_min) & (front_df["delta"] <= delta_max)]
                front_put_band = front_df[(front_df["type"] == "put") & (front_df["delta"].abs() >= delta_min) & (front_df["delta"].abs() <= delta_max)]
                short_call = _nearest_by_abs_delta(front_call_band, target_mid_delta)
                short_put = _nearest_by_abs_delta(front_put_band, target_mid_delta)
                if short_call is None or short_put is None:
                    continue

                back_calls = back_df[back_df["type"] == "call"]
                back_puts = back_df[back_df["type"] == "put"]
                long_call = _nearest_strike_row(back_calls, short_call["strike"] + 10)
                long_put = _nearest_strike_row(back_puts, short_put["strike"] - 10)
                if long_call is None or long_put is None:
                    continue

                net_debit = (
                    long_call["last_price"] - short_call["last_price"]
                    + long_put["last_price"] - short_put["last_price"]
                )
                candidates.append({
                    "symbol": symbol,
                    "strategy": "double diagonal",
                    "expiration": front_exp,
                    "this_expiration_atm_iv": front_atm_iv,
                    "legs": [
                        _leg(short_call, "short call"), _leg(long_call, "long call"),
                        _leg(short_put, "short put"), _leg(long_put, "long put"),
                    ],
                    "max_loss": abs(net_debit) * 100,
                    "premium": premium,
                    "net_short": True,
                    "tilt": None,
                })
    return candidates
