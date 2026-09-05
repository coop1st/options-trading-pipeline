# Handover — pick this up from here

Last updated 2026-09-05 (evening) to hand this project off between
Claude Code sessions. Everything referenced here is committed and pushed
to `master` at https://github.com/coop1st/options-trading-pipeline
(public repo). Read this file first, then the specs/plans it points to.

**All four originally-planned sub-projects are now built and live.** A
possible sub-project 5 (monthly adaptive-learning tuning suggestions,
building on sub-project 4's outcome data) has been discussed but not yet
designed — see "What's next" below.

## Where things stand

**Sub-project 1 (Options Playbook skill) — complete.** A Claude Code skill
at `.claude/skills/options-playbook/` distilling both source books
(Bittman's *Trading Options as a Professional*, Chen/Sebastian's *The
Option Trader's Hedge Fund*) into 8 reference docs + `SKILL.md`. Built via
36-task plan in `docs/superpowers/plans/2026-08-26-options-playbook.md`
(all tasks done, plan fully executed). Source PDFs live in `Material/`
(git-ignored — copyrighted, never commit them) with per-chapter extraction
notes in `docs/extraction-notes/` for traceability.

**Sub-project 2 (Data & Scoring Pipeline) — built and live.** Spec at
`docs/superpowers/specs/2026-08-26-data-and-scoring-pipeline-design.md`,
implementation plan at
`docs/superpowers/plans/2026-08-28-data-and-scoring-pipeline.md` (8 tasks,
all complete). Components:

- **A (watchlist)** — read live from the Stocks project's public
  `stock_price_ledger.csv`.
- **B (cloud fetch)** — `.github/workflows/options-snapshot-fetch.yml`
  runs `cloud/fetch_options_snapshot.py` 3x/trading day on GitHub Actions,
  fetches options chains via yfinance (now also including 5 tail-hedge
  instruments, `^SPX`/`SPY`/`^VIX`/`VXX`/`UVXY` — added in sub-project 3),
  commits dated CSVs to `data/github_sync/options_snapshots/`.
- **C (local merge + score)** — `pipeline/merge_and_score.py` (run
  manually, whenever this PC is next on): pulls new snapshots, upserts
  into gitignored `data/db/options.db`, computes Black-Scholes Greeks,
  liquidity/bid-ask flags, ATM IV/skew reads (now also persisting skew
  history — sub-project 3 addition), publishes
  `data/github_sync/signals/{date}.csv`, commits + pushes.
- **D (nightly cloud routine)** — `RemoteTrigger` id
  `trig_019GMK964MKrAunz5KZiZv8x`, cron `30 1 * * 2-6` (~2:30am Irish
  time), https://claude.ai/code/routines/trig_019GMK964MKrAunz5KZiZv8x.
  Drafts real trade recommendations from the options recommendation
  ledger every night (updated in sub-project 3).

**Sub-project 3 (Strategy/Screening Engine) — complete, verified live.**
Spec at `docs/superpowers/specs/2026-09-05-strategy-engine-design.md`,
implementation plan at `docs/superpowers/plans/2026-09-05-strategy-engine.md`
(16 tasks, all complete). What's live:

- **Four data prerequisites**: ATR (daily cloud fetch +
  `pipeline/atr.py`'s weekly local refresh), skew history (persisted
  alongside `atm_iv_history`), term-structure history (derived query, no
  new table — still accumulating, needs 5+ trading days per expiration
  pair before calendar/diagonal candidates can build), and tail-hedge
  instruments (`^SPX`/`SPY`/`^VIX`/`VXX`/`UVXY`, with `^VIX` explicitly
  excluded from strategy screening since its options price off futures,
  not spot, which this pipeline's Black-Scholes Greeks can't model).
- **Five strategy-family candidate builders** in `pipeline/strategy_rules.py`
  (vertical credit spreads, iron condors, directional longs, calendars,
  double diagonals), each hard-gated per book-cited thresholds.
- **7-criteria composite scorer** in `pipeline/scoring.py`.
- **Orchestrator** `pipeline/screen_trades.py`: builds, scores, ranks,
  sizes (2% of `ACCOUNT_EQUITY`, currently a `100000` placeholder — edit
  to real trading capital), writes the recommendation ledger, and builds
  the portfolio-insurance ("units") reminder.

**Sub-project 4 (Strategy Comparison & Simulated Outcome Tracking) —
complete, verified live.** Spec at
`docs/superpowers/specs/2026-09-05-strategy-comparison-design.md`,
implementation plan at
`docs/superpowers/plans/2026-09-05-strategy-comparison.md` (9 tasks, all
complete, executed inline with real-data/live-cloud verification after
every task). What's live:

- **Score-breakdown persistence**: `screen_trades.py` now writes 8 new
  ledger columns (`composite_score` + the 7 criteria) instead of
  discarding them after ranking — needed so outcomes can eventually be
  correlated against what predicted them.
- **`pipeline/track_outcomes.py`** (daily, `.github/workflows/track-outcomes.yml`,
  fully cloud-side — no external fetch, no local-machine dependency at
  all): simulates each recommendation's outcome by replaying its
  strategy family's book-cited exit rule (target %, stop %, and for iron
  condors a 30-DTE time exit) against every `signals.csv` snapshot since
  entry. **Re-scans full history on every run** rather than resuming from
  a checkpoint, so a contract's temporary absence from one day's data is
  just skipped, never treated as a permanent loss — only marked
  `UNRESOLVED_AT_EXPIRATION` if a position's expiration passes with zero
  pricing data ever found across its whole life.
- **`pipeline/compare_strategies.py`** (weekly,
  `.github/workflows/compare-strategies.yml`): aggregates scoreable
  terminal trades by strategy family (win rate, avg realized P&L) and by
  each of the 7 scoring criteria (above/below-median win-rate split),
  publishing `data/github_sync/options_ledger/strategy_performance_report.csv`.
  Small-sample results (fewer than 5 terminal trades) are explicitly
  flagged "too few trades to be meaningful yet" rather than presented as
  reliable.
- **New weekly cloud routine**, "Strategy performance digest",
  `RemoteTrigger` id `trig_01CUvKC5TLDezGhgVUgisVzq`, cron `30 20 * * 0`
  (Sunday 20:30 UTC, after `compare-strategies.yml`'s 20:00 UTC run),
  https://claude.ai/code/routines/trig_01CUvKC5TLDezGhgVUgisVzq. Drafts
  the digest email from the published report — verified live, correctly
  reporting "not enough data yet" rather than fabricating conclusions
  from zero-sample rows.

**Two real bugs found and fixed during sub-project 4's verification, both
worth knowing about**:
1. **A pre-existing sub-project 3 bug**: `scoring.py`'s `_iv_richness`/
   `_skew_quality` checked `is not None`, which doesn't filter out `NaN`
   — and a blank `signals.csv` cell (like `atm_iv_90d_percentile` before
   5 days of history accumulate) round-trips through pandas as `NaN`, not
   `None`. This let `NaN` poison `composite_score`'s average, silently
   corrupting candidate ranking since sub-project 3 shipped; it only
   became visible once `composite_score` started being persisted. Fixed
   with a NaN-aware `_valid()` helper, with a permanent regression test
   in `verify_scoring.py`.
2. **Missing git identity in the two new GitHub Actions workflows**:
   `track-outcomes.yml`/`compare-strategies.yml` call `commit_and_push()`
   from Python (matching `merge_and_score.py`/`screen_trades.py`'s
   architecture) but nothing configured a git identity for the runner
   first — didn't surface in `track-outcomes.yml`'s own first run since
   that run had nothing to commit. Fixed with the same
   `github-actions[bot]` identity the project's other cloud workflows
   already use.

## What's next

- **Sub-project 5 (proposed, not yet designed)**: the user asked for a
  monthly "advanced learning feedback" system that goes beyond
  sub-project 4's reporting to generate concrete change suggestions
  (e.g., re-weighting `scoring.py`'s criteria, retuning exit-rule
  percentages) based on accumulated performance data — analogous to the
  Stocks project's existing weekly "Pick Tuning Review" routine. Needs
  its own brainstorming → spec → plan cycle, and depends on sub-project
  4's outcome-tracking data actually accumulating first (there's nothing
  to learn from yet — every terminal-trade count is currently 0).
- **Let terminal trades start accumulating** — no action needed, just
  time: the SPY iron condor recommended 2026-09-05 needs to hit its 55%
  target, its max-loss ceiling, or 30 DTE before `track_outcomes.py` has
  anything to report on.
- **Let calendar/diagonal candidates start appearing** — same as
  sub-project 3's handover note: needs 5+ trading days of accumulated
  `atm_iv_history` per expiration pair.
- **`ACCOUNT_EQUITY` in `pipeline/config.py`** is a placeholder
  (`100000`) — edit it to the user's real trading capital before relying
  on `suggested_contracts` for real position sizing.
- Post-entry position **management** (as opposed to the entry
  recommendation and simulated exit tracking now built) — actively
  monitoring and alerting on genuinely open positions in real time —
  remains out of scope; sub-project 4's simulation is retrospective
  (checked daily against published snapshots), not a live position
  monitor.

## Environment gotcha (local machine only)

Norton antivirus on this machine does TLS inspection that breaks strict
OpenSSL certificate validation for Python HTTPS calls. Already solved in
`pipeline/config.py` (`truststore` for stdlib SSL, plus exporting
Windows' trusted root store to a PEM file and setting `CURL_CA_BUNDLE` for
`curl_cffi`-based libraries like yfinance's crumb auth). **This fix is
only needed locally** — GitHub Actions runners and Claude Code cloud
routines don't have this problem. When testing a `cloud/*.py` script
locally (they're deliberately self-contained, so they don't import
`pipeline/config.py`'s fix automatically), prefix the run with
`python -c "import sys; sys.path.insert(0,'pipeline'); import config; import runpy; runpy.run_path('cloud/script.py', run_name='__main__')"`
or similar to get the fix without modifying the cloud script itself.

## Repo / directory pointers

- Local: `C:\Users\coope\Claude_Work\Projects\Options Trading`
- Remote: `coop1st/options-trading-pipeline` (public, pushed and up to date)
- `Material/` — source book PDFs, git-ignored, never commit
- `.claude/skills/options-playbook/` — the finished skill (SKILL.md +
  8 reference docs)
- `docs/extraction-notes/` — per-chapter extraction notes (26 files, both
  books), traceability layer behind the skill
- `docs/superpowers/specs/` — 4 design specs (playbook, pipeline,
  strategy engine, strategy comparison)
- `docs/superpowers/plans/` — 4 implementation plans, all fully executed
- `pipeline/` — local/cloud-shared pipeline code: `config.py`, `db.py`,
  `greeks.py`, `merge_and_score.py`, `atr.py`, `directional_bias.py`,
  `strategy_rules.py`, `scoring.py`, `screen_trades.py`,
  `track_outcomes.py`, `compare_strategies.py`, plus `verify_greeks.py`/
  `verify_scoring.py`/`verify_track_outcomes.py`/`verify_compare_strategies.py`
- `cloud/` — GitHub-Actions-runnable scripts: `fetch_options_snapshot.py`,
  `fetch_daily_true_range.py`
- `data/db/options.db` — gitignored SQLite DB, regenerable from published
  snapshots
- `data/github_sync/` — published pipeline data: `options_snapshots/`,
  `signals/`, `daily_true_range/`, `options_ledger/` (recommendation
  ledger + `strategy_performance_report.csv`)
