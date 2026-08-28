# Handover — pick this up from here

Last updated 2026-08-28 (evening) to hand this project off between Claude
Code sessions. Everything referenced here is committed and pushed to
`master` at https://github.com/coop1st/options-trading-pipeline (public
repo). Read this file first, then the specs/plans it points to.

**Session paused mid-design on sub-project 3 — resume there.** See
"Sub-project 3" section below for exactly where the brainstorming left
off and what to do next (write the spec doc — nothing has been built or
committed for sub-project 3 yet, this is all still design).

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
all complete, one final-review fix round). All four components are live:

- **A (watchlist)** — read live from the Stocks project's public
  `stock_price_ledger.csv`, no separate file, per spec.
- **B (cloud fetch)** — `.github/workflows/options-snapshot-fetch.yml`
  runs `cloud/fetch_options_snapshot.py` 3x/trading day on GitHub Actions,
  fetches options chains via yfinance, commits dated CSVs to
  `data/github_sync/options_snapshots/`. Verified live: a manual trigger
  run succeeded (121/124 symbols, 8,960 rows), matching the local test run
  exactly.
- **C (local merge + score)** — `pipeline/merge_and_score.py` (run
  manually, whenever this PC is next on): pulls new snapshots, upserts
  into gitignored `data/db/options.db`, computes Black-Scholes Greeks
  (`pipeline/greeks.py`, put-call-parity verified), liquidity/bid-ask
  quality flags, and ATM IV/skew reads, publishes
  `data/github_sync/signals/{date}.csv`, commits + pushes. Verified live:
  a real run published 1,369 signal rows, confirmed fetchable via
  `raw.githubusercontent.com`.
- **D (nightly cloud routine)** — created via `RemoteTrigger`, id
  `trig_019GMK964MKrAunz5KZiZv8x`, cron `30 1 * * 2-6` (~2:30am Irish
  time, Tue–Sat UTC so it always reports the prior weekday's close),
  https://claude.ai/code/routines/trig_019GMK964MKrAunz5KZiZv8x. Reads the
  latest signals CSV, checks staleness (drafts an alert email if the local
  merge script hasn't run), and — since sub-project 3 doesn't exist yet —
  drafts a diagnostic placeholder email (contract/symbol counts, IV
  richness ranking once enough history accumulates) rather than real trade
  recommendations. Manually verified: drafted a correct diagnostic email
  to kcoopercscs@gmail.com on the first try, no fixes needed.

**Not yet built, by design**: the options recommendation ledger
(`data/github_sync/options_ledger/options_recommendation_ledger.csv`,
component E) and the routine's actual trade-selection logic (spec's
component D step 3) — both depend on sub-project 3. `atm_iv_90d_percentile`
will read null for the first ~5 trading days post-deploy (needs
accumulated history); this is expected, not a bug, and the routine already
says so explicitly rather than reporting a misleading empty ranking.

**Known deferred minors** (see the plan's ledger history / final review
for full detail, none blocking): the GitHub Actions workflow still has one
residual script-injection-class line (`cloud/fetch_options_snapshot.py`'s
own invocation step interpolates `${{ steps.session.outputs.session }}`
directly — same class as a fix already applied to the session-determination
step, just one step downstream); the local merge script backfills only the
single most recent unscored date, not multiple missed nights; a handful of
Minor code-quality notes (unpinned `requirements.txt`, no workflow
timeout/concurrency guard, etc.).

## Sub-project 3 (Strategy/Screening Engine) — design in progress, brainstorming path

**Status: architecture agreed with the user in chat, spec doc not yet
written.** Session was parked here — **next step on resume is to write
this up as a spec at `docs/superpowers/specs/YYYY-MM-DD-strategy-engine-design.md`
following the brainstorming skill's architectural path** (self-review,
then have the user review the written spec, then `writing-plans`). Do
not skip straight to a plan/implementation — the spec hasn't been
written or reviewed yet, only talked through.

**Scope decided:**
- **Split from sub-project 4**: this sub-project is (a) picking which
  underlyings to screen and (b) generating broad-coverage trade
  candidates. A/B-testing/comparing strategies against each other is a
  *separate, future sub-project 4*, deferred until the recommendation
  ledger has real tracked outcome history to compare against — it can't
  produce anything meaningful before that.
- **Strategy coverage**: broad — income (vertical credit spreads, iron
  condors), directional (long calls/puts), and calendars/diagonals. All
  three families, not a narrower first slice.
- **Selection criteria source**: strictly the two source books' own
  documented criteria (via the `options-playbook` skill), not an
  invented multi-indicator framework. Key source sections already
  identified and read this session:
  - `income-strategies.md` §1 "Five underwriting decisions" (Ch.2) and
    §6 "Pre-Trade Evaluation" checklist (Ch.4) — market/strategy/
    duration/volatility/pricing decisions, condition-of-the-market
    assessment, IV/term-structure/skew evaluation, strike-picking
    guidance.
  - `income-strategies.md` §3 (vertical credit spreads: 30–60 DTE,
    skew-tracks-spread-width) and §4 (iron condors: 60 DTE, 10–15 delta,
    ATR-relative vol condition, 55%-of-credit/30-DTE exit target,
    Third-Third-Third loss discipline).
  - `directional-strategies.md` §5 "Choosing a Directional Trade" (Ch.2)
    — same five decisions, but **explicitly requires a directional view**
    the books don't prescribe a method for ("technical or fundamental
    analysis, whatever's comfortable") — this is the one place the
    books punt, and it's resolved below via the new Stocks-project
    ledger.
  - `income-strategies.md` §5 position sizing (2%/trade, 6%/month caps;
    Card Game Value exit ~$0.10–0.25).
  - `spreads-and-combinations.md` calendar/diagonal entry conditions
    (term-structure based) — read at a high level, not yet gone through
    in the same depth as the income/directional sections above; do that
    before writing the spec.

**Directional-bias source resolved this session**: the Stocks project's
weekly email already computes a high-conviction STRONG BUY/STRONG SELL
shortlist (`pipeline/draft_weekly_email.py`'s `build_shortlist()`) but
never used to persist it — **this session added
`Projects/Stocks/pipeline/publish_rating_shortlist.py`**, wired into
`scheduled_run.py`'s weekly stage list right before `email_draft`,
publishing to
`Projects/Stocks/data/github_sync/weekly_ratings_ledger/stock_rating_ledger.csv`
(wide format: one row per symbol, one column per week, cell =
`RATING/last_close`, e.g. `STRONG BUY/152.30`) — same convention as the
existing day-trade shortlist ledger. Tested against real local data (41
tickers, 15 BUY / 26 SELL) and pushed to
`github.com/coop1st/stocks-research-pipeline`. This options project
should read that ledger (via `raw.githubusercontent.com`, same pattern
as the existing day-trade-ledger watchlist read) for per-symbol
bullish/bearish/neutral tilt.

**Flag-vs-score decision**: hybrid, not either/or — the books' concrete
numeric thresholds (liquidity, DTE windows, delta targets) are **hard
gates** (pass/fail, exclude if failed); on survivors, a **composite
score** ranks candidates (the books explicitly favor comparative
selection — "sell the richest option... not just the first one that
fits a rule of thumb" — not a binary flag). **Top 20** ranked candidates
surface in the nightly email (user's choice over top-10 or an unbounded
score-threshold cut).

**7 scoring criteria for the composite score** (user chose to build all
7 in the first pass, not phase them in):
1. IV percentile richness (`atm_iv_90d_percentile`, already computed by
   sub-project 2)
2. Skew quality (`skew_put_pct_of_atm`/`skew_call_pct_of_atm`, already
   computed) — richest setups combine high skew + high ATM IV per the
   book
3. Risk/reward ratio of the specific structure (credit/width,
   credit/margin)
4. Modeled probability of success (delta as a POP proxy, per the condor
   sizing section)
5. Term structure signal (ATM IV across expirations for the same
   symbol — computable now, multiple expirations are already fetched
   per symbol)
6. Liquidity quality as a gradient (distance above `MIN_VOLUME`/
   `MIN_OPEN_INTEREST`, plus the `zero_bid`/`wide_spread` flags already
   in the signals export)
7. Directional tilt alignment (from the new Stocks ledger above —
   bullish tilt favors bullish structures, bearish favors bearish,
   absence of a strong signal favors neutral iron condors)

Explicitly **not** included (would need a new data source not yet
built): earnings/Fed-meeting/event-risk calendar checks, which the
books explicitly call for (`income-strategies.md` §6 "Evaluate
Potential Realized Volatility") but which needs a fetch this pipeline
doesn't do.

**File breakdown agreed** (none created yet — this is still design):
- `pipeline/strategy_rules.py` — one candidate-builder function per
  strategy family (vertical credit spreads, iron condors, long
  calls/puts, calendars/diagonals), each hard-gated by the book-cited
  thresholds above, each documented with its book/chapter citation
  (matching this project's established traceability convention). Takes
  one symbol's signals rows, returns candidate structures or nothing.
- `pipeline/scoring.py` — the 7-criteria composite score, pure function,
  no I/O, same shape as `greeks.py`.
- `pipeline/directional_bias.py` — fetches the Stocks weekly ratings
  ledger, returns each symbol's latest bullish/bearish/neutral tilt.
- `pipeline/screen_trades.py` — orchestrator (mirrors
  `merge_and_score.py`'s shape): reads signals + both Stocks ledgers,
  calls the rule builders per symbol, scores and ranks survivors, writes
  the top 20 to the recommendation ledger (component E's schema from the
  sub-project 2 spec — already fully speced, just needs its first
  writer), commits + pushes.
- Task 8's routine prompt gets a `RemoteTrigger update` once this is
  verified live — swap the current diagnostic placeholder for: read the
  recommendation ledger's newest `trade_id`s, draft the real
  recommendation email.

**Error handling agreed**: per-candidate try/except-and-continue
isolation (same pattern as `merge_and_score.py`'s Greeks/IV-skew loops).
If the directional-bias ledger fetch fails, that's a soft signal, not a
hard dependency — directional-strategy candidates get skipped for that
run (logged clearly) while non-directional strategies (iron condors)
proceed unaffected, rather than failing the whole run or silently
guessing at direction. Missing/empty signals file → "nothing to
screen," matching the existing no-data pattern.

**Testing agreed**: same convention as the rest of this project (no
pytest; run against real/synthetic data and inspect).
`pipeline/verify_scoring.py` (analogous to `verify_greeks.py`) checks
the gates and composite score behave sensibly — a candidate failing a
hard threshold gets excluded outright, not just down-scored; scores move
in the expected direction as individual criteria improve. Manual runs
against the real, already-published `signals.csv` confirm output count
≤20, leg counts per `trade_id` match the strategy (2 for a vertical
spread, 4 for an iron condor), and a few example picks are spot-checked
against the books' worked examples for plausibility.

## Environment gotcha (local machine only)

Norton antivirus on this machine does TLS inspection that breaks strict
OpenSSL certificate validation for Python HTTPS calls (shows up as
`SSL: CERTIFICATE_VERIFY_FAILED` or, more confusingly, `Basic Constraints
of CA cert not marked critical`). Already solved once in
`Projects/Stocks/pipeline/config.py` — reuse that exact fix (`truststore`
for stdlib SSL, plus exporting Windows' trusted root store to a PEM file
and setting `CURL_CA_BUNDLE` for `curl_cffi`-based libraries like
yfinance's crumb auth) rather than re-debugging from scratch. **This fix
is only needed locally** — confirmed this session that GitHub Actions
runners don't have this problem at all.

## Repo / directory pointers

- Local: `C:\Users\coope\Claude_Work\Projects\Options Trading`
- Remote: `coop1st/options-trading-pipeline` (public, pushed and up to date)
- `Material/` — source book PDFs, git-ignored, never commit
- `.claude/skills/options-playbook/` — the finished skill (SKILL.md +
  8 reference docs)
- `docs/extraction-notes/` — per-chapter extraction notes (26 files, both
  books), traceability layer behind the skill
- `docs/superpowers/specs/` — 2 design specs (playbook, pipeline)
- `docs/superpowers/plans/` — 2 implementation plans, both fully executed
  (playbook; data & scoring pipeline)
- `pipeline/` — local pipeline code (config, db, greeks, merge_and_score)
- `cloud/` — GitHub-Actions-runnable scripts (options snapshot fetch)
- `data/db/options.db` — gitignored SQLite DB, regenerable from published
  snapshots
- `data/github_sync/options_snapshots/`, `data/github_sync/signals/` —
  published pipeline data (options_snapshots is cloud-committed;
  signals is committed by the local merge script)
