"""
Verifies the pieces that let scoring run on any machine and never lose a
day: merge_and_score.select_dates_to_score (which days to score, and from
which session) and iv_history's publish/load round trip through an empty
throwaway database. No pytest -- run directly and inspect output.

Run: python pipeline/verify_score_all_days.py
"""
import sys
import tempfile
from datetime import date
from pathlib import Path

import config

ALL_OK = True


def check(label, condition):
    global ALL_OK
    print(f"{'OK' if condition else 'FAIL'}: {label}")
    ALL_OK = ALL_OK and condition


def verify_select_dates():
    from merge_and_score import select_dates_to_score

    all3 = {"open", "mid", "close"}
    sessions = {"2026-11-10": all3, "2026-11-11": {"mid", "close"}, "2026-11-12": all3, "2026-11-13": all3}

    check("every unscored day is picked, oldest first -- not only the newest",
          select_dates_to_score(sessions, {"2026-11-10"}) ==
          [("2026-11-11", "close"), ("2026-11-12", "close"), ("2026-11-13", "close")])
    check("nothing to do when every day is scored",
          select_dates_to_score(sessions, set(sessions)) == [])
    check("a gap in the middle is filled even when the newest day is scored",
          select_dates_to_score(sessions, {"2026-11-10", "2026-11-11", "2026-11-13"}) == [("2026-11-12", "close")])

    waiting = dict(sessions, **{"2026-11-16": {"open", "mid"}})
    check("the newest day is NOT scored from 'mid' while its close may still land",
          select_dates_to_score(waiting, set(sessions)) == [])

    no_close = {"2026-10-05": {"open", "mid"}, "2026-10-06": all3}
    check("an older day whose close never landed falls back to 'mid'",
          select_dates_to_score(no_close, set()) == [("2026-10-05", "mid"), ("2026-10-06", "close")])
    check("...and to 'open' when that is all there is",
          select_dates_to_score({"2026-10-05": {"open"}, "2026-10-06": all3}, {"2026-10-06"}) == [("2026-10-05", "open")])
    check("no snapshots at all -> nothing to score",
          select_dates_to_score({}, set()) == [])


def verify_iv_history_round_trip():
    import db
    import iv_history

    real_db, real_dir = config.DB_PATH, iv_history.IV_HISTORY_DIR
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        try:
            iv_history.IV_HISTORY_DIR = tmp / "iv_history"

            # A "PC" database with two scored days.
            config.DB_PATH = tmp / "pc.db"
            db.init_db()
            db.upsert_atm_iv_history([
                {"symbol": "AAA", "expiration": "2026-12-18", "snapshot_date": "2026-11-12", "atm_iv": 0.31},
                {"symbol": "AAA", "expiration": "2027-01-15", "snapshot_date": "2026-11-12", "atm_iv": 0.29},
                {"symbol": "AAA", "expiration": "2026-12-18", "snapshot_date": "2026-11-13", "atm_iv": 0.33},
                {"symbol": "BBB", "expiration": "2026-12-18", "snapshot_date": "2026-11-13", "atm_iv": 0.5},
            ])
            db.upsert_skew_history([
                {"symbol": "AAA", "expiration": "2026-12-18", "snapshot_date": "2026-11-13",
                 "skew_put_pct_of_atm": 118.2, "skew_call_pct_of_atm": None},
            ])
            written = iv_history.export_missing()
            check("one file is published per scored day", sorted(p.name for p in written) ==
                  ["2026-11-12.csv", "2026-11-13.csv"])
            check("publishing again writes nothing new", iv_history.export_missing() == [])

            # A "cloud runner": empty database, only the published files.
            config.DB_PATH = tmp / "cloud.db"
            db.init_db()
            check("an empty database starts with no history",
                  db.get_atm_iv_history("AAA", "2026-12-18", "2026-11-14") == [])
            loaded = iv_history.load_into_db(as_of=date(2026, 11, 16))
            check("both day-files load", loaded == 2)
            check("ATM-IV history matches the PC database",
                  sorted(db.get_atm_iv_history("AAA", "2026-12-18", "2026-11-14")) == [0.31, 0.33])
            check("history strictly before a date excludes that date (no look-ahead)",
                  db.get_atm_iv_history("AAA", "2026-12-18", "2026-11-13") == [0.31])
            check("term-structure spread history survives the round trip",
                  [round(x, 4) for x in db.get_term_structure_spread_history(
                      "AAA", "2026-12-18", "2027-01-15", "2026-11-14")] == [0.02])
            check("skew survives, including a blank side",
                  db.get_skew_rows_for_date("2026-11-13") == {("AAA", "2026-12-18"): (118.2, None)})
            check("loading twice changes nothing", iv_history.load_into_db(as_of=date(2026, 11, 16)) == 2 and
                  sorted(db.get_atm_iv_history("AAA", "2026-12-18", "2026-11-14")) == [0.31, 0.33])
            check("files older than the look-back window are skipped",
                  iv_history.load_into_db(as_of=date(2027, 6, 1)) == 0)
        finally:
            config.DB_PATH, iv_history.IV_HISTORY_DIR = real_db, real_dir


if __name__ == "__main__":
    verify_select_dates()
    verify_iv_history_round_trip()
    print("\nALL OK" if ALL_OK else "\nFAILURES ABOVE")
    sys.exit(0 if ALL_OK else 1)
