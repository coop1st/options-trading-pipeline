# Options Playbook Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Distill both books in `Material/` into a comprehensive Claude Code skill (`options-playbook`) — a lean `SKILL.md` plus topic-based `references/*.md` files — with nothing from either book left uncaptured.

**Architecture:** Three phases. (1) Chapter-by-chapter extraction: read each chapter in ≤20-page batches, write one structured extraction note per chapter to `docs/extraction-notes/`, tagged with source/page attribution. (2) Synthesis: eight topic-based reference docs are each written by reading *all* extraction notes and pulling everything relevant to that topic (topics cut across chapters and across the two books). (3) `SKILL.md` authored last from the finished reference docs, then a completeness pass cross-checks both books' tables of contents against what got captured.

**Tech Stack:** Markdown only. No code. PDF text extraction via `pdftotext` (already available in this environment) when the `Read` tool's built-in PDF rendering isn't available; `Read` tool otherwise. Page-range batches are capped at 20 pages per the `Read` tool's PDF limit.

**Spec:** `docs/superpowers/specs/2026-08-26-options-playbook-design.md`

## Global Constraints

- Any single PDF read must cover **20 pages or fewer**. A chapter longer than 20 pages is split into multiple sequential batches (e.g., 29 pages → 2 batches; 55 pages → 3 batches) — see per-task batch breakdown below.
- `Material/` is git-ignored (contains copyrighted book PDFs). **Never** `git add` anything under `Material/`.
- Every extraction note starts with a one-line `Source:` header naming the book, chapter number/title, and printed-page range.
- Where the two books disagree on a point, synthesis notes both views with attribution rather than silently picking one (per spec).
- Extraction notes live under `docs/extraction-notes/`, one file per chapter (or appendix group), named `<book>-chNN-<slug>.md`.
- Reference docs live under `.claude/skills/options-playbook/references/`, one file per topic, per the spec's breakdown.
- Commit after every task. Never batch multiple tasks into one commit.

## Source Page Maps (for reference across all tasks)

**Bittman, *Trading Options as a Professional* (McGraw-Hill, 2008)** — file:
`Material/(McGraw-Hill finance & investing) James Bittman - Trading Options as a Professional_ Techniques for Market Makers and Experienced Traders-McGraw-Hill (2008).pdf`
Physical PDF page = printed page + 23.

| Ch | Title | Printed pp. | Physical PDF pp. |
|----|-------|-------------|-------------------|
| 1 | Option Market Fundamentals | 1–29 | 24–52 |
| 2 | Operating the Op-Eval Pro Software | 31–48 | 54–71 |
| 3 | The Basics of Option Price Behavior | 49–75 | 72–98 |
| 4 | The Greeks | 77–131 | 100–154 |
| 5 | Synthetic Relationships | 135–160 | 158–183 |
| 6 | Arbitrage Strategies | 163–203 | 186–226 |
| 7 | Volatility | 205–238 | 228–261 |
| 8 | Delta-Neutral Trading: Theory and Reality | 241–277 | 264–300 |
| 9 | Setting Bid-Ask Prices | 279–310 | 302–333 |
| 10 | Managing Position Risk | 311–340 | 334–363 |
| — | Epilogue | 343 | 366 |

**Chen & Sebastian, *The Option Trader's Hedge Fund* (Pearson/FT Press, 2012)** — file:
`Material/dennis_a._chen__mark_sebastian_-_the_option_trader_s_hedge_fund__a_business_framework_for_trading_equity_and_index_options-pearson_education_2012_.pdf`
(Physical PDF pages given directly; this book's own printed-page numbers are not needed.)

| Ch | Title | Physical PDF pp. |
|----|-------|-------------------|
| 1 | The Insurance Business | 22–36 |
| 2 | Trade Selection | 37–49 |
| 3 | Risk Management | 50–59 |
| 4 | Trade Execution | 60–71 |
| 5 | The Trading Plan | 72–79 |
| 6 | Trading Infrastructure | 80–87 |
| 7 | Learning Processes | 88–96 |
| 8 | Understanding Volatility | 97–104 |
| 9 | Most Used Strategies | 105–147 |
| 10 | Operating the Business: TOMIC 1.0 A to Z | 148–157 |
| 11 | Lessons from the Trading Floor on Volatility | 158–173 |
| 12 | Lessons from the Trading Floor on Risk Management | 174–182 |
| 13 | Lessons from the Trading Floor on Trading and Execution | 183–200 |
| 14 | Lessons from the Trading Floor on the Other Greeks | 201–221 |
| 15 | The Beginning | 222–224 |
| A–D | Appendices (Recommended Reading; Strategy Learning Sequence; OptionPit.com; Kite Spread) | 225–235 |

Both books' indexes (Bittman ~368+, Chen 236–267) are excluded — no content to extract.

## PDF reading note

If the `Read` tool's PDF rendering errors (as it did during planning — `pdftoppm is not installed`), fall back to:

```bash
pdftotext -f <first_page> -l <last_page> "Material/<exact filename>.pdf" -
```

`pdftotext` is confirmed available in this environment. Use the exact filenames from the Source Page Maps above (they contain spaces and punctuation — quote them).

---

# Phase 1: Extraction (26 tasks)

Each task is independent of every other extraction task — they can be dispatched in parallel.

### Task 1: Extract Bittman Ch.1 — Option Market Fundamentals

**Files:**
- Create: `docs/extraction-notes/bittman-ch01-option-market-fundamentals.md`

**Source:** Bittman, Chapter 1, printed pp. 1–29 (physical pp. 24–52). Known section headings: Fundamental Terms; The Market—Definition 1; The Market—Definition 2; National Best Bid and Best Offer; Margin Accounts and Related Terms; Profit/Loss Diagrams; Summary.

**Interfaces:**
- Produces: `docs/extraction-notes/bittman-ch01-option-market-fundamentals.md` (consumed by Tasks 27–34)

- [ ] Step 1: Read physical pages 24–38 (15 pp.)
- [ ] Step 2: Read physical pages 39–52 (14 pp.)
- [ ] Step 3: Write the extraction note. Start with `Source: Bittman, *Trading Options as a Professional*, Chapter 1 "Option Market Fundamentals", printed pp. 1–29.` Then one subsection per section heading found, covering: term definitions, the option-quoting/trading mechanics described, margin-account rules, and profit/loss diagram construction — each tagged with the printed page number it came from.
- [ ] Step 4: Re-scan the two page ranges and confirm every section heading actually present in the text (not just the ones listed above) has a corresponding subsection. Add anything missed.
- [ ] Step 5: Commit

```bash
git add "docs/extraction-notes/bittman-ch01-option-market-fundamentals.md"
git commit -m "docs: extract Bittman ch.1 notes — Option Market Fundamentals"
```

### Task 2: Extract Bittman Ch.2 — Operating the Op-Eval Pro Software

**Files:**
- Create: `docs/extraction-notes/bittman-ch02-operating-op-eval-pro-software.md`

**Source:** Bittman, Chapter 2, printed pp. 31–48 (physical pp. 54–71, 18 pp.). Known headings: Overview of Program Features; Installing the Software; Choices of Pricing Formulas; Features of Op-Eval Pro; The Single Option Calculator; Calculating Implied Volatility; The Spread Positions Screen; Theoretical Graph Screen; Theoretical Price Table; The Portfolio Screen; The Distribution Screen; Summary.

**Interfaces:**
- Produces: `docs/extraction-notes/bittman-ch02-operating-op-eval-pro-software.md`

- [ ] Step 1: Read physical pages 54–71 (18 pp.)
- [ ] Step 2: Write the extraction note with `Source:` header. This chapter documents a bundled software tool (Op-Eval Pro) rather than trading concepts — capture what each screen/feature computes (e.g., what the Spread Positions screen calculates, what the Distribution screen shows) since the underlying analytical concepts (implied volatility calculation, theoretical pricing, portfolio Greeks) are reusable even though the specific software isn't. Note explicitly which parts are software-mechanics-only vs. reusable concepts.
- [ ] Step 3: Re-scan the page range and confirm every heading present has a corresponding subsection.
- [ ] Step 4: Commit

```bash
git add "docs/extraction-notes/bittman-ch02-operating-op-eval-pro-software.md"
git commit -m "docs: extract Bittman ch.2 notes — Operating the Op-Eval Pro Software"
```

### Task 3: Extract Bittman Ch.3 — The Basics of Option Price Behavior

**Files:**
- Create: `docs/extraction-notes/bittman-ch03-basics-of-option-price-behavior.md`

**Source:** Bittman, Chapter 3, printed pp. 49–75 (physical pp. 72–98, 27 pp.). Known headings: The Insurance Analogy; Option Pricing Formulas; Call Values and Stock Prices; Put Values and Stock Prices; Call Values Relative to Put Values; Option Values and Strike Price; Option Values and Time to Expiration; Time Decay Is Complicated; Time Decay and Volatility; Option Values and Interest Rates; Option Values and Dividends; Option Values and Volatility; Extreme Volatility; Dynamic Markets; Three-Part Forecasts; Trading Scenarios; Summary.

**Interfaces:**
- Produces: `docs/extraction-notes/bittman-ch03-basics-of-option-price-behavior.md`

- [ ] Step 1: Read physical pages 72–85 (14 pp.)
- [ ] Step 2: Read physical pages 86–98 (13 pp.)
- [ ] Step 3: Write the extraction note with `Source:` header, one subsection per heading, including all pricing formulas verbatim and the worked "Trading Scenarios" examples in full.
- [ ] Step 4: Re-scan both ranges and confirm every heading present has a corresponding subsection.
- [ ] Step 5: Commit

```bash
git add "docs/extraction-notes/bittman-ch03-basics-of-option-price-behavior.md"
git commit -m "docs: extract Bittman ch.3 notes — The Basics of Option Price Behavior"
```

### Task 4: Extract Bittman Ch.4 — The Greeks

**Files:**
- Create: `docs/extraction-notes/bittman-ch04-the-greeks.md`

**Source:** Bittman, Chapter 4, printed pp. 77–131 (physical pp. 100–154, 55 pp. — the book's longest chapter). Known headings: Overview; Delta; Gamma; Vega; Theta; Rho; How the Greeks Change (How Delta/Gamma/Vega/Theta/Rho Changes); Position Greeks; Summary.

**Interfaces:**
- Produces: `docs/extraction-notes/bittman-ch04-the-greeks.md` — this is a primary source for `greeks-and-volatility.md` (Task 27)

- [ ] Step 1: Read physical pages 100–118 (19 pp.)
- [ ] Step 2: Read physical pages 119–137 (19 pp.)
- [ ] Step 3: Read physical pages 138–154 (17 pp.)
- [ ] Step 4: Write the extraction note with `Source:` header. Give each Greek (delta, gamma, vega, theta, rho) its own subsection: definition, formula, sign conventions for long/short calls/puts, and how it behaves as price/time/volatility change (the "How X Changes" material). Add a Position Greeks subsection covering how individual-option Greeks combine into position-level Greeks.
- [ ] Step 5: Re-scan all three ranges and confirm every heading present has a corresponding subsection.
- [ ] Step 6: Commit

```bash
git add "docs/extraction-notes/bittman-ch04-the-greeks.md"
git commit -m "docs: extract Bittman ch.4 notes — The Greeks"
```

### Task 5: Extract Bittman Ch.5 — Synthetic Relationships

**Files:**
- Create: `docs/extraction-notes/bittman-ch05-synthetic-relationships.md`

**Source:** Bittman, Chapter 5, printed pp. 135–160 (physical pp. 158–183, 26 pp.). Known headings: Synthetic Relationships; Synthetic Long Stock; Synthetic Short Stock; Synthetic Long Call; Synthetic Short Call; Synthetic Long Put; Synthetic Short Put; When Stock Price = Strike Price; The Put-Call Parity Equation; Applying the Effective Stock Price Concept; The Role of Interest Rates and Dividends; Summary.

**Interfaces:**
- Produces: `docs/extraction-notes/bittman-ch05-synthetic-relationships.md`

- [ ] Step 1: Read physical pages 158–170 (13 pp.)
- [ ] Step 2: Read physical pages 171–183 (13 pp.)
- [ ] Step 3: Write the extraction note with `Source:` header. Capture every synthetic equivalence exactly as given (e.g., synthetic long stock = long call + short put) along with the put-call parity equation and effective stock price concept.
- [ ] Step 4: Re-scan both ranges and confirm every heading present has a corresponding subsection.
- [ ] Step 5: Commit

```bash
git add "docs/extraction-notes/bittman-ch05-synthetic-relationships.md"
git commit -m "docs: extract Bittman ch.5 notes — Synthetic Relationships"
```

### Task 6: Extract Bittman Ch.6 — Arbitrage Strategies

**Files:**
- Create: `docs/extraction-notes/bittman-ch06-arbitrage-strategies.md`

**Source:** Bittman, Chapter 6, printed pp. 163–203 (physical pp. 186–226, 41 pp.). Known headings: Arbitrage—the Concept; The Conversion; Pin Risk; Pricing a Conversion (with and without Dividends); Pricing Conversions by Strike Price; The Concept of Relative Pricing; The Reverse Conversion; Pricing a Reverse Conversion (with Dividends); Box Spreads (Long and Short); Pricing a Long/Short Box Spread; Summary.

**Interfaces:**
- Produces: `docs/extraction-notes/bittman-ch06-arbitrage-strategies.md`

- [ ] Step 1: Read physical pages 186–199 (14 pp.)
- [ ] Step 2: Read physical pages 200–213 (14 pp.)
- [ ] Step 3: Read physical pages 214–226 (13 pp.)
- [ ] Step 4: Write the extraction note with `Source:` header, one subsection per strategy (conversion, reverse conversion, long box, short box) including full pricing mechanics and pin risk discussion.
- [ ] Step 5: Re-scan all three ranges and confirm every heading present has a corresponding subsection.
- [ ] Step 6: Commit

```bash
git add "docs/extraction-notes/bittman-ch06-arbitrage-strategies.md"
git commit -m "docs: extract Bittman ch.6 notes — Arbitrage Strategies"
```

### Task 7: Extract Bittman Ch.7 — Volatility

**Files:**
- Create: `docs/extraction-notes/bittman-ch07-volatility.md`

**Source:** Bittman, Chapter 7, printed pp. 205–238 (physical pp. 228–261, 34 pp.). Known headings: Volatility Defined; Historic Volatility; Another Look at Daily Returns; Realized Volatility; The Meaning of "30 Percent Volatility"; Converting Annual Volatility to Different Time Periods; Calendar Days Versus Trading Days; Implied Volatility; Expected Volatility; Using Volatility; "Overvalued" and "Undervalued"; An Alternative Focus; Volatility Skews; Summary.

**Interfaces:**
- Produces: `docs/extraction-notes/bittman-ch07-volatility.md` — primary source for `greeks-and-volatility.md` (Task 27)

- [ ] Step 1: Read physical pages 228–244 (17 pp.)
- [ ] Step 2: Read physical pages 245–261 (17 pp.)
- [ ] Step 3: Write the extraction note with `Source:` header, capturing formulas for historic/realized volatility, the annualization conversions, implied vs. expected volatility distinctions, and the volatility skew discussion in full.
- [ ] Step 4: Re-scan both ranges and confirm every heading present has a corresponding subsection.
- [ ] Step 5: Commit

```bash
git add "docs/extraction-notes/bittman-ch07-volatility.md"
git commit -m "docs: extract Bittman ch.7 notes — Volatility"
```

### Task 8: Extract Bittman Ch.8 — Delta-Neutral Trading: Theory and Reality

**Files:**
- Create: `docs/extraction-notes/bittman-ch08-delta-neutral-trading.md`

**Source:** Bittman, Chapter 8, printed pp. 241–277 (physical pp. 264–300, 37 pp.). Known headings: Delta-Neutral Defined; The Theory of Delta-Neutral Trading; Delta-Neutral Trading—Long Volatility Example; Delta-Neutral Trading—Short Volatility Example; Simulated "Real" Delta-Neutral Trade 1 and 2; Delta-Neutral Trading—Opportunities and Risks for Speculators; Delta-Neutral Trading—Opportunities and Risks for Market Makers; Summary.

**Interfaces:**
- Produces: `docs/extraction-notes/bittman-ch08-delta-neutral-trading.md`

- [ ] Step 1: Read physical pages 264–282 (19 pp.)
- [ ] Step 2: Read physical pages 283–300 (18 pp.)
- [ ] Step 3: Write the extraction note with `Source:` header. Reproduce both simulated trade examples in full (entry, adjustments, outcome) since these are the chapter's core teaching device.
- [ ] Step 4: Re-scan both ranges and confirm every heading present has a corresponding subsection.
- [ ] Step 5: Commit

```bash
git add "docs/extraction-notes/bittman-ch08-delta-neutral-trading.md"
git commit -m "docs: extract Bittman ch.8 notes — Delta-Neutral Trading"
```

### Task 9: Extract Bittman Ch.9 — Setting Bid-Ask Prices

**Files:**
- Create: `docs/extraction-notes/bittman-ch09-setting-bid-ask-prices.md`

**Source:** Bittman, Chapter 9, printed pp. 279–310 (physical pp. 302–333, 32 pp.). Known headings: The Theory of the Bid-Ask Spread; The Need to Adjust Bid and Ask Prices; The Process of Adjusting Bid and Ask Prices; The Limit on Adjusting Bid and Ask Prices; Estimating Option Prices as Volatility Changes; Expressing Bid and Ask Prices in Volatility Terms; Trading Exercises Introduced (Exercises 1–4); Summary.

**Interfaces:**
- Produces: `docs/extraction-notes/bittman-ch09-setting-bid-ask-prices.md` — primary source for `market-making-techniques.md` (Task 31)

- [ ] Step 1: Read physical pages 302–317 (16 pp.)
- [ ] Step 2: Read physical pages 318–333 (16 pp.)
- [ ] Step 3: Write the extraction note with `Source:` header, including all four trading exercises in full (setup, trades, resolution).
- [ ] Step 4: Re-scan both ranges and confirm every heading present has a corresponding subsection.
- [ ] Step 5: Commit

```bash
git add "docs/extraction-notes/bittman-ch09-setting-bid-ask-prices.md"
git commit -m "docs: extract Bittman ch.9 notes — Setting Bid-Ask Prices"
```

### Task 10: Extract Bittman Ch.10 — Managing Position Risk (+ Epilogue)

**Files:**
- Create: `docs/extraction-notes/bittman-ch10-managing-position-risk.md`

**Source:** Bittman, Chapter 10, printed pp. 311–340 (physical pp. 334–363, 30 pp.) plus the one-page Epilogue (printed p. 343, physical p. 366). Known headings: Calculating Position Risks; Managing Directional Risk with Delta; Vertical Spreads versus Outright Long Options; Vertical Spreads—How the Risks Change; Greeks of Delta-Neutral Positions; Neutralizing Position Greeks; Neutralizing Greeks when Interest Rates Are Positive; Establishing Risk Limits; Summary.

**Interfaces:**
- Produces: `docs/extraction-notes/bittman-ch10-managing-position-risk.md` — primary source for `risk-management-and-position-sizing.md` (Task 32)

- [ ] Step 1: Read physical pages 334–348 (15 pp.)
- [ ] Step 2: Read physical pages 349–363 (15 pp.)
- [ ] Step 3: Read physical page 366 (Epilogue, 1 pp.)
- [ ] Step 4: Write the extraction note with `Source:` header for Chapter 10, plus a short final "Epilogue" subsection summarizing the book's closing remarks.
- [ ] Step 5: Re-scan all three ranges and confirm every heading present has a corresponding subsection.
- [ ] Step 6: Commit

```bash
git add "docs/extraction-notes/bittman-ch10-managing-position-risk.md"
git commit -m "docs: extract Bittman ch.10 notes — Managing Position Risk + Epilogue"
```

### Task 11: Extract Chen/Sebastian Ch.1 — The Insurance Business

**Files:**
- Create: `docs/extraction-notes/chen-ch01-the-insurance-business.md`

**Source:** Chen/Sebastian, Chapter 1, physical pp. 22–36 (15 pp.). Known headings: How Insurance Companies Make Money; How Insurance Companies Lose Money; Success Drivers of the Insurance Business.

**Interfaces:**
- Produces: `docs/extraction-notes/chen-ch01-the-insurance-business.md` — primary source for `trading-business-framework.md` (Task 33)

- [ ] Step 1: Read physical pages 22–36 (15 pp.)
- [ ] Step 2: Write the extraction note with `Source:` header. Capture the insurance-company value chain and how it's mapped onto "The One Man Insurance Company" (TOMIC) framing — this analogy underlies the rest of the book.
- [ ] Step 3: Re-scan the range and confirm every heading present has a corresponding subsection.
- [ ] Step 4: Commit

```bash
git add "docs/extraction-notes/chen-ch01-the-insurance-business.md"
git commit -m "docs: extract Chen/Sebastian ch.1 notes — The Insurance Business"
```

### Task 12: Extract Chen/Sebastian Ch.2 — Trade Selection

**Files:**
- Create: `docs/extraction-notes/chen-ch02-trade-selection.md`

**Source:** Chen/Sebastian, Chapter 2, physical pp. 37–49 (13 pp.). Known headings: Market Selection; Strategy Selection; Time Frame; Volatility; Pricing; Endnote.

**Interfaces:**
- Produces: `docs/extraction-notes/chen-ch02-trade-selection.md`

- [ ] Step 1: Read physical pages 37–49 (13 pp.)
- [ ] Step 2: Write the extraction note with `Source:` header, including the specific index/ETF/equity examples given for market selection (e.g., which underlyings are named as suitable).
- [ ] Step 3: Re-scan the range and confirm every heading present has a corresponding subsection.
- [ ] Step 4: Commit

```bash
git add "docs/extraction-notes/chen-ch02-trade-selection.md"
git commit -m "docs: extract Chen/Sebastian ch.2 notes — Trade Selection"
```

### Task 13: Extract Chen/Sebastian Ch.3 — Risk Management

**Files:**
- Create: `docs/extraction-notes/chen-ch03-risk-management.md`

**Source:** Chen/Sebastian, Chapter 3, physical pp. 50–59 (10 pp.). Known headings: Risk Management; Money Management; Position Sizing; Portfolio Diversification; Adjusting the Different Trades; Addressable Risks; Insuring the Portfolio Against Black Swan Events.

**Interfaces:**
- Produces: `docs/extraction-notes/chen-ch03-risk-management.md` — primary source for `risk-management-and-position-sizing.md` (Task 32)

- [ ] Step 1: Read physical pages 50–59 (10 pp.)
- [ ] Step 2: Write the extraction note with `Source:` header, capturing position-sizing rules and black-swan protection guidance verbatim where formulaic.
- [ ] Step 3: Re-scan the range and confirm every heading present has a corresponding subsection.
- [ ] Step 4: Commit

```bash
git add "docs/extraction-notes/chen-ch03-risk-management.md"
git commit -m "docs: extract Chen/Sebastian ch.3 notes — Risk Management"
```

### Task 14: Extract Chen/Sebastian Ch.4 — Trade Execution

**Files:**
- Create: `docs/extraction-notes/chen-ch04-trade-execution.md`

**Source:** Chen/Sebastian, Chapter 4, physical pp. 60–71 (12 pp.). Known headings: Conditions of the Market; Evaluate Potential Realized Volatility; Evaluate Implied Volatility; Evaluate the Months; Evaluate the Skew; Evaluate Other Products; Trade Order Entry.

**Interfaces:**
- Produces: `docs/extraction-notes/chen-ch04-trade-execution.md`

- [ ] Step 1: Read physical pages 60–71 (12 pp.)
- [ ] Step 2: Write the extraction note with `Source:` header, one subsection per evaluation criterion listed, plus order-entry mechanics.
- [ ] Step 3: Re-scan the range and confirm every heading present has a corresponding subsection.
- [ ] Step 4: Commit

```bash
git add "docs/extraction-notes/chen-ch04-trade-execution.md"
git commit -m "docs: extract Chen/Sebastian ch.4 notes — Trade Execution"
```

### Task 15: Extract Chen/Sebastian Ch.5 — The Trading Plan

**Files:**
- Create: `docs/extraction-notes/chen-ch05-the-trading-plan.md`

**Source:** Chen/Sebastian, Chapter 5, physical pp. 72–79 (8 pp.). Known headings: The Mind-Set; The Importance of Sticking to the Process; Questions Your Trading Plan Should Answer; Endnotes.

**Interfaces:**
- Produces: `docs/extraction-notes/chen-ch05-the-trading-plan.md` — primary source for `trading-business-framework.md` (Task 33)

- [ ] Step 1: Read physical pages 72–79 (8 pp.)
- [ ] Step 2: Write the extraction note with `Source:` header. Reproduce the trading-plan question checklist in full — it's directly reusable.
- [ ] Step 3: Re-scan the range and confirm every heading present has a corresponding subsection.
- [ ] Step 4: Commit

```bash
git add "docs/extraction-notes/chen-ch05-the-trading-plan.md"
git commit -m "docs: extract Chen/Sebastian ch.5 notes — The Trading Plan"
```

### Task 16: Extract Chen/Sebastian Ch.6 — Trading Infrastructure

**Files:**
- Create: `docs/extraction-notes/chen-ch06-trading-infrastructure.md`

**Source:** Chen/Sebastian, Chapter 6, physical pp. 80–87 (8 pp.). Known headings: Risk Capital; The Trading Platform (Broker); Portfolio Margin; Information Resources and Other Analytical Tools; Dedicated Space; Backup Plans.

**Interfaces:**
- Produces: `docs/extraction-notes/chen-ch06-trading-infrastructure.md`

- [ ] Step 1: Read physical pages 80–87 (8 pp.)
- [ ] Step 2: Write the extraction note with `Source:` header, including the specific broker/tool selection criteria given.
- [ ] Step 3: Re-scan the range and confirm every heading present has a corresponding subsection.
- [ ] Step 4: Commit

```bash
git add "docs/extraction-notes/chen-ch06-trading-infrastructure.md"
git commit -m "docs: extract Chen/Sebastian ch.6 notes — Trading Infrastructure"
```

### Task 17: Extract Chen/Sebastian Ch.7 — Learning Processes

**Files:**
- Create: `docs/extraction-notes/chen-ch07-learning-processes.md`

**Source:** Chen/Sebastian, Chapter 7, physical pp. 88–96 (9 pp.). Known headings: The Trading Journal; Sounding Board; Endnote.

**Interfaces:**
- Produces: `docs/extraction-notes/chen-ch07-learning-processes.md` — primary source for `trading-business-framework.md` (Task 33)

- [ ] Step 1: Read physical pages 88–96 (9 pp.)
- [ ] Step 2: Write the extraction note with `Source:` header, capturing the specific trading-journal metrics/fields recommended (e.g., win rate, annualized yield formula).
- [ ] Step 3: Re-scan the range and confirm every heading present has a corresponding subsection.
- [ ] Step 4: Commit

```bash
git add "docs/extraction-notes/chen-ch07-learning-processes.md"
git commit -m "docs: extract Chen/Sebastian ch.7 notes — Learning Processes"
```

### Task 18: Extract Chen/Sebastian Ch.8 — Understanding Volatility

**Files:**
- Create: `docs/extraction-notes/chen-ch08-understanding-volatility.md`

**Source:** Chen/Sebastian, Chapter 8, physical pp. 97–104 (8 pp.). Known headings: What Causes Volatility?; Three-Dimensional Volatility and the Model.

**Interfaces:**
- Produces: `docs/extraction-notes/chen-ch08-understanding-volatility.md` — primary source for `greeks-and-volatility.md` (Task 27)

- [ ] Step 1: Read physical pages 97–104 (8 pp.)
- [ ] Step 2: Write the extraction note with `Source:` header, capturing the "three-dimensional volatility" model in full since it's this book's distinct volatility framework (distinct from Bittman's).
- [ ] Step 3: Re-scan the range and confirm every heading present has a corresponding subsection.
- [ ] Step 4: Commit

```bash
git add "docs/extraction-notes/chen-ch08-understanding-volatility.md"
git commit -m "docs: extract Chen/Sebastian ch.8 notes — Understanding Volatility"
```

### Task 19: Extract Chen/Sebastian Ch.9 — Most Used Strategies

**Files:**
- Create: `docs/extraction-notes/chen-ch09-most-used-strategies.md`

**Source:** Chen/Sebastian, Chapter 9, physical pp. 105–147 (43 pp. — this book's longest chapter). Known headings: The Vertical Spread; The Iron Condor; The ATM Iron Butterfly; The Calendar Spread or Time Spread; The Ratio Back and Front Spread; Endnote.

**Interfaces:**
- Produces: `docs/extraction-notes/chen-ch09-most-used-strategies.md` — primary source for `spreads-and-combinations.md` (Task 29) and `income-strategies.md` (Task 28)

- [ ] Step 1: Read physical pages 105–119 (15 pp.)
- [ ] Step 2: Read physical pages 120–133 (14 pp.)
- [ ] Step 3: Read physical pages 134–147 (14 pp.)
- [ ] Step 4: Write the extraction note with `Source:` header. Give each of the five strategies its own subsection: construction, entry criteria, greeks profile, management/adjustment rules, and exit criteria as given in the text.
- [ ] Step 5: Re-scan all three ranges and confirm every heading present has a corresponding subsection.
- [ ] Step 6: Commit

```bash
git add "docs/extraction-notes/chen-ch09-most-used-strategies.md"
git commit -m "docs: extract Chen/Sebastian ch.9 notes — Most Used Strategies"
```

### Task 20: Extract Chen/Sebastian Ch.10 — Operating the Business: TOMIC 1.0 A to Z

**Files:**
- Create: `docs/extraction-notes/chen-ch10-operating-the-business-tomic.md`

**Source:** Chen/Sebastian, Chapter 10, physical pp. 148–157 (10 pp.). Known headings: Trading Plan; Executing the Trading Plan.

**Interfaces:**
- Produces: `docs/extraction-notes/chen-ch10-operating-the-business-tomic.md` — primary source for `trading-business-framework.md` (Task 33)

- [ ] Step 1: Read physical pages 148–157 (10 pp.)
- [ ] Step 2: Write the extraction note with `Source:` header. This chapter is an end-to-end walkthrough tying together Chapters 1–9 — capture it as a sequential checklist/process, not a topic list.
- [ ] Step 3: Re-scan the range and confirm every heading present has a corresponding subsection.
- [ ] Step 4: Commit

```bash
git add "docs/extraction-notes/chen-ch10-operating-the-business-tomic.md"
git commit -m "docs: extract Chen/Sebastian ch.10 notes — Operating the Business"
```

### Task 21: Extract Chen/Sebastian Ch.11 — Lessons from the Trading Floor on Volatility

**Files:**
- Create: `docs/extraction-notes/chen-ch11-lessons-volatility.md`

**Source:** Chen/Sebastian, Chapter 11, physical pp. 158–173 (16 pp.). Known headings: Understanding Weighted Vegas in SPX Index Options; Taking on the Skew; Four Tips When the VIX Cash Is Depressed; How to Find and Track Volatility Skew; SPX Skew: It's All Relative; Understanding Implied Volatility in Iron Condors; The Stages of Skew.

**Interfaces:**
- Produces: `docs/extraction-notes/chen-ch11-lessons-volatility.md` — primary source for `greeks-and-volatility.md` (Task 27)

- [ ] Step 1: Read physical pages 158–173 (16 pp.)
- [ ] Step 2: Write the extraction note with `Source:` header. This chapter is a set of standalone blog-post-style lessons — give each its own subsection named after its heading, since they don't build on each other sequentially.
- [ ] Step 3: Re-scan the range and confirm every heading present has a corresponding subsection.
- [ ] Step 4: Commit

```bash
git add "docs/extraction-notes/chen-ch11-lessons-volatility.md"
git commit -m "docs: extract Chen/Sebastian ch.11 notes — Lessons on Volatility"
```

### Task 22: Extract Chen/Sebastian Ch.12 — Lessons from the Trading Floor on Risk Management

**Files:**
- Create: `docs/extraction-notes/chen-ch12-lessons-risk-management.md`

**Source:** Chen/Sebastian, Chapter 12, physical pp. 174–182 (9 pp.). Known headings: Cash Is a Position; The Card Game Value; Why Are Option Trading Hands So Hard to Sit On?; How Option Time Value Premium Decays over the Weekend; When Is the Time to De-risk Your Portfolio?; How to Trade When You Go on Vacation.

**Interfaces:**
- Produces: `docs/extraction-notes/chen-ch12-lessons-risk-management.md` — primary source for `risk-management-and-position-sizing.md` (Task 32)

- [ ] Step 1: Read physical pages 174–182 (9 pp.)
- [ ] Step 2: Write the extraction note with `Source:` header, one subsection per lesson, including the "Card Game Value" concept in full (it's a distinctive risk-sizing heuristic from this book).
- [ ] Step 3: Re-scan the range and confirm every heading present has a corresponding subsection.
- [ ] Step 4: Commit

```bash
git add "docs/extraction-notes/chen-ch12-lessons-risk-management.md"
git commit -m "docs: extract Chen/Sebastian ch.12 notes — Lessons on Risk Management"
```

### Task 23: Extract Chen/Sebastian Ch.13 — Lessons from the Trading Floor on Trading and Execution

**Files:**
- Create: `docs/extraction-notes/chen-ch13-lessons-trading-execution.md`

**Source:** Chen/Sebastian, Chapter 13, physical pp. 183–200 (18 pp.). Known headings: What Everybody Should Know About Payment for Order Flow; When Should You Worry About Assignment?; A Successful Short SPX Calendar; Butterfly Trading Checklist; What Is the Proper Width for an Index Butterfly's Wings?; The Importance of Good Exits; Preparing to Trade for a Living, How Much Capital Is Needed?; The Importance of Focus.

**Interfaces:**
- Produces: `docs/extraction-notes/chen-ch13-lessons-trading-execution.md` — primary source for `market-making-techniques.md` (Task 31) and `spreads-and-combinations.md` (Task 29, butterfly checklist)

- [ ] Step 1: Read physical pages 183–200 (18 pp.)
- [ ] Step 2: Write the extraction note with `Source:` header. Reproduce the "Butterfly Trading Checklist" as a literal checklist and the capital-needed-to-trade-for-a-living figures/reasoning in full.
- [ ] Step 3: Re-scan the range and confirm every heading present has a corresponding subsection.
- [ ] Step 4: Commit

```bash
git add "docs/extraction-notes/chen-ch13-lessons-trading-execution.md"
git commit -m "docs: extract Chen/Sebastian ch.13 notes — Lessons on Trading and Execution"
```

### Task 24: Extract Chen/Sebastian Ch.14 — Lessons from the Trading Floor on the Other Greeks

**Files:**
- Create: `docs/extraction-notes/chen-ch14-lessons-other-greeks.md`

**Source:** Chen/Sebastian, Chapter 14, physical pp. 201–221 (21 pp.). Known headings: What Happens to the Gamma of ITM or OTM Options When IV Increases?; Why Do I Need to Weight My Option Portfolio?; Gamma Scalping.

**Interfaces:**
- Produces: `docs/extraction-notes/chen-ch14-lessons-other-greeks.md` — primary source for `greeks-and-volatility.md` (Task 27)

- [ ] Step 1: Read physical pages 201–211 (11 pp.)
- [ ] Step 2: Read physical pages 212–221 (10 pp.)
- [ ] Step 3: Write the extraction note with `Source:` header, capturing the "weighted vega" concept (introduced in Ch.11 but revisited here) and the gamma-scalping mechanics in full.
- [ ] Step 4: Re-scan both ranges and confirm every heading present has a corresponding subsection.
- [ ] Step 5: Commit

```bash
git add "docs/extraction-notes/chen-ch14-lessons-other-greeks.md"
git commit -m "docs: extract Chen/Sebastian ch.14 notes — Lessons on the Other Greeks"
```

### Task 25: Extract Chen/Sebastian Ch.15 — The Beginning

**Files:**
- Create: `docs/extraction-notes/chen-ch15-the-beginning.md`

**Source:** Chen/Sebastian, Chapter 15, physical pp. 222–224 (3 pp.). Closing/conclusion chapter, no subheadings.

**Interfaces:**
- Produces: `docs/extraction-notes/chen-ch15-the-beginning.md`

- [ ] Step 1: Read physical pages 222–224 (3 pp.)
- [ ] Step 2: Write a short extraction note with `Source:` header summarizing the closing framing (this is a conclusion, not new technical content — a few sentences is sufficient, but don't skip it since completeness includes closing caveats/disclaimers if any appear).
- [ ] Step 3: Commit

```bash
git add "docs/extraction-notes/chen-ch15-the-beginning.md"
git commit -m "docs: extract Chen/Sebastian ch.15 notes — The Beginning"
```

### Task 26: Extract Chen/Sebastian Appendices A–D

**Files:**
- Create: `docs/extraction-notes/chen-appendices.md`

**Source:** Chen/Sebastian, Appendices, physical pp. 225–235 (11 pp.). A: Recommended Reading. B: Strategy Learning Sequence. C: OptionPit.com. D: Kite Spread.

**Interfaces:**
- Produces: `docs/extraction-notes/chen-appendices.md` — Appendix D is a primary source for `spreads-and-combinations.md` (Task 29); Appendix B informs `SKILL.md` sequencing guidance (Task 35)

- [ ] Step 1: Read physical pages 225–235 (11 pp.)
- [ ] Step 2: Write the extraction note with `Source:` header, one subsection per appendix. For Appendix D (Kite Spread), capture the full construction and risk profile — it's a real strategy, not meta-content. For Appendix B, reproduce the recommended strategy-learning sequence table. Appendices A and C (book recommendations, author's commercial service) can be captured briefly — they're bibliographic/promotional, not trading content.
- [ ] Step 3: Re-scan the range and confirm every heading present has a corresponding subsection.
- [ ] Step 4: Commit

```bash
git add "docs/extraction-notes/chen-appendices.md"
git commit -m "docs: extract Chen/Sebastian appendices A-D"
```

---

# Phase 2: Synthesis (8 tasks)

Each synthesis task reads **all 26 extraction notes** (`docs/extraction-notes/*.md`) and pulls everything relevant to its one topic, regardless of which book or chapter it came from. All Phase 1 tasks must be complete before Phase 2 starts.

### Task 27: Synthesize `greeks-and-volatility.md`

**Files:**
- Create: `.claude/skills/options-playbook/references/greeks-and-volatility.md`

**Interfaces:**
- Consumes: all files in `docs/extraction-notes/*.md` (primarily `bittman-ch03`, `bittman-ch04`, `bittman-ch07`, `bittman-ch08`, `chen-ch08`, `chen-ch11`, `chen-ch14`)
- Produces: `.claude/skills/options-playbook/references/greeks-and-volatility.md` (referenced by `SKILL.md`, Task 35)

- [ ] Step 1: Read every file in `docs/extraction-notes/`
- [ ] Step 2: Write `.claude/skills/options-playbook/references/greeks-and-volatility.md` covering: delta/gamma/vega/theta/rho mechanics and formulas; historic vs. realized vs. implied vs. expected volatility; annualization conversions; volatility skew (including the "three-dimensional volatility" model and SPX-specific skew lessons); weighted vega; gamma scalping. Organize by subtopic, not by source chapter. Where Bittman and Chen/Sebastian frame the same concept differently (e.g., volatility skew), present both framings with attribution (`Per Bittman, ...` / `Per Chen/Sebastian, ...`).
- [ ] Step 3: Confirm every greeks/volatility-related item flagged across the 26 extraction notes appears somewhere in this file (skim each note's headings once more).
- [ ] Step 4: Commit

```bash
git add ".claude/skills/options-playbook/references/greeks-and-volatility.md"
git commit -m "docs: synthesize greeks-and-volatility reference"
```

### Task 28: Synthesize `income-strategies.md`

**Files:**
- Create: `.claude/skills/options-playbook/references/income-strategies.md`

**Interfaces:**
- Consumes: all files in `docs/extraction-notes/*.md` (primarily `chen-ch02`, `chen-ch09`, `bittman-ch05`)
- Produces: `.claude/skills/options-playbook/references/income-strategies.md`

- [ ] Step 1: Read every file in `docs/extraction-notes/`
- [ ] Step 2: Write `.claude/skills/options-playbook/references/income-strategies.md` covering premium-selling/credit strategies used for income: credit spreads and iron condors as covered in Chen/Sebastian's "Most Used Strategies," the underwriting/pricing framing from "Trade Selection," and the synthetic equivalence between a covered call and a short put (from Bittman's synthetic relationships) since that equivalence is directly relevant to income-strategy selection. Note explicitly that neither book has a dedicated "covered call" or "cash-secured put" chapter — this doc synthesizes the income-generating angle across both books' actual content rather than forcing a chapter that doesn't exist.
- [ ] Step 3: Confirm nothing income-relevant across the 26 notes was missed.
- [ ] Step 4: Commit

```bash
git add ".claude/skills/options-playbook/references/income-strategies.md"
git commit -m "docs: synthesize income-strategies reference"
```

### Task 29: Synthesize `spreads-and-combinations.md`

**Files:**
- Create: `.claude/skills/options-playbook/references/spreads-and-combinations.md`

**Interfaces:**
- Consumes: all files in `docs/extraction-notes/*.md` (primarily `chen-ch09`, `chen-ch13`, `chen-appendices`, `bittman-ch06`, `bittman-ch10`)
- Produces: `.claude/skills/options-playbook/references/spreads-and-combinations.md`

- [ ] Step 1: Read every file in `docs/extraction-notes/`
- [ ] Step 2: Write `.claude/skills/options-playbook/references/spreads-and-combinations.md` covering: vertical spreads (both books), iron condors, ATM iron butterflies (plus the full Butterfly Trading Checklist from Chen ch.13 and the index-butterfly-wing-width guidance), calendar/time spreads, ratio back/front spreads, the kite spread (Appendix D), and Bittman's box spreads / conversions / reverse conversions as the arbitrage-oriented combination strategies. Give each strategy: construction, greeks profile, entry criteria, management/adjustment, and exit criteria.
- [ ] Step 3: Confirm nothing spread/combination-relevant across the 26 notes was missed.
- [ ] Step 4: Commit

```bash
git add ".claude/skills/options-playbook/references/spreads-and-combinations.md"
git commit -m "docs: synthesize spreads-and-combinations reference"
```

### Task 30: Synthesize `directional-strategies.md`

**Files:**
- Create: `.claude/skills/options-playbook/references/directional-strategies.md`

**Interfaces:**
- Consumes: all files in `docs/extraction-notes/*.md` (primarily `bittman-ch01`, `bittman-ch03`, `bittman-ch05`)
- Produces: `.claude/skills/options-playbook/references/directional-strategies.md`

- [ ] Step 1: Read every file in `docs/extraction-notes/`
- [ ] Step 2: Write `.claude/skills/options-playbook/references/directional-strategies.md` covering outright long calls/puts (P&L diagrams and pricing behavior from Bittman ch.1/ch.3) and synthetic long/short stock and long/short call/put positions (Bittman ch.5) as the directional-exposure toolkit. Note where Chen/Sebastian's "Trade Selection" market/direction criteria apply to choosing a directional trade.
- [ ] Step 3: Confirm nothing directional-strategy-relevant across the 26 notes was missed.
- [ ] Step 4: Commit

```bash
git add ".claude/skills/options-playbook/references/directional-strategies.md"
git commit -m "docs: synthesize directional-strategies reference"
```

### Task 31: Synthesize `market-making-techniques.md`

**Files:**
- Create: `.claude/skills/options-playbook/references/market-making-techniques.md`

**Interfaces:**
- Consumes: all files in `docs/extraction-notes/*.md` (primarily `bittman-ch09`, `bittman-ch02`, `chen-ch13`)
- Produces: `.claude/skills/options-playbook/references/market-making-techniques.md`

- [ ] Step 1: Read every file in `docs/extraction-notes/`
- [ ] Step 2: Write `.claude/skills/options-playbook/references/market-making-techniques.md` covering bid-ask spread theory, the process/limits of adjusting bid and ask prices, expressing prices in volatility terms, the four trading exercises from Bittman ch.9, the Op-Eval Pro analytical concepts from ch.2 (implied volatility calculation, theoretical pricing — flagged as concept, not software instructions), and payment-for-order-flow mechanics from Chen ch.13.
- [ ] Step 3: Confirm nothing market-making-relevant across the 26 notes was missed.
- [ ] Step 4: Commit

```bash
git add ".claude/skills/options-playbook/references/market-making-techniques.md"
git commit -m "docs: synthesize market-making-techniques reference"
```

### Task 32: Synthesize `risk-management-and-position-sizing.md`

**Files:**
- Create: `.claude/skills/options-playbook/references/risk-management-and-position-sizing.md`

**Interfaces:**
- Consumes: all files in `docs/extraction-notes/*.md` (primarily `bittman-ch10`, `chen-ch03`, `chen-ch12`)
- Produces: `.claude/skills/options-playbook/references/risk-management-and-position-sizing.md`

- [ ] Step 1: Read every file in `docs/extraction-notes/`
- [ ] Step 2: Write `.claude/skills/options-playbook/references/risk-management-and-position-sizing.md` covering: calculating and managing position risk with delta (Bittman ch.10), neutralizing position Greeks and setting risk limits, money management/position sizing/portfolio diversification/black-swan insurance (Chen ch.3), and the trading-floor risk lessons (Cash Is a Position, the Card Game Value heuristic, weekend time-decay risk, when to de-risk, vacation risk management from Chen ch.12).
- [ ] Step 3: Confirm nothing risk-management-relevant across the 26 notes was missed.
- [ ] Step 4: Commit

```bash
git add ".claude/skills/options-playbook/references/risk-management-and-position-sizing.md"
git commit -m "docs: synthesize risk-management-and-position-sizing reference"
```

### Task 33: Synthesize `trading-business-framework.md`

**Files:**
- Create: `.claude/skills/options-playbook/references/trading-business-framework.md`

**Interfaces:**
- Consumes: all files in `docs/extraction-notes/*.md` (primarily `chen-ch01`, `chen-ch05`, `chen-ch06`, `chen-ch07`, `chen-ch10`, `chen-ch15`)
- Produces: `.claude/skills/options-playbook/references/trading-business-framework.md`

- [ ] Step 1: Read every file in `docs/extraction-notes/`
- [ ] Step 2: Write `.claude/skills/options-playbook/references/trading-business-framework.md` covering the "One Man Insurance Company" (TOMIC) business framework end to end: the insurance-business analogy and value chain, the trading plan and its required questions, trading infrastructure requirements (broker, portfolio margin, tools, backup plans), the learning-process feedback loop (trading journal fields, win-rate/annualized-yield calculations), and the full A-to-Z operating walkthrough from Chapter 10. This is entirely Chen/Sebastian-sourced — Bittman's book doesn't cover business-of-trading framing.
- [ ] Step 3: Confirm nothing business-framework-relevant across the 26 notes was missed.
- [ ] Step 4: Commit

```bash
git add ".claude/skills/options-playbook/references/trading-business-framework.md"
git commit -m "docs: synthesize trading-business-framework reference"
```

### Task 34: Synthesize `glossary.md`

**Files:**
- Create: `.claude/skills/options-playbook/references/glossary.md`

**Interfaces:**
- Consumes: all files in `docs/extraction-notes/*.md`
- Produces: `.claude/skills/options-playbook/references/glossary.md`

- [ ] Step 1: Read every file in `docs/extraction-notes/`
- [ ] Step 2: Write `.claude/skills/options-playbook/references/glossary.md` as an alphabetical list of every defined term and named formula across both books (e.g., NBBO, pin risk, delta-neutral, weighted vega, Card Game Value, put-call parity), each with a one-line definition and a pointer to which reference doc (Tasks 27–33) has the full treatment.
- [ ] Step 3: Cross-check against the other seven reference docs (once they exist) to confirm every term used there appears in the glossary.
- [ ] Step 4: Commit

```bash
git add ".claude/skills/options-playbook/references/glossary.md"
git commit -m "docs: synthesize glossary reference"
```

---

# Phase 3: Skill Assembly and Validation

### Task 35: Author SKILL.md

**Files:**
- Create: `.claude/skills/options-playbook/SKILL.md`

**Interfaces:**
- Consumes: all 8 files in `.claude/skills/options-playbook/references/` (Tasks 27–34)
- Produces: `.claude/skills/options-playbook/SKILL.md` — the skill's entry point, invocable in future sessions

- [ ] Step 1: Read all 8 reference files to confirm their actual final content and section headings.
- [ ] Step 2: Write `.claude/skills/options-playbook/SKILL.md` with this frontmatter:

```markdown
---
name: options-playbook
description: Comprehensive options-trading knowledge base distilled from Bittman's "Trading Options as a Professional" and Chen/Sebastian's "The Option Trader's Hedge Fund" — greeks, volatility, strategies (income, spreads, directional), market-making mechanics, risk management, and a business framework for running an options-trading operation. Use when selecting, evaluating, sizing, or reasoning about an options trade or strategy, or when applying risk/position-sizing rules to a portfolio.
---
```

- [ ] Step 3: Below the frontmatter, write a short "when to use each reference" map — one line per file in `references/` naming the topics it actually covers (pull the real subtopic list from Step 1, don't guess) — plus a one-paragraph overview of the two source books and the three-part organizational structure (Framework / Implementing the Business / Lessons from the Trading Floor, per Chen/Sebastian's own Parts I–III) so a future reader has enough context to know which file to open. Keep `SKILL.md` itself under ~100 lines — detail lives in `references/`, not here.
- [ ] Step 4: Commit

```bash
git add ".claude/skills/options-playbook/SKILL.md"
git commit -m "feat: author options-playbook SKILL.md entry point"
```

### Task 36: Completeness validation pass

**Files:**
- Modify: any file under `.claude/skills/options-playbook/references/` or `docs/extraction-notes/` found to have a gap

**Interfaces:**
- Consumes: both books' tables of contents (reproduced in the Source Page Maps section of this plan) and all 26 extraction notes and 8 reference docs
- Produces: a written confirmation (as a commit message and a summary reported back at the end of this task) that every chapter/appendix/topic from both tables of contents is represented somewhere in `references/`

- [ ] Step 1: For each of the 10 Bittman chapters + epilogue and 15 Chen/Sebastian chapters + 4 appendices listed in this plan's Source Page Maps, find at least one reference doc in `.claude/skills/options-playbook/references/` that covers its content. Build a simple checklist as you go (chapter → reference doc(s) it landed in).
- [ ] Step 2: For any chapter/appendix that doesn't clearly land anywhere, read its extraction note and add the missing material to the appropriate reference doc (or create a new reference doc if it genuinely doesn't fit the existing 8 — e.g., if Op-Eval Pro software mechanics turn out too extensive for `market-making-techniques.md` alone).
- [ ] Step 3: Re-read `SKILL.md` and confirm its topic map still accurately reflects `references/` after any Step 2 additions; update if not.
- [ ] Step 4: Commit

```bash
git add ".claude/skills/options-playbook/"
git commit -m "docs: completeness pass over options-playbook skill"
```

- [ ] Step 5: Report back a short summary: confirm all 10 Bittman chapters, the Bittman epilogue, all 15 Chen/Sebastian chapters, and all 4 Chen/Sebastian appendices are accounted for, and list any judgment calls made about ambiguous placement.
