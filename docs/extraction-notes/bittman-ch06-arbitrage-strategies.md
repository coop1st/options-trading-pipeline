Source: Bittman, *Trading Options as a Professional*, Chapter 6 "Arbitrage Strategies", printed pp. 163–203.

## Arbitrage — the Concept (p.163–164)

- **Arbitrage**: buying in one market, selling in another, to lock in a **nearly riskless** (not risk-free) profit. Classic example: gold priced differently in two cities net of delivery costs — profit exists only until costs/logistics/financing risk (rate changes, tariffs, shipping delays) are accounted for; these residual risks are exactly what create (and threaten) the arbitrage profit.
- For options: an arbitrage relationship exists between stock and its synthetic equivalent (built from options, per Ch.5). A trader can buy real stock and sell synthetic stock, or the reverse, to try to capture mispricings.

## The Conversion (p.165–176)

- **Definition**: long stock + long put + short call, same strike/expiration, share-for-share. The foundational arbitrage strategy — all other option-to-stock arbitrage builds on this concept.
- **Profitability condition**: call's time value must exceed put's time value by enough to cover transaction costs, cost of carry, and target profit.
- Worked example (Table 6-1): long stock@103 + long 100 Put@4.50 + short 100 Call@8.25 → **flat $0.75/share profit at every stock price at expiration** (verified across stock prices 90–110).
- **Outcomes at expiration** (Table 6-2): stock below strike → put exercised (sells stock at strike); stock above strike → call assigned (sells stock at strike); either way the position closes with the locked-in profit. Stock exactly at strike → **pin risk** (below).

### Pin Risk (p.167–168)

- **Pin risk**: stock closes exactly at the strike at expiration — in theory both call and put expire worthless, leaving the long stock intact, but in practice it's unknown how many written calls will actually be assigned (assignment is probabilistic per Ch.1's OCC process).
- If a trader exercises all long puts assuming no call assignment, but some calls ARE assigned, a **short stock position over the weekend** results (exercise/assignment settles Friday, but any resulting stock position can't be closed until Monday) — "over-the-weekend risk."
- **Standard market-maker practice**: exercise half the long puts, hoping only half the short calls get assigned — no assignment outcome is knowable in advance, so *some* weekend stock-position risk is unavoidable. Cited as a reason arbitrage is best left to professionals.

### Pricing a Conversion (p.168–177)

- **Conceptual model**: a conversion's value ≈ a Treasury bill's discounted-present-value (DPV) structure — pay less than face value now, receive face value (here, the strike price) at maturity (expiration); the spread is the "interest" earned.
- **Formula**: `DPV of strike = strike × [1 − (borrowing rate × days/365)]`.
- Net investment per share = `DPV of strike − (transaction costs + target profit)`.
- Given net investment and known stock/put prices, solve for the required call price: `Call = Stock − Put − NI` is rearranged from `Stock + Put − Call = NI` (i.e., long stock + long put − short call = net investment).
- **Worked example** (Tables 6-3–6-5): strike 55, stock 57.70, 55 Put 1.45, 5% borrow rate, 60 days, costs 4¢/share, target profit 5¢/share → DPV of strike = 54.55 → NI = 54.55 − (0.04+0.05) = 54.46 → solves for 55 Call = 57.70 + 1.45 − 54.46 = **4.69**.
- **Cash-flow breakdown** (Table 6-5): revenue (strike, 55.00) − cost (NI, 54.46) = gross profit 0.54; minus borrowing cost (NI × rate × days/365 = 0.44) = profit before costs 0.10; minus transaction costs (0.04) = **net profit 0.06** (vs. 5¢ target — gap from rounding).
- **Key identity**: `time value of call − time value of put = gross profit` (0.54 in the example: call time value 1.99 minus put time value 1.45 = 0.54, matching strike−NI).
- **Competition**: market makers may accept sub-target profit if competitors quote tighter — part of "the art" of market making; also compare opportunities across strikes/underlyings for the best available edge.

### Pricing a Conversion with Dividends (p.173–176, Tables 6-6–6-8)

- A dividend is extra income to a stock *owner*, so it **reduces** the call price needed (the position becomes more attractive to hold, so less call premium is needed to hit the target). Formula shifts to `DPV of (strike + dividend)` (treats the dividend as economically equivalent to extra proceeds at expiration, ignoring the small timing/interest difference, which is usually <1¢).
- Worked example: same inputs as base case + 22¢ dividend → DPV of (55+0.22) = 54.77 → NI = 54.68 → 55 Call price drops from 4.69 to **4.47** (exactly the 22¢ dividend).
- **Ex-dividend date / record date mechanics**: the **ex-date** is the first day a new buyer does *not* receive the upcoming dividend. Stock trades settle **T+3**; to receive the dividend, settlement must land on or before the **record date** (the day you must already be a shareholder of record). Worked calendar example: record date Friday May 7 → buying Tue May 4 settles Fri May 7 (in time, dividend received); buying Wed May 5 settles Mon May 10 (too late — Wed May 5 is therefore the ex-date).

### Pricing Conversions by Strike Price (p.176–177, Table 6-9)

- As strike price rises (holding rate/days/costs/target profit constant), the required call-time-value-over-put-time-value gap **widens** — because a higher strike means more borrowed capital (DPV scales with strike), hence higher financing cost that must be recovered. Table 6-9 shows the gap rising from 46¢ (strike 45) to 62¢ (strike 62) as strike rises in $5 increments (borrowing 5%, 60 days, no div, costs 4¢, target profit 5¢, gap increases roughly $0.04 per $5 of strike).

### The Concept of Relative Pricing (p.177–178)

- **Relative pricing**: given the conversion's fixed call-minus-put time-value gap for a strike, knowing any two of {stock, call, put} prices lets you solve for the third. Historically (open-outcry era) market makers computed this gap once per strike each morning, then quoted calls/puts off it all day as stock/order flow moved; today this is computer-automated, but traders must still understand the logic to override/adjust the model when needed.

## The Reverse Conversion (p.178–188)

- **Definition** ("the reversal"): short stock + short put + long call, same strike/expiration, share-for-share — the opposite of a conversion (buys synthetic stock, sells real stock). Established for a **net credit**, invested at the risk-free rate.
- **Profitability condition**: interest earned on the net credit must exceed transaction costs plus (call time value − put time value).
- Worked example (Table 6-10): short stock@102 + short 100 Put@5.25 + long 100 Call@6.50 → flat **$0.75/share profit** at every stock price (mirrors the conversion's structure).
- **Outcomes at expiration** (Table 6-11): stock below strike → put assigned (buys stock at strike, covering the short); stock above strike → call exercised (buys stock at strike). Either way the position closes. Stock exactly at strike → **pin risk again** (same "exercise half, hope for the best" practice as conversions).

### Pricing a Reverse Conversion (p.181–186)

- **Conceptual model**: opposite of the conversion's T-bill analogy — like borrowing money (via the short-stock proceeds) to be repaid, with interest, when the position closes.
- **Formula**: `DPV of strike = strike × [1 − (lending rate × days/365)]`; net credit required (NC) = `DPV of strike + costs + target profit`; solve for call price via `Call = Stock − Put − NC` is rearranged from `−Stock − Put + Call = −NC`.
- Worked example: strike 55, stock 57.70, 55 Put 1.45, 4% lending rate, 60 days, costs 4¢, target profit 5¢ → DPV=54.64 → NC=54.73 → 55 Call = 57.70 − 1.45 − 54.73 = **4.42** (wait, actual worked value per text: Call = Stock − Put − ... solved to 4.42, matches `stock − put − NC` sign convention used in the source).
- **Cash flow** (Table 6-14): revenue (NC, 54.73) − cost (strike paid at expiration, 55.00) = gross **loss** 0.27; + interest income (NC × rate × days/365 = 0.36) = profit before costs 0.09; − transaction costs (0.04) = **net profit 0.05**.
- **Key identity**: `time value of call − time value of put = |gross loss|` (0.27 = 1.72 − 1.45).
- **Competition and Reverse Conversions** (p.184–185): same dynamic as conversions — if competing market makers bid a tighter price than the target-profit-derived price (e.g., bidding 4.44 for the 55 Call vs. a trader's target-implied 4.42), the trader must accept a thinner profit or pass on the trade; deciding which reverse-conversion opportunities are "acceptable" across strikes/underlyings is again part of the market-making skill set.
- **Dividends increase costs for reverse conversions** (opposite of conversions) — a short-seller of stock owes the dividend to the stock's lender, so `DPV of (strike + dividend)` raises the required net credit, which **lowers** the affordable call purchase price (worked example: dividend 22¢ → 55 Call drops from 4.42 to **4.20**).
- **Pricing by strike** (Table 6-18): same directional logic as conversions — required call-minus-put time-value gap widens as strike rises (39¢ at strike 45 up to 51¢ at strike 65, per the table), because a higher strike means more interest income potential/opportunity cost to account for.

## Box Spreads (p.188–202)

- **Definition**: 4-part, options-only arbitrage (no stock leg) — a long call + short put at one strike, and a short call + long put at another strike. Two variants:
  - **Long box** (net debit): long call + short put at the *lower* strike, short call + long put at the *higher* strike. Equivalent framing: (a) long synthetic stock at lower strike + short synthetic stock at higher strike, or (b) a bull call spread + a bear put spread (same two strikes).
  - **Short box** (net credit): mirror image — short call + long put at lower strike, long call + short put at higher strike. Equivalent framing: (a) short synthetic stock at lower strike + long synthetic stock at higher strike, or (b) a bear call spread + a bull put spread.
- **Long box worked example** (Table 6-19): long 90 Call@6.50 + short 90 Put@2.00 + short 100 Call@2.25 + long 100 Put@7.00 → flat **$0.75/share profit** at every stock price. **Profitability condition**: (difference between strikes − cost of position) > cost of carry.
- **Long box outcomes at expiration** — 5 possible cases (Table 6-20): stock below lower strike, exactly at lower strike, between strikes, exactly at higher strike, or above higher strike. The three "clean" outcomes (below/between/above) all net to receiving exactly the strike-price difference (10 points in the example) via simultaneous stock purchase+sale from exercise/assignment, closing the position with no residual stock. The two "exactly at a strike" outcomes create **double pin risk** (see below).
- **Long Box — Double Pin Risk** (p.192): landing exactly on either strike leaves an in-the-money option from the *other* strike creating an unpredictable stock position (short stock if pinned at the lower strike, long stock if pinned at the higher strike) — same "exercise half the ATM longs" mitigation as single conversions, but now the risk exists at *both* strikes.
- **Pricing a long box** (Tables 6-21–6-23): value = DPV of (strike spread) minus costs minus target profit. Formula: `NI = DPV(strike₂ − strike₁) − (costs + target profit)`; solve for the unknown leg via algebra on `Call₁ − Put₁ − Call₂ + Put₂ = NI`. Worked 100-110 box example: DPV(10)=9.92, NI=9.81, known legs 100 Call=9.10/100 Put=2.30/110 Put=6.70 → solves 110 Call = **3.69**. **Key identity**: value of the (debit) call spread + value of the (debit) put spread = net investment (5.41 + 4.40 = 9.81).
- **Relative pricing applies to box spreads too** — knowing the box's target value and 3 of the 4 leg prices (or one of the two vertical-spread values) solves for the rest.
- **Short box worked example** (Table 6-24): short 90 Call@6.50 + long 90 Put@2.00 + long 100 Call@1.50 + short 100 Put@7.50 → flat **$0.50/share profit**. **Profitability condition**: (credit received + interest earned) > (strike spread + costs).
- **Short box outcomes/pin risk** mirror the long box (Table 6-25) — same 5 outcomes, same double-pin-risk exposure at both strikes.
- **Pricing a short box** (Tables 6-26–6-28): `NC = DPV(strike spread) + costs + target profit`; solve unknown leg similarly. Worked 100-110 example: DPV=9.93 (4% lending rate), NC=10.04 → solves 110 Call = **3.46**. **Key identity**: credit call spread value + credit put spread value = net credit (5.64+4.40=10.04).
- **Motivations for establishing a short box** (p.202–203): market makers who run books across many underlyings often carry *both* conversions (net debit, needing borrowed funds) and reverse conversions/short boxes (net credit, generating lendable funds) simultaneously — internally offsetting borrowing against lending can save the borrow-lend rate spread (e.g., borrowing at 5% vs. lending at 4% — using your own credit balances to fund your own debit balances saves that 1% spread). This isn't unlimited, though: every position (even low-risk arbitrage) consumes some **capital/equity requirement**, so how aggressively a market maker can cross-subsidize rates depends on available capital relative to position size.

## Summary

Arbitrage exploits price differences between markets for near-riskless profit; in options, this means trading real stock against its synthetic equivalent (Ch.5) or vice versa. The **conversion** (long stock + long put + short call) is the foundational strategy — profitable when call time value exceeds put time value enough to cover carrying/transaction costs; its **reverse** (short stock + short put + long call) profits when interest earned on the resulting credit exceeds costs plus that same time-value gap. **Box spreads** are the options-only, no-stock-leg version of the same idea — a **long box** (net debit) locks in the strike-price spread if its cost is cheap enough versus carry; a **short box** (net credit) locks it in if the credit-plus-interest is rich enough versus the eventual payout. All four strategies share the same core risks: **pin risk** (uncertain assignment when the stock settles exactly at a strike, creating unavoidable weekend stock-position exposure) and dependence on precise, constantly-updated interest-rate/cost/dividend assumptions for correct pricing.
