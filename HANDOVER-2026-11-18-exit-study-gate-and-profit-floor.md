# Handover: exit-rule study, looser entry gate, 5-cent minimum profit (Wed 18 Nov 2026)

**To pick up tomorrow (Thu 19 Nov):** do "First thing tomorrow". Everything else is background.

The session was paused in the afternoon, before any of the evening's runs. Nothing from Wednesday evening has been checked.

## Where things stand in one paragraph

The exit-rule study is done. Three rule changes for calendars and double diagonals went live on 18 Nov: a looser entry gate, a 5-cent minimum profit on the target, and a short calendar stop measured on estimated margin. Wednesday evening is the first run of all three, and also the first real run of the snapshot routine's three on-time starts.

## First thing tomorrow

Times are Dublin. Do these in order.

1. **The three snapshot starts on Wed 18 Nov** (first real run of each).
   - `gh run list --repo coop1st/options-trading-pipeline --workflow options-snapshot-fetch.yml --limit 6`
   - `gh run list --repo coop1st/options-trading-pipeline --workflow options-preclose-fetch.yml --limit 4`
   - About 19:10: a run titled "Options snapshot fetch (mid)", commit "Options snapshot: mid 2026-11-18". If the title says "(close)", the routine failed to pass the session setting.
   - About 20:10: a hand-started "Options preclose fetch" run, commit "Options snapshot: preclose 2026-11-18".
   - About 21:10: a run titled "Options snapshot fetch (close)", commit "Options snapshot: close 2026-11-18".
   - If any is missing: RemoteTrigger `list_runs` then `get_run_log` on `trig_01R4JSaGK3iZ8Jq2UwMyJ9Uk`.
2. **Scoring and the first list under the new gate**, by about 21:45 on 18 Nov.
   - `gh run list --repo coop1st/options-trading-pipeline --workflow score-and-screen.yml --limit 4`
   - Good: a new `data/github_sync/signals/2026-11-18.csv`, a `rec:2026-11-18` column in the ledger, and a "Scoring ..." log line naming the `preclose` snapshot captured about 15:10-15:25 New York.
   - In the same log, look for "... calendar/diagonal candidate(s) left out: net price smaller than the quote width of the legs". Note how many were left out and what the 20 trades are made of.
   - Bad: a Python error mentioning `target_clears_quote_width` or `QUOTE_WIDTH_GATE_STRATEGIES`.
3. **Outcome tracking**, the 01:29 run on Thu 19 Nov.
   - `gh run list --repo coop1st/options-trading-pipeline --workflow track-outcomes.yml --limit 3`
   - Good: success. Any short calendar that closes should be a target, not a stop. Any calendar or diagonal marked HIT_TARGET should have made at least 5 cents.
   - Bad: an error mentioning `short_calendar_margin` or `margin`.
4. **Nightly email for 18 Nov.** Gmail drafts, "Options recommendations -- 2026-11-18", about 03:30 on Thu 19 Nov. Bad: "Options signals -- automation alert", or no draft.
5. **Status email.** Draft "Options status -- 2026-11-18", about 17:05 on Wed 18 Nov. Good: "ALL GOOD" and a line on Tuesday's snapshots with New York capture times (first run of the reworded prompt).

Already checked on 18 Nov: the nightly draft for 17 Nov passed (20 trades, bid, ask and midpoint on every leg, SPY condor in, no BABA short calendars).

## What the study found

Script: `studies/exit_rule_study.py`. It matches the ledger exactly (138 exits, 0 mismatches).

- 73 of 138 calendar and double diagonal exits fired on the first day, 97 within two days.
- Outside ^SPX the typical net price is $0.47 to $0.63. The 5% target is 2 to 3 cents against 21 cents of half quote width.
- 78-79% of exits outside ^SPX were moves smaller than half the quote width. ^SPX short calendar moves are real (9%).
- Paying half the quote width in and out: long calendar winners fall from 54% to 3%, short calendars from 72% to 37%.
- Holding longer helps long calendars (inside the noise) and hurts short calendars.
- Books: the 5-10% target "in a few days" is Chen/Sebastian ch.9. The stop there is "10% of the original margin", not 10% of the net price.

## Decisions the owner made today

| Decision | In the owner's words |
|---|---|
| Build the entry gate and the margin stop; no minimum holding period; thresholds stay | "lets do 1 and 2. But on 3, no minimum holding period. And leave the rules but also leave as is." |
| The first gate was too strict | "it takes away too many of the trades we already did" |
| Use the looser gate and add a minimum profit | "lets go with the looser gate (A), and also give a minimum cent value increase on profit margin in order to cover cost of trade" |
| Size of the minimum profit | "i want a flat amount per trade, 5 cents" |

## The calendar and double diagonal rules as they now stand

| Rule | Now | Whose number |
|---|---|---|
| Entry gate | Refused only when the net price is smaller than the combined bid-ask width of the legs | Project's own |
| Profit target | 5% of the net price, and at least 5 cents per share | 5% is the book's; 5 cents is the owner's |
| Stop, long calendar and double diagonal | 10% of the net price (unchanged) | Book's for the long calendar |
| Stop, short calendar | 10% of estimated original margin | Book's rule; the margin estimate is the project's own |
| Minimum holding period | None | Owner's decision |

All apply to open and new trades. Past results were not replayed.

## What was built today

1. **Entry gate** (`screen_trades.target_clears_quote_width`, `config.QUOTE_WIDTH_GATE_STRATEGIES`). 116 of 180 past trades pass. 9 of the 14 calendar and diagonal trades on the 17 Nov list pass. A stricter first version (the 5% target had to clear half the width) passed only 25 of 180 and was replaced the same afternoon.
2. **Minimum profit** (`config.CALENDAR_MIN_PROFIT_DOLLARS = 0.05`). On past trades it changes one long calendar and one short calendar.
3. **Short calendar stop on margin** (`track_outcomes.short_calendar_margin`, `config.NAKED_MARGIN_*`). The estimate is the exchange rule for an uncovered short option: 15% of the underlying for index options, 20% for shares.
4. **Study scripts** in `studies/`: `exit_rule_study.py` (two output tables beside it) and `target_floor_replay.py`.

## Things the owner has been told and should keep in mind

- **The short calendar stop will almost never fire.** The estimated margin is about 87 times the credit on ^SPX and 17 times elsewhere. On 68 past short calendars it would not have fired once. The 19 old stops would have become 6 targets, 3 expiry marks and 10 still open at -30% to -64% of the credit. A second, tighter stop was offered; no answer yet.
- **5 cents is well below the real cost of trading these.** The bid-ask width of the legs is 19 cents on the KHC example. After taking the full width off as cost, the replay shows 3% of long calendars and 52% of short calendars as winners.

## Open questions for the owner

1. **Short calendar position size** is still worked out from the credit, which is not the trade's real risk (88 contracts suggested on a KHC short calendar on 17 Nov). Use the margin estimate instead? Asked 18 Nov, not answered.
2. **A second, tighter stop for short calendars?** Offered 18 Nov, not answered.
3. **Keep the daily 17:00 status email?** (Carried over.)
4. **Double diagonals entered for a net credit** are left out of the recommendations. (Carried over.)
5. **Account size** is still the 100,000 placeholder. (Carried over.)
6. **Chance-of-profit score for iron condors** averages the two short deltas instead of summing them. Reported, not changed. (Carried over.)

The old open question about a quote-width limit is now answered for calendars and diagonals by the entry gate. It is still open for the other strategies.

## Not done yet

Carried over unchanged from the 17 Nov handover: Master Schedule CSVs and Google Sheet, repo size, the half-day window (next: Fri 27 Nov), the Tradier decision, and the untracked `HANDOVER-2026-11-11-local-steps-problem.md`. The Master Schedule needs no entry for today's changes, as no job or time changed.

## Where things are

- Repo: `coop1st/options-trading-pipeline`. Local copy: `C:\Users\coope\Claude_Work\Projects\Options Trading`.
- Today's commits: `df21c2b` (strict gate and margin stop), `1029e0b` (looser gate), `2f96912` (5-cent minimum profit).
- Before today's changes: `47eb54a`.
- Earlier handovers: `HANDOVER-2026-11-17-on-time-snapshots-and-exit-rules-next.md` (routine ids, "If something has gone wrong" commands) and `HANDOVER-2026-11-16-cloud-scoring-and-midpoint-pricing.md`.

## If something has gone wrong tonight

- **The screen failed on the new gate:** fix forward, or `git revert 1029e0b df21c2b` is not clean because the tracker change shares `df21c2b`. Quicker: set `QUOTE_WIDTH_GATE_STRATEGIES = ()` in `pipeline/config.py`, push, then `gh workflow run score-and-screen.yml --repo coop1st/options-trading-pipeline`.
- **The tracker failed on the margin stop:** in `run_track_outcomes` set `overrides = None` for short calendars (the stop then falls back to 10% of the credit), push, then `gh workflow run track-outcomes.yml --repo coop1st/options-trading-pipeline`.
- **A snapshot was not started, or a day is unscored:** the commands are in the 17 Nov handover.
- **Run all the checks** (from the project folder): `python pipeline/verify_track_outcomes.py`, `python pipeline/verify_score_all_days.py`, `python pipeline/verify_strategy_rules.py`.
