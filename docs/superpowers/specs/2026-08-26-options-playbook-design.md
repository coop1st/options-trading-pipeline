# Options Playbook Skill — Design

## Context

This is the first of three connected sub-projects that make up the Options
Trading project:

1. **Options Playbook** (this spec) — a Claude Code skill distilling two
   options-trading books into a structured, comprehensive knowledge base.
2. **Data & scoring pipeline** — fetch options chains, compute greeks, and
   integrate the existing `Projects/Stocks` project's scores/RSI/fundamentals.
3. **Strategy/screening engine** — combine (1) and (2) to surface concrete
   options trade setups and underlying-stock buy/sell price targets.

Sub-project 2 depends on nothing in this spec. Sub-project 3 depends on both
1 and 2. This spec covers only sub-project 1, which has no data dependencies
and can be built standalone.

Source material lives in `Material/` (git-ignored — copyrighted book PDFs,
never committed):

- James Bittman, *Trading Options as a Professional: Techniques for Market
  Makers and Experienced Traders* (McGraw-Hill, 2008)
- Dennis A. Chen & Mark Sebastian, *The Option Trader's Hedge Fund: A
  Business Framework for Trading Equity and Index Options* (Pearson, 2012)

The user has explicitly prioritized completeness over speed: "fully
comprehensive, don't shortcut this... don't miss anything... take your
time." This spec optimizes for coverage and traceability back to source,
not for minimizing effort.

## Goals

- Capture the full content of both books — strategies, greeks mechanics,
  risk frameworks, market-making techniques, and the hedge-fund business
  framework — as a structured, reusable knowledge base.
- Package it as a Claude Code skill (`options-playbook`) scoped to this
  project, invocable in future sessions so sub-project 3's strategy engine
  (and any manual research) can apply the rules consistently.
- Keep any single invocation cheap via progressive disclosure: a lean
  `SKILL.md` entry point, detail pushed into `references/` files loaded on
  demand.
- Preserve enough source traceability (which book/chapter a rule came from)
  that later work can go back to the original material if needed.

## Non-goals

- No code in this sub-project — it is a content/knowledge-authoring task.
- Not deciding sub-project 2/3 implementation details here (data provider
  wiring, screening logic) beyond noting how they'll consume this skill.
- No attempt to resolve every disagreement between the two books into one
  "correct" answer — where they differ, the playbook notes both views and
  why, rather than silently picking one.

## Architecture

```
Projects/Options Trading/
├── .claude/skills/options-playbook/
│   ├── SKILL.md                              Entry point: when to use, strategy map, pointers
│   └── references/
│       ├── greeks-and-volatility.md          Delta/gamma/theta/vega/rho, IV vs HV, skew, term structure
│       ├── income-strategies.md              Covered calls, cash-secured puts, credit spreads
│       ├── spreads-and-combinations.md       Verticals, iron condors, calendars, diagonals, ratios, butterflies
│       ├── directional-strategies.md         Long calls/puts, synthetics
│       ├── market-making-techniques.md       Bittman's market-maker material: pricing, hedging, order flow
│       ├── risk-management-and-position-sizing.md   Risk of ruin, capital allocation, hedging
│       ├── trading-business-framework.md     Chen/Sebastian's business-of-trading framework
│       └── glossary.md                       Terms and formulas, cross-referenced
└── docs/
    └── extraction-notes/                     Intermediate per-chapter extraction notes (working material, committed
                                               for traceability, not part of the skill itself)
```

`SKILL.md` stays short: a description of what the skill covers, a map of
which reference file addresses which topic, and guidance on when to pull
which file in. It does not restate the detailed content itself.

## Process

**1. Chapter-batched extraction.** Both books get processed chapter by
chapter. The `Read` tool caps PDF reads at 20 pages per call, so any chapter
longer than 20 pages is split into multiple sequential batches sized to fit
(a 35-page chapter → two batches of ~18; a 42-page chapter → three batches
of 14). Each batch is read and extracted before moving to the next, so no
content is skipped at a batch boundary.

**2. Structured notes per chapter.** For each chapter, produce a structured
extraction note under `docs/extraction-notes/` capturing: strategy
definitions, formulas, worked examples, rules of thumb, risk caveats, and
which book/chapter/page range it came from. This is the traceability layer
and the raw material the synthesis pass draws on.

**3. Dispatch via parallel subagents.** Because both books combined are
long (~700+ pages) and each chapter-batch extraction is a bounded,
independent task, extraction work is dispatched using
`superpowers:dispatching-parallel-agents` rather than done serially in the
main session — one subagent per chapter (respecting the 20-page batching
rule internally), reporting back structured notes.

**4. Synthesis pass.** Once extraction notes exist for both books, a
synthesis pass writes the actual `references/*.md` files, organized by
topic (not by book or chapter), cross-referencing both sources. Where the
books agree, state the consensus. Where they differ, present both views
with attribution. Where only one book covers a topic (e.g., Bittman's
market-making focus, Chen/Sebastian's business framework), attribute
accordingly.

**5. `SKILL.md` authored last**, once the reference files exist, so its
topic map and guidance accurately reflect what's actually in each file.

## Completeness validation

Before considering the skill done, cross-reference each book's table of
contents against the extraction notes and reference docs to confirm every
chapter/topic was captured somewhere. Any gap gets filled before moving to
sub-project 2. This is the explicit check against the user's "don't miss
anything" requirement — it's a checklist pass, not a rewrite.

## How later sub-projects use this

Sub-project 3's screening engine invokes this skill to apply selection
criteria (e.g., "what greeks profile and risk rules define an acceptable
credit spread entry") when generating trade candidates. It should not need
to re-derive strategy rules — it looks them up here.

## Open questions

None blocking — the reference-file breakdown was confirmed with the user,
as was the batching rule for large chapters.
