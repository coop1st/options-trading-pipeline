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
- **Stop discarding the 7-criteria score breakdown.** `screen_trades.py`
  already computes it for every candidate and throws it away after
  ranking — this sub-project's first, non-negotiable requirement is to
  persist it at recommendation time (see "New Data Prerequisite" below),
  because without it there is nothing to correlate outcomes against.
  Persisting it and building the correlation view are two parts of the
  same goal, not a nice-to-have layered on top.
- Combine that persisted breakdown with the simulated outcome data to
  support two aggregate views: performance **by strategy family** and
  performance **by scoring criterion** — the latter resolves sub-project
  3's own deferred open question ("worth revisiting [score weighting]
  once the ledger has enough history").
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

## New Data Prerequisite: persisting the score breakdown (required, not optional)

Writing this spec surfaced one real gap: `screen_trades.py` already
computes each candidate's full 7-criterion breakdown
(`score_candidate()`'s second return value) but only ever uses it for
ranking — it's discarded after `score_and_rank()`, never written to the
ledger. Without it, "performance by scoring criterion" has nothing to
correlate against. This is confirmed as a required part of this
sub-project's scope, not a deferred nice-to-have: the whole point of
tracking outcomes is to eventually know whether the composite score (and
each of its 7 inputs) actually predicts anything, and that's impossible
to answer retroactively for trades whose breakdown was never recorded.

**Resolved design**: extend the recommendation ledger with 8 new columns
— `composite_score` and the 7 criteria
(`iv_richness, skew_quality, risk_reward, pop_proxy, term_structure,
liquidity, directional_alignment`) — populated at write time from the
same breakdown dict `score_and_rank()` already computes, repeated across
every leg row of a `trade_id` (same convention `suggested_contracts`
already uses). No new file, no new fetch, and — importantly — no
retroactive backfill possible for trades already recommended before this
ships: those rows keep blank score columns and are excluded from the
by-criterion aggregation (but still included in the by-family
aggregation, since family and outcome are both known regardless). This
takes effect the moment `screen_trades.py` is modified, so the sooner
this sub-project ships, the less history is lost to the gap.

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
| Long call / long put | `HIT_MAX_LOSS` once `cost_to_close_now / premium_paid ≤ 0.50` (50% of premium lost); `HIT_TARGET` once `cost_to_close_now / premium_paid ≥ 2.00` (premium doubled); otherwise ride to expiration, outcome = final intrinsic value vs. premium paid. See rationale immediately below — this is this spec's own choice, not a book formula. |

**Rationale for the long call/put rule** (an explicit exit strategy is
required here — an earlier draft of this spec defaulted to "hold to
expiration with no intermediate exit," which was wrong: every other
family gets a defined exit, and letting directional trades ride
unconditionally to expiration wasn't just under-specified, it silently
gave this one family a different, harsher risk profile than the rest of
the simulation). The books give no formula, but they do give direction:
`directional-strategies.md` §6 (Bittman ch.10) states the dominant risk
for a long option is delta and calls for "individually-chosen stop-loss
points... set *below* the theoretical max loss, since few traders want
to risk 100% of a long option's premium" — i.e., a stop-loss expressed
as a fraction of premium is exactly the book's own framing, just without
a specific fraction attached. 50% is this spec's chosen fraction:
concrete enough to simulate, conservative enough to leave real room
between it and the 100%-of-premium theoretical max the book explicitly
says traders avoid risking in full. The 100%-gain profit target is the
mirror choice, giving the simulation a defined upside endpoint
consistent with `directional-strategies.md` §5's framing of long
options as an inherently asymmetric risk/reward tool worth capturing
gains from rather than assuming will run unboundedly — not a number the
books state directly, so flagged the same way `CONDOR_MIN_DTE`'s 45–75
window was flagged in sub-project 3: an implementation choice standing
in for a judgment call the books leave to the individual trader. Both
numbers are ordinary config constants once implemented
(`DIRECTIONAL_STOP_PCT = 0.50`, `DIRECTIONAL_TARGET_PCT = 2.00`) and
easy to change later if real outcome data suggests they're miscalibrated
— which is, not incidentally, exactly what this sub-project exists to
find out.

**If DTE reaches 0 before any rule triggers** (verticals/condors that
never hit target or max loss, calendars that ran past their own
short-dated horizon): mark `EXPIRED_ITM` or `EXPIRED_OTM` per the final
snapshot's moneyness, with `realized_pct` computed from final intrinsic
value — **provided** at least one leg still has pricing data on or near
expiration. See below for the case where it doesn't.

**Data gaps are not terminal — every run re-scans full history, not just
forward from the last checkpoint.** A contract can legitimately vanish
from one day's `signals.csv` and reappear later (e.g. it dipped below
`MIN_VOLUME`/`MIN_OPEN_INTEREST` for a session, or its symbol was
skipped that day by component B's rate-limit skip-and-continue handling)
— treating a single absence as a permanent loss would be premature and
was the wrong design in an earlier draft of this spec. The corrected
algorithm: for any `trade_id` not yet at a terminal outcome, walk
**every** `signals.csv` date after entry, in chronological order, up to
today. A date where a needed `contract_symbol` is simply absent is
**skipped, not treated as a signal** — evaluation continues to the next
available date where pricing exists, applying the family's exit rule at
each point that has data. Because `track_outcomes.py` runs daily (per
the Architecture section), a trade that has no resolvable data point
today is naturally re-checked again tomorrow as new `signals.csv` files
publish, with no special retry logic needed beyond "always re-scan from
entry, not from the last run's stopping point."

**`UNRESOLVED_AT_EXPIRATION`** (replaces the earlier, too-eager
`LOST_TO_TRACKING` design): only once a position's expiration date has
**passed** and **no signals.csv snapshot at any point after entry ever
contained pricing for the position's legs** does tracking give up and
mark it terminal — at that point there is no data anywhere to compute a
final value from, so guessing would be worse than reporting the gap
plainly. This should be rare: it only fires for a contract that
disappeared from every single fetch for a position's entire holding
period, not merely a one-day gap.

**Still open**: if DTE hasn't elapsed, no rule has triggered on any
available data point yet, and expiration hasn't passed, mark `OPEN` —
excluded from the win-rate aggregation (below) until it resolves to a
terminal status on some future daily run.

## Component Detail: Aggregation (`compare_strategies.py`)

Reads every `trade_id` whose `outcome_status` is a *scoreable* terminal
state (`HIT_TARGET`, `HIT_MAX_LOSS`, `TIME_EXIT`, `EXPIRED_ITM`,
`EXPIRED_OTM`) — not `OPEN` (still unresolved) and not
`UNRESOLVED_AT_EXPIRATION` (terminal, but with no data to derive a
result from, so it's reported as its own count in the digest rather than
folded into win-rate math):

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
multi-date signals fixtures confirming (a) each family's rule fires in
the right priority order (target before time-exit before max-loss where
multiple could apply on the same date), (b) a one-day gap in a
contract's data is skipped over and evaluation resumes correctly on the
next date the contract reappears (not marked terminal on the first
absence), and (c) only a contract absent from *every* date through
expiration produces `UNRESOLVED_AT_EXPIRATION`.
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
- **`DIRECTIONAL_STOP_PCT`/`DIRECTIONAL_TARGET_PCT` (50%/200% of
  premium)** — resolved with a concrete rule and rationale above rather
  than left open, but the exact fractions are still this spec's own
  choice rather than a book number; easy to retune once real data exists
  to check them against.
