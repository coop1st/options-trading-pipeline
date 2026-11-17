# Handover: cloud scoring and bid/ask midpoint pricing (Mon 16 Nov 2026)

**To pick up tomorrow (Tue 17 Nov):** start at "First thing tomorrow" below. Everything else is background.

The full detail of each change is in `HANDOVER.md`, section "Session 2026-11-16". This file is the short version plus the list of what to do next.

## Where things stand in one paragraph

The options project no longer needs the PC. GitHub scores every trading day and builds the recommendations by itself, straight after each snapshot. Every price in the system is now the midpoint between the bid and the ask, taken from the snapshot captured closest to the market close. All 57 past days were re-scored that way and all 255 trades in the ledger were replayed. Nothing has yet run through a full night unattended, and one new job has never run at all. Those are the first things to check.

## First thing tomorrow

Do these in order. Each one says what "good" looks like.

1. **Did the nightly email arrive as real recommendations?**
   - Look in Gmail drafts for "Options recommendations -- 2026-11-16", created at about 03:30 Dublin on Tue 17 Nov.
   - Good: 20 trades, each leg showing a midpoint price plus its bid and ask, and the line "Prices are bid/ask midpoints; a real order may fill worse than the midpoint."
   - Bad: a draft titled "Options signals -- automation alert", or no draft. Then check the routine's last run (id below).
2. **Did the new last-hour snapshot job work?** This is the untested piece.
   - After about 21:15 Dublin on Tue 17 Nov, look for `data/github_sync/options_snapshots/2026-11-17_preclose.csv` and `data/github_sync/snapshot_times/2026-11-17_preclose.txt` in the repo.
   - Check the runs: `gh run list --repo coop1st/options-trading-pipeline --workflow options-preclose-fetch.yml --limit 30`
   - Good: many runs that finished in a few seconds, and exactly one that took about 15 minutes and committed "Options snapshot: preclose 2026-11-17".
   - Bad: no run landed between 15:00 and 15:50 New York (20:00 to 20:50 Dublin). Then the schedule needs widening or a different trigger. The day still gets scored from the next-best snapshot, so nothing is lost.
3. **Did Tuesday get scored and screened without anyone touching it?**
   - `gh run list --repo coop1st/options-trading-pipeline --workflow score-and-screen.yml --limit 10`
   - Good: a successful run after the 17 Nov close snapshot, a new `data/github_sync/signals/2026-11-17.csv`, and a `rec:2026-11-17` column in the ledger.
   - In that run's log, the "Scoring ..." line says which snapshot was used and when it was captured. Good is the `preclose` one, captured about 15:00 to 16:00 New York.
4. **Did the 17:00 status email change its wording?**
   - Draft "Options status -- 2026-11-17". Good: first line is "ALL GOOD: nothing for you to do." or "PROBLEM: ...". It should no longer say "turn the PC on".
5. **Did GitHub's schedule recover?** On 16 Nov none of the three scheduled snapshot fetches had started by 22:00 Dublin (over eight hours late), so the close snapshot was started by hand at 17:03 New York. If the late scheduled fetches ran afterwards they will have added `2026-11-16_open.csv` and `_mid.csv` (the close one is skipped because it exists). That is harmless.

## Decisions the owner made today

| Decision | In the owner's words |
|---|---|
| Fix the lost days by re-scoring history, without inventing recommendations for past days | "go with option 1" |
| Replay the closed trades, and make stale prices impossible in future | "lets do the replay same day trades only, but make sure this isnt an issue going forward" |
| Price at the exact midpoint between bid and ask | "lets go with exact midpoint" |
| A trade that day is not needed for a price; a real bid and ask is enough | "do we not get prices as snapshots without a trade though? why do we need a trade?" |

The owner also asked for a full audit before trusting surprising numbers ("these swings seem crazy to me"). The audit is what led to the pricing change. Do the same again if results look odd: check the source, then the data, then the arithmetic, and only then present.

## What was built today

1. **Scoring and screening in the cloud.** Workflow `score-and-screen.yml` runs after every snapshot fetch, with backup schedules at 02:15 and 08:15 UTC. It scores every day that has a snapshot and no signals file, so a missed night is picked up by the next run.
2. **Volatility history in the repo.** One small file per day in `data/github_sync/iv_history/`, so a cloud runner with an empty database can score. The 1.1 GB local database is no longer needed.
3. **One pricing rule** in `pipeline/pricing.py`: a contract is priced on a day if it has a real bid and ask; the price is the midpoint; the same for entering and for valuing later.
4. **Best-timed snapshot.** Each day is scored from the snapshot captured closest to the 16:00 New York close, between 09:45 and 17:00 that day. Capture times are in `data/github_sync/snapshot_times/`.
5. **Last-hour snapshot.** Workflow `options-preclose-fetch.yml` fires every 20 minutes and only fetches if it starts between 15:00 and 15:50 New York.
6. **A gate in the screen** so a trade is only recommended if its legs give the net credit or debit its strategy needs.
7. **Ledger replayed** and the strategy performance report rebuilt.
8. **Nightly email** moved to 03:30 Dublin, with a staleness check that compares the signals date with the newest close snapshot.
9. **Status email** reworded.

## Results as they stand (midpoint pricing, 255 trades)

| Strategy | Scored | Winners | Typical result | Average result |
|---|---|---|---|---|
| Short calendar | 62 | 69% | +16% | +10.6% |
| Long calendar | 61 | 52% | +6% | +1.3% |
| Iron condor | 22 | 95% | +56% | +41.1% |
| Double diagonal | 3 | 33% | -19% | -9.8% |
| All | 148 | 66% | +15% | +10.9% |

Not scored: 47 open, 57 that could not be priced at entry, 3 unpriced at expiry.

**Read these with care.** The midpoint assumes every leg fills exactly halfway between bid and ask. Tested on the same trades, the calendars lose money once half the bid-ask width is paid; only iron condors stayed profitable under every pricing method tried.

## Open questions for the owner

1. **Quote width.** Should a quote be refused if it is too wide? On 13 Nov a put quoted 0.01 bid / 0.35 ask was priced at 0.18.
2. **Calendar exits.** Calendars exit at a 10% loss or a 5% gain, measured on a very small net price. One day's movement in the quotes can trigger either. Is that what is wanted?
3. **Keep the daily 17:00 status email?** Most days it will now say "all good". The nightly email already raises an alert if scoring falls behind.
4. **Double diagonals entered for a net credit** are now left out of the recommendations, because the tracker measures results against a net debit. They could be tracked as credit trades instead.
5. **The account size is still the 100,000 placeholder** (`pipeline/config.py`), which sets the suggested contract counts in the public ledger.

## Not done yet

- **Master Schedule Google Sheet** is not synced. The two CSV files were updated (backups end `.bak-20261116`), but they do not yet mention the new last-hour snapshot job or the midpoint pricing. Update the CSVs for those two, then sync the Sheet.
- **Repo size.** `options_snapshots/` is about 715 MB and now grows by a fourth file (about 7 MB) each trading day. Every cloud job checks all of it out. Old snapshots need archiving or pruning.
- **Tuning statistics** (`generate_tuning_stats.py`, monthly) will pick up the replayed outcomes on its next run on 1 Dec. It was not re-run today.
- **Two old non-market days** (Sat 5 Sep, Labor Day 7 Sep) still have snapshot and signals files. Nothing is priced on them, so they are harmless.
- **A data subscription** (Tradier was the best fit) is still deferred. With the last-hour snapshot in place, wait a week or two and measure how good the free quotes are before deciding.

## Where things are

- Repo: `coop1st/options-trading-pipeline`. Local copy: `C:\Users\coope\Claude_Work\Projects\Options Trading`.
- Latest commit when this was written: `95ad0ee`. The ledger replay is `0696414`; the ledger before any of today's changes is at `c0a4156`.
- Nightly email routine: `trig_019GMK964MKrAunz5KZiZv8x`, cron `30 3 * * 2-6` UTC.
- Status email routine: `trig_01VBvPrZuubm8yYaXhywrzgz`, cron `0 17 * * 1-5` UTC.
- Routine prompt backups (local only): `routine_backups/options_nightly_email_prompt_2026-11-16b.txt` and `routine_backups/options_status_email_prompt_2026-11-16.txt`.
- A copy of the local database from before today's changes: `data/db/options_pre_backfill_2026-11-16.db` (1.1 GB). Safe to delete once the cloud runs have been clean for a week.
- Tonight's hand-written draft "Options recommendations -- 2026-11-13" used last traded prices, before the pricing change. Six of its 20 trades cannot be priced at entry under the new rule.

## If something has gone wrong

- **Catch up every unscored day:** `gh workflow run score-and-screen.yml --repo coop1st/options-trading-pipeline`
- **Take a snapshot now:** `gh workflow run options-snapshot-fetch.yml --repo coop1st/options-trading-pipeline -f session=close`
- **Rebuild one day's recommendations** (from the project folder, replaces that day's trades): `python pipeline/screen_trades.py --force`
- **Re-score every day** (only after changing the scoring or snapshot rule): `gh workflow run score-and-screen.yml --repo coop1st/options-trading-pipeline -f rescore_all=true`
- **Run all the checks** (from the project folder): `python pipeline/verify_track_outcomes.py`, `python pipeline/verify_score_all_days.py`, `python pipeline/verify_strategy_rules.py`

## Update, Tue 17 Nov 2026 (evening)

**Checks from "First thing tomorrow":**

1. Nightly email: PASS. "Options recommendations -- 2026-11-16" drafted 03:34, 20 trades, midpoint with bid and ask on every leg.
2. Last-hour snapshot: PASS, by luck. `2026-11-17_preclose.csv` captured 15:28 New York (54,197 contracts; 72% had a real two-sided quote, against 62% in the 16 Nov close snapshot taken at 17:03). But GitHub started the every-20-minutes schedule only ONCE all day.
3. Tuesday scored unattended: NOT YET CHECKED. It happens after the 17 Nov close snapshot. Check that the "Scoring ..." line in the run log names the `preclose` snapshot.
4. Status email: PASS ("ALL GOOD: nothing for you to do.").
5. GitHub schedule: NOT recovered. The 17 Nov open and midday fetches had not started by 21:40 Dublin.

**Built today: an on-time start for the last-hour snapshot.**

- Cloud routine "Options preclose dispatch", `trig_01R4JSaGK3iZ8Jq2UwMyJ9Uk`, cron `10 19,20 * * 1-5` UTC. One of the two fires lands at about 15:10 New York in summer and in winter. It checks the New York clock and, inside 15:00-15:50, starts `options-preclose-fetch.yml` through the GitHub tools (`gh` does not work in a routine). It sends a phone notification only if the workflow could not be started.
- The workflow changed (`ca2b983`): a hand start now follows the same rules as a scheduled one (window, holidays, never overwrite). To override: `gh workflow run options-preclose-fetch.yml --repo coop1st/options-trading-pipeline -f force=true`.
- GitHub's own schedule stays as the backup.
- First real fire: Wed 18 Nov at 20:10 Dublin. Good: a `workflow_dispatch` run of "Options preclose fetch" starting about 20:10-20:25 Dublin that takes about 15 minutes and commits "Options snapshot: preclose 2026-11-18".
- Known gap: on half-days (market closes 13:00 New York, next one Fri 27 Nov) the window is after the close, so that day is scored from an earlier snapshot.
- Still to add to the Master Schedule CSVs and Sheet, with the other two outstanding items.

## Update 2, Tue 17 Nov 2026 (late evening): three snapshots a day, two on time

The owner agreed to stop relying on GitHub's clock for anything that needs live quotes.

| Snapshot | When (New York) | Started by | Purpose |
|---|---|---|---|
| `_mid` | about 14:10 | cloud routine | fallback for pricing |
| `_preclose` | about 15:10 | cloud routine | the one trades are priced from |
| `_close` | after 16:00 | GitHub schedule (often hours late) | marks the day as over, sets off scoring |

- The routine is now called "Options snapshot dispatch (14:10 + 15:10 New York)", same id `trig_01R4JSaGK3iZ8Jq2UwMyJ9Uk`, cron `10 18,19,20 * * 1-5` UTC. It picks the job from the New York clock: 14:00-14:50 starts `options-snapshot-fetch.yml` with `session=mid`; 15:00-15:50 starts `options-preclose-fetch.yml`.
- The scheduled open and midday fetches are gone (`a3bef9a`). GitHub started them after the market had shut, so they were never usable. The close schedule is now 20:20 and 21:20 UTC (16:20 New York in summer and winter).
- New guard in `cloud/fetch_options_snapshot.py` (`wrong_time_reason`): `close` is refused before 16:00 New York, `mid`/`open` outside 09:30-16:00, `preclose` outside 15:00-15:50. This matters because scoring treats a `_close` file as proof the day is over.
- Hand starts of either fetch workflow now follow the same rules. To override: add `-f force=true`. So "take a snapshot now" is: `gh workflow run options-snapshot-fetch.yml --repo coop1st/options-trading-pipeline -f session=close -f force=true`
- Runs of the snapshot workflow are now titled with their session, for example "Options snapshot fetch (mid)".
- The status email (`trig_01VBvPrZuubm8yYaXhywrzgz`) now reports the previous trading day's three snapshots and their capture times, and says PROBLEM if the last-hour snapshot is missed two days running. Prompt backup: `routine_backups/options_status_email_prompt_2026-11-17.txt`.

**Check on Wed 18 Nov (evening, Dublin):**

1. About 19:10-19:25: a run titled "Options snapshot fetch (mid)", about 15 minutes, commit "Options snapshot: mid 2026-11-18". This is the first time the routine passes the session input; if the title says "(close)" the input did not get through (the run then skips and the routine sends a phone notification).
2. About 20:10-20:25: a hand-started "Options preclose fetch" run, commit "Options snapshot: preclose 2026-11-18".
3. The close fetch and "Score and screen" afterwards; the "Scoring ..." log line should name the `preclose` snapshot.

**Possible next step (not built):** have the routine also start the close fetch at about 16:10 New York, so scoring happens by about 21:45 Dublin instead of whenever GitHub gets round to it.

## Update 3, Tue 17 Nov 2026 (night): close started on time too, and an ATM IV bug found

- The routine is now "Options snapshot dispatch (14:10 + 15:10 + 16:10 New York)", cron `10 18,19,20,21 * * 1-5` UTC. 16:00-16:50 New York starts `options-snapshot-fetch.yml` with `session=close`, so scoring should finish by about 21:45 Dublin. GitHub's 20:20 and 21:20 UTC close schedules stay as the backup. First real fire Wed 18 Nov, 21:10 Dublin.
- Scoring rule change (`9de90db`, `best_quoted_session`): a snapshot captured in the last hour of trading (15:00-16:00 New York) always beats one captured after the close. Otherwise the 16:10 close capture would have become the pricing source. If the last-hour one is missing, the 16:10 one is used ahead of the 14:10 one. Past days were not re-scored; only 21 Sep would choose differently.
- **Bug found, NOT fixed (owner to decide):** `atm_iv` for an expiry is read from the single strike nearest the underlying price, with no check that its quote is live. On 17 Nov BABA's 15 Jan 2027 expiry got ATM IV 164% because the nearest strike (87.5 call) last traded in May 2025 and carried a stale 42.15 / 43.00 quote; the neighbouring strikes were about 50%. That gave the BABA iron condor (rank 5, score 74.01) full marks for IV richness and term structure it had not earned. 32 of 917 symbol-expiries that day had ATM IV above 150% and 4 were below 3%. Suggested fix: take ATM IV only from strikes with a real two-sided quote and a recent trade, and reject values far from the neighbouring strikes. This feeds iv_history too, so past percentiles are affected.
- Observation, not changed: the iron condor `pop_proxy` score uses 1 minus the AVERAGE of the two short deltas. A condor can lose on either side, so 1 minus the SUM is the closer rough estimate (about 75% rather than 87% for the SPY example).

## Update 4, Tue 17 Nov 2026 (about 23:45 Dublin): ATM IV reading fixed, history rebuilt

The owner said "yes, fix the volatility reading". Commit `d1dcc33`.

**The rule now** (`pipeline/merge_and_score.py`, `live_quote_flags` and `_atm_iv`; numbers in `pipeline/config.py`):
- A contract's implied volatility is only read if its quote is live: bid above zero, ask above bid, spread no more than half the ask, and a trade in the last 7 calendar days.
- An expiry's ATM IV is the median over the 3 live strikes nearest the underlying price (call and put averaged per strike), using no strike more than 15% from the money.
- No live strike near the money means no reading. That expiry then gets no IV percentile and fails the gates that need one.
- The skew reading uses the same live test.
- These numbers (7 days, 3 strikes, 15%) are the project's own choices, not book numbers.
- Re-scoring a day now replaces that day's history rows (`db.delete_history_for_date`) instead of leaving old ones behind.

**Measured before changing anything** (all 59 days, 48,440 expiry readings):
- 76% keep a reading. The 24% that lose one are thin chains: on 17 Nov their median near-the-money open interest was 51, and they held 2.4% of the liquid signal rows.
- Of those that keep one, 77% are within 10% of the old value and 2.9% differ by more than double.
- BABA 15 Jan 2027: 164% became 51%. BABA 18 Dec 2026: 0.4% became 54%.

**What was re-run** (cloud run 44198801901, 8 minutes, `rescore_all=true` + the new `rescreen_newest=true` input):
- All 59 signals files and all 59 `iv_history` files were rebuilt. Checked afterwards: every day has exactly the same contract rows and prices as before, except 21 Sep (see below). Readings above 150% or below 3% in the signals files fell from 643 to 343; the ones left are real (UVXY, earnings-week names).
- 17 Nov recommendations were rebuilt (`0b3ada8`). 10 of 20 trades changed. All six BABA short calendars went (they were built on the false 0.4% / 164% readings), and the BABA iron condor fell from rank 5 (74.01) to rank 17 (67.94). Now: 9 long calendars, 6 iron condors, 4 short calendars, 1 double diagonal. Candidates built fell from 120 to 70.
- Ledger rows for every other day are byte-for-byte unchanged. Past recommendations were NOT rebuilt (standing decision).

**Side effects and things noticed, none acted on:**
- 21 Sep is now scored from its 15:00 "open" snapshot instead of the 16:37 "mid" one (the last-hour rule from Update 3). A full replay shows one stored result would differ: `2026-09-17-^SPX-1`, +23.47% stored, +21.63% on replay. The ledger was left as it is.
- Tracker quirk: when a trade's legs stop being priced before expiry, the tracker records EXPIRED_PROFIT / EXPIRED_LOSS using the last day all legs had a price. 5 of the 6 "expired" trades were last priced 6 to 43 days before expiry (`2026-09-17-^SPX-1` was marked 4 days after entry, 43 days before expiry). These are marks, not expiry results. Owner to decide whether they should count.
- 12 open trades have new results waiting from the 17 Nov prices; the tracker will pick them up on its next run.
- The rebuilt list suggests 266, 400 and 800 contracts on three TE long calendars. That is the 100,000 placeholder account meeting very cheap options (same as ABR on 13 Nov).
