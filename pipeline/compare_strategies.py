"""
Aggregation script (sub-project 4). Reads the recommendation ledger's
scoreable terminal-outcome rows and produces two views: performance by
strategy family, and performance by scoring criterion (above/below-
median win-rate split). Purely reads/writes repo-local files -- runs
entirely in GitHub Actions.

Run from the repo root: `python pipeline/compare_strategies.py`
"""
import csv
import statistics
import subprocess

from config import MIN_TERMINAL_TRADES_FOR_STATS, PROJECT_DIR
from track_outcomes import SCOREABLE_STATUSES

LEDGER_PATH = PROJECT_DIR / "data" / "github_sync" / "options_ledger" / "options_recommendation_ledger.csv"
REPORT_PATH = PROJECT_DIR / "data" / "github_sync" / "options_ledger" / "strategy_performance_report.csv"

WINNING_STATUSES = {"HIT_TARGET", "EXPIRED_PROFIT"}
CRITERIA = [
    "iv_richness", "skew_quality", "risk_reward", "pop_proxy",
    "term_structure", "liquidity", "directional_alignment",
]


def _load_terminal_trades():
    """One dict per trade_id (deduped across its leg rows) for every
    trade_id whose outcome_status is scoreable."""
    trades = {}
    with open(LEDGER_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("outcome_status") not in SCOREABLE_STATUSES:
                continue
            trade_id = row["trade_id"]
            if trade_id in trades:
                continue
            realized_raw = row.get("realized_pct")
            realized_pct = float(realized_raw) if realized_raw not in (None, "") else None
            is_win = row["outcome_status"] in WINNING_STATUSES or (
                row["outcome_status"] == "TIME_EXIT" and realized_pct is not None and realized_pct > 0
            )
            trade = {"strategy": row["strategy"], "realized_pct": realized_pct, "is_win": is_win}
            for c in CRITERIA:
                val = row.get(c)
                trade[c] = float(val) if val not in (None, "") else None
            trades[trade_id] = trade
    return list(trades.values())


def by_family(trades):
    families = {}
    for t in trades:
        families.setdefault(t["strategy"], []).append(t)

    rows = []
    for strategy, group in families.items():
        n = len(group)
        wins = sum(1 for t in group if t["is_win"])
        pcts = [t["realized_pct"] for t in group if t["realized_pct"] is not None]
        rows.append({
            "strategy": strategy,
            "sample_size": n,
            "win_rate": round(wins / n, 3) if n else None,
            "avg_realized_pct": round(statistics.mean(pcts), 4) if pcts else None,
            "note": "" if n >= MIN_TERMINAL_TRADES_FOR_STATS else "too few trades to be meaningful yet",
        })
    return rows


def by_criterion(trades):
    rows = []
    for criterion in CRITERIA:
        scored = [t for t in trades if t.get(criterion) is not None]
        if len(scored) < MIN_TERMINAL_TRADES_FOR_STATS:
            rows.append({
                "criterion": criterion, "sample_size": len(scored),
                "above_median_win_rate": None, "below_median_win_rate": None,
                "note": "too few trades to be meaningful yet",
            })
            continue
        median = statistics.median(t[criterion] for t in scored)
        above = [t for t in scored if t[criterion] >= median]
        below = [t for t in scored if t[criterion] < median]
        rows.append({
            "criterion": criterion,
            "sample_size": len(scored),
            "above_median_win_rate": round(sum(1 for t in above if t["is_win"]) / len(above), 3) if above else None,
            "below_median_win_rate": round(sum(1 for t in below if t["is_win"]) / len(below), 3) if below else None,
            "note": "",
        })
    return rows


def commit_and_push(paths, message):
    paths = [str(p) for p in paths]
    subprocess.run(["git", "add", *paths], cwd=PROJECT_DIR, check=True, timeout=60)
    diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=PROJECT_DIR, timeout=30)
    if diff.returncode == 0:
        return "no_changes"
    subprocess.run(["git", "commit", "-m", message], cwd=PROJECT_DIR, check=True, timeout=60)
    subprocess.run(["git", "push"], cwd=PROJECT_DIR, check=True, timeout=120)
    return "pushed"


def git_pull():
    result = subprocess.run(["git", "pull"], cwd=PROJECT_DIR, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"git pull failed: {result.stderr}")
    return result.stdout.strip()


def run_compare_strategies():
    print("Pulling latest from GitHub...")
    print(git_pull())

    if not LEDGER_PATH.exists():
        print("No recommendation ledger yet -- nothing to compare")
        return {"status": "no_data"}

    trades = _load_terminal_trades()
    print(f"{len(trades)} scoreable terminal trade(s) found")

    family_rows = by_family(trades)
    criterion_rows = by_criterion(trades)

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["section", "key", "sample_size", "win_rate_or_above_median", "avg_realized_pct_or_below_median", "note"])
        for r in family_rows:
            writer.writerow(["by_family", r["strategy"], r["sample_size"], r["win_rate"], r["avg_realized_pct"], r["note"]])
        for r in criterion_rows:
            writer.writerow(["by_criterion", r["criterion"], r["sample_size"], r["above_median_win_rate"], r["below_median_win_rate"], r["note"]])

    status = commit_and_push([REPORT_PATH], f"Strategy performance report: {len(trades)} terminal trades")
    print(f"Publish status: {status}")
    return {"status": status, "terminal_trades": len(trades)}


if __name__ == "__main__":
    print(run_compare_strategies())
