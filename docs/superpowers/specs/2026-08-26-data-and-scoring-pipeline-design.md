# Data & Scoring Pipeline — Design

## Context

This is the second of three connected sub-projects that make up the Options
Trading project (see `2026-08-26-options-playbook-design.md` for the full
decomposition):

1. **Options Playbook** (complete) — a Claude Code skill (`options-playbook`)
   distilling Bittman's *Trading Options as a Professional* and
   Chen/Sebastian's *The Option Trader's Hedge Fund* into structured
   reference docs under `.claude/skills/options-playbook/references/`.
2. **Data & Scoring Pipeline** (this spec) — collect options-chain data,
   compute the Greeks and derived signals the playbook needs, and surface
   them for the strategy engine to consume.
3. **Strategy/Screening Engine** — applies the playbook's rules to the
   signals this pipeline produces, to generate concrete trade
   recommendations.

This sub-project depends on nothing else being built first. Sub-project 3
depends on this one's output (the daily "signals" export) plus the
playbook skill.

## Goals

- Collect options-chain data (strikes, prices, volume, open interest,
  Yahoo's own implied volatility) for every symbol the Stocks project's
  day-trade routine has ever suggested, three times per trading day.
- Compute the Greeks (delta, gamma, vega, theta, rho) ourselves using the
  Black-Scholes formulas documented in the `options-playbook` skill, since
  the free data source doesn't provide them.
- Build our own historical archive of implied volatility, skew, and
  term-structure data over time — the free data source only ever gives a
  live snapshot, so any history has to be accumulated by us, snapshot by
  snapshot, starting now.
- Run the mechanical data collection entirely in the cloud (GitHub
  Actions), independent of any local machine being on.
- Produce one daily "signals" export (Greeks + IV + skew + liquidity
  flags) that sub-project 3's screening engine can consume without needing
  to know anything about how the data was collected.
- Track every trade recommendation sub-project 3 ever makes, leg by leg,
  in a ledger analogous to the Stocks project's `stock_price_ledger.csv`.

## Non-goals

- No live/real-time trading or order execution — this remains research and
  screening, matching the rest of the Options Trading project's scope.
- No backtesting against historical options chains — the free data source
  cannot provide historical chains (only current ones), so any backtesting
  that needs deep history remains dependent on a future paid-data decision
  (out of scope here, per the original project brainstorm).
- No filtering of the watchlist yet — every symbol ever suggested in the
  day-trade email is included, unfiltered, per explicit direction. A
  filtering/prioritization layer may be added later but isn't designed
  here.
- Sub-project 3's actual strategy/entry-selection logic is out of scope
  for this spec — this pipeline only produces the signals that logic will
  consume.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│ A. Watchlist source (no separate file — read live at fetch time)     │
│    Stocks project's public stock_price_ledger.csv, fetched via       │
│    raw.githubusercontent.com. Every symbol ever suggested in the     │
│    day-trade email, unfiltered.                                      │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ B. Cloud data collection — GitHub Actions, 3x/trading day             │
│    (market open / midday / market close, ET-anchored cron)           │
│    Self-contained script (no repo imports, matching Stocks'          │
│    cloud/*.py convention): reads the ledger's symbol list, fetches   │
│    each symbol's options chain via yfinance (all expirations out to  │
│    ~75 days), writes a dated raw CSV, commits + pushes.              │
│    Output: data/github_sync/options_snapshots/{date}_{session}.csv   │
└─────────────────────────────────────────────────────────────────────┘
                              │  (whenever the local PC is next on,
                              │   overnight Irish time)
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ C. Local nightly merge + compute (your PC)                           │
│    git pull → read the day's 3 raw snapshots → upsert into local     │
│    options.db (SQLite, gitignored, mirrors Stocks' db.py pattern) →  │
│    compute Greeks (Black-Scholes, using the playbook's formulas)     │
│    → compute liquidity flags + IV/skew reads → write compiled        │
│    "signals" export → commit + push.                                 │
│    Output: data/github_sync/signals/{date}.csv                       │
└─────────────────────────────────────────────────────────────────────┘
                              │  (~2:30am, independent of whether C
                              │   ran that night — see Error Handling)
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ D. Overnight cloud routine — Claude Code scheduled routine            │
│    (same mechanism as the day-trade/chocolate-digest routines,       │
│    NOT a GitHub Actions workflow — this step needs judgment, not     │
│    just mechanical computation)                                      │
│    Reads the latest signals CSV, invokes the options-playbook skill  │
│    to apply entry/risk rules, drafts a Gmail email of suggested      │
│    trades, and appends to the options recommendation ledger.         │
│    If the signals file is missing or stale: drafts an alert email    │
│    instead of failing silently.                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Component detail

### A. Watchlist source

No new watchlist file for this project. Every fetch (step B) reads
`https://raw.githubusercontent.com/coop1st/stocks-research-pipeline/main/data/github_sync/daytrade_ledger/stock_price_ledger.csv`
fresh, and uses every row's `symbol` column. This ledger already exists
specifically for this purpose — `update_stock_ledger.py`'s own docstring
in the Stocks project states it's designed "so a future project (options
trading, built separately) can look back... and compute how a suggested
stock actually moved from its suggestion price." No filtering is applied
now; that's an explicit non-goal for this spec.

Empirically confirmed (see Validation below): this fetch works with a
plain `curl`/`requests` GET, no authentication, from a GitHub Actions
runner.

### B. Cloud data collection

- **Trigger**: GitHub Actions `schedule` cron, 3 entries per trading day —
  market open (~9:35am ET), midday (~12:30pm ET), market close (~3:55pm
  ET) — converted to UTC. Like the Stocks project's weekly job, this
  accepts the DST-driven few-minutes-of-drift a fixed UTC cron implies
  rather than maintaining separate summer/winter schedules, since a few
  minutes either side of open/mid/close doesn't materially change the
  snapshot's value. Also exposes `workflow_dispatch` for manual runs.
- **Runner**: `ubuntu-latest`. **Empirically confirmed no special
  SSL/proxy workaround is needed** — unlike the local machine (Norton TLS
  inspection, needs `truststore` + a `CURL_CA_BUNDLE` export) or the
  Claude Code cloud sandbox (restrictive egress proxy, needs
  `YF_DISABLE_CURL_CFFI=1`), GitHub's hosted runners have neither problem;
  yfinance's default `curl_cffi` backend works immediately (see
  Validation).
- **Script** (self-contained, no imports from the rest of this repo,
  matching `cloud/daytrade_shortlist.py`'s convention since GitHub Actions
  clones fresh every run with no other persistent state):
  1. Fetch the ledger CSV (source A), extract the `symbol` column.
  2. For each symbol, fetch its options chain via `yfinance` — all
     expirations within ~75 days of today (covers the playbook's 30-60 DTE
     entry window plus Chen/Sebastian's term-structure evaluation, which
     needs multiple expirations to compare).
  3. Flatten calls + puts across all fetched expirations into one table
     per symbol: `symbol, expiration, contractSymbol, strike, type
     (call/put), lastPrice, bid, ask, volume, openInterest,
     impliedVolatility, inTheMoney, lastTradeDate`.
  4. Write one CSV per run:
     `data/github_sync/options_snapshots/{date}_{session}.csv` (session ∈
     {open, mid, close}).
  5. Commit and push, matching `weekly-price-fetch.yml`'s
     `git add` / conditional-commit / `git push` pattern (skip the commit
     if nothing changed, e.g., a holiday with no trading).
- **Rate limiting**: pace requests (~1-2s between symbols, matching the
  spike's working cadence) and treat a `YFRateLimitError` on any individual
  symbol as a skip-and-continue, not a job failure — log which symbols
  were skipped in the run's output so gaps are visible, rather than
  aborting the whole snapshot over one symbol.

### C. Local nightly merge + compute

Runs on the user's own PC, whenever it's next on overnight (Irish time) —
not scheduled via GitHub Actions or a cloud routine. Mirrors the Stocks
project's local-pipeline-picks-up-cloud-output pattern
(`pull_github_updates.py` equivalent).

1. `git pull` to get the day's raw snapshots.
2. Read every `options_snapshots/{today}_*.csv` not yet merged (track via
   a local `fetch_log`-style table, matching Stocks' `db.py` convention).
3. Upsert into `data/db/options.db` (SQLite, gitignored — regenerable from
   the published snapshots, same reasoning as Stocks' `stocks.db`).
4. Compute Greeks for every contract using the Black-Scholes formulas
   documented in `.claude/skills/options-playbook/references/greeks-and-volatility.md`
   — inputs: underlying price (fetched alongside the chain, or via a
   separate lightweight price call), strike, days to expiration, Yahoo's
   own `impliedVolatility`, and a risk-free rate (a fixed reasonable
   constant, e.g., 4-5%, refreshed periodically — see Open Questions).
5. Compute liquidity flags (e.g., minimum volume/open-interest thresholds,
   flagging contracts whose IV is likely unreliable per the data-quality
   issues found in the exploration spike — near-zero bid/ask, zero open
   interest).
6. Compute IV/skew reads: today's ATM IV vs. the underlying's own rolling
   IV history (this improves as the archive accumulates), and a basic
   skew read (OTM put IV vs. OTM call IV vs. ATM IV) per Chen/Sebastian's
   skew framework in the playbook.
7. Write the compiled signals export:
   `data/github_sync/signals/{date}.csv` — one row per contract that
   passed the liquidity filter, with strike, expiration, type, price,
   Greeks, IV, skew reads, and volume/OI.
8. Commit and push.

### D. Overnight cloud routine (~2:30am)

A **Claude Code scheduled routine** (via `/schedule` / `RemoteTrigger` —
the same mechanism the day-trade shortlist and chocolate-digest routines
already use), not a GitHub Actions workflow, since this step requires
judgment (applying the playbook's rules, composing an email) rather than
pure mechanical computation.

1. Read the latest `data/github_sync/signals/{date}.csv` from this repo.
2. **Staleness check**: if today's signals file is missing, or its date is
   older than the most recent trading day, draft an alert email instead of
   proceeding — mirroring the day-trade cloud routine's explicit
   fail-loud-not-silent behavior for exactly this situation (step C not
   having run is the direct analog of the day-trade routine's "weekly job
   missed its run").
3. Invoke the `options-playbook` skill and apply its entry/risk criteria
   to the signals data to generate concrete trade candidates (sub-project
   3's actual scope — this spec only requires that step D exists as the
   consumer of this pipeline's output; the selection logic itself is
   designed in sub-project 3).
4. Draft (not send) a Gmail email listing the day's suggested trades.
5. Append the new recommendations to the options recommendation ledger
   (below) and commit + push.

### E. Options recommendation ledger

`data/github_sync/options_ledger/options_recommendation_ledger.csv` —
wide-format CSV, mirroring `stock_price_ledger.csv`'s pattern of
accumulating one set of columns per calendar date, extended for options'
multi-leg nature:

| Column | Purpose |
|---|---|
| `symbol` | Underlying ticker |
| `company_name` | For filtering, same as the stock ledger |
| `trade_id` | Groups every leg of one recommendation together (e.g. all legs of one iron condor share a `trade_id`) |
| `strategy` | e.g. "vertical put credit spread", "iron condor" |
| `leg_role` | e.g. "short put", "long put", "short call", "long call" |
| `rec:YYYY-MM-DD` | On a day this leg is (re)recommended: `contractSymbol/lastPrice`. Blank otherwise. |
| `tgt:YYYY-MM-DD` | Same date, paired with the column above: `targetPrice/stopLossPrice`. Blank otherwise. |

One row per leg. A 2-leg vertical spread recommendation produces 2 rows
sharing one `trade_id`; a 4-leg iron condor produces 4. `contractSymbol`
is the standard OCC symbol (encodes underlying, expiration, type, and
strike already, e.g. `AAPL260828C00310000`), so no separate
strike/expiration columns are needed — mirroring exactly how the user
specified this format. A new `rec:`/`tgt:` column pair is added for every
calendar date going forward, exactly as the stock ledger adds one new date
column per day — this file will grow wide over time by design, matching
the existing precedent.

## Validation (empirical, this session)

A disposable test workflow was run against the newly created
`coop1st/options-trading-pipeline` repo (public) to check feasibility
before committing to this design, then deleted:

- **yfinance options-chain fetch, default backend**: works immediately on
  `ubuntu-latest` — no SSL errors, no rate limiting observed for a single
  symbol. AAPL returned 47 calls / 38 puts with the expected columns.
- **`YF_DISABLE_CURL_CFFI=1` fallback**: also works, confirming a fallback
  path exists if the default backend ever becomes unreliable on Actions
  runners, but it is **not needed** by default.
- **Reading the Stocks ledger via `raw.githubusercontent.com`**: works
  with a plain unauthenticated `curl`, confirmed against the live,
  currently-112-row ledger.

Separately (local machine, this session): a full 25-ticker options-chain
pull via yfinance required the same `truststore` + `CURL_CA_BUNDLE`
Norton-TLS-inspection fix already used in `Projects/Stocks/pipeline/config.py`,
plus clearing a stale `cookies.db` crumb cache once, before succeeding
cleanly at a ~2s/ticker pace. This fix should be included in the *local*
merge script (component C) defensively, matching Stocks' precedent, even
though it is confirmed unnecessary for the *cloud* fetch script (component
B).

## Cost estimate

At the current watchlist size (~112 symbols) and 3 snapshots/day:

- **GitHub Actions minutes**: ~3-5 minutes/run × 3 runs/day × ~22 trading
  days/month ≈ 200-330 minutes/month. The repo is public, so **Actions
  minutes are free and unlimited** on standard GitHub-hosted runners
  regardless of this estimate.
- **Storage**: each snapshot run's raw CSV is on the order of a few MB
  across ~112 symbols' full option chains; three snapshots/day over a
  full year is roughly 1-2GB uncompressed before git's own delta
  compression on repetitive text data, well under GitHub's soft
  guidance (warnings start around 5GB) and far from any hard limit.
- **The judgment step (component D)** runs as a Claude Code cloud routine,
  not a GitHub Actions job — its cost is whatever the user's existing
  Claude Code cloud-routine usage already covers (the same infrastructure
  the day-trade and chocolate-digest routines already run on), not a
  GitHub cost at all.

**Conclusion: this fits entirely inside GitHub's free tier at the current
scale.** Re-check if the watchlist grows into the hundreds of symbols or
the snapshot depth increases substantially (e.g., capturing far more than
~75 days of expirations).

## Error handling

- **Component B** (cloud fetch): a rate-limited or failed individual
  symbol is skipped and logged, not a job failure. A wholesale failure
  (e.g., the ledger fetch itself fails) does fail the job, since there's
  nothing useful to snapshot without a symbol list.
- **Component C** (local merge): matches Stocks' `run_stage_safely()`
  isolation convention — a failure computing one derived signal (e.g., a
  malformed IV producing a bad Greek) shouldn't prevent the rest of that
  day's contracts from being processed and published.
- **Component D** (cloud routine): stateless between runs, same as the
  day-trade routine — no local checkpoint to coordinate with. The
  staleness check (see above) is the safety net for "component C didn't
  run last night."

## Open questions

- **Risk-free rate source**: a fixed constant is proposed for now (see
  component C step 4); whether to instead fetch a live short-term
  Treasury rate periodically is deferred to the implementation plan, since
  the playbook's own examples show the impact on Greeks is small (Ch.4 of
  Bittman's book: raising rates from 3% to 5% moved a 90-day ATM call by
  only ~0.24) and not worth over-engineering now.
- **Underlying price source for Greeks**: whether to fetch it via a
  separate lightweight call per symbol during the cloud fetch (component
  B) or during the local merge (component C) is an implementation-time
  decision, not a design one — either works, and the choice should follow
  whichever has the lower rate-limit footprint once the actual fetch code
  is written.
