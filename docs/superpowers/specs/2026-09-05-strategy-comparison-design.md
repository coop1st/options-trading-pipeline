# Strategy Comparison & Simulated Outcome Tracking — Design

## Context

This is the fourth and final planned sub-project of the Options Trading
project (see `2026-08-26-options-playbook-design.md`,
`2026-08-26-data-and-scoring-pipeline-design.md`, and
`2026-09-05-strategy-engine-design.md` for the prior three, all complete
and live):

1. **Options Playbook** — the `options-playbook` skill.
2. **Data & Scoring Pipeline** — daily options-chain signals export.
3. **Strategy/Screening Engine** — hard-gated, scored, ranked trade
   candidates published to the options recommendation ledger.
4. **Strategy Comparison** (this spec) — was explicitly deferred in both
   prior specs until "the recommendation ledger has real tracked outcome
   history to compare against." No such history exists yet, because
   nothing tracks outcomes — the recommendation ledger only ever records
   what was *recommended*, never what happened to it. This sub-project
   builds that tracking and the comparison it enables.

**Resolved with the user before writing this spec**: outcome data is
**simulated/paper-tracked**, not manually logged. Each recommendation's
book-cited exit rule is automatically replayed against later `signals.csv`
snapshots — no ongoing data entry required. This sidesteps needing to
know whether the user actually took a given trade, which the pipeline has
no way to observe.

## Goals

- Simulate each published recommendation's outcome by replaying its
  strategy family's book-cited exit rule against the same contracts'
  prices in later `signals.csv` snapshots.
- Persist enough at recommendation time (the 7-criteria score breakdown)
  and at outcome time (status, date, realized result) to support two
  aggregate views: performance **by strategy family** and performance
  **by scoring criterion** — the latter resolves sub-project 3's own
  deferred open question ("worth revisiting [score weighting] once the
  ledger has enough history").
- Publish a **weekly digest email** summarizing both views, via a new
  Claude Code cloud routine, matching the Stocks project's existing
  weekly-report precedent (`draft_weekly_email.py` / the pick-tuning
  review routine).
- Do all of this **without any new external data fetch** — everything
  needed already exists in the repo (past `signals.csv` files, the
  recommendation ledger) once the New Data Prerequisite below is added.

## Non-goals

- **Real fill tracking.** Explicitly declined in favor of simulation —
  see Context. Nothing here assumes the user took any specific trade.
- **Adjustment simulation.** The books' management-phase tools (kite
  spread, ratio-spread adjustments, rolling) are not modeled. Each
  simulated position is tracked from entry to one terminal outcome
  (target hit, stop hit, time exit, or expiration) with no simulated
  mid-course adjustments — the iron condor's Third-Third-Third ladder is
  used only for its **final** threshold (exit at the full credit-received
  loss), not its staged 1/3-adjustment/2/3-adjustment triggers, since
  simulating an adjustment trade requires modeling a position this
  pipeline was never designed to construct. This is a real simplification
  worth stating plainly rather than pretending the simulation captures
  book-accurate risk management.
- **Changing the scoring formula itself.** This sub-project produces the
  data needed to judge whether `scoring.py`'s criteria and unweighted
  average are working; it does not itself re-weight or rewrite
  `scoring.py`. That would be a follow-up decision made *from* this
  sub-project's output, not part of building it.
- **Portfolio-level performance** (aggregate P&L across all simultaneously
  open positions, correlation/drawdown analysis). Per-trade and
  per-family/per-criterion aggregation only.

## New Data Prerequisite: persisting the score breakdown

Writing this spec surfaced one real gap: `screen_trades.py` already
computes each candidate's full 7-criterion breakdown
(`score_candidate()`'s second return value) but only ever uses it for
ranking — it's discarded after `score_and_rank()`, never written to the
ledger. Without it, "performance by scoring criterion" has nothing to
correlate against.

**Resolved design**: extend the recommendation ledger with 8 new columns
— `composite_score` and the 7 criteria
(`iv_richness, skew_quality, risk_reward, pop_proxy, term_structure,
liquidity, directional_alignment`) — populated at write time from the
same breakdown dict already computed, repeated across every leg row of a
`trade_id` (same convention `suggested_contracts` already uses). No new
file, no new fetch — purely a "stop discarding data already computed."

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│ Inputs (already published, read fresh each run)                      │
│  • data/github_sync/signals/*.csv          (full history, this repo) │
│  • data/github_sync/options_ledger/options_recommendation_ledger.csv │
│    (now carrying the score breakdown, per the prerequisite above)    │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ pipeline/track_outcomes.py  (new GitHub Actions workflow, daily)      │
│  For every trade_id not yet at a terminal outcome: replay its         │
│  family's exit rule against every signals.csv dated after its entry,  │
│  in order, and write outcome_status/outcome_date/realized_pct.        │
│  No external fetch -- every input is already in this repo, so this    │
│  runs entirely in GitHub Actions, decoupled from the local-PC-only    │
│  cadence that constrains merge_and_score.py/screen_trades.py.         │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ pipeline/compare_strategies.py  (new GitHub Actions workflow, weekly) │
│  Reads the ledger's terminal-outcome rows, aggregates by strategy     │
│  family (win rate, avg realized_pct, sample size) and by each of the  │
│  7 criteria (does a high score on this criterion correlate with a     │
│  win?), publishes a report file. Also mechanical -- no external fetch.│
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ New weekly Claude Code cloud routine ("Strategy performance digest")  │
│  Reads the published report, drafts a Gmail digest -- judgment layer  │
│  only (composing the email), matching the existing GH-Actions-vs-     │
│  routine split used throughout this project.                          │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Detail: Exit-Rule Simulation

Each family's simulated exit rule is drawn from the same book citations
already used to build the candidate in sub-project 3 — no new criteria
invented. All monetary figures are recovered **purely from the ledger's
already-recorded per-leg entry prices** (`leg_role` + the `rec:` column's
`contractSymbol/price`), not from any new stored field:

- **Credit received** (credit structures: verticals, condors) = sum of
  short-leg entry prices − sum of long-leg entry prices.
- **Debit paid** (debit structures: long calendars, double diagonals) =
  sum of long-leg entry prices − sum of short-leg entry prices.
- **Cost to close now**, on any later date = sum of each short leg's
  *current* price (what it costs to buy back) − sum of each long leg's
  current price (what it's worth to sell) — the mirror-image calculation,
  evaluated using that date's `signals.csv`.

| Family | Simulated rule | Source |
|---|---|---|
| Iron condor | `HIT_TARGET` once `(credit − cost_to_close_now) / credit ≥ 0.55`; `TIME_EXIT` once DTE remaining ≤ 30; `HIT_MAX_LOSS` once `cost_to_close_now − credit ≥ credit` (the absolute ceiling — "never exceed the value of credit received"); checked in that priority order on whichever comes first chronologically. | `income-strategies.md` §4 |
| Vertical credit spread | `HIT_TARGET` once `(credit − cost_to_close_now) / credit ≥ 0.10`; `HIT_MAX_LOSS` once the spread reaches its full theoretical max loss (`cost_to_close_now == width`, i.e. both legs settled against the short side). | `spreads-and-combinations.md` §1 |
| Calendar (long/short) | `HIT_TARGET` once realized gain ≥ 5% of debit/margin; `HIT_MAX_LOSS` once realized loss ≥ 10% of debit/margin. | `spreads-and-combinations.md` §4 |
| Double diagonal | Same ~10%-of-margin target/stop discipline as calendar/condor (no more specific book number given for this structure). | `spreads-and-combinations.md` §5 |
| Long call / long put | **No book-given intermediate target** (Bittman ch.10 frames this as an individually-chosen delta-based stop, not a formula). Default: hold to expiration, outcome = final intrinsic value vs. premium paid. Flagged explicitly as this spec's own default, not a book rule — easy to change if you'd rather simulate an early stop. |

**If DTE reaches 0 before any rule triggers** (verticals/condors that
never hit target or max loss, calendars that ran past their own
short-dated horizon): mark `EXPIRED_ITM` or `EXPIRED_OTM` per the final
snapshot's moneyness, with `realized_pct` computed from final intrinsic
value.

**"Lost to tracking"**: if any leg's `contract_symbol` stops appearing in
`signals.csv` before a terminal outcome is reached (filtered by the
liquidity thresholds, or genuinely delisted) and the position hasn't yet
reached its expiration date, mark `LOST_TO_TRACKING` — reported plainly,
never guessed at, matching this project's established fail-loud
convention.

**Still open**: if the entry date is recent enough that DTE hasn't
elapsed and no rule has triggered yet, mark `OPEN` — excluded from the
win-rate aggregation (below) until it resolves.

## Component Detail: Aggregation (`compare_strategies.py`)

Reads every `trade_id` whose `outcome_status` is terminal (`HIT_TARGET`,
`HIT_MAX_LOSS`, `TIME_EXIT`, `EXPIRED_ITM`, `EXPIRED_OTM` — not `OPEN` or
`LOST_TO_TRACKING`, which have no definitive result to score):

- **By strategy family**: win rate (`HIT_TARGET`/`TIME_EXIT`-with-positive-`realized_pct`
  count over total), average `realized_pct`, sample size. Small-sample
  families (fewer than 5 terminal trades) are reported with an explicit
  "too few trades to be meaningful yet" note rather than a misleadingly
  precise percentage — matching this project's established convention for
  early-history degraded states (`atm_iv_90d_percentile`'s own
  precedent).
- **By scoring criterion**: for each of the 7 criteria, split terminal
  trades into above-median vs. below-median on that criterion's entry-time
  score, and compare win rates between the two halves — a simple,
  transparent signal of whether that criterion is actually predictive,
  without fitting a model the ledger doesn't have enough data to support
  yet.

Publishes `data/github_sync/options_ledger/strategy_performance_report.csv`
(or `.md` — implementation-time choice), read by the new routine.

## Error Handling

- Per-`trade_id` try/except-and-continue isolation, matching every prior
  script's convention — one malformed row shouldn't block the rest.
- Missing/empty `signals.csv` history for a date range → that trade stays
  `OPEN`, not a failure.
- Aggregation over zero terminal trades (e.g. the very first week) →
  the routine drafts an email saying so explicitly, not an empty or
  fabricated report — same staleness-safety-net pattern component D
  already uses.

## Testing

No pytest, matching this project's convention.
`pipeline/verify_track_outcomes.py`: synthetic ledger + synthetic
multi-date signals fixtures confirming each family's rule fires in the
right priority order (target before time-exit before max-loss where
multiple could apply on the same date), and that a contract's
disappearance produces `LOST_TO_TRACKING` rather than a guess.
`pipeline/verify_compare_strategies.py`: synthetic terminal-outcome rows
confirming win-rate/avg-`realized_pct` math and the above/below-median
split.

## File Breakdown

None created yet — this remains design until reviewed:

- `pipeline/screen_trades.py` *(modify)* — persist the score breakdown
  into the 8 new ledger columns.
- `pipeline/track_outcomes.py` *(new)* — the exit-rule simulator.
- `pipeline/verify_track_outcomes.py` *(new)*.
- `pipeline/compare_strategies.py` *(new)* — the aggregation script.
- `pipeline/verify_compare_strategies.py` *(new)*.
- `.github/workflows/track-outcomes.yml` *(new)* — daily, mechanical.
- `.github/workflows/compare-strategies.yml` *(new)* — weekly, mechanical.
- New `RemoteTrigger` routine, "Strategy performance digest" — weekly,
  judgment-only (composes the email from the published report).

## Open Questions

- **Report format**: CSV (machine-joinable, matches every other ledger in
  this project) vs. Markdown (more directly routine-readable prose).
  Leaning CSV for consistency; the routine can format it into prose
  either way.
- **Weekly routine's exact schedule**: leaning toward mirroring the
  Stocks project's existing weekly-digest timing for consistency, to be
  finalized in the implementation plan.
- **Long call/put's "hold to expiration" default** (flagged above) — open
  to a different default (e.g., a fixed delta-based stop) if you'd rather
  simulate active management for directional trades too.
