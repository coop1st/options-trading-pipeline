# Monthly Tuning Review -- 2026-10

**Source:** `tuning_stats_latest.json`, `generated_date: 2026-09-05`.

## Summary

This month's stats file reports **0 terminal trades** (`total_terminal_trades: 0`), and is, byte-for-byte, the same file last month's review (`tuning_suggestions_2026-09.md`) already analyzed. All seven `criterion_correlations` entries have `n: 0` / `correlation: null`, `weight_sensitivity` is all-null, `label_performance` is an empty list, and `directional_exit_sweep` is `null`. The minimum sample size for any suggestion, per this run's own `min_trades_for_suggestion`, is 10. None of the four analyses clears that bar, or any bar -- there is no data behind any of them.

No parameters (`DIRECTIONAL_STOP_PCT` = 0.50, `DIRECTIONAL_TARGET_PCT` = 2.00, the composite score's equal criterion weights, or `selection_label` / `LABEL_THESIS_THRESHOLD` = 65.0 filtering) are being suggested for change this month.

## Operational note (not a tuning finding)

`generate-tuning-stats.yml` is scheduled for `0 21 1 * *` (1st of each month, 21:00 UTC) and this review ran after that time today. Checking the Actions history, the workflow has **only ever run once** -- a manual `workflow_dispatch` on 2026-09-05, the day it was added -- and its monthly cron trigger does not appear to have fired today. By contrast, the pipeline's other scheduled jobs (`options-snapshot-fetch.yml`, `daily-true-range-fetch.yml`, `track-outcomes.yml`) all ran on schedule earlier today without issue, and the workflow itself shows `state: active` with no apparent configuration problem. This is worth a human checking (and manually dispatching the workflow if it still hasn't fired by tomorrow) -- not because any tuning parameter is affected, but because next month's review will have the same empty, stale input if the schedule continues not to fire. Separately, even once it does run, the input ledger still shows 0 terminal trades, so no real tuning signal exists yet regardless.

## Per-analysis detail

### 1. Criterion correlations (score vs. realized P&L)
No data (`n: 0` for all 7 criteria: `iv_richness`, `skew_quality`, `risk_reward`, `pop_proxy`, `term_structure`, `liquidity`, `directional_alignment`). Not enough evidence yet.

### 2. Weight sensitivity (doubling/halving each criterion's weight)
No data (`baseline_correlation`, `doubled_weight_correlation`, `halved_weight_correlation` all null for every criterion). Not enough evidence yet.

### 3. Label performance (`selection_label` win rate / avg realized %)
`label_performance` is an empty list -- no labels have any terminal trades yet. Not enough evidence yet.

### 4. Directional exit threshold sweep (`DIRECTIONAL_STOP_PCT` / `DIRECTIONAL_TARGET_PCT`)
`directional_exit_sweep` is `null` -- too few terminal long call/put trades to build the grid. Not enough evidence yet.

## Conclusion

Nothing to suggest this month. Nothing further to report on tuning until enough terminal trades accumulate; separately, the stats-generation schedule is worth a human's attention since it does not appear to have produced new data in the month since it was set up.
