# Market-Making Techniques

Bittman's *Trading Options as a Professional* is written substantially from
the market maker's chair, and its Chapter 9 ("Setting Bid-Ask Prices") plus
Chapter 2 (the Op-Eval Pro software chapter) are the primary sources here.
Chen/Sebastian's *The Option Trader's Hedge Fund* approaches the same
market-making machinery from the opposite side of the trade — as a retail/
TOMIC trader trying to get good fills *against* market makers — and adds
genuinely new material: how market makers actually move prices in response
to order flow, payment-for-order-flow mechanics, and specific execution
tactics for beating algorithmic quoting. Both angles are included below,
each attributed to its source.

## 1. Market Structure Fundamentals (Per Bittman, Ch.1)

Before market-making technique makes sense, the underlying market mechanics
need to be clear:

- **Bid**: the highest price a buyer currently offers to pay, with a **size**
  (quantity available at that price). **Ask/offer**: the lowest price a
  seller currently offers to sell at. A "market" is quoted as
  "bid-ask, bid-size by ask-size" (e.g., "2.20-2.30, 40 by 20").
- **Public trader**: not an exchange member/broker-dealer; subject to
  standard margin requirements; can post/withdraw quotes freely.
- **Market maker**: an exchange member and SEC-registered broker-dealer,
  **obligated** to maintain two-sided quotes within maximum spreads and
  minimum size (under normal market conditions, varying by exchange/class).
  This obligation exists to guarantee liquidity for public traders, and in
  exchange market makers receive lower margin requirements than public
  traders.
- **National Best Bid and Best Offer (NBBO)**: with multiple exchanges and
  market makers quoting the same option simultaneously, the NBBO aggregates
  the single best bid and single best ask across all venues (summing size at
  that best price across venues). SEC rules prohibit executing trades outside
  the NBBO — if a trader's own exchange isn't at the NBBO price, the order is
  either filled by a local market maker improving its quote, or routed/split
  to whichever exchange(s) actually hold the NBBO.
- **Short stock rebate**: when stock is shorted, the sale proceeds are held
  as escrow collateral and invested in T-bills/cash-like instruments; the
  interest earned is split between the stock lender and the party who
  facilitated the short. Public traders do not share in this interest, but
  **professional traders and broker-dealers — including market makers — do**
  (typically ~80% to the market maker, ~20% to the stock lender). This
  interest feeds directly into arbitrage pricing (conversions, reverse
  conversions, box spreads — see `spreads-and-combinations.md`), since it
  changes the effective cost/benefit of carrying a short-stock hedge.

## 2. The Core Market-Making Technique: Buy the Bid, Sell the Ask, Stay Delta-Neutral (Per Bittman, Ch.8–9)

The foundational market-maker technique has three parts: **buy on the bid
(or sell at the ask), immediately hedge to delta-neutral with the
underlying, then later close both legs** — capturing the option's bid-ask
spread while staying insulated from directional risk.

- **Worked example** (Bittman Ch.9, "Alex," Tables 9-1/9-2): sell 10 55 Calls
  at the 1.85 ask (delta 0.40) and buy 400 shares to hedge. Whether the stock
  subsequently rallies $1 or falls $1, closing both legs an hour later nets
  the **same $42 profit either way** — because the option's 5¢ bid-ask
  spread was wider than the stock's 2¢ spread, leaving a net edge regardless
  of direction.
- **Why it works regardless of direction**: buying options on the bid /
  selling at the ask while staying delta-hedged captures the *option's*
  bid-ask spread net of the *stock's* bid-ask spread given up on the hedge.
  Real-world complications: transaction costs must be budgeted even though
  small per-trade; the ratio of the stock's spread to the option's spread
  matters (if the stock spread is too wide relative to the option spread,
  the edge disappears and wider option quotes are required); and because
  prices constantly move, market makers need a fast way to track/re-quote as
  conditions change (delta alone doesn't capture gamma/vega effects — see
  §5 below).
- **Framed from the market maker's own perspective** (Bittman Ch.8,
  "Trading Delta-Neutral — Opportunities and Risks for Market Makers,"
  p.275–277): for a market maker, delta-neutral is **not** a volatility
  forecast (contrast speculative delta-neutral trading, covered in
  `greeks-and-volatility.md`) but "step one" of a two-step, bid/ask-capture
  process meant to last minutes to hours, not days or weeks. Step 1: get
  filled at the bid or ask and immediately hedge to delta-neutral (this
  hedge trade is the defensive, no-forecast-implied piece). Step 2: unwind
  both the option and the stock hedge, ideally at a net profit. Market
  makers additionally try to stay **volatility-neutral**: while IV looks
  stable or rising they'll sit on the resulting position hoping another
  counterparty crosses the other side of the market; if IV looks like it's
  starting to fall, they'll hedge that vega exposure by trading another
  option rather than just holding. Their *practical* risk is much lower
  than a speculator's holding the same theoretical position, purely because
  their holding periods are so much shorter — less time for an adverse IV
  move or a price gap to materialize.

## 3. How Market Makers Actually Move Prices — Price Discovery from Order Flow (Per Chen/Sebastian, Ch.8)

Chen/Sebastian explicitly debunk a common misconception and describe the
mechanism from the trader's vantage point, complementing Bittman's
theoretical treatment:

- **Myth**: market makers set option prices/volatility arbitrarily (in some
  "boiler room"). **Reality**: market makers only ever set the *momentary*
  market; the actual price is set through **price discovery** — supply and
  demand — not market-maker fiat.
- **The mechanism** (Table 8.1 in the source): if market makers bid too
  high, the public sells to them aggressively, forcing market makers to
  either absorb a lot of inventory or lower the bid — lowering the bid (and
  thus IV) is how they manage inventory as a side effect of order flow, not
  a top-down decision. If market makers overcorrect and cut the bid/offer
  too low, the public starts buying the now-cheap options, signaling to
  market makers that volatility is "oversold," at which point they raise
  the bid back. In other words: **market makers merely take the other side
  of public order flow; that flow, and the resulting price discovery, is
  the true determinant of implied volatility**, not the market maker's own
  judgment.
- **Trading implication**: because IV moves are order-flow-driven rather
  than model-driven, a trader who can identify when the public has pushed a
  price to an obviously overbought or oversold extreme (the source's
  example reaches a hypothetical "26% implied volatility" oversold level
  before reversing) can profitably take the other side — "selling when
  others are buying and buying when others are selling."

## 4. Adjusting Bid and Ask Prices (Per Bittman, Ch.9)

- **The need to adjust**: implied volatility itself can shift beyond what
  delta/gamma alone predict (see `greeks-and-volatility.md`'s intraday-IV-swing
  discussion), so market makers manage risk two ways: **setting risk limits**
  (e.g., a maximum of 100 contracts long/short) and **scaling into/out of
  positions**.
- **The process — scaling** (Table 9-3, "Anna"): sell (or buy) in increments
  at successively worse prices for the counterparty (better for the market
  maker) as a position grows — e.g., selling 20 contracts, then 20 more at a
  higher price, then 20 more higher still, up to a preset max, hedging delta
  after each tranche. Worked example: three successive 20-lot sales at a
  rising offer (4.60→4.62→4.64), closed out in one 60-lot buy-back at 4.56
  bid, nets a $288 profit even though the incidental stock hedging alone
  lost $72 — the rising-quote discipline is what produced the edge. Scaling
  serves two purposes: it improves the market maker's average execution
  price as a position grows, and the raised offer can itself attract sellers
  back into the market (or a lowered bid attract buyers). There is no
  "scientifically right" increment size (10 vs. 20 vs. 25 contracts) or
  price-adjustment size (1 tick vs. 2 ticks) — these are experience-based
  judgment calls.
- **The limit on adjusting**: how many times can a quote be walked before an
  immediate round-trip close (open then close the whole position at the
  current opposite side) merely breaks even? **Formula**:
  `number of adjustments before breakeven = (2 × bid-ask spread − increment) / increment`.
  Worked check: a 5¢ spread with a 1¢ increment allows 9 successive
  1-lot raises before a 10th would put an immediate close into loss
  territory — `(2×5−1)/1 = 9`, confirmed by the fact that after 9 raises the
  average sale price exactly equals the *current* bid. This gives market
  makers a hard, calculable cap on how far a quote can be walked before
  scaling stops being profitable if closed out immediately.

## 5. Pricing Options in Volatility Terms (Per Bittman, Ch.9)

Two related skills, both built on vega, are described as essential because
trading decisions must be made in seconds and dollar prices alone are hard
to compare as the underlying moves:

- **Re-pricing for a new IV assumption without re-running the full model**:
  `new theoretical value ≈ known theoretical value + (Δ implied volatility in percentage points) × vega`.
  Example: an 80 Call theoretically worth 4.00 at 30% vol with vega 0.10, at
  +1 point of IV (31%), reprices to 4.00 + 0.10 = **4.10**.
- **Expressing a dollar bid-ask spread as an implied-volatility spread**
  (the reverse operation, using the same vega scaling): this becomes the
  market maker's actual internal "unit" for quoting and comparison. Example:
  an 80 Call (theo 4.00 at 30% vol, vega 0.10) quoted 3.90 bid / 4.10 ask is
  exactly 1 vega below/above theo on each side, so it's quoted internally as
  **29% bid / 31% ask**.
- These two conversions — price↔IV via vega, in both directions — are the
  foundation for the position-management and risk-management techniques in
  `risk-management-and-position-sizing.md` (Bittman Ch.10).

## 6. Building Multi-Leg Positions via Market-Making Trades: The Four Trading Exercises (Per Bittman, Ch.9)

Bittman's Chapter 9 walks a hypothetical trader ("Ross") through four
exercises, each demonstrating that market makers can be indifferent to
*which* specific options they're filled on, as long as every fill is
properly hedged and priced. (Full strategy construction/risk-profile detail
for the resulting combinations — butterflies, reverse conversions, box
spreads — lives in `spreads-and-combinations.md`; this section captures the
market-making *technique* used to assemble them.)

1. **Buying calls delta-neutral**: buy 10 calls on the bid, hedge short
   stock; when the stock later moves and the quote is adjusted (both to
   potentially scale in at a better price and to entice counterparties),
   close both legs. Net profit ($96 in the worked example) comes from the
   combination of the option and stock legs, not either alone — the same
   dynamic as §2 above, but demonstrated with a genuinely moving stock price
   and IV-denominated quoting instead of a static example.
2. **Creating a butterfly spread in three separate delta-neutral trades**:
   sell the middle strike, buy the lower strike, buy the higher strike — at
   three different times and stock prices, each individually hedged to
   delta-neutral, adjusting the IV quote up after a sale (to seek more
   sellers) or down after a purchase (to seek more buyers). In the worked
   example, the three incidental stock hedges happened to net a $750 profit,
   pulling the assembled butterfly's net cost 8¢ below its own theoretical
   value — market-making mechanics, not a directional bet, built the
   position at a structural discount.
3. **Creating a reverse conversion in two trades**: buy calls delta-neutral,
   then sell puts delta-neutral, accumulating a long-call/short-put/short-stock
   position. The achieved net credit (79.61) beat the required target
   (79.60, computed via the conversion-pricing method from
   `spreads-and-combinations.md`) by a penny — confirming the position was
   assembled profitably purely through the mechanics of hitting bids and
   lifting offers while staying hedged.
4. **Creating a long box spread in two trades**: buy one vertical call
   spread delta-neutral, then buy the corresponding vertical put spread
   delta-neutral. **Vertical-spread quoting convention**: because a vertical
   spread carries lower delta/gamma/vega/theta (in absolute value) than a
   single option, it's standard practice to trade one leg at the touch
   (bid or ask) and the other leg at the bid-ask **midpoint** — an accepted
   shortcut since the spread doesn't need as wide a two-sided market as an
   outright option. The example's achieved cost matched the box's
   theoretical value exactly, confirming a correctly and profitably priced
   box spread.

## 7. Managing Time Decay Across Weekends: Advancing the "Theoretical Date" (Per Chen/Sebastian, Ch.12)

A market-making technique described from the trader-facing-market-makers
side, explaining why "free" weekend theta decay doesn't actually exist to
capture:

- **The problem it prevents**: if option prices didn't already account for
  the weekend by Friday's close, arbitrageurs could sell large premium right
  before the close and buy it back Monday morning, capturing 2.5 days of
  decay (Friday 4pm to Monday 9:30am) for the cost of only one real overnight
  of elapsed risk.
- **The mechanism**: market makers begin decaying the *entire* weekend into
  prices as early as possible — often starting Thursday midday — by
  advancing their quoting software's "theoretical day" forward artificially.
  Two levers accomplish this: (1) **lowering the theoretical implied
  volatility** used for pricing, or (2) **advancing the theoretical date**
  directly (manipulating days-to-expiration rather than IV) — one of the
  rare cases where the days-to-expiration input to a pricing model matters
  as much as volatility itself. By Friday's close, a market maker's system
  is typically already set to 4pm Sunday, leaving only one genuine overnight
  (Sunday 4pm–Monday 9:30am) of real decay still priced in.
- **Net effect**: there is no "free" weekend premium left for anyone to
  capture by Friday's close — retail platforms that assume linear daily
  theta decay (ignoring the weekend front-loading) will overstate the decay
  still available going into a weekend. (The retail-trader-facing version of
  this lesson — don't hold into a weekend expecting extra decay — is in
  `risk-management-and-position-sizing.md`.)

## 8. Analytical Concepts Behind Market-Maker Pricing Software (Per Bittman, Ch.2 — Concepts, Not Software Instructions)

Bittman Chapter 2 documents a specific bundled tool (Op-Eval Pro, long
obsolete as software) rather than reusable trading concepts per se. The
software mechanics themselves are **not** reproduced here since they're
irrelevant without the program; what's captured is the underlying analytical
concepts a market maker (or anyone pricing options) needs, which any modern
pricing tool must still provide:

- **Calculating implied volatility [Concept]**: entering a known *market
  price* into a pricing formula and solving backward for the volatility %
  that would produce that price. This is the inverse of the normal
  direction (volatility → price) and is the core operation behind §5's
  price↔IV conversions.
- **Theoretical pricing and choice of model [Concept]**: American-style
  (early exercise permitted) options require a binomial/discrete-time model;
  European-style (no early exercise) options can use a closed-form model
  (e.g., Black-Scholes). Equity underlyings need discrete, dated dividend
  inputs; index underlyings are typically modeled with a continuous dividend
  yield (an industry-standard simplification). These modeling choices affect
  the theoretical values a market maker quotes against.
- **Multi-leg position Greeks aggregation [Concept]**: summing/aggregating
  delta, gamma, vega, and theta across multiple legs (options and/or
  underlying) sharing the same or different underlying prices/volatilities —
  the basis for the position-Greek techniques in `risk-management-and-position-sizing.md`.
- **Sensitivity ("what-if") analysis [Concept]**: recalculating value and
  Greeks under a hypothetical price move or a hypothetical passage of time,
  without needing to build a new position from scratch — directly useful for
  judging how a quote should move (§4 above) before the market actually gets
  there.
- **One-standard-deviation price-range estimation from implied volatility
  [Concept]**: given an underlying price, a volatility %, and a time period,
  computing the market-implied 1-SD price range for that period. Directly
  useful for selecting strikes to quote and for judging how far a quote
  should be adjusted (§4) relative to a "normal" expected move.
- **Software-only, not reproduced**: CD installation instructions, specific
  screen navigation, print/save mechanics, and other UI-level operating
  instructions — these have no reusable value once the specific program is
  gone.

## 9. Execution Mechanics: Getting Filled Against Market Makers (Per Chen/Sebastian, Ch.4)

Chen/Sebastian describe modern market-making from the perspective of a
trader trying to get a good fill against it — this is squarely
market-making-relevant even though the audience is the counterparty rather
than the market maker:

- **Order routing and "smart routers"**: brokers' smart routers route based
  on where the *broker* makes the most money, not necessarily where the
  *trader* gets the best fill. Manually routing to a specific exchange can
  produce meaningfully better fills. General guidance: route first to the
  exchange holding the best bid/offer; **never route to a maker-taker
  exchange unless hitting a bid or lifting an offer**, since market makers
  strongly dislike paying to fill orders they're hit on and it materially
  affects fill price. Named best-fill exchanges (per the source): CBOE and
  ISE, followed by PHLX, NYSE-ARCA, and AMEX.
- **How complex orders get priced**: historically, human market makers
  priced multi-leg orders leg-by-leg on the floor and were often willing to
  improve pricing on spreads (a spread order is partially self-hedged).
  Today, complex orders are mostly priced by **algorithms**, and market
  makers must be careful how much edge they concede on any given order type
  — firms like Timber Hill and Citadel are described as constantly probing
  exchange quoting algorithms for exploitable weaknesses ("much like
  computer hackers") and aggressively picking off a weak quoting algorithm
  in size when found. Consequence: simpler trades (single options) fill more
  easily and at relatively better prices than spreads, almost always — but
  legging into a spread introduces directional risk in the meantime.
- **Relative ease of getting a complex order filled**, hardest to easiest
  per the source: nontraditional spreads, iron condors, double diagonals,
  straddles, strangles, butterflies, vertical spreads, calendar spreads,
  single option trades. A small trade with unusual strikes can occasionally
  land in a spot an algorithm is specifically tuned to execute, so
  nontraditional spreads sometimes fill surprisingly well.
- **Order size effects**: orders under 10 contracts fill more easily than
  larger ones, since most quoting algorithms are tuned to just signal an
  order's existence to the market maker rather than automatically trade a
  large spread, unless the firm has a large edge or a very tight quoting
  system.
- **"Working an order"**: a platform's quoted "midprice" is not necessarily
  the true midpoint — resting customer orders ("book orders") can distort
  the quoted bid-ask spread and the implied IV calculated from it.
  Computer-generated quotes can also simply be wrong (e.g., a bad IV input
  feeding the quoting algorithm). Establishing the *true* midpoint yourself
  and trying to do better than the displayed price is worthwhile — analogous
  to how professional market makers train for roughly a year before being
  trusted to quote independently.
- **Vega-based minimum acceptable price**: if willing to sell a spread down
  to a target IV from its current quoted IV, multiply the IV gap (in
  percentage points) by the spread's net vega to get the dollar price
  flexibility available, and refuse to sell below that floor. Worked
  example: sell-side IV of 21% pricing at $2.00, willing to go to 20% IV,
  net vega 0.05 → 0.05 × 1 = $0.05 of flexibility → won't sell below **$1.95**.

## 10. Payment for Order Flow (Per Chen/Sebastian, Ch.13)

- **Origin and mechanics**: in 2001, a market-making firm pioneered payment
  for order flow to attract volume to the exchange pits where it held
  Specialist/DPM (Designated Primary Market-Maker) status. Exchanges now
  often package this as a "marketing fee"; brokers use various other names.
  It has since become integrated at the exchange level, not just an
  individual-firm arrangement, creating a hierarchy where firms willing to
  pay for order-flow visibility get preferential treatment on large orders.
  The source's own assessment: the practice is bad for the customer, bad for
  the liquidity provider, and good for the online broker.
- **Three order-routing scenarios** (using a firm paying for order flow as
  the running example): (1) the firm is matching NBBO and the order hits
  NBBO → routes to the firm's pit, minimal impact on the trader since NBBO
  is received regardless; (2) the firm isn't the best bid/offer but still
  gets "first look" → the order routes via linkage to whichever exchange
  actually holds the NBBO, introducing a brief window (the linkage routing
  delay) during which the market can move against a large order, though many
  payment-for-order-flow firms carry a "matching guarantee" against this;
  (3) the firm is matching NBBO but the incoming order doesn't itself hit
  NBBO → the order still routes to the paying firm regardless, landing in
  the pit with the fewest eyes on it rather than the exchange with the
  deepest liquidity — described as "the real culprit" of the practice.
- **Worked illustration**: a deeper, more visible exchange (ISE, willing to
  buy up to 5,000 contracts at $0.50) is passed over in favor of a much
  thinner venue (PHLX, willing to buy only 30 contracts at the same $0.50)
  purely because the broker receives payment for order flow from the
  thinner venue — "the only thing smart about a smart router is that it is
  smart for your broker to make the most money."

## 11. Competitive Dynamics Among Market Makers (Per Bittman, Ch.6 — Cross-Reference)

Briefly, since the full arbitrage-pricing mechanics live in
`spreads-and-combinations.md`: market makers price conversions, reverse
conversions, and box spreads against a target profit derived from
interest-rate/dividend/carry math, but **competition can force acceptance
of a sub-target profit** if a rival market maker is willing to quote
tighter — described as part of "the art" of market making, alongside
comparing opportunities across strikes and underlyings for the best
available edge at any given moment.

## 12. Why This Matters for Non-Market-Makers (Per Bittman's Epilogue)

Bittman's closing framing, worth carrying forward explicitly: market makers
are a distinct kind of market participant — not competing directional
speculators, and only one participant among many, not "the market" itself —
who take on and are compensated for genuine risk just like any other trader.
For an individual (non-market-maker) trader, the value of understanding how
market makers think and operate is to sharpen order-entry judgment (knowing
why a fill happened the way it did, what a resting quote actually represents)
and strategy-performance judgment (recognizing when a quoted spread reflects
real risk versus routing/order-flow artifacts covered in §§9–10). Computers
assist market makers with execution, pricing, and risk monitoring, but do
not replace the human judgment behind quoting, scaling, and risk-limit
decisions described throughout this document.
