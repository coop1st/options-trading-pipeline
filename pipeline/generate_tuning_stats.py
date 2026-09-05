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
