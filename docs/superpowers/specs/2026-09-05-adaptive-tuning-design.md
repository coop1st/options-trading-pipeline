# Adaptive Tuning Suggestions — Design

## Context

This is the fifth sub-project of the Options Trading project (see
`2026-08-26-options-playbook-design.md`, `2026-08-26-data-and-scoring-pipeline-design.md`,
`2026-09-05-strategy-engine-design.md`, and `2026-09-05-strategy-comparison-design.md`
for the prior four, all complete and live). The user asked for a monthly
"advanced learning feedback" system that goes beyond sub-project 4's
weekly reporting to generate concrete change suggestions based on
accumulated performance data — analogous to the Stocks project's
existing weekly "Pick Tuning Review" routine (which proposes, but never
auto-applies, changes to its own live parameters).

**Two prerequisites for this spec were built immediately, before writing
it, rather than deferred into its implementation plan** (matching the
"the sooner this ships, the less history is lost" principle sub-project
4 already established for score-breakdown persistence):

1. **A real bug fix.** `build_iron_condors`, `build_calendars`, and
   `build_double_diagonals` hardcoded `"tilt": None` and never received
   the real bias signal, making `scoring.py`'s `directional_alignment`
   criterion a constant `100.0` for these three families regardless of
   whether a real market tilt existed — contradicting sub-project 3's
   own approved spec. Fixed by threading `bias` through to all three
   builders. Verified synthetically and against real data.
2. **`selection_label`**, a new ledger column assigned at recommendation
   time: which of the 4 "thesis" criteria (`iv_richness`, `skew_quality`,
   `term_structure`, `directional_alignment` — the criteria that
   describe *why* a trade was picked, not how good it is) scored
   meaningfully above the neutral baseline for that candidate, joined
   into a label like `"rich_iv+rich_skew"` — directly matching
   `greeks-and-volatility.md` §4.3's "richest setups combine high skew
   and high ATM IV" rather than an invented taxonomy. `compare_strategies.py`
   (sub-project 4) now also reports win rate/avg realized P&L **by
   label**, alongside its existing by-family and by-criterion views.

This spec's job is to turn that data — now flowing correctly — into
monthly, evidence-gated, human-reviewed suggestions.

## The core design constraint: a three-tier boundary

This project's entire identity is being book-grounded, not a black-box
backtested optimizer. A learning-feedback system that starts suggesting
changes to the books' own numbers would quietly turn it into something
else. Every parameter this pipeline uses is classified into exactly one
tier, and **this classification is a hard boundary the implementation
must enforce in code, not just describe in prose**:

| Tier | Definition | Examples | Eligible for suggestions? |
|---|---|---|---|
| **1 — Book-verbatim** | A specific number the books themselves state | Condor's 55% target / 30-DTE exit / 10-15Δ, vertical's 10% target, calendar's 5%/10%, the 2% position-sizing rule | **Never** |
| **2 — This project's own flagged guesses** | Explicitly documented in prior specs as "this spec's own choice, not a book number" | `DIRECTIONAL_STOP_PCT`/`DIRECTIONAL_TARGET_PCT` (exit-side); `CONDOR_MIN_DTE`/`MAX_DTE`, `CALENDAR_MIN_FRONT_DAYS`, `VERTICAL_SPREAD_WIDTHS`, `VERTICAL_DELTA_BAND` (entry-side) | Yes, but see the entry/exit-side split below |
| **3 — Composite score weighting** | The 7 criteria's currently-equal weights in `scoring.py` | — | Yes |

## Goals

- Monthly, deeper analysis than sub-project 4's weekly median-split:
  rank-correlation strength per criterion (not just above/below-median),
  a genuine counterfactual parameter sweep for Tier 2's *exit-side*
  constants, and a label-driven filtering suggestion mechanism.
- Every suggestion is evidence-gated (a stricter sample-size bar than
  the weekly report) and **never auto-applied** — written to a tracked,
  committed monthly file plus a digest email, for manual review and
  application in a future session.
- Reuse `track_outcomes.py`'s existing evaluator functions for the
  parameter sweep rather than duplicating simulation logic — this needs
  one small, safe, backward-compatible refactor (default-valued optional
  parameters, described below).

## Non-goals

- **Auto-applying any suggested change** to `config.py` or `scoring.py`.
- **Suggesting changes to Tier 1** constants, ever, under any evidence.
- **Sweeping Tier 2's *entry-side* constants** (`CONDOR_MIN_DTE`/`MAX_DTE`,
  `CALENDAR_MIN_FRONT_DAYS`, `VERTICAL_SPREAD_WIDTHS`, `VERTICAL_DELTA_BAND`)
  in this version. These live in `strategy_rules.py`'s *builders* — they
  control which candidates get built at all, not how an already-built
  trade exits. Sweeping them honestly would mean reconstructing a
  hypothetical candidate from a historical date's full (unfiltered)
  signals.csv using an alternate DTE window or delta band, then
  replaying it forward exactly like a real trade — a materially harder
  mechanism than reusing an existing evaluator, since no such
  "rebuild-from-history" capability exists yet for the builders. Flagged
  explicitly as a future extension, not built here, rather than faked
  with a lower-fidelity approximation.
- **Full candidate-pool counterfactual reranking** (already flagged as a
  limitation in the earlier design discussion): the ledger only ever
  stores the top-20 candidates that were actually recommended, so
  Tier 3's analysis can only ask "would reweighting have ranked our
  actual winners higher among what we already recommended," never
  "would a different weighting have surfaced better candidates we never
  considered." Closing that gap would mean persisting substantially more
  data than today and is a separate decision, not part of this spec.
- **Fitting an actual regression/optimization model.** Given the trade
  volumes this pipeline will realistically produce for a long while,
  fitting a multi-parameter model would be overfitting dressed up as
  rigor. This system uses transparent, explainable statistics (rank
  correlation, a small discrete sweep grid, single-criterion sensitivity
  nudges) that a human can sanity-check against the books' own theory.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│ Inputs (already published, read fresh each run)                      │
│  • options_recommendation_ledger.csv (composite_score, 7 criteria,   │
│    selection_label, outcome_status/date/realized_pct -- all live)    │
│  • data/github_sync/signals/*.csv (full history, for the Tier-2      │
│    exit-side sweep, replaying already-terminal trades only)          │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ pipeline/generate_tuning_stats.py (new, monthly GitHub Actions,       │
│ mechanical -- no external fetch, matching track_outcomes.py's split) │
│  1. Rank-correlation (Spearman) per criterion vs. realized_pct, on    │
│     scoreable terminal trades only.                                  │
│  2. Label performance (reuses compare_strategies.by_label; a stricter │
│     evidence bar than the weekly report).                            │
│  3. Tier-2 exit-side sweep: for DIRECTIONAL_STOP_PCT/TARGET_PCT, re-  │
│     evaluate every terminal long-call/put trade against a small grid  │
│     of alternate values using track_outcomes.py's own (now           │
│     parameterized) evaluator, against the SAME historical price path. │
│  4. Tier-3 sensitivity: for each criterion, recompute composite_score │
│     with that criterion's weight doubled (others reduced proportion-  │
│     ally) and halved; compare rank-correlation with realized_pct      │
│     against the current equal-weight baseline.                       │
│  Publishes raw stats to a JSON file -- no suggestions authored yet,   │
│  purely mechanical numbers.                                           │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ New monthly Claude Code cloud routine ("Monthly tuning review")       │
│  Reads the raw stats, applies judgment: is each finding well-         │
│  supported (sample size, robustness, book-theory consistency)? Drafts │
│  an email AND commits tuning_suggestions_{YYYY-MM}.md documenting any │
│  well-supported suggestions with rationale and the exact tier-2/      │
│  tier-3 change proposed. Never edits config.py/scoring.py itself.     │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Detail: Required `track_outcomes.py` Refactor

`_evaluate_directional_long()` currently reads `DIRECTIONAL_STOP_PCT`/
`DIRECTIONAL_TARGET_PCT` as fixed module-level imports. To sweep
alternate values without duplicating the evaluator's logic, it needs
optional parameters defaulting to the current config values:

```python
def _evaluate_directional_long(legs, price_lookup, dte, width,
                                stop_pct=DIRECTIONAL_STOP_PCT,
                                target_pct=DIRECTIONAL_TARGET_PCT):
    ...
    if ratio <= stop_pct:
        return "HIT_MAX_LOSS", (value - debit) / debit
    if ratio >= target_pct:
        return "HIT_TARGET", (value - debit) / debit
    return None
```

This is the *only* evaluator that needs this treatment — every other
family's exit-rule thresholds (condor's 55%/30-DTE, vertical's 10%,
calendar's 5%/10%) are Tier 1, never swept, so they stay exactly as
they are. Backward-compatible by construction (default values match
current behavior exactly); `verify_track_outcomes.py`'s existing checks
must still pass unchanged after this refactor.

## Component Detail: Tier-2 Exit-Side Sweep

For every terminal (`SCOREABLE_STATUSES`) long call/put trade, re-run
`_evaluate_directional_long` chronologically against the *same* signals
history that trade already has, substituting a small grid of alternate
`stop_pct`/`target_pct` values (e.g. `{0.40, 0.50, 0.60}` ×
`{1.5, 1.75, 2.0, 2.25}` — implementation-time detail, not fixed here)
in place of the real thresholds used at the time. This is a genuine
counterfactual: the price path is real and already fully known (the
trade already terminaled), only the exit rule applied to it changes.
Aggregate, per grid point, the resulting win rate and average
`realized_pct` across all swept trades — the grid point that would have
performed best, if it clears the evidence bar below, becomes a candidate
suggestion.

## Component Detail: Tier-3 Sensitivity and Label Filtering

- **Per-criterion rank correlation**: Spearman correlation between each
  of the 7 criteria's stored score and `realized_pct`, across scoreable
  terminal trades — more informative than the weekly report's binary
  median split, and more robust than Pearson correlation given
  `realized_pct`'s likely non-normal, outcome-driven distribution.
- **Weight-sensitivity check**: for each criterion, recompute what
  `composite_score` would have been with that criterion's weight doubled
  (others reduced proportionally to keep weights summing to 1) and
  halved, and compare the resulting rank-correlation with `realized_pct`
  against the current equal-weight baseline. A criterion whose doubled
  weight clearly improves correlation is a reweighting candidate; one
  whose halved weight improves it is a down-weighting candidate.
- **Label filtering**: reuses `compare_strategies.by_label()` directly.
  A label with enough terminal trades (see evidence bar below) and a
  win rate/avg realized P&L clearly worse than the overall average
  becomes a candidate for a suggested filter (e.g., "require at least
  one thesis criterion above threshold before recommending" — i.e.,
  exclude `no_dominant_thesis`) or a suggested threshold change (e.g.,
  raising `LABEL_THESIS_THRESHOLD` if borderline-thesis trades are
  underperforming clear-thesis ones).

## Evidence Bar

A stricter bar than the weekly report's `MIN_TERMINAL_TRADES_FOR_STATS`
(5) applies before this system generates *any* suggestion — proposing an
actual parameter or filter change deserves more evidence than reporting
a raw statistic. New constant: `MIN_TRADES_FOR_TUNING_SUGGESTION = 10`.
Below this bar for a given family/label/grid-point, `generate_tuning_stats.py`
still computes and publishes the raw numbers (transparency), but the
routine's judgment step must not turn them into a suggestion, and must
say so explicitly if asked.

## Error Handling

- Per-trade/per-grid-point try/except-and-continue, matching every
  prior script's convention.
- Zero terminal trades, or zero trades clearing the evidence bar for
  every analysis → the routine drafts an email saying so explicitly
  (matching sub-project 4's own zero-data digest, already verified live)
  rather than fabricating a suggestion from insufficient evidence.
- If `tuning_suggestions_{YYYY-MM}.md` already exists for the current
  month (e.g. a re-run), it's overwritten, not appended — one file per
  month is the unit of record, not a growing log within a month.

## Testing

No pytest, matching this project's convention.
`pipeline/verify_generate_tuning_stats.py`: synthetic ledger fixtures
confirming (a) the Spearman correlation calculation against a known
monotonic and a known random relationship, (b) the weight-sensitivity
check moves in the expected direction for a criterion with strong vs.
weak correlation, (c) the exit-side sweep grid correctly re-evaluates a
synthetic trade's known price path under alternate thresholds and picks
the best-performing grid point, and (d) nothing below
`MIN_TRADES_FOR_TUNING_SUGGESTION` produces a suggestion.

## File Breakdown

None created yet — this remains design until reviewed (the two
prerequisites above are already shipped, separately from this plan):

- `pipeline/track_outcomes.py` *(modify)* — parameterize
  `_evaluate_directional_long`'s thresholds (backward-compatible).
- `pipeline/generate_tuning_stats.py` *(new)* — correlation, sweep,
  sensitivity, and label-filtering raw-stats computation.
- `pipeline/verify_generate_tuning_stats.py` *(new)*.
- `.github/workflows/generate-tuning-stats.yml` *(new)* — monthly,
  mechanical (1st of each month, after that week's `compare-strategies.yml`
  run has published fresh data).
- New `RemoteTrigger` routine, "Monthly tuning review" — monthly,
  judgment-only (interprets the raw stats, drafts the email, commits
  `tuning_suggestions_{YYYY-MM}.md` — never edits `config.py`/`scoring.py`).

## Open Questions

- **Exact sweep grid values** for `DIRECTIONAL_STOP_PCT`/`TARGET_PCT` —
  implementation-time detail once real terminal directional trades exist
  to sweep against (there are currently zero).
- **Monthly schedule's exact day/time** — leaning 1st of the month,
  21:00 UTC for the GitHub Actions job and ~21:30 UTC for the routine,
  mirroring the weekly job's own same-day-offset pattern; open to
  adjustment.
- **When (if ever) to build the entry-side Tier-2 sweep** (the
  rebuild-from-historical-chain-data capability flagged as a Non-goal) —
  deferred until there's a concrete reason to believe the current
  entry-side windows are miscalibrated, rather than built speculatively.
