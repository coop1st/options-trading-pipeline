"""
The ATM-IV and skew history, published as one small CSV per scored day
under data/github_sync/iv_history/.

Scoring a day needs two things beyond that day's own snapshot: the
ATM-IV history (for the 90-day IV percentile and the calendar
term-structure gate) and the skew history. Both used to live only in the
local SQLite database, which is why scoring could only run on the PC.
Publishing them here lets any machine -- a GitHub Actions runner starting
from an empty database included -- rebuild exactly the history it needs
in a few seconds: load_into_db() before scoring, export_date() after.

One file per day (never rewritten once its day is scored) keeps the git
history small: a new small file per trading day instead of a
multi-megabyte file re-committed nightly.
"""
import csv
from datetime import date, timedelta

import db
from config import PROJECT_DIR

IV_HISTORY_DIR = PROJECT_DIR / "data" / "github_sync" / "iv_history"
COLUMNS = ["symbol", "expiration", "atm_iv", "skew_put_pct_of_atm", "skew_call_pct_of_atm"]

# Scoring looks back 90 calendar days; load a little more than that.
LOAD_WINDOW_DAYS = 130


def _num(value):
    return float(value) if value not in ("", None) else None


def _cell(value):
    return "" if value is None else value


def published_dates():
    if not IV_HISTORY_DIR.exists():
        return []
    return sorted(f.stem for f in IV_HISTORY_DIR.glob("*.csv"))


def export_date(snapshot_date):
    """Writes data/github_sync/iv_history/{snapshot_date}.csv from the
    database's two history tables. Returns the path, or None if the
    database holds no history for that date."""
    atm = db.get_atm_iv_rows_for_date(snapshot_date)
    skew = db.get_skew_rows_for_date(snapshot_date)
    keys = sorted(set(atm) | set(skew))
    if not keys:
        return None
    IV_HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    path = IV_HISTORY_DIR / f"{snapshot_date}.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(COLUMNS)
        for key in keys:
            put, call = skew.get(key, (None, None))
            writer.writerow([key[0], key[1], _cell(atm.get(key)), _cell(put), _cell(call)])
    return path


def export_missing():
    """Publishes a file for every date the database has history for but
    the folder doesn't (the days scored locally before this folder
    existed). Returns the list of paths written."""
    have = set(published_dates())
    written = []
    for snapshot_date in db.get_history_dates():
        if snapshot_date not in have:
            path = export_date(snapshot_date)
            if path is not None:
                written.append(path)
    return written


def load_into_db(as_of=None):
    """Upserts every published day within LOAD_WINDOW_DAYS of as_of
    (default today) into the database's history tables. Idempotent.
    Returns the number of day-files loaded."""
    as_of = as_of or date.today()
    cutoff = (as_of - timedelta(days=LOAD_WINDOW_DAYS)).isoformat()
    loaded = 0
    for snapshot_date in published_dates():
        if snapshot_date < cutoff:
            continue
        atm_rows, skew_rows = [], []
        with open(IV_HISTORY_DIR / f"{snapshot_date}.csv", newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                atm_iv = _num(r["atm_iv"])
                put, call = _num(r["skew_put_pct_of_atm"]), _num(r["skew_call_pct_of_atm"])
                if atm_iv is not None:
                    atm_rows.append({"symbol": r["symbol"], "expiration": r["expiration"],
                                     "snapshot_date": snapshot_date, "atm_iv": atm_iv})
                if put is not None or call is not None:
                    skew_rows.append({"symbol": r["symbol"], "expiration": r["expiration"],
                                      "snapshot_date": snapshot_date,
                                      "skew_put_pct_of_atm": put, "skew_call_pct_of_atm": call})
        if atm_rows:
            db.upsert_atm_iv_history(atm_rows)
        if skew_rows:
            db.upsert_skew_history(skew_rows)
        loaded += 1
    return loaded
