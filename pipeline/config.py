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
