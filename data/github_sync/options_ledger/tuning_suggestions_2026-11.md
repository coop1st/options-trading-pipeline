# Monthly Tuning Review -- 2026-11

**Source:** `tuning_stats_latest.json`, `generated_date: 2026-10-02`.

## Summary

This month's stats file reports **7 terminal trades** (`total_terminal_trades: 7`) -- up from 0 in last month's file, so the pipeline is starting to accumulate real outcomes, but `min_trades_for_suggestion` is 10 and nothing in this file reaches that bar yet. All seven `criterion_correlations` entries sit at `n: 7`; `weight_sensitivity` is derived from that same 7-trade sample; `label_performance` lists two labels with sample sizes of 2 and 5; `directional_exit_sweep` is `null` (too few terminal directional trades to build the grid). No suggestions below.

## Per-analysis detail

### 1. Criterion correlations (score vs. realized P&L)
`n: 7` for every criterion (`iv_richness` 0.0598, `skew_quality` -0.8018, `risk_reward` 0.691, `pop_proxy` 0.8018, `term_structure` 0.982, `liquidity` null, `directional_alignment` null). Some of these look large in magnitude, but with only 7 trades a handful of outcomes can swing a rank correlation this far either way -- **not enough evidence yet**.

### 2. Weight sensitivity (doubling/halving each criterion's weight)
Built on the same 7-trade sample as above. `risk_reward` and `term_structure` show the composite's correlation with realized P&L improving when their weight is doubled (0.691 -> 0.8729 and 0.691 -> 0.982, respectively), which is directionally consistent with their individual correlations above. Still **not enough evidence yet** -- this is the same underlying n=7 sample reflected through a different lens, not independent confirmation.

### 3. Label performance (`selection_label` win rate / avg realized %)
Two labels on record: `term_structure_edge+directional_confirmation` (n=2, 100% win rate, avg +0.65%) and `directional_confirmation` (n=5, 40% win rate, avg -3.72%). Both are well below the n=10 floor -- **not enough evidence yet**, even though the `directional_confirmation` numbers are worth watching next month.

### 4. Directional exit threshold sweep (`DIRECTIONAL_STOP_PCT` / `DIRECTIONAL_TARGET_PCT`)
`directional_exit_sweep` is `null` -- too few terminal long call/put trades to build the grid. **Not enough evidence yet.**

## Conclusion

No parameters (`DIRECTIONAL_STOP_PCT` = 0.50, `DIRECTIONAL_TARGET_PCT` = 2.00, the composite score's equal criterion weights, or `selection_label` / `LABEL_THESIS_THRESHOLD` = 65.0 filtering) are being suggested for change this month. Terminal trade count is growing (0 -> 7) but still sits below the 10-trade floor this report itself requires before treating any of the above as a real signal. Revisit next month once more trades resolve.
