Source: Bittman, *Trading Options as a Professional*, Chapter 9 "Setting Bid-Ask Prices", printed pp. 279–310.

## The Theory of the Bid-Ask Spread (p.280–283, Tables 9-1/9-2 — "Alex")

- Core market-maker technique: **buy on the bid (or sell at the ask), immediately hedge delta-neutral with stock, then later close both legs** — aiming to capture the option's bid-ask spread while remaining insulated from market direction.
- **Worked example, stock rallies** (Table 9-1): sell 10 55 Calls at ask 1.85 (delta 0.40) → buy 400 shares at ask 54.01 to hedge. One hour later, stock +$1, call bid/ask +$0.40 → buy back the 10 calls at bid 2.20 (loss $350 on the option leg) and sell the 400 shares at bid 54.99 (profit $392 on the stock leg) → **net profit $42**.
- **Worked example, stock declines** (Table 9-2): identical opening trade; stock instead falls $1, call falls $0.40 → buy back calls at bid 1.40 (profit $450 on options) and sell stock at bid 52.99 (loss $408) → **net profit $42 — the exact same result as the rally case.**
- **Key insight**: buying options on the bid / selling at the ask while staying delta-hedged can be profitable **regardless of which way the stock moves** — even after "giving up" the stock's own bid-ask spread on the hedge trade — because the option bid-ask spread (5¢ in the example) was wider than the stock's bid-ask spread (2¢), leaving a net edge either way.
- **Real-world complicating factors** (p.283): (1) transaction costs, even if small for market makers, must be budgeted; (2) the relative width of the stock's bid-ask spread vs. the option's matters — at some ratio the stock spread would erase the edge, requiring wider option quotes; (3) since prices constantly move, market makers need a fast, reliable way to track/adjust bid-ask levels as conditions change (addressed via implied-volatility-denominated quoting, below) — delta alone is a useful but insufficient tool for this (gamma/vega effects complicate simple delta-based repricing in reality).

## The Need to Adjust Bid and Ask Prices (p.284–285)

- Because implied volatility itself can shift (beyond what delta/gamma alone predict — see Ch.7's Table 7-6 intraday-IV-swing example), market makers manage risk two ways: **setting risk limits** (max contracts long/short, e.g., a 100-contract cap) and **scaling into/out of positions**.
- **Scaling in**: selling (or buying) in increments at successively worse prices for the counterparty (better for the market maker) as a position grows, e.g., selling 20 contracts, then 20 more at a higher price, then 20 more higher still, up to a preset max. This both (a) improves the market maker's average execution price as the position grows and (b) the raised offer may itself attract sellers back into the market.
- No "scientifically right" answer for increment size (20 vs. 10 vs. 25 contracts) or price-adjustment size (1 tick, 2 ticks) — these are individual, experience-based judgment calls.

## The Process of Adjusting Bid and Ask Prices (p.285–288, Table 9-3 — "Anna")

- **Fully worked scaling example**: Anna quotes the 80 Call (delta 0.60) at 4.50 bid/4.60 ask with stock at 80.40/80.42. Three successive 20-lot buy orders hit her offer at rising prices (she raises the quote 2¢ after each 20-lot sold: 4.60→4.62→4.64 ask), each time hedging by buying 1,200 shares (20×100×0.60) to stay delta-neutral — building to a 60-short-call / 3,600-long-share position. A 60-lot sell order then arrives and she buys all 60 calls back at 4.56 bid, simultaneously selling all 3,600 shares at 80.40 bid to flatten.
- **P&L**: stock trading lost $72 (bought 3,600 sh at 80.42, sold at 80.40, −2¢/share) but the three option tranches sold at progressively higher prices (4.60/4.62/4.64) and all bought back at the same 4.56 → profits of $80+$120+$160 = $360 → **net profit $288**.
- Demonstrates that scaling lets a market maker absorb a large one-directional order flow imbalance without taking on one single large position at one price, while raising quotes both manages the market maker's risk and may re-attract counter-flow.

## The Limit on Adjusting Bid and Ask Prices (p.288–290, Table 9-4)

- Key question: how many times can a quote be walked before a full round-trip (open then close all contracts at the current opposite side) merely breaks even?
- **Worked example**: 5¢ initial bid-ask spread, 1¢ increment per successive 1-lot sale → after the market maker sells contracts at rising ask prices 9 times (1.80, 1.81, ... 1.88), the average sale price across all 9 contracts equals 1.84 — exactly the *current bid* at that point, so buying all 9 back on the bid nets to **exactly breakeven**. A 10th raise would put the position into loss territory if closed immediately.
- **General formula**: `number of times a bid-ask spread can be adjusted before breakeven = (2 × bid-ask spread − increment) / increment`. Worked check: (2×5−1)/1 = 9, matching the example.
- This gives market makers a concrete cap: beyond this many scale-in steps, an immediate round-trip close would produce a loss, not a profit, at the given spread width and increment size.

## Estimating Option Prices as Volatility Changes (p.290–292, Table 9-5)

- **Core formula**: `new theoretical value ≈ known theoretical value + (Δ implied volatility in percentage points) × vega`. Lets a trader quickly re-price an option for a new IV assumption without re-running the full pricing model.
- Worked example (stock=81.50, three calls at 30% vol): 80 Call (theo 4.00, vega 0.10) at +1pt IV (30%→31%) → new value 4.00+0.10=**4.10**. 85 Call (theo 1.75, vega 0.08) at +1.5pt IV → new value 1.75+(1.5×0.08)=**1.87**. 90 Call (theo 0.65, vega 0.06) at +2pt IV → new value 0.65+(2×0.06)=**0.77**.

## Expressing Bid and Ask Prices in Volatility Terms (p.292–294, Table 9-6)

- Second essential skill: converting a dollar bid-ask spread into an **implied-volatility bid-ask spread**, using the same vega-scaling logic in reverse — this becomes the market maker's actual internal "unit" for quoting and comparison, since dollar prices alone are hard to compare as the stock price moves.
- Worked examples (same three calls): 80 Call priced 3.90 bid/4.10 ask (theo 4.00 @30% vol, vega 0.10) → since 3.90 is exactly 1 vega below theo and 4.10 is 1 vega above → quoted as **29% bid / 31% ask**. 85 Call (theo 1.75, vega 0.08) priced 1.75/1.83 → **30% bid / 31% ask** (bid unchanged from theo's own vol, ask 1 vega up). 90 Call (theo 0.65, vega 0.06) priced 0.68/0.77 → **30.5% bid / 32% ask** (bid = +0.5 vega, ask = +2 vega).
- These two skills (price↔IV conversion, and quoting spreads in IV terms) are described as essential for professional traders because trading decisions must be made quickly, and are the foundation for the position-management and risk-management techniques in Ch.10.

## Trading Exercises Introduced (p.294–295, Table 9-7)

Four worked exercises follow, all using "Ross" as the hypothetical trader and a shared reference table (Table 9-7: theoretical values/deltas/vegas for 80/85/90 strike calls and puts across stock prices 83.60–85.00, 32% vol, 56 days, 4% rate, no dividends). Each exercise demonstrates the same three techniques — (1) trade delta-neutral to stay direction-agnostic, (2) use implied volatility to set/adjust quotes, (3) market makers can be indifferent to *which* options they trade since buying-bid/selling-ask profitably works across many strategy types — with a different bid-ask-spread width (in vol terms) per exercise, reflecting how real markets vary in liquidity/spread width by underlying, volume, or pending events (e.g., earnings).

### Exercise 1: Buying Calls Delta-Neutral (p.296–298, Tables 9-8A/B/C)

- Ross quotes the 85 Call 32.0%/32.5% IV (stock=84.60, theo 4.28) → buys 10 on the bid (4.28), sells 520 shares short to hedge (delta 0.52 × 1,000 shares). Stock later falls to 83.80; Ross re-quotes 31.8%/32.8% IV (lowering the quote both to potentially scale into more calls at a better average price *and* to entice buyers) → sells the 10 calls at the new ask (3.96) and buys back the 520 shares (83.80).
- **P&L**: options lost $320 (bought 4.28, sold 3.96 ×10×100), stock gained $416 (sold short 84.60, covered 83.80 ×520) → **net profit $96**. Same conclusion as Exercise in Tables 9-1/9-2, but this time demonstrated with a genuinely moving stock price and IV-denominated quoting.

### Exercise 2: Creating a Butterfly Spread in Three Trades (p.298–302, Tables 9-9A/B/C)

- Ross builds a **long call butterfly** (long 1 lower-strike call, short 2 middle-strike calls, long 1 higher-strike call — per Ch.1's Fig 1-11) via three separate delta-neutral market-making trades at three different times/stock prices: sells 50 85 Calls delta-neutral (stock=84.00), buys 25 80 Calls delta-neutral (stock=84.60, adjusting IV up after a sale to seek more sellers), buys 25 90 Calls delta-neutral (stock=83.60, adjusting IV back down after a purchase to seek more buyers).
- **Result**: gross option cost per spread = 1.14 (incl. 4¢ costs) vs. theoretical value of 0.92 — but the three incidental stock hedge trades themselves netted a **$750 stock profit** (30¢/share per spread) since the stock happened to trend down across the trades in a way that favored the accumulated hedge positions. Net cost per spread: 1.14 − 0.30 = **0.84, i.e., 8¢ below theoretical value**. Demonstrates that market-making mechanics (not a directional bet) can build complex multi-leg positions at a structural discount to theoretical value.

### Exercise 3: Creating a Reverse Conversion in Two Trades (p.302–306, Tables 9-10A/B/C)

- Ross buys 10 80 Calls on the bid delta-neutral (stock=84.60, shorts 700 shares), then sells 10 80 Puts at the ask delta-neutral (stock=84.00, shorts 300 more shares) — ending with long 10 Calls + short 10 Puts + short 1,000 shares = a **reverse conversion** (per Ch.6).
- **Pricing check** (per Ch.6's method): DPV of the 80 strike (4% rate, 60 days) = 79.51; net credit required for a 5¢ target profit (with 4¢ costs) = 79.60. **Actual net credit achieved**: stock sold short at avg. 84.42, minus 80 Calls bought at 7.14, plus 80 Puts sold at 2.33 = **79.61** — 1¢ better than required, confirming a profitable reverse conversion was established purely through bid/ask market-making mechanics.

### Exercise 4: Creating a Long Box Spread in Two Trades (p.306–310, Tables 9-11A/B/C)

- Ross buys the 85-90 call spread delta-neutral (buy 85 Calls on the bid, sell 90 Calls at the *midpoint* of their bid-ask — standard practice for one-to-one vertical spreads, since a spread has lower risk/lower Greeks than either leg alone and so doesn't need as wide a market as an outright option), then buys the 90-85 put spread delta-neutral similarly — together forming a **long box spread** (per Ch.6).
- **Note on vertical-spread quoting convention** (p.307): because a vertical spread carries lower delta/gamma/vega/theta (in absolute value) than a single option, it's standard practice not to quote it with as wide a bid-ask spread as an individual option — hence trading one leg at the touch and the other at the spread's midpoint is an accepted shortcut.
- **Pricing check**: gross cost of the box = 1.92 (call spread) + 3.11 (put spread) = 5.03; incidental stock-hedge trades netted an $18/spread profit → net cost per spread = 4.85. Theoretical value (DPV of the $5 strike difference minus costs plus target profit, 5% borrowing rate, 56 days, 6¢ costs, 5¢ target profit) = **4.85** — an exact match, confirming a correctly (and profitably, relative to the embedded 5¢ target) priced long box spread.

## Summary

Market making has three core components: buy on the bid, sell at the ask, and stay delta-neutral throughout — aiming to capture the bid-ask spread while remaining insulated from directional risk. This requires three learnable skills: (1) **converting between option price and implied volatility using vega** (both directions — pricing a new IV level, and expressing a dollar bid-ask spread in volatility terms); (2) knowing how to assemble **low-risk multi-leg strategies** (butterflies, reverse conversions, box spreads, and others) via a sequence of individually delta-neutral trades, since market makers can be indifferent to *which* specific options they're filled on as long as each fill is properly hedged; and (3) **judiciously adjusting bid/ask quotes** as risk limits are reached, to scale into/out of positions at favorable average prices — bounded by a hard mathematical limit (`(2×spread − increment)/increment`) on how many times a quote can be walked before an immediate round-trip close would turn unprofitable.
