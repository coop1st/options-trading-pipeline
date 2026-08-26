---
name: options-playbook
description: Comprehensive options-trading knowledge base distilled from Bittman's "Trading Options as a Professional" and Chen/Sebastian's "The Option Trader's Hedge Fund" — greeks, volatility, strategies (income, spreads, directional), market-making mechanics, risk management, and a business framework for running an options-trading operation. Use when selecting, evaluating, sizing, or reasoning about an options trade or strategy, or when applying risk/position-sizing rules to a portfolio.
---

# Options Playbook

Two source books, two complementary lenses. Bittman's *Trading Options as a
Professional* supplies formal market-maker mechanics — pricing, the Greeks,
volatility, synthetic relationships, arbitrage, bid-ask theory, and position
risk. Chen/Sebastian's *The Option Trader's Hedge Fund* supplies a
practitioner's business framework for running an options operation as "The
One Man Insurance Company" (TOMIC) — trade selection, the five most-used
strategies, and real trading-floor lessons. Where the books frame the same
idea differently (e.g., volatility skew, weighted vega), the reference docs
below present both views with attribution rather than picking one.

Chen/Sebastian's own three-part structure is a useful mental map, since it
spans both books' content: **Part I, The Framework** (trade selection, risk
management, execution, the trading plan, infrastructure, learning loop) →
**Part II, Implementing the Business** (volatility, the five core
strategies, running TOMIC end-to-end) → **Part III, Lessons from the
Trading Floor** (real-world volatility, risk, execution, and Greeks
lessons). Bittman's ten chapters underpin Part I and II with the underlying
pricing/Greeks/arbitrage mechanics.

Full source material and per-chapter extraction notes (with page
attribution) live under `docs/extraction-notes/` if you need to trace a
claim back to its exact source passage.

## Reference map — which file to open

- **`references/greeks-and-volatility.md`** — Delta/gamma/vega/theta/rho
  definitions, formulas, and how each changes with moneyness, time, and
  volatility. Historic/realized/implied/expected volatility, annualizing
  volatility across time periods, volatility skew (including
  Chen/Sebastian's "three-dimensional volatility" model), weighted
  vega/gamma, gamma scalping, and delta-neutral trading theory (long vs.
  short volatility, why it breaks even when implied and realized volatility
  match, and the asymmetric risk profile when they don't). Start here for
  any question about *why* an option is priced the way it is or *how* a
  Greek will move.

- **`references/income-strategies.md`** — Premium-selling as underwriting:
  the covered-call/cash-secured-put ↔ short-put synthetic equivalence,
  vertical credit spreads, iron condors, the risk controls specific to being
  a net option seller, and a pre-trade evaluation checklist (market
  conditions, realized/implied volatility, term structure, skew,
  cross-product correlation, strike selection) plus the full trade-execution
  checklist. Use for "should I sell this premium" questions.

- **`references/spreads-and-combinations.md`** — Construction, greeks
  profile, entry/management/exit rules for vertical spreads, iron condors,
  ATM iron butterflies (with the full butterfly trading checklist and
  wing-width sizing), calendar and diagonal spreads, ratio spreads, the kite
  spread, and Bittman's arbitrage combinations (conversions, reverse
  conversions, box spreads). Use for "how do I build/adjust/exit this
  multi-leg structure" questions.

- **`references/directional-strategies.md`** — Outright long calls/puts,
  the six synthetic equivalences and put-call parity, Chen/Sebastian's
  trade-selection criteria for picking a directional trade, and managing a
  directional position's delta risk (including when a vertical spread beats
  an outright long option). Use for simple bullish/bearish plays.

- **`references/market-making-techniques.md`** — Bid-ask spread theory,
  quoting and adjusting prices in volatility terms, scaling into positions,
  the four worked market-making exercises (building a butterfly/reverse
  conversion/box spread via delta-neutral trades), payment for order flow,
  and why understanding this matters even if you're not a market maker.

- **`references/risk-management-and-position-sizing.md`** — Calculating and
  neutralizing position Greeks, setting risk limits by position type, money
  management and position sizing, portfolio diversification, black-swan
  insurance ("units"), and the trading-floor risk heuristics (Cash Is a
  Position, the Card Game Value, weekend/vacation risk). Use before sizing
  any trade or reviewing portfolio-level risk.

- **`references/trading-business-framework.md`** — The TOMIC business
  framework end-to-end: the insurance-business analogy, writing a trading
  plan, infrastructure requirements (broker, portfolio margin, tools), the
  journal/feedback-loop discipline, and the full A-to-Z operating
  walkthrough. Use for process/discipline questions, not trade-level ones.

- **`references/glossary.md`** — Alphabetical one-line definitions of every
  named term and formula across both books, each pointing back to its
  source chapter. Use to look up an unfamiliar term fast.

## How to use this skill

For a specific trade or strategy question, start with whichever reference
file matches the strategy family, then cross-check
`greeks-and-volatility.md` for the sensitivities involved and
`risk-management-and-position-sizing.md` before committing capital. For
"how do I run this as an ongoing operation" questions, go straight to
`trading-business-framework.md`. Don't re-derive strategy rules from
scratch — look them up here first; the reference docs are the distilled,
attributed source of truth for this project's screening and strategy work.
