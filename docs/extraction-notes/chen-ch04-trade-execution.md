Source: Chen/Sebastian, *The Option Trader's Hedge Fund*, Chapter 4 "Trade Execution", physical pp. 60–71.

## Overview / Introduction (p.60)

Analogy to sports/construction planning: plans can go out the window once conditions change, but unlike sports/construction, a TOMIC trader has much greater ability to control outcomes. Key theme: execute a plan in a way that is **disciplined but adaptive** — guidelines and an approach rather than rigid "trading rules." The chapter walks through implementing a TOMIC trading plan end-to-end via a checklist-driven thought process, then covers how to get an order filled effectively.

## Conditions of the Market (heading present)

First step: evaluate the market. At any time the market can be volatile or calm, with implied volatility inflated or undervalued; different contract months and different strikes within a month can be overpriced or underpriced independently. Because of all this variability, the market is more or less favorable to specific trades at any given moment.

Explicitly rejects the "enter the same trade every month regardless of conditions" approach as flawed. Correct approach (insurance-company framing, consistent with earlier chapters): assess current market conditions and sell the insurance policy least likely to be exercised.

## Evaluate Potential Realized Volatility (heading present)

Anecdote: as a floor trader, co-author Mark didn't need an opinion on a company's earnings or an FDA decision — just needed to know **that the event was coming up**. TOMIC traders should apply the same approach, especially for nondirectional premium selling: check for earnings, major federal data releases, Federal Reserve policy meetings, and geopolitical/far-off trouble that could hit financial markets. You can't evaluate a policy's premium fairly without knowing what could trigger it.

Caveat: no amount of research predicts earthquakes, terrorist attacks, or other true catastrophes — relying purely on historical volatility (HV) here "can equate to pissing in the wind." Always keep a worst-case scenario in mind.

**Mean reversion assumption**: the entire options universe relies on the assumption that volatility is **mean reverting** — a stock/index moving unusually fast is likely to slow down; one moving unusually slowly is likely to speed up. This assumption underlies evaluating whether an "insurance policy" (option) is cheap or expensive.

## Evaluate Implied Volatility (heading present)

If HV is mean reverting and IV is based on HV expectations, IV should mean-revert too — important for anyone selling premium.

**Proof via VIX options case study (the May 2010 flash crash):** VIX options are cash-settled and European-style (no early-assignment risk), so if IV gets too extreme, VIX options should price toward an expectation of VIX reverting to its mean rather than tracking the spot VIX cash level directly. On an IV spike, ITM calls should appear underpriced; when VIX is oversold, calls should appear overpriced.

Worked example: during the flash crash, at 3:30 ET, VIX cash traded just under 40%, but VIX futures were only around 29.20. Comparing VIX 30 calls to VIX 47.5 calls (Figure 4.1, sourced from OptionVue6): despite one being ITM and one OTM relative to the *cash* VIX, their prices were not far apart, because relative to the *futures* level (29.20) both were effectively OTM (the 30-strike was the practical ATM option against futures). Even as the market exploded, expectations of the VIX calming down kept VIX futures/options from ever pricing to the 40% cash level. Lesson drawn: **buying VIX OTM calls in the middle of a crash is one of the worst trades possible**, because VIX's mean reversion will kill most of these positions.

General rule: when IV trades at a premium to its mean, it's typically a better sell than buy — but this is not simple; there can be good reasons IV is elevated, so you must complete the "Evaluate Potential Realized Volatility" step first and have a clear picture of the policy's actual risk before concluding it's overpriced.

## Evaluate the Months (heading present)

Beyond overall volatility, evaluate the full **term structure** — how different contract months are priced relative to each other. Months are tightly correlated but not perfectly tied together; **paper flow** (direction/size of customer buying or selling) can make one month relatively cheap or expensive versus another, creating both outright buy/sell opportunities and month-vs.-month spread opportunities.

Goal: sell the most expensive policy relative to risk — finding the richest contract month materially improves collected premium. Different months can have different pricing drivers; digging into *why* a month is priced a certain way may reveal a trade is worse than it first appears, or (when a large trader with "an ax to grind" — a big position to establish or unwind — distorts a month) may reveal an exploitable opportunity.

## Evaluate the Skew (heading present)

Skew = how cheap or expensive calls and puts are relative to ATM options, largely as a byproduct of institutional hedging activity. Typical driver: equities/IRA/401(k)/pension hedgers **collar** their positions — buying downside puts and selling upside calls to help finance the puts — which structurally makes puts relatively expensive and calls relatively cheap versus ATM (visible in SPX's volatility surface structure). This dynamic isn't constant; the skew curve moves up and down as hedging flow changes, and the curve's steepness affects which trades are relatively favorable. Knowing how "expensive" the skew curve currently is helps determine what trade to enter and where to execute it.

## Evaluate Other Products (heading present)

Most SPX-focused trading firms also trade OEX, RUT, NDX, ES, and individual equity options because of cross-index correlation — don't "fall in love with" one product. Example: OEX has a historical beta to SPX of about **0.98**, yet due to liquidity differences it can be significantly overpriced or underpriced relative to SPX at times. Trading only one product risks missing better opportunities in a closely correlated one. Before any trade, confirm it's the single best trade available at that time by walking correlated products through the same evaluation process. Framing line: an insurance company doesn't care *who* it insures, only that it's selling the statistically best product at the highest price with the best return.

## Trade (heading present — covers strike selection and pricing/order-sizing mechanics)

Once a product is chosen, design the trade and get it executed: pick strikes, then get filled as cheaply/efficiently as possible.

### Picking Strikes (sub-heading present)

As large customers buy/sell up and down the skew curve, specific strikes can become relatively over/underpriced versus neighboring strikes. Consistently buying the relatively cheap strike against selling the relatively expensive one produces a higher relative credit on credit spreads — small per-trade improvements (pennies) compound at scale: a fully funded TOMIC might execute 15–30 trades/month at 1,000+ contracts each (10,000–100,000 contracts/month), so improving average fill by even $0.01/contract adds up quickly.

**Key rule: don't be married to a fixed delta or fixed percentage-OTM target, or a fixed spread width.** If targeting a 10-delta strike but the 9- or 11-delta strike is the better relative sale, sell that one instead. If a 5-point-wide spread is the habit but 10- or 15-points-wide offers a better relative credit, use the wider spread. Evaluate the whole surface and sell the richest available option near your target strike.

### Price (sub-heading present)

Volatility equates to price — every cent conceded to market makers is effectively selling at a slightly lower IV. Know the IV you intend to sell and its equivalent dollar price; attempt to execute at that price. **If you can't get filled at your price, it's better not to sell at all than to concede too much** — there's only an edge if the right price is achieved.

**Worked example — using vega to set a minimum acceptable price:** Suppose the sell side of a spread has IV of 21%, producing a price of $2.00, and you're willing to sell down to 20% IV. Net vega of the spread = 0.05. Multiply 0.05 × 1% (×100) = $0.05 of price flexibility. So you're willing to sell the spread down to **$1.95**, but no lower.

### Order Entry (sub-heading present)

Anecdote: as a floor trader, Mark dealt directly with brokers/institutional flow, and later had to select brokers to represent his own orders — eventually narrowing to just **three** trusted brokers who rewarded consistent flow with better fills and lower rates ("cream of the brokers rises to the top"). Never rely on only one broker — keep flexibility to route to whichever is likely to give the best fill.

**Why broker selection matters:**
- Different brokers are better at different products (e.g., adding futures options to TOMIC may require a second, futures-specialist broker; keep futures capital with the futures broker, options capital with the options broker).
- If you want to learn/trade a product your primary broker doesn't carry, consider a small account elsewhere to learn it.
- A broker might have superior analytics but weaker execution (or vice versa) — sometimes worth leaving assets with a broker purely for real-time data/analytics.

**Broker-selection criteria for TOMIC:**
- **Low commissions** — a low/no ticket charge is helpful early on, but a ticket charge with lower per-contract commission is typically better long-term.
- **Ability to read spread books** — visibility into order-book information (better resting offers, counter-offers) is valuable.
- **Ability to route orders to a specific exchange** — "smart routers" route based on where the *broker* makes the most money, not necessarily where the *trader* gets the best fill. Manually routing to a specific exchange defeats this and can get meaningfully better fills relative to the underlying's price (e.g., getting a call filled while the stock trades slightly higher than it otherwise would).

**Exchange routing guidance**: route first to the exchange with the best bid/offer — generally the best fill, *unless* that best offer sits on a "maker-taker model" exchange, which the text says has little practical effect on fill quality. If competing bids/offers are tied, routing to the exchange trading the largest size in that product can help (though the author flags the belief that "biggest bid wins access" is largely unfounded, except when one exchange is genuinely dominant in size for that product). **Named best-fill exchanges: CBOE and ISE** (top two), followed by **PHLX, NYSE-ARCA, and AMEX**. **Never route to a maker-taker exchange unless hitting a bid or lifting an offer** — market makers strongly dislike paying to fill orders they're hit on, and it materially affects fill price.

**How orders get filled — historical vs. current market structure:**
- Historically (pre-algorithmic era), complex orders were priced leg-by-leg by human market makers in the crowd, who were often willing to improve pricing on spreads because a spread order is partially self-hedged (buying one option, selling another). Even then, market makers disliked overly complex orders (multiple strikes, multiple months, unusual spread widths).
- Today, complex orders are mostly priced by algorithms, and market makers must be careful how much edge they concede on any order type — firms like **Timber Hill and Citadel** are described as constantly probing exchange quoting algorithms for exploitable weaknesses ("much like computer hackers"), and will pick off a weak quoting algorithm aggressively and in size if found.
- Consequence: **simpler trades fill more easily and at relatively better prices than spreads**, almost always. But trading individual legs introduces directional risk — which the TOMIC trader is generally trying to avoid — so buying/selling individual legs to build a spread isn't advisable unless you plan to actively trade the underlying to stay hedged while legging in.
- **Recommendation by experience level**: newer traders should almost always enter delta-neutral spread trades as a single complex order (harder to execute, but individual-leg pricing is where retail traders most often get mispriced/disadvantaged by market makers). More experienced traders can begin breaking orders apart — first attempt to fill the whole spread at an efficient price; only break it up if that fails.

**Relative ease of filling different spread types (from hardest to easiest, per the text's ordered list):**
1. Nontraditional spreads
2. Iron condors
3. Double diagonals
4. Straddles
5. Strangles
6. Butterflies
7. Vertical spreads
8. Calendar spreads
9. Single option trades

Caveat: a small trade with unusual strikes can occasionally land in a spot an algorithm is specifically set up to execute, so nontraditional spreads may sometimes fill at surprisingly good prices.

**Size of Order (sub-heading present)**: Orders under 10 contracts fill more easily than larger ones — most algorithms are tuned to signal an order exists to the market maker rather than trade a large spread automatically, unless the firm has a large edge or a very tight quoting system. Starting with sub-10-contract clips helps secure a better fill.

**Working an Order (sub-heading present)**: A quoted "midprice" is not necessarily the true midpoint — **"book orders"** (resting customer orders) can distort the quoted bid-ask spread and the implied IV calculated from the midprice. Once you've established the *true* midpoint yourself, it never hurts to try to do better than that price. Computer-generated quotes can also simply be wrong (e.g., a bad IV input can cause a fill above/below where it should be) — "it never hurts to try" applies here too. Analogy: professional market makers train for roughly a year before "getting on a badge"; a self-backed TOMIC trader trading their own capital should be equally rigorous about extracting the best possible price. Quantified stakes: saving $0.05 on a 10-contract trade every trading day equates to **$12,500/year**.

## Trade Execution Checklist (heading present — final section of the chapter)

Presented explicitly as a checklist to run through before every trade entry, organized by trade lifecycle (parallel in structure to Ch.3's risk-management checklist):

*Before the trade:*
- What market are you going to trade?
- What is the direction of the market?
- Did you check the volatility conditions of the market? What is the historical volatility? What is the implied volatility? Did you check the skew?
- What is the strategy you will be using?
- If this is a complex spread, how will it be executed? Is it worth executing at the individual component level? Will you be legging into the spread? Will it be sent as a complex order?
- What is the maximum allowed loss?
- Is the expected return within the underwriting parameters?
- What is the target profit for this trade?
- What is the size for this trade? Does it conform to the position sizing parameters?
- At what point would the trade require adjustment (if any)? Do you know the possible adjustments to make (if needed)?

*During the trade:*
- Has the trade hit an adjustment point?
- Has the trade hit the profit/loss target?

*After the trade:*
- Did you log the trade in the trading diary?
- Did you follow the trading plan?
- If not, why not?

## Notes on completeness / discrepancy with task's known-headings list

The task description's "known headings" list ("Conditions of the Market; Evaluate Potential Realized Volatility; Evaluate Implied Volatility; Evaluate the Months; Evaluate the Skew; Evaluate Other Products; Trade Order Entry") does not exactly match the actual heading structure found in the source text. The real chapter uses a separate **"Trade"** heading (covering "Picking Strikes," "Price," and "Order Entry" as sub-sections, not a single combined "Trade Order Entry" heading), plus a final **"Trade Execution Checklist"** section not mentioned in the task's list at all. All of this content has been captured above under its actual heading structure. No content appears to have been missed — every heading and sub-heading present in the physical pages 60–71 text has a corresponding section in this note.
