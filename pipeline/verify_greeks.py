"""
Verifies pipeline/greeks.py against the put-call-parity invariants
.claude/skills/options-playbook/references/greeks-and-volatility.md SS1
states as always-true rules (not against hardcoded numeric reference
values -- more robust, and directly traceable to a cited source). This
repo has no pytest suite; every script here is verified by running it
directly and inspecting output, same convention as
Projects/Stocks/model/_rsi_pairwise_test.py.

Run: python pipeline/verify_greeks.py
"""
import sys

from greeks import compute_greeks

TOLERANCE = 0.005

# (underlying_price, strike, days_to_expiration, iv, risk_free_rate) --
# a spread of ITM/ATM/OTM cases so the invariants are checked across
# moneyness levels, not just at-the-money.
CASES = [
    (100, 100, 30, 0.25, 0.05),   # ATM, short-dated
    (100, 100, 365, 0.20, 0.05),  # ATM, 1yr
    (100, 80, 45, 0.30, 0.05),    # call ITM / put OTM
    (100, 120, 45, 0.30, 0.05),   # call OTM / put ITM
]


def check(label, condition):
    print(f"{'OK' if condition else 'FAIL'}: {label}")
    return condition


def main():
    all_ok = True
    for S, K, days, iv, r in CASES:
        call = compute_greeks(S, K, days, iv, "call", r)
        put = compute_greeks(S, K, days, iv, "put", r)
        label = f"S={S} K={K} days={days} iv={iv}"

        # SS1.1: "|call delta| + |put delta| ~= 1.00 always"
        all_ok &= check(f"[{label}] call_delta - put_delta ~= 1.0",
                         abs((call["delta"] - put["delta"]) - 1.0) < TOLERANCE)
        # SS1.2: "same-strike call/put gammas are (nearly) equal"
        all_ok &= check(f"[{label}] call_gamma ~= put_gamma",
                         abs(call["gamma"] - put["gamma"]) < TOLERANCE)
        # SS1.3: "same-strike call/put vegas are equal"
        all_ok &= check(f"[{label}] call_vega ~= put_vega",
                         abs(call["vega"] - put["vega"]) < TOLERANCE)
        # SS1.1: "call deltas are always positive... put deltas are always negative"
        all_ok &= check(f"[{label}] call_delta > 0", call["delta"] > 0)
        all_ok &= check(f"[{label}] put_delta < 0", put["delta"] < 0)
        # SS1.2: "gammas are always positive for both calls and puts"
        all_ok &= check(f"[{label}] gamma > 0", call["gamma"] > 0)
        # SS1.3: "vegas are always positive for both calls and puts"
        all_ok &= check(f"[{label}] vega > 0", call["vega"] > 0)
        # SS1.5: "rho is positive for calls, negative for puts"
        all_ok &= check(f"[{label}] call_rho > 0", call["rho"] > 0)
        all_ok &= check(f"[{label}] put_rho < 0", put["rho"] < 0)

    print("ALL_OK" if all_ok else "VERIFICATION_FAILED")
    if not all_ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
