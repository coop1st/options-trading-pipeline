Source: Bittman, *Trading Options as a Professional*, Chapter 3 "The Basics of Option Price Behavior", printed pp. 49–75.

## The Insurance Analogy (p.49–53)

- Puts ≈ insurance against a real loss (owned asset declining). Calls ≈ insurance against an "opportunity loss" (missing a rally while holding cash/liquid assets, i.e., insuring participation in a price rise).
- **Insurance premium has 5 components** → **option value has 6 components** (mapping, Table 3-1):
  1. Asset value → **Price of underlying** (direct effect on calls, inverse on puts)
  2. Deductible → **Strike price** (inverse on calls, direct on puts) — an OTM option is like a policy with a deductible (pays nothing unless the underlying moves past the strike); an ATM option is like a policy with no deductible.
  3. Term/time to expiration → **Time** (direct effect on both calls and puts — more time = more value, since values decay toward expiration)
  4. Interest rates → **Interest rates** (direct on calls, inverse on puts) — insurance premiums decline as rates rise because insurers invest premiums; options: rate increases raise call value/lower put value, tied to put-call parity (Ch.5). Effect is small for short-term options but material to arbitrage pricing (Ch.6).
  5. Risk → **Volatility** (direct effect on both calls and puts) — conceptually identical to insurance risk assessment.
  - **Dividends** is the extra 6th option-value component with no insurance analogue: effect is opposite interest rates (dividend increase → call value down, put value up). Small effect for speculative traders, material for arbitrage (Ch.6).
- Table 3-2 (component → effect on call/put): Price of Underlying (Direct/Inverse), Strike Price (Inverse/Direct), Time (Direct/Direct), Interest Rate (Direct/Inverse), Dividends (Inverse/Direct), Volatility (Direct/Direct).
- Insurance companies (and option market makers) also price against competition, not pure formula — a judgment call on whether to "meet the market" or hold back.

## Option-Pricing Formulas (p.53–54)

- **Black-Scholes** (Black & Myron Scholes, 1973): closed-form, advanced calculus.
- **Binomial models** (Cox/Ross, Rubinstein, Hull and others): discrete-step, present-value-of-outcomes approach — used by Op-Eval Pro alongside Black-Scholes (per Ch.2).
- Different formulas produce similar results in practice; book's exhibits use standard Black-Scholes, rounded to 2 decimals.

## Call Values and Stock Prices (p.54–56, Table 3-3, Fig 3-1)

- Table 3-3: theoretical values of a 100 Call at stock prices 95–105, at 0/15/30/45/60/75/90 days to expiration (5% interest, 30% vol, no dividends) — full table captured. E.g., at 90 days: 100 Call = 6.53 at stock=100; rises to 7.11 at stock=101 (+0.58, i.e., "delta of 58"); falls to 5.99 at stock=99 (−0.54).
- **Key finding**: an option's price always changes *less than one-for-one* with the underlying, and the ratio (delta) varies with both stock price and time remaining.
- Delta increases as the option moves further ITM: e.g., at 45 days, a $1 move from 97→98 moves the call ~45% (0.45); at 60 days, a $1 move from 102→103 moves it ~63% (0.63).
- Fig 3-1 shape: call value near zero deep OTM, rises slowly approaching the strike, rises faster near/above the strike, and approaches 1:1 with the underlying deep ITM — but theoretically never exactly 1:1 pre-expiration (always retains a slight time premium).

## Put Values and Stock Prices (p.56–59, Table 3-4, Fig 3-2)

- Same dynamics as calls but **inversely correlated** with the underlying: put values rise as stock falls, fall as stock rises. Full Table 3-4 captured (100 Put values, same price/time grid as Table 3-3).
- Example: 100 Put at 90 days = 5.31 at stock=100; rises to 5.76 at stock=99 (+0.45); falls to 4.88 at stock=101.
- Fig 3-2 shape: mirror image of the call curve — near zero deep OTM (stock far above strike), approaches 1:1 deep ITM (stock far below strike), never exactly 1:1 pre-expiration.

## Delta (introduced here, detailed in Ch.4) (p.59)

- **Delta** = the change in an option's theoretical value given a one-unit change in the underlying's price, expressed as a ratio/percentage. Calls have positive delta (e.g., "delta of 58" = 0.58 = 58%); puts have negative delta (e.g., "delta of 53" = −0.53, i.e., rises $0.53 when stock falls $1).

## Call Values Relative to Put Values (p.59–60)

- Common misconception: ATM call and put (same strike/expiration) should have equal value. **They don't** — assuming no dividends, call value > put value because calls contain an interest-rate component puts lack (evidenced comparing Table 3-3 row 6 to Table 3-4 row 6: at 90 days, 100 Call=6.53 vs. 100 Put=5.31).
- The underlying reason is **put-call parity** (detailed in Ch.5) — a no-arbitrage relationship between stock price, call price, and put price. Deviations from parity create fleeting arbitrage opportunities that professional market makers compete away within cents/short timeframes, but the volume they trade makes capturing these worthwhile.

## Option Values and Strike Price (p.60–62, Table 3-5)

- Raising the strike (further OTM, "bigger deductible") lowers call value, holding stock price/other factors constant. Worked example (Table 3-5, stock=100, 60 days, 30% vol): 100 Call=6.53 → 105 Call=4.37 → 110 Call=2.80 as strike rises; conversely 100 Put=5.31 → 105 Put=8.08 → 110 Put=11.45 as strike rises.
- Stock splits change strike prices but don't change moneyness (e.g., a 2:1 split from 100→50 turns a 110 Call OTM-by-10% into a 55 Call, still OTM-by-10%) — the value change from a split is driven by the *stock price change*, not the strike change itself.
- 2007 rule change: for splits other than 2-for-1 and 4-for-1, only the deliverable is adjusted (not strike or premium multiplier) — per SEC Release No. 34-55258.

## Option Values and Time to Expiration / Theta (p.62–64, Fig 3-3)

- Option values decay toward zero (time value) as expiration nears, holding other factors constant.
- **Theta** = the theoretical change in option value given a one-unit change in time to expiration (day, week, etc. — user-definable unit; discussed fully in Ch.4).
- **ATM decay pattern** (Fig 3-3A): roughly linear/slow initially, then a sharp drop in the final ~30 days (100 Call at stock=100: 6.53→5.92→5.25 at 90/75/60 days; loses only ~31% of value in the first half of its life (90→45 days: 6.53→4.50), ~30-31% again per subsequent halving period 60→30 days and 30→15 days).

## Time Decay Is Complicated (p.64–67, Table 3-6)

- **OTM and ITM options decay differently from ATM options.**
  - OTM calls (Fig 3-3B, e.g., 110 Call w/ stock=100): decay is nearly a straight line across time, with the *least* decay in the final week (opposite of ATM).
  - ITM calls (Fig 3-3C, e.g., 90 Call w/ stock=100): only the time-value portion (not intrinsic value) decays — e.g., a 90 Call worth 12.82 at 90 days with stock=100 has only 2.82 of decay-able time value; it settles at its 10.00 intrinsic value at expiration.
- **Volatility interacts with time decay for OTM options** (Table 3-6, full table captured: 100/105/110 Calls × 20%/30%/40% vol × 56 days down to expiration):
  - ATM (100 Call): decay rate ~constant regardless of volatility level — loses ~31% of value in first half of life, ~69% in second half, at all three vol levels.
  - 5% OTM (105 Call): decay rate *changes* with volatility — at 20% vol, loses 56% in first half/44% in second half; at 30% vol, 47%/53%; at 40% vol, 42%/58%. Higher volatility → less decay in the first half, more in the second.
  - 10% OTM (110 Call): same directional pattern, more pronounced — at 20% vol, 79%/21% split; at 30% vol, 65%/35%; at 40% vol, 54%/46%.
- **Three conclusions**: (1) OTM options decay differently than ATM (more early, less late — opposite of ATM's less-early/more-late pattern); (2) the further OTM, the more decay happens in the first half of life; (3) higher volatility shifts more of an OTM option's decay into the second half of its life.
- **Alternatives for Premium Sellers**: this data suggests that for options 5–10% OTM, selling 2-month options and covering them 1 month before expiration (then rolling into the next 2-month option) can capture more time premium than selling 1-month options every month — a direct consequence of the decay-rate-by-moneyness finding above.

## Option Values and Interest Rates (p.67–69, Fig 3-4)

- Call values rise with rising interest rates; put values fall — a direct consequence of put-call parity (Ch.5).
- Effect is small in practice: raising rates from 3%→5% moves a 90-day ATM 100 Call (stock=100, 30% vol, no div) from 6.29→6.53.
- Small day-to-day impact on speculative decisions, but material for arbitrage-strategy pricing (Ch.6) — large rate moves historically coincide with other macro/volatility shocks that dominate the price impact anyway.

## Option Values and Dividends (p.69)

- Opposite effect of interest rates: with no dividends, call value exceeds put value by the cost-of-money (interest) component; dividends effectively offset that cost of money (dividend proceeds can fund the equivalent of the interest cost), so rising dividends lower call value and raise put value. **Call and put values are equal when dividend yield = interest rate.**

## Option Values and Volatility (p.69–71, Fig 3-5, 3-6)

- Volatility = a measure of price fluctuation magnitude, without regard to direction (fully covered in Ch.7). Higher volatility → higher option value for both calls and puts.
- **ATM options**: value changes roughly *linearly* with volatility, regardless of time to expiration (Fig 3-5A).
- **OTM options** (e.g., 10% OTM 110 Call, Fig 3-5B): the volatility-value relationship is *not* linear and depends on both time to expiration and distance from the strike.
- **Extreme Volatility** (Fig 3-6): as volatility → very high levels (chart shown to 1,000%), a call's value approaches its theoretical ceiling of the underlying's price itself (no rational buyer pays more for a call than for the stock outright); symmetrically, a put's ceiling is the strike price (since the underlying can't go below zero).

## Dynamic Markets (p.71–72)

- Real markets move more than one factor simultaneously (price, time, *and* volatility all shift together over days/weeks) — interest rate and dividend changes are typically small/predictable enough to ignore in short-term scenario planning (dividends are discussed further in Ch.6).

## Three-Part Forecasts (p.72)

- Unlike stock traders (who forecast direction only), **option traders must forecast three things: direction (price), time, and implied volatility level.** (Volatility forecasting detailed in Ch.7.)
- Illustrative point: the same price-target forecast achieved over *more* time (15 extra days) produces a meaningfully smaller option-price gain (e.g., 100 Call moving 4.97→6.49 over a fast move vs. only to 5.82, ~40% less gain, if the same price move takes 15 days longer).

## Trading Scenarios (p.72–75, Table 3-7) — the "Joe / Jumpco" worked example

Full 3-scenario worked example, illustrating why a 3-part (price/time/volatility) forecast matters, not just a directional call:

- Setup: Jumpco stock at $67, considering the April 75 Call (currently priced 0.50, implied vol 38%, computed via the method in Ch.7), 16 days to April expiration, 4% interest, 2% dividend yield. Joe expects a bullish earnings surprise in 3 days that could send the stock to $74 (+10%).
- **Scenario 1** (stock +10% to $74 in 7 days, IV unchanged at 38%): call value rises 0.50 → 2.10, **+320%**.
- **Scenario 2** (same price move, but IV reverts to a more "typical" 25% for Jumpco): call value rises 0.50 → 1.25, **+150%** — still large, but less than half of Scenario 1's gain, purely from the volatility assumption changing.
- **Scenario 3** (stock up only +5% to $70.50, IV reverts to 25%): call value *falls* 0.50 → 0.30, **−40%** — despite still being directionally right, a smaller move combined with IV compression produces a loss. Max risk on a long call is 100% of premium paid.
- Takeaway: multi-scenario analysis across price/time/volatility combinations (using tools like Op-Eval Pro, Ch.2) is what distinguishes disciplined option speculation from simple directional stock betting — Joe proceeds with the trade only after seeing it survive a less-favorable-but-plausible scenario.

## Summary

Options are insurance-like: puts insure owned assets, calls insure against missing a rally. The insurance-premium-factor analogy maps cleanly onto the six option-value components (underlying price↔asset value, strike↔deductible, time↔time, interest+dividends↔insurance interest-rate effect, volatility↔risk). Option prices always move less than 1:1 with the underlying pre-expiration (delta captures the ratio). Time decay reduces value toward expiration, but its *rate* depends heavily on moneyness (ATM decays slowly then fast, nonlinearly; ITM/OTM decay differently — increasing for a while, then slowing near expiration). Interest rates directly affect calls and inversely affect puts; dividends are the mirror image (dividends up → calls down, puts up). Volatility directly raises both put and call prices, and while it's a statistical concept, it can be reasoned about intuitively even without the underlying math. Markets are dynamic (multiple factors move together), so option traders must forecast three dimensions (price, time, volatility), not just direction, and analyze multiple scenarios — as the Joe/Jumpco example demonstrates — to form realistic expectations about a trade's potential profit and risk.
