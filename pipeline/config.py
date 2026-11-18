"""Shared configuration for the options data pipeline."""
import os
import sys
from pathlib import Path

# Norton antivirus on this machine does TLS inspection that breaks strict
# OpenSSL certificate validation for Python HTTPS calls. Routing through the
# OS-native validator instead avoids that mismatch without weakening
# certificate validation -- this is strictly "trust what Windows already
# trusts," not "skip verification." Safe to call unconditionally; a no-op
# if nothing intercepts traffic on a given machine. Verbatim copy of the
# fix already proven in Projects/Stocks/pipeline/config.py:1-62 -- see that
# file's comments for the full explanation of why each piece is needed.
import truststore

truststore.inject_into_ssl()

PIPELINE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = PIPELINE_DIR.parent
DB_PATH = PROJECT_DIR / "data" / "db" / "options.db"


def _ensure_curl_cffi_trusts_os_certs():
    """truststore above only patches Python's stdlib ssl module -- yfinance's
    cookie/crumb auth step goes through curl_cffi instead, which bundles its
    own separate TLS stack. curl_cffi (like real curl) honors the
    CURL_CA_BUNDLE env var, so fix it the same way: export Windows' trusted
    root/CA stores to a PEM file and point CURL_CA_BUNDLE at it. Regenerated
    on every import rather than cached. Respects an existing CURL_CA_BUNDLE
    if the environment already sets one. No-op on non-Windows or if nothing
    intercepts traffic here."""
    if sys.platform != "win32" or os.environ.get("CURL_CA_BUNDLE"):
        return
    import base64
    import ssl

    bundle_path = PROJECT_DIR / "data" / "cache" / "curl_cffi_ca_bundle.pem"
    try:
        bundle_path.parent.mkdir(parents=True, exist_ok=True)
        with open(bundle_path, "w") as f:
            for storename in ("ROOT", "CA"):
                for cert_der, _encoding, _trust in ssl.enum_certificates(storename):
                    b64 = base64.b64encode(cert_der).decode("ascii")
                    f.write("-----BEGIN CERTIFICATE-----\n")
                    for i in range(0, len(b64), 64):
                        f.write(b64[i:i + 64] + "\n")
                    f.write("-----END CERTIFICATE-----\n")
        os.environ["CURL_CA_BUNDLE"] = str(bundle_path)
    except OSError:
        pass  # best-effort -- curl_cffi calls just fail the same way they did before


_ensure_curl_cffi_trusts_os_certs()

# Black-Scholes risk-free rate: fixed constant per the pipeline design
# spec's resolved open question (Bittman ch.4 shows a 2-point rate change
# moves a 90-day ATM call by only ~0.24, so a fixed reasonable constant is
# fine rather than fetching a live Treasury rate).
RISK_FREE_RATE = 0.05

# Liquidity filter thresholds (component C step 5) -- a contract below
# either is excluded from the signals export.
MIN_VOLUME = 10
MIN_OPEN_INTEREST = 50

# Delta target for the skew reads (component C step 6) -- matches the
# options-playbook skill's own recommendation (greeks-and-volatility.md
# SS4.2) to track skew by delta rather than %-OTM.
SKEW_DELTA_TARGET = 0.25

# Cloud fetch (component B): only expirations within this many days out.
MAX_DTE_DAYS = 75

# ATR refresh cadence (New Data Prerequisites item 1b) -- ATR is a
# slow-moving 14-day average, so a weekly local recompute is enough.
ATR_HISTORY_WINDOW = 14
ATR_REFRESH_DAYS = 7

# Strategy-engine constants (docs/superpowers/specs/2026-09-05-strategy-engine-design.md)

# directional-strategies.md SS5: equity underlying-liquidity floor.
EQUITY_MIN_DAILY_VOLUME = 50000

# income-strategies.md SS3 / spreads-and-combinations.md SS1: vertical
# credit spread DTE window and delta band (band, not a fixed delta --
# strike selection is a scoring matter, not a gate).
VERTICAL_MIN_DTE = 30
VERTICAL_MAX_DTE = 60
VERTICAL_DELTA_BAND = (0.10, 0.30)
VERTICAL_SPREAD_WIDTHS = [5, 10]

# income-strategies.md SS4 / spreads-and-combinations.md SS2: iron
# condor delta target and DTE window (45-75 is this spec's own
# operationalization of the book's "around 60 days," not a book number).
CONDOR_DELTA_MIN = 0.10
CONDOR_DELTA_MAX = 0.15
CONDOR_MIN_DTE = 45
CONDOR_MAX_DTE = 75

# spreads-and-combinations.md SS4: calendar entry thresholds. 10 days is
# this spec's own operationalization of "avoid the final days before
# expiration" -- not a book number.
CALENDAR_MIN_FRONT_DAYS = 10
CALENDAR_LONG_PREMIUM_MIN = 0.10
CALENDAR_LONG_PREMIUM_MAX = 0.25
CALENDAR_SHORT_DISCOUNT = 0.10

# risk-management-and-position-sizing.md SS6 (Chen/Sebastian ch.3): 2%
# max risk per trade. ACCOUNT_EQUITY is a fixed constant the user edits
# directly (same precedent as RISK_FREE_RATE) -- no account-balance data
# source exists in this project.
ACCOUNT_EQUITY = 100000
MAX_LOSS_PCT_PER_TRADE = 0.02

# Number of ranked candidates published to the recommendation ledger.
TOP_N_CANDIDATES = 20

# risk-management-and-position-sizing.md SS8 (Chen/Sebastian ch.3/8/11):
# "units" -- cheap, deep-OTM tail hedges. Priority-ordered fallback
# chains per hedge type (New Data Prerequisites item 4) -- component B's
# existing skip-and-continue handling is what makes the fallback work:
# if a symbol isn't in that day's signals, it's simply not considered.
UNIT_MAX_DELTA = 0.05
UNIT_MAX_PRICE = 3.0
TAIL_HEDGE_PRIORITY = {
    "equity downside": ["^SPX", "SPY"],
    "volatility spike": ["^VIX", "VXX", "UVXY"],
}
# Option type per hedge type: Chen/Sebastian ch.3 names OTM puts on the
# S&P 500 and OTM calls on the VIX. Calls on VXX/UVXY (long-volatility
# ETPs) are this project's own extension of the VIX-call rule.
TAIL_HEDGE_OPTION_TYPE = {
    "equity downside": "put",
    "volatility spike": "call",
}

# Exit-rule simulation thresholds (docs/superpowers/specs/2026-09-05-strategy-comparison-design.md)
CONDOR_EXIT_TARGET_PCT = 0.55
CONDOR_EXIT_TIME_DTE = 30
VERTICAL_EXIT_TARGET_PCT = 0.10
CALENDAR_EXIT_TARGET_PCT = 0.05
CALENDAR_EXIT_STOP_PCT = 0.10
DIAGONAL_EXIT_TARGET_PCT = 0.05
DIAGONAL_EXIT_STOP_PCT = 0.10
# Short calendar stop (owner, 2026-11-18): Chen/Sebastian ch.9 says "never
# lose more than 10% of the original margin". For a long calendar the
# margin is the debit, so 10% of the debit is the book rule. For a short
# calendar the margin is far larger than the credit, so its stop is now
# 10% of an ESTIMATED original margin. The estimate is NOT from the books
# (they give no margin formula): it is the standard exchange rule for an
# uncovered short option -- the bought front month expires first, so it
# does not cover the sold back month -- i.e. the option's price plus the
# larger of (rate x underlying, less any out-of-the-money amount) and
# (10% of the underlying for a call / of the strike for a put), plus the
# price paid for the bought option. A broker's real figure, or portfolio
# margin, will differ.
NAKED_MARGIN_RATE_EQUITY = 0.20
NAKED_MARGIN_RATE_INDEX = 0.15   # broad-based index options (symbols starting "^")
NAKED_MARGIN_MIN_RATE = 0.10

# Entry gate for calendars and double diagonals (owner, 2026-11-18; the
# project's own rule, not a book rule). The 5% exit target, in dollars,
# must be at least half the combined bid-ask width of the legs. Below
# that, the target and stop sit inside the quote and fire on noise: in
# the 18 Nov study 78-79% of exits outside ^SPX were moves smaller than
# half the quote width (studies/exit_rule_study.py).
QUOTE_WIDTH_GATE_STRATEGIES = ("long calendar", "short calendar", "double diagonal")
# directional-strategies.md SS6: "individually-chosen stop-loss...
# below the theoretical max loss" -- no book-given fraction, so 50%/200%
# of premium are this spec's own choice (see the design spec's rationale).
DIRECTIONAL_STOP_PCT = 0.50
DIRECTIONAL_TARGET_PCT = 2.00

# Minimum terminal trades before an aggregate stat is reported as
# meaningful rather than flagged "too few trades yet."
MIN_TERMINAL_TRADES_FOR_STATS = 5

# Selection-label thesis threshold (sub-project 5): a thesis criterion
# (iv_richness, skew_quality, term_structure, directional_alignment)
# must score at or above this to count as a driver of the label -- a
# book-consistent but not book-mandated bar for "meaningfully above the
# 50 NEUTRAL baseline," not a book number.
LABEL_THESIS_THRESHOLD = 65.0

# Sub-project 5: stricter evidence bar before generating an actual
# tuning suggestion (vs. the weekly report's looser MIN_TERMINAL_TRADES_FOR_STATS).
MIN_TRADES_FOR_TUNING_SUGGESTION = 10

# Tier-2 exit-side sweep grid for directional longs -- an
# implementation-time choice of which alternate values to test, not a
# book number (see adaptive-tuning-design.md). The only Tier-2 pair
# eligible for sweeping; every other Tier-2 constant lives in
# strategy_rules.py's builders and is out of scope for this sub-project.
DIRECTIONAL_STOP_PCT_GRID = [0.40, 0.50, 0.60]
DIRECTIONAL_TARGET_PCT_GRID = [1.5, 1.75, 2.0, 2.25]

# ATM implied-volatility reading (pipeline/merge_and_score.py, _atm_iv).
# A strike only counts if its quote is live: a real two-sided bid/ask that
# is not flagged wide, and a trade within ATM_MAX_TRADE_AGE_DAYS calendar
# days. The reading is the median over the ATM_STRIKES_USED live strikes
# nearest the underlying price, none further than ATM_MAX_MONEYNESS_GAP
# from it. All three numbers are this project's own operationalization
# (added 17 Nov 2026 after BABA's Jan-2027 expiry read 164% from one
# strike that last traded in May 2025) -- not book numbers.
ATM_MAX_TRADE_AGE_DAYS = 7
ATM_STRIKES_USED = 3
ATM_MAX_MONEYNESS_GAP = 0.15
