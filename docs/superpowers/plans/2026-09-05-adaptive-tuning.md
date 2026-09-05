# Adaptive Tuning Suggestions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a monthly, evidence-gated tuning-suggestion system: rank-correlation analysis per scoring criterion, a genuine counterfactual sweep of the one Tier-2 exit-side parameter pair that's actually eligible (`DIRECTIONAL_STOP_PCT`/`TARGET_PCT`), a weight-sensitivity check for the composite score, and label-driven filtering signals — published as raw mechanical stats, interpreted by a monthly cloud routine that drafts a digest and commits a suggestions file, never auto-applying anything.

**Architecture:** `pipeline/generate_tuning_stats.py` runs monthly via GitHub Actions (mechanical, no external fetch, matching `track_outcomes.py`/`compare_strategies.py`'s existing split), reusing `compare_strategies.py`'s ledger-loading and by-label logic plus a small backward-compatible refactor to `track_outcomes.py`'s directional-long evaluator so it accepts optional threshold overrides for the sweep. It publishes raw stats as JSON. A new monthly Claude Code routine reads that JSON, applies judgment (sample-size/robustness checks against the evidence bar), drafts an email, and commits `tuning_suggestions_{YYYY-MM}.md` — never editing `config.py`/`scoring.py` directly.

**Tech Stack:** Python 3.12, pandas, scipy (`spearmanr`, already a dependency), stdlib `statistics`/`json` — no new dependencies.

**Spec:** `docs/superpowers/specs/2026-09-05-adaptive-tuning-design.md`

## Global Constraints

- **The three-tier boundary is absolute**: this plan never writes code that could suggest changing a Tier-1 (book-verbatim) constant. The only Tier-2 parameter pair swept is `DIRECTIONAL_STOP_PCT`/`DIRECTIONAL_TARGET_PCT` — every other Tier-2 constant (`CONDOR_MIN_DTE`/`MAX_DTE`, `CALENDAR_MIN_FRONT_DAYS`, `VERTICAL_SPREAD_WIDTHS`, `VERTICAL_DELTA_BAND`) lives in `strategy_rules.py`'s builders and is explicitly out of scope per the spec's Non-goals — this plan does not touch `strategy_rules.py` at all.
- **Nothing in this plan ever calls `git commit`/`git push` against `config.py` or `scoring.py`.** The mechanical script only ever writes a JSON stats file; only the cloud routine writes the dated suggestions markdown file, and only that file.
- Evidence bar: `MIN_TRADES_FOR_TUNING_SUGGESTION = 10`, stricter than the weekly report's `MIN_TERMINAL_TRADES_FOR_STATS = 5`. Below this bar, raw numbers are still computed and published (transparency) but the routine must not present them as an actionable suggestion.
- Spearman rank correlation (via `scipy.stats.spearmanr`, already a project dependency) is used throughout, not Pearson — more robust for `realized_pct`'s likely non-normal, outcome-driven distribution, per the spec.
- No pytest — every script verified by running it directly, matching this project's convention.

---

## File Structure

- **Modify** `pipeline/config.py` — 3 new constants: `MIN_TRADES_FOR_TUNING_SUGGESTION`, `DIRECTIONAL_STOP_PCT_GRID`, `DIRECTIONAL_TARGET_PCT_GRID`.
- **Modify** `pipeline/track_outcomes.py` — parameterize `_evaluate_directional_long` and thread optional overrides through `evaluate_trade`, backward-compatible.
- **Modify** `pipeline/verify_track_outcomes.py` — one new regression test confirming the override path works and doesn't change default behavior.
- **Create** `pipeline/generate_tuning_stats.py` — correlation, weight-sensitivity, exit-side sweep, label performance, orchestration.
- **Create** `pipeline/verify_generate_tuning_stats.py` — synthetic fixtures for all four analyses.
- **Create** `.github/workflows/generate-tuning-stats.yml` — monthly, mechanical.
- **Deployment step** (not a file): create the "Monthly tuning review" `RemoteTrigger` routine.

---

### Task 1: Config constants + `track_outcomes.py` override plumbing

**Files:**
- Modify: `pipeline/config.py`
- Modify: `pipeline/track_outcomes.py`
- Modify: `pipeline/verify_track_outcomes.py`
- Test: `pipeline/verify_track_outcomes.py`

**Interfaces:**
- Produces: `config.MIN_TRADES_FOR_TUNING_SUGGESTION`, `config.DIRECTIONAL_STOP_PCT_GRID`, `config.DIRECTIONAL_TARGET_PCT_GRID`; `track_outcomes.evaluate_trade(strategy, legs, signals_by_date, today, evaluator_overrides=None)` — the new optional 5th parameter, forwarded as kwargs to the evaluator, meaningful only for `_evaluate_directional_long`. Consumed by Task 4's exit-side sweep.

- [ ] **Step 1: Add the three constants to `pipeline/config.py`**

```python
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
```

- [ ] **Step 2: Parameterize `_evaluate_directional_long` in `pipeline/track_outcomes.py`**

Replace:

```python
def _evaluate_directional_long(legs, price_lookup, dte, width):
    debit = _debit_paid(legs)
    if debit <= 0:
        return None
    value = _current_value_now(legs, price_lookup)
    ratio = value / debit
    if ratio <= DIRECTIONAL_STOP_PCT:
        return "HIT_MAX_LOSS", (value - debit) / debit
    if ratio >= DIRECTIONAL_TARGET_PCT:
        return "HIT_TARGET", (value - debit) / debit
    return None
```

with:

```python
def _evaluate_directional_long(legs, price_lookup, dte, width,
                                stop_pct=DIRECTIONAL_STOP_PCT, target_pct=DIRECTIONAL_TARGET_PCT):
    """stop_pct/target_pct default to the live config constants -- the
    only reason they're parameters at all is sub-project 5's exit-side
    sweep (generate_tuning_stats.py), which re-evaluates already-
    terminal trades' known price paths under alternate values. No other
    evaluator in this module takes overrides: every other family's exit
    rule is Tier 1 (book-verbatim), never swept."""
    debit = _debit_paid(legs)
    if debit <= 0:
        return None
    value = _current_value_now(legs, price_lookup)
    ratio = value / debit
    if ratio <= stop_pct:
        return "HIT_MAX_LOSS", (value - debit) / debit
    if ratio >= target_pct:
        return "HIT_TARGET", (value - debit) / debit
    return None
```

- [ ] **Step 3: Thread `evaluator_overrides` through `evaluate_trade`**

Replace:

```python
def evaluate_trade(strategy, legs, signals_by_date, today):
    """Core re-scan-from-entry algorithm. legs: list of dicts with
    leg_role, entry_price, contract_symbol, expiration, strike.
    signals_by_date: {date_str: {contract_symbol: last_price}}. Returns
    (status, outcome_date, realized_pct); realized_pct is None for OPEN
    and UNRESOLVED_AT_EXPIRATION."""
    if strategy not in EVALUATORS:
        raise ValueError(f"No evaluator for strategy {strategy!r}")

    nearest_expiration = min(l["expiration"] for l in legs)
    width = None
    if strategy in ("vertical put credit spread", "vertical call credit spread"):
        strikes = sorted(l["strike"] for l in legs)
        width = strikes[-1] - strikes[0]

    evaluator = EVALUATORS[strategy]
    structure_type = STRUCTURE_TYPE[strategy]
```

with:

```python
def evaluate_trade(strategy, legs, signals_by_date, today, evaluator_overrides=None):
    """Core re-scan-from-entry algorithm. legs: list of dicts with
    leg_role, entry_price, contract_symbol, expiration, strike.
    signals_by_date: {date_str: {contract_symbol: last_price}}. Returns
    (status, outcome_date, realized_pct); realized_pct is None for OPEN
    and UNRESOLVED_AT_EXPIRATION. evaluator_overrides (optional dict of
    kwargs) is forwarded to the evaluator -- meaningful only for
    "long call"/"long put" (see _evaluate_directional_long); passing it
    for any other strategy will raise, since those evaluators take no
    such kwargs, by design (Tier 1 exit rules are never swept)."""
    if strategy not in EVALUATORS:
        raise ValueError(f"No evaluator for strategy {strategy!r}")

    nearest_expiration = min(l["expiration"] for l in legs)
    width = None
    if strategy in ("vertical put credit spread", "vertical call credit spread"):
        strikes = sorted(l["strike"] for l in legs)
        width = strikes[-1] - strikes[0]

    evaluator = EVALUATORS[strategy]
    structure_type = STRUCTURE_TYPE[strategy]
    overrides = evaluator_overrides or {}
```

Then update both `evaluator(legs, price_lookup, dte, width)` call sites (one inside the date loop, no others exist) to `evaluator(legs, price_lookup, dte, width, **overrides)`.

- [ ] **Step 4: Add a regression test to `pipeline/verify_track_outcomes.py`**

Add, right after the existing "long call hits 50% stop" check:

```python
    # Sub-project 5: evaluator_overrides must actually change behavior
    # (the sweep depends on this), and must not affect the default path.
    status, _, _ = evaluate_trade(
        "long call", long_call_legs, {"2026-03-01": {"TEST260601C00100000": 1.60}}, date(2026, 3, 1),
    )
    check("default thresholds: 160% of premium hits neither target nor stop yet", status == "OPEN")
    status, _, _ = evaluate_trade(
        "long call", long_call_legs, {"2026-03-01": {"TEST260601C00100000": 1.60}}, date(2026, 3, 1),
        evaluator_overrides={"target_pct": 1.5},
    )
    check("overridden target_pct=1.5: same 160% now hits HIT_TARGET", status == "HIT_TARGET")
```

- [ ] **Step 5: Run the full verification suite**

```bash
cd pipeline
python verify_track_outcomes.py
python verify_compare_strategies.py
```

Expected: `ALL_OK` for both — confirms the refactor is backward-compatible (no prior check broken) and the new override behavior works.

- [ ] **Step 6: Commit**

```bash
git add pipeline/config.py pipeline/track_outcomes.py pipeline/verify_track_outcomes.py
git commit -m "Add tuning-sweep config constants and evaluator_overrides plumbing"
```

---

### Task 2: Criterion rank-correlation

**Files:**
- Create: `pipeline/generate_tuning_stats.py` (this task's portion)
- Create: `pipeline/verify_generate_tuning_stats.py`
- Test: `pipeline/verify_generate_tuning_stats.py`

**Interfaces:**
- Consumes: `compare_strategies._load_terminal_trades`, `compare_strategies.CRITERIA` (reused directly, not duplicated).
- Produces: `compute_criterion_correlations(trades) -> dict[str, dict]` — consumed by Task 5's orchestration.

- [ ] **Step 1: Write the failing verification script first**

```python
"""
Verifies pipeline/generate_tuning_stats.py's correlation, sensitivity,
and exit-side sweep logic against synthetic fixtures. No pytest -- run
directly and inspect output.

Run: python pipeline/verify_generate_tuning_stats.py
"""
import sys
from datetime import date

from generate_tuning_stats import compute_criterion_correlations

ALL_OK = True


def check(label, condition):
    global ALL_OK
    print(f"{'OK' if condition else 'FAIL'}: {label}")
    ALL_OK = ALL_OK and condition


def _trade(realized_pct, **criteria):
    t = {"realized_pct": realized_pct}
    t.update(criteria)
    return t


def main():
    # Perfectly monotonic relationship: iv_richness strongly predicts realized_pct.
    monotonic_trades = [_trade(i * 0.1, iv_richness=i * 10.0) for i in range(1, 10)]
    corr = compute_criterion_correlations(monotonic_trades)
    check("perfectly monotonic criterion -> correlation near 1.0", corr["iv_richness"]["correlation"] > 0.99)
    check("perfectly monotonic criterion -> n == 9", corr["iv_richness"]["n"] == 9)

    # Constant criterion (no variation) -> undefined correlation, not a crash.
    constant_trades = [_trade(i * 0.1, skew_quality=50.0) for i in range(1, 10)]
    corr2 = compute_criterion_correlations(constant_trades)
    check("constant criterion -> correlation is None, not a crash", corr2["skew_quality"]["correlation"] is None)

    # Too few paired observations -> None, not a fabricated number.
    sparse_trades = [_trade(0.5, risk_reward=80.0)]
    corr3 = compute_criterion_correlations(sparse_trades)
    check("fewer than 3 pairs -> correlation is None", corr3["risk_reward"]["correlation"] is None)

    print("ALL_OK" if ALL_OK else "VERIFICATION_FAILED")
    if not ALL_OK:
        sys.exit(1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run it to verify it fails**

```bash
cd pipeline
python verify_generate_tuning_stats.py
```

Expected: `ModuleNotFoundError: No module named 'generate_tuning_stats'`.

- [ ] **Step 3: Write `pipeline/generate_tuning_stats.py` (Task 2's portion)**

```python
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
```

- [ ] **Step 4: Run the verification script and confirm it passes**

```bash
cd pipeline
python verify_generate_tuning_stats.py
```

Expected: every line prints `OK:`, final line `ALL_OK`.

- [ ] **Step 5: Commit**

```bash
git add pipeline/generate_tuning_stats.py pipeline/verify_generate_tuning_stats.py
git commit -m "Add per-criterion rank-correlation analysis"
```

---

### Task 3: Weight-sensitivity check

**Files:**
- Modify: `pipeline/generate_tuning_stats.py`
- Modify: `pipeline/verify_generate_tuning_stats.py`
- Test: `pipeline/verify_generate_tuning_stats.py`

**Interfaces:**
- Produces: `compute_weight_sensitivity(trades) -> dict[str, dict]` — consumed by Task 5's orchestration.

- [ ] **Step 1: Add the failing checks to `verify_generate_tuning_stats.py`**

```python
    # Weight sensitivity: a criterion that strongly predicts realized_pct
    # should show improved correlation when its weight is doubled.
    strong_trades = [
        {"realized_pct": i * 0.1, "iv_richness": i * 10.0, "skew_quality": 50.0,
         "risk_reward": 50.0, "pop_proxy": 50.0, "term_structure": 50.0,
         "liquidity": 50.0, "directional_alignment": 50.0}
        for i in range(1, 10)
    ]
    sensitivity = compute_weight_sensitivity(strong_trades)
    check("doubling a strongly-predictive criterion's weight improves (or holds) correlation",
          sensitivity["iv_richness"]["doubled_weight_correlation"] >= sensitivity["iv_richness"]["baseline_correlation"])
    check("halving a strongly-predictive criterion's weight worsens (or holds) correlation",
          sensitivity["iv_richness"]["halved_weight_correlation"] <= sensitivity["iv_richness"]["baseline_correlation"])
```

Update the import line to `from generate_tuning_stats import compute_criterion_correlations, compute_weight_sensitivity`.

- [ ] **Step 2: Run it to verify it fails**

```bash
cd pipeline
python verify_generate_tuning_stats.py
```

Expected: `ImportError: cannot import name 'compute_weight_sensitivity'`.

- [ ] **Step 3: Add `compute_weight_sensitivity` to `pipeline/generate_tuning_stats.py`**

```python
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
```

- [ ] **Step 4: Run the verification script and confirm it passes**

```bash
cd pipeline
python verify_generate_tuning_stats.py
```

Expected: every line prints `OK:`, final line `ALL_OK`.

- [ ] **Step 5: Commit**

```bash
git add pipeline/generate_tuning_stats.py pipeline/verify_generate_tuning_stats.py
git commit -m "Add composite-score weight-sensitivity analysis"
```

---

### Task 4: Tier-2 exit-side sweep for directional longs

**Files:**
- Modify: `pipeline/generate_tuning_stats.py`
- Modify: `pipeline/verify_generate_tuning_stats.py`
- Test: `pipeline/verify_generate_tuning_stats.py`

**Interfaces:**
- Consumes: `track_outcomes.evaluate_trade` (with `evaluator_overrides`, Task 1), `track_outcomes.SCOREABLE_STATUSES`.
- Produces: `sweep_directional_thresholds(directional_trades, stop_grid, target_grid, signals_by_date, today) -> dict[tuple, dict]` (pure, testable with synthetic fixtures) and `load_directional_trade_legs() -> dict` (I/O, reads the real ledger — kept separate from the pure sweep function, matching `track_outcomes.py`'s own pure/I/O split). Consumed by Task 5's orchestration.

- [ ] **Step 1: Add the failing checks to `verify_generate_tuning_stats.py`**

```python
    # Exit-side sweep: a known synthetic long-call price path should
    # pick out whichever grid point performs best against it.
    long_call_legs = {"trade-1": ("long call", [
        {"leg_role": "long call", "entry_price": 3.00, "contract_symbol": "TEST260601C00100000",
         "expiration": "2026-06-01", "strike": 100.0},
    ])}
    # Real price never exceeds 175% of premium (5.25) but does hit 160% (4.80) --
    # a target_pct of 1.5 should show a win here; the default 2.0 would not.
    signals_by_date = {"2026-03-01": {"TEST260601C00100000": 4.80}}
    sweep = sweep_directional_thresholds(long_call_legs, [0.50], [1.5, 2.0], signals_by_date, date(2026, 3, 1))
    check("lower target_pct grid point captures a win the default would miss",
          sweep[(0.50, 1.5)]["win_rate"] == 1.0)
    check("higher (default) target_pct grid point shows no win yet for the same trade",
          sweep[(0.50, 2.0)]["win_rate"] in (0.0, None))
```

Update the import line to also bring in `sweep_directional_thresholds`.

- [ ] **Step 2: Run it to verify it fails**

```bash
cd pipeline
python verify_generate_tuning_stats.py
```

Expected: `ImportError: cannot import name 'sweep_directional_thresholds'`.

- [ ] **Step 3: Add the sweep function and ledger loader to `pipeline/generate_tuning_stats.py`**

```python
import csv
import statistics
from pathlib import Path

from config import PROJECT_DIR
from track_outcomes import SCOREABLE_STATUSES, _entry_info_for_trade, evaluate_trade

LEDGER_PATH = PROJECT_DIR / "data" / "github_sync" / "options_ledger" / "options_recommendation_ledger.csv"


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
```

- [ ] **Step 4: Run the verification script and confirm it passes**

```bash
cd pipeline
python verify_generate_tuning_stats.py
```

Expected: every line prints `OK:`, final line `ALL_OK`.

- [ ] **Step 5: Commit**

```bash
git add pipeline/generate_tuning_stats.py pipeline/verify_generate_tuning_stats.py
git commit -m "Add Tier-2 exit-side sweep for directional long stop/target thresholds"
```

---

### Task 5: Orchestration — publish raw stats

**Files:**
- Modify: `pipeline/generate_tuning_stats.py`
- Test: manual run against real data

**Interfaces:**
- Consumes: everything from Tasks 2-4, plus `compare_strategies.by_label`.
- Produces: `run_generate_tuning_stats()` — publishes `data/github_sync/options_ledger/tuning_stats_latest.json`, commits + pushes.

- [ ] **Step 1: Append the orchestration to `pipeline/generate_tuning_stats.py`**

```python
import json
import subprocess
from datetime import date

from config import DIRECTIONAL_STOP_PCT_GRID, DIRECTIONAL_TARGET_PCT_GRID, MIN_TRADES_FOR_TUNING_SUGGESTION
from compare_strategies import by_label
from track_outcomes import _load_all_signals

STATS_PATH = PROJECT_DIR / "data" / "github_sync" / "options_ledger" / "tuning_stats_latest.json"


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
```

- [ ] **Step 2: Run it against real data**

```bash
cd "C:\Users\coope\Claude_Work\Projects\Options Trading"
python pipeline/generate_tuning_stats.py
```

Expected: `0 scoreable terminal trade(s) found` (correct — still true at this point in the project), `Only 0 terminal directional trade(s) (< 10) -- skipping exit-side sweep`, and a published JSON file with `null`/empty values throughout rather than fabricated numbers.

- [ ] **Step 3: Spot-check the published JSON is honest about having no data**

```bash
python -c "
import json
with open('data/github_sync/options_ledger/tuning_stats_latest.json') as f:
    stats = json.load(f)
print('total_terminal_trades:', stats['total_terminal_trades'])
print('directional_exit_sweep:', stats['directional_exit_sweep'])
print('sample correlation entry:', stats['criterion_correlations']['iv_richness'])
"
```

Expected: `total_terminal_trades: 0`, `directional_exit_sweep: None`, and the correlation entry shows `{'n': 0, 'correlation': None}` — no fabricated statistics.

- [ ] **Step 4: Commit**

```bash
git add pipeline/generate_tuning_stats.py
git commit -m "Add generate_tuning_stats.py orchestration: publish raw monthly stats"
```

---

### Task 6: Monthly GitHub Actions workflow

**Files:**
- Create: `.github/workflows/generate-tuning-stats.yml`

**Interfaces:**
- Consumes: `pipeline/generate_tuning_stats.py` (Tasks 2-5).

- [ ] **Step 1: Write the workflow**

```yaml
name: Generate tuning stats

# Runs entirely in the cloud, on the 1st of each month, after that
# week's compare-strategies.yml run has published fresh label/criterion
# data. Purely mechanical -- correlation, sweep, and sensitivity math,
# no external fetch, no judgment. A separate monthly Claude Code routine
# reads this output and decides what (if anything) is suggestion-worthy.

on:
  schedule:
    - cron: "0 21 1 * *"  # 1st of each month, 21:00 UTC
  workflow_dispatch:

permissions:
  contents: write

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7

      - uses: actions/setup-python@v7
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: pip install -r pipeline/requirements.txt

      - name: Configure git identity for the commit_and_push step
        run: |
          git config --global user.name "github-actions[bot]"
          git config --global user.email "41898282+github-actions[bot]@users.noreply.github.com"

      - name: Generate tuning stats
        run: python pipeline/generate_tuning_stats.py
```

- [ ] **Step 2: Commit, push, and verify one manual Actions run**

```bash
git add .github/workflows/generate-tuning-stats.yml
git commit -m "Add monthly generate-tuning-stats GitHub Actions workflow"
git push
gh workflow run generate-tuning-stats.yml
```

Then poll until it completes:

```bash
for i in 1 2 3 4 5 6; do
  status=$(gh run list --workflow=generate-tuning-stats.yml --limit 1 --json status,conclusion -q '.[0].status + " " + (.[0].conclusion // "pending")')
  echo "check $i: $status"
  if [[ "$status" != in_progress* && "$status" != queued* ]]; then break; fi
  sleep 15
done
gh run list --workflow=generate-tuning-stats.yml --limit 1
```

Expected: `completed success` (the git-identity step is included from the start here, unlike sub-project 4's first attempt, precisely because that gap was found and fixed then).

---

### Task 7: Create and verify the "Monthly tuning review" cloud routine

**Files:** none (a `RemoteTrigger` API call, not a repo file)

- [ ] **Step 1: Confirm local and remote are in sync, and the stats file is reachable**

```bash
cd "C:\Users\coope\Claude_Work\Projects\Options Trading"
git pull
git push
python -c "
import sys
sys.path.insert(0, 'pipeline')
import config
import requests
r = requests.get('https://raw.githubusercontent.com/coop1st/options-trading-pipeline/master/data/github_sync/options_ledger/tuning_stats_latest.json', timeout=30)
print(r.status_code, len(r.text), 'bytes')
"
```

Expected: `200`, a non-trivial byte count.

- [ ] **Step 2: Generate a fresh UUID for the routine's initial event**

```bash
python -c "import uuid; print(str(uuid.uuid4()))"
```

- [ ] **Step 3: Create the recurring routine**

Call `RemoteTrigger` with `action: "create"`, reusing the existing `environment_id` (`env_017ZfNsQhAPemSDvsptSbtZr`) already confirmed working for this repo:

```json
{
  "name": "Monthly tuning review",
  "cron_expression": "30 21 1 * *",
  "enabled": true,
  "job_config": {
    "ccr": {
      "environment_id": "env_017ZfNsQhAPemSDvsptSbtZr",
      "session_context": {
        "model": "claude-sonnet-5",
        "sources": [{"git_repository": {"url": "https://github.com/coop1st/options-trading-pipeline"}}],
        "allowed_tools": ["Bash", "Read", "Glob", "mcp__Gmail__create_draft"]
      },
      "events": [{"data": {
        "uuid": "<fresh UUID from Step 2>",
        "session_id": "",
        "type": "user",
        "parent_tool_use_id": null,
        "message": {"role": "user", "content": "<PROMPT -- see below>"}
      }}]
    }
  }
}
```

`cron_expression` explanation: `30 21 1 * *` fires the 1st of each month at 21:30 UTC, 30 minutes after `generate-tuning-stats.yml`'s 21:00 UTC run.

The prompt (fill in as the `message.content` string above):

```
You are running the monthly tuning review for the
coop1st/options-trading-pipeline repo, already cloned into your working
directory. A GitHub Actions job (generate_tuning_stats.py) runs on the
1st of each month and publishes
data/github_sync/options_ledger/tuning_stats_latest.json -- raw,
mechanical statistics only. Your job is to apply judgment to that data
and decide what, if anything, is well-supported enough to suggest as an
actual change. Hard safety requirements, in order of importance:

1. NEVER suggest changing a book-verbatim ("Tier 1") threshold. The only
   parameters ever eligible for a suggestion are: DIRECTIONAL_STOP_PCT,
   DIRECTIONAL_TARGET_PCT (in pipeline/config.py -- these control long
   call/put exit rules and have no book-given number), the composite
   score's per-criterion weights (currently equal, in pipeline/scoring.py),
   and selection_label filtering (e.g. excluding a specific label, or
   raising LABEL_THESIS_THRESHOLD). If you are ever unsure whether a
   parameter is Tier 1, do not suggest changing it -- say so and move on.
2. NEVER edit pipeline/config.py or pipeline/scoring.py yourself. Every
   suggestion is written to a new markdown file for a human (or a future
   Claude Code session, deliberately) to review and apply -- nothing here
   is automatic.
3. NEVER present a finding as a suggestion if its sample size is below
   min_trades_for_suggestion (a field in the stats JSON itself, currently
   10). Report the raw numbers if you like, but say explicitly that
   there isn't enough evidence yet for anything below that bar.

Steps:

1. Read data/github_sync/options_ledger/tuning_stats_latest.json.
   Fields: total_terminal_trades, min_trades_for_suggestion,
   criterion_correlations (per-criterion {n, correlation}, Spearman rank
   correlation between that criterion's score and realized P&L),
   weight_sensitivity (per-criterion {baseline_correlation,
   doubled_weight_correlation, halved_weight_correlation} -- does
   doubling or halving that one criterion's weight, holding others
   proportional, improve how well the composite score's rank predicts
   realized P&L?), label_performance (list of {selection_label,
   sample_size, win_rate, avg_realized_pct, note} -- performance by the
   book-grounded "why this trade was picked" tag), directional_exit_sweep
   (null if too few directional trades, else a dict of "stop_pct/target_pct"
   -> {n, win_rate, avg_realized_pct} showing how differently-thresholded
   long call/put exits would have performed against the SAME real,
   already-resolved price history).

2. If the file is missing entirely, draft a short alert email to
   kcoopercscs@gmail.com (subject "Monthly tuning review -- automation
   alert") stating the stats file wasn't found, and stop.

3. For each of the four analyses, identify any finding whose sample size
   meets min_trades_for_suggestion AND whose effect is clear enough to
   be worth a human's attention (a strong correlation, a sensitivity
   check that clearly favors reweighting, a label performing clearly
   worse than the rest, or a sweep grid point that clearly outperforms
   the current DIRECTIONAL_STOP_PCT/TARGET_PCT). Be conservative --
   this is real recommendation logic driving actual suggestions;
   marginal or noisy-looking findings should be reported as "not
   conclusive yet," not turned into a suggestion.

4. Create (do not just draft in memory) a new file at
   data/github_sync/options_ledger/tuning_suggestions_{YYYY-MM}.md
   (using this month's year-month, e.g. tuning_suggestions_2026-10.md)
   containing: a one-paragraph summary of overall data volume this
   month, then one section per analysis with either (a) a clearly-stated
   suggestion (the exact parameter, its current value, the suggested new
   value, and the evidence behind it) or (b) an explicit "not enough
   evidence yet" or "no clear signal" statement. Then commit and push it:
   git add, git commit -m "Monthly tuning review: {YYYY-MM}", git pull
   --rebase then git push (if the push is rejected as non-fast-forward,
   resolve it mechanically with git pull --rebase and push once more,
   rather than investigating further -- this matches how this repo's
   other automated commits already handle that situation).

5. Draft (do NOT send) a Gmail email to kcoopercscs@gmail.com, subject
   "Monthly tuning review -- {YYYY-MM}", summarizing the same content in
   plain language, and mention that the full file is committed to the
   repo at the path above. If literally nothing in the whole report
   clears the evidence bar (expected for a while after this pipeline
   first ships), say that plainly as the entire content of both the file
   and the email, rather than padding either out with inconclusive
   numbers presented as if they meant something.
```

- [ ] **Step 4: Relay the created routine's URL and confirmed run time**

The `RemoteTrigger create` response includes a summary line with the server-parsed schedule and the routine's `https://claude.ai/code/routines/{id}` URL — relay both.

- [ ] **Step 5: Manually trigger one verification run**

```
RemoteTrigger action=run trigger_id=<id from Step 3's response>
```

- [ ] **Step 6: Poll the run log until it completes**

```
RemoteTrigger action=list_runs trigger_id=<id>
RemoteTrigger action=get_run_log session_id=<id from list_runs>
```

(Repeat `get_run_log` every ~20-30 seconds until the log shows a `result:` line.)

Expected: `result: success`, no tool-permission errors. Check that:
- A new `data/github_sync/options_ledger/tuning_suggestions_{this-month}.md` file was actually committed and pushed to the repo (`git log --oneline -3` should show it).
- The file and the Gmail draft both correctly state there isn't enough data yet (0 terminal trades at this point in the project) rather than fabricating a conclusion.
- No suggestion references a Tier-1 constant.

---

## Not done here

- **Entry-side Tier-2 sweep** (`CONDOR_MIN_DTE`/`MAX_DTE`, `CALENDAR_MIN_FRONT_DAYS`,
  `VERTICAL_SPREAD_WIDTHS`, `VERTICAL_DELTA_BAND`) — explicitly deferred per the
  spec's Non-goals; would need a materially harder rebuild-from-historical-
  chain-data mechanism that doesn't exist.
- **Actually applying any suggestion** — deliberately manual, in a future
  session, by design.
- **Full candidate-pool counterfactual reranking** — the ledger only
  stores top-20 candidates/day; closing that gap is a separate future
  decision, not part of this plan.

## Self-Review Notes

- **Spec coverage**: the required `track_outcomes.py` refactor (Task 1),
  per-criterion correlation (Task 2), weight sensitivity (Task 3), the
  Tier-2 exit-side sweep (Task 4), orchestration/publishing (Task 5), the
  monthly GH Actions job (Task 6), and the judgment-layer routine with
  its explicit Tier-1 safety instructions (Task 7) each have a task. The
  evidence bar (`MIN_TRADES_FOR_TUNING_SUGGESTION`) is enforced in both
  the mechanical script (skips the sweep entirely below it) and the
  routine's own explicit instructions (a second, independent check).
- **Placeholder scan**: no TBD/TODO; every step has real, runnable code.
  The exact sweep grid values and monthly schedule time are the spec's
  own flagged open questions, carried into `config.py`/the workflow as
  concrete defaults here rather than left unresolved.
- **Type/interface consistency checked**: `evaluate_trade`'s new
  `evaluator_overrides` parameter (Task 1) is used identically in Task 4's
  `sweep_directional_thresholds`; `compare_strategies.CRITERIA`/
  `_load_terminal_trades`/`by_label` (all pre-existing, sub-project 4)
  are imported and reused verbatim in `generate_tuning_stats.py`, never
  redefined or duplicated; `track_outcomes.SCOREABLE_STATUSES`/
  `_entry_info_for_trade`/`_load_all_signals` are likewise imported, not
  copied.
