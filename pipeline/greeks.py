"""Black-Scholes option pricing and Greeks (component C step 4).

Standard (non-dividend-paying) Black-Scholes, matching the four inputs the
pipeline design spec calls for: underlying price, strike, days to
expiration, and an implied-volatility assumption (Yahoo's own
impliedVolatility, per contract), plus a fixed risk-free rate
(config.RISK_FREE_RATE). Sign conventions and definitions match
.claude/skills/options-playbook/references/greeks-and-volatility.md SS1 --
that reference gives the conceptual grounding (why each Greek behaves as
it does) but not the closed-form equations themselves, so the formulas
below are the standard Black-Scholes/Merton closed forms.
"""
import math

from scipy.stats import norm


def _d1_d2(underlying_price, strike, years_to_expiration, iv, risk_free_rate):
    sqrt_t = math.sqrt(years_to_expiration)
    d1 = (
        math.log(underlying_price / strike)
        + (risk_free_rate + 0.5 * iv ** 2) * years_to_expiration
    ) / (iv * sqrt_t)
    d2 = d1 - iv * sqrt_t
    return d1, d2


def compute_greeks(underlying_price, strike, days_to_expiration, iv, option_type, risk_free_rate):
    """Returns a dict with delta, gamma, theta (per calendar day), vega
    (per 1 IV percentage point), and rho (per 1 rate percentage point).
    option_type: 'call' or 'put'. Returns all-None values if inputs are
    degenerate (zero/negative DTE or IV -- can't price a contract with no
    time value or no volatility assumption)."""
    if underlying_price is None or strike is None or days_to_expiration is None:
        return {"delta": None, "gamma": None, "theta": None, "vega": None, "rho": None}
    if days_to_expiration <= 0 or iv is None or iv <= 0:
        return {"delta": None, "gamma": None, "theta": None, "vega": None, "rho": None}

    years_to_expiration = days_to_expiration / 365.0
    d1, d2 = _d1_d2(underlying_price, strike, years_to_expiration, iv, risk_free_rate)
    sqrt_t = math.sqrt(years_to_expiration)
    discount = math.exp(-risk_free_rate * years_to_expiration)
    pdf_d1 = norm.pdf(d1)

    gamma = pdf_d1 / (underlying_price * iv * sqrt_t)
    vega = underlying_price * pdf_d1 * sqrt_t / 100.0  # per 1 IV percentage point

    if option_type == "call":
        delta = norm.cdf(d1)
        theta_annual = (
            -(underlying_price * pdf_d1 * iv) / (2 * sqrt_t)
            - risk_free_rate * strike * discount * norm.cdf(d2)
        )
        rho = strike * years_to_expiration * discount * norm.cdf(d2) / 100.0
    elif option_type == "put":
        delta = norm.cdf(d1) - 1
        theta_annual = (
            -(underlying_price * pdf_d1 * iv) / (2 * sqrt_t)
            + risk_free_rate * strike * discount * norm.cdf(-d2)
        )
        rho = -strike * years_to_expiration * discount * norm.cdf(-d2) / 100.0
    else:
        raise ValueError(f"option_type must be 'call' or 'put', got {option_type!r}")

    return {
        "delta": delta,
        "gamma": gamma,
        # per calendar day, matching Bittman's "one day is most common
        # among professionals" convention (greeks-and-volatility.md SS1.4)
        "theta": theta_annual / 365.0,
        "vega": vega,
        "rho": rho,
    }
