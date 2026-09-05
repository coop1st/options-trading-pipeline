"""
Monthly tuning-stats generator (sub-project 5). Purely reads/writes
repo-local files -- no external fetch -- runs entirely in GitHub
Actions, matching track_outcomes.py/compare_strategies.py's split.
Publishes raw, mechanical statistics only; a separate monthly Claude
Code routine applies judgment to turn well-supported findings into
suggestions -- this script never authors a suggestion itself.

Run from the repo root: `python pipeline/generate_tuning_stats.py`
"""
from scipy.stats import spearmanr

from compare_strategies import CRITERIA, _load_terminal_trades


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
