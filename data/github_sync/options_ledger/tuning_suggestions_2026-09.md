# Monthly Tuning Review -- 2026-09

**Source:** `tuning_stats_latest.json`, generated 2026-09-05.

## Summary

This month's stats file reports **0 terminal trades** (`total_terminal_trades: 0`). Every downstream field is consequently empty or null: all seven `criterion_correlations` entries have `n: 0` / `correlation: null`, `weight_sensitivity` is all-null, `label_performance` is an empty list, and `directional_exit_sweep` is `null` (too few directional trades to build the grid). The minimum sample size for any suggestion, per this run's own `min_trades_for_suggestion`, is 10.

There is nothing to suggest this month. No criterion correlation, weight-sensitivity check, label-performance comparison, or directional exit-threshold sweep has any data behind it at all, let alone the 10-trade minimum -- so none of the four analyses clears the evidence bar, and none is close enough to call "not conclusive yet" as opposed to simply absent. This is expected shortly after the pipeline first started publishing these stats; no parameters (`DIRECTIONAL_STOP_PCT`, `DIRECTIONAL_TARGET_PCT`, the composite score weights, or `selection_label` filtering) are being suggested for change.

Nothing further to report until enough terminal trades accumulate.
