Source: Chen/Sebastian, *The Option Trader's Hedge Fund*, Chapter 13 "Lessons from the Trading Floor on Trading and Execution", physical pp. 183–200.

Note: like Ch.11/12, standalone blog-post-style lessons, each given its own subsection. Primary source for `market-making-techniques.md` (payment for order flow) and `spreads-and-combinations.md` (Butterfly Trading Checklist, wing-width guidance).

## What Everybody Should Know About Payment for Order Flow (heading present; blog post dated 12/20/2009)

Origin story: in 2001, a market-making firm (anonymized as "Firm XYZ") pioneered **payment for order flow** to attract volume to the exchange pits where it held Specialist/DPM (Designated Primary Market-Maker) status. Exchanges now often call this a "marketing fee"; brokers use various other names. Author's blunt assessment: the practice is **bad for the customer, bad for the liquidity provider, and great for the online broker.** Over time the practice became integrated at the exchange level (no longer just individual-firm arrangements), creating a hierarchy where firms willing to pay for order-flow visibility get preferential treatment on large orders, "and the public in the trunk."

**"Getting the First Look" — three routing scenarios explained** (using Firm XYZ as the running example; explicitly noted this reflects broad industry/exchange practice, not one bad actor):
1. **Firm XYZ is matching NBBO and the order hits NBBO** → order routes to Firm XYZ's pit. Minimal impact on the retail trader — they're getting the NBBO price regardless.
2. **Firm XYZ isn't the best bid/offer, but still gets first look** → the order gets routed via linkage to whichever exchange actually holds the NBBO. Slightly more risky for large orders: if only one exchange holds the best bid/offer at a given size, the seconds required to route via linkage create a window where the market can move against the trader (though the author notes many payment-for-order-flow firms carry some kind of "matching guarantee" to protect against this).
3. **Firm XYZ is matching NBBO, but the incoming order doesn't hit NBBO** → order still routes to Firm XYZ regardless. Called "the real culprit" — a non-marketable order lands in a market-making pit with the *fewest eyes on it*, rather than the exchange with the deepest liquidity.

**Worked example (author's own IBM experience)**: ISE is willing to buy an option at $0.50 up to 5,000 contracts; PHLX is willing to buy at $0.50 up to only 30 contracts. A trader has an order to sell 10 contracts at $0.55. Intuitively the order "should" go to the ISE (deeper size, presumably more eyes), but a firm accepting payment for order flow would instead route it to the **PHLX** — the venue with far less depth and visibility. Author states he's personally observed resting offers sitting unfilled on PHLX while the same price traded actively on the CBOE. Reiterates a recurring theme from Ch.4: "the only thing smart about a smart router is that it is smart for your broker to make the most money."

## When Should You Worry About Assignment? (heading present; blog post dated 2/07/2010)

Framing: retail traders (even asking about *call* assignment) overweight assignment risk — in reality, being assigned should be one of a trader's lowest concerns, since it happens rarely, especially in a low-interest-rate environment.

**Foundational principle**: "a put is a call and a call is a put" — most professional option trades are conversions between the two via combinations with stock. Examples given:
- **Protective put** (long put + long stock) has the same risk/payoff shape as a **long call** — limited loss, unlimited upside.
- **Covered call** (long stock + short call) has the same risk/payoff shape as a **short put** — limited upside, unlimited downside.

Since all such stock/option combinations are convertible into one another, a governing relationship must hold them together — analogized to E=MC². That relationship is **put-call parity**: the formula ensuring no arbitrage-free way to make more money buying calls than buying puts + stock (mispricings get arbitraged away quickly).

**Put-call parity formula given**: **Call − Put = Stock Price − Strike Price + (Interest − Dividends)**, i.e., **C − P = S − X + (I − D)**, where (I−D) is often shortened to **K** (cost of carry).

**Worked example — deriving a put's fair value from a call price**: customer sells the Feb 50 call at $9, stock at $55.00, cost of carry $0.20 → solve `9 − P = 55 − 50 + 0.20` → **P ≈ $3.80.** If the actual put bid were instead $4.00, market makers would arbitrage: buy calls at $9, sell stock against them (synthetically creating a put), then sell the (overpriced) actual put — effectively "synthetically buying the put and selling the actual put."

**Applying parity to assignment risk on a long/protective-put position**: if long a put and long the underlying against it, the combined position is economically a **long call** — you would only exercise the put if doing so beat holding the equivalent call position.

**Worked numeric example — OEX ATM put butterfly**: entered OEX 500/530/560 put fly on Jan 19. By Feb 5, OEX down 40 points to 491.35; the 530 puts trade at 41.50; market-maker interest rate 0.25%, cash accrued dividend ~$2.95 → cost of carry ≈ **−2.90**; calls trading at $0.15. Exercise decision test: is `0.15 < 491.35 − 530 + (−2.90) + 41.5`? Right side computes to **−0.05**, so the answer is **no** — even after a major 8% down move, it is *not* in the counterparty's interest to exercise the put. Conclusion: with interest rates this low, put assignment is rare; the market-maker rate would need to rise by **at least ~1%** before this position becomes even a marginally attractive exercise candidate.

**Calls are a different story**: non-dividend-paying calls should essentially never be early-exercised, but calls **do carry real assignment risk around dividend dates.**

**Worked numeric example — EXC short call around an ex-dividend date**: EXC goes ex-dividend Feb 11, paying $0.525/share. Short the 40 calls — should you worry? Call trades ~$4.25, put ~$0.05, stock $44.25, cost of carry = (0.01 − 0.525). Plugging into parity: `4.25 − 0.05 = 44.25 − 40 + (0.01 + 0.525)` — the two sides **don't balance**, signaling the calls are likely to be exercised/assigned.

**"Trader's Short Hand" — quick rules given explicitly** (a simplified substitute for the full parity math):
1. If **(I − D) is greater than the value of the call opposite your short put**, you may get assigned on the put. Practically, this only becomes relevant once the opposing call is worth less than about **$0.25** (or, with rates this low, closer to **$0.05**).
2. If the **dividend exceeds the value of the put opposite your short call**, you're likely to be assigned on the short call. If the underlying pays no dividend, you should essentially never be assigned on a short call.

Closing point: while there are many risks in an options position, assignment risk should generally sit at or near the **bottom** of a trader's priority list — the one clear exception being dividend-driven call assignment risk.

## A Successful Short SPX Calendar (heading present; blog post dated 8/24/10) — worked-trade case study

Setup: noted a very wide (~2-point) September-vs-October ATM call IV spread during a Mid-Day Pit Report, with the market up on the day — pushed a specific spread's price over 14.00 at one point.

**Trade**: sold the **Sep-Oct 1085 SPX call spread** (a short calendar) with SPX around 1080, for a credit of **13.25**, against a still->1.5-point IV spread between the two months. A resting bid was placed to buy the spread back at **12.20** (which alone would have represented an 8% return on a standard long calendar equivalent), but the actual fill on the next morning's open was even better — **11.75**, a **$150 profit in a single day, an 11.3% return in one day.**

Lesson drawn: this specific setup is transient/won't recur exactly, but similar setups reappear for traders who understand volatility and term structure. Explicit caution: "the other side of this calendar has lost what my trader has made" — a reminder that a calendar's edge is not free money, and is a reason not to mechanically "slap the same trade on every month" (echoing earlier chapters' rejection of formulaic, condition-blind trading).

## Butterfly Trading Checklist (heading present; blog post dated 9/13/2010) — reproduced as a literal checklist per the task's instruction

Framing: rejects the idea that "trade the same thing every month" mentors are actually trading themselves; trading is genuinely hard, and this is offered as a starting-point three-part checklist for whether it's safe to enter a butterfly (explicitly not exhaustive).

**1. Check the butterfly's own implied volatility level.** Avoid entering when IV is "sky-high" (risk of a snapback rally) *or* too low (risk of an IV pop). Sweet spot: **IV between the 25th and 75th percentile of its 90-day mean.** ✓ Check the box if IV falls in that middle range; otherwise, no check.

**2. Check that inter-month skew (term structure) isn't too wide.** Since butterflies are a front-month trade, an inter-month skew that's **too negative** (front month relatively too rich vs. back month) is a warning sign of an impending breakout. Skew that's **too positive** implies the market is moving around a lot in relative terms — also bad, since butterflies are fundamentally a gamma trade. Suggested quick proxy: compare **VIX to VXV** (30-day vs. 90-day implied vol) to gauge whether the term spread is behaving normally. ✓ Check the box if the term spread is neither too wide nor too narrow; otherwise no.

**3. Watch intra-month skew.** High intra-month skew makes butterflies a tough, expensive-to-insure trade (referenced named examples in the original blog's chart: May, June, July); low intra-month skew makes butterflies easy and cheap to insure (referenced example: August).

Caveat (author's own, reproduced): no specific numeric thresholds are given for checklist items 2 and 3 (acknowledged as something that "should be done"), and there are more factors beyond these three worth examining — but if all three items check out, a butterfly is "probably a favorable trade to enter at that given time." In the specific market example discussed in the original post, **none of the three items could be checked off**, implying an unfavorable setup at that time.

## What Is the Proper Width for an Index Butterfly's Wings? (heading present; blog post dated 11/29/2009)

Anecdote: a mentoring student believed he had a "split strike butterfly" in MNX, but the wings were spaced so wide that the position was actually functioning as an **unhedged strangle** — the long options he'd bought had "no effect on profit and loss," i.e., hedged nothing.

**Diagnosis of the common failure mode**: traders generally pick good short strikes, but frequently mis-set the *long* wing strikes — either too close (less common) or, far more commonly, **too far from the ATM strikes.**

**Purpose of the long wings, explicitly stated**: reduce margin, reduce position risk, and maximize capital efficiency. **Warning signs that wings are set too wide**:
- The longs don't meaningfully reduce the trade's margin.
- The trade's max risk is significantly greater than its max reward.
- The underlying could move a full standard deviation without materially affecting the long option's price.

Consequence of over-wide wings: excess capital at risk, a distorted (inflated) apparent return-on-capital calculation, and a tendency for traders to stay in a bad trade too long as a result of that distorted math.

**Four explicit guidelines for setting butterfly wing width** (reproduced in full, as instructed):
1. **Options worth less than $0.25 do not hedge anything** — don't buy a wing under $0.25 purely as a spread hedge (this explicitly excludes "units" bought deliberately as black-swan insurance — a distinct purpose from spread-construction hedging). Worked illustration: buying a $0.25 call as a butterfly wing, then the underlying rallies $3 — the short calls lose significantly, but the $0.25 long wing is still worth roughly $0.25, having provided essentially no offsetting protection. Buying wings worth meaningfully more than $0.25 performs better and, counterintuitively, ends up cheaper in net effect.
2. **Look for at least a one-to-one risk/reward.** If max risk exceeds max potential profit, margin can usually be reduced cheaply (or free) by moving the wings in.
3. **Always check the next-closest strike.** If moving a wing in by one strike costs less than roughly **1-to-5 dollars of margin per dollar of profit potential** gained, the wings were probably set too wide. Worked example: if narrowing a one-lot butterfly's wings by 5 points costs less than **$100**, the original wings were likely too far out.
4. **Once wing decay falls under $0.25**, either exit the trade and take the money, or "kick the wings in" to reduce margin on the remaining trade.

Closing line: following these guidelines improves capital efficiency, reduces risk taken, and generally increases profitability.

## The Importance of Good Exits (heading present)

Framing: entry conditions matter most for consistent profit, but **exits matter most for not losing significant money.** Football analogy: entries are the offense (placing trades with an edge), exits are the defense (knowing when to stop). Airplane analogy: just as flight attendants point out emergency exits before every flight, a TOMIC trader must know exit conditions *before* entering, because when things go wrong they go wrong fast.

**Two exit points required for every trade, defined before entry** (reproduced in full):
1. The exit when the trade is going against you.
2. The exit when the trade is going in your favor.

**On the losing-trade exit**: must be taken without hesitation once triggered, exactly like an emergency exit. Hesitation (hoping the market reverses) can turn a small loss into an unrecoverable large one — explicitly compared to the psychology of a losing gambler who keeps playing because they always expect their luck to turn. Predetermined exit points counter this impulse. Stated principle: **"the best loss is the first loss."**

**On the winning-trade exit**: must also be predefined, since holding for "just a bit more" risks a reversal that wipes out accumulated profit. **Recommended trigger mechanism: a percentage of margin.** Worked example: on an iron condor, set the exit at a **loss of 20% of margin** or a **gain of 15% of margin** — adjustments may be attempted while the trade is between those thresholds, but once either threshold is actually hit, exit without exception.

**Variation noted**: traders managing larger positions may scale out — e.g., selling part of the position at a 10% gain, then the rest at 15%, rather than an all-or-nothing single exit. The specific percentages given are illustrative examples, not universal rules — but having *some* predefined, disciplined exit criteria (and actually following them) is what saves money and improves profitability.

## Preparing to Trade for a Living, How Much Capital Is Needed? (heading present) — with a full worked capital-requirement calculation, reproduced in full per the task's instruction

Framing: trading for a living as a professional (fully self-directed, reporting to no one, tracking success purely via account balance) requires knowledge, mental discipline, **and** financial means.

**Step-by-step capital calculation given:**
1. Know your annual living expenses (example used: **$60,000/year**).
2. Save **at least two years' worth of living expenses** liquid before starting — in the example, **$120,000.**
3. Know your historical average trading return from part-time trading *before* attempting to trade full-time (the text explicitly requires prior trading experience first — cites an example trader averaging **2% per month return on Reg-T margin** over the prior two years, implying 500+ trades of track record).
4. Annualizing: 2%/month compounds (assuming fully invested) to roughly **24%/year** — but in reality capital utilization is rarely 100%; realistic average deployment is **40–60%**, so the example assumes **50% invested on average.**
5. **Required working (investment) capital**: to generate $60,000/year ($5,000/month) at a 2%/month return, you'd need $5,000 / 0.02 = **$250,000** if fully invested — but since only ~50% of capital is deployed at any time, actual required working capital doubles to **$500,000.**
6. **Total capital needed to trade for a living, per this worked example**: **$120,000 (savings) + $500,000 (working capital) = $620,000.**

**Closing guidance / self-assessment framework after starting**: after two years, if you've covered expenses *and* grown savings — you're doing very well. If you've covered expenses while keeping savings flat — you're doing fine. If savings have been depleted and expenses haven't been covered — **seriously consider whether trading for a living is right for you**; if still determined to continue in that scenario, the explicit recommendation is to **hire a coach and reread this book.**

## The Importance of Focus (heading present)

Opens with a diagnostic list of behavioral red flags (reproduced in full, as a self-assessment checklist):
- Felt overwhelmed by too much information?
- Wanted to trade every market a TV talking head recommended?
- Traded multiple markets with different strategies simultaneously, and lost on every one?
- Frozen "like a deer in headlights" during a flash crash?
- Over-analyzed a trade repeatedly without placing it, only to enter after the opportunity had already played out?
- Felt like switching strategies every day?
- Bought a new investment newsletter every time an email promised it was great?
- Wanted to change professions after the market moved against you?
- Traded while upset, and made costly mistakes as a result?
- Lost money trading after a close friend or relative died?

Answering yes to any of these suggests a focus problem — and focus is framed as a core success factor for a TOMIC manager (or any pursuit).

**Analogies for the importance of total focus:**
- A surgeon must not be distracted by personal matters (dinner plans, or even, in an extreme illustrative example, a parent's death) while operating — you wouldn't want a distracted surgeon operating on you regardless of their claimed competence.
- **Michael Jordan**, with the game on the line and seconds remaining, was fully "in the zone" — not hearing the crowd or opposing trash talk, focused purely on scoring.
- **Steve Jobs** (Apple) is cited as an example of focus applied to product design — his singular focus on elegant, simple devices let him surface consumer needs people didn't know they had (example given: the many uses later found for the iPad).
- **Daniel LaRusso (Ralph Macchio) in *The Karate Kid Part II* (1986)** breaking six ice slabs with one strike — achieved by concentrating all force into one small point of impact, used as a physical metaphor for concentrated focus.

**Practical conclusion for the TOMIC manager**: define who you are as a trader — know your investment strategy and how you will implement it — and once defined, **don't get sidetracked** by other people's trades, other markets, other strategies, or other products; stay focused on your own defined approach.

## Notes on completeness

All eight headings from the task's known list ("What Everybody Should Know About Payment for Order Flow," "When Should You Worry About Assignment?," "A Successful Short SPX Calendar," "Butterfly Trading Checklist," "What Is the Proper Width for an Index Butterfly's Wings?," "The Importance of Good Exits," "Preparing to Trade for a Living, How Much Capital Is Needed?," "The Importance of Focus") are present and fully covered above, each as its own standalone lesson per the task's instruction. The Butterfly Trading Checklist has been reproduced as a literal checklist and the capital-needed figures/reasoning reproduced in full, exactly as the task instructed. All figures referenced (Livevol charts, TD Ameritrade screenshots) are visual exhibits not machine-extractable as text; the narrative fully describes their numeric substance in every case. No content appears to have been missed across the full 18-page range, which was read in a single call.
