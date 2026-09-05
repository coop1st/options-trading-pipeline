"""
Monthly tuning-stats generator (sub-project 5). Purely reads/writes
repo-local files -- no external fetch -- runs entirely in GitHub
Actions, matching track_outcomes.py/compare_strategies.py's split.
Publishes raw, mechanical statistics only; a separate monthly Claude
Code routine applies judgment to turn well-supported findings into
suggestions -- this script never authors a suggestion itself.

Run from the repo root: `python pipeline/generate_tuning_stats.py`
"""
import csv
import json
import statistics
import subprocess
from datetime import date

from scipy.stats import spearmanr

from compare_strategies import CRITERIA, _load_terminal_trades, by_label
from config import DIRECTIONAL_STOP_PCT_GRID, DIRECTIONAL_TARGET_PCT_GRID, MIN_TRADES_FOR_TUNING_SUGGESTION, PROJECT_DIR
from track_outcomes import SCOREABLE_STATUSES, _entry_info_for_trade, _load_all_signals, evaluate_trade

LEDGER_PATH = PROJECT_DIR / "data" / "github_sync" / "options_ledger" / "options_recommendation_ledger.csv"
STATS_PATH = PROJECT_DIR / "data" / "github_sync" / "options_ledger" / "tuning_stats_latest.json"


def _spearman_or_none(pairs):
    if len(pairs) < 3:
        return None
    xs, ys = zip(*pairs)
    if len(set(xs)) < 2:
        return None  # a constant series has no defined correlation
    corr, _pvalue = spearmanr(xs, ys)
    return None if corr != corr else round(float(corr), 4)  # NaN guard


def compute_criterion_correlations(trades):
    """{criterion: {'n': int, 'correlation': float|None}} -- Spearman
    rank correlation between each of the 7 criteria's stored score and
    realized_pct, across trades where both are present."""
    results = {}
    for criterion in CRITERIA:
        pairs = [
            (t[criterion], t["realized_pct"]) for t in trades
            if t.get(criterion) is not None and t.get("realized_pct") is not None
        ]
        results[criterion] = {"n": len(pairs), "correlation": _spearman_or_none(pairs)}
    return results


def _composite_correlation(trades, weights):
    """Recomputes what composite_score would have been under an
    alternate weighting (only criteria actually present per trade
    contribute, matching by_criterion's existing missing-data
    convention), and returns its Spearman correlation with realized_pct."""
    pairs = []
    for t in trades:
        if t.get("realized_pct") is None:
            continue
        available = [(c, t[c]) for c in CRITERIA if t.get(c) is not None]
        if not available:
            continue
        weight_used = sum(weights[c] for c, _ in available)
        if weight_used <= 0:
            continue
        composite = sum(weights[c] * v for c, v in available) / weight_used
        pairs.append((composite, t["realized_pct"]))
    return _spearman_or_none(pairs)


def compute_weight_sensitivity(trades):
    """For each criterion, recomputes composite_score with that
    criterion's weight doubled (others reduced proportionally) and
    halved (others increased proportionally), and compares the
    resulting Spearman correlation with realized_pct against the
    current equal-weight baseline. A criterion whose doubled weight
    clearly improves correlation is a reweighting candidate; one whose
    halved weight improves it is a down-weighting candidate -- the
    routine, not this function, decides what "clearly" means against
    the evidence bar."""
    n = len(CRITERIA)
    baseline_weights = {c: 1.0 for c in CRITERIA}
    baseline_correlation = _composite_correlation(trades, baseline_weights)

    results = {}
    for criterion in CRITERIA:
        others_doubled = (n - 2.0) / (n - 1)  # keeps sum of weights == n
        others_halved = (n - 0.5) / (n - 1)
        doubled_weights = {c: (2.0 if c == criterion else others_doubled) for c in CRITERIA}
        halved_weights = {c: (0.5 if c == criterion else others_halved) for c in CRITERIA}
        results[criterion] = {
            "baseline_correlation": baseline_correlation,
            "doubled_weight_correlation": _composite_correlation(trades, doubled_weights),
            "halved_weight_correlation": _composite_correlation(trades, halved_weights),
        }
    return results


def sweep_directional_thresholds(directional_trades, stop_grid, target_grid, signals_by_date, today):
    """directional_trades: {trade_id: (strategy, legs)} for terminal
    long call/put trades only -- kept as a parameter (not read from the
    ledger internally) so this is testable with synthetic fixtures. For
    each (stop_pct, target_pct) grid point, re-evaluates every trade's
    already-known price history under that alternate pair -- a genuine
    counterfactual, since the price path is real and already fully
    resolved. Returns {(stop_pct, target_pct): {'n':, 'win_rate':, 'avg_realized_pct':}}."""
    grid_results = {}
    for stop_pct in stop_grid:
        for target_pct in target_grid:
            outcomes = []
            for strategy, legs in directional_trades.values():
                status, _date, realized_pct = evaluate_trade(
                    strategy, legs, signals_by_date, today,
                    evaluator_overrides={"stop_pct": stop_pct, "target_pct": target_pct},
                )
                if status in SCOREABLE_STATUSES and realized_pct is not None:
                    outcomes.append(realized_pct)
            n = len(outcomes)
            grid_results[(stop_pct, target_pct)] = {
                "n": n,
                "win_rate": round(sum(1 for r in outcomes if r > 0) / n, 3) if n else None,
                "avg_realized_pct": round(statistics.mean(outcomes), 4) if outcomes else None,
            }
    return grid_results


def load_directional_trade_legs():
    """{trade_id: (strategy, legs)} for every terminal long call/put
    trade in the real ledger -- the I/O counterpart to
    sweep_directional_thresholds, kept separate per this project's
    established pure-logic/I/O split."""
    if not LEDGER_PATH.exists():
        return {}
    with open(LEDGER_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    by_trade_id = {}
    for row in rows:
        by_trade_id.setdefault(row["trade_id"], []).append(row)

    result = {}
    for trade_id, trade_rows in by_trade_id.items():
        strategy = trade_rows[0]["strategy"]
        if strategy not in ("long call", "long put"):
            continue
        if trade_rows[0].get("outcome_status") not in SCOREABLE_STATUSES:
            continue
        _entry_date, legs = _entry_info_for_trade(trade_rows)
        if legs:
            result[trade_id] = (strategy, legs)
    return result


def git_pull():
    result = subprocess.run(["git", "pull"], cwd=PROJECT_DIR, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"git pull failed: {result.stderr}")
    return result.stdout.strip()


def commit_and_push(paths, message):
    paths = [str(p) for p in paths]
    subprocess.run(["git", "add", *paths], cwd=PROJECT_DIR, check=True, timeout=60)
    diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=PROJECT_DIR, timeout=30)
    if diff.returncode == 0:
        return "no_changes"
    subprocess.run(["git", "commit", "-m", message], cwd=PROJECT_DIR, check=True, timeout=60)
    subprocess.run(["git", "push"], cwd=PROJECT_DIR, check=True, timeout=120)
    return "pushed"


def run_generate_tuning_stats():
    print("Pulling latest from GitHub...")
    print(git_pull())

    if not LEDGER_PATH.exists():
        print("No recommendation ledger yet -- nothing to analyze")
        return {"status": "no_data"}

    trades = _load_terminal_trades()
    print(f"{len(trades)} scoreable terminal trade(s) found")

    correlations = compute_criterion_correlations(trades)
    sensitivity = compute_weight_sensitivity(trades)
    label_rows = by_label(trades)

    directional_trades = load_directional_trade_legs()
    if len(directional_trades) >= MIN_TRADES_FOR_TUNING_SUGGESTION:
        signals_by_date = _load_all_signals()
        sweep = sweep_directional_thresholds(
            directional_trades, DIRECTIONAL_STOP_PCT_GRID, DIRECTIONAL_TARGET_PCT_GRID,
            signals_by_date, date.today(),
        )
        sweep_json = {f"{s}/{t}": v for (s, t), v in sweep.items()}
    else:
        print(f"Only {len(directional_trades)} terminal directional trade(s) "
              f"(< {MIN_TRADES_FOR_TUNING_SUGGESTION}) -- skipping exit-side sweep")
        sweep_json = None

    stats = {
        "generated_date": date.today().isoformat(),
        "total_terminal_trades": len(trades),
        "min_trades_for_suggestion": MIN_TRADES_FOR_TUNING_SUGGESTION,
        "criterion_correlations": correlations,
        "weight_sensitivity": sensitivity,
        "label_performance": label_rows,
        "directional_exit_sweep": sweep_json,
    }

    STATS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STATS_PATH, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
    print(f"Wrote stats to {STATS_PATH}")

    status = commit_and_push([STATS_PATH], f"Tuning stats: {len(trades)} terminal trades, {date.today().isoformat()}")
    print(f"Publish status: {status}")
    return {"status": status, "terminal_trades": len(trades)}


if __name__ == "__main__":
    print(run_generate_tuning_stats())
