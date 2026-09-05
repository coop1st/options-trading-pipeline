"""Composite scoring (Composite Scoring section, strategy-engine spec),
pure function, no I/O, same shape as greeks.py. Each of the 7 criteria
maps to a 0-100 sub-score; family/criterion cells the books don't
support default to a neutral 50 rather than a fabricated number, per the
spec's explicit policy.
"""
import math

NEUTRAL = 50.0

_DIRECTIONAL_FAMILIES = ("vertical put credit spread", "vertical call credit spread", "long call", "long put")


def _valid(x):
    """True if x is a usable number -- excludes both None and NaN. A
    blank cell in signals.csv (e.g. atm_iv_90d_percentile before 5 days
    of history accumulate) round-trips through pandas as NaN, not None,
    so checking only `is not None` silently lets NaN poison a sum/average
    -- this bug shipped with sub-project 3 and only surfaced once
    composite_score started being persisted (sub-project 4)."""
    return x is not None and not (isinstance(x, float) and math.isnan(x))


def _iv_richness(candidate):
    percentiles = [leg["atm_iv_90d_percentile"] for leg in candidate["legs"] if _valid(leg["atm_iv_90d_percentile"])]
    if not percentiles:
        return NEUTRAL
    percentile = sum(percentiles) / len(percentiles)
    # income-strategies.md SS6 / directional-strategies.md SS5: net-short
    # (premium-selling) structures favor a RICH (high-percentile) sold
    # leg; net-long (directional/short-calendar) structures favor a
    # CHEAP (low-percentile) bought leg.
    return percentile if candidate["net_short"] else 100 - percentile


def _skew_quality(candidate):
    """greeks-and-volatility.md SS4.3: richest setups combine high skew
    and high ATM IV. skew_*_pct_of_atm values run roughly 80-200+
    (percent of ATM IV); dividing by 2 and capping at 100 is this
    module's own normalization choice, not a book number -- the books
    give no explicit 0-100 scale for this."""
    strategy = candidate["strategy"]
    if strategy == "vertical put credit spread":
        vals = [leg["skew_put_pct_of_atm"] for leg in candidate["legs"] if _valid(leg["skew_put_pct_of_atm"])]
    elif strategy == "vertical call credit spread":
        vals = [leg["skew_call_pct_of_atm"] for leg in candidate["legs"] if _valid(leg["skew_call_pct_of_atm"])]
    elif strategy == "iron condor":
        vals = [
            leg[k] for leg in candidate["legs"]
            for k in ("skew_put_pct_of_atm", "skew_call_pct_of_atm")
            if _valid(leg[k])
        ]
    else:
        return NEUTRAL  # calendars/diagonals: skew "roughly nets out" (spreads-and-combinations.md SS4); directional: no computable book rule
    return min(sum(vals) / len(vals), 200.0) / 2 if vals else NEUTRAL


def _risk_reward(candidate, calendar_premium_min, calendar_premium_max):
    strategy = candidate["strategy"]
    if strategy in ("vertical put credit spread", "vertical call credit spread", "iron condor"):
        if candidate.get("width", 0) <= 0:
            return NEUTRAL
        return min(100 * candidate["credit"] / candidate["width"], 100.0)
    if strategy in ("long calendar", "short calendar", "double diagonal"):
        premium = abs(candidate.get("premium", 0))
        span = calendar_premium_max - calendar_premium_min
        if span <= 0:
            return NEUTRAL
        return max(0.0, min(100.0, 100 * (premium - calendar_premium_min) / span))
    return NEUTRAL  # directional longs: capped-risk/uncapped-reward by construction, not a comparable ratio


def _pop_proxy(candidate):
    strategy = candidate["strategy"]
    if strategy in ("vertical put credit spread", "vertical call credit spread"):
        return 100 * (1 - abs(candidate["short_delta"]))
    if strategy == "iron condor":
        avg_delta = (abs(candidate["short_call_delta"]) + abs(candidate["short_put_delta"])) / 2
        return 100 * (1 - avg_delta)
    if strategy in ("long call", "long put"):
        return 100 * abs(candidate["legs"][0]["delta"])
    return NEUTRAL  # calendars/diagonals: term-structure trades, not probability-of-success trades


def _term_structure_signal(candidate, other_expirations_atm_iv):
    if not other_expirations_atm_iv or candidate.get("this_expiration_atm_iv") is None:
        return NEUTRAL
    diff = (candidate["this_expiration_atm_iv"] - other_expirations_atm_iv) / other_expirations_atm_iv
    score = 50 + diff * 100
    score = score if candidate["net_short"] else 100 - score
    return max(0.0, min(100.0, score))


def _liquidity_gradient(candidate, min_volume, min_open_interest):
    scores = []
    for leg in candidate["legs"]:
        vol_score = min(100.0, 100 * leg["volume"] / max(min_volume, 1))
        oi_score = min(100.0, 100 * leg["open_interest"] / max(min_open_interest, 1))
        penalty = (30 if leg["zero_bid"] else 0) + (20 if leg["wide_spread"] else 0)
        scores.append(max(0.0, (vol_score + oi_score) / 2 - penalty))
    return sum(scores) / len(scores) if scores else NEUTRAL


def _directional_alignment(candidate):
    if candidate["strategy"] in _DIRECTIONAL_FAMILIES:
        return 100.0 if candidate.get("tilt") else NEUTRAL
    return 100.0 if candidate.get("tilt") is None else NEUTRAL


def score_candidate(candidate, min_volume, min_open_interest, calendar_premium_min, calendar_premium_max, other_expirations_atm_iv=None):
    """Returns (composite_score, breakdown_dict) -- the breakdown is kept
    for ledger/debugging traceability per the spec."""
    breakdown = {
        "iv_richness": _iv_richness(candidate),
        "skew_quality": _skew_quality(candidate),
        "risk_reward": _risk_reward(candidate, calendar_premium_min, calendar_premium_max),
        "pop_proxy": _pop_proxy(candidate),
        "term_structure": _term_structure_signal(candidate, other_expirations_atm_iv),
        "liquidity": _liquidity_gradient(candidate, min_volume, min_open_interest),
        "directional_alignment": _directional_alignment(candidate),
    }
    composite = sum(breakdown.values()) / len(breakdown)
    return composite, breakdown


# Sub-project 5 (strategy-comparison-design.md's label refinement):
# "thesis" criteria describe WHY a candidate was picked (a book-cited
# edge -- rich IV, rich skew, a term-structure edge, a confirmed
# directional tilt); risk_reward/pop_proxy/liquidity describe HOW GOOD
# the trade is, not why it was chosen, so they don't drive the label.
THESIS_CRITERIA = ["iv_richness", "skew_quality", "term_structure", "directional_alignment"]
_THESIS_LABEL_NAMES = {
    "iv_richness": "rich_iv",
    "skew_quality": "rich_skew",
    "term_structure": "term_structure_edge",
    "directional_alignment": "directional_confirmation",
}


def compute_selection_label(breakdown, threshold):
    """Returns a human-readable label naming which thesis criteria
    scored at or above `threshold` (meaningfully above the NEUTRAL=50
    baseline) for this candidate -- e.g. "rich_iv+rich_skew" for an iron
    condor combining both, directly matching greeks-and-volatility.md
    SS4.3's "richest setups combine high skew and high ATM IV" rather
    than an invented category. "no_dominant_thesis" if none clear the
    bar -- itself a meaningful, trackable label. `threshold` is passed
    in (not imported) to keep this module dependency-free, matching
    score_candidate()'s own pattern; config.LABEL_THESIS_THRESHOLD is
    this project's chosen value, not a book number."""
    drivers = [c for c in THESIS_CRITERIA if breakdown.get(c, 0) >= threshold]
    if not drivers:
        return "no_dominant_thesis"
    return "+".join(_THESIS_LABEL_NAMES[c] for c in drivers)
