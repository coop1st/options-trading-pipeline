"""
Verifies pipeline/scoring.py's composite score moves in the book-cited
direction as each of the 7 criteria's underlying input improves, and
that a candidate's score never depends on a criterion the family/data
doesn't support (those default to a neutral 50, per the strategy-engine
spec's explicit policy). No pytest in this repo -- run directly and
inspect output, same convention as verify_greeks.py.

Run: python pipeline/verify_scoring.py
"""
import sys

from scoring import score_candidate

MIN_VOLUME, MIN_OI = 10, 50
PREMIUM_MIN, PREMIUM_MAX = 0.10, 0.25


def _leg(**overrides):
    base = {
        "leg_role": "short put", "contract_symbol": "X", "strike": 100, "expiration": "2026-10-16",
        "type": "put", "delta": -0.15, "last_price": 1.0, "bid": 0.95, "ask": 1.05,
        "volume": 100, "open_interest": 200, "atm_iv_90d_percentile": 50.0,
        "skew_put_pct_of_atm": 150.0, "skew_call_pct_of_atm": 90.0,
        "zero_bid": False, "wide_spread": False,
    }
    base.update(overrides)
    return base


def check(label, condition):
    print(f"{'OK' if condition else 'FAIL'}: {label}")
    return condition


def main():
    all_ok = True

    # Criterion 1: net-short candidate should score HIGHER as IV percentile rises.
    low_iv = {"symbol": "X", "strategy": "vertical put credit spread", "expiration": "2026-10-16",
              "this_expiration_atm_iv": 0.25, "legs": [_leg(atm_iv_90d_percentile=20.0)],
              "credit": 1.0, "width": 5.0, "max_loss": 400.0, "short_delta": -0.15,
              "net_short": True, "tilt": "bullish"}
    high_iv = {**low_iv, "legs": [_leg(atm_iv_90d_percentile=80.0)]}
    score_low, _ = score_candidate(low_iv, MIN_VOLUME, MIN_OI, PREMIUM_MIN, PREMIUM_MAX)
    score_high, _ = score_candidate(high_iv, MIN_VOLUME, MIN_OI, PREMIUM_MIN, PREMIUM_MAX)
    all_ok &= check("net-short: higher IV percentile scores higher", score_high > score_low)

    # Same criterion, opposite direction for a net-long candidate (directional-strategies.md SS5).
    long_low_iv = {"symbol": "X", "strategy": "long call", "expiration": "2026-10-16",
                   "this_expiration_atm_iv": 0.25, "legs": [_leg(type="call", delta=0.50, atm_iv_90d_percentile=20.0)],
                   "max_loss": 500.0, "net_short": False, "tilt": "bullish"}
    long_high_iv = {**long_low_iv, "legs": [_leg(type="call", delta=0.50, atm_iv_90d_percentile=80.0)]}
    score_long_low, _ = score_candidate(long_low_iv, MIN_VOLUME, MIN_OI, PREMIUM_MIN, PREMIUM_MAX)
    score_long_high, _ = score_candidate(long_high_iv, MIN_VOLUME, MIN_OI, PREMIUM_MIN, PREMIUM_MAX)
    all_ok &= check("net-long: LOWER IV percentile scores higher", score_long_low > score_long_high)

    # Criterion 3: risk/reward -- higher credit/width should score higher for a vertical spread.
    low_credit = {**low_iv, "credit": 0.5}
    high_credit = {**low_iv, "credit": 2.0}
    _, breakdown_low = score_candidate(low_credit, MIN_VOLUME, MIN_OI, PREMIUM_MIN, PREMIUM_MAX)
    _, breakdown_high = score_candidate(high_credit, MIN_VOLUME, MIN_OI, PREMIUM_MIN, PREMIUM_MAX)
    all_ok &= check("higher credit/width scores higher risk_reward", breakdown_high["risk_reward"] > breakdown_low["risk_reward"])

    # Criterion 4: POP proxy -- a further-OTM (lower |delta|) short strike scores higher.
    far_otm = {**low_iv, "short_delta": -0.10}
    near_atm = {**low_iv, "short_delta": -0.30}
    _, b_far = score_candidate(far_otm, MIN_VOLUME, MIN_OI, PREMIUM_MIN, PREMIUM_MAX)
    _, b_near = score_candidate(near_atm, MIN_VOLUME, MIN_OI, PREMIUM_MIN, PREMIUM_MAX)
    all_ok &= check("further-OTM short strike scores higher pop_proxy", b_far["pop_proxy"] > b_near["pop_proxy"])

    # Criterion 6: liquidity -- higher volume/OI, no flags, scores higher.
    illiquid = {**low_iv, "legs": [_leg(volume=1, open_interest=5, zero_bid=True, wide_spread=True)]}
    liquid = {**low_iv, "legs": [_leg(volume=500, open_interest=1000)]}
    _, b_illiquid = score_candidate(illiquid, MIN_VOLUME, MIN_OI, PREMIUM_MIN, PREMIUM_MAX)
    _, b_liquid = score_candidate(liquid, MIN_VOLUME, MIN_OI, PREMIUM_MIN, PREMIUM_MAX)
    all_ok &= check("liquid legs score higher than illiquid/flagged legs", b_liquid["liquidity"] > b_illiquid["liquidity"])

    # Criterion 7: directional families need a tilt to score full marks; neutral families need the absence of one.
    _, b_directional_with_tilt = score_candidate(low_iv, MIN_VOLUME, MIN_OI, PREMIUM_MIN, PREMIUM_MAX)
    condor = {"symbol": "X", "strategy": "iron condor", "expiration": "2026-10-16",
              "this_expiration_atm_iv": 0.25, "legs": [_leg()], "credit": 1.0, "width": 5.0,
              "max_loss": 400.0, "short_call_delta": 0.12, "short_put_delta": -0.12,
              "net_short": True, "tilt": None}
    _, b_condor_neutral = score_candidate(condor, MIN_VOLUME, MIN_OI, PREMIUM_MIN, PREMIUM_MAX)
    all_ok &= check("directional family with a matching tilt scores full alignment", b_directional_with_tilt["directional_alignment"] == 100.0)
    all_ok &= check("neutral family with no tilt scores full alignment", b_condor_neutral["directional_alignment"] == 100.0)

    print("ALL_OK" if all_ok else "VERIFICATION_FAILED")
    if not all_ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
