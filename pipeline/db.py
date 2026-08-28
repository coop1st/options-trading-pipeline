"""SQLite schema and connection helper for the options data pipeline."""
import sqlite3
from contextlib import contextmanager

from config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS options_chains (
    symbol TEXT NOT NULL,
    snapshot_date TEXT NOT NULL,
    session TEXT NOT NULL,
    expiration TEXT NOT NULL,
    contract_symbol TEXT NOT NULL,
    type TEXT NOT NULL,
    strike REAL,
    last_price REAL,
    bid REAL,
    ask REAL,
    volume INTEGER,
    open_interest INTEGER,
    implied_volatility REAL,
    in_the_money INTEGER,
    last_trade_date TEXT,
    underlying_price REAL,
    PRIMARY KEY (contract_symbol, snapshot_date, session)
);
CREATE INDEX IF NOT EXISTS idx_options_symbol_date ON options_chains(symbol, snapshot_date);

CREATE TABLE IF NOT EXISTS merge_log (
    snapshot_file TEXT PRIMARY KEY,
    merged_at TEXT,
    rows INTEGER
);

CREATE TABLE IF NOT EXISTS atm_iv_history (
    symbol TEXT NOT NULL,
    expiration TEXT NOT NULL,
    snapshot_date TEXT NOT NULL,
    atm_iv REAL,
    PRIMARY KEY (symbol, expiration, snapshot_date)
);
"""


@contextmanager
def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_connection() as conn:
        conn.executescript(SCHEMA)


def is_merged(snapshot_file):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT 1 FROM merge_log WHERE snapshot_file = ?", (snapshot_file,)
        ).fetchone()
        return row is not None


def mark_merged(snapshot_file, n_rows):
    with get_connection() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO merge_log (snapshot_file, merged_at, rows) "
            "VALUES (?, datetime('now'), ?)",
            (snapshot_file, n_rows),
        )


def upsert_options_chain(rows):
    """rows: iterable of dicts with symbol, snapshot_date, session,
    expiration, contract_symbol, type, strike, last_price, bid, ask,
    volume, open_interest, implied_volatility, in_the_money,
    last_trade_date, underlying_price"""
    with get_connection() as conn:
        conn.executemany(
            """
            INSERT INTO options_chains (
                symbol, snapshot_date, session, expiration, contract_symbol,
                type, strike, last_price, bid, ask, volume, open_interest,
                implied_volatility, in_the_money, last_trade_date, underlying_price
            ) VALUES (
                :symbol, :snapshot_date, :session, :expiration, :contract_symbol,
                :type, :strike, :last_price, :bid, :ask, :volume, :open_interest,
                :implied_volatility, :in_the_money, :last_trade_date, :underlying_price
            )
            ON CONFLICT(contract_symbol, snapshot_date, session) DO UPDATE SET
                last_price=excluded.last_price, bid=excluded.bid, ask=excluded.ask,
                volume=excluded.volume, open_interest=excluded.open_interest,
                implied_volatility=excluded.implied_volatility,
                in_the_money=excluded.in_the_money,
                last_trade_date=excluded.last_trade_date,
                underlying_price=excluded.underlying_price
            """,
            rows,
        )


def upsert_atm_iv_history(rows):
    """rows: iterable of dicts with symbol, expiration, snapshot_date, atm_iv"""
    with get_connection() as conn:
        conn.executemany(
            """
            INSERT INTO atm_iv_history (symbol, expiration, snapshot_date, atm_iv)
            VALUES (:symbol, :expiration, :snapshot_date, :atm_iv)
            ON CONFLICT(symbol, expiration, snapshot_date) DO UPDATE SET
                atm_iv=excluded.atm_iv
            """,
            rows,
        )


def get_atm_iv_history(symbol, expiration, before_date, window_days=90):
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT atm_iv FROM atm_iv_history
            WHERE symbol = ? AND expiration = ? AND snapshot_date < ?
            AND snapshot_date >= date(?, ?)
            """,
            (symbol, expiration, before_date, before_date, f"-{window_days} days"),
        ).fetchall()
        return [r[0] for r in rows if r[0] is not None]


def get_most_recent_snapshot_date():
    """Returns the most recent snapshot_date present in options_chains (as
    an ISO date string), or None if the table is empty. Used instead of
    date.today() to decide what to score -- the script runs "whenever the
    PC is next on, overnight," so today's date and the most recently
    merged snapshot's date are often not the same."""
    with get_connection() as conn:
        row = conn.execute("SELECT MAX(snapshot_date) FROM options_chains").fetchone()
        return row[0] if row and row[0] is not None else None


def get_latest_snapshot_rows(snapshot_date):
    """Returns (rows, session) for the most complete session captured that
    day, preferring close > mid > open -- if a symbol was only captured
    during an earlier session (e.g. skipped during 'close' due to a
    rate-limit), it's simply absent from that day's signals export rather
    than merged across sessions. Returns ([], None) if nothing was merged
    for that date yet."""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        for session in ("close", "mid", "open"):
            rows = conn.execute(
                "SELECT * FROM options_chains WHERE snapshot_date = ? AND session = ?",
                (snapshot_date, session),
            ).fetchall()
            if rows:
                return [dict(r) for r in rows], session
        return [], None
