Source: Bittman, *Trading Options as a Professional*, Chapter 7 "Volatility", printed pp. 205–238.

## Volatility Defined (p.206)

- **Volatility = price change without regard to direction.** A 1% rise and a 1% decline are equal in volatility terms — only the magnitude of percentage change matters, not the direction, absolute dollar amount, or stock price level.
- Two conceptual traps: (1) traders instinctively think in "good direction / bad direction" terms, which obscures volatility's non-directional nature; (2) a single day's price change means nothing — volatility describes a *series* of changes over time (analogy: a "shallow river" averaging 6 inches can still have a 9-foot hole; a low-volatility stock can still have one big-move day, and vice versa).

## Historic Volatility (p.206–216)

- **Definition**: the annualized standard deviation of daily returns over a specified observation period (30/90 days, etc. — period must be specified for comparisons to be meaningful). Standard deviation = average difference between each daily return and the mean return.
- **Daily return formula**: `(closing price today − closing price yesterday) / closing price yesterday`.
- Annualizing: daily standard deviation × √(number of trading periods per year).
- **Worked comparison (Stock 1 vs. Stock 2, Figs 7-1–7-3, Tables 7-1–7-3)**: both stocks start and end at $100 over 31 days. Visually, Stock 2 looks more dramatic (falls to $94, rallies to $110, falls back to $100) while Stock 1 stays in a narrow ~5-point range — but Stock 1's annualized historic volatility (37.55%) is actually *higher* than Stock 2's (22.11%). Lesson: volatility reflects the *frequency/magnitude of daily percentage swings*, not the size of the overall trend or range traveled.
- Ranking daily returns from smallest to largest (Table 7-3) confirms this: Stock 1's daily moves are consistently larger in magnitude across every percentile band checked (smallest 20 of 30 obs., smallest 29 of 30 obs.), even though its net cumulative journey looks calmer.
- **Distribution shape**: a bell-curve/normal-distribution model of daily returns — a **wider, flatter** curve = higher volatility; a **narrower, taller-peaked** curve = lower volatility.
- **Normal distribution statistics** (Table 7-4, standard, cited to Wikipedia): 68.27% of outcomes fall within 1 standard deviation, 95.45% within 2, 99.73% within 3, 99.994% within 4, 99.99994% within 5, 99.9999998% within 6. A 6-SD move is "not impossible, just unlikely."

## Realized Volatility (p.216)

- **Definition**: the volatility that *actually occurs* between today and some future date — i.e., historic volatility computed retroactively over a period that hasn't happened yet. Also called "future volatility" because it's unknown today.

## The Meaning of "30 Percent Volatility" (p.216–218)

- If a stock's volatility is 30%: **68% chance** the stock is within ±30% of today's price one year out (1 SD); **95% chance** within ±60% (2 SD); **99% chance** within ±90% (3 SD).
- **No direction implied** — volatility gives range, not direction; it cannot forecast which way price moves, only how far it might move once a trader supplies their own directional view. Example: a bullish trader targeting a 2-SD move on a $100 stock at 30% vol targets **$160** (100 + 2×30%) — the "bullish" and "2-SD" assumptions are subjective, but the resulting $160 target is an objective calculation given those inputs.

## Converting Annual Volatility to Different Time Periods (p.217–220, Table 7-5, Fig 7-5)

- **Formula**: `SD for period = annual volatility × √(days in period / days per year)`.
- Worked example: stock=$78.50, annual vol=35% → 1-year SD=27.47; 4-week (28-day) SD=7.61 (implied range $70.89–$86.11, 68% confidence); 1-week SD=3.77; 1-day SD=1.41.
- Practical use: comparing a 4-week vs. 8-week option (e.g., XYZ 80 Call: 4wk@2.50 vs 8wk@3.85) using the corresponding SD ranges (7.61 vs 10.76) to judge whether the extra cost buys enough extra range to be worth it — a subjective trader call, informed by an objective range calculation.
- **Op-Eval Pro's Distribution screen** automates this (per Ch.2): enter price/vol/days, get 1-SD ranges at 1×/2×/3×/4× the base period.

## Calendar Days versus Trading Days (p.220–222)

- Debate: should the time-period formula use calendar days (365/yr) or trading days (~252/yr)? **Conclusion: usually doesn't matter much, except for very short periods.**
- Worked comparisons (stock=$78.50, 35% vol): a **2-month period** (61 calendar / 43 trading days) → SD of $11.23 (calendar) vs. $11.38 (trading) — only 15¢ difference, immaterial. A **3-day period** → SD of $2.51 (calendar) vs. $2.98 (trading) — 47¢ difference, ~17%, which *can* matter for very-short-dated strategies.
- Practical note: most traders default to calendar days since brokers readily supply "days to expiration," while trading-day counts are less accessible/more effort to compute.

## Implied Volatility (p.222–226, Figs 7-6/7-7)

- **Definition**: the volatility percentage that, plugged into the pricing formula, reproduces an option's actual *market* price as its theoretical value — i.e., solving the pricing formula backward from a known price to the implied vol input.
- **Worked example ("Gary")**: XYZ March 70 Call, stock=68.00, no div, 4% rate, 75 days. Using 26% vol (recent historic vol) → theoretical value 2.57. Market price is actually 3.40. Since price, strike, expiration, rate, and dividend are all known/fixed, the *only* variable that can explain the gap is volatility — solving backward gives **implied volatility = 32.84%**.
- **The Role of Supply and Demand / P-E ratio analogy**: implied volatility is a *market-determined* "common denominator" for comparing option prices across different underlyings, the same way a stock's P/E ratio (itself market-determined, since it's a function of price) lets analysts compare companies with different absolute prices/share counts. If Company A's options trade at 38% IV and Company B's at 25% IV, the market is pricing A as likely to be more volatile than B going forward — a statement of market opinion, not a guarantee of what will actually happen (realized volatility may differ).
- **Implied Volatility Changes** (p.225–226): all else equal, an option trading at *relatively low* IV (vs. its own history) is a relatively better purchase; one at *relatively high* IV is a relatively better sale — but "all else equal" rarely holds, so IV level alone can't dictate a buy/sell decision; it's one input into a subjective judgment.
- **Both Historic and Implied Volatility Change** (p.226–228, Fig 7-8): both types of volatility rise and fall with company-specific and market-wide events. Real 12-month example (unnamed large-cap stock, IVolatility.com data) shows IV *rising* alongside a rising stock price (Apr–Jul 2007) — directly contradicting the "conventional wisdom" that volatility only rises when prices fall. Lesson: don't assume the standard inverse price/vol relationship always holds; analyze each situation.
- **Revisiting the Insurance Analogy** (p.228–229): historic volatility ≈ an insurer's actual claims record; implied/expected volatility ≈ the market's/insurer's *forward-looking* risk assessment, which can diverge from history when the market perceives a genuine regime change before most individuals do (cited real-world analogy: oil prices climbing from ~$40 to $140/barrel 2006-2008 despite repeated "this can't be sustained" calls from analysts — in hindsight the market was pricing in a real supply-demand shift). Lesson for traders: treat implied volatility as the market's consensus forecast and ask what it might be seeing that you aren't — and how to hedge against being wrong.
- **Implied Volatility Can Change Intraday** (p.229–230, Table 7-6): worked full-day example (80 Call bid/ask IV) shows IV drifting from ~31%/32.6% (open) up to ~33.8%/35.4% (midday, as stock rallied from 76.25 to 77.95) and back down to ~31.1%/32.7% (close, as stock pulled back to 77.40) — a ~3-point intraday IV swing invisible to anyone checking only the open and close. Forecasting IV changes, like forecasting price, is "an art, not a science" (revisited in Ch.10).

## Expected Volatility (p.230–231)

- **Definition**: a loosely-used term for a trader's *forecast* of either (a) future realized volatility (leading toward delta-neutral volatility trades, Ch.8) or (b) future implied volatility (leading toward directional vol bets — buying options if IV is expected to rise, or the reverse). Per Ch.3's three-part forecast, "expected volatility" is the volatility component of that forecast. Also called "forecast volatility" or "predicted volatility."

## Many Terms for Volatility (p.231, glossary-style)

| Term | Meaning |
|---|---|
| Historic / past volatility | Stock-price action already observed |
| Option volatility / "an option's volatility" | Implied volatility |
| Future volatility | Realized volatility (not yet known) |
| Expected / forecast / predicted volatility | A trader's prediction of realized or implied volatility |
| (input to a pricing calculator) | Whatever number you enter there is, by definition, expected volatility |

## Using Volatility (p.231–232)

- Traders use volatility + price-range distributions to plan trades/choose strikes: e.g., **selling an option at least 1 SD away from the current price** on the logic that it has roughly a 68% chance of expiring worthless. Worked example: stock=78.50, 35% vol, 1-month 1-SD range=7.61 → the $70 strike (more than 1 SD below spot) put-sale has an argued ~68% edge.
- **Important caveat**: a statistical edge doesn't guarantee an outcome in any single instance — an option could still move ITM intraday/intraweek and force a stop-loss even if it would have expired worthless, and "68% over many months" says nothing about any one specific month.

## "Overvalued" and "Undervalued" (p.232–234)

- Since realized (future) volatility is unknown, an option's "true" theoretical value is unknowable — a theoretical value is only an estimate, driven by whatever volatility assumption (expected volatility) the calculator user supplies.
- **Overvalued** = market price > theoretical value ⟺ **implied volatility > expected volatility** (the trader's own forecast). **Undervalued** = market price < theoretical value ⟺ **implied volatility < expected volatility**.
- Implied volatility itself is objectively computable (from known inputs + market price); theoretical value is inherently subjective (depends on the trader's own expected-volatility forecast) — so "overvalued/undervalued" is fundamentally a subjective judgment, not an objective fact. Two traders can agree on IV but disagree on over/undervaluation if their own volatility forecasts differ.
- **An Alternative Focus** (p.234): rather than chasing the overvalued/undervalued framing, Bittman recommends spending trader effort refining the three-part forecast (price, time, implied-volatility level) from Ch.3 instead.

## Volatility Skews (p.234–238, Table 7-7, Fig 7-9)

- **Definition**: same-underlying, same-expiration options at *different strikes* trading at *different implied volatilities* — common in index/futures options, less common in individual equity options.
- **Worked real example** (Table 7-7): XSP (Mini-SPX) Index at 132.00, 25 days to expiration, 13 strikes from 120–144. ATM (132) IV = 20.83%. IV *rises* moving away from ATM in both directions — e.g., 130 strike (both call and put) IV=21.75%; deep-OTM/ITM strikes (120, 144) IV ≈ 26.25%/24.10%. The skew curve is **not symmetric** around the ATM strike and not perfectly linear (Fig 7-9's "smile"/"smirk" shape).
- **Why Skews Exist** (p.235–236): no rigorous theoretical justification — a practical explanation ties back to the insurance analogy (strike ≈ deductible): supply/demand for "cheap protection" (low-absolute-premium, far-OTM options) can push up the *implied volatility* of those options even without pushing up their absolute dollar price much, because sellers of cheap/high-leverage protection demand a higher risk premium per unit.
- **Skews Affect Trading Results** (p.236–238, worked "Barb" example): buying an XSP 126 Put (6 points OTM, IV=23.52%) on a bearish forecast that XSP falls to 126 in 10 days. If the put becomes ATM as XSP falls to 126, and the *skew stays fixed*, its IV would fall from 23.52% to the (lower) ATM level of 20.83% — even with the directional forecast entirely correct. Worked comparison: estimated profit is **1.35/share if IV stays at 23.52%** vs. only **1.05/share if IV correctly reprices down to 20.83%** as the option becomes ATM. **General conclusion**: all else equal, volatility skew is a structural *disadvantage for buyers of OTM options* (their purchased option's IV tends to compress as it approaches the money) — though changes in the overall IV level or in the skew's shape/slope can offset or worsen this in either direction, so skew must be tracked alongside the overall IV level.

## Summary

Volatility is price change magnitude without regard to direction, and different audiences use it differently: mathematically it's the annualized standard deviation of daily returns (convertible between time periods via ×√time). **Historic volatility** = observed past price action; **realized volatility** = the (unknown) future counterpart; **expected volatility** = a trader's forecast of either, used as the input to theoretical-value calculations; **implied volatility** = the volatility that reconciles a pricing formula with an option's actual market price. Implied volatility functions as options' equivalent of a stock's P/E ratio — a market-determined common denominator enabling comparison across underlyings and across time. **Volatility skew** — different strikes at the same expiration trading at different IVs — has no firm theoretical basis but is a persistent, tradeable market feature (especially in index options) that structurally disadvantages naive OTM option buyers.
