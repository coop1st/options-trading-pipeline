# Handover — pick this up from here

Last updated 2026-08-28 to hand this project off between Claude Code
sessions. Everything referenced here is committed and pushed to `master`
at https://github.com/coop1st/options-trading-pipeline (public repo).
Read this file first, then the specs/plans it points to.

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

**Next step**: sub-project 3 (Strategy/Screening Engine) — apply the
`options-playbook` skill's entry/risk rules to the signals export to
generate real trade candidates, replacing the routine's current diagnostic
placeholder, and build the recommendation ledger to track them.

**Known deferred minors** (see the plan's ledger history / final review
for full detail, none blocking): the GitHub Actions workflow still has one
residual script-injection-class line (`cloud/fetch_options_snapshot.py`'s
own invocation step interpolates `${{ steps.session.outputs.session }}`
directly — same class as a fix already applied to the session-determination
step, just one step downstream); the local merge script backfills only the
single most recent unscored date, not multiple missed nights; a handful of
Minor code-quality notes (unpinned `requirements.txt`, no workflow
timeout/concurrency guard, etc.).

**Sub-project 3 (Strategy/Screening Engine) — not started.** Scoped only
at the top level, in sub-project 1's spec's decomposition section. Depends
on sub-project 2's signals export existing first — which it now does.

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
