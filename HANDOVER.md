# Handover — pick this up from here

Last updated 2026-10-17 (afternoon). The 2026-10-17 and 2026-10-15 sections just
below are the newest (read 2026-10-17 first). Everything after them is the 2026-09-05
build handover and is still accurate, apart from the corrections noted in those sections.

## Session 2026-10-17 (afternoon): daily status reminder routine (NEW)

**Why:** the user often misses the window for having the PC on, so the 02:30 email falls back to the staleness alert.
They asked for a daily email with a quick status report on the project, plus automatic deletion of these status
drafts once they are more than 5 days old.

**What was built** (cloud routine only, with no repo code changes):
- **Routine:** `trig_01VBvPrZuubm8yYaXhywrzgz` "Options status check (daily)".
  - Cron `0 17 * * 1-5` UTC: 18:00 Dublin until 25 Oct, then 17:00 Dublin.
  - Model Sonnet 5.5, repo coop1st/options-trading-pipeline.
  - Tools: Bash, Read, Glob, Grep, plus Gmail list_drafts, create_draft and delete_draft.
  - Read-only on the repo. It never sends.
  - Link: https://claude.ai/code/routines/trig_01VBvPrZuubm8yYaXhywrzgz
- **Draft:** subject "Options status -- YYYY-MM-DD", to kcoopercscs@gmail.com. Contents:
  - the verdict line: "ACTION TONIGHT ...", prefixed with "BEHIND by N trading day(s)" if any trading day has a
    `_close` snapshot newer than the newest signals file;
  - the signals and ledger dates (it flags a ledger that lags the signals, meaning `screen_trades.py` was not run);
  - today's snapshots;
  - the close landing window, taken from `git log` of the last 5 `*_close.csv` files;
  - whether the last options draft was real or an alert;
  - the two commands.
- **Cleanup:** runs before drafting. It deletes only drafts whose subject starts with "Options status --" and whose
  date is more than 5 days ago, and never any other draft.
- **Prompt backup:** `routine_backups/options_status_email_prompt_2026-10-17.txt`. This folder is untracked; it is
  local only.

**Test run** (fired by hand on Sat 17 Oct at 13:46 UTC): correct output.
- It saw that it was Saturday, so there was nothing to do; it was caught up through 16 Oct; 15 Oct was lost.
- It found that the 01:33 draft was an alert and the 10:43 draft was real (20 candidates).
- It deleted 0 drafts. The first real deletion is expected around Fri 23 Oct, so check then that only old status
  drafts went.

**Timing correction:**
- The close snapshot measured from git landed between 23:25 and 00:40 Dublin, with one outlier at 02:50.
- That is not the "~21:15" the master schedule used to say. A run at 21:15 would have scored the mid snapshot.
- The master schedule rows (CSV and Google Sheet) were corrected on 17 Oct and the new routine was added on Mon-Fri at
  18:00. The Sheet was verified with 0 mismatches.

**To check next week:**
1. Mon 19 Oct about 17:00 UTC: the first scheduled run should say "ACTION TONIGHT" with no backlog.
2. Around Fri 23 Oct: the cleanup deletes the Sat 17 Oct test draft and nothing else.
3. After the clocks change on 25 Oct, the draft arrives at 17:00 Dublin. Move the cron to `0 18 * * 1-5` only if the
   user wants 18:00 kept.

## Session 2026-10-17: staleness alert again, plus four builder fixes (READ FIRST)

### 1. The alert
The 01:33 "Options signals -- automation alert" (17 Oct) had the same cause as on 15 Oct: the two local
scripts had not run since 14 Oct, while the cloud fetch was healthy. Catch-up:
- `merge_and_score.py` wrote `signals/2026-10-16.csv` (11,962 rows; commit `e7f46dc`).
- `screen_trades.py` ran, and the routine `trig_019GMK964MKrAunz5KZiZv8x` was fired by hand.
- 15 Oct has no signals file, so its candidates are lost (the scorer only scores the newest date).

### 2. Four bugs found in that draft, all fixed with the user's approval
The fix is commit `2122866`; there are no other code changes.

| # | Bug | Evidence | Fix | File |
|---|---|---|---|---|
| 1 | Iron condor `width = min(call wing, put wing)`, so max loss came from the **narrower** wing. The true max loss is the wider wing minus the credit, because only one side can finish in the money. | 26 ledger condors have uneven wings. 17 Sep ^SPX-1 had a 2,600-pt put wing (gaps in the strike chain) and was sized at 5 contracts on a stated $364 risk; the real risk is about $255k per contract. | `width = max(call_width, put_width)` | `pipeline/strategy_rules.py` `build_iron_condors` |
| 2 | Builders grouped by symbol + expiration only. ^SPX lists AM-settled **SPX** and PM-settled **SPXW** on the same third-Friday dates, so one trade could mix them. | 8 ledger trades (condors and short calendars); 16 Oct #1 had SPXW shorts and SPX longs. | New `_by_series(signals)` groups by symbol + option root (regex on `contract_symbol`). It is used by the vertical, condor, calendar and double-diagonal builders. The vertical's volume gate still sums the whole symbol. Directional longs are single-leg and unchanged. ^VIX/VIXW was already excluded from screening. | `strategy_rules.py` |
| 3 | No check for impossible credits. A stale `last_price` let a spread "collect" at least its width, so max loss went negative and the size came out as 0, yet it still ranked #1. | 16 Oct #1: the 6990 put's last trade was $45.07 against $51.40/$54.70 bid/ask (volume 12), so the 7000/6990 put spread showed a $10.05 credit on 10 wide. At bid/ask it is a $0.70 debit. | Verticals reject `credit >= width`. Condors reject either side whose own credit is at least its own width. **Stop-gap**: bid/ask pricing is the real fix. | `strategy_rules.py` |
| 4 | Trades sized to 0 contracts still took top-20 slots. | 24 of 104 ledger trades: mostly ^SPX short calendars and condors whose one-contract max loss is above 2% of `ACCOUNT_EQUITY` ($2,000). The sizing itself was correct. | `score_and_rank` skips any candidate where `suggested_contracts(c) <= 0`, before the top-N slice. | `pipeline/screen_trades.py` |

**Tests:**
- New `pipeline/verify_strategy_rules.py` has 13 checks. Run it with `python pipeline/verify_strategy_rules.py`; it prints `ALL OK`.
- All 9 fix checks were watched failing before the change.
- The existing `verify_scoring`, `verify_track_outcomes`, `verify_greeks`, `verify_compare_strategies` and `verify_generate_tuning_stats` all still print `ALL_OK`.

### 3. What changed in the published output
**The 16 Oct ledger was regenerated** (commit `6d9e67d`). A re-run replaces that date's rows by design.
- Gone:
  - the impossible ^SPX condor (old #1);
  - the ^SPX condor with 25/100 wings (old #14), whose true risk is above the 2% limit.
- UVXY condor: 28 → 3 contracts (its 8-pt wing now sets the risk, not the 3-pt one).
- New in the top 20: NRG short calendar (#19) and ABR long calendar (#20).
- All 20 trades are sized at 2 contracts or more, and none mixes roots.

**The email:** the old "Options recommendations -- 2026-10-16" draft was deleted and the routine re-fired. The corrected
draft was created at 10:43Z on 17 Oct.

**Ledger rows dated before 16 Oct were NOT rewritten.** They keep their old sizes and mixed roots. Before any
analysis of past outcomes or position sizes, remember that pre-16-Oct condors with uneven wings were
oversized and that 8 trades mixed SPX and SPXW.

### 4. Known limits still open (not fixed; revisit with the bid/ask task)
- **Wing-distance cap: the user chose "leave for now".** A gap in the strike chain can still pick a very far long wing.
  Fix 1 now gives such a trade its true (huge) risk, so it sizes to 0 and fix 4 drops it.
- **The calendar and double-diagonal max loss is `abs(net debit)`.** That's right for a long calendar but understates risk for a
  double diagonal (offset strikes) and for a short calendar (e.g. 16 Oct NRG #19). These are noted, not raised with
  the user as a task.
- The condor/diagonal long-wing target is a fixed 10 strike points, whatever the underlying's price.
- Everything still prices on `last_price`. **Bid/ask pricing remains the agreed next task** (user requirement), and
  removes the cause of bug 3.

### 5. Next
- **Mon 19 Oct evening, with the PC on:** after the "Options snapshot: close 2026-10-19" commit lands (often after
  23:00 Irish time), run `merge_and_score.py` then `screen_trades.py`. The routine fires Tue 20 Oct at about 01:34 UTC
  (`next_run_at` 2026-10-20T01:34Z). If the scripts are skipped, the newest file is still Fri 16 Oct, 3 days older than
  Mon 19 Oct, so the email will be the staleness alert again.
- Then start the bid/ask pricing task, and fold in the open limits from section 4.

## Latest session — 2026-10-15 (health check + VIX hedge fix)

**Why the session happened:** the user said the nightly email "didn't
have any info in it". The emails from 10–15 Oct were the routine's
**staleness alert** (subject "Options signals -- automation alert"), not
a broken recommendations email. The cloud snapshot fetch was healthy the
whole time, with open/mid/close committed through 14 Oct. The two
**local** steps had last run on 9 Oct, so no newer signals file existed
and the routine stopped at its staleness check, as it is designed to.

**What was done:**
1. Ran `python pipeline/merge_and_score.py`, which merged 9 new snapshot
   files and published `signals/2026-10-14.csv` (11,073 contracts).
2. Ran `python pipeline/screen_trades.py`, which wrote 8 candidates
   dated 2026-10-14 to the ledger: STM/VFC/DECK calendars and
   SPY/^SPX/TFC iron condors.
3. Fired the nightly routine by hand (`trig_019GMK964MKrAunz5KZiZv8x`).
   That produced a full "Options recommendations -- 2026-10-14" draft.
4. **Fixed the VIX put bug** (commit `9d8ba3a`). The tail-hedge reminder
   only ever looked for **puts**, including on ^VIX/VXX/UVXY, so the
   "volatility spike" example could be a VIX put, which profits when
   volatility *falls*. Chen/Sebastian ch.3 names OTM S&P **puts** and OTM
   VIX **calls**. The fix had two parts:
   - `pipeline/config.py`: new `TAIL_HEDGE_OPTION_TYPE` setting
     (equity downside → put, volatility spike → call). `screen_trades.py`
     `_cheapest_unit` now takes the option type. Calls on VXX/UVXY are
     this project's own extension of the VIX-call rule and are flagged in
     the code as such.
   - Step 5 of the nightly routine's prompt was rewritten to check SPX/SPY
     puts and VIX/VXX/UVXY calls separately, with one example per hedge
     type (or a plain "none"). Before this, the prompt had the same
     puts-only bug, and the prompt is the version that reaches the email.
     Verified against the 14 Oct signals: the volatility example is now
     `VIX261021C00055000` @ $0.01.

**Decisions made by the user this session (don't re-raise):**
- The cheapest qualifying hedge can be nearly worthless (for example an
  SPX put expiring the next day, because there is no minimum
  days-to-expiry). The user said **"this is fine"**. Leave it alone.
- The two local steps stay manual, with no cloud migration and no Windows
  scheduled task (decided 2026-09-17). Help by telling the user when the
  PC needs to be on, and by running the scripts whenever the ledger is
  behind the snapshots.

**Daily operating rule for the user:** on each US trading-day evening,
with the PC on, run `merge_and_score.py` then `screen_trades.py`
*after* that day's close snapshot has landed in the repo and *before*
the routine fires at 01:30 UTC (~02:30 Irish). GitHub crons on this
account start hours late, so the close snapshot often lands around
23:00 UTC or later. Check `git log` for "Options snapshot: close
<date>" before running. If it's skipped, the next email is the
staleness alert again.

**Things to know:**
- `merge_and_score.py` scores only the **most recent** snapshot date.
  Missed days get no signals file of their own (12 and 13 Oct have none,
  and neither do the earlier gaps). `track_outcomes.py` just skips
  missing days, so nothing breaks, but those days' candidates are lost.
- Earlier fix (2026-10-12, commit `d973459`): snapshot and true-range
  files are now dated by the America/New_York market day, not the
  runner's UTC date. Late-starting evening crons had been overwriting
  the next day's file, which lost the closes for 5 and 8 Oct.
- To check the routine's health, read the draft's content, not just the
  run status. An alert-only run still reports success.

**Outcome-tracking bug found the same evening (commit `bbc65cd`):**
`evaluate_trade` replayed *every* signals file, including files from
before the trade's entry date, so trades resolved on prices from weeks
before they were recommended. 23 recorded outcomes were dated on or
before entry. It now takes `entry_date` and skips snapshots up to and
including it; `generate_tuning_stats.py`'s sweep passes it too.
Regression checks were added, and all 5 verify scripts pass.

**Ledger reset and re-score (done, with the user's OK):** the tracker
never re-checks terminal trades, so the outcome columns
(`outcome_status`, `outcome_date`, `realized_pct`) were cleared for
all 236 ledger rows. A check confirmed no other column changed. Then
`track_outcomes.py` re-scored all 84 trades (commit `5cfc835`), and
`compare_strategies.py` rebuilt `strategy_performance_report.csv`
(`7cbe8f1`). The pre-reset values are in git history if ever needed.
`tuning_suggestions_2026-10.md` was **not** affected because it had 0
terminal trades. That review did note that `generate-tuning-stats.yml`'s
monthly cron didn't fire on 1 Oct, which is still unchecked.

**Corrected results as of 2026-10-15** (simulated; percentages are of
each trade's own credit/debit): 84 trades, 35 terminal, 46 open, 3
unresolved at expiration.

| Family | Closed | Wins | Avg realized |
|---|---|---|---|
| Iron condor | 7 | 7 | +67% (about +49% without the bad-data +177% trade) |
| Short calendar | 27 | 20 | −30% (about +12%, 20/26, without the −1,122% trade) |
| Long calendar | 1 | 0 | −77% |

By label: `rich_iv+directional_confirmation` won 15/17;
`directional_confirmation` alone won 5/10. It's early, since most trades
closed in the last two weeks.

### Requirement from the user: use the bid/ask spread

The user stated **"we need the bid ask spread"**. Pricing must be based
on bid/ask, not `last_price`. This is the agreed next piece of work (not
started):

- **Why:** measured on the 2, 9 and 14 Oct signals, about 85% of
  contracts have a real bid and ask, but `last_price` falls **outside**
  the bid/ask in 31–39% of contracts, and about 20% hadn't traded that
  day. The +177% condor (`2026-10-02-^SPX-15`) is the proof: on 14 Oct
  the 7225 long put's `last_price` (32.30) was above the 7235 short put's
  (29.91), which is impossible, while their quotes were sensible
  (31.40/32.50 vs 32.00/33.30, mids about 31.95 vs 32.65).
- **What to build:**
  1. Value legs at the bid/ask **mid** (or at natural prices: sell at
     bid, buy at ask) in `track_outcomes.py`, and at entry in
     `screen_trades.py` (the ledger's `rec:` cells currently store
     `last_price`).
  2. Skip, or mark as unpriceable, any leg with `bid <= 0` or no ask
     (the existing `zero_bid` flag), instead of using a stale last.
  3. Consider the spread itself as a quality gate/cost: `wide_spread`
     is already flagged in `signals.csv`, and `liquidity` is a scoring
     criterion.
  4. Separately, add a minimum gap between calendar expiries. The
     −1,122% `2026-09-30-^SPX-7` had expiries one day apart (12/13 Oct)
     with a $0.50 credit.
  5. After the change, reset and re-score the ledger again, the same way
     as above.
- The current yfinance snapshots **already include bid and ask** (the
  `bid`/`ask` columns in the snapshots and signals), so this needs no
  new data source.
- Follow `options-trading-spec-rigor`: say plainly that the mid-vs-natural
  choice is this project's own operationalization, not a book rule.

### Data-source research (2026-10-15): decision deferred

The user asked whether to buy a data subscription. The recommendation:
don't pay yet. Do the bid/ask change above first, measure what noise is
left, then decide. The user's general rule is not to pay for data APIs
(memory `prefer-scraping-over-paid-apis`); they raised paying themselves
this time, but nothing has been bought.

**Tradier (best fit if we switch), checked against Tradier's own docs:**
- **Live data requires a real Tradier brokerage account.** Their Market
  Data page: "Real-time data is available to all Tradier Brokerage
  account holders for US-based stocks and options. If you are not a
  Tradier Brokerage account holder, we are unable to provide you with
  any real-time data solution."
- Brokerage API: stocks, options and indices live (NDX, RUT and COMP are
  calculated values); Greeks updated **hourly** (from ORATS). Sandbox:
  15-minute delayed stocks and options, no indices, no Greeks.
- **Ireland is on Tradier's permitted-countries list**, so the user (an
  Ireland resident) can open an account. The UK is blocked; Ireland is
  not.
- Fields include bid/ask with sizes, exchanges and timestamps (`bid_date`,
  `ask_date`), open interest, and `bid_iv`/`mid_iv`/`ask_iv`/`smv_vol`.
  The chain lookup includes extra roots (SPXW, RUTW).
- Limits: market data is 120 requests/minute in production. The chains
  endpoint takes one symbol plus one expiration per call. The 14 Oct
  close snapshot was 296 symbols / 990 symbol-expiration pairs, so about
  1,300 calls, about 11 minutes per snapshot. That's fine on Actions.
- Missing: **no history for expired options** (daily candles only for
  live contracts; fine, since we keep our own snapshots); intraday
  history is short (tick 5 days, 1-minute 10–20 days); no mutual funds.
- Cost: plans are Lite (free), Pro ($10/month) and Pro Plus ($35/month);
  those are trading-commission tiers. Nothing found says live API data
  costs extra.
- **Unconfirmed, ask Tradier support before signing up:** whether Lite
  gets live API data; any minimum deposit or funding requirement; whether
  production access tokens expire (this matters for unattended cloud
  runs).
- Switching means rewriting `cloud/fetch_options_snapshot.py` (about a
  day) and storing the token as a GitHub Actions secret.

**Other options, from third-party sources (verify before buying):**
- Schwab Trader API: free with a Schwab account (price not published).
  Needs an approved developer app, and its tokens expire regularly, which
  is awkward for the cloud.
- Interactive Brokers: OPRA live options data about $1.50/month for
  non-professionals, waived at $20/month in commissions. It needs
  IBKR's software running locally, so it's a poor fit for cloud jobs.
- Massive (formerly Polygon): free end-of-day tier; Options Starter
  $29/month (15-minute delayed, 2 years of history).
- ThetaData: from about $40/month (sources disagree); more than needed
  now.

**Open items:**
1. Bid/ask-based pricing plus a minimum calendar expiry gap (above), then
   re-score.
2. Check why `generate-tuning-stats.yml` didn't fire on 1 Oct.
3. `ACCOUNT_EQUITY` is still the `100000` placeholder.
4. The older "What's next" list below still applies.

---

*Below: the 2026-09-05 build handover.* Everything referenced is
committed and pushed to `master` at
https://github.com/coop1st/options-trading-pipeline (public repo). Read
this file first, then the specs/plans it points to.

**All five planned sub-projects are built and live.** Sub-project 5
(monthly adaptive-tuning suggestions) shipped its full implementation
this session — see its section below and
`docs/superpowers/specs/2026-09-05-adaptive-tuning-design.md` /
`docs/superpowers/plans/2026-09-05-adaptive-tuning.md` (7 tasks, all
complete).

**Two things shipped immediately as sub-project 5's prerequisites, ahead
of its own implementation plan** (same "don't lose history waiting"
principle sub-project 4 established for score-breakdown persistence):

1. **Bug fix**: `build_iron_condors`/`build_calendars`/`build_double_diagonals`
   hardcoded `"tilt": None` and never received the real bias signal, so
   `scoring.py`'s `directional_alignment` criterion was a constant
   `100.0` for these three families regardless of the real market tilt —
   contradicting sub-project 3's own approved spec. Fixed; verified both
   synthetically and against real data.
2. **`selection_label`**: a new ledger column, assigned at recommendation
   time, naming which of the 4 "thesis" criteria (`iv_richness`,
   `skew_quality`, `term_structure`, `directional_alignment`) scored
   meaningfully above neutral for that candidate — e.g. `"rich_iv+rich_skew"`,
   directly matching the books' own "richest setups combine high skew
   and high ATM IV." `compare_strategies.py` now also reports win
   rate/avg realized P&L **by label**, alongside its existing by-family
   and by-criterion views.

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

**Sub-project 5 (Adaptive Tuning Suggestions) — complete, verified live.**
Spec at `docs/superpowers/specs/2026-09-05-adaptive-tuning-design.md`,
implementation plan at `docs/superpowers/plans/2026-09-05-adaptive-tuning.md`
(7 tasks, all complete, executed inline). Built on a three-tier parameter
classification that is the whole system's protective boundary:

- **Tier 1** (book-verbatim thresholds, e.g. the condor's 55%/30-DTE/
  10-15Δ) — never touchable, never suggested.
- **Tier 2** (this project's own flagged implementation guesses) — split
  into entry-side (DTE windows, delta bands, spread widths in
  `strategy_rules.py`'s builders — **not swept in v1**, would require
  reconstructing hypothetical candidates from raw historical chains, a
  materially harder capability that doesn't exist) and exit-side (only
  `DIRECTIONAL_STOP_PCT`/`DIRECTIONAL_TARGET_PCT` in `track_outcomes.py`'s
  directional-long evaluator — the only Tier-2 pair actually swept).
- **Tier 3** (composite score's 7 criteria weights, currently equal) —
  eligible for sensitivity analysis, never auto-applied.

What's live:

- **`pipeline/generate_tuning_stats.py`** (monthly,
  `.github/workflows/generate-tuning-stats.yml`, cron 1st of month
  21:00 UTC, cloud-only, no external fetch): computes Spearman
  correlations between each of the 7 scoring criteria and `realized_pct`,
  a weight-sensitivity check (doubling/halving each criterion's weight
  and comparing correlation against the equal-weight baseline), a
  counterfactual sweep of `DIRECTIONAL_STOP_PCT_GRID` ×
  `DIRECTIONAL_TARGET_PCT_GRID` against already-resolved directional
  trades' real price paths (via `track_outcomes.py`'s own evaluator, reused
  through a new `evaluator_overrides` parameter), and label-performance
  aggregation — publishing raw, mechanical
  `data/github_sync/options_ledger/tuning_stats_latest.json`. Never
  authors a suggestion itself. Requires `MIN_TRADES_FOR_TUNING_SUGGESTION
  = 10` scoreable trades before the exit-side sweep even runs.
- **`selection_label`**: assigned at recommendation time in
  `screen_trades.py` via `scoring.py`'s `compute_selection_label()`,
  naming which of the 4 "thesis" criteria (`iv_richness`, `skew_quality`,
  `term_structure`, `directional_alignment`) scored ≥65
  (`LABEL_THESIS_THRESHOLD`) — e.g. `"rich_iv+rich_skew"`, or
  `"no_dominant_thesis"` if none did. `compare_strategies.py` reports win
  rate/avg realized P&L by label alongside its by-family/by-criterion
  views, feeding label-filtering suggestions.
- **New monthly cloud routine**, "Monthly tuning review", `RemoteTrigger`
  id `trig_01LRt3LyVSeyNCk2mqG4aQF3`, cron `30 21 1 * *` (1st of month,
  21:30 UTC, after `generate-tuning-stats.yml`'s 21:00 UTC run). Reads
  `tuning_stats_latest.json`, applies the three hard safety rules (never
  suggest a Tier-1 change, never edit `config.py`/`scoring.py` directly —
  always propose via a committed markdown file, never present
  sub-evidence-bar findings as suggestions), writes and commits
  `data/github_sync/options_ledger/tuning_suggestions_{YYYY-MM}.md`, and
  drafts (never sends) a Gmail summary. Verified live on first manual
  trigger: correctly reported 0 terminal trades and "nothing to suggest
  this month" rather than fabricating a conclusion — committed as
  `9fb55f5`, file and draft both accurate.
- **Propose-never-auto-apply policy**, mirroring the Stocks project's
  "Pick Tuning Review" precedent: suggestions only ever land as a
  reviewable file + email, never as a direct code edit.

**Two real pre-existing bugs found and fixed during sub-project 5's
design/pre-work, both worth knowing about**:
1. **`build_iron_condors`/`build_calendars`/`build_double_diagonals`**
   hardcoded `"tilt": None` and never received the real bias signal, so
   `directional_alignment` was a constant `100.0` for these 3 families —
   contradicting sub-project 3's own approved spec. Fixed by threading
   `bias` through all three builders; verified synthetically and against
   real data.
2. **Sign-convention bug caught during spec self-review** (before any
   code was written): a single `cost_to_close_now` formula was being
   applied to both credit and debit structures, producing backwards
   numbers for debit structures. Split into `credit_received`/
   `cost_to_close_now` (credit) vs. `debit_paid`/`current_value_now`
   (debit); also caught short calendar being misclassified as debit when
   it's actually credit (buys cheap front, sells pricier back).

## What's next

- **All five sub-projects are now built and live — no implementation
  work outstanding.** The system runs itself monthly/weekly/daily; the
  only remaining "next steps" are data accumulation, not code:
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
- `docs/superpowers/specs/` — 5 design specs (playbook, pipeline,
  strategy engine, strategy comparison, adaptive tuning), all with
  implementation plans fully executed
- `docs/superpowers/plans/` — 5 implementation plans, all fully executed
- `pipeline/` — local/cloud-shared pipeline code: `config.py`, `db.py`,
  `greeks.py`, `merge_and_score.py`, `atr.py`, `directional_bias.py`,
  `strategy_rules.py`, `scoring.py`, `screen_trades.py`,
  `track_outcomes.py`, `compare_strategies.py`, `generate_tuning_stats.py`,
  plus `verify_greeks.py`/`verify_scoring.py`/`verify_track_outcomes.py`/
  `verify_compare_strategies.py`/`verify_generate_tuning_stats.py`
- `cloud/` — GitHub-Actions-runnable scripts: `fetch_options_snapshot.py`,
  `fetch_daily_true_range.py`
- `data/db/options.db` — gitignored SQLite DB, regenerable from published
  snapshots
- `data/github_sync/` — published pipeline data: `options_snapshots/`,
  `signals/`, `daily_true_range/`, `options_ledger/` (recommendation
  ledger, `strategy_performance_report.csv`, `tuning_stats_latest.json`,
  `tuning_suggestions_{YYYY-MM}.md`)
