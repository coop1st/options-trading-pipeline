# Handover: on-time snapshots, volatility reading fix, and the exit-rule study next (Tue 17 Nov 2026)

**To pick up tomorrow (Wed 18 Nov):** do "First thing tomorrow", then start "Next step: the exit-rule study". Everything else is background.

The detail of each change made today is in `HANDOVER-2026-11-16-cloud-scoring-and-midpoint-pricing.md`, sections "Update, Tue 17 Nov" to "Update 5". This file is the short version plus what to do next.

## Where things stand in one paragraph

The options project runs entirely in the cloud and no longer relies on GitHub's clock for anything that needs live prices. A cloud routine starts three snapshots a day on time. Tuesday 17 Nov was scored and screened from a last-hour snapshot. Two faults found today are fixed: the at-the-money volatility reading (one dead strike could set it) and "expired" results that were really early marks. None of the routine's three real starts has happened yet; the first are on Wed 18 Nov.

## First thing tomorrow

Times are Dublin. Do these in order.

1. **Nightly email for 17 Nov.** Gmail drafts, "Options recommendations -- 2026-11-17", created about 03:30 on Wed 18 Nov.
   - Good: 20 trades with midpoint, bid and ask on every leg. No BABA short calendars. The SPY iron condor (790/800 calls, 650/640 puts, 15 Jan 2027) is in it.
   - Bad: "Options signals -- automation alert", or no draft.
2. **Status email.** Draft "Options status -- 2026-11-18", about 17:05.
   - Good: "ALL GOOD", and a line on yesterday's snapshots with their New York capture times. This is the first run of the reworded prompt.
3. **The routine's three starts** (first real run of each):
   - `gh run list --repo coop1st/options-trading-pipeline --workflow options-snapshot-fetch.yml --limit 6`
   - `gh run list --repo coop1st/options-trading-pipeline --workflow options-preclose-fetch.yml --limit 4`
   - About 19:10: a run titled "Options snapshot fetch (mid)", about 15 minutes, commit "Options snapshot: mid 2026-11-18". If the title says "(close)", the routine failed to pass the session setting; the run then skips and a phone notification is sent.
   - About 20:10: a hand-started "Options preclose fetch" run, commit "Options snapshot: preclose 2026-11-18".
   - About 21:10: a run titled "Options snapshot fetch (close)", commit "Options snapshot: close 2026-11-18".
   - If any is missing, read the routine's own log: RemoteTrigger `list_runs` then `get_run_log` on `trig_01R4JSaGK3iZ8Jq2UwMyJ9Uk`.
4. **Scoring after the close**, by about 21:45.
   - `gh run list --repo coop1st/options-trading-pipeline --workflow score-and-screen.yml --limit 4`
   - Good: a new `data/github_sync/signals/2026-11-18.csv`, a `rec:2026-11-18` column in the ledger, and in the run log a "Scoring ..." line naming the `preclose` snapshot captured about 15:10-15:25 New York.

## Next step: the exit-rule study

**Why.** The calendar and double diagonal exit rules are now the weakest part of the results. On 17 Nov, 17 trades recommended on 13 and 16 Nov closed after one or two trading days: 10 short calendars (5 targets, 5 stops, results from -81% to +45%), 6 double diagonals (all targets) and 1 long calendar (+109%). The exits are measured against a very small net price, so a day or two of quote movement triggers them. This is open question 2 from the 16 Nov handover.

**What the owner was offered** (17 Nov, last message of the session): measure first, propose a rule change second. The owner has not yet said yes to the study; they asked for it to be written here and picked up tomorrow. Confirm before starting.

**The study, in order:**

1. **Count the fast exits.** For every scored calendar and double diagonal in the ledger: days from entry to exit, by strategy and by exit type (target or stop). How many exited within 1, 2 and 5 trading days.
2. **Size of the base.** For the same trades: the net entry price (credit or debit) in dollars per share, and that price as a share of the larger leg's price. Show how small the base is when exits fire fast.
3. **Quote noise against the thresholds.** For each fast exit: was the move bigger than the legs' own bid-ask width on the exit day? An exit that sits inside the quote width is noise, not a result.
4. **Hold-longer replay.** Re-run those trades ignoring exits in the first N days (try N = 2, 3, 5) and to the front leg's last week. Compare winners and average result with today's figures. `evaluate_trade` in `pipeline/track_outcomes.py` takes `evaluator_overrides`, but only for the directional longs by design; the replay will need its own loop, kept in a study script, not in the tracker.
5. **Check the books before proposing anything.** Read the `options-playbook` reference docs in full for calendar and diagonal exits (spreads-and-combinations, income-strategies). Cite chapter and number. The thresholds are in `pipeline/config.py`: `CALENDAR_EXIT_TARGET_PCT`, `CALENDAR_EXIT_STOP_PCT`, `DIAGONAL_EXIT_TARGET_PCT`, `DIAGONAL_EXIT_STOP_PCT`. Say plainly which are book numbers and which are the project's own.
6. **Present the numbers, then options.** Audit first, then present. No rule change without the owner's say.

**Things to keep in mind while doing it:**

- Results are at bid/ask midpoints. The 16 Nov handover found calendars lose money once half the bid-ask width is paid.
- Most of the fast exits are on ^SPX, with legs a few days apart. Split ^SPX from everything else.
- The double diagonal figure (9 scored, 78% winners) is six one-day exits plus three older trades. Do not read it as a result.
- Open question 4 (double diagonals entered for a credit) and open question 1 (quote-width limit) touch the same trades.

## Decisions the owner made today

| Decision | In the owner's words |
|---|---|
| Start the last-hour snapshot on time from a cloud routine | "yes, build that 15:10 job." |
| No extra snapshots; make the few land on time; drop the open and midday schedules | "yes" |
| Start the close snapshot on time too | "yes, add the 16:10 close start too" |
| Fix the at-the-money volatility reading | "yes, fix the volatility reading" |
| Take the early "expired" marks out of the results | "yes, take the expired trades out of the win-rate figures" |

## What was built today

1. **Routine "Options snapshot dispatch (14:10 + 15:10 + 16:10 New York)"**, `trig_01R4JSaGK3iZ8Jq2UwMyJ9Uk`, cron `10 18,19,20,21 * * 1-5` UTC. It reads the New York clock and starts the midday, last-hour or close snapshot. Phone notification only on failure.
2. **Snapshot workflows.** Scheduled open and midday fetches removed. Close scheduled at 20:20 and 21:20 UTC as a backup. A hand start follows the same rules as a scheduled one; `-f force=true` overrides. A session started at the wrong time of day for its name is skipped.
3. **Snapshot choice.** A capture from the last hour of trading always beats one taken after the close.
4. **Volatility reading.** Live quotes only (two-sided, not wide, traded in the last 7 days); the middle value of the 3 live strikes nearest the money, none more than 15% away; otherwise no reading. All 59 days re-scored; 17 Nov recommendations rebuilt (10 of 20 changed).
5. **Expiry results.** Only from prices on the expiry day itself. Six trades reclassified as unresolved. Performance report rebuilt (159 scored).
6. **Status email** now reports the previous day's three snapshots and says PROBLEM if the last-hour one is missed two days running.

## Results as they stand (midpoint pricing)

| Strategy | Scored | Winners | Average result |
|---|---|---|---|
| Iron condor | 21 | 95.2% | +42.0% |
| Short calendar | 68 | 72.1% | +8.9% |
| Long calendar | 61 | 54.1% | +3.1% |
| Double diagonal | 9 | 77.8% | +12.9% |

Not scored: 50 open, 57 that could not be priced at entry, 9 unresolved at expiry.

## Open questions for the owner

1. **Quote-width limit.** Should a quote be refused for pricing if it is too wide? (Carried over.)
2. **Calendar and diagonal exits.** The study above.
3. **Keep the daily 17:00 status email?** (Carried over.)
4. **Double diagonals entered for a net credit** are left out of the recommendations. (Carried over.)
5. **Account size** is still the 100,000 placeholder. The 17 Nov list suggests 266, 400 and 800 contracts on three TE long calendars.
6. **Chance-of-profit score for iron condors** uses the average of the two short deltas (87% on the SPY example). The sum (about 75%) is the closer estimate. Reported, not changed.
7. **One past result out of step.** 21 Sep is now scored from a different snapshot. Only `2026-09-17-^SPX-1` was affected, and that trade is now unresolved anyway, so nothing needs doing unless the ledger is ever replayed.

## Not done yet

- **Master Schedule CSVs and Google Sheet.** Still to add: the snapshot routine (three fires), the removed open and midday fetches, the new close times, midpoint pricing. Backups from 16 Nov end `.bak-20261116`.
- **Repo size.** `options_snapshots/` is about 720 MB and grows by three files (about 7 MB each) per trading day.
- **Half-days.** When the market closes at 13:00 New York (next: Fri 27 Nov), the 14:10 and 15:10 starts fall after the close and are skipped. That day is scored from the 16:10 close snapshot, which is three hours stale. A half-day window is not built.
- **Tuning statistics** run on 1 Dec and will pick up today's changes by themselves.
- **A data subscription** (Tradier) is still deferred. After a week of on-time snapshots, measure the free quotes before deciding.
- **`HANDOVER-2026-11-11-local-steps-problem.md`** is still untracked in the project folder. It predates the cloud move.

## Where things are

- Repo: `coop1st/options-trading-pipeline`. Local copy: `C:\Users\coope\Claude_Work\Projects\Options Trading`.
- Latest code commit: `0669fae` (expiry rule). Before today's changes: `39344e3`.
- Key commits today: `ca2b983` and `a3bef9a` (snapshot workflows), `9de90db` (last-hour-first), `d1dcc33` (volatility reading), `0b3ada8` (17 Nov recommendations rebuilt), `0669fae` (expiry rule), `df60341` (report).
- Snapshot routine: `trig_01R4JSaGK3iZ8Jq2UwMyJ9Uk`, https://claude.ai/code/routines/trig_01R4JSaGK3iZ8Jq2UwMyJ9Uk
- Nightly email routine: `trig_019GMK964MKrAunz5KZiZv8x`, cron `30 3 * * 2-6` UTC.
- Status email routine: `trig_01VBvPrZuubm8yYaXhywrzgz`, cron `0 17 * * 1-5` UTC. Prompt backup (local only): `routine_backups/options_status_email_prompt_2026-11-17.txt`.
- The snapshot routine's prompt has no local backup; read it with RemoteTrigger `get`.

## If something has gone wrong

- **A snapshot was not started:** `gh workflow run options-snapshot-fetch.yml --repo coop1st/options-trading-pipeline -f session=mid` (or `close`), or `gh workflow run options-preclose-fetch.yml --repo coop1st/options-trading-pipeline`. Both obey the time-of-day rules. Add `-f force=true` to fetch regardless.
- **Catch up every unscored day:** `gh workflow run score-and-screen.yml --repo coop1st/options-trading-pipeline`
- **Re-score every day** (only after a change to a reading or the snapshot rule): add `-f rescore_all=true`
- **Rebuild the newest day's recommendations** (replaces that day's trades): add `-f rescreen_newest=true`
- **Update trade results now:** `gh workflow run track-outcomes.yml --repo coop1st/options-trading-pipeline`
- **Rebuild the performance report:** `gh workflow run compare-strategies.yml --repo coop1st/options-trading-pipeline`
- **Run all the checks** (from the project folder): `python pipeline/verify_track_outcomes.py`, `python pipeline/verify_score_all_days.py`, `python pipeline/verify_strategy_rules.py`

## Update, Wed 18 Nov: exit-rule study done, two changes live

**Study** (`studies/exit_rule_study.py`, outputs beside it; matches the ledger exactly, 138 exits):

- 73 of 138 calendar and double diagonal exits fired on day 1, 97 within two days.
- Outside ^SPX the typical net price is $0.47 to $0.63, so the 5% target is 2 to 3 cents against 21 cents of half quote width. 78-79% of those exits were moves smaller than half the quote width. ^SPX short calendar moves are real (9% inside).
- Paying half the quote width in and out: long calendar winners fall from 54% to 3%, short calendar 72% to 37%.
- Holding longer: long calendars look better (inside the noise), short calendars get worse.
- Books: the 5-10% target "in a few days" is Chen/Sebastian ch.9. The stop is "10% of the original margin", not of the net price.

**Owner's decisions (18 Nov):** "lets do 1 and 2. But on 3, no minimum holding period. And leave the rules but also leave as is."

1. **Entry gate, live (df21c2b).** A calendar or double diagonal is not recommended when its 5% target in dollars is smaller than half the combined bid-ask width of its legs (`screen_trades.target_clears_quote_width`). On past data only 25 of 180 priceable trades pass: 23 ^SPX short calendars and 2 SPY. No long calendar and no double diagonal has ever passed. None of the 14 calendar/diagonal trades on the 17 Nov list would pass.
2. **Short calendar stop on margin, live (df21c2b).** Stop = a loss of 10% of an estimated original margin (`track_outcomes.short_calendar_margin`; exchange rule for an uncovered short option, the project's own estimate, constants in `config.py`). Target still 5% of the credit; result still reported on the credit. Applies to open (11) and new short calendars. Past results are not replayed.
3. No minimum holding period. Thresholds unchanged.

**Known consequence of 2, told to the owner:** the estimated margin is about 87 times the credit on ^SPX and 17 times elsewhere, so on the 68 past short calendars the new stop would never have fired. The 19 old stops would have become 6 targets, 3 expiry marks and 10 still open at -30% to -64% of the credit.

**Found, not changed:** short calendar position size is still worked out from the credit (`max_loss` in `build_calendars`), which is not the trade's real risk.

**Evening checks for 18 Nov** (items 2 to 4 of "First thing tomorrow") were not yet due when this was written. Item 1 passed. Tonight's screen is the first with the entry gate: expect a log line "... calendar/diagonal candidate(s) left out: exit target smaller than half the quote width" and a list made mostly of iron condors and verticals.

### Later on 18 Nov: gate loosened, profit floor waiting on the owner

- The owner did not like the strict gate ("it takes away too many of the trades we already did"). Replaced the same afternoon (1029e0b) with the looser one: a calendar or double diagonal is refused only when its net price is smaller than the combined bid-ask width of its legs. 116 of 180 past trades pass; 9 of the 14 on the 17 Nov list pass.
- The owner also asked for "a minimum cent value increase on profit margin in order to cover cost of trade". NOT built yet. Replay (`studies/target_floor_replay.py`): a profit floor on its own makes long calendars worse (19 stops, 3 targets) because the stop stays a few cents wide; the same floor on the stop fixes that. Waiting on the owner's yes/no for the stop.
