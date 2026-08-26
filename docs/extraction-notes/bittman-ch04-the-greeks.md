Source: Bittman, *Trading Options as a Professional*, Chapter 4 "The Greeks", printed pp. 77–131.

## Overview (p.77–78)

Five Greeks, each an estimate of option-value change given a one-unit change in one pricing input, holding others constant:
- **Delta**: sensitivity to underlying price.
- **Gamma**: sensitivity of *delta* to underlying price (delta's rate of change).
- **Vega**: sensitivity to volatility.
- **Theta**: sensitivity to time passing.
- **Rho**: sensitivity to interest rates.

Essential preparation for Ch.10 (position-risk management).

## Delta (p.78–80)

- Definition: estimated change in option value per one-unit change in underlying price, other factors constant. Mathematically the first derivative of value w.r.t. underlying price. Answers: "if the stock moves $1, how much do I make/lose?"
- Baseline example used throughout the chapter (Tables 4-1–4-19): stock=100, strike=100, vol=30%, rate=4%, 60 days, no dividends → 100 Call value 5.19/delta 0.55; 100 Put value 4.59/delta 0.46 (approx.; put delta magnitude ≈ 1 − call delta per put-call parity).
- Table 4-1: stock 100→101 (+1) ⇒ 100 Call 5.19→5.74 (+0.55, matching delta); 100 Put 4.59→4.13 (−0.46, matching delta). Deltas only *predict* — actual moves differ slightly (explained by gamma, next section).
- **Call deltas are positive** (direct relationship with underlying). **Put deltas are negative** (inverse relationship). Note: the sign convention for an option's own delta differs conceptually from the sign convention for a *position's* delta (see Position Greeks below).
- A $1 underlying move causes bigger $-changes in ITM option values, moderate in ATM, smallest in OTM.
- Op-Eval Pro: delta shown under call/put values on the Single Option Calculator; on Spread Positions/Portfolio screens, individual-leg deltas appear in the "DELTA" row and a summed "Spread delta" is shown separately.

## Gamma (p.80–83)

- Definition: the change in delta per one-unit change in underlying price, other factors constant — the second derivative of value w.r.t. underlying price. Answers: "how much does my delta (market exposure) change when the underlying moves?"
- Table 4-2: stock 100→101 ⇒ 100 Call delta 0.55→0.58 (Δ=0.03=gamma); 100 Put delta −0.46→−0.43 (Δ=+0.03 — an *increase* in the (negative) put delta; watch signs carefully). Table 4-3: stock 100→99 ⇒ both call and put deltas *decrease* (100 Call delta 0.55→0.51; 100 Put delta −0.46→−0.50).
- Rounding note: at 2-decimal precision the call/put gammas look identical (0.03), but at 4-decimal precision they differ slightly (e.g., call gamma 0.0327→0.0321, put 0.0335→0.0328 after a 1-point move) — small per-share but can matter at large position size or bigger (5%+) underlying moves.
- **Gammas are always positive for both calls and puts** (delta and underlying price change are always positively correlated in the same direction: price up → delta up, for both call and put deltas, even though put delta itself is negative).
- **Gammas of same-strike/same-expiration calls and puts are nearly equal** — a consequence of put-call parity: |call delta| + |put delta| ≈ 1.00 always, so a rise in one's absolute delta must be offset by an equal fall in the other's, meaning their *rates of change* (gammas) match. (Put-call parity detailed in Ch.5.)

## Vega (p.83–85)

- Definition: change in option value per one-percentage-point change in the volatility assumption, other factors constant (first derivative of value w.r.t. volatility). Full treatment of volatility itself is in Ch.7. Answers: "if IV moves 1%, how much do I make/lose?"
- Table 4-4: vol 30%→31% ⇒ 100 Call 5.19→5.35, 100 Put 4.59→4.75 (both vega=0.16).
- **Vegas are always positive for both calls and puts** (value is always positively correlated with volatility).
- **Vegas of same-strike/same-expiration calls and puts are equal** — another put-call-parity consequence (a volatility change must move the parity-linked call and put by the identical amount).
- **Naming note**: "vega" is not an actual Greek letter — origin is murky (theorized: traders wanted a "v" word, for volatility, that sounded like delta/gamma/theta). Some traders/mathematicians use kappa or lambda instead — no universal convention exists.

## Theta (p.85–89)

- Definition: change in option value per one-unit change in time to expiration, other factors constant (first derivative w.r.t. time — theoretically instantaneous, so practitioners pick a practical unit: one day is common among professionals; retail traders may use a week, 10 days, etc. — no universally "right" unit). Answers: "if time passes, how much do I make/lose?"
- Table 4-5: days 60→53 ⇒ 100 Call 5.19→4.86 (theta=0.33 over 7 days), 100 Put 4.59→4.33 (theta=0.26 over 7 days). Op-Eval Pro lets the user set the theta time unit (up to 999 days); it auto-switches to a 1-day theta if days-to-expiry ≤ the configured theta window (avoids nonsensical "7-day theta" with only 6 days left).
- **Call and put thetas differ** even at the same strike/expiration/underlying, because they carry different time-value amounts (calls have an extra interest-rate component vs. puts, per Ch.5/Ch.6 arbitrage discussion), so they decay to zero at different rates.
- **Thetas are (usually) negative** — an owned option loses value as time passes. Convention assumes a *long* position; the negative sign reflects decay, even though the underlying "more time = more value" relationship is itself positive.
- **Exception**: deep ITM *European-style* options can theoretically be priced *below* intrinsic value (since early exercise isn't possible — arbitrage pricing per Ch.6), producing a *positive* theta — value rises toward intrinsic as expiration nears.

## Rho (p.87–89)

- Definition: change in option value per one-percentage-point change in interest rates, other factors constant. Answers: "if rates move 1%, how much do I make/lose?"
- Table 4-6: rate 4%→5% ⇒ 100 Call 5.19→5.27 (rho=+0.08); 100 Put 4.59→4.52 (rho=−0.07).
- **Rho is positive for calls, negative for puts** — a consequence of put-call parity's cost-of-carry relationship (cost of carry = the expense of financing/holding the underlying, mostly interest net of dividends; detailed in Ch.6). Rising rates raise the cost of carry, which must widen the call's time value relative to the put's (in practice, call value rises a little *and* put value falls a little — the net difference is the cost-of-carry change).
- Small effect on short-term option values → low priority for non-professional short-term traders, but material to arbitrageurs (Ch.6).

## How the Greeks Change (p.89–92, Tables 4-7 & 4-8)

Two reference tables used throughout the rest of the chapter (both fully captured):
- **Table 4-7**: 100 Call/100 Put values + delta/gamma/vega/theta(1-day)/rho at stock prices 100/105/110, across 56/42/28/14 days and at expiration (30% vol, 5% rate, no div). Shows how Greeks evolve as an option moves from ATM (stock=100) toward ITM (call, at stock=110)/OTM (put, at stock=110), and as time passes.
- **Table 4-8**: 90/100/110 Calls, at 25% and 50% volatility, across the same day-columns (stock fixed at 100, 5% rate). Shows how Greeks and moneyness interact with volatility level.

### How Delta Changes — 5 rules (p.92–99, Figs 4-1–4-3)

1. **Deltas and stock price**: |delta| of both calls and puts rises as stock price rises, falls as stock price falls (e.g., at 56 days, 100 Call delta 0.55→0.71→0.82 as stock 100→105→110; 100 Put delta 0.45→0.30→0.18 over the same moves).
2. **Deltas and strike (moneyness)**: ITM options always have |delta| > 0.50; ATM options ≈ 0.50; OTM options < 0.50 — true regardless of time to expiration.
3. **Deltas and time to expiration**: |delta| of ITM options increases toward 1.00 as expiration nears (e.g., 100 Call at stock=110: 0.82→0.89→1.00 across 56→28→0 days); |delta| of ATM options stays near 0.50 throughout; |delta| of OTM options decreases toward 0.00 as expiration nears (e.g., 100 Put at stock=105: 0.30→0.25→0.00).
4. **Deltas of same-strike calls and puts**: |call delta| + |put delta| ≈ 1.00 always (put-call parity corollary — e.g., 0.55 + 0.45 = 1.00).
5. **Deltas and volatility**: rising volatility pushes |delta| *toward* 0.50 (OTM deltas rise, ITM deltas fall) — because volatility rising increases the standard deviation of expected price range, effectively moving a fixed-strike option "closer" to the money in standard-deviation terms. E.g., 90 Call (ITM) delta falls 0.89→0.75 as vol rises 25%→50%; 110 Call (OTM) delta rises 0.30→0.36. ATM delta stays ≈0.50 across a wide vol range, but at *very low* volatility (e.g., 1%), ATM delta can rise sharply toward 1.00 because the tiny option value becomes highly price-correlated (worked micro-example: 1% vol, 60-day ATM 100 Call value 0.82/delta 0.98; a 10-cent stock rise to 100.10 → value 0.92/delta 0.99).

**Option Prices and Volatility** (p.98, using Table 4-8): doubling volatility from 25%→50% increases an ITM 90 Call by only 24% (11.26→13.94), an ATM 100 Call by 90% (4.30→8.20), and an OTM 110 Call by 430% (1.02→4.39) — OTM option values respond *exponentially* to rising volatility, ATM roughly linearly, ITM less than proportionally. Practical implication: pure-OTM positions carry outsized IV risk vs. ATM/ITM, which is why full-time traders holding OTM options often use vertical spreads to cut IV exposure.

### How Gamma Changes (p.99–104, Figs 4-4–4-6)

- **Gamma is largest ATM**, and grows as expiration approaches (for ATM options specifically) — this is why an ATM option can seem to "explode" in value as the underlying crosses the strike, delighting long option holders and alarming short sellers.
- Worked example ("Debra"): buys 100 Call at 5.08 (stock=100, 56 days). Stock rises to 110 at 28 days → call worth 10.88 (+5.80 unrealized profit). Stock then falls $5 over the next 2 weeks (now deep ITM, delta risen to 0.89) → call falls to 5.84 — nearly all profit erased in half the time/half the price reversal, because the position's delta had grown much larger by the time of the reversal.
- **Call and put gammas (same strike/expiration) are equal** — put-call parity consequence (as with vega/delta sums above).
- **ITM/OTM gammas** rise only slightly until ~30 days before expiration, then *decrease* to zero — i.e., delta changes at a nearly constant rate until the last month, then changes less. (E.g., an ITM call's delta might move 0.75→0.77 for a $1 stock move at 4-5 months out (gamma 0.02), but only 0.75→0.76 with 1 week left (gamma 0.01).)
- **ATM gamma** stays small/nearly constant until about a month before expiration, then rises dramatically, then collapses to zero exactly at expiration — reflecting the "coin flip" nature of an ATM option settling either fully ITM (delta→1.00) or fully OTM (delta→0.00) at the last instant (a 2-cent move from 99.99 to 100.01 near expiration can flip a call's delta from 0.00 to 1.00 — a near-infinite gamma).
- **Gamma and volatility**: for ITM/OTM options, gamma *rises* with volatility from ~10-20%, then *falls* as volatility rises further above ~30% (because rising vol pushes delta toward 0.50, which reduces the *marginal* delta sensitivity). For ATM options, gamma is roughly flat across most volatility levels but spikes dramatically at *very low* volatility (a small price move becomes a large standard-deviation move when the standard deviation itself is tiny).

### How Vega Changes (p.104–108, Figs 4-7–4-9)

- **Vega is largest ATM** (biggest absolute price impact from a 1% vol change) — e.g., doubling vol 25%→50%: ITM 90 Call +2.68 (11.26→13.94), ATM 100 Call +3.90 (4.30→8.20, the largest move), OTM 110 Call +3.37 (1.02→4.39, less than ATM but more than the ITM's absolute move despite starting from the lowest base).
- **Vegas decrease as expiration approaches** for all moneyness levels (less time = less room for the underlying to move, so less price sensitivity to a vol assumption) — but ATM vegas stay elevated longer than ITM/OTM vegas as expiration nears.
- **Vegas and volatility**: for ATM options, vega is roughly *constant* above ~10% volatility, so the value-vs-volatility relationship is close to linear for ATM options in that range (worked check: 100 Call at row E vega 0.16 → 25 points × 0.16 + 4.30 ≈ 8.30 ≈ actual 8.20 at 50% vol, small gap from rounding). For ITM/OTM options, vega is near zero below ~10% vol, rises through ~50% vol, then flattens — so the linear-extrapolation trick that works for ATM options *fails* for ITM/OTM (worked check: 110 Call row D vega 0.11 → 25×0.11+1.02=3.77, far from the actual 4.39 at 50% vol — confirms non-linearity).

### How Theta Changes (p.108–111, Figs 4-10–4-12)

- **Theta is smallest (i.e., largest |theta|, fastest decay) for ATM options** — ATM options carry the most time value of any strike at a given expiration, so they have the most to lose per unit of time.
- **ATM thetas** shrink in absolute terms as expiration nears then collapse to zero almost immediately before expiration (theta gets *bigger* in magnitude right up until the very end) — e.g., 100 Call theta (1-day) at stock=100: 0.05 (56d) → 0.06 → 0.07 → 0.09 (14d) → 0 at expiration.
- **ITM/OTM thetas** behave differently: they get *larger in magnitude* for a while, then get *smaller* (less decay per day) as expiration nears — the opposite pattern from ATM. Because ITM/OTM/ATM thetas evolve so differently, blanket generalizations about "time decay accelerates near expiration" are unsafe without checking moneyness.
- **Using theta with delta**: a long-option trader can combine theta and delta to solve for the underlying move needed, over a given holding period, to offset time decay — worked example: theta=0.05/day, delta=0.35 → a trader needs roughly a $1.00 move in 7 days for the delta-driven gain (0.35 × $1.00) to offset the theta-driven loss (7 × 0.05 = 0.35). Gives a trader a concrete price/time target for a subjective forecast.
- **Thetas and volatility**: theta magnitude *increases* (more decay per day) as volatility rises, for ITM/ATM/OTM alike — logical, since higher vol means a higher option value with more time-value to erode over the same remaining time.

### How Rho Changes — 4 rules (p.111–118, Figs 4-13–4-15)

Generally the least important Greek for most traders (small in absolute terms; rates rarely move >1% quickly), but four rules:
1. **Sign**: rho positive for calls, negative for puts (cost-of-carry / put-call-parity consequence — see Rho definition above).
2. **Rho and stock price**: rho *increases in magnitude* as the underlying price rises, for both calls and puts (e.g., 100 Call rho at 56 days: 0.08→0.10→0.12 as stock 100→105→110) — because financing a higher-priced stock costs more, so rate changes matter proportionally more.
3. **Rho and time to expiration**: rho increases in an almost *linear* fashion as time to expiration lengthens (more time = proportionally more financing-cost exposure).
4. **Rho and volatility** (most complex rule): volatility affects rho only *indirectly*, through its effect on option price — a higher-priced option (from higher vol) has more "foregone interest" at stake, so its rho grows too. For an OTM call, rising volatility raises rho *exponentially* up to ~50% vol, then the effect levels off (mirroring the option-price ceiling effect at extreme vol from Ch.3). For an ATM call, the volatility-rho relationship is closer to linear (even slightly declining at the high end). For an ITM call, rising volatility actually *decreases* rho.

## Position Greeks (p.118–131)

- **"Position"** = whether an option holding is long (purchased) or short (written). A trader's *position Greeks* estimate whole-position profit/loss sensitivity to each market-condition change — computed as the sum, across all legs, of (quantity × per-option Greek).
- **Critical sign-convention warning — "+"/"−" have three different, context-dependent meanings**:
  1. On a *quantity* of options: + = long, − = short.
  2. On an *individual option's* delta/vega/theta/rho: + = positively correlated with that input, − = negatively correlated. (Gamma's sign describes whether *delta itself* moves with or against the underlying's direction.)
  3. On a *position's* Greek (the whole book): + = position profits if that input rises, − = position loses if that input rises. (Exception noted for gamma — see below, since gamma doesn't itself signal profit/loss, only delta's rate of change.)

### Position Delta (p.120–122, Tables 4-9 & 4-10)

- **Long calls and short puts have positive position delta** (profit if underlying rises). Worked examples (full tables captured):
  - Long 4 XYZ 80 Calls @4.20, delta 0.55 → position delta = 4×0.55 = **2.20**. Stock 80→81: estimated profit $220; actual profit $228 (16.80 debit → 19.08 debit) — the gap is explained by gamma (delta itself rose during the move).
  - Short 10 QRS 40 Puts @0.81, delta −0.34 → position delta = 10×0.34 = **3.40** (positive, since short puts profit as stock rises). Stock 41→42: estimated profit $340; actual $290 (8.10 credit → 5.20 credit) — gap again from changing delta.
- **Short calls and long puts have negative position delta** (lose if underlying rises) — mirror-image worked examples given (short 4 XYZ 80 Calls: −2.20 delta, loses as stock rises; long 10 QRS 40 Puts: −3.40 delta, loses as stock rises).
- Debit/credit terminology: **debit** position = money paid to establish it (profit = value increase); **credit** position = money received to establish it (profit = value *decrease*).

### Position Gamma (p.122–126, Tables 4-11 & 4-12)

- Gamma of a position does **not** itself indicate profit/loss — it indicates how the *position's delta* will change as the underlying moves.
- **Long calls and long puts have positive position gamma** — delta moves in the *same* direction as the underlying (favorable: as the market moves in the option owner's favored direction, their exposure/delta grows in that same favorable direction; as it moves against them, delta shrinks, cushioning the loss). Worked example: long 4 XYZ 80 Calls, option gamma 0.04 → position gamma 4×0.04=0.16; stock 80→81 → position delta 2.20→2.36, confirming the estimate.
- **Short calls and short puts have negative position gamma** — delta moves *opposite* the underlying's direction, which is unfavorable to the short position (losses accelerate as the market moves against a short-option holder, since their opposing exposure keeps growing). Worked mirror examples given (same magnitudes, opposite favorability interpretation).

### Position Vega (p.126–128, Tables 4-13 & 4-14)

- **Long option positions (calls or puts) have positive position vega** — profit if volatility rises. Worked example: long 4 XYZ 80 Calls, vega 0.13 → position vega 0.52 → estimated/actual profit $52 on a 1% vol rise (16.80→17.32 debit).
- **Short option positions have negative position vega** — lose if volatility rises, profit if it falls. Mirror worked examples given (short calls, short puts).

### Position Theta (p.127–129, Tables 4-15 & 4-16)

- **Short option positions have positive position theta** — profit as time passes (decay works in the seller's favor). Worked example: short 4 XYZ 80 Calls, theta 0.04 → position theta 0.16 → estimated/actual $16 profit per day (16.80→16.64 credit).
- **Long option positions have negative position theta** — lose as time passes. Mirror worked examples given.

### Position Rho (p.129–131, Tables 4-17 & 4-18)

- **Long calls and short puts have positive position rho** — profit if rates rise. Worked examples given (long 4 XYZ 80 Calls: rho 0.28, estimated/actual $28 profit on a 1% rate rise; short 10 QRS 40 Puts: rho 0.20 estimated vs. $10 actual, difference from rounding).
- **Short calls and long puts have negative position rho** — lose if rates rise. Mirror worked examples given.

### Position Greeks Summarized (p.131, Table 4-19)

| Position | Delta | Gamma | Theta | Vega | Rho |
|---|---|---|---|---|---|
| Long call | + | + | − | + | + |
| Short call | − | − | + | − | − |
| Long put | − | + | − | + | − |
| Short put | + | − | + | − | + |

No two rows are identical — each combination has a unique sensitivity profile, and every option's actual sensitivities further depend on its specific moneyness (ITM/ATM/OTM). Understanding position Greeks (not just individual-option Greeks) is described as a key differentiator between good and bad option traders, and is the foundation for selecting appropriate strategies given a market view.

## Summary

The five Greeks (delta, gamma, vega, theta, rho) each estimate an option's or position's sensitivity to one pricing input, holding the others constant — but the Greeks themselves are not static; they shift continuously as price, time, and volatility change, which is why traders need not just today's Greeks but a working model of *how* each Greek moves under different scenarios (ITM vs. ATM vs. OTM, near vs. far from expiration, low vs. high volatility). Position Greeks — the quantity-weighted sum across every leg of a book — translate these single-option sensitivities into an actionable profit/loss estimate for an entire position, and are the direct groundwork for Ch.10's position-risk-management framework.
