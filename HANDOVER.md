# Handover — pick this up from here

Written 2026-08-26 to hand this project off between Claude Code sessions.
Everything referenced here is committed and pushed to `master` at
https://github.com/coop1st/options-trading-pipeline (public repo). Read
this file first, then the specs/plans it points to.

## Where things stand

**Sub-project 1 (Options Playbook skill) — complete.** A Claude Code skill
at `.claude/skills/options-playbook/` distilling both source books
(Bittman's *Trading Options as a Professional*, Chen/Sebastian's *The
Option Trader's Hedge Fund*) into 8 reference docs + `SKILL.md`. Built via
36-task plan in `docs/superpowers/plans/2026-08-26-options-playbook.md`
(all tasks done, plan fully executed). Source PDFs live in `Material/`
(git-ignored — copyrighted, never commit them) with per-chapter extraction
notes in `docs/extraction-notes/` for traceability.

**Sub-project 2 (Data & Scoring Pipeline) — designed, not yet built.**
Spec is written, self-reviewed, and committed at
`docs/superpowers/specs/2026-08-26-data-and-scoring-pipeline-design.md` —
**read that file in full before doing anything else**. Short version:

- Watchlist comes live from the Stocks project's public
  `stock_price_ledger.csv` (every symbol ever suggested in its day-trade
  email) — no separate watchlist file for this project.
- A GitHub Actions workflow (not yet created) fetches options chains 3x/day
  (open/mid/close) via yfinance and commits raw snapshots.
- A local script (not yet created) merges those snapshots nightly, computes
  Greeks using the playbook's Black-Scholes formulas, and publishes a
  "signals" export back to GitHub.
- An overnight (~2:30am) **Claude Code scheduled routine** (not GitHub
  Actions — same mechanism as the Stocks project's day-trade/chocolate-digest
  routines) reads the signals, applies the playbook, drafts a Gmail email,
  and updates a new options recommendation ledger.
- This was empirically validated this session: a throwaway test workflow
  confirmed GitHub-hosted Actions runners need **no** special SSL/proxy
  workaround for yfinance (unlike this local machine, which needs the
  Norton-TLS-inspection fix below), and confirmed the Stocks ledger is
  fetchable via `raw.githubusercontent.com` with no auth. The test workflow
  was deleted after confirming this — nothing to clean up.

**Next step**: the spec needs your review/sign-off, then invoke the
`writing-plans` skill to turn it into an implementation plan (same
process sub-project 1 went through: brainstorm → spec → plan → execute).

**Sub-project 3 (Strategy/Screening Engine) — not started.** Scoped only
at the top level, in sub-project 1's spec's decomposition section. Depends
on sub-project 2's signals export existing first.

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
- `docs/superpowers/plans/` — 1 implementation plan so far (playbook,
  fully executed)
