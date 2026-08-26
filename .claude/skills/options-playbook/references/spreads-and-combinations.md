# Spreads and Combinations

Multi-leg option structures: vertical spreads, iron condors, iron butterflies (and
their broken-wing/unbalanced variants), calendar and diagonal spreads, ratio
spreads, the kite spread, and the arbitrage-oriented combinations (conversions,
reverse conversions, box spreads). For single-leg directional positions and
synthetic equivalences, see `directional-strategies.md`. For premium-selling
framing of credit spreads/condors as an "insurance" income business, see
`income-strategies.md`. For the Greeks mechanics and volatility/skew concepts
referenced throughout (vega, weighted vega, skew, term structure), see
`greeks-and-volatility.md`. For sizing, black-swan "units," and the Card Game
Value heuristic that governs when to exit a decayed credit spread, see
`risk-management-and-position-sizing.md`.

Primary sources: Chen/Sebastian ch.9 ("Most Used Strategies," the book's five
core strategies), ch.13 ("Lessons from the Trading Floor on Trading and
Execution" — Butterfly Trading Checklist, wing-width guidance), ch.10 (broken-
wing/unbalanced variants), Appendix D (Kite Spread); Bittman ch.1 (vertical
spread P/L basics), ch.6 (Arbitrage Strategies — conversions, reverse
conversions, box spreads), ch.9 (market-maker construction of butterflies,
reverse conversions, and box spreads via delta-neutral trades), ch.10 (position-
risk comparison of vertical spreads vs. outright options).

---

## 1. Vertical Spreads

### Construction

A vertical spread combines a long and short option of the **same type** (both
calls or both puts), **same underlying and expiration, different strikes** —
named for how the strikes stack vertically on an option montage (Chen/Sebastian
ch.9). Four variants (Chen/Sebastian ch.9):

| Spread | Legs | Debit/Credit | Directional bias | Theta |
|---|---|---|---|---|
| Vertical call debit spread ("bull call spread") | buy lower-strike call, sell higher-strike call | debit | bullish | negative (decay hurts) |
| Vertical put debit spread ("bear put spread") | buy higher-strike put, sell lower-strike put | debit | bearish | negative |
| Vertical put credit spread | sell higher-strike put, buy lower-strike put | credit | bullish | positive (decay helps) |
| Vertical call credit spread ("bear call spread") | sell lower-strike call, buy higher-strike call | credit | bearish | positive |

Per Bittman ch.1's P/L-diagram treatment of the debit versions: a **bull call
spread** (buy lower-strike call, sell higher-strike call) has breakeven =
lower strike + net premium paid, max risk = net debit, max profit = strike
width − net debit. The **bear call spread** is the mirror image (net credit,
same breakeven formula, profits below breakeven). Chen/Sebastian's chapter
focuses on the two **credit** spreads specifically because they carry positive
theta — they profit from time decay if the underlying doesn't move much.

Verticals are also the foundational building block for the more complex
structures below: an iron condor is two vertical credit spreads (a call
spread + a put spread); an iron butterfly is two verticals centered ATM; a
box spread (§8) is a call vertical + a put vertical at the same two strikes.

### Greeks Profile

A vertical spread carries **meaningfully lower Greeks across the board** than
the equivalent outright long option, because the short leg's opposite-signed
Greeks partially offset the long leg's. Per Bittman ch.10's worked comparison
(20 long 70 Calls vs. 20 long 70-75 bull call spreads, same underlying/time/
vol assumptions): the spread's price, delta, gamma, vega, and theta are all
reduced relative to the outright — e.g., delta 546 vs. 1,070, gamma 20 vs.
118, vega 42 vs. 174, theta −170 vs. −620.

**A vertical spread's Greek character is not static — it can fully reverse
sign as the underlying moves between the two strikes.** Per Bittman ch.10's
70-75 bull call spread example: with the underlying at the lower (long) strike,
the spread is gamma-positive/vega-positive/theta-negative (a bullish,
long-volatility, time-hurts profile); with the underlying at the higher (short)
strike, the same spread becomes gamma-negative/vega-negative/theta-positive (a
bullish-but-time-helps, volatility-decline-helps profile) even though delta
stays directionally positive throughout. Practical implication: **a vertical
spread can outperform an outright long option specifically in a declining-IV
environment**, because it is far less vega-sensitive (Bittman ch.10's two-
scenario comparison: identical price/time move, but with IV also falling, the
spread outgained the outright call).

### Entry Criteria

- **Directional opinion required** — verticals are Chen/Sebastian's pick for a
  trader with a market view, unlike the volatility-only strategies below.
- **Volatility**: use credit spreads in stable-or-declining IV conditions.
- **Skew should govern spread width**: steeper skew → use a **narrower**
  spread (reduces the IV gap between the long and short strikes); flatter
  skew → wider spreads are fine and save commissions (Chen/Sebastian ch.9).
- **Time**: typically 30–60 days to expiration, adjusted for how far OTM the
  spread sits (far-OTM spreads decay more linearly — see the moneyness-based
  decay-rate findings in `greeks-and-volatility.md`).
- **Don't anchor to a fixed delta, fixed %-OTM, or fixed spread width.**
  Evaluate the whole strike surface and sell whichever nearby strike/width
  offers the best relative credit (Chen/Sebastian ch.4) — e.g., prefer an
  11-delta strike over a 10-delta target if it's genuinely richer, or a
  15-point-wide spread over a habitual 5-point width if the credit justifies it.
- **Use vega to set a minimum acceptable price** before entry: net vega ×
  (your maximum acceptable IV concession, in points) = the dollar amount
  you're willing to give up; below that price, walk away rather than
  concede edge (Chen/Sebastian ch.4 worked example: vega 0.05, willing to sell
  down 1 IV point → $0.05 of price flexibility, no further).

### Management and Adjustment

- Verticals are the building blocks used to adjust larger structures (iron
  condors, butterflies) — see §2–3's adjustment tables, where a vertical
  spread itself is listed as a downside-adjustment tool for both.
- Per Chen/Sebastian ch.12's **Card Game Value**: as a short-leg credit spread
  decays toward $0.10–$0.25, it stops trading on the pricing model and starts
  trading on residual "lottery ticket" value that decays far more slowly than
  theory predicts. Don't wait for full decay to zero — exit once the position
  is clearly in Card Game Value territory (full heuristic in
  `risk-management-and-position-sizing.md`).
- Per Chen/Sebastian ch.13's "Importance of Good Exits": define both a losing-
  trade exit and a winning-trade exit *before* entry, typically as a
  percentage of margin (e.g., iron-condor example: −20% of margin / +15% of
  margin).

### Exit Criteria

- Worked AAPL example (Chen/Sebastian ch.9): a vertical put credit spread
  captured 83% of its credit in 22 days and was closed rather than held for
  full decay — 15.4% return on Reg-T margin.
- General rule across all these strategies (§1–6): **take profit around 10%
  of margin/credit and get out**; chasing more usually means hoping IV and
  price don't move against you, which isn't the actual edge in the trade.

---

## 2. Iron Condors

### Construction

Two out-of-the-money vertical **credit** spreads on the same underlying and
expiration — a short call spread above the underlying, a short put spread
below — set at a distance the underlying is unlikely to reach over the
trade's life (Chen/Sebastian ch.9, citing Jared Woodard's *Iron Condor Spread
Strategies*). Chen/Sebastian ch.10 also names an **unbalanced iron condor**
variant (asymmetric width and/or distance on the call side vs. the put side,
e.g., to reflect skew) as one of TOMIC 1.0's starter strategies, alongside
the standard symmetric condor — the source doesn't give unbalanced-condor
construction detail beyond naming it as a live variation traders use.

### Greeks Profile

Net short vega and short gamma (a "sell insurance" structure, per the
premium-selling framing in `income-strategies.md`), positive theta. Skew
matters less for an iron condor than for a naked strangle, since the long
wing partially offsets the short strike, but skew still flags red flags: an
overly steep curve while IV hasn't yet rallied can presage a volatility spike.

### Entry Criteria

- **Volatility**: IV doesn't need to be absolutely high — only higher than
  the underlying's Average True Range (ATR; Welles Wilder's 14-day moving
  average of true range — see the endnote definition in Chen/Sebastian
  ch.9). **Key skill: sell when volatility is stable or falling, not merely
  because it's "high."** A condor sold while IV is still rising (even at an
  already-elevated level) runs into trouble; the same condor sold a month
  earlier, while IV was lower but declining, works out.
- **Skew**: in low volatility, a slightly steeper skew is preferred (pushes
  the short put further OTM, adds a little call-side credit). An overly steep
  curve combined with still-low IV is a warning sign — avoid or insure
  heavily.
- **Time**: per Bittman's time-decay findings (only ATM options decay
  exponentially in the final 30 days; further-OTM options decay more
  linearly — the "cone of feasibility"), set up the condor to lose the bulk
  of its value inside that cone. Prefer the **10–15 delta** range and **~60
  days to expiration** as the near-universal optimal entry.
- **Relative pricing check**: examine strikes around the target delta for
  mispricings from resting orders before finalizing which strike to sell.
- **Risk/reward framing**: e.g., a $2.00 credit on a 10-point-wide spread =
  200/800 risk/reward (25% return on risk); combine with the model's
  probability of success to judge the trade (85% probability at that
  risk/reward is very favorable; 70% is much less so).

### Management and Adjustment

- **Insuring**: the greatest danger to a condor is neither low nor high
  volatility alone but the **transition from low to high** — this can
  "completely destroy a TOMIC." If volatility sits in the lower 25% of its
  historical range, spend a modest amount insuring the open condor (no more
  than ~10% of the credit received) via unit puts (see
  `risk-management-and-position-sizing.md`).
- **Two loss thresholds**: a **maximum loss** level (set equal to the profit
  target; expected to be hit once or twice a year as normal business) and an
  **absolute maximum loss** (a hard ceiling, suggested at the value of credit
  received, never to be exceeded). The **"Third-Third-Third Rule"**: first
  adjustment at 1/3 of maximum loss, second at 2/3, exit at the final third.
- **Explicitly not a fan of "rolling"** the trade out — rolling/increasing
  size is often costly, difficult, and risky given how wide the short strikes
  already are.
- **Upside adjustments, ranked**: (1) **kite spread** (primary — cheap gamma
  reduction, works in nearly all conditions except very low IV; §7); (2)
  **back ratio spread** (secondary — also cheap gamma reduction, best when IV
  is very depressed; §6); (3) **call spread** (last resort — fast delta when
  the market is expected to "roar" higher and IV is extremely depressed;
  costly); (4) **the margin trade / time call spread** (portfolio-margin
  accounts: buy a front-month call, sell a higher-strike back-month call —
  strong but complex, requires solid term-structure understanding); (5)
  **one-by-two call spread** (§6 — typically a debit on the upside but can
  profit even on a reversal if traded properly).
- **Downside adjustments, ranked**: (1) **ratio spread** (short 1, long 2;
  primary when volatility is normal — flattens the curve quickly without
  widening the trade); (2) **put spread** (secondary, cheaper than a call
  spread for index trades due to put skew); (3) **the margin trade / one-by-
  two front spread** (inexpensive, sets a wide tent, and can add to P&L on a
  reversal).
- General adjustment principle: get the most effective hedge for the least
  cost; the condor's wide short strikes make in-range management manageable
  without resorting to rolling or size increases.

### Exit Criteria

- A spread almost never fully decays — letting it try to is rarely wise.
  **Target ~55% of credit received**, aiming to be out by **30 days to
  expiration** (captures the trade as it exits its "cone of feasibility,"
  typically just over 50% of the condor's value).
- **Quick-profit rule**: if 25% of the credit is captured within 5 trading
  days, that signals real edge was present — exit, reassess, and consider a
  fresh entry.
- When a goal is hit (win or loss), exit the entire position including any
  insurance/hedges — "discipline must trump 'gut.'" (Exception: a protective
  long put worth under $0.10 isn't worth paying commission to close.)
  Adjustments may change margin used, but original profit/loss targets
  should not be revised just because capital was added or removed.
- Worked SPX example (Chen/Sebastian ch.9): a 990/1000/1340/1350 iron condor
  collecting ~$2.50, goal $1,250 by 30 DTE, was closed at ~$1,000 (short of
  goal) anyway once 30 DTE arrived, given proximity to the top of the range —
  "the setup made the trade," not the adjustment.

---

## 3. ATM Iron Butterfly

### Construction

Two vertical spreads, both centered **at-the-money**: a short call spread
with the short strike ATM, and a short put spread with the short strike
ATM — equivalently, a short ATM straddle wrapped in a protective long
strangle (Chen/Sebastian ch.9). Chen/Sebastian ch.10 names a **broken-wing
butterfly** variant — an asymmetric-wing version — among TOMIC 1.0's starter
strategies alongside the standard symmetric fly; the source doesn't give
broken-wing construction detail beyond naming it as a live variation.

### Greeks Profile

Net short gamma, short vega near the center, positive theta while the
underlying stays near the short strikes. Where an iron condor is a play on
IV vs. ATR, **an iron butterfly is more a play on how current ATR compares to
expected future ATR**, combined with relatively high IV, because the fly is
ATM with a narrower wingspan — even with low ATR relative to IV, a fly can
still lose to a single large or gapping move.

**Skew is the single most important factor for a butterfly's success** (more
so than for a condor), because the fly is economically a short straddle plus
a long strangle, and the price of that protective strangle (a function of
skew) sets the trade's edge:

- Equity-fly put-skew rule of thumb: put trading at a **>6% discount** to its
  normal skew level is favorable; a **10% discount** is excellent; a **flat**
  put skew implies a likely-profitable trade.
- Mechanism: an underpriced put that later normalizes upward as IV rises
  cushions losses beyond what the model predicts; if IV falls instead, the
  already-cheap put's IV won't fall proportionally as much, letting the fly
  outperform the model on the downside too; if ATM IV is flat, the put skew
  alone tends to normalize 1–2% higher, adding straight profit regardless.
- The **OTM call side matters less** — cheaper is always better on the long
  call leg.
- **Explicit skew rule: "you want a flat put curve and a steep call curve."**

### Entry Criteria

- Entries **inside 30 days** are reasonable (captures exponential decay of
  the ATM "insurance" value), but avoid holding into the **final 3–4 days**
  before expiration — gamma explodes on the decaying premium. Weekly options
  enable running short-dated flies to smooth returns.
- Find a product with stable/falling ATR, stable/falling ATM IV, and the flat-
  put/steep-call skew shape described above.
- **Construction sizing**: sell the ATM straddle; buy wings at roughly **one
  standard deviation** for the intended holding period (e.g., 15–20 days for
  a fly planned to run 30 DTE — see §3's "Index Butterfly Wing Width"
  guidance below for the exact SD-based sizing formula). After placing
  wings, the position will be short delta — flatten it, preferably by
  buying 1–2 calls **closer to the money** (more predictable than several
  far-OTM calls) rather than stock/futures. Add unit puts at this point if
  insuring (see below).
- **Insuring**: hold **1–2 unit puts for every 10 iron butterflies sold**,
  especially when IV is low with flat skew.

### Management and Adjustment

- **Goal: get in and out quickly.** A well-constructed fly can return 5–10%
  in just a few days; beyond 10%, edge is likely being given up by holding
  too long. Chasing 15–20% by hoping nothing goes wrong is explicitly
  discouraged.
- **Strangle-tightening technique**: once up ~10%, the wings have lost much
  of their protective long gamma. Sell the far wings and buy wings closer in
  (converting the fly into an iron condor) to flatten the P&L curve again —
  locking in profit while staying in the trade. If day's P&L then breaks the
  expiration tent after tightening, close entirely.
- **Explicit warning against "tranching flies"** (adding more butterflies as
  an adjustment) — every major fly-trading loss the authors observed
  involved tranching. Only add a fly if you'd enter it as a standalone trade
  on its own merits.
- **Upside adjustments**: for non-margin accounts, buy a call (or a call
  spread) to clean up delta while tightening the downside half of the
  strangle. For margined accounts, a call time spread or a one-by-two ratio
  spread (§6) work well.
- **Downside adjustments**: a well-built fly shouldn't lose on a downside
  break of the tent — first choice is simply to close. If staying in,
  manage like a condor: ratio spread (primary, normal vol), put spread
  (secondary), margin-account one-by-two front spread.

### Exit Criteria

- Iron butterflies should make or lose **10% or less**. A breakout of the
  tent generally means close; hitting the 10% profit target means the edge
  is gone — close or tighten.
- Worked post-Christmas SPX example (Chen/Sebastian ch.9): SPX 1220/1270/
  1270/1320 fly, sold at 41.35, flattened with a call purchase and a unit
  put; up almost $900 (exceeding the 10% goal) within days — closed on
  schedule per the discipline even though holding longer would have made
  slightly more.

### Butterfly Trading Checklist (Chen/Sebastian ch.13, reproduced in full)

A three-part, explicitly non-exhaustive checklist for whether it's safe to
enter a butterfly:

1. **Check the butterfly's own implied volatility level.** Avoid entering
   when IV is "sky-high" (snapback risk) *or* too low (IV-pop risk). Sweet
   spot: **IV between the 25th and 75th percentile of its 90-day mean.**
2. **Check that inter-month skew (term structure) isn't too wide.** Too
   negative (front month too rich vs. back month) warns of an impending
   breakout; too positive implies the market is moving around a lot in
   relative terms — also bad, since a fly is fundamentally a gamma trade.
   Quick proxy: compare **VIX to VXV** (30-day vs. 90-day IV) to gauge
   whether the term spread is behaving normally.
3. **Watch intra-month skew.** High intra-month skew makes flies tough and
   expensive to insure; low intra-month skew makes them easy and cheap to
   insure.

No numeric thresholds are given for items 2–3 (acknowledged by the authors
as something that "should be done" but left qualitative), and more factors
beyond these three are worth examining — but if all three check out, a
butterfly is "probably a favorable trade to enter at that given time."

### Index Butterfly Wing-Width Guidance (Chen/Sebastian ch.13, reproduced in full)

**Common failure mode**: traders generally pick good short strikes but
mis-set the long wing strikes — usually **too far from the ATM strikes**,
which turns the position into an effectively unhedged strangle (the long
wings "have no effect on profit and loss"). Purpose of the long wings:
reduce margin, reduce position risk, and maximize capital efficiency.

**Warning signs the wings are set too wide**: the longs don't meaningfully
reduce margin; max risk is significantly greater than max reward; the
underlying could move a full standard deviation without materially affecting
the long option's price. Consequence: excess capital at risk, an inflated
(distorted) apparent return-on-capital, and a tendency to stay in a bad trade
too long as a result.

**Four explicit guidelines for setting wing width:**

1. **Options worth less than $0.25 do not hedge anything** — don't buy a
   wing under $0.25 purely as a spread hedge (this excludes "units" bought
   deliberately as black-swan insurance, a distinct purpose). A $0.25 wing
   still worth ~$0.25 after a $3 rally has provided essentially no
   offsetting protection; buying wings meaningfully above $0.25 performs
   better and, counterintuitively, ends up cheaper in net effect.
2. **Look for at least a one-to-one risk/reward.** If max risk exceeds max
   potential profit, margin can usually be reduced cheaply (or free) by
   moving the wings in.
3. **Always check the next-closest strike.** If moving a wing in by one
   strike costs less than roughly **$1–$5 of margin per dollar of profit
   potential** gained, the wings were probably set too wide (e.g., if
   narrowing a one-lot fly's wings by 5 points costs less than $100, the
   original wings were likely too far out).
4. **Once wing decay falls under $0.25**, either exit and take the money, or
   "kick the wings in" to reduce margin on the remaining trade.

**Standard-deviation wing-sizing formula** (used in the worked post-Christmas
example above): `SD = ATM_IV × SQRT(holding_days / 365) × underlying_price`,
rounded to the nearest strike, sized to the intended holding period (e.g., an
18.5-day holding assumption is one author's own standing practice per
Chen/Sebastian ch.11's low-VIX tips). This makes wings automatically wider in
high-IV months and tighter in low-IV months.

---

## 4. Calendar Spread (Time Spread)

### Construction

Sell one expiration's option and buy the same-strike option in a different
expiration, same underlying, same option type (call or call, put or put) —
depends fundamentally on the *relationship between two expiration months*
rather than a single-expiration structure (Chen/Sebastian ch.9). Described as
possibly "the best trade a hedge fund can use." S&P 500 futures options can
substitute for SPX options for funds without SPX access.

- **Long calendar**: sell the front month, buy the back month (net debit) —
  profits from the front month decaying faster than the back month and/or
  from a front-month IV premium correcting.
- **Short calendar**: buy the front month, sell the back month (net credit) —
  profits from breaking out of an extreme IV regime (very high or very low).

### Greeks Profile

Central concept: **weighted vega** — different expiration months carry
different vega *and* different sensitivity to realized-volatility changes
(front-month IV is far more "frenetic"/reactive than back-month IV, largely
because front-month price action has a more permanent, delta-moving gamma
effect — see `greeks-and-volatility.md` for the full weighted-vega mechanics
from Chen/Sebastian ch.9/11/14). A calendar's *raw* (unweighted) vega can look
flat or modest while its *weighted* vega is significantly net long or short —
this is the entire point of tracking weighted vega separately. Skew is not a
major factor for a calendar since both legs are bought/sold together and
skew exposure roughly nets out.

### Entry Criteria

- **Term structure is the core determinant** — overall IV plus the front-
  month/back-month spread is the number one success factor.
- **Long calendar setup**: sell the front month when it trades at a
  significant premium to its normal relationship with the back month —
  defined as **at least 10% of front-month IV** over the normal relationship
  (e.g., front IV 20% → look for a 2-point premium). Avoid if IV is
  out-of-control high across the board (possible pending-event risk); be
  wary above a **25%** premium — investigate before trading. Key principle:
  **sell overbought volatility, not volatility that's high for a good
  reason.** Prefer below-average IV and very low realized volatility for the
  underlying itself; prefer normal IV, not the bottom 15% of the range.
- **Short calendar setup**: the mirror image — buy a contract month trading
  at a **10% discount** to normal ATM IV; be wary of overly wide spreads.
  Key principle: **buy oversold IV, not simply sell high IV.** Works best at
  volatility *extremes* (superdepressed or very high IV), since breaking out
  of an extreme drives the trade.
- **Time**: same ~30-day guideline as butterflies, with two exceptions: (1)
  if IVs are badly out of whack, any two months can be swapped (e.g., 5-
  month vs. 6/7/8-month, especially in ETFs/index products — far-out-month
  distortions are usually liquidity-driven); (2) avoid trading a calendar
  into the final days before expiration — gamma explodes against the back-
  month leg and it becomes a straddle-price trade, not an IV trade.
- Chen/Sebastian ch.2 notes calendars suit a market forecast of sideways
  movement over the trade's life with a stable month-to-month volatility
  relationship.

### Management and Adjustment

- **Rarely worth adding to** a well-constructed calendar — most large
  calendar losses come from adding more time spreads once already out of the
  tent.
- On a still-out-of-whack **long** calendar, adding is acceptable only under
  conditions as good as or better than the original entry, while flattening
  delta at the same time; otherwise cut delta by buying an option in the
  cheaper month instead of adding another calendar.
- On the **short** side, underlying movement itself tends to be profitable —
  a conservative "pay the decay" gamma-scalp is acceptable in small
  increments, up to about a one-day standard-deviation move, but don't scalp
  back-and-forth repeatedly (see the "Pay the Decay" formula in
  `greeks-and-volatility.md`, Chen/Sebastian ch.14).
- Watch for event-driven month spreads (earnings, FDA announcements,
  corporate actions, dividends) before treating a wide inter-month spread as
  a tradeable mispricing — "if a swap seems too good to be true, it probably
  is" (Chen/Sebastian ch.8).

### Exit Criteria

- Goal: **5–10% in a few days**; going for more implies hoping the underlying
  and IV don't move against you — "hedge fund traders trade volatility, not
  theta decay of calendars." If the trade reaches breakeven at expiration,
  kill it rather than adding.
- **Never lose more than 10%** of the original margin — exit at that
  threshold. If 5% is achieved in under a day, treat it as a gift and close.
- Worked long-calendar example (OEX Dec/Jan call spread, Chen/Sebastian ch.9):
  sold Dec, bought Jan for 4.80 net; overnight Dec IV fell and Jan IV rose
  slightly → over 5% profit overnight.
- Worked short-calendar example (SPX Dec-Jan 1220 call calendar): sold at
  14.10, closed 4 days later at 13.40 for ~5%+ in days; a real-trade case
  study (Chen/Sebastian ch.13) shows a short Sep-Oct SPX calendar sold for
  13.25 bought back at 11.75 the next morning — an 11.3% one-day return —
  with the explicit caution that "the other side of this calendar has lost
  what my trader has made," i.e., not a mechanically repeatable free trade.

---

## 5. Diagonal Spreads

### Construction

A diagonal spread combines a calendar spread's different-expiration
structure with a vertical spread's different-strike structure — different
strike **and** different expiration (an extension of the calendar concept
listed among the strategy types Op-Eval Pro's Spread Positions screen
handles, per Bittman ch.2, and named as a strategy type a Level 1/intermediate
TOMIC trader should understand per Chen/Sebastian ch.6).

**Double diagonal** (Chen/Sebastian ch.11): sell a front-month OTM call and
put, buy a further-out back-month OTM call and put — i.e., a diagonal built
on both the call side and the put side simultaneously, effectively an iron
condor stretched across two expirations. Worked OEX example: front month
(elevated but not extreme IV) sold against a further-out back month, with a
raw (unweighted) vega of ~82 that, once properly weighted, was actually
short ~170 weighted vega — illustrating why weighted vega (not raw vega)
must govern sizing for this structure (see `greeks-and-volatility.md`).
Profits if skew flattens, if the near-vs-far month spread tightens, or if IV
broadly falls from an elevated level. Described as "the most underutilized
and possibly the best play for the money" in that market environment, and a
way to trade the front-month "smile" without the capital outlay of a full
strangle.

### Greeks Profile

Like the calendar, weighted vega (not raw vega) governs the real volatility
exposure — see §4. Chen/Sebastian ch.4's order-fill-difficulty ranking places
**double diagonals** as the third-hardest complex order type to get filled
efficiently (harder than iron condors and straddles are easier still),
behind only "nontraditional spreads" and iron condors themselves — a
practical execution consideration when choosing this structure.

### Entry Criteria

Same term-structure and skew evaluation as calendars (§4) and iron
condors/butterflies (§2–3): favorable when the front month is elevated
relative to further-out months (sell it) and skew on both wings is rich
enough to justify selling. Chen/Sebastian ch.11's four tips for a depressed-
VIX-cash/wide-term-structure environment apply directly (avoid pure long
term-risk plays like this one when the spread is unusually wide, unless
overlaying extra back-month IV exposure or a cheap front-month strangle
hedge — full detail in `greeks-and-volatility.md`).

### Management and Adjustment

Managed like the calendar and condor structures it combines — see §2 and
§4's adjustment tables; the weighted-vega recalculation should be rerun
whenever the position is adjusted, since a diagonal's raw Greeks can mask a
materially different weighted exposure.

### Exit Criteria

Same discipline as calendars and condors: target a modest (~10%) return on
margin, exit promptly once the term-structure or skew edge that motivated
the trade has closed.

---

## 6. Ratio Back and Front Spreads

### Construction

**Back spread** (buy more than you sell): sell 1 ATM/near-ATM option, buy 2
further-OTM options of the same type — the ordinary retail version without
portfolio margin. **Front spread / one-by-two** (buy 1, sell 2, requiring
portfolio margin): buy 1 option, sell 2 further-OTM options against it, for
a net credit (Chen/Sebastian ch.9). Unlike a butterfly, the ratio spread adds
a **third dimension — direction** — beyond skew and volatility: being right
on direction isn't strictly required, but being right on skew *and*
volatility is, and adding correct direction can make the trade "wildly
successful."

### Greeks Profile

A back spread is almost always **net long vega** at initiation (two longs
outweigh one short in vega terms, though this fades over time). A front
spread/one-by-two behaves more like a calendar spread in character —
conditions that hurt a back spread tend to favor a front spread.

### Entry Criteria

- **Volatility rule for back spreads: only enter when IV is in the lower 40%
  of its current range** — otherwise the trade needs a large directional
  move to succeed since it can't rely on IV expansion.
- **Skew**: because you sell one ATM option and buy two OTM options, flatter
  skew is better — buy the OTM curve as cheaply as possible, ideally while
  IV is also low. Target skew **7–10% underpriced**. Conversely, steep skew
  + high volatility can produce a loss even if directionally correct —
  "ignoring IV/skew here is throwing money down the drain."
- **Time**: workable in any timeframe; pick the month with the **lowest
  relative IV** (compare the ~60-day option's IV against its own historical
  60-day-IV norm). For a portfolio hedge or long-IV play, prefer **at least
  60 days to expiration**.
- **Construction target**: enter for a **net credit or at worst zero cost**
  (net premium paid for the two longs less than the value of the one short)
  — don't chase a large credit, since accepting only a small credit lets the
  two long positions "hang in" longer.
- **One-by-two/front spread**: the trade must generate a **credit**; it
  profits from the underlying moving *away* from the two short strikes
  (opposite of the back spread, which wants the underlying to move *toward*
  the long strikes).

### Management and Adjustment

Few adjustments make sense. If the trade isn't working, close it. If
conditions have turned against the position and it's losing, close it. If
conditions have genuinely improved (even while the trade is currently
losing) and capital isn't overcommitted, adding is reasonable. As a portfolio-
level adjustment tool, both variants recur throughout §2–3's condor/
butterfly adjustment tables (back ratio as a secondary upside condor
adjustment; ratio spread as the primary downside condor/butterfly
adjustment; the margin-account one-by-two as a cheap wide-tent adjustment on
both sides).

### Exit Criteria

- Same **~10%** discipline as the other structures: take the win (or lock it
  up) at ~10%; never let a loss exceed 10% of original margin (including any
  added margin from scaling up).
- On a one-by-two specifically: as the underlying moves away from the short
  strikes, skew flattens and IV compresses, and the credit-sold position
  becomes closeable at a credit too — a clear signal it's time to close.
- Worked SPX ratio back spread example (Chen/Sebastian ch.9): sold ATM 1280
  puts, bought 2x further-OTM 1230 puts with flat skew (10-delta put at only
  135% of ATM); IV rose and SPX dropped as hoped, skew also steepened
  incrementally — profitable exit the next day. Explicit conclusion:
  **direction helped but was the least important part of the trade** — skew,
  time, and volume being favorable mattered more.

---

## 7. Kite Spread (Chen/Sebastian, Appendix D)

### Construction

An adjustment technique for an existing short spread (typically an iron
condor's call side): buy a long option **below** where the existing short
spread sits, then sell **more** of the original spread (now available at a
higher credit, since it's being added further OTM/richer) against that new
long — using the added credit to pay for **at least half** of the new long
option's cost. Worked example: buy 1 call at a lower strike (e.g., 1370),
sell 2–3 additional call spreads on top of the existing spread (e.g., 3x
1390/1400 call spreads).

### Greeks Profile

Similar character to a ratio spread but with **less vega and more explosive
gamma**. Long gamma; as the underlying rallies, the position goes short
vega — behaving in many ways like a ratio spread. As time passes, the trade
becomes progressively longer gamma, continuing to hedge the underlying
position.

### Entry Criteria

Used specifically as the **primary upside adjustment for an iron condor**
under nearly all conditions except very low IV (where the back ratio spread,
§6, is preferred instead — see §2's ranked adjustment table). It is nearly
impossible to execute effectively on the **downside** of a condor, because
the mechanics rely on **vertical skew** to make the added call spreads
generate sufficient credit — this makes it primarily an upside/call-side
tool.

### Management/Adjustment

**Benefits**: long gamma that grows over time; relatively inexpensive; hedges
effectively with fairly predictable returns; adds much less incremental risk
than the disfavored alternative of rolling the spread back and increasing
size. **Detractions**: there is a "sour spot" where the trade can actually
lose money; it adds to margin requirements; it does not add a large amount
of gamma; it's nearly unusable on the downside (see above).

### Exit Criteria

Once placed, the recommendation is to **leave the kite spread on until the
entire position is unwound together** — it's cheap enough as an adjustment
to carry through to the end of the trade rather than actively trading in and
out of it.

---

## 8. Arbitrage Combinations (Bittman, Ch.6)

These four structures exploit the near-riskless relationship between real
stock and its synthetic equivalent built from options (see the six synthetic
equivalences and put-call parity equation in `directional-strategies.md`,
Bittman ch.5). All four are properly the domain of professional market
makers — they lock in tiny, structurally-guaranteed edges that retail
transaction costs generally erase, and all four share **pin risk**: uncertain
assignment when the underlying settles exactly at a strike, creating
unavoidable weekend stock-position exposure.

### The Conversion

**Construction**: long stock + long put + short call, same strike/
expiration, share-for-share — the foundational arbitrage strategy that all
the others build on. **Profitability condition**: the call's time value must
exceed the put's time value by enough to cover transaction costs, cost of
carry, and target profit. Worked example: long stock@103 + long 100 Put@4.50
+ short 100 Call@8.25 → a flat $0.75/share profit at every stock price at
expiration.

**Pricing**: modeled like a T-bill's discounted-present-value structure —
`DPV of strike = strike × [1 − (borrowing rate × days/365)]`; net investment
= DPV of strike − (transaction costs + target profit); solve
`Call = Stock − Put − NI`. A dividend reduces the required call price (it's
extra income to the position, making it more attractive to hold) via
`DPV of (strike + dividend)`. As strike price rises, the required call-minus-
put time-value gap widens (more borrowed capital, more financing cost to
recover).

**Greeks/risk profile**: economically flat/delta-neutral by construction
(the stock, put, and call legs are calibrated to converge to the same P/L at
every terminal stock price) — the residual risk is **pin risk**: if the stock
closes exactly at the strike, it's unknown how many written calls will
actually be assigned, so standard market-maker practice is to exercise half
the long puts, accepting some unavoidable weekend stock-position risk.

**Exit**: resolves automatically at expiration (stock below strike → put
exercised; above strike → call assigned; either way the position closes with
the locked-in profit) — not a position typically closed early.

### The Reverse Conversion ("the Reversal")

**Construction**: short stock + short put + long call, same strike/
expiration — the mirror image of the conversion, established for a **net
credit** invested at the risk-free rate. **Profitability condition**: interest
earned on the net credit must exceed transaction costs plus (call time value
− put time value). Worked example: short stock@102 + short 100 Put@5.25 +
long 100 Call@6.50 → flat $0.75/share profit at every stock price.

**Pricing**: opposite of the conversion's T-bill analogy — like borrowing
money (via the short-stock proceeds) to be repaid with interest when the
position closes. `DPV of strike = strike × [1 − (lending rate × days/365)]`;
net credit required = DPV of strike + costs + target profit; solve
`Call = Stock − Put − NC`. Dividends **increase** costs here (opposite of the
conversion) since the short-seller owes the dividend to the stock's lender,
which lowers the affordable call purchase price.

**Greeks/risk profile**: same pin-risk exposure as the conversion, mirrored.

**Worked market-making construction** (Bittman ch.9, Exercise 3): a reverse
conversion can be assembled purely through ordinary delta-neutral bid/ask
market-making — buy calls on the bid delta-neutral, then sell puts at the
ask delta-neutral, ending with the long-call/short-put/short-stock
combination and a net credit that beats the parity-derived target by a cent.

### Box Spreads

**Construction**: a 4-part, **options-only** arbitrage (no stock leg) — a
long call + short put at one strike, and a short call + long put at another
strike.

- **Long box** (net debit): long call + short put at the *lower* strike,
  short call + long put at the *higher* strike. Equivalent framings: long
  synthetic stock at the lower strike + short synthetic stock at the higher
  strike; or a bull call spread + a bear put spread (same two strikes).
  **Profitability condition**: (difference between strikes − cost of
  position) > cost of carry. Worked example: long 90 Call@6.50 + short 90
  Put@2.00 + short 100 Call@2.25 + long 100 Put@7.00 → flat $0.75/share
  profit at every stock price.
- **Short box** (net credit): the mirror image — short call + long put at
  the lower strike, long call + short put at the higher strike (equivalently,
  a bear call spread + a bull put spread). **Profitability condition**:
  (credit received + interest earned) > (strike spread + costs).

**Pricing**: `NI (long box) = DPV(strike spread) − (costs + target profit)`;
`NC (short box) = DPV(strike spread) + costs + target profit`; solve the
unknown leg algebraically from the other three. **Key identity**: the value
of the (debit) call spread plus the value of the (debit) put spread equals
the net investment (long box); the credit call spread plus credit put spread
equals the net credit (short box).

**Greeks/risk profile**: **double pin risk** — landing exactly on *either*
strike leaves an in-the-money option from the other strike creating an
unpredictable stock position, so the "exercise half the ATM longs"
mitigation applies at both strikes, not just one.

**Motivation for running both conversions and short boxes together**:
market makers who run books across many underlyings often carry conversions
(net debit, needing borrowed funds) and reverse conversions/short boxes (net
credit, generating lendable funds) simultaneously, internally offsetting
borrowing against lending to save the borrow-lend rate spread — bounded by
how much capital/equity is available to support the combined position size.

**Worked market-making construction** (Bittman ch.9, Exercise 4): a long box
can be assembled from two delta-neutral market-making trades — buy the lower-
strike call spread delta-neutral (one leg at the touch, the other at the
bid-ask midpoint, standard practice for a one-to-one vertical since it
carries lower Greeks than an outright option), then buy the mirror put
spread the same way — landing on a long box priced exactly at its
theoretical (parity-derived) value once the incidental stock-hedge trades'
P&L is included.

### Cross-reference: Butterfly Construction via Market Making

Bittman ch.9 (Exercise 2) also shows a **long call butterfly** (long 1 lower-
strike call, short 2 middle-strike calls, long 1 higher-strike call — the
same basic butterfly shape as §3's iron butterfly, but built entirely from
calls rather than as an iron combination) assembled through three sequential
delta-neutral market-making trades at different times/prices, arriving at a
net cost below the position's own theoretical value purely from the
incidental stock-hedge P&L — a market-maker's-eye illustration of how
Chapter 1's basic four-strike butterfly/condor shapes get built in practice,
one delta-neutral leg at a time.

---

## Completeness Check

Cross-referenced against all 26 extraction notes. Spread/combination content
located and incorporated from: Chen/Sebastian ch.9 (all five strategies:
vertical, iron condor, ATM iron butterfly, calendar/time spread, ratio back/
front spread — full construction/Greeks/entry/management/exit for each);
ch.10 (broken-wing butterfly and unbalanced condor named as variants; TOMIC
1.0's strategy cheat sheet and worked AAPL vertical spread trade); ch.11
(double diagonal worked example, weighted-vega-vs-raw-vega distinction,
low-VIX-cash tips applicable to calendars/diagonals); ch.13 (Butterfly
Trading Checklist and index butterfly wing-width guidance, both reproduced
in full; the Good Exits framework; a short-calendar case study); ch.4
(spread-type order-fill-difficulty ranking, relevant to structure choice);
ch.6 (broker's complex-order margining of iron condors); Appendix D (kite
spread, reproduced in full). From Bittman: ch.1 (basic vertical/straddle/
strangle/butterfly/condor P/L-diagram construction); ch.5 (synthetic
relationships underlying the arbitrage combinations, cross-referenced rather
than duplicated); ch.6 (conversions, reverse conversions, box spreads, in
full); ch.9 (market-maker construction of butterflies, reverse conversions,
and box spreads via delta-neutral trades; vertical-spread bid-ask quoting
convention); ch.10 (vertical-spread Greeks-reduction and Greek-sign-reversal
findings).

Two items are flagged as judgment calls on placement rather than gaps:

- **Diagonal spreads** (§5) have no dedicated chapter/section in either book —
  the double diagonal is documented as a worked example inside Chen/
  Sebastian's volatility "lessons" chapter (ch.11), and "diagonal" otherwise
  appears only as a named strategy type (Op-Eval Pro's spread screen,
  Bittman ch.2; a Level-1-trader vocabulary item, Chen/Sebastian ch.6). This
  reference synthesizes those scattered mentions into a standalone section
  per the design spec's explicit inclusion of "diagonals" in this file's
  scope, rather than omitting the topic for lack of a dedicated chapter.
- The **broken-wing butterfly** and **unbalanced iron condor** are named in
  Chen/Sebastian ch.10 as strategies in TOMIC 1.0's toolkit but never given
  their own construction walkthrough anywhere in the source text (ch.9's
  detailed treatment covers only the symmetric versions) — noted as named
  variants of §2/§3's base structures rather than given fabricated
  construction detail the books don't actually provide.
