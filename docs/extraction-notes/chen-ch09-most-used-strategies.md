Source: Chen/Sebastian, *The Option Trader's Hedge Fund*, Chapter 9 "Most Used Strategies", physical pp. 105–147 (the book's longest chapter).

## Overview / Introduction (p.105)

Presents the five most-used TOMIC strategies with construction-to-exit detail for each. Framing: not all premium sales are equal — the key to success is selling insurance premium at a "good price." The chapter explicitly frames its guidance as **guidelines, not rigid rules** — every trader has different risk tolerance/goals, and traders should expect to continually tweak their approach as conditions change.

The five strategies (each its own major heading, all present in the source text as listed in the task): **The Vertical Spread**, **The Iron Condor**, **The ATM Iron Butterfly**, **The Calendar Spread or Time Spread**, **The Ratio Back and Front Spread**.

---

## The Vertical Spread (heading present)

**Definition**: general term for a bull call spread, bull put spread, bear call spread, or bear put spread — named for how the strikes lay out vertically on an option montage. Composed of a long and short option at *different strikes, same expiration*.

Framed as a foundational building block for more complex spreads (iron condor, butterfly). Described as the spread a trader would pick if "stranded on a desert island" with only one strategy allowed — familiar to beginners (who often start with covered calls or naked puts; a vertical can be built as a short put + insurance, or short call + insurance). Mostly used for directional plays (bullish or bearish).

**Four vertical spread types and when to use each:**
1. **Vertical call debit spread** (bullish) — use when partially bullish and comfortable with theta decay.
2. **Vertical put debit spread** (bearish) — use when partially bearish and comfortable with theta decay.
3. **Vertical put credit spread** (bullish) — use when partially bullish and want positive theta.
4. **Vertical call credit spread** (bearish) — use when partially bearish and want positive theta.

The chapter's focus is on the two **credit spreads** (#3 and #4) since they are theta-positive — profitable over time if the underlying doesn't move.

### Conditions
- **Best used when you have a directional opinion** on the market.
- **Volatility rule**: use vertical credit spreads in stable-or-declining volatility conditions. **Spread width should track skew steepness**: steeper skew → use narrower spreads (reduces the volatility gap between long and short strikes); flatter skew → wider spreads are fine and save on commissions.
- **Time**: typically placed with **30–60 days to expiration**, adjusted for how far OTM the spread sits — far-OTM spreads decay more linearly, so for longer trades (e.g., building toward an iron condor), 30–60 DTE entry is optimal.

### Worked Example — AAPL vertical put credit spread
- Entered Oct 13, 2011, 10 a.m., AAPL @ $405. 30-day IV = 38%, 10-day HV = 37% (IV > HV, within normal parameters); IV trending down from 51% (Oct 4) — a favorable environment for this trade.
- Trade: short 10 AAPL Nov 360 puts, long 10 AAPL Nov 350 puts, for a credit of **$1.55/spread ($1,550 total)**.
- By Nov 4: AAPL at $401 (below entry price) but IV down — Nov 360 put IV fell from 41.7% (entry) to 34.1%. Spread now worth $0.25 — **83% of credit captured**, so the trade was closed: bought to close for $250, for a **$1,300 profit** ($1,550 − $250).
- **Reg-T margin was $8,450**; profit $1,300 → **return on margin of 15.4% over 22 days.**

---

## The Iron Condor (heading present)

**Definition**: two OTM vertical spreads — a short call spread above the underlying, a short put spread below — set at a distance the underlying is unlikely to reach over the trade's life. External reference cited: Jared Woodard's ebook *Iron Condor Spread Strategies*.

### Conditions

- **Volatility**: IV does not need to be absolutely high, only **higher than the underlying's average true range (ATR)** — see Endnote 1 for the ATR definition. So an iron condor can theoretically be traded in almost any volatility regime; what matters is that IV *expectations* exceed ATR (i.e., you believe IV is too high relative to actual/expected movement). Iron condors are easier in **lower volatility**; in higher volatility you get more premium or must widen the spread, but ATR also tends to be higher then. **Key skill: sell when volatility is stable or falling, not merely because it's "high."** Worked illustration: on Aug 5, 2011, VIX traded >25% (historically elevated) but volatility was still *rising* — an iron condor sold that day would have run into trouble; a condor sold a month earlier (when VIX was lower but *declining*) would have worked out well and exited quickly. **Volatility rule: stable or declining volatility is key to a successful condor.**
- **Skew**: matters less for an iron condor than for a naked strangle (since you're long one leg against the short), but still useful for spotting red flags. In low volatility, a **slightly steeper skew is preferred** — it pushes the short put further from ATM and gives slightly more credit on the call side. **An overly steep curve is a major warning sign**, especially when IV hasn't yet rallied but skew has already caught a bid — this can presage a volatility spike, and selling a condor into rising volatility is "a recipe for disaster." Skew tends to run steep in both rising *and* falling volatility regimes; if IV is very low and skew is steep, either avoid the trade or buy heavy insurance.
- **Time**: Cross-references **Jim Bittman's *Trading Options as a Professional*** (explicitly called "a great primer for this book") on time decay — rebuts the common belief that option time premium decays exponentially across *all* strikes in the final 30 days. Per Bittman, only **ATM options** decay exponentially in the final 30 days; options further OTM decay much more linearly (a 10%-OTM option loses more value from day 60→30 than from day 30→1). Concept introduced: options have a **"cone of feasibility"** relating to when/how they decay — value is shed fastest as an option moves from being logically capable of finishing ITM to logically incapable of doing so. **Practical rule**: set up the condor to lose the bulk of its value during this "cone" window — prefer the **10–15 delta range**, and **~60 days to expiration** is called the optimal entry timing under almost all circumstances.
- **Insuring**: the greatest danger to an iron condor is neither low nor high volatility alone, but the **transition from low to high volatility** — this can "completely destroy a TOMIC." Proper use of "unit puts" (per Ch.3/Ch.8's units concept) can save the portfolio here. Guidance: if volatility sits in the lower 25% of its historical range, always spend a modest amount insuring the open condor — **no more than 10% of the credit received** is generally necessary. When volatility is already at its highest levels and declining, insurance may be unnecessary (you likely already assessed the risk fully at entry, and far-OTM puts will already have rich premium built in, making new insurance purchases inefficient).
- **The setup**: once IV is judged "too high," look to sell a **10–11 delta call**, buy the next strike out; examine strikes around 10–11 delta for mispricings (example given: an SPX 1350/1360 call spread netting more credit than a 1340/1350 spread, often due to resting public orders). Then sell a **10–12 delta put** against the call spread — you may "cheat" the put strike slightly to boost credit and flatten delta (skew naturally pushes the short put further from spot than the short call, so minor put-side adjustments don't materially change outcomes, especially once insured). **Risk/reward framing**: e.g., $2.00 credit on a 10-point spread = 200/800 risk/reward = 25% return on risk; if that trade also carries an 85% modeled probability of success, it's very favorable; at only 70% probability, much less so. Squeezing a few cents of relative pricing edge (every $0.05 counts) can cover insurance cost or commissions.
- **Goals**: a spread almost never fully decays, and letting it try to is rarely wise. Goal: capture premium as the trade exits its "cone of feasibility" — this is typically **just over 50%** of the iron condor's value, so **target ~55% of credit received**, aiming to be out by **30 days to expiration**. **Quick-profit rule**: if the trade captures 25% of the credit within 5 trading days, that signals real edge was present — exit, reassess conditions, and consider a fresh entry if appropriate (capture edge promptly).
- **Risk — two loss thresholds**:
  - **Maximum loss**: the level at which you always exit; suggested to be set equal to your profit target. Expected to be hit once or twice a year as part of normal business, offset by other winning trades.
  - **"Third Third Third Rule"**: first adjustment at 1/3 of maximum loss, second adjustment at 2/3 of maximum loss, exit at the final third (i.e., at maximum loss).
  - **Absolute maximum loss**: a hard ceiling never to be exceeded — suggested to set this at the value of credit received. If a 1.5-standard-deviation move in either direction would push the trade past absolute maximum loss, adjust or exit immediately even if maximum loss hasn't technically been hit yet.
- **Adjustments — explicitly NOT a fan of "rolling"** a trade out. Preferred adjustments: the **kite spread**, **ratio spread**, **vertical spread**, and **back ratio spread** (kite spread examples cross-referenced to **Appendix D, "Kite Spread"**). Because the condor's short strikes are set wide, managing within that range isn't especially hard; rolling/increasing size is often costly, difficult, and risky. General principle: get the most effective hedge for the least cost.

  **Upside adjustments** (ranked):
  1. **Kite spread** (primary) — reduces gamma cheaply; works in nearly all conditions except when IV is especially low.
  2. **Back ratio** (secondary) — also reduces gamma cheaply, but should be used mainly when IV is very depressed.
  3. **Call spread** (last resort) — for when a lot of delta is needed fast; only makes sense if the market is expected to "roar" higher and IV is extremely depressed; costly, so avoid unless truly necessary.
  4. **The margin trade (time call spread)** — for portfolio-margin accounts: buy a front-month call, sell a higher-strike back-month call against it. Called a strong, possibly preferred TOMIC adjustment, but complex — requires solid term-structure understanding first.
  5. **One-by-two call spread** — typically a debit on the upside but can profit even if the market reverses, if traded properly.

  **Downside adjustments** (ranked):
  1. **Ratio spread** (short 1, long 2) (primary, when volatility is normal) — used when expecting volatility to rally as the market falls; flattens the curve quickly without expanding the trade's width.
  2. **Put spread** (secondary) — cheaper than a call spread for index trades (due to put skew); versatile but still relatively expensive.
  3. **The margin trade (one-by-two front spread)** — for margin accounts: inexpensive, sets a wide tent, and (if entered properly) actually adds to P&L if the market reverses.
- **Exit**: when a goal is hit (win or loss), exit — "discipline must trump 'gut.'" Exit the *entire* position including any insurance/hedges purchased (the dollars matter) — exception: if a protective long put is worth less than $0.10, keep it rather than pay commission to sell essentially nothing. Adjustments may change margin used, but original profit/loss targets should not be revised just because capital was added or removed.

### Worked Example — SPX iron condor
- Oct 19, 2011: evaluating the January contract for a condor. IV at a premium to realized vol and trending lower; skew elevated but not extreme. Entered along liquid strikes with a favorable payout/probability tradeoff.
- Structure: **SPX 990/1000/1340/1350 iron condor**, collecting ~**$2.50**; goal to make at least **$1,250** and exit by 30 DTE.
- Over the next 30 days the trade was threatened at times but never hit the Third-Third-Third trigger. After 30 days, condor was up ~$1,000 — short of the $1,250 goal, but exited anyway given proximity to the top of the range and the 30-day exit discipline.
- Lesson drawn: "the setup made the trade" — adjusting is tempting, but the real risk-management lever is trade *entry* quality.

---

## The ATM Iron Butterfly (heading present)

**Definition**: two vertical spreads, both centered ATM — a short call spread with the short strike ATM, and a short put spread with the short strike ATM (i.e., short ATM straddle + protective long strangle around it). Goal: the underlying doesn't move, so decay of the short ATM straddle outpaces decay of the protective strangle.

### Conditions

- **Volatility**: similar surface-level rule to the condor (IV > ATR), but the underlying logic differs — an iron condor is a play on IV-vs-ATR; an **iron butterfly is more a play on how current ATR compares to expected future ATR**, combined with relatively high IV, because the fly is ATM with a narrower wingspan. Even with low ATR relative to IV, a fly can still lose to a large move or a gapping move. Iron butterflies are easier to manage in **low-volatility** environments.
- **Skew is called the single most important factor for an iron butterfly's success** (more so than for the condor) — because a fly is essentially a short straddle + long strangle, and the price paid for that protective strangle (a function of skew) determines the trade's edge.
  - Equity-fly put skew rule of thumb: if the put trades at a **>6% discount** to its "normal" skew level, that's a favorable entry; a **10% discount** is excellent; a **flat put skew** implies a likely short, probably profitable trade.
  - Mechanism: if the put is underpriced and IV later rises, the OTM put can overreact upward (beyond just normalizing skew) — cushioning losses on a spike. If IV falls, the depressed put's IV won't fall as much proportionally as ATM IV, letting the fly outperform the model's prediction on IV declines (rising skew as IV falls). If ATM IV is flat, the put skew alone is likely to normalize upward 1–2%, nudging the trade toward profit regardless.
  - **Worked numeric example**: normal SPX 10-delta put trades at 140% of ATM IV (e.g., ATM 20% → put ~28%). If that put instead trades at only 130% of ATM (26% IV, "too flat"), three scenarios: (1) ATM rises to 22% and skew normalizes → put IV jumps from 26% to ~30.8% (~5 points) vs. the <3 points it would move if skew stayed flat — this dampens the impact of the ATM IV spike on the fly; (2) ATM falls to 18% and skew normalizes → put IV barely moves (26%→25.2%), letting you capture more of the downward IV move than the model implies, shortening the required holding period; (3) ATM stable → the put skew likely normalizes 1–2% higher regardless, adding straight profit.
  - The **OTM call side matters less** and moves around less; cheaper is always better on the long call leg — a cheap long call also behaves as expected (i.e., loses little) if the underlying rallies and IV falls.
  - **Explicit skew rule**: "You want a flat put curve and a steep call curve" — noted as not as rare a combination as one might expect.
- **Time**: since the trade is ATM, entries **inside 30 days** are reasonable to capture exponential decay of the "insurance" value. No hard "too close" cutoff, but the most experienced traders avoid holding into the **final 3–4 days** before expiration due to exploding gamma on the decaying premium. **Weekly options** create meaningful opportunity to run short-dated iron butterflies and smooth returns.
- **Insuring**: iron butterflies have tightly defined risk by construction, but insurance still belongs in the broader portfolio — when IV is low (especially with flat skew), it pays off long-term to hold **1–2 unit puts for every 10 iron butterflies sold.**
- **The setup**: inside 30 days, find a product with stable/falling ATR, stable/falling ATM IV, and a flat put curve / steep call curve. Construction: sell the ATM straddle; buy wings at roughly **one standard deviation** for the number of days you plan to hold (e.g., **15–20 days** for a fly with 30 DTE). After placing wings, the position will be short delta — flatten it, ideally by buying 1–2 calls **closer to the money** (more predictable than buying many far-OTM calls) rather than with many OTM calls; stock/futures can also flatten delta. If buying unit puts (advisable), do so at this point — this may leave the trade nominally short delta overall.
- **Goals**: get in and out quickly. A well-constructed fly can return **5–10% in just a few days**. Beyond 10%, you're likely giving up edge by holding too long; chasing 15–20% by hoping nothing goes wrong is explicitly discouraged as not a sound long-term approach. **At 10%, start locking in profit** via a "strangle-tightening" technique (see below).
- **Risk**: well-constructed flies are easy to manage — if the trade breaks outside the "tent" (wing range), it should be roughly a wash; exit there. Once the profit target is hit again, either close entirely or tighten the strangle.
  - **Strangle-tightening technique**: once up ~10%, the wings will have lost much of their protective long gamma and the P&L curve starts to resemble the expiration payoff. Selling the far wings and buying wings closer in (in effect converting the fly into an **iron condor**) flattens the P&L curve again — locking in profit while staying in the trade. If the day's P&L then breaks the expiration tent after tightening, close out entirely.
  - Caution against **"tranching flies"** (adding on more butterflies as an adjustment) — explicitly warned against unless you'd enter that additional fly as a standalone trade on its own merits; every major fly-trading loss the authors have observed involved tranching. General principle: "throwing capital at a trade is not a long-term solution to making money in options."
  - **Upside adjustments**: for non-margin accounts, buy a call to clean up delta while tightening the downside half of the strangle (or use a call spread for the same effect) if the stock rallies toward the top of the tent. For margined accounts, the **call time spread** and **one-by-two ratio spread** work well (same tools as for the condor).
  - **Downside adjustments**: a well-built fly shouldn't lose on a downside break of the tent — first choice is simply to close. If staying in anyway, manage much like an iron condor: **ratio spread** (primary, when volatility is normal), **put spread** (secondary, cheaper than call spread for index due to put skew), **margin trade / one-by-two front spread** (for margined accounts — inexpensive, wide tent, adds to profit on a reversal).
- **Exit**: iron butterflies should make or lose **10% or less**. A "breakout" of the tent generally means close; hitting the 10% profit target means the edge is gone — close or tighten.

### Worked Example — SPX ATM iron butterfly (post-Christmas)
- Noted unusually flat SPX skew post-Christmas (common during holiday weeks due to fewer open positions / less hedging demand), with IV average-to-high.
- Calculated 17-day standard deviation off the 1270 strike with 18.5% ATM IV: `0.185 * SQRT(17/365) * 1270 ≈ 51`, rounded to 50.
- Structure: **SPX 1220/1270/1270/1320 iron butterfly**, sold at **41.35** (before wing/unit costs); flattened −28 delta by buying a call; also bought a far-OTM unit put (standard practice in a flat-skew environment).
- Goal: 5–10% return in a few days. The stock moved around but the trade was never in real trouble; by Jan 5, up almost **$900**, exceeding the 10% goal, so it was closed. Noted that holding 1–2 more days would have made more, but taking the disciplined profit is still correct. General lesson reiterated: well-constructed trades are easy to manage.

---

## The Calendar Spread or Time Spread (heading present)

Description: "the calendar spread, either short or long, can be the best trade a hedge fund can use." Notes that S&P 500 futures options can substitute for SPX options when selling calendars (for funds without SPX access). Distinct from butterflies/condors in that it depends on the *relationship between two different expiration months* rather than a single-expiration structure.

Core concept introduced (**cross-referenced explicitly to Ch.11 and Ch.14's later "Lessons from the Trading Floor" treatment**): **weighted vega** — different months carry different vega *and* different sensitivities to changes in realized volatility. Ideal state: a book of both long and short calendars, near-flat aggregate theta, entered under favorable conditions, with balanced weighted vega across the book — protecting the portfolio from large swings.

### Conditions

- **Volatility (long calendar)**: prefer **below-average IV and very low realized volatility**. Ideally little underlying movement plus rising IV (rare in practice) — but if IV bought is too low, a realized-vol pop will hurt the calendar regardless of the IV level bought; the underlying moving at all tends to hurt a calendar. Prefer **normal IV, not the bottom 15% of the IV range.**
- **Volatility (short calendar)**: works best at **extremes** — either superdepressed IV or very high IV — because breaking out of an extreme is what drives the trade. At high IV: long gamma + IV compression together make the short calendar a strong winner; the long gamma cushions against sharp underlying moves. At low IV: term structure matters — front-month IV, being far more sensitive, can move and generate gamma P&L even without back-month IV moving (most likely when IV is extremely low).
- **Skew**: not a major factor, since both legs are bought/sold together (skew exposure roughly nets out).
- **Term structure**: this is the core determinant — the calendar is fundamentally a "term swap," selling one month against another. Overall IV plus the front-month/back-month spread is the number one success factor.
  - **Long calendar setup**: sell the front month when it trades at a **significant premium** to its normal relationship with the back month — defined as **at least 10% of front-month IV** (e.g., front IV 20% → look for a 2-point premium over the normal relationship). Avoid entering if IV is out-of-control high across the board (possible sign of a pending event); be wary if the front premium exceeds **25%** over normal — investigate before trading, since an out-of-whack relationship always warrants scrutiny. Key principle: **sell overbought volatility, not volatility that's high for a good reason.**
  - **Short calendar setup**: the mirror image — conditions bad for a long calendar are good for a short. Look to buy a contract month trading at a **10% discount** to normal ATM IV; be wary of overly wide spreads. Key principle: **buy oversold IV, not simply sell high IV.**
- **Time**: same 30-day-to-expiration guideline as butterflies, with two exceptions: (1) if IVs are badly out of whack, any two months can be swapped against each other (e.g., a 5-month vs. 6/7/8-month contract, especially in ETFs/index products) — far-out-month distortions are usually liquidity-driven rather than event-driven; (2) trading a calendar into the **final days before expiration is harder to manage than a butterfly** because gamma explodes against the back-month leg, and IV relationships become less relevant — inside the final week, it's essentially a straddle-price trade, not an IV trade.
- **The setup (long)**: sell an ATM option, buy the same strike one month out, when the relationship is ~10% out of line; unwind once back in line. Prefer buying relative mid-range IV, and confirm IV has been *stable* (don't try to "catch a falling knife") — a stable, mid-range-IV setup is a good long candidate.
- **The setup (short)**: look for ultra-low or ultra-high overall IV with the bought month cheaper than the sold month; close once the spread realigns. Trading overall high IV while ignoring the specific month-to-month spread is possible but reserved for the most experienced traders.
- **Goals**: **5–10% in a few days**; going for more implies hoping the underlying and IV don't move against you, which isn't the actual edge in the trade — "hedge fund traders trade volatility, not theta decay of calendars." If the trade reaches breakeven at expiration, kill it — don't add to a trade heading toward flat/slightly down.
- **Risk**: rarely worth adding to a well-constructed calendar — most large calendar losses come from adding more time spreads once already out of the tent. Some adjustment room exists, especially on the short side:
  - On a still-out-of-whack **long** calendar, you may add — but only under conditions as good as or better than the original entry, and only while flattening delta at the same time; if conditions aren't as good, don't add via another calendar (instead, buy an option in the *cheaper* month to cut delta).
  - On the **short** side, underlying movement itself tends to be profitable; if the underlying moves but conditions don't otherwise change, you can scalp long gamma — but use a conservative "pay the decay" approach, only in small increments, and only up to about a one-day standard deviation move; don't scalp back-and-forth repeatedly (gamma scalping here is meant to defend against time decay, not as a standalone profit engine). At 10%, take the profit.
- **Exit**: never lose more than **10%** of the original margin — exit at that threshold; target no more than 10% return; if 5% is achieved in under a day, treat it as a gift and close.

### Worked Example — Long Calendar (OEX Dec/Jan call spread)
- Nov 16, 2010, 3 p.m.: OEX Dec-Jan call spread setup — overall IV low (~19%), but a minor market shock pushed December IV to a premium over January.
- Entered: sold December, bought January for **4.80** net.
- Outcome: overnight, December IV fell and January IV rose slightly — trade made **over 5% overnight**. Emphasized point: the calendar's edge comes from correcting mispriced volatility, not from simply holding for decay.

### Worked Example — Short Calendar (SPX Dec-Jan 1220 call spread)
- Dec 16: January options became oversold relative to February; overall volatility elevated.
- Entered: SPX Dec-Jan short 1220 call calendar, net sale of **14.10** (selling Feb at 24.4% IV, taking in a 1.6% volatility-terms credit on the front).
- By Dec 20: front month fell further, but the underlying moved and back-month options sold off harder — bought to close for **13.40**, a profit of **~$0.80 in 4 days** (>5% in days). Noted that with more patience, as the underlying kept rallying, the trade could have reached **20%** just by holding the oversold options.

---

## The Ratio Back and Front Spread (heading present)

**Definition**: "the ratio spread can be one of the best trades a hedge fund can apply." Without portfolio margin, **buying 2 and selling 1** (a **back spread**) is typically the only usable version; with portfolio margin, **buying 1 and selling 2** (a **front spread**) becomes accessible. Unlike the butterfly, this spread adds a **third dimension — direction** — beyond skew and volatility; being right on direction is not always required, but being right on skew *and* volatility is necessary, and adding correct direction makes the trade "wildly successful."

### Conditions

- **Volatility**: a back spread is almost always **net long vega** at initiation (two longs outweigh one short in vega terms initially, though this fades over time all else equal). **Rule: only enter when IV is in the lower 40% of its current range** — otherwise the trade needs a large directional move to succeed since it can't rely on IV expansion.
- **Skew**: because you sell one ATM option and buy two OTM options, skew materially affects the trade — flatter skew is better (per the butterfly discussion), since you want to buy the OTM curve as cheaply as possible, ideally while IV is also low. If the public later bids up those OTM options (even without IV moving broadly) or if IV itself rises (normalizing skew), the position benefits — a pop in IV, in skew, or both can produce a profitable exit without the underlying even moving. Combine that with correct direction for a very large win. Conversely: **steep skew + high volatility can cause a loss even if directionally correct** — ignoring IV/skew here is "throwing money down the drain."
- **Time**: workable in any time frame — key is picking the month with the **lowest relative IV** (compare the ~60-day option's IV against its own historical 60-day-IV norm). Trades closer to expiration depend more on the underlying actually moving; trades further out depend more on volatility movements. For a directional bet, use whatever month sets up well; for a portfolio hedge or long-IV play, prefer **at least 60 days to expiration.**
- **The setup**: aim for the same flat-skew profile sought in butterflies — target skew **7–10% underpriced**, with IV in the **lower 40th percentile** of its historical range. Sell one ATM/near-ATM put or call; buy two OTM options (calls or puts) against it, such that net premium paid for the two longs is **less than** the value of the one short — i.e., enter for a **net credit or at worst zero cost**, so a wrong directional bet can still be salvaged by a volatility move. Don't chase a large credit — accepting only a small credit lets the two long positions "hang in" longer.
- **Goals**: same volatility-trade discipline as other strategies — **get in, take ~10%, get out**; never target more than 10%.
- **Risk**: few adjustments make sense. If the trade isn't working, close it. If conditions turn against the position and it's losing, close it. If conditions have actually improved (even though the trade is currently losing) and capital isn't overcommitted, adding is reasonable.
- **Exit**: take the win (or at least lock it up) at **10%**; never let a loss exceed **10% of original margin** (using any added margin if the trade was scaled up).

### The One-by-Two (One Long, Two Short) — front spread variant

Described as similar to a calendar spread in character — conditions that hurt a back ratio spread tend to favor a one-by-two. Key structural requirement: **the trade must generate a credit.** Unlike the back-ratio spread (which wants the underlying to move *toward* the long strikes), a one-by-two profits from the underlying moving *away* from the two short strikes — as it does, skew flattens and IV compresses, and the position (sold at a credit) becomes closeable at a credit as well — a clear signal it's time to close. As with all these trades, the goal is the standard ~10%, not a "home run."

### Worked Example — SPX Ratio Back Spread
- June 6, 2011: VIX near all-time lows; skew relatively flat (10-delta put trading at only 135% of ATM, versus a richer historical norm).
- Entered: sold July ATM SPX 1280 puts, bought **2x** July 1230 puts (a back spread) — long gamma, long vega, slightly short delta; limited loss potential if SPX instead rallied.
- Thesis: IV rallies and the underlying falls together; since skew was flat, hoped skew would also steepen so the 1230s gained more than the pricing model predicted.
- By June 15: IV rose, SPX dropped, skew increased incrementally — trade profitable. Exited June 16 for a significant gain. Explicit conclusion: **direction helped but was the least important part of the trade** — skew, time, and volume being on the trader's side mattered more.

---

## Endnote (heading present)

1. **Average True Range (ATR)** — a volatility measure introduced by Welles Wilder in *New Concepts in Technical Trading Systems*. ATR = a moving average (typically 14 days) of "true range" values. **True range** = the greatest of: (1) current high minus current low; (2) absolute value of the most recent period's high minus the previous close; (3) absolute value of the most recent period's low minus the previous close.

## Notes on completeness

All five strategy headings from the task's known list ("The Vertical Spread," "The Iron Condor," "The ATM Iron Butterfly," "The Calendar Spread or Time Spread," "The Ratio Back and Front Spread") plus "Endnote" are present and fully covered above, each with construction, entry criteria, greeks profile, management/adjustment rules, exit criteria, and worked examples as instructed. This is an extremely dense, example-heavy chapter (all figures referenced in the source are OptionVue6 screenshots and are not machine-extractable as text — their content has been reconstructed from the surrounding narrative description in every case, which appears to fully describe each figure's substance). No sub-heading or worked example appears to have been missed across the three read batches (pp.105–119, 120–133, 134–147); batch boundaries were checked for continuity and no content was dropped between them. This chapter is flagged as a primary source for both `spreads-and-combinations.md` and `income-strategies.md` synthesis per the plan, and the "weighted vega" concept introduced here under the Calendar Spread section is the first mention of that term in the book — it recurs and is treated in more depth in Ch.11 and Ch.14, per those chapters' extraction notes.
