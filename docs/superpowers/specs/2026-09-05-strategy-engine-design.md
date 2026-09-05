# Strategy/Screening Engine — Design

## Context

This is the third of three connected sub-projects that make up the Options
Trading project (see `2026-08-26-options-playbook-design.md` and
`2026-08-26-data-and-scoring-pipeline-design.md` for the first two):

1. **Options Playbook** (complete) — a Claude Code skill (`options-playbook`)
   distilling Bittman's *Trading Options as a Professional* and
   Chen/Sebastian's *The Option Trader's Hedge Fund* into structured
   reference docs under `.claude/skills/options-playbook/references/`.
2. **Data & Scoring Pipeline** (complete, live) — collects options-chain
   data, computes Greeks/IV/skew, and publishes a daily
   `data/github_sync/signals/{date}.csv` export.
3. **Strategy/Screening Engine** (this spec) — applies the playbook's
   book-cited entry rules to the signals export plus two feeds from the
   separate Stocks project (watchlist, directional bias) to generate
   concrete, ranked trade candidates, and writes them to the options
   recommendation ledger the nightly cloud routine emails.

Comparing/backtesting strategies against each other, and tracking realized
outcomes of past recommendations, is explicitly deferred to a future
**sub-project 4** — it needs the recommendation ledger to accumulate real
history first, which doesn't exist until this sub-project ships.

This document was written from a full re-read of all eight
`options-playbook` reference docs (`income-strategies.md`,
`directional-strategies.md`, `spreads-and-combinations.md`,
`greeks-and-volatility.md`, `risk-management-and-position-sizing.md`, plus
`glossary.md`, `market-making-techniques.md`, `trading-business-framework.md`
for cross-checking), not just the prior session's chat recap, specifically
so every numeric threshold below can be traced to its source chapter.

## Goals

- Read the daily signals export (component C's output) plus two ledgers
  published by the separate Stocks project — the day-trade watchlist
  (`stock_price_ledger.csv`, already the source of this pipeline's
  watchlist) and the new weekly ratings ledger
  (`stock_rating_ledger.csv`) — and, for every symbol with liquid signals
  data, build candidate option structures across three strategy families:
  **income** (vertical credit spreads, iron condors), **directional**
  (long calls, long puts), and **volatility/term-structure** (long
  calendars, short calendars, double diagonals).
- Exclude any candidate that fails a **hard gate**: a concrete, book-cited
  numeric threshold (DTE window, delta target, liquidity minimum,
  IV-premium threshold). Gates are pass/fail, not scored.
- Rank every surviving candidate with a **composite score** built from 7
  criteria, all traceable to specific book guidance (§ "Composite Scoring"
  below), and publish the **top 20** to the options recommendation ledger
  (`data/github_sync/options_ledger/options_recommendation_ledger.csv`,
  schema already fixed by the sub-project 2 spec's component E, with one
  proposed extension — see § "Proposed Extensions").
- Attach a book-cited **position-sizing suggestion** (2%-of-capital rule,
  Chen/Sebastian ch.3) to every recommended candidate, and a standing
  **portfolio-insurance reminder** (the "units" concept, ch.3/8/11) to the
  nightly output — both are new relative to the prior chat recap; see
  § "Proposed Extensions" for why they're being proposed now and what they
  need to work.
- Give the overnight cloud routine (component D, already built as a
  diagnostic placeholder) a real data source to draft its recommendation
  email from, and update its prompt once this is verified live.

## Non-goals

Kept deliberately narrow so the engine that ships is fully book-grounded
rather than half-built across too many strategies:

- **Strategy comparison/backtesting** (sub-project 4) — deferred until the
  recommendation ledger has tracked outcome history.
- **Butterflies, ratio/back spreads, the kite spread, and Bittman's
  arbitrage combinations** (conversions, reverse conversions, box spreads)
  — all fully documented in `spreads-and-combinations.md`, but **not** part
  of the three-family scope already agreed for this sub-project (income =
  vertical credit spreads + iron condors specifically, not the wider
  Chen/Sebastian ch.9 strategy list). They remain available in the skill
  for manual reference or a future sub-project, not fabricated into this
  engine's candidate universe.
- **Earnings/Fed-meeting/event-risk calendar filtering** — both books call
  for it (`income-strategies.md` §6 "Evaluate Potential Realized
  Volatility"), but it needs a data fetch (an events calendar) this
  pipeline doesn't have. Unchanged from the sub-project 2 spec's own
  non-goal.
- **Post-entry position management and exit alerting.** This is a real
  scope boundary worth stating explicitly: the recommendation ledger
  (component E) records *entry* recommendations only — it has no concept
  of an open position, a fill, or a realized P&L. That means the books'
  extensive *management*-phase machinery — the iron condor's
  Third-Third-Third loss ladder, the Card Game Value ($0.10–$0.25) exit
  heuristic, the calendar's 10%-of-margin stop, "Good Exits" percentage-
  of-margin triggers — is **not implemented here**, even though it's fully
  documented in the skill. Implementing it would require tracking which
  recommendations were actually acted on and at what fill price, which is
  a natural future sub-project once this one is generating real
  recommendations to track.
- **Portfolio-level diversification and correlation limits** (Chen/
  Sebastian ch.3: 5+ sectors, no sector >25%) and the **6%-of-capital
  monthly circuit breaker** — both require knowing the user's actual open
  positions and realized month-to-date P&L, neither of which this pipeline
  tracks. The 2%-per-trade sizing suggestion (§ "Proposed Extensions") is
  included because it only needs a single candidate's own max loss; these
  two do not.
- **Weighted-vega as a precise computed number.** Both books describe
  *why* front-month vega is more reactive than back-month vega
  (`greeks-and-volatility.md` §5) but neither gives a single closed-form
  weighting formula the way they do for gamma-across-products (§5.2's
  percentage-equivalent-move scaling). Claiming a precise "weighted vega"
  output for calendars/diagonals would mean inventing a formula the source
  material doesn't provide. See § "New Data Prerequisites" for what this
  sub-project does instead.

## New Data Prerequisites

Writing this spec against the actual book criteria (rather than the
higher-level recap) surfaced four gaps between what sub-project 2's
pipeline currently persists and what several book-cited entry conditions
actually need to be computed. These are small, targeted additions to the
existing pipeline, not a redesign of it:

1. **Underlying ATR (Average True Range).** The iron condor's volatility
   condition is explicitly "IV relative to ATR" (`income-strategies.md`
   §4, `greeks-and-volatility.md` §3), not IV in isolation. ATR needs
   daily OHLC price history per underlying (Welles Wilder's 14-day
   true-range average). Neither `options_snapshots` (option chains only)
   nor the Stocks day-trade ledger (sparse suggestion-day closing prices)
   provides this. **Needed**: a small new fetch (e.g. `yfinance`'s
   `history()`) for ~20 trading days of daily OHLC per watchlist symbol,
   either folded into component B's existing cloud fetch or added as a
   lightweight step in this sub-project's own code.
2. **Skew history, not just ATM IV history.** `merge_and_score.py`
   already persists `atm_iv_history` (symbol, expiration, date, atm_iv)
   to compute `atm_iv_90d_percentile`, but it does **not** persist
   `skew_put_pct_of_atm`/`skew_call_pct_of_atm` over time. Several
   book-cited skew rules are explicitly *relative-to-own-history*, not
   absolute (`greeks-and-volatility.md` §4.3: "skew is relative, not
   absolute" — a given skew percentage only means something compared to
   that symbol's own normal level). **Needed**: extend `db.py` with a
   `skew_history` table (mirroring `atm_iv_history`'s shape) and have
   `compute_signals()` upsert into it alongside the existing IV history
   write.
3. **Term-structure-spread history**, for the calendar/diagonal entry
   gates specifically. "At least 10% of front-month IV over the normal
   relationship" (`spreads-and-combinations.md` §4) requires knowing what
   the front-minus-back IV spread normally looks like for that symbol —
   not just today's snapshot. **Needed**: derive this from the same
   `atm_iv_history` table (now keyed per expiration) by comparing the
   *current* front/back spread against the distribution of that same
   spread on prior dates — feasible once (1) and (2) above give enough
   history, but not before.
4. **SPX/VIX in the fetch list**, only if the portfolio-insurance reminder
   (§ "Proposed Extensions") is approved — the current watchlist is
   entirely individual equities sourced from the day-trade shortlist,
   which never suggests SPX or VIX. Both books' named tail-hedge
   instruments (`risk-management-and-position-sizing.md` §8) are OTM SPX
   puts and OTM VIX calls specifically.

None of (1)–(3) block shipping the engine — they gate specific entry
conditions (condor's ATR check, calendar's "normal relationship" check,
some skew-quality scoring) that can run in a degraded/skipped mode with a
visible note until enough history accumulates, exactly like
`atm_iv_90d_percentile` already does for its first ~5 trading days
post-deploy (per the sub-project 2 HANDOVER note). (4) only matters if the
portfolio-insurance reminder is approved.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│ Inputs (all already published, read fresh each run)                  │
│  • data/github_sync/signals/{today}.csv           (sub-project 2)    │
│  • Stocks: stock_price_ledger.csv                 (watchlist)        │
│  • Stocks: stock_rating_ledger.csv                (directional bias) │
│  • options.db: atm_iv_history, skew_history*, atr_history*  (*new)   │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ pipeline/directional_bias.py                                         │
│  Reads stock_rating_ledger.csv, returns each symbol's latest          │
│  bullish/bearish/neutral tilt (most recent non-blank week column).    │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ pipeline/strategy_rules.py                                            │
│  One candidate-builder function per family, each hard-gated and       │
│  book/chapter-cited:                                                  │
│   • build_vertical_credit_spreads(signals, bias)                      │
│   • build_iron_condors(signals, atr)                                  │
│   • build_directional_longs(signals, bias)                            │
│   • build_calendars(signals, iv_history)                              │
│   • build_diagonals(signals, iv_history)                              │
│  Each takes one symbol's signal rows (+ the inputs it needs) and      │
│  returns zero or more candidate structures, or nothing.               │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ pipeline/scoring.py                                                   │
│  Pure function: 7-criteria composite score per candidate (no I/O),    │
│  same shape as greeks.py. Returns a 0-100 score plus a per-criterion   │
│  breakdown (kept for traceability in the ledger / debugging).         │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ pipeline/screen_trades.py  (orchestrator, mirrors merge_and_score.py) │
│  1. Read today's signals.csv, the two Stocks ledgers, and history.    │
│  2. For each watchlist symbol: call every applicable builder.         │
│  3. Score and rank all survivors; take the top 20 overall.            │
│  4. Attach a position-sizing suggestion to each (§ Proposed           │
│     Extensions).                                                      │
│  5. Write the options recommendation ledger; commit + push.           │
│  6. Append the standing portfolio-insurance reminder line, if          │
│     approved (§ Proposed Extensions).                                 │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ Overnight cloud routine (component D, already built)                  │
│  Swap the current diagnostic placeholder for: read the ledger's       │
│  newest trade_ids, draft the real recommendation email.               │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Detail: Strategy Families

Each family below lists **construction**, **hard gates** (pass/fail,
excludes the candidate outright), and **not-gated** book guidance that
instead feeds the composite score (§ next section). Every threshold is
labeled either book-verbatim or an explicit implementation choice, per the
"don't hallucinate precision" instruction.

### A. Vertical Credit Spreads

*Source: `income-strategies.md` §3, `spreads-and-combinations.md` §1.*

**Construction**: bullish → sell higher-strike put, buy lower-strike put
(vertical put credit spread); bearish → sell lower-strike call, buy
higher-strike call (vertical call credit spread). Built only for symbols
with a bullish or bearish tilt from `directional_bias.py` — no tilt, no
candidate (a non-directional structure isn't this family's job; that's the
iron condor below).

**Hard gates**:
- DTE **30–60** (book-verbatim, `income-strategies.md` §3).
- Directional tilt present (STRONG BUY → put credit spread; STRONG SELL
  → call credit spread) — absence excludes the symbol from this family
  entirely, per the error-handling convention in § "Error Handling".
- Underlying liquidity floor, per `directional-strategies.md` §5 / Ch.2:
  equities need **>50,000 contracts/day** aggregate volume; ETFs need
  **>500 open interest per strike**. *Implementation choice, flagged*:
  the pipeline doesn't currently classify a symbol as equity/ETF/index, so
  the conservative default is to apply the equity threshold uniformly
  until an instrument-type classification is added — see Open Questions.

**Not gated (feeds scoring instead)**: strike/width selection.
`income-strategies.md` §6 and `spreads-and-combinations.md` §1 both
explicitly warn against anchoring to a fixed delta or fixed width — "sell
the richest option near the target, not just the first one that fits a
rule of thumb." The builder therefore constructs candidates at a small
fixed set of widths (5-point and 10-point, configurable) across a band of
short strikes (10–30 delta) and lets the composite score's risk/reward and
IV-richness criteria pick the winner, rather than gating on one delta.
Skew-tracks-width guidance (steeper skew → narrower spread) is a scoring
input for the same reason: the books give the *direction* of the
relationship, not a numeric cutoff.

### B. Iron Condors

*Source: `income-strategies.md` §4, `spreads-and-combinations.md` §2.*

**Construction**: short call spread above the market + short put spread
below it, same expiration. Built for every symbol regardless of
directional tilt — this is the non-directional counterpart to family A,
and per `income-strategies.md` §4 works better *without* needing a
directional view.

**Hard gates**:
- Delta **10–15** on both short strikes (book-verbatim: "the 10–15 delta
  range... to capture this decay window").
- DTE window **45–75, centered on 60**. *Implementation choice, flagged*:
  the book states "around 60 days to expiration" as "the near-universal
  optimal entry," not a literal range — 45–75 is this spec's own
  reasonable operationalization of "around," not a book number.
- **IV vs. ATR**: today's ATM IV must exceed the underlying's 14-day ATR
  (book-verbatim mechanism, `greeks-and-volatility.md` §3). **Gated only
  once ATR history exists** (§ "New Data Prerequisites" item 1) — until
  then this gate is skipped with a visible note, matching the
  `atm_iv_90d_percentile` precedent from sub-project 2.

**Not gated (feeds scoring instead)**: skew steepness (a soft warning
sign per the book, not a cutoff), and the risk/reward-vs-probability
framing ("$2.00 credit on a 10-point spread... 85% probability is very
favorable, 70% much less so" — an example, not a threshold).

### C. Directional Long Calls / Long Puts

*Source: `directional-strategies.md` §1–2, §5–6.*

**Construction**: bullish tilt → long call; bearish tilt → long put. No
synthetic positions, no verticals-as-directional-substitute — those
remain documented in the skill but are out of this engine's candidate set
(the skill's own summary already frames verticals as *this sub-project's
family A when a falling-IV expectation exists*, but building that
substitution logic wasn't part of the agreed scope, so it's left as
manual-reference-only for now).

**Hard gates**:
- Directional tilt present (STRONG BUY → long call; STRONG SELL → long
  put) — no tilt, no candidate.
- Same underlying liquidity floor as family A
  (`directional-strategies.md` §5).
- DTE: no book-given numeric window for outright directional options (the
  books frame this via the three-part price/time/volatility forecast, not
  a DTE rule) — **no DTE hard gate for this family**, an explicit
  decision rather than an invented number.

**Not gated (feeds scoring instead)**: entry IV level. Per §5, buying when
IV is elevated "raises the bar the directional move must clear to
profit" — the books give the *direction* of this effect (buy calls/puts
when IV is cheap relative to the underlying's own history) with a worked
example (Joe/Jumpco) showing a correct directional call still losing 40%
purely from IV reverting lower, but no numeric IV-percentile cutoff — so
this becomes criterion #1 of the composite score (§ next section), not a
gate.

### D. Calendar Spreads (Long and Short)

*Source: `spreads-and-combinations.md` §4.*

**Construction**: long calendar (sell front month, buy back month, net
debit) when the front month is rich; short calendar (buy front month,
sell back month, net credit) when the front month is cheap. Built for
symbols with **no strong directional tilt** (neutral), per
`income-strategies.md`/Chen/Sebastian ch.2's note that calendars suit "a
market forecast of sideways movement."

**Hard gates**:
- **Long calendar**: front-month IV trading at **≥10%** premium over its
  normal relationship to the back month (book-verbatim: "front IV 20% →
  look for a 2-point premium"); **exclude outright above a 25% premium**
  without a manual investigate-first flag (book-verbatim: "be wary above
  a 25% premium — investigate before trading").
- **Short calendar**: front month at a **10% discount** to normal ATM IV
  (book-verbatim, mirror image).
- Both: avoid the final days before expiration (book says avoid "the
  final days"; **implementation choice**: hard-gate out anything inside
  **10 calendar days** to expiration on the front leg, since the book
  doesn't give an exact day count — flagged as this spec's own number).
- **Gated only once term-structure-spread history exists** (§ "New Data
  Prerequisites" item 3) — "normal relationship" is inherently a
  relative-to-own-history comparison, so until that history accumulates,
  calendar candidates are skipped entirely with a visible note (not
  built with a fabricated "normal" baseline).

**Not gated (feeds scoring instead)**: nothing else — the entry criteria
here are almost entirely the term-structure gate itself per the book.

### E. Diagonal Spreads / Double Diagonals

*Source: `spreads-and-combinations.md` §5, `greeks-and-volatility.md` §4.6.*

**Construction**: double diagonal only (sell front-month OTM call and put,
buy further-out back-month OTM call and put) — the single-sided diagonal
variant is named in the books only as a vocabulary item, with no
construction detail beyond "an extension of the calendar concept," so
building it would mean inventing entry rules the source doesn't give. Only
the double diagonal, which the books do document with a worked example,
is implemented.

**Hard gates**: same term-structure gate as family D (front month elevated
relative to further-out months), plus the same history prerequisite.

**Not gated (feeds scoring instead)**: skew richness on both wings (the
book gives direction — "skew on both wings is rich enough to justify
selling" — not a cutoff). **Explicitly not computed**: a precise
"weighted vega" figure — per the Non-goals section, the books describe the
front/back reactivity difference qualitatively, without a closed-form
weighting formula, so this sub-project does not fabricate one. The
composite score's IV-richness criterion is computed on raw (per-leg) IV
instead, with a documentation note in the ledger that weighted-vega sizing
remains a manual step per the skill until a defensible formula exists.

## Composite Scoring (`pipeline/scoring.py`)

Per candidate, 7 criteria are each mapped to a 0–100 sub-score, then
combined (simple average by default — see Open Questions on weighting).
Where the books don't support a family-specific formula, that
family/criterion cell defaults to a **neutral 50** rather than a
fabricated number, so it doesn't bias the ranking either direction.

| # | Criterion | Formula | Family notes |
|---|---|---|---|
| 1 | IV percentile richness | Net-short-premium families (A, B, D-long, E): score = `atm_iv_90d_percentile` (higher = richer to sell, favorable). Net-long-premium families (C, D-short): score = `100 − atm_iv_90d_percentile` (lower percentile = cheaper to buy, favorable). | Direction of the mapping is book-cited per family (`income-strategies.md` §6 "Evaluate Implied Volatility"; `directional-strategies.md` §5); the percentile itself is already computed by sub-project 2. |
| 2 | Skew quality | A (put spread): `skew_put_pct_of_atm`. A (call spread): `skew_call_pct_of_atm`. B: average of both, softly weighted (skew "matters less" for condors per `income-strategies.md` §4). D, E: **neutral 50** — book says skew "roughly nets out" for calendars (`spreads-and-combinations.md` §4). C: **neutral 50** — books name skew as *a* relevant measure for directional trades but give no computable rule. | Per `greeks-and-volatility.md` §4.3: richest setups combine high skew *and* high ATM IV — this criterion is intentionally kept separate from #1 rather than pre-multiplied, so both can be inspected independently in the ledger. |
| 3 | Risk/reward of the structure | A, B: `credit / spread_width` (book's own framing, e.g. "$2.00 credit on 10-point width = 25% return on risk"). D, E: front-back IV spread size scaled between the 10% floor and 25% caution ceiling (bigger spread within the safe band = richer setup). C: **neutral 50** — outright long options are capped-risk/uncapped-reward by construction (§1–2), not a comparable ratio. | |
| 4 | Modeled probability of success (POP proxy) | A, B: `1 − |short strike delta|` (industry-standard delta-as-OTM-probability approximation; consistent with the book pairing 10–15 delta with "85% modeled probability of success"). C: the long option's own delta (probability of finishing ITM). D, E: **neutral 50** — the books frame these as term-structure/volatility trades, not probability-of-success trades. | |
| 5 | Term structure signal | All families: `(this expiration's atm_iv − average atm_iv of the symbol's other fetched expirations) / average`, oriented by the same net-short/net-long logic as #1 (elevated-relative-to-neighbors favors selling that month; cheap-relative-to-neighbors favors buying it). | Generalizes `income-strategies.md` §6's "Evaluate the Months" checklist item across all families using expirations already fetched per symbol (component B fetches out to ~75 DTE). |
| 6 | Liquidity gradient | All families: normalized distance of `volume`/`open_interest` above `MIN_VOLUME`/`MIN_OPEN_INTEREST` (already in `config.py`), penalized by the existing `zero_bid`/`wide_spread` flags. | Reuses sub-project 2's already-computed liquidity-quality signals directly — no new computation. |
| 7 | Directional tilt alignment | A, C: full credit if the candidate's direction matches the Stocks ledger's tilt (it must, per each family's hard gate, so this is really a strength-of-signal score — e.g. how many consecutive weeks the tilt has held). B, D, E: full credit if there is **no** strong tilt (these are the neutral structures) — a strong tilt on the underlying is a mild negative for a neutral structure, not a gate. | |

**Ranking and output**: candidates are scored across all applicable
families for a symbol, sorted descending by composite score across the
*entire* day's candidate universe (not per-symbol), and the **top 20**
overall are written to the ledger — matching the number already agreed
with the user over building an unbounded score-threshold cut.

## Proposed Extensions Beyond the Prior Recap

Two additions surfaced while reading the risk-management reference in
full, both clearly book-mandated but not discussed in the prior session's
recap — flagging both explicitly for your review rather than silently
folding them in.

### 1. Position-sizing suggestion (2% rule)

`risk-management-and-position-sizing.md` §6 (Chen/Sebastian ch.3) gives
the two core money-management rules — never risk more than 2% of capital
on one trade, stop trading for the month past a 6% monthly loss — and a
worked refined-sizing method (use the *actual* stop-loss threshold, not
full theoretical margin, since realized risk on a well-managed trade is
much smaller than max loss). Proposal: attach a `suggested_contracts`
figure to every recommended candidate:

```
per_contract_max_loss = (spread_width − credit) × 100        # A, B
                       = debit_paid × 100                     # D-long, E
                       = margin × configured_stop_pct         # D-short
                       = premium_paid × 100                   # C
suggested_contracts = floor(ACCOUNT_EQUITY × 0.02 / per_contract_max_loss)
```

This needs one new config constant, `ACCOUNT_EQUITY`, which the pipeline
has no existing source for (nothing in this project or the Stocks project
tracks the user's actual trading capital) — see Open Questions. The
**6%-monthly circuit breaker is not implemented**: it requires tracking
realized month-to-date results, which doesn't exist without the
post-entry tracking explicitly out of scope above.

### 2. Portfolio-insurance ("units") standing reminder

`risk-management-and-position-sizing.md` §8 (Chen/Sebastian ch.3/8/11) is
emphatic that *any* book of premium-selling trades should carry a
standing tail hedge — cheap, deep-OTM SPX puts or VIX calls, sized at
5–10% of allocated trading capital, bought *before* it's needed ("buy 'em
when you can, not when you have to"). Given how much of this engine's
output (families A, B, D-long, E) is structurally short volatility, and
how directly the books tie that structural short-vol exposure to needing
this hedge, leaving it out felt like skipping a base the user explicitly
asked to cover. Proposal, scoped modestly: not a scored/ranked candidate,
just a standing line in the nightly email restating the rule and — once
SPX/VIX are added to the fetch list (§ "New Data Prerequisites" item 4)
— citing the day's cheapest qualifying contract (delta <5, price under a
small configurable ceiling) as a concrete example. Sizing the hedge
precisely to the book's stated goal (breakeven-or-better on a 10% market
drop, profitable on a 20% drop) would need a scenario-pricing model well
beyond a Black-Scholes snapshot, so this reminder stops at "here's a
qualifying contract," not "here's the exact size to buy."

**If either extension isn't wanted for this pass, say so during spec
review and both sections above are removed before the implementation
plan.**

## Recommendation Ledger Writer (Component E)

Reuses the schema already fixed in the sub-project 2 spec
(`symbol, company_name, trade_id, strategy, leg_role, rec:YYYY-MM-DD,
tgt:YYYY-MM-DD`), with **one proposed extension**: a `suggested_contracts`
column, constant across every leg row sharing a `trade_id` (per §
"Proposed Extensions" item 1). If the sizing extension is declined, this
column is dropped and the schema is implemented exactly as sub-project 2
specified it.

`pipeline/screen_trades.py` writes one row per leg (2 rows for a vertical
spread, 4 for an iron condor, 2 for a calendar, 4 for a double diagonal),
appends a new `rec:`/`tgt:` column pair for today's date exactly as the
existing ledgers do, and commits + pushes — identical mechanics to
`merge_and_score.py`'s own `commit_and_push()`.

## Error Handling

Per-candidate try/except-and-continue isolation, matching
`merge_and_score.py`'s existing per-row/per-group pattern (`greek_failures`,
`group_failures` counters, logged not raised):

- A failure in one symbol's candidate-building doesn't stop the rest of
  the watchlist from being screened.
- If the directional-bias ledger fetch fails outright, that's a **soft**
  signal: families A and C (which require a tilt) are skipped for the
  run and logged clearly; families B, D, and E (non-directional) proceed
  unaffected.
- If a hard-gate prerequisite is missing entirely (ATR history, skew
  history, term-structure history — § "New Data Prerequisites"), the
  affected gate/family is skipped with an explicit note, not silently
  defaulted to "pass."
- Missing/empty signals file → "nothing to screen," matching the existing
  no-data pattern from sub-project 2's component D staleness check.

## Testing

No pytest, matching this project's established convention (real/synthetic
data, manual inspection). `pipeline/verify_scoring.py` (analogous to the
existing `verify_greeks.py`):

- Confirms a candidate failing any hard gate is excluded outright, not
  merely down-scored.
- Confirms each of the 7 criteria moves the composite score in the
  expected direction as the underlying input improves (e.g., raising
  `atm_iv_90d_percentile` should raise a vertical-put-credit-spread's
  score, and lower a long-call's score — the inverse mapping from
  criterion #1 above, checked explicitly both directions).
- Run against the real, already-published `signals/{date}.csv`: output
  count ≤20, leg counts per `trade_id` match the strategy (2 for a
  vertical spread or calendar, 4 for a condor or double diagonal), and a
  handful of picks are spot-checked by hand against the books' worked
  examples (the AAPL vertical spread, the SPX iron condor, the OEX/SPX
  calendar examples) for plausibility, not exact reproduction.

## File Breakdown

None created yet — this remains design until the spec is approved and an
implementation plan is written:

- `pipeline/directional_bias.py` — reads the Stocks weekly ratings ledger.
- `pipeline/atr.py` *(new, per prerequisite 1)* — fetches and computes
  14-day ATR per watchlist symbol.
- `pipeline/strategy_rules.py` — one builder function per family (A–E),
  each hard-gated and book/chapter-cited in its own docstring.
- `pipeline/scoring.py` — the 7-criteria composite score, pure function,
  no I/O, same shape as `greeks.py`.
- `pipeline/screen_trades.py` — orchestrator: reads signals + both Stocks
  ledgers + history tables, calls the builders per symbol, scores and
  ranks survivors, writes the top 20 to the recommendation ledger,
  commits + pushes.
- `pipeline/verify_scoring.py` — manual verification script, no pytest.
- `pipeline/db.py` — extended with `skew_history` and (if prerequisite 1
  is implemented here rather than in component B) `atr_history` tables.
- Routine prompt update (`RemoteTrigger update`) once verified live —
  swap the current diagnostic placeholder for: read the recommendation
  ledger's newest `trade_id`s, draft the real recommendation email,
  including the portfolio-insurance reminder line if approved.

## Open Questions

Carried into the implementation plan rather than blocking this spec:

- **`ACCOUNT_EQUITY` source**: a hardcoded config constant the user edits
  directly (matching `RISK_FREE_RATE`'s precedent in `config.py`), or an
  input the nightly routine prompt asks for at draft time? Simplicity
  favors a config constant; leaning that way unless you'd rather set it
  per-run.
- **Instrument-type classification** (equity vs. ETF vs. index) for
  family A/C's liquidity floor: worth adding a small static lookup
  (the watchlist is currently all individual equities in practice, so
  this may be low-priority until SPX/VIX are added for the units
  reminder).
- **Score weighting**: this spec proposes an unweighted average across
  the 7 criteria as the simplest defensible default (no book gives
  relative weights between, say, skew quality and liquidity). Worth
  revisiting once the ledger has enough history to check whether any
  single criterion is dominating or being drowned out in practice.
- **Where prerequisite 1 (ATR fetch) lives**: folded into component B's
  existing GitHub Actions cloud fetch (keeps all market-data fetching
  cloud-side) or added as a local fetch inside this sub-project's own
  code (keeps sub-project 2's already-shipped, already-verified workflow
  untouched). Leaning toward the latter to avoid re-touching a component
  that's already live and verified, but flagging for your input.
