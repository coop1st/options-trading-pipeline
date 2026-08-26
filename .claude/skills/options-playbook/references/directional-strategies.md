# Directional Strategies

The directional-exposure toolkit: taking a straight bullish or bearish view
using a single option (an outright long call or put) or a synthetic
position built from stock plus options. This is the simplest layer of the
options playbook — one leg or a two-leg synthetic, no spread construction —
and it's almost entirely Bittman-sourced (Chs. 1, 3, 5), with
Chen/Sebastian's Trade Selection framework (Ch.2) supplying the criteria
for *when* a directional trade is the right call versus a non-directional
premium-selling structure.

Related reference docs: `greeks-and-volatility.md` (delta/gamma/theta/vega
mechanics referenced throughout this file), `spreads-and-combinations.md`
(vertical spreads and other multi-leg structures — including the
directional vertical spreads Chen/Sebastian build on top of this toolkit),
`risk-management-and-position-sizing.md` (position-Greek risk limits and
stop-loss discipline for directional positions), `income-strategies.md`
(the covered-call/short-put synthetic equivalence used for income rather
than directional speculation).

## 1. Outright Long Call

**Construction**: buy a call at a chosen strike/expiration. Right (not
obligation) to buy the underlying at the strike until expiration.

**P&L profile** (Bittman Ch.1, Figs. 1-1): unlimited profit potential as
the underlying rises; risk limited to the premium paid; breakeven = strike
+ premium paid. Example: 100 Call bought at 4.00 → max risk 4.00 (100% of
premium if it expires worthless), breakeven 104, unlimited upside above
that.

**Pricing behavior that governs how this P&L unfolds before expiration**
(Bittman Ch.3):

- Calls have a **direct** relationship with the underlying price: value
  rises as the underlying rises, falls as it falls — but always **less
  than one-for-one** pre-expiration. The ratio is delta, and it is never
  exactly 1.00 until expiration (a slight time premium always remains).
  Delta rises as the option moves further ITM, and moves further from 0.50
  as it does — see `greeks-and-volatility.md` for the full delta/gamma
  mechanics.
- **Strike price** acts like a deductible: a higher strike (further OTM)
  lowers the call's value and delta, holding the underlying constant.
- **Time decay (theta)** is *not* uniform by moneyness. ATM calls decay
  slowly at first, then sharply in the final ~30 days. OTM calls decay
  more like a straight line across time, with the *least* decay in the
  final week — the opposite pattern from ATM. Deep ITM calls only have
  their (small) time-value portion decay; the intrinsic-value floor holds.
  Higher volatility shifts more of an OTM call's decay into the second
  half of its life. Practical corollary Bittman draws for premium sellers
  (relevant when evaluating whether to buy or sell time value in a
  directional trade): options 5–10% OTM decay disproportionately early, so
  selling 2-month OTM options and covering 1 month out can capture more
  time premium than rolling 1-month options.
- **Interest rates**: call values rise with rising rates (small effect for
  short-term speculative trades, material for arbitrage pricing — see
  `market-making-techniques.md`).
- **Dividends**: opposite of interest rates — rising dividends lower call
  value. Call and put values are equal when dividend yield = interest
  rate.
- **Volatility**: higher volatility raises call value. ATM call value
  moves roughly *linearly* with volatility; OTM call value moves
  *non-linearly* (small at low vol, then rises steeply) — doubling
  volatility from 25%→50% raises an ATM call's value by roughly 90% but an
  OTM call's value by 400%+ (per the worked figures in
  `greeks-and-volatility.md`). At extreme volatility, a call's value
  approaches its theoretical ceiling: the underlying's price itself (no
  rational buyer pays more for a call than for the stock outright).
- **Three-part forecast**: because price, time, and volatility all move
  together, a long call is not just a bet on direction — it's a bet on
  direction *and* the pace of the move *and* where implied volatility ends
  up. Bittman's worked "Joe/Jumpco" example (100 Call analog) shows the
  same directionally-correct forecast (+10% stock move) producing outcomes
  ranging from **+320%** (fast move, IV unchanged) to **+150%** (same move,
  IV reverts to a lower "normal" level) to an outright **−40% loss** (a
  smaller +5% move combined with IV compression) — despite the trader
  being right about direction in every scenario. The lesson: evaluate a
  long call (or put) across multiple price/time/volatility scenarios, not
  a single point forecast.

## 2. Outright Long Put

**Construction**: buy a put at a chosen strike/expiration. Right to sell
the underlying at the strike until expiration.

**P&L profile** (Bittman Ch.1, Figs. 1-3): risk limited to premium paid;
large profit potential as the underlying falls toward zero; breakeven =
strike − premium paid. Example: 100 Put bought at 3.00 → max risk 3.00,
breakeven 97.

**Pricing behavior** (Bittman Ch.3) mirrors the long call, inverted:

- Put values move **inversely** with the underlying (rise as it falls,
  fall as it rises), also always less than one-for-one pre-expiration.
- A higher strike raises put value (a put's "deductible" logic runs the
  opposite direction from a call's).
- Time decay follows the same ATM-vs-OTM-vs-ITM asymmetry described above
  for calls (moneyness drives the decay pattern, not option type).
- Interest rates: put values **fall** as rates rise (mirror of calls,
  again a put-call-parity consequence — see Section 4).
- Dividends: put values **rise** as dividends rise (mirror of calls).
- Volatility: raises put value, same linear-ATM/non-linear-OTM pattern as
  calls. At extreme volatility, a put's value ceiling is the strike price
  itself (the underlying can't go below zero).
- Same three-part (price/time/volatility) forecasting discipline applies.

**The insurance framing** (Bittman Ch.3's "Insurance Analogy," also
Chen/Sebastian's TOMIC framework in `trading-business-framework.md`): a
put is insurance against a real loss on an owned/anticipated asset; a call
is insurance against an "opportunity loss" — missing a rally while holding
cash. The insurance-premium components (asset value, deductible, term,
interest, risk) map directly onto the six option-value components
(underlying price, strike, time, interest rate, dividends, volatility).

## 3. Short Call and Short Put (for completeness)

Bittman Ch.1 presents these as the mirror images of the long positions in
the basic four-building-block P/L set:

- **Short call**: profit limited to premium received, **unlimited** risk
  above breakeven (strike + premium received).
- **Short put**: profit limited to premium received, substantial (but
  bounded at zero) risk below breakeven (strike − premium received).

These are directional-exposure tools too (a short put is a bullish trade,
a short call bearish), but their risk profile — particularly the
uncovered short call's unlimited risk — puts their sizing and risk-limit
treatment in `risk-management-and-position-sizing.md` rather than here.
Note also the direct synthetic equivalence used for income generation:
short put ≡ long stock + short call (Section 4 below), covered from the
income angle in `income-strategies.md`.

## 4. Synthetic Directional Positions (Bittman Ch.5)

**Put-call parity** means any one of the six real directional positions
(long/short stock, long/short call, long/short put) can be built
("synthesized") from a two-part combination of the other two instruments,
at the same strike/expiration. A synthetic position has the **same
theoretical risk, breakeven, and profit potential** as the real position
it replicates — but costs two bid-ask spreads/commissions instead of one
and carries different margin treatment, which is why trading synthetics
(as opposed to just understanding the equivalence) is mostly a
professional/market-maker activity.

**The six equivalences**, each verified in the source at every stock price
and at expiration via exercise/assignment mechanics converging to the same
"effective price":

| Synthetic position | Built from |
|---|---|
| Synthetic long stock | Long call + short put (same strike/expiration) |
| Synthetic short stock | Short call + long put |
| Synthetic long call | Long stock + long put (same strike as the put) |
| Synthetic short call | Short stock + short put |
| Synthetic long put | Short stock + long call |
| Synthetic short put | Long stock + short call |

**Put-call parity equation** (0% interest, no dividends baseline):

```
Stock = Call − Put        (long stock = long call + short put)
```

Five algebraic variants (convention: `+` = long, `−` = short):

| # | Equation | Meaning |
|---|---|---|
| 1 | Stock = Call − Put | Long stock = long call + short put |
| 2 | Stock + Put = Call | Long call = long stock + long put |
| 3 | Put = Call − Stock | Long put = long call + short stock |
| 4 | Put − Call = −Stock | Short stock = long put + short call |
| 5 | −Call = −Stock − Put | Short call = short stock + short put |
| 6 | −Call + Stock = −Put | Short put = long stock + short call |

**Effective stock price concept**: a call's price *increases* the
effective stock price implied by a synthetic (an exercised/assigned call
implies buying/selling at strike + call price); a put's price *decreases*
it (strike − put price). With 0% interest and no dividends: `synthetic
stock price = strike + call price − put price`.

**Why the equivalence holds regardless of moneyness**: the six
equivalences are true no matter where the stock price sits relative to the
strike at entry — verified in the source at stock above, below, and at the
strike.

**Equal time premiums (zero-rate baseline)**: with 0% interest and no
dividends, the time value of a call equals the time value of a put at the
same strike/expiration, regardless of moneyness — a direct consequence of
put-call parity.

**Real-world interest rates and dividends break this equality** — this is
the part of the synthetic-relationships material most directly relevant to
*choosing* between a real directional position and a synthetic one:

- With interest rates > 0 and no dividends, a synthetic long stock
  position (long call + short put, net-zero cost) is preferred over real
  stock, because it leaves capital free to earn interest for the same P&L.
- With 0% rates and dividends paid, real stock is preferred (captures the
  dividend; the synthetic has no equivalent).
- With both rates > 0 and dividends paid, whichever effect is larger
  determines the theoretically preferred structure.
- Because rational investors arbitrage away any such advantage,
  **real-world call prices are bid up and put prices are bid down**
  relative to the zero-interest baseline: the call's time value exceeds
  the put's time value by approximately the interest earned on the strike
  price over the option's life. (Worked checks in the source: a 0.38
  time-value gap against a 0.41 interest estimate; a 0.79 gap against a
  0.84 estimate — close given rounding/model technicalities.)
- **Practical implication**: theoretically there's no advantage between
  real and synthetic stock once prices adjust to reflect this rule, but
  transaction costs and bid-ask spreads keep most non-professional traders
  in real stock rather than trading the synthetic. Professional
  market-makers are the ones who actually trade these relationships
  (arbitrage strategies built on them — conversions, reverse conversions,
  box spreads — are covered in `market-making-techniques.md` /
  `spreads-and-combinations.md`, sourced from Bittman Ch.6).

**Practical use of synthetics for a directional trader**: the main
reason a non-market-maker would care about this section (rather than just
buying a call or put outright) is (a) understanding that a "long call"
position is economically the same risk as "long stock + long put," which
clarifies what a protective put actually is (synthetic long call), and (b)
the short-put-as-covered-call equivalence used for income generation
rather than pure direction (`income-strategies.md`).

## 5. Choosing a Directional Trade — Chen/Sebastian's Trade-Selection Criteria

Chen/Sebastian's "Trade Selection" chapter (Ch.2) frames trade selection
as the underwriting function of the TOMIC (One Man Insurance Company)
business, and its market/direction/time-frame/volatility/pricing criteria
apply directly to deciding *whether* and *how* to put on a directional
trade (long call, long put, or a directional synthetic) rather than a
non-directional premium-selling structure.

**Five trade-selection decisions** (per Chen/Sebastian): which market(s)
to trade; the best available strategy for that market; the trade's
duration; the impact of volatility on the trade; the price at which to
enter.

**Market selection**: liquidity determines whether a directional options
trade is even practical. Rules of thumb given: index options — check open
interest (SPX has the deepest liquidity among indexes and "should be on
top of your list"); ETF options — open interest > 500 per strike, plus
adequate underlying volume; equity options — daily volume > 50,000
contracts to be considered liquid. A directional trade in an illiquid
name/strike will suffer from wide bid-ask spreads that erode the P&L edge
described in Section 1–2 above.

**Direction** (Ch.2's "Strategy Selection" section, one of its five
strategy-selection questions — "What is the direction?"): three
possibilities — up, down, sideways. Chen/Sebastian note that **having a
directional view matters for strategy choice, but a trader can still
profit without being 100% right on direction** (true of non-directional
premium-selling strategies covered in `income-strategies.md` and
`spreads-and-combinations.md`, in contrast to the outright long
call/put/synthetic positions in this file, which require being
directionally correct — or at least not badly wrong — to profit, per the
Joe/Jumpco example above). Traders are told to use technical analysis,
fundamental analysis, or a blend — "study both and use what is most
comfortable for you." No specific directional-analysis method is
prescribed beyond that.

**Time frame**: matters for a directional trade because the same
directional forecast realized over a longer holding period produces a
smaller option-price gain (per Bittman's three-part-forecast finding
above) — Chen/Sebastian's insurance-policy-duration analogy applies
equally to a long call/put's expiration choice.

**Volatility**: Chen/Sebastian's Florida-vs.-Cayman-Islands insurance
analogy (higher-hit-frequency risk should command a higher premium)
applies to a directional trade's entry price — buying a long call/put when
implied volatility is elevated relative to the underlying's actual risk
raises the bar the directional move must clear to profit (directly
consistent with Bittman's Joe/Jumpco scenario, where IV reverting to a
lower level erased most of a correct directional call's gain). Relevant
volatility measures per Chen/Sebastian: the underlying's own volatility,
the volatility curve (skew across strikes), and the term structure
(volatility across expirations) — full treatment in
`greeks-and-volatility.md`.

**Risk/reward and pricing**: Chen/Sebastian frame the final trade-selection
factor as pricing — a mispriced option (skew or term-structure edge) can
turn an otherwise-average directional setup into a favorable one, or vice
versa. "Risk/reward defines your edge," and occasional **asymmetric**
risk/reward opportunities (disproportionate reward for the risk taken) are
explicitly called out as the kind of edge trade selection should be
hunting for — a long call or put's capped-risk/uncapped-reward profile
(Section 1–2 above) is itself a naturally asymmetric structure, which is
part of why outright long options remain a viable directional tool despite
their well-documented time-decay and volatility-compression risks.

## 6. Managing a Directional Position

Bittman Ch.10 ("Managing Position Risk") gives explicit guidance for
directional positions as a distinct risk-management category (fuller
treatment, including delta-neutral and stock-hedged positions, in
`risk-management-and-position-sizing.md`):

- **For directional positions, the dominant risk is delta** — "how much
  delta can I take on?" is the first question. This is answered via
  individually-chosen **stop-loss points** (expressed in dollar amount,
  option price, or underlying price) set *below* the theoretical max loss,
  since few traders want to risk 100% of a long option's premium.
- A losing **short**-option directional position (Section 3) is
  especially dangerous because its negative gamma makes losses accelerate
  as the market moves further against it — stop-losses are more critical
  for short-option directional trades than for long ones (whose maximum
  loss is capped at the premium paid).
- Attempting to *also* manage gamma/vega/theta on a directional trade
  usually just perturbs delta further and undermines the trade's purpose
  — e.g., selling a higher-strike call to cut vega risk on an existing
  long call also cuts the position's delta, the very exposure the trade
  was meant to preserve. Directional risk management should stay centered
  on delta first, treating other-Greek adjustments as secondary.
- **Active delta management as a profit technique**: because stock prices
  tend to move choppily rather than in a straight line, and long options
  carry positive gamma (delta rises as price rises in the trader's favor),
  a trader can sell part of a long-call position when a rally pushes
  delta above a threshold and buy back when a pullback drops delta below a
  lower threshold — keeping position delta centered around a target and
  capturing extra profit from the underlying's natural oscillation.
  Bittman's worked example ("Grace," 20 long calls) shows this approach
  producing $12,625 in profit versus $10,900 from naive buy-and-hold over
  the same overall price path — a $1,725 improvement — but this
  outperformance depends on genuine price choppiness; it underperforms
  buy-and-hold when the underlying trends smoothly, and it is not
  risk-free (a sharp adverse move right after entry would force buying
  more calls into a losing position under the same delta-target rule).
- **Vertical spreads as a lower-Greek alternative to outright directional
  options**: Bittman's direct comparison (20 long 70 Calls vs. the
  equivalent 70-75 bull call spread, same underlying/time/vol
  assumptions) shows every Greek reduced by adding the short higher-strike
  leg — position delta 1,070→546, gamma 118→20, vega 174→42, theta
  −620→−170. A 2-scenario comparison shows the spread can actually
  **outperform** the outright long call specifically when implied
  volatility falls during the trade (the spread's short leg partially
  offsets the long leg's vega exposure) — e.g., the same price/time move
  produced a 1.29 profit for the outright call but only 1.03 if IV also
  fell 7 points, versus the spread's 1.12 and 1.25 respectively (the
  spread *gained* under falling IV in this example). This is the practical
  bridge between the pure directional tools in this file and the spread
  constructions in `spreads-and-combinations.md`: a trader with a
  directional view but expecting flat-to-falling implied volatility has an
  incentive to prefer a vertical spread over an outright long option.
  Important caveat from the same chapter: a vertical spread's own Greeks
  are not stable over the life of the trade — as the underlying moves from
  near the long strike toward the short strike, the spread's gamma, vega,
  and theta can flip sign entirely (bullish-and-long-volatility near the
  long strike, bullish-but-time-decay-now-helps near the short strike)
  even while delta stays directionally the same.

## Summary

The directional toolkit is the simplest layer in the playbook: an outright
long call or put gives capped risk / open-ended reward on a straight
directional view, priced and decaying according to the six-component
option-value model (Bittman Ch.3) and requiring a three-part
price/time/volatility forecast rather than direction alone. Every real
directional position (long/short stock, long/short call, long/short put)
has a synthetic two-instrument equivalent (Bittman Ch.5, put-call parity),
theoretically interchangeable but practically distinguished by transaction
costs, margin treatment, and (once real-world interest rates and dividends
are in play) a systematic call/put pricing skew. Chen/Sebastian's
Trade-Selection framework (Ch.2) supplies the criteria — market liquidity,
directional view, time frame, volatility level, and pricing/risk-reward —
for deciding when a directional trade (versus a non-directional
premium-selling structure) is the right call, while Bittman's Ch.10
position-risk chapter supplies the day-to-day management discipline:
directional positions should be managed primarily through delta and
stop-losses, with vertical spreads available as a reduced-Greek
alternative when the directional view is paired with an expectation of
falling implied volatility.
