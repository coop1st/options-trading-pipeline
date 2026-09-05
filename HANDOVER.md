# Handover — pick this up from here

Last updated 2026-09-05 (afternoon) to hand this project off between
Claude Code sessions. Everything referenced here is committed and pushed
to `master` at https://github.com/coop1st/options-trading-pipeline
(public repo). Read this file first, then the specs/plans it points to.

**All three planned sub-projects are now built and live.** Sub-project 4
(strategy comparison/backtesting) is the only remaining piece, and it's
explicitly deferred until the recommendation ledger has real tracked
outcome history — see "What's next" below.

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
  **Updated in sub-project 3** to draft real trade recommendations from
  the options recommendation ledger (component E, now built) instead of
  the old diagnostic placeholder — see below.

**Sub-project 3 (Strategy/Screening Engine) — complete, verified live.**
Spec at `docs/superpowers/specs/2026-09-05-strategy-engine-design.md`,
implementation plan at
`docs/superpowers/plans/2026-09-05-strategy-engine.md` (16 tasks, all
complete, executed inline task-by-task with real-data verification after
every task). What's live:

- **Four data prerequisites** the spec identified as missing, all built:
  - **ATR**: `.github/workflows/daily-true-range-fetch.yml` runs
    `cloud/fetch_daily_true_range.py` once/trading day, publishing
    `data/github_sync/daily_true_range/true_range_ledger.csv` (wide
    format, same convention as the other ledgers). `pipeline/atr.py`'s
    `refresh_atr_if_stale()` recomputes each symbol's 14-day ATR weekly
    from that ledger, cached in a new `atr_by_symbol` table in
    `options.db`. Feeds the iron condor's IV-vs-ATR gate.
  - **Skew history**: `merge_and_score.py` now persists
    `skew_put_pct_of_atm`/`skew_call_pct_of_atm` over time into a new
    `skew_history` table, alongside the existing `atm_iv_history`.
  - **Term-structure history**: no new table needed — a new
    `db.get_term_structure_spread_history()` derives the front-minus-back
    IV spread's history by joining `atm_iv_history` against itself.
    Feeds the calendar/diagonal builders' "normal relationship" gate.
    **Still accumulating** — needs 5+ trading days of history per
    expiration pair before calendar/diagonal candidates can be built;
    correctly reports "not enough history yet" and skips rather than
    guessing, in the meantime (same pattern as
    `atm_iv_90d_percentile`'s own early-history behavior).
  - **Tail-hedge instruments**: `^SPX`/`SPY`/`^VIX`/`VXX`/`UVXY` added to
    component B's fetch list, feeding the units reminder (below). `^VIX`
    is explicitly **excluded from strategy-family screening** (but not
    from the units reminder) — VIX options price off VIX futures, not
    spot VIX, so this pipeline's spot-priced Black-Scholes Greeks are
    unreliable for it; discovered and fixed during Task 14's real-data
    verification.
- **Five strategy-family candidate builders** in
  `pipeline/strategy_rules.py`, each hard-gated per book-cited thresholds
  (see the spec for exact citations): vertical credit spreads, iron
  condors, directional long calls/puts, calendar spreads (long/short),
  double diagonals.
- **7-criteria composite scorer** in `pipeline/scoring.py`
  (`pipeline/verify_scoring.py` checks each criterion moves in the
  book-cited direction — all passing).
- **Orchestrator** `pipeline/screen_trades.py`: refreshes ATR, builds
  every family's candidates, scores and ranks, attaches a **2%-of-capital
  position-sizing suggestion** (`ACCOUNT_EQUITY = 100000` in
  `config.py` — a placeholder the user should edit to their real trading
  capital), writes the top 20 to
  `data/github_sync/options_ledger/options_recommendation_ledger.csv`
  (component E, extended with a `suggested_contracts` column), and builds
  a **portfolio-insurance ("units") reminder** citing a real qualifying
  deep-OTM SPX/VIX put from that day's data when one exists.
- **Verified live end-to-end** 2026-09-05: real signals data produced one
  real candidate (a SPY iron condor), the ledger published correctly, and
  the updated nightly routine — manually triggered twice — correctly read
  it and drafted a real (not diagnostic) recommendations email including
  the portfolio-insurance section.

**One bug found and fixed during verification**: `write_ledger()`
originally appended new rows on top of all prior rows unconditionally: SO
re-running the orchestrator twice for the *same* `snapshot_date` (e.g.
after a code fix) left both runs' rows in the ledger instead of replacing
that date's rows — this is exactly how a stale, already-fixed `^VIX`
candidate briefly survived in the committed ledger after the fix that
was supposed to remove it. Fixed: `write_ledger()` now purges any prior
row whose `trade_id` belongs to the date being written before appending,
so a same-date rerun replaces rather than duplicates. Verified both
directions (same-date replace, different-date accumulate) with synthetic
fixtures before confirming on real data.

## What's next

- **Sub-project 4** (strategy comparison/backtesting against tracked
  outcomes) — not started, deliberately deferred until the recommendation
  ledger accumulates real history to compare against.
- **Let calendar/diagonal candidates start appearing** — no action
  needed, just time: the term-structure history gate needs 5+ trading
  days of accumulated `atm_iv_history` per expiration pair, which only
  started accumulating once sub-project 2 shipped in late August.
- **`ACCOUNT_EQUITY` in `pipeline/config.py`** is a placeholder
  (`100000`) — edit it to the user's real trading capital before relying
  on `suggested_contracts` for real position sizing.
- Post-entry position management (Card Game Value exits, Third-Third-Third
  loss ladders, etc.) remains explicitly out of scope — the ledger only
  ever records entry recommendations, not open positions. A natural
  future sub-project once real recommendations have something to track.

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
- `docs/superpowers/specs/` — 3 design specs (playbook, pipeline,
  strategy engine)
- `docs/superpowers/plans/` — 3 implementation plans, all fully executed
- `pipeline/` — local pipeline code: `config.py`, `db.py`, `greeks.py`,
  `merge_and_score.py`, `atr.py`, `directional_bias.py`,
  `strategy_rules.py`, `scoring.py`, `screen_trades.py`, plus
  `verify_greeks.py`/`verify_scoring.py`
- `cloud/` — GitHub-Actions-runnable scripts: `fetch_options_snapshot.py`,
  `fetch_daily_true_range.py`
- `data/db/options.db` — gitignored SQLite DB, regenerable from published
  snapshots
- `data/github_sync/` — published pipeline data: `options_snapshots/`,
  `signals/`, `daily_true_range/`, `options_ledger/` (recommendation
  ledger)
