# Income Strategies (Premium Selling)

**Scope note:** Neither source book has a chapter titled "Covered Calls" or "Cash-Secured Puts." Bittman's book (*Trading Options as a Professional*) is organized around option mechanics and market-making, not strategy categories, and never uses "income strategy" as a label. Chen/Sebastian's book (*The Option Trader's Hedge Fund*) is organized around a business framework (TOMIC — "The One Man Insurance Company") whose entire premise *is* income generation via premium selling, but its concrete strategy chapter ("Most Used Strategies," Ch.9) groups strategies by structure (vertical, condor, butterfly, calendar, ratio), not by an "income" label either. This document synthesizes the income-generating angle across both books' actual content — the insurance/underwriting framing, the specific premium-selling structures the books do cover (vertical credit spreads and iron condors), and the synthetic-equivalence math that shows why "covered call" and "cash-secured put" are two names for the same risk position — rather than forcing a chapter that doesn't exist in either source.

For full construction/adjustment/exit mechanics of butterflies, calendars, ratio spreads, and Bittman's arbitrage combinations (which are volatility or arbitrage trades, not premium-for-income trades in the sense used here), see `spreads-and-combinations.md`. For the general risk-management and position-sizing framework, see `risk-management-and-position-sizing.md`. For skew, term structure, and weighted-vega mechanics referenced below, see `greeks-and-volatility.md`.

---

## 1. The Underwriting Framing: Why Selling Premium Is a Business

*Per Chen/Sebastian, Ch.1 "The Insurance Business" and Ch.2 "Trade Selection."*

Chen/Sebastian's entire book is built on treating an options-selling operation as a one-person insurance company (**TOMIC**). This is the conceptual foundation for every income strategy in this document: **selling an option is selling an insurance policy** — you collect a premium up front in exchange for taking on the risk that the buyer's "claim" (the option finishing in-the-money) is realized.

**The core mapping (Ch.1, Table 1.1):**

| Auto insurance element | Options-selling equivalent |
|---|---|
| Asset insured (the car) | Asset insured (stock/index/future) |
| Policy term (e.g., 12 months) | Option's days to expiration |
| Insured amount (vehicle value) | Strike price |
| Deductible (owner absorbs first $X of damage) | Selling an OTM option — buyer absorbs the first portion of adverse movement |
| Premium paid for the policy | Premium paid for the option |
| Loss ratio (actuarial expectation) | Probability of the option expiring worthless (from the pricing model) |
| Claim paid, or premium kept if claims-free | Put/call seller is assigned if ITM at expiration; keeps full premium if OTM |
| Reinsuring catastrophic risk | Buying deep-OTM puts (or index puts) as tail protection |

Bottom line, quoted directly: *"The business of a one-man insurance company is to collect premiums from option buyers in exchange for the risks of losses in the underlying markets of the options and earn profits from the time decay of the options."* This is the single sentence that defines "income strategy" for purposes of this playbook: **a position that is net short options (collects premium up front) and profits primarily from time decay (positive theta), where risk is priced (underwritten) rather than eliminated.**

**Underwriting is the single most important function** (Ch.2) — trade selection *is* underwriting. Good underwriting (Hurricane Katrina, 2005: insurers priced catastrophe risk correctly and remained solvent through record claims) and bad underwriting (AIG/CDS, 2008: sold ~$450B of credit protection without understanding correlated tail risk) bookend the stakes of mispricing what you sell. AIG's failure mode is the cautionary tale for every income-strategy seller: a credit-spread or iron-condor book is *correlated* risk (many short premium positions can go bad together in a broad selloff), not independent risk like fire-insurance claims — see `risk-management-and-position-sizing.md` for the portfolio-level implications (diversification rules, black-swan insurance, "units").

**Five underwriting decisions when selecting any premium-selling trade** (Ch.2): (1) which market(s) to trade, (2) which strategy fits the market, (3) trade duration, (4) volatility's impact on the trade, (5) entry price. Pricing determines whether a trade is worth taking at all: *"an option's price should be directly proportional to volatility, all else equal"* — a mispricing (skew or term-structure distortion) is where the edge comes from, and the correct response to a mispricing is to **sell the relatively overpriced insurance and, if needed, buy the relatively underpriced insurance** (Ch.2's Florida-vs.-Cayman-Islands hurricane-insurance analogy). Recommended underlyings for premium selling, per Ch.2: broad indexes (SPX, NDX, RUT, DJX, OEX — favored partly for IRC §1256's 60/40 blended tax treatment), liquid ETFs (open interest >500/strike), and liquid equities (daily volume >50,000 contracts).

---

## 2. The Building Block: Short Options and Their Synthetic Twins

*Per Bittman, Ch.1 "Option Market Fundamentals" and Ch.5 "Synthetic Relationships"; confirmed in Chen/Sebastian Ch.13.*

Every premium-selling income strategy is built from two basic short positions:

- **Short call**: limited profit (premium received), unlimited risk above the breakeven (strike + premium received).
- **Short put**: limited profit (premium received), substantial risk below the breakeven (strike − premium received), bounded only because the underlying can't go below zero.

(Bittman Ch.1, Figs 1-3/1-4 — full P/L mechanics in `directional-strategies.md`.)

### The synthetic equivalence that defines "covered call" and "cash-secured put"

Bittman's Ch.5 derives six synthetic equivalences from put-call parity (`Stock = Call − Put`, i.e., long stock = long call + short put). The one most directly relevant to income-strategy selection is:

> **Synthetic short put = long stock + short call.**

This is the exact structure of a **covered call**: you already own (or buy) the stock, and you sell a call against it. Per Bittman's algebra (`−Call + Stock = −Put`), a covered call has the *same theoretical risk, breakeven, and profit potential* as a naked short put at the same strike/expiration. Symmetrically, a **cash-secured put** (selling a put while holding the cash to buy the stock if assigned) *is* the "real" short put — the position the covered call synthetically replicates.

Chen/Sebastian's Ch.13 independently confirms this from the trading-floor side, under the heading "When Should You Worry About Assignment?": *"a put is a call and a call is a put"* — most professional option trades are conversions between the two via combinations with stock. They state explicitly:

- **Protective put** (long put + long stock) has the same risk/payoff shape as a **long call**.
- **Covered call** (long stock + short call) has the same risk/payoff shape as a **short put**.

Both books therefore agree, independently and from different angles (Bittman via formal put-call-parity derivation with worked P/L tables; Chen/Sebastian via trading-floor assignment-risk reasoning), that **a covered call and a cash-secured put are the same economic bet**: bullish-to-neutral, capped upside, substantial downside, and both profit from the option leg's time decay. Practical consequences for an income-strategy trader:

1. **Choosing between "sell a covered call" and "sell a cash-secured put" at the same strike/expiration is mostly a capital-structure and tax/logistics decision, not a risk decision** — the risk profile is identical (net of dividends and financing effects; see below).
2. **Real-world divergence from the zero-interest-rate baseline**: with zero interest and no dividends, a call's time value equals a corresponding put's time value exactly (Bittman Ch.5). With positive interest rates, the call's time value exceeds the put's by roughly the interest earned on the strike price over the option's life — meaning a covered call (financed like owning stock) and a cash-secured put (financed like holding cash/margin) are not *quite* identical once financing and dividends are priced in, but the theoretical equivalence is what determines fair relative pricing between the two approaches.
3. **Assignment risk is generally low priority** for a short-put/covered-call income seller in a low-rate environment (Chen/Sebastian Ch.13's put-call-parity "trader's shorthand": you're at meaningful risk of early assignment on a short put only once the opposing call is worth less than roughly $0.25, or on a short call only once the dividend exceeds the value of the opposing put). Dividend dates are the one case where covered-call assignment risk is real and should be checked explicitly.

Bittman's own caveat applies here too: synthetic positions carry **two bid-ask spreads/commissions instead of one**, so a retail trader is usually better off just holding the "real" version (buy-write for a covered call, sell a cash-secured put directly) rather than actually constructing the synthetic twin — the value of the equivalence is in understanding *why* the two strategies behave the same, and in pricing one off the other, not in routinely trading the synthetic version.

---

## 3. Vertical Credit Spreads

*Per Chen/Sebastian, Ch.9 "Most Used Strategies" (The Vertical Spread) and Ch.10 (worked TOMIC 1.0 example).*

The vertical spread is Chen/Sebastian's foundational building block — "the spread a trader would pick if stranded on a desert island with only one strategy allowed." A vertical spread is a long and short option at *different strikes, same expiration*. Four variants exist; the two that are genuine income strategies (net credit, positive theta) are:

- **Vertical put credit spread** — bullish-to-neutral: sell a higher-strike put, buy a lower-strike put for protection.
- **Vertical call credit spread** — bearish-to-neutral: sell a lower-strike call, buy a higher-strike call for protection.

A credit spread is functionally a **defined-risk version of a naked short put or short call** — it caps both the premium collected and the maximum loss, at the cost of some of the naked position's income. This makes it a direct risk-reducing evolution of the "sell a cash-secured put" / "sell a covered call" strategies in §2: same directional bias and same profit-from-decay mechanism, but bounded downside via the long "insurance" leg. Explicitly noted in Ch.9: beginners often start with a naked short put/covered call and build toward the credit-spread version by "adding insurance."

**Entry conditions:**
- Best used with a directional opinion.
- Use in **stable-or-declining volatility**, not rising volatility.
- **Spread width should track skew steepness**: steeper skew → narrower spreads (less volatility gap between the two strikes); flatter skew → wider spreads are fine and save on commissions.
- Typical entry window: **30–60 days to expiration.**

**Worked example (AAPL vertical put credit spread, Ch.9):** Entered Oct 13, 2011 with AAPL @ $405, 30-day IV 38% (above 10-day HV of 37%, within normal range) and trending down from 51% — a favorable environment. Sold 10 Nov 360 puts, bought 10 Nov 350 puts, for a **$1.55/spread credit ($1,550 total)**. By Nov 4, AAPL had drifted down to $401 but IV had fallen further (41.7%→34.1% on the short strike) — the spread was worth only $0.25 (83% of credit captured), so it was closed for a **$1,300 profit** on **$8,450 of Reg-T margin** — a **15.4% return on margin in 22 days.**

**Worked example (TOMIC 1.0 portfolio construction, Ch.10):** An AAPL vertical put spread (10-point width) required **$9,010** Reg-T margin, collected **$990** credit after commissions. Exit rules were set *before* entry: maximum-loss exit at **150% of credit received** ($1,485 — 1.49% of a $100,000 account, within the 2%-per-trade cap) and a profit-side exit around **$693**. The trade was closed at a **$710 profit** once the target was hit — illustrating the general income-strategy discipline of defining both exits before entry (see §5).

---

## 4. Iron Condors

*Per Chen/Sebastian, Ch.9 "Most Used Strategies" (The Iron Condor), Ch.11 (skew/IV lessons), and Ch.10 (worked example).*

An iron condor is two OTM vertical credit spreads on the same underlying/expiration — a short call spread above the market and a short put spread below it — set at a distance the underlying is judged unlikely to reach. It is the two-sided combination of the credit spreads in §3, and is the flagship income strategy in Chen/Sebastian's "most used strategies" list precisely because it collects premium on both sides without requiring a directional view.

**Volatility condition:** IV doesn't need to be absolutely high — it needs to be higher than the underlying's **average true range (ATR)** (a 14-day moving average of true range, per J. Welles Wilder). The key skill is selling when volatility is **stable or falling**, not merely "high": a condor sold while VIX is elevated *and rising* is dangerous; a condor sold while VIX is lower *but declining* tends to work out.

**Skew condition:** matters less than for a naked strangle (the long legs offset skew exposure somewhat), but an unusually steep skew while IV itself hasn't yet moved is a warning sign of a possible volatility spike ahead — avoid or insure heavily in that case.

**Time condition:** Cross-referencing Bittman directly (Ch.9 calls Bittman's book "a great primer" on this point) — only **ATM** options decay exponentially in the final 30 days; OTM options decay much more linearly. Chen/Sebastian's "cone of feasibility" concept describes the window in which an OTM option sheds most of its value as it moves from logically-capable-of-finishing-ITM to logically-incapable. Practical rule: enter around **60 days to expiration**, at the **10–15 delta** range, to capture this decay window.

**Sizing / pricing an entry:** Sell a 10–11 delta call, buy the next strike out (checking neighboring strikes for relative mispricing — resting orders can make one strike richer than its neighbor); then sell a 10–12 delta put, allowing the put strike to be nudged for extra credit since skew naturally sits it further from spot than the call side. Example risk/reward: a $2.00 credit on a 10-point-wide spread = 200/800 risk/reward (25% return on risk); paired with an 85% modeled probability of success this is attractive, at 70% much less so.

**Goals and exits:**
- Target roughly **55% of credit received**, aiming to exit by **~30 days to expiration** (before the "cone of feasibility" window compresses further and gamma risk rises).
- **Quick-profit rule**: capturing 25% of credit within 5 trading days signals real edge — take it and reassess rather than holding for more.
- **Loss discipline — the "Third Third Third Rule"**: first adjustment at 1/3 of the pre-set maximum loss, second adjustment at 2/3, exit at the full maximum loss (suggested to equal the profit target). A **hard absolute-maximum-loss ceiling**, set at the value of credit received, should never be exceeded — if a 1.5-SD move would breach it, act immediately even before the staged maximum-loss trigger is hit.
- **Insurance**: when volatility sits in the lower 25% of its historical range, spend a modest amount (no more than ~10% of credit received) on unit-put insurance against a low-to-high volatility transition — described as the single greatest danger to an iron condor.
- **Adjustments** (in preference order): kite spread (see `spreads-and-combinations.md`) for upside gamma reduction; back ratio spread if IV is very depressed; call spread only as a costly last resort. Downside: ratio spread (short 1, long 2) as the primary tool when volatility is normal; put spread as a cheaper index-specific alternative. Rolling the trade out is explicitly disfavored.

**Worked example (SPX iron condor, Ch.9):** Entered Oct 19, 2011 on the January contract with IV at a premium to realized vol and trending lower. Structure: **SPX 990/1000/1340/1350 iron condor**, collecting ~$2.50, targeting at least $1,250 and a 30-DTE exit. The trade was never seriously threatened; after 30 days it was up ~$1,000 (short of the $1,250 goal) and was closed anyway per the time-based exit discipline. Lesson: *"the setup made the trade"* — entry quality, not mid-trade adjustment skill, is the primary risk-management lever.

### Pricing nuance specific to iron condors: "all credits are not created equal"

Chen/Sebastian's Ch.11 ("Understanding Implied Volatility in Iron Condors") makes a point directly relevant to evaluating any condor-for-income trade: the *same nominal credit* is not the same trade if skew/IV levels have shifted. Worked comparison: a 10-delta put spread sold for $0.60 at 8.5% OTM (when IV/skew were flat/low relative to recent history) is a **worse** trade than an equivalent $0.60 credit sold a month earlier when the short strike was a full ~15 points further OTM (10% OTM) for the identical premium. Falling volatility and flattening skew "pull in the wings" of a condor over time — collecting the same dollar credit for a strike sitting closer to spot means less compensation for the same nominal risk. **Always compare a condor's credit against the distance (in standard deviations or delta) it buys, not against the raw dollar amount alone.**

Related pricing/skew tools relevant to condor entry (fully covered in `greeks-and-volatility.md`): the SPX skew-is-relative framework (skew is a *percentage* of ATM IV, so a high skew on a low ATM-IV base can be less rich in absolute terms than a lower skew on a high ATM-IV base — the richest setups combine both high skew and high ATM IV) and the five-phase skew-cycle model (Calm → Calm Before the Storm → Typhoon → Calming Storm → resolving-Phase-5), which helps judge whether current skew reflects "normal" compensation or transitional risk.

---

## 5. Risk Management Specific to Premium-Selling / Income Trades

*Full general risk framework lives in `risk-management-and-position-sizing.md`; this section covers the risk mechanics that are distinctive to being a net premium seller.*

**Position sizing (Ch.3):** the 2%-of-capital-per-trade / 6%-of-capital-per-month rules apply directly to credit spreads and condors. Worked example: a $2,000,000 fund's 2% rule implies $40,000 max risk per trade; a 10-point RUT iron condor using $1,000 Reg-T margin per contract could naively suggest 40 condors, but since traders typically set an *actual* stop-loss well inside the full margin (e.g., a 20%-of-margin loss trigger = $200/condor), the real capacity is **200 condors** — five times the naive figure, because true realized risk on a well-managed income trade is much smaller than its theoretical maximum loss.

**The Card Game Value (Ch.12) — the risk unique to short premium positions near full decay:** standard pricing models say a very cheap short option (down to a few cents) is worth close to nothing, but such options persistently hold residual value of roughly **$0.10–$0.25** for an unusually long time. The mechanism: probability-weighted pricing is only a fair approximation across *many repeated plays*; any single option's life is one play, and if that low-probability tail event hits, the premium seller has no chance to "run it back" within that contract — and unlike the book's card-game illustration (a fixed $1,000 payout), a short option's downside is typically **open-ended**. Practical rule: **exit a credit spread once it has decayed onto Card Game Value (~$0.10–$0.25) rather than holding for full decay to zero** — the marginal premium remaining isn't worth the tail risk retained.

**Good exits (Ch.13):** every income trade needs two exits defined *before* entry — a losing-trade exit and a winning-trade exit — most practically expressed as a **percentage of margin used** (worked example: exit an iron condor at a 20%-of-margin loss or a 15%-of-margin gain). *"The best loss is the first loss"* — hesitating on a triggered stop, hoping for reversal, is explicitly identified as the most common way a small loss becomes an unrecoverable one.

**Skew/wing guidance relevant to defined-risk income trades (Ch.13):** an option worth less than $0.25 does not meaningfully hedge anything — buying a protective wing that cheap on a credit spread or condor provides essentially no offsetting protection if the short leg is tested, even though it looks like "insurance" was bought. Target at least a one-to-one risk/reward on the wing width, and re-check whether narrowing the wings would meaningfully reduce margin without giving up much protection.

**Portfolio-level tail insurance ("units," Ch.3/Ch.8):** a standing hedge of cheap, deep-OTM puts (**5–10% of allocated trading capital**) is recommended alongside any book of income-generating credit spreads/condors, specifically because premium-selling income strategies are structurally short volatility and vulnerable to the low-to-high volatility transition that ordinary position-level stops may not catch in time. See `risk-management-and-position-sizing.md` for the full mechanics (why "units" behave nonlinearly in a crash, and the flash-crash case study where units more than offset a losing butterfly).

---

## 6. Summary Table: Income-Strategy Structures Covered Here

| Strategy | Structure | Directional bias | Source |
|---|---|---|---|
| Cash-secured put | Short put + cash reserve | Bullish-to-neutral | Bittman Ch.1 (mechanics); Chen/Sebastian Ch.13 (assignment) |
| Covered call | Long stock + short call | Bullish-to-neutral (capped) | Bittman Ch.5 (synthetic = short put); Chen/Sebastian Ch.13 (confirms equivalence) |
| Vertical put credit spread | Short put + long lower-strike put | Bullish-to-neutral | Chen/Sebastian Ch.9, Ch.10 |
| Vertical call credit spread | Short call + long higher-strike call | Bearish-to-neutral | Chen/Sebastian Ch.9 |
| Iron condor | Short call spread + short put spread | Neutral (range-bound) | Chen/Sebastian Ch.9, Ch.11 |

Strategies with premium-collection characteristics but a *volatility or arbitrage* rather than income framing (ATM iron butterfly, calendar/time spread, ratio back/front spread, kite spread, conversions/reverse conversions, box spreads) are covered in `spreads-and-combinations.md` — Chen/Sebastian frame those explicitly as trades on skew, term structure, or realized-vs-implied volatility rather than as steady premium-income vehicles, and Bittman's arbitrage strategies generate profit from financing-rate/dividend mispricing rather than from underwriting directional or range-bound risk.
