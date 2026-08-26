Source: Bittman, *Trading Options as a Professional*, Chapter 2 "Operating the Op-Eval Pro Software", printed pp. 31–48.

**Note on this chapter's nature**: this chapter documents a specific bundled Windows software tool (Op-Eval Pro, distributed on a CD with the book — long obsolete as software). It is captured here for completeness, but its *reusable value* is the analytical concepts it exposes (implied volatility solving, theoretical/Greeks calculation, standard-deviation price-range estimation, "what-if" sensitivity analysis) rather than the specific UI mechanics. Each subsection below is flagged **[Concept]** (reusable — the calculation/idea itself) or **[Software-only]** (specific to operating this particular program).

## Overview of Program Features **[Software-only, concepts noted]**

Op-Eval Pro has six screens:
- **Single Option Calculator [Concept: single-option theoretical value/Greeks/IV calculator]** — theoretical values, implied volatility, and Greeks for a call and put sharing the same inputs.
- **Spread Positions screen [Concept: multi-leg position Greeks aggregation]** — theoretical values and Greeks for up to 4 options, or 1 underlying + 3 options; supports per-leg volatility inputs; "Price ±1" buttons recalculate under a hypothetical stock move.
- **Theoretical Graph screen [Concept: P&L/Greeks visualization vs. price, vol, time, or rates]** — graphs positions built on the Spread Positions screen (all legs must share the same expiration).
- **Table screen [Concept: theoretical value/Greek sensitivity table across a price × time grid]**.
- **Portfolio screen [Concept: portfolio-level Greeks aggregation across up to 15 options with differing expirations/IV]** — includes "what-if" move-volatility / move-days-to-expiry inputs.
- **Distribution screen [Concept: one-standard-deviation price-range estimate from IV, price, and time]** — directly useful for picking strike prices and stock-price targets (ties into Ch.7's volatility discussion).

## Installing the Software **[Software-only]**

CD-based install (Windows XP/Vista specific instructions) — not reusable content; the program's assumptions/disclaimers, however, are worth noting: the reader must read the "Disclosures and Disclaimers" screen and explicitly accept before use, since incorrect inputs can produce theoretical values that diverge sharply from real market prices.

## Choices of Pricing Formulas **[Concept: American/binomial vs. European/Black-Scholes; Equity vs. Index dividend treatment]**

- **American vs. European** exercise style selects the pricing model:
  - **American**: early exercise permitted → **binomial model** (discrete time steps/"Steps", default 25, discounted present-value over the outcome tree). Steps rarely need adjusting.
  - **European**: no early exercise → **Black-Scholes** (closed-form, differential calculus, no step parameter).
- **Equity vs. Index** selects how dividends are modeled:
  - **Equity** (individual stocks): discrete, dated dividends — requires dividend amount + days-to-ex-dividend inputs.
  - **Index**: modeled as a continuous **dividend yield** (assumes dividends paid evenly/continuously through the year) — a simplification but industry-standard for index options.
- Practical note: "Index" + "European" calculates fastest with only a small accuracy cost vs. "Equity" + "American" (binomial); useful default when precision loss is acceptable.
- Expiration-date convention matters for correct "days to expiry" input: American-style equity/index options (e.g., OEX) expire the Saturday after the 3rd Friday (last trading day = 3rd Friday); European-style index options (SPX, DJX, MNX) expire the 3rd Friday itself (last trading day = Thursday before).

## Features of Op-Eval Pro — the 10 features **[Software-only]**

Single Option Calculator; Spread Calculator; Graphing; Theoretical Table Generator; Portfolio Analysis and Graphing; Probability Distribution; Print Preview; Print; Save Spread; Open Spread.

### The Single Option Calculator **[mostly software-only; concept: inputs driving an option pricing model]**

Inputs: stock price (0–99,999.99), strike price (any level 0–99,999 — supports any underlying), volatility % (1.00–999.99), interest rate % (0–99.99, noted to have relatively small price impact vs. other inputs — consistent with Ch.3's treatment), days to expiry (0–9,999; include current day if analyzing before/during market hours, exclude if after close), dividend (yield if Index, discrete amount + days-to-ex-div if Equity). Outputs: value, delta, gamma, vega, theta, rho for both a call and put sharing inputs.

**[Concept] Calculating Implied Volatility**: entering a known *market price* into the Value box and solving backward recalculates the volatility % that would produce that price — this is **implied volatility** (IV). Op-Eval Pro treats IV-solving as inverting the pricing formula given an observed price rather than an input.

### The Spread Positions Screen **[mostly software-only; concepts noted]**

Handles vertical spreads (calls-only or puts-only), ratio spreads, time spreads, mixed call/put spreads, and stock+option combinations. **[Concept] "Locking" a row (the asterisk convention)**: marking a row (e.g., Stock Price) with `*` forces all legs in that row to move together (shared underlying price / IV / days-to-expiry across legs) — the absence of an asterisk lets each leg's value in that row move independently. This is the software's way of representing "these legs share the same underlying" vs. "these legs can have individually different volatility assumptions" for volatility-skew-aware analysis. **[Concept] Multiplier consistency**: quantity × multiplier must be set consistently between options and any underlying stock leg in the same position, since it scales value *and* the Greeks. **[Concept] "Price ±1" / "Days ±1" scenario buttons**: quick what-if recalculation of a position's value/Greeks under a 1-point underlying move or 1-day time decay — worked example: a 100-110 bull call spread (value 2.87, delta 0.28) under +$4 stock / −5 days → value rises to 4.01, delta to 0.32. **[Concept] Spread-level implied volatility**: entering a market price for one leg solves IV for that leg only (if that leg's volatility cell isn't asterisk-locked to others).

### Theoretical Graph Screen **[mostly software-only; concepts noted]**

**[Concept] Three-line P&L graph convention** used throughout the book's figures: straight-segment line = payoff at expiration; middle curved line = payoff at half the days-to-expiration; third curved line = payoff at full days-to-expiration entered. Requires all legs to share underlying price, expiration, dividend terms, and interest rate to be graphable. Can graph value or any Greek (delta/gamma/theta/vega/rho) against underlying price (or vs. volatility/time/rates, per the chapter's opening summary).

### Theoretical Price Table **[Concept: price/Greek sensitivity table across a price-by-time-to-expiration grid]**

Faster than re-running the Spread Positions screen one price at a time; produces a full grid (e.g., strike range 80–125 down rows, 60→6 days to expiration across columns) of theoretical value or a chosen Greek — worked example given for a bull call spread (100-110) with full table reproduced (theo values ranging ~9.12 at 60-days/125-underlying down to 0.00 at 80-underlying near expiration).

### The Portfolio Screen **[Concept: portfolio-level Greeks + P&L graphing across many legs/expirations]**

Up to 15 options + 1 underlying, legs can have differing expirations and differing implied volatilities. "Move volatility" / "Move days to expiry" what-if inputs shift the whole portfolio's assumed vol/time and recompute. Worked 6-part example position (long 6,000 shares stock, short calls/puts across multiple strikes) shown with aggregate Greeks (Value 600,799; Delta 5,260.1; Gamma −150.58; Vega −414.17; Theta 1,254.95; Rho −71.17) and a full P&L graph.

### The Distribution Screen **[Concept: one-standard-deviation expected price range from IV]**

Given underlying price, volatility %, and a set of time periods, calculates the market-implied one-standard-deviation price range for each period (ties directly to Ch.7's volatility discussion — an option's implied volatility encodes the market's expectation of the underlying's future dispersion). Worked example: stock at $83.00, 33% vol → 1-SD ranges of [79.21, 86.79] at 6 days, [77.64, 88.36] at 14 days, [76.43, 89.57] at 21 days, [75.41, 90.59] at 28 days. Directly useful for selecting strike prices and stock-price targets.

### Previewing, Printing, and Saving **[Software-only]**

All screens can be previewed/printed; scenarios can be saved and reopened via "Save As" / "Open".

## Summary

Op-Eval Pro performs calculations and draws graphs but does not make trading decisions. Users must read the Disclosures/Disclaimers before use. The Single Option Calculator, Spread Positions, and Portfolio screens all expose theoretical value + delta/gamma/theta/vega; changing "Stock Price" (or entering a market price) triggers an implied-volatility recalculation. The three-line graphing convention (expiration / half-time / full-time-remaining) recurs throughout the rest of the book's figures. Complex multi-expiration positions are handled on the Portfolio screen.
