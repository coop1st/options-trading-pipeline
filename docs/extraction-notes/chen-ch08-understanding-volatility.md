Source: Chen/Sebastian, *The Option Trader's Hedge Fund*, Chapter 8 "Understanding Volatility", physical pp. 97–104.

Note: this chapter opens **Part II ("Implementing the Business")** per the "Part II" marker seen at the end of Chapter 7's extraction. This is the book's distinct volatility framework — the "three-dimensional volatility" model — and is a primary source for the `greeks-and-volatility.md` synthesis doc, to be read alongside Bittman's volatility chapter (Bittman ch.7) and this book's later "Lessons from the Trading Floor on Volatility" (Ch.11).

## Overview / Introduction (p.97)

Claim: all option pricing models (even "antiquated" ones like Black-Scholes and Whaley) rely on five core inputs: **underlying price, strike price, time to expiration, cost of carry, and forward volatility.** Of these five, four are simple/known; **forward volatility is the only factor traders do not actually know** — and per the authors, volatility is "by far the number one determinant of success" for a hedge fund trader. Strong claim: "Any educator, coach, book, software, or service that ignores volatility, or does not emphasize volatility as the primary and fundamental key to success, is likely not worth much."

## What Causes Volatility? (heading present)

Since forward volatility is unknown, its *uncertainty* is actually the trader's advantage — "the uncertainty of volatility is your best friend." Mastering volatility isn't about predicting the unknowable, but about judging whether **implied volatility** is currently high or low.

**Myth-busting on what drives implied volatility**: retail/institutional traders track IV, but usually misunderstand its driver. Common (wrong) belief: market makers set option prices/volatility in some kind of "boiler room." Reality: market makers only set the *momentary* market; the actual price is set through **price discovery** — driven by supply and demand, not by market maker fiat.

**Mechanism example** (Table 8.1, "Sample of How a Market Maker Might Move Markets as Customer Paper Flows" — table contents not machine-extractable, but the narrated mechanism is fully described):
- If market makers bid too high, the public sells to them aggressively; market makers must either absorb a lot of inventory or lower their bid — lowering the bid (and thus IV) is how they manage inventory as a side effect.
- If market makers overcorrect and cut the bid/offer too low (e.g., dropping the offer to 1.00), the public will start bidding for those cheap options — signaling to market makers that volatility is now "oversold," at which point they raise the bid back up (illustrated with a hypothetical case reaching "26% implied volatility" as the oversold level, then reversing).
- Lesson: **implied volatility is determined by market supply/demand, not by market maker choice.** Market makers merely take the other side of public order flow; that flow (and the resulting price discovery) is the true determinant. A smart TOMIC manager can exploit this the way a savvy buyer or seller exploited the mispricing in the illustrated example (explicit callout: the best trade in the illustrated sequence was "the first sale of 100 at 1.10" — i.e., selling into an overpriced/overbought moment). Because TOMIC can *initiate* trades (unlike a pure market maker), it should look for opportunities to sell overvalued contracts. Key principle: "Selling when others are buying and buying when others are selling is the key to success" — smart funds take on risk from those panicking or those overly complacent.

## Three-Dimensional (heading present — the book's central volatility framework)

Central claim: volatility is **not one-dimensional**; it is **three-dimensional**. A trader pricing/using volatility must examine all three facets together: (1) the ATM options' price in the near term, (2) volatility skew, (3) term structure. Each gets its own sub-section below.

### ATM Options (sub-heading present)

The most actively traded options at any time are almost universally **front-month ATM options**, and their trading activity sets the overall volatility structure for the whole product. Analogy: ATM options are like the sails of a boat — other parts affect speed, but the sail (and its size/angle to the wind) dominates. Movements in front-month ATM IV propagate to OTM puts, OTM calls, and the entire term structure: if front-month ATM IV drops, further-out months drop too; if it rallies, the whole structure follows.

Nuance: front-month options don't have the *most* vega (that typically belongs to longer-dated options), but they are **far more sensitive to changes in implied volatility** — a property the text calls **"vomma"** (sensitivity of vega/IV response), described here as "the greatest sensitivity to changes in implied volatility." Practical implication: watching front-month ATM options is the best single indicator of where IV on any option in that product is headed, even when you don't hold ATM options yourself.

### Skew (sub-heading present; also called "kurtosis" in the text)

Definition: skew = how different options' implied volatilities relate to one another within a given contract series. In equity/equity-index options, the typical pattern is an **"investment skew"**: OTM puts trade at higher IV than ATM, OTM calls trade at lower IV than ATM. Exceptions noted: deal stocks, FDA-announcement stocks, and VIX options often don't follow this pattern.

**Root cause of investment skew, per the authors**: the equity market is structurally full of "natural longs" — 401(k)s and mutual funds are mostly long stock, and individual accounts are predominantly long as well (shorting stock in a personal account requires extra paperwork/margin approval). Since the market is structurally biased toward being long stock, the natural hedges are (1) buying puts and (2) selling calls against those long positions. Widespread simultaneous demand for this exact hedge (buy puts, sell calls) bids up put IV and depresses call IV — this is presented as *the* main driver of investment skew (an options-market-structure explanation, distinct from Bittman's more model/hedging-based skew treatment — flagged for cross-reference in synthesis).

### Using Skew (sub-heading present, nested under Skew)

Like ATM IV, skew moves with order flow — excess buying/selling pressure on low-priced OTM puts/calls can push IV "out of whack," creating statistically favorable setups. **A flat (undistorted) skew is called out as possibly the single biggest determinant of a butterfly's success**, and also tends to favor back-spread and front-spread trades. On simpler trades, this can just mean choosing to sell OTM put or call *spreads* selectively.

**Practical edge-capture technique**: buy an oversold option / sell an overbought option within a credit spread to squeeze an extra **$0.02–$0.10** of edge per spread. Quantified payoff: saving $0.10 across 10 trades = $100 saved — more than covering typical commission costs; scaled up, **a fund trading 500 contracts/month can save up to $5,000.**

**Recommended monitoring approach for single names**: examine the full strike-by-strike curve before every trade to find mispriced options.

**Recommended monitoring approach for index traders (more complex)**: (1) globally track a few OTM puts/calls by delta (preferred over %-OTM) and monitor their IV relationship to ATM IV over time — worked example: if a 10-delta put trades at 30% IV while ATM trades at 20% IV, the put trades at "150% of ATM," and this ratio itself should be tracked as it moves; (2) for index credit-spread traders specifically, monitor the relationship across the *entire* curve to consistently extract a few cents of edge per trade — the text notes this is impractical to do by eyeballing a trading platform, and that dedicated curve-mapping software "pay[s] for themselves and are worth the investment."

### Units (sub-heading present — distinct treatment of the "units" concept, complementary to Ch.3's flash-crash "units" discussion)

At a certain point, deep OTM options stop trading based on volatility and instead trade at a "lottery ticket price" — e.g., a $0.10 SPX option isn't really priced on volatility anymore. Even though the odds of a $0.05–$0.10 option becoming valuable are slim, **the risk of shorting these cannot be overstated**: a $0.10 option that moves to $15.00 returns **1,500%**, a move option-pricing models are not built to price. The authors term this **"human risk"**: the real-world unwillingness of traders to sell extremely cheap options naked, because of catastrophic tail-loss potential. Framing: the first and second standard deviations of outcomes are fairly priced by the model, but once price action exceeds roughly two standard deviations (more than the model expects), these far-OTM options can move to what is effectively a 4th or 5th standard deviation of payoff.

**Three explicit "units" rules** (reproduced verbatim as numbered rules):
1. **Never short options worth $0.10 or less.**
2. **If you are short an option worth less than $0.10, it is probably worth buying to close even if there is a commission for that closing purchase.**
3. **A hedge fund that sells premium should always be net long these "units."**

Following these rules avoids total catastrophic loss and can produce a surprise windfall on a major move. Sizing guidance (consistent with Ch.3's flash-crash figures): an investment of roughly **5%–10% of the fund** in this kind of option "insurance" will pay out over the long run.

### Term Structure (sub-heading present)

Similar dynamic to skew/ATM: different contract months see different amounts of order flow ("paper"), and liquidity thins the further out you go — so a large order can move one month's pricing substantially relative to others. Monitoring the *relationship* between expiries (not just overall volatility) opens up opportunities, especially for calendar spreads.

**Trading rule based on term-structure mispricing**: if the near-term month is underpriced, buy near-term and sell longer-term against it (classic long calendar) — **but the text warns retail traders to avoid this specific setup**, because when the near term is genuinely underpriced (vs. simply cheap), a long calendar is actually a losing proposition. When the near term is overpriced, the correct trade is to sell near-term and buy back months against it (i.e., go the other way — effectively a reverse/short calendar). Front-month options are far more IV-sensitive than back months (the "vomma" property again) — some traders make a living purely trading this front-month-vs.-back-month "vomma" relationship.

**Broader application**: the same monitoring approach applies to iron condors, butterflies, and strangles — when one month's IV becomes overbought relative to others, it can make sense to shift the trade into that overbought month, or to avoid trading a different, comparatively mispriced month.

**Pitfalls when "volatility swapping" / moving between contract months**, especially in individual equities — watch for:
- Earnings
- FDA announcements
- Corporate actions
- Dividends

A month-to-month spread caused by one of these events is often a legitimate reason to leave that month alone rather than trade the apparent mispricing. General caution: if a spread between months looks "exorbitantly wide" with no obvious explanation, there is probably a real reason — do additional research (calls, message boards) before trading it; "if a swap seems too good to be true, it probably is." That said, the chapter still encourages trading legitimate month-vs.-month swaps: months are correlated but not rigidly tied together, and exploiting real relative mispricings between them offers better odds of success than the pricing model alone would suggest.

## Volatility and the Model (heading present — final section, not listed among the task's known headings)

Key conceptual point: **implied volatility is an *output* of the pricing model, not an input** — the same is true of the Greeks. This means a trader looking at a screen has limited direct control over the risk outputs shown; if you're not actively managing/tracking your own volatility inputs, you can't really see your true risk parameters. Recommended practice: **model how the Greeks and P&L would move across a range of scenarios**, and know the IV of every contract you own — doing so helps sidestep many of the pitfalls of retail trading-platform defaults.

**Recommended ongoing volatility monitoring, per underlying traded:**
- ATM IV
- Skew
- Three-month term structure

**Recommended ongoing monitoring, per position held:**
- The IV of every contract held
- The Greeks of the entire position
- Expected Greeks (i.e., how Greeks are expected to evolve)
- Profit and loss under a decline or increase in IV of 5%, 10%, and 25%

## Notes on completeness

The task's known-headings list ("What Causes Volatility?"; "Three-Dimensional Volatility and the Model") undersells the chapter's actual structure. The real heading hierarchy found in the source text is: **"What Causes Volatility?"** → **"Three-Dimensional"** (with nested sub-headings **"ATM Options,"** **"Skew"** → **"Using Skew,"** **"Units,"** and **"Term Structure"**) → **"Volatility and the Model"** as a separate final heading. All of this has been captured above under its actual structure; nothing appears to have been missed across the full 8-page range. The final "Volatility and the Model" section and the "Units" sub-section are additional content beyond what the task's abbreviated heading list implied, and have been fully captured since both are substantively important (the units rules recur/connect to Ch.3's flash-crash discussion, and "Volatility and the Model" gives the practical monitoring checklist that operationalizes the whole three-dimensional framework).
