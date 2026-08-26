Source: Bittman, *Trading Options as a Professional*, Chapter 5 "Synthetic Relationships", printed pp. 135–160.

## Synthetic Relationships (intro) (p.135–137)

- **Put-call parity** links stock, call, and put prices such that any one of the three real positions (long/short stock, long/short call, long/short put) can be replicated ("synthesized") by a two-part combination of the other two instruments.
- A synthetic position has the **same theoretical risk, breakeven, and profit potential** as the real position it replicates — but in practice carries **two bid-ask spreads/commissions instead of one** and different margin treatment, so trading synthetics is mostly the domain of professional traders. Understanding synthetics is foundational to arbitrage strategies (Ch.6).
- **Effective price**: the true stock price implied once option premium is factored in — e.g., a 100 Call bought for 2.00 and exercised gives an effective long-stock price of 102.
- Simplifying assumptions used for the chapter's introductory examples: 1 option = 1 share (not 100), interest rate = 0% (time to expiration irrelevant), no commissions/dividends, and $100 cash held in reserve (to buy stock or serve as margin). Baseline prices: stock=100, 100 Call=3.00, 100 Put=3.00.

## The Six Synthetic Equivalences (p.137–151)

Each backed by a full P/L table (5 stock-price rows) + graph + "mechanics at expiration" walkthrough of all 3 outcomes (stock above/below/at strike) — all six follow the identical proof pattern: the combined synthetic P/L exactly matches the real position's P/L at every stock price, and at expiration the synthetic converts into the real position (or an equivalent cash result) via exercise/assignment, at the same **effective price**.

1. **Synthetic long stock = long call + short put** (same strike/expiration). Example: long 100 Call@3.00 + short 100 Put@3.00 ≡ long stock@100. At expiration: stock>100 → put expires worthless, call exercised (buy stock using the $100 reserve) → effective price $100. Stock<100 → call worthless, put assigned (buy stock) → effective price $100. Stock=100 → both worthless, no position (cash reserve could still be used to buy stock at $100 for the same result).

2. **Synthetic short stock = short call + long put**. Example: short 100 Call@3.00 + long 100 Put@3.00 ≡ short stock@100. Mechanics mirror #1: stock>100 → call assigned (creates short sale); stock<100 → put exercised (creates short sale); stock=100 → both worthless.

3. **Synthetic long call = long stock + long put** (same strike as the put). Example: long stock@100 + long 100 Put@3.00 ≡ long 100 Call@3.00. At expiration: stock>100 → put worthless, stock position remains at effective price $103 (100 + 3.00 put cost) — matches buying a real 100 Call@3.00 and exercising. Stock≤100 → put exercised/worthless, stock is sold at 100, net loss = put's cost (3.00), leaving only the cash reserve — matches a real call expiring worthless with the premium as the max loss.

4. **Synthetic short call = short stock + short put**. Example: short stock@100 + short 100 Put@3.00 ≡ short 100 Call@3.00. Stock>100 → put worthless, short stock effective sale price $103 (100+3.00 premium received) — matches assignment of a real short call. Stock≤100 → put assigned (covers the short stock), profit = premium received (3.00), only cash reserve remains.

5. **Synthetic long put = short stock + long call**. Example: short stock@100 + long 100 Call@3.00 ≡ long 100 Put@3.00. Stock>100 → call exercised (covers short stock) at effective price $103 (100+3.00 call cost) — net loss of 3.00, matching a real put expiring worthless. Stock≤100 → call worthless, short stock remains at effective price $97 (100−3.00) — matches exercising a real long put.

6. **Synthetic short put = long stock + short call**. Example: long stock@100 + short 100 Call@3.00 ≡ short 100 Put@3.00. Stock>100 → call assigned (sells the stock) at effective price $103 (100+3.00 premium received) — profit of 3.00, no position left, matching a real short put expiring worthless. Stock≤100 → call worthless, long stock remains at effective price $97 (100−3.00 premium received) — matches assignment of a real short put.

## When Stock Price ≠ Strike Price (p.151–153, Tables 5-7/5-8)

- The six equivalences hold **regardless of where the stock price sits relative to the strike** — worked examples given at non-ATM prices:
  - Stock=103, 100 Call=4.50, 100 Put=1.50: long call + short put ≡ long stock@103 (full table verified row by row).
  - Stock=97, 100 Call=2.50, 100 Put=5.50: long stock + long put ≡ long 100 Call@2.50 (full table verified).

## The Put-Call Parity Equation (p.153–154, Table 5-9)

Basic equation (assuming same underlying/strike/expiration, 0% interest, no dividends):

```
Stock = Call − Put        (long stock = long call + short put)
```

Five other relationships derived algebraically by adding/subtracting terms from both sides:

| # | Equation | Meaning |
|---|---|---|
| 1 | Stock = Call − Put | Long stock = long call + short put |
| 2 | Stock + Put = Call | Long call = long stock + long put |
| 3 | Put = Call − Stock | Long put = long call + short stock |
| 4 | Put − Call = −Stock | Short stock = long put + short call |
| 5 | −Call = −Stock − Put | Short call = short stock + short put |
| 6 | −Call + Stock = −Put | Short put = long stock + short call |

(Convention: `+` = long, `−` = short.)

## Equality of Call and Put Time Premiums (p.154–155, Fig 5-9)

- Across every example in the chapter, **the time value of the call equals the time value of the put** (same underlying/strike/expiration), regardless of moneyness:
  - Stock=100: both 100 Call and 100 Put priced 3.00, entirely time value (equal by construction).
  - Stock=103: 100 Call=4.50 (3.00 intrinsic + 1.50 time value); 100 Put=1.50 (all time value) — **equal time values (1.50 = 1.50)**.
  - Stock=97: 100 Put=5.50 (3.00 intrinsic + 2.50 time value); 100 Call=2.50 (all time value) — **equal time values (2.50 = 2.50)**. This is the zero-interest-rate baseline; the next section shows how real-world interest rates break this exact equality.

## Applying the Effective Stock Price Concept (p.155–156)

- **A call's price increases the effective stock price; a put's price decreases it** — because an exercised/assigned call implies buying/selling at strike+call price, while a put implies strike−put price.
- With 0% interest/no dividends, **synthetic stock price = strike + call price − put price**. Verified across all three worked examples: 100+3.00−3.00=100; 100+4.50−1.50=103; 100+2.50−5.50=97.

## The Role of Interest Rates and Dividends (p.156–160, Figs 5-10/5-11)

- Thought experiment: an investor with $100 can buy real stock, or build a net-zero-cost synthetic long stock position (buy 100 Call@3.00 + sell 100 Put@3.00) and keep the $100 earning interest.
  - **Interest rate > 0, no dividends** → synthetic stock is preferred (keeps the $100 earning interest on top of the same P/L).
  - **Interest rate = 0, dividends paid** → real stock is preferred (captures the dividend; synthetic has no analogous benefit).
  - **Both interest rate > 0 and dividends paid** → ambiguous; whichever is larger (rate vs. dividend yield) determines the preferred structure.
- Because rational investors arbitrage away any advantage, **real-world option prices adjust so that call prices are bid up and put prices are bid down** relative to the zero-interest baseline — meaning the earlier "equal time premiums" result does NOT hold once interest rates are positive.
- **Key real-world rule**: for same-underlying/strike/expiration calls and puts, **the call's time value exceeds the put's time value by (approximately) the interest earned on the strike price** over the option's life.
  - Worked example 1 (Fig 5-10, Op-Eval Pro): stock=100, strike=100, 25% vol, 5% rate, 30 days, no div → Call=3.08, Put=2.70 → time-value gap = 0.38. Interest check: 100 × 0.05 × 30/365 = **0.41** (close to 0.38; gap attributed to rounding and pricing-formula technicalities).
  - Worked example 2 (Fig 5-11): stock=88, strike=85, 30% vol, 4% rate, 90 days → Call=7.27 (time value 4.27), Put=3.48 (time value 3.48... wait, computed as 4.27−3.48=0.79 gap). Interest check: 85 × 0.04 × 90/365 = **0.84** (again close, small gap from rounding/model technicalities).
- Practical implication: theoretically no advantage exists between trading real vs. synthetic stock once prices adjust to reflect this rule — but transaction costs and bid-ask spreads in practice keep most non-professional traders in real stock rather than synthetics. Ch.6 explores how interest rates/dividends drive arbitrage strategies built on these same relationships.

## Summary

Six real positions (long/short stock, call, put) each have a synthetic two-part equivalent built from the other two instruments. Core equation: `Call − Put = Stock` (long call + short put = long stock), with five algebraic variants covering the other five equivalences. Regardless of where the stock price lands relative to the strike at expiration, a synthetic position converges to the same P/L and effective price as its real counterpart. With zero interest and no dividends, call and put time values in a parity relationship are exactly equal; in the real world, interest rates (and dividends) break that equality — a call's time value exceeds a put's by approximately the interest earned on the strike price over the option's life. Theoretically investors should be indifferent between real and synthetic positions, but transaction costs and spreads drive most non-professionals toward real stock.
