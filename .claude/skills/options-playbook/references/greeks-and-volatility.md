# Greeks and Volatility

Synthesized from both source books' treatment of option sensitivities (the
Greeks) and volatility. Bittman (*Trading Options as a Professional*)
supplies the formal mechanics — precise definitions, worked tables, and
formulas for each Greek and for historic/implied volatility. Chen/Sebastian
(*The Option Trader's Hedge Fund*) supply a practitioner's operating layer on
top of that — the "three-dimensional volatility" model, skew-tracking
methodology, weighted vega/gamma, and gamma-scalping technique developed
from real trading-floor experience. Where the books frame the same concept
differently, both framings are given, attributed.

Primary sources: `bittman-ch03`, `bittman-ch04`, `bittman-ch07`,
`bittman-ch08`, `bittman-ch09`, `bittman-ch10`, `chen-ch04`, `chen-ch08`,
`chen-ch09`, `chen-ch11`, `chen-ch12`, `chen-ch13`, `chen-appendices`.

---

## 1. The Greeks: Definitions, Formulas, and Sign Conventions

Per Bittman, the five Greeks are each an estimate of an option's value
change given a one-unit change in one pricing input, holding all other
inputs constant. Each is a rate of change (a derivative) of option value
with respect to one variable.

### 1.1 Delta

- **Definition**: the estimated change in an option's value per one-unit
  (e.g., $1) change in the underlying's price, other factors held constant
  — the first derivative of value with respect to underlying price.
  Answers: "if the stock moves $1, how much do I make or lose?"
- **Sign**: call deltas are always positive (direct relationship with the
  underlying); put deltas are always negative (inverse relationship).
- An option's price always moves *less than* one-for-one with the
  underlying pre-expiration — delta is the ratio that captures how much
  less (Bittman ch.3). Delta increases as an option moves further ITM.
- **Rule — delta and moneyness**: ITM options always have |delta| > 0.50;
  ATM options ≈ 0.50; OTM options < 0.50, regardless of time to expiration.
- **Rule — delta and time to expiration**: |delta| of ITM options increases
  toward 1.00 as expiration nears; ATM stays near 0.50 throughout; OTM
  decreases toward 0.00 as expiration nears.
- **Rule — same-strike call/put deltas**: |call delta| + |put delta| ≈ 1.00
  always (a put-call-parity corollary).
- **Rule — delta and volatility**: rising volatility pushes |delta| *toward*
  0.50 (OTM deltas rise, ITM deltas fall), because higher volatility widens
  the standard-deviation-implied range, effectively moving a fixed strike
  "closer" to the money in standard-deviation terms. At very low volatility,
  ATM delta can jump sharply toward 1.00 (a tiny option value becomes
  highly price-correlated).
- **Position delta**: long calls and short puts have positive position
  delta (profit if underlying rises); short calls and long puts have
  negative position delta. Computed as the sum, across all legs, of
  (contracts × 100 × per-option delta).

### 1.2 Gamma

- **Definition**: the change in delta per one-unit change in the
  underlying's price — the second derivative of value with respect to
  underlying price, i.e., delta's own rate of change. Answers: "how much
  does my market exposure change when the underlying moves?"
- **Sign**: gammas are always positive for both calls and puts (delta and
  the underlying always move in the same direction, for both call and put
  deltas, even though put delta itself is negative).
- **Rule — same-strike call/put gammas are (nearly) equal** — a put-call
  parity consequence: since |call delta| + |put delta| ≈ 1.00 always, a
  rise in one's absolute delta must be offset by an equal fall in the
  other's, so their rates of change match.
- **Rule — gamma is largest ATM**, and grows as expiration approaches for
  ATM options specifically — this is why an ATM option can seem to
  "explode" in value as the underlying crosses the strike. ATM gamma stays
  small/nearly constant until about a month before expiration, then rises
  dramatically, then collapses to zero exactly at expiration (a 2-cent move
  near expiration can flip a call's delta from 0.00 to 1.00 — near-infinite
  gamma).
- **Rule — ITM/OTM gamma** rises only slightly until ~30 days before
  expiration, then decreases to zero (opposite pattern from ATM).
- **Rule — gamma and volatility**: for ITM/OTM options, gamma rises with
  volatility from roughly 10–20%, then falls as volatility rises further
  above ~30% (rising vol pushes delta toward 0.50, reducing marginal delta
  sensitivity). For ATM options, gamma is roughly flat across most
  volatility levels but spikes dramatically at very low volatility.
- **Position gamma** does not itself signal profit/loss — it signals how
  the *position's delta* will change as the underlying moves. Long calls
  and long puts have positive position gamma (delta moves favorably with
  the underlying); short calls and short puts have negative position gamma
  (delta moves unfavorably, accelerating losses as the market moves against
  the position).
- **Practical risk lesson** (Bittman's "Debra" example): a long call's
  unrealized profit from a big favorable move can be nearly erased by a
  much smaller reversal, because gamma had grown the position's delta much
  larger by the time of the reversal.

### 1.3 Vega

- **Definition**: the change in an option's value per one-percentage-point
  change in the volatility assumption, other factors constant. Answers:
  "if implied volatility moves 1 point, how much do I make or lose?"
- **Naming note**: "vega" is not an actual Greek letter (origin murky —
  theorized traders wanted a "v" word for volatility that sounded like
  delta/gamma/theta); some traders/mathematicians use kappa or lambda
  instead — no universal convention exists.
- **Sign**: vegas are always positive for both calls and puts (value is
  always positively correlated with volatility).
- **Rule — same-strike call/put vegas are equal** (another put-call-parity
  consequence).
- **Rule — vega is largest ATM** (biggest absolute dollar impact from a
  1-point IV change).
- **Rule — vegas decrease as expiration approaches**, for all moneyness
  levels, but ATM vegas stay elevated longer than ITM/OTM vegas as
  expiration nears.
- **Rule — vega and volatility level**: for ATM options, vega is roughly
  constant above ~10% volatility, so value moves close to linearly with
  volatility in that range. For ITM/OTM options, vega is near zero below
  ~10% vol, rises through ~50% vol, then flattens — the linear
  extrapolation trick that works for ATM options fails for ITM/OTM options.
- **Doubling volatility does not double option value uniformly**: an ITM
  option's value rises less than proportionally, an ATM option's value
  rises roughly proportionally, and an OTM option's value rises
  *exponentially* (Bittman's worked example: 25%→50% vol roughly doubling
  ITM value by only 24%, ATM by 90%, and OTM by 430%). Practical
  implication: pure-OTM positions carry outsized IV risk relative to
  ATM/ITM, which is one reason full-time traders holding OTM options often
  use vertical spreads to cut IV exposure.
- **Position vega**: long option positions (calls or puts) have positive
  position vega (profit if volatility rises); short option positions have
  negative position vega (profit if volatility falls).

### 1.4 Theta

- **Definition**: the change in an option's value per one-unit change in
  time to expiration, other factors constant. Theoretically instantaneous,
  so practitioners pick a practical unit — one day is most common among
  professionals; retail traders may use a week or ten days. No universally
  "right" unit.
- **Sign**: thetas are (usually) negative for a long position — an owned
  option loses value as time passes. **Exception**: deep-ITM
  *European-style* options can theoretically price below intrinsic value
  (since early exercise isn't possible), producing a positive theta as
  value rises toward intrinsic near expiration.
- **Rule — call and put thetas differ** even at the same
  strike/expiration/underlying, because calls carry an extra
  interest-rate/cost-of-carry component puts lack, so they decay to zero at
  different rates.
- **Rule — theta is largest in magnitude ATM** — ATM options carry the most
  time value at a given expiration, so they have the most to lose per unit
  of time.
- **Rule — ATM theta** shrinks in absolute terms as expiration nears, then
  collapses to zero almost immediately before expiration (theta gets
  *bigger* in magnitude right up until the very end).
- **Rule — ITM/OTM theta** behaves oppositely to ATM: it gets larger in
  magnitude for a while, then smaller as expiration nears. Because ATM vs.
  ITM/OTM patterns diverge, blanket claims that "time decay always
  accelerates near expiration" are unsafe without checking moneyness.
- **Rule — theta and volatility**: theta magnitude increases (more decay
  per day) as volatility rises, for ITM/ATM/OTM alike — a higher-volatility
  option has more time value to erode over the same remaining time.
- **Using theta with delta**: a long-option trader can combine theta and
  delta to solve for the underlying move needed, over a holding period, to
  offset time decay (e.g., theta=0.05/day, delta=0.35 → a ~$1.00 move over
  7 days offsets 7 days of decay: 0.35 × $1.00 ≈ 7 × 0.05).
- **Position theta**: short option positions have positive position theta
  (profit as time passes, decay favors the seller); long option positions
  have negative position theta.
- **Weekend decay is front-loaded, not spread evenly** (Per Chen/Sebastian,
  ch.12): a stated linear "daily theta" implicitly assumes evenly-spaced
  decay, but if Friday's close didn't already price in the coming weekend,
  arbitrageurs could sell premium right before the close and buy it back
  Monday, capturing 2.5 days of decay for one overnight's worth of real
  risk. Market makers prevent this by advancing their pricing software's
  "theoretical day" forward starting as early as Thursday midday — via
  either lowering theoretical IV or advancing the theoretical
  days-to-expiration input directly — so that by Friday's close the system
  is effectively already priced to 4 p.m. Sunday, leaving only one real
  overnight of decay still outstanding. Practical rule: don't hold a
  position over a weekend expecting "extra" decay to show up Monday — most
  retail platforms don't model this front-loading correctly, and there is
  no free weekend edge, only whatever trading edge you already have.

### 1.5 Rho

- **Definition**: the change in an option's value per one-percentage-point
  change in interest rates, other factors constant.
- **Sign**: rho is positive for calls, negative for puts — a
  put-call-parity/cost-of-carry consequence (rising rates raise the cost of
  carrying the underlying, which widens a call's time value relative to a
  put's).
- Generally the least important Greek for short-term/non-arbitrage traders
  (small absolute effect; rates rarely move sharply on short notice) but
  material to arbitrageurs.
- **Rule — rho and stock price**: rho increases in magnitude as the
  underlying price rises (financing a higher-priced stock costs more).
- **Rule — rho and time**: rho increases almost linearly as time to
  expiration lengthens.
- **Rule — rho and volatility** (most complex): volatility affects rho only
  indirectly, through option price. For OTM calls, rising volatility raises
  rho exponentially up to ~50% vol, then levels off. For ATM calls, the
  relationship is closer to linear (even slightly declining at the high
  end). For ITM calls, rising volatility actually decreases rho.
- **Position rho**: long calls and short puts have positive position rho
  (profit if rates rise); short calls and long puts have negative position
  rho. Bittman ch.10 explicitly excludes rho from position-risk-management
  calculations, since small short-term rate moves don't materially affect
  short-term option positions.

### 1.6 Position Greeks Summary Table (Bittman ch.4, Table 4-19)

| Position | Delta | Gamma | Theta | Vega | Rho |
|---|---|---|---|---|---|
| Long call | + | + | − | + | + |
| Short call | − | − | + | − | − |
| Long put | − | + | − | + | − |
| Short put | + | − | + | − | + |

No two rows are identical — each combination has a unique sensitivity
profile, and every option's actual sensitivities further depend on
moneyness (ITM/ATM/OTM). Position Greeks are computed as the sum across
every leg of (quantity × 100 × per-option Greek); understanding them (not
just single-option Greeks) is a key differentiator between disciplined and
undisciplined option traders, and is the foundation for both trade
selection and position-risk management. Sign-convention warning: "+/−" on
a *quantity* means long/short; on an *individual option's* Greek it means
positively/negatively correlated with that input; on a *position's* Greek
it means the whole book profits/loses if that input rises. Gamma is the
one exception — its sign describes delta's behavior, not profit/loss
directly.

### 1.7 Greek Interlinkage — Neutralizing More Than One at Once

Per Bittman (ch.10), the Greeks are not fully independent once a position
mixes options with a stock component:

- With **zero interest rates** (applies generally to options on futures),
  neutralizing *any one* of gamma, vega, or theta (by trading a single
  option series, plus an offsetting stock trade to preserve delta
  neutrality) automatically neutralizes the *other two* as well — a trader
  doesn't need to choose which Greek to target; they're linked.
- With **positive interest rates**, gamma and vega remain linked (the same
  option quantity neutralizes both), but theta requires a *different*
  quantity — the theta/gamma/vega link breaks once carrying costs enter.
  This interest-theta linkage only applies when the position has a
  meaningful stock component; for stock-free option combinations, theta
  is instead governed by its usual inverse relationship with gamma/vega
  (same-expiration positions with positive gamma+vega always have negative
  theta, and vice versa).
- Practical framing for a delta-neutral position with no stock component:
  since theta can't be tied to an interest calculation, the real decision
  becomes strategic — be a net option buyer (profit from a big move or
  rising IV, pay theta) or a net option seller (profit from time decay,
  risk a big move or rising IV) — then set a risk limit on vega or theta
  accordingly. Full risk-limit mechanics are covered in
  `risk-management-and-position-sizing.md`.

### 1.8 Practical Vega Application: Repricing and Quoting in Volatility Terms

Per Bittman (ch.9), two vega-based shortcuts underlie professional
bid/ask-setting (full market-making mechanics in
`market-making-techniques.md`):

- **Repricing formula**: `new theoretical value ≈ known theoretical value +
  (change in IV, in percentage points) × vega`. Lets a trader re-price an
  option for a new IV assumption without re-running the full pricing
  model.
- **Quoting in volatility terms**: the same vega-scaling logic run in
  reverse converts a dollar bid-ask spread into an implied-volatility
  bid-ask spread — the market maker's actual internal "unit" for quoting
  and comparison, since dollar prices alone are hard to compare as the
  stock price moves.
- Op-Eval Pro's **Portfolio screen** (Bittman ch.2) automates position-Greek
  aggregation across up to 15 options with differing expirations/implied
  volatilities, including "what-if" move-volatility / move-days-to-expiry
  inputs; its **Single Option Calculator** solves implied volatility
  backward from an entered market price; its **Distribution screen**
  converts price/volatility/days inputs directly into 1-SD (and
  multiple-SD) price ranges. These are reusable *concepts* (IV solving,
  position-Greek aggregation, SD-range calculation) independent of the
  specific bundled software.

---

## 2. Volatility: Definitions and Types

### 2.1 What Volatility Is

Per Bittman: **volatility = price change without regard to direction.** A
1% rise and a 1% decline are equal in volatility terms — only the magnitude
of percentage change matters, not direction, absolute dollar amount, or
price level. Two traps: (1) traders instinctively think in "good
direction/bad direction" terms, which obscures volatility's non-directional
nature; (2) a single day's move means nothing — volatility describes a
*series* of changes over time (a stock can be "calm" on average yet still
have one big-move day, and vice versa).

### 2.2 Historic Volatility

- **Definition**: the annualized standard deviation of daily returns over a
  specified observation period (30, 90 days, etc. — the period must be
  specified for comparisons to be meaningful).
- **Daily return formula**: `(closing price today − closing price
  yesterday) / closing price yesterday`.
- **Annualizing**: `daily standard deviation × √(number of trading periods
  per year)`.
- Historic volatility reflects the *frequency/magnitude* of daily
  percentage swings, not the size of the overall trend traveled — a stock
  that looks visually calm (narrow overall range) can have *higher*
  historic volatility than one that looks dramatic (big round-trip swings)
  if its daily percentage moves are consistently larger.
- Normal-distribution reference points for daily returns: 68.27% of
  outcomes within 1 SD, 95.45% within 2 SD, 99.73% within 3 SD, 99.994%
  within 4 SD, 99.99994% within 5 SD, 99.9999998% within 6 SD. A 6-SD move
  is "not impossible, just unlikely."

### 2.3 Realized Volatility

**Definition**: the volatility that *actually occurs* between today and
some future date — i.e., historic volatility computed retroactively over a
period that hasn't happened yet as of today. Also called "future
volatility" because it is unknown in advance. Per Chen/Sebastian (ch.4),
the entire options universe assumes volatility is **mean-reverting** — an
unusually fast-moving stock/index is likely to slow down, and an unusually
slow one is likely to speed up — which underlies judging whether an
option's price is cheap or rich relative to what will actually happen.
Caveat: no amount of research predicts true catastrophes (earthquakes,
terrorist attacks); relying purely on historical volatility there "can
equate to pissing in the wind" — always keep a worst-case scenario in mind.

### 2.4 Implied Volatility

- **Definition** (Bittman): the volatility percentage that, plugged into
  the pricing formula, reproduces an option's actual market price as its
  theoretical value — i.e., solving the pricing formula backward from a
  known price.
- **Analogy**: implied volatility functions like a stock's P/E ratio — a
  market-determined common denominator that lets traders compare option
  richness across different underlyings, independent of absolute price
  level.
- An option trading at relatively low IV (vs. its own history) is, all else
  equal, a relatively better purchase; one at relatively high IV is a
  relatively better sale — but "all else equal" rarely holds, so IV level
  alone can't dictate a buy/sell decision.
- **Both historic and implied volatility change together with events**, but
  the conventional wisdom that "volatility only rises when prices fall"
  does not always hold — Bittman documents a real 12-month case where IV
  rose alongside a *rising* stock price. Don't assume the standard
  inverse price/vol relationship always applies; analyze each situation.
- **Implied volatility can swing meaningfully intraday** — Bittman's
  worked example shows a ~3-point IV swing between a stock's intraday high
  and its open/close, invisible to anyone checking only two points in the
  day. Forecasting IV changes, like forecasting price, is "an art, not a
  science."
- **Per Chen/Sebastian (ch.8)**: implied volatility is *set by the market
  through price discovery* (supply and demand of customer order flow), not
  by market-maker fiat — a common misconception. Market makers only set
  the momentary quote; if they bid too high, aggressive public selling
  forces the bid (and IV) down; if they cut prices too low, public buying
  signals the level is now "oversold," and market makers raise it back.
  Practical edge: "selling when others are buying and buying when others
  are selling is the key to success" — a fund that can *initiate* trades
  (unlike a pure market maker) should look to sell into these
  supply/demand-driven overpricing moments.
- **Per Chen/Sebastian (ch.8), a further conceptual point**: implied
  volatility (like the Greeks) is an *output* of the pricing model, not an
  input a trader directly controls — a trader who isn't actively tracking
  their own volatility assumptions can't really see their true risk.
  Recommended practice: model how Greeks and P&L would move across a range
  of IV scenarios, and know the IV of every contract held.

### 2.5 Expected Volatility

**Definition** (Bittman): a loosely used term for a trader's *forecast* of
either (a) future realized volatility (relevant to delta-neutral trading)
or (b) future implied volatility (relevant to directional volatility
bets). Also called "forecast" or "predicted" volatility. Whatever number a
trader enters into a pricing calculator is, by definition, their expected
volatility for that calculation.

### 2.6 Terminology Reference Table (Bittman ch.7)

| Term | Meaning |
|---|---|
| Historic / past volatility | Stock-price action already observed |
| Option volatility / "an option's volatility" | Implied volatility |
| Future volatility | Realized volatility (not yet known) |
| Expected / forecast / predicted volatility | A trader's prediction of realized or implied volatility |
| (input to a pricing calculator) | Whatever number you enter is, by definition, expected volatility |

### 2.7 "Overvalued" and "Undervalued"

Since realized (future) volatility is unknown, an option's "true"
theoretical value is unknowable — it is only an estimate driven by whatever
expected-volatility assumption is supplied. **Overvalued** = market price >
theoretical value ⟺ implied volatility > the trader's own expected
volatility. **Undervalued** = the reverse. Implied volatility itself is
objectively computable from known inputs plus market price; theoretical
value is inherently subjective (depends on the trader's own forecast) — so
"overvalued/undervalued" is a subjective judgment, not an objective fact.
Two traders can agree on IV and still disagree on over/undervaluation if
their own volatility forecasts differ. Bittman recommends spending effort
refining the three-part forecast (price, time, implied-volatility level)
rather than chasing the overvalued/undervalued framing directly.

---

## 3. Annualization and Time-Period Conversions

- **Formula**: `standard deviation for a period = annual volatility × √(days
  in period / days per year)`.
- Worked example (Bittman): stock=$78.50, annual vol=35% → 1-year SD=27.47;
  4-week (28-day) SD=7.61 (implied 68%-confidence range $70.89–$86.11);
  1-week SD=3.77; 1-day SD=1.41.
- Practical use: comparing options of different expirations by their
  implied SD-ranges, or choosing strikes at a target number of standard
  deviations from the current price.
- **Calendar days vs. trading days**: whether the formula uses 365 or ~252
  days/year usually doesn't matter much, except over very short periods.
  A 2-month period showed only a 15¢ difference between calendar-day and
  trading-day SD estimates (immaterial); a 3-day period showed a ~17%
  difference (potentially material for very short-dated strategies). Most
  traders default to calendar days since "days to expiration" is readily
  available from brokers.
- **Using volatility to pick strikes**: a common technique is selling an
  option at least 1 SD away from the current price, reasoning it has
  roughly a 68% chance of expiring worthless. Caveat: a statistical edge
  over many trades doesn't guarantee any single outcome — the option can
  still move ITM intraday/intraweek and force a stop-loss even where it
  would eventually have expired worthless.
- **Average True Range (ATR)** (Per Chen/Sebastian, ch.9, citing Welles
  Wilder's *New Concepts in Technical Trading Systems*): a distinct,
  price-action-based volatility measure used to sanity-check
  IV — typically a 14-day moving average of "true range," where **true
  range** = the greatest of (a) current high minus current low, (b)
  absolute value of the most recent period's high minus the previous
  close, (c) absolute value of the most recent period's low minus the
  previous close. Iron condor entry logic is framed as "IV relative to
  ATR"; iron butterfly entry logic is framed as "current ATR relative to
  expected future ATR," combined with a relatively high IV level.

---

## 4. Volatility Skew

### 4.1 Per Bittman: Definition, Cause, and Effect on Buyers

- **Definition**: same-underlying, same-expiration options at *different
  strikes* trading at *different* implied volatilities — common in
  index/futures options, less common in individual equity options.
- Worked real example (XSP Mini-SPX): ATM IV = 20.83%; IV *rises* moving
  away from ATM in both directions (e.g., a strike 2 points OTM at 21.75%,
  strikes far OTM/ITM around 24–26%). The skew curve is not symmetric
  around the ATM strike and not perfectly linear (a "smile"/"smirk"
  shape).
- **Why skews exist**: no rigorous theoretical justification exists.
  Bittman's practical explanation ties to the insurance analogy (strike ≈
  deductible): demand for "cheap protection" (low-absolute-premium,
  far-OTM options) can push up the *implied volatility* of those options
  even without moving their absolute dollar price much, because sellers of
  cheap, high-leverage protection demand a higher risk premium per unit.
- **Skew structurally disadvantages naive OTM option buyers**: as a
  purchased OTM option approaches the money, its IV tends to compress
  toward the (lower) ATM level even if the underlying's directional
  forecast is exactly right — meaning realized profit can come in well
  below what a naive fixed-IV projection would suggest. Changes in the
  overall IV level or in the skew's shape can offset or worsen this
  either way, so skew must be tracked alongside the overall IV level, not
  in isolation.

### 4.2 Per Chen/Sebastian: Three-Dimensional Volatility Model

Chen/Sebastian frame volatility as inherently **three-dimensional**, not a
single number: (1) near-term ATM level, (2) skew, (3) term structure. All
three must be read together.

**ATM options**: front-month ATM options are almost always the most
actively traded, and their trading activity sets the overall volatility
structure for the whole product — analogized to a boat's sail. Movements
in front-month ATM IV propagate to OTM puts, OTM calls, and the entire term
structure. Front-month options don't carry the *most* vega (that belongs to
longer-dated options) but are far more sensitive to *changes* in implied
volatility — a property the authors call **"vomma."** Watching front-month
ATM options is the single best indicator of where IV is headed across the
whole product.

**Skew** (also called "kurtosis" in the text): how different strikes'
implied volatilities relate to one another within a contract series. The
typical equity/index pattern is an **"investment skew"**: OTM puts trade at
higher IV than ATM, OTM calls at lower IV (exceptions: deal stocks, FDA
stocks, VIX options). **Root cause per Chen/Sebastian — a structural,
hedging-flow explanation, distinct from Bittman's insurance/demand-for-cheap-protection
framing**: the market is structurally full of "natural longs" (401(k)s,
mutual funds, and most individual accounts are long stock; shorting in a
personal account requires extra paperwork/margin). The natural hedge for
this structural long bias is buying puts and selling calls — widespread
simultaneous demand for that exact hedge bids up put IV and depresses call
IV. **Per Chen/Sebastian, ch.4, this is elaborated as a collar mechanism**:
equity/IRA/401(k)/pension hedgers routinely collar their positions (buy
downside puts, sell upside calls to help finance them), which structurally
makes puts relatively expensive and calls relatively cheap versus ATM —
visible in SPX's volatility surface. This dynamic isn't constant; the skew
curve moves as hedging flow shifts, and its steepness affects which trades
are relatively favorable.

**Using skew**: a flat (undistorted) skew is called out as possibly the
single biggest determinant of a butterfly's success, and also favors
back-spread and front-spread trades; on simpler trades it can just mean
selectively choosing to sell OTM put or call *spreads*. A named
edge-capture technique: buy an oversold option / sell an overbought option
within a credit spread to squeeze an extra $0.02–$0.10 of edge per spread —
scaled to a fund trading 500 contracts/month, up to $5,000/month.
Recommended monitoring: for single names, examine the full strike-by-strike
curve before every trade; for index traders, track a few OTM puts/calls by
*delta* (preferred over %-OTM) and their IV ratio to ATM IV over time (a
10-delta put at 30% IV vs. 20% ATM IV = "150% of ATM" — track that ratio
itself), and note that dedicated curve-mapping software "pay[s] for
themselves" for active index credit-spread traders.

**Term structure**: different contract months see different order flow
("paper"), and liquidity thins further out, so a large order can move one
month's pricing substantially relative to others. Monitoring the
*relationship* between expiries (not just overall volatility level) opens
opportunities, especially for calendar spreads. Trading rule: if the
near-term month is underpriced, in theory buy near-term/sell longer-term
(a long calendar) — but retail traders are explicitly warned this specific
setup is often a loser in practice, since a genuinely (not just apparently)
underpriced near month usually stays that way. When the near month is
*overpriced*, sell near-term and buy back months (a reverse/short
calendar). The same monitoring approach extends to iron condors,
butterflies, and strangles — when one month's IV becomes overbought
relative to others, shift the trade into that month or avoid trading a
mispriced one. Watch for earnings, FDA announcements, corporate actions,
and dividends before assuming an unusual month-to-month spread is a "free"
mispricing to exploit — "if a swap seems too good to be true, it probably
is," but legitimate month-vs.-month mispricings, once vetted, offer better
odds than the pricing model alone would suggest.

**Practical monitoring checklist** (per underlying traded): ATM IV, skew,
and three-month term structure. **Per position held**: the IV of every
contract owned, the Greeks of the entire position, expected Greeks (how
they'll evolve), and P&L under a 5%, 10%, and 25% IV decline or increase.
Named skew/term-structure tracking tools: **ivolatility.com** and
**livevolpro.com** (Chen/Sebastian, ch.6/ch.11).

### 4.3 Finding, Tracking, and Interpreting Skew — Trading-Floor Lessons

Per Chen/Sebastian (ch.11), practical skew methodology:

- **Tracking set**: log the IV of a fixed set of specific-delta options
  daily — the 5-delta put, 20-delta put, 50-delta call (ATM), 25-delta
  call, and 10-delta call give a fairly accurate skew-curve
  representation. Graph the raw IVs to see the curve's shape; graph the
  *differences* between them to see how the curve's shape is changing over
  time.
- **Month-rolling rule**: switch to charting the next month out around 15
  days to expiration; stop using a month once the calendar rolls to the
  first of that month. Record exactly when you switch months to avoid
  discontinuities in the tracked series.
- **Skew is relative, not absolute**: skew is a *percentage* of ATM IV, so
  the ATM IV level matters as much as the skew percentage itself. A high
  skew percentage on a low ATM-IV base can represent *less* absolute
  richness than a lower skew percentage on a high ATM-IV base. Worked
  comparison of two 15-delta SPX iron condors: Trade 1 (steep skew, low
  19% ATM IV, below its own 23% median) computes to a 26.6% put / 17.1%
  call absolute IV; Trade 2 (normal skew, high 25% ATM IV, above its own
  23% median) computes to a richer 33.75% put / 21.25% call absolute IV
  despite the *lower* skew percentage — because its elevated ATM IV base
  dominates. General rule: the lower the ATM IV level, the more you need
  skew to compensate for it; the higher ATM IV is, the less skew itself
  matters for finding edge — though the single best setup is high skew
  *and* high ATM IV together.
- **"All credits are not created equal" in iron condors**: getting an
  identical nominal credit for a strike that sits *closer* to the money
  (because volatility/skew has compressed since a comparable earlier
  trade) is a worse trade, even though the premium collected looks
  identical — worked example showed two $0.60 10-delta put-spread credits
  placed ~15 points apart in absolute OTM distance for the same nominal
  premium. Skew and IV level effectively "pull in the wings" of a
  condor over time; unlike a butterfly (where richer wings can mitigate
  risk), this dynamic makes an iron condor *more* vulnerable to a
  subsequent IV spike.
- **Butterfly-specific skew rules** (per Chen/Sebastian, ch.9/ch.13): skew
  is called the single most important factor for an iron butterfly's
  success — more so than for a condor — because a fly is essentially a
  short straddle plus a long protective strangle, and the price of that
  strangle (a function of skew) sets the trade's edge. Equity-fly put-skew
  rule of thumb: a put trading at a >6% discount to its "normal" skew
  level is a favorable entry; a 10% discount is excellent; a flat put skew
  implies a likely-profitable short. The rule of thumb: "you want a flat
  put curve and a steep call curve," and the cheaper the long call leg,
  the better (a cheap long call behaves as expected — losing little — if
  the underlying rallies and IV falls). As part of the butterfly entry
  screen, also check the butterfly's own IV level directly (favor entries
  with IV between the 25th and 75th percentile of its 90-day mean —
  avoiding both "sky-high" IV, which risks a snapback rally, and IV too
  low, which risks an IV pop) and intra-month skew specifically (high
  intra-month skew makes a butterfly expensive to insure; low intra-month
  skew makes it cheap). Full butterfly construction and the complete
  entry/adjustment/exit checklist are in `spreads-and-combinations.md`.

### 4.4 The Five Phases of Volatility Skew (Chen/Sebastian, ch.11)

A behavioral framework for how skew moves through a full calm-to-crisis-to-calm
cycle, illustrated via VIX/SPX skew behavior:

1. **Phase 1 — Calm**: IV low (VIX roughly 16–18%), skew normal-to-flattish;
   ordinary market moves, little fear of a major event.
2. **Phase 2 — Calm Before the Storm**: IV still relatively low
   (roughly 15–20 VIX) but developing fear starts building, or IV is
   "oversold" with pent-up hedging demand; the market begins buying
   protection but avoids ATM options, so unit-put buying pushes up skew
   without moving ATM IV much yet. Reversible — can go back to Phase 1 or
   forward to Phase 3.
3. **Phase 3 — The Typhoon**: extreme fear (VIX 30–40%+); downside IV
   stays high but ATM IV rises so much it catches up, so **skew actually
   flattens** — "borderline panic."
4. **Phase 4 — The Calming Storm**: IV still high but falling; ATM IV is
   being sold off while many sellers of ATM vol simultaneously buy OTM
   puts — so tail/unit protection is at its *most expensive* in this
   phase (ATM IV elevated and skew steep together). VIX roughly 20–35%.
   Reversible — can relapse to Phase 3 or progress to Phase 5.
5. **Phase 5**: broadly "all is well," IV normalizes, but skew stays
   slightly elevated for a period as the market "licks its wounds" —
   distinguished from Phase 1 mainly by residual steeper skew. Can take up
   to 6 months to fully resolve back to genuine calm. Can transition back
   to Phase 1 or Phase 2.

Behavioral point underlying the whole framework: as IV comes down from a
spike, the market tends to keep bidding up cheap OTM puts for an extended
period, out of residual fear IV could reverse higher rather than continue
toward its mean — which is why skew normalization typically lags ATM IV
normalization.

### 4.5 Practical Tips When the Term Structure Is Distorted (Chen/Sebastian, ch.11)

When VIX futures trade well above VIX cash (a wide term-structure spread,
front month cheap relative to back month):

1. Avoid long term-risk plays (calendars, double diagonals) in that
   environment; if entering one anyway, overlay extra back-month IV
   exposure or buy cheap front-month strangles as a hedge.
2. Don't fear trading the front month outright (e.g., butterflies), as
   long as wing width is set via a standard-deviation calculation off the
   ATM strike's IV (e.g., assume an 18.5-day holding period, size wings
   from that period's implied SD) — this automatically widens wings in
   high-IV months and tightens them in low-IV months.
3. Don't fear a condor if the back month is still elevated relative to the
   front — selling the relatively higher-IV month has historically worked
   in comparable term-structure setups.
4. Buy cheap tail protection ("units") while it's available — tail
   protection becomes unaffordable exactly when it's needed most.

### 4.6 Weighted Vega Application to Skew Trades (Chen/Sebastian, ch.11)

A **double diagonal** (sell front-month OTM call and put, buy back-month
OTM further out) is described as an underutilized way to trade an elevated
front-month "smile" without the capital outlay of a full strangle. Worked
OEX example: a spread's *raw* (unweighted) vega looked "pretty flat" at
about 82, but after weighting the vega (see §5), the position was actually
**short about 170 weighted vega** — a materially different risk picture.
This example is the clearest illustration in either book that raw and
weighted vega can disagree sharply in both sign and magnitude.

---

## 5. Weighted Vega and Weighted Gamma

This concept was first introduced by Chen/Sebastian in the Calendar Spread
section of ch.9 ("Most Used Strategies"), given a skew-trading application
in ch.11, and given its full mechanical grounding in ch.14. All three
should be read together.

### 5.1 Why Weighting Is Needed at All

Per Chen/Sebastian: different expiration months (for vega) and different
underlyings/products (for delta and gamma) do not carry equivalent risk
per unit of the raw Greek — a "1 vega" or "1 gamma" number means different
things depending on context, so raw Greeks must be *weighted* before they
can be meaningfully compared or netted across a book.

- **Vega across time (ch.9/ch.11 framing)**: different expiration months
  carry different vega *and* different sensitivities to changes in
  realized/implied volatility. Front-month IV is far more "frenetic"
  (volatile) than back-month IV, because front-month price movement has a
  more permanent, delta-moving effect (it's driven largely by gamma),
  while back-month options have much more time to expiration and so react
  less to the same daily move — the **"vega neutralizer"** effect: a
  calendar spread is technically long *raw* vega, but front-month IV
  movement can neutralize or overwhelm whatever the back-month IV does.
  During a volatility spike, floor practice pushes front-month IV up
  faster/further than back-month IV (since back-month options have more
  time to "relax"); during a calm-down, front-month IV gets killed
  faster than back-month IV. This term-structure/weighted-vega dynamic
  matters not just for calendars but also for double diagonals,
  butterflies, and condors.
- **Delta/gamma across products (ch.14 framing)**: delta represents
  sensitivity to a 1-*point* move in the underlying, but a "1-point" move
  means very different things in percentage terms across products/prices.
  Worked pairs-trade example: short 100 shares IBM (~$146.52) vs. long 100
  shares Ford (~$16.75) on a "Ford will outperform IBM" thesis. Ford
  rallies 5%, IBM rallies 2% (the directional call is *correct*) — yet the
  trade **loses money overall**, because share-count-based sizing ignored
  the huge price-level/dollar-exposure mismatch (Ford return
  +$83.75 vs. IBM return −$293.04). Correct sizing (~9 shares of Ford per 1
  share of IBM) would have made the intended bet actually profitable
  (+$460). The same logic applies across index products: a 1-point move in
  SPX (~0.08%) is economically negligible while a $1 move in SPY (~0.8%)
  is meaningful — selling 1,000 SPY 30-delta calls is roughly
  risk-equivalent to selling only 100 SPX calls, a ~10:1 ratio driven
  purely by index-level difference. Understanding each product's absolute
  underlying "size" is essential to building a genuinely balanced
  cross-product portfolio — "in trading, size does matter."
- **Vega and theta are comparatively easy to cross-hedge without
  weighting** (ch.14): both are tied to the *dollar amount of premium* in
  a contract, not to any property of the specific underlying — $3,000 of
  premium with 30 days to decay decays to zero in 30 days regardless of
  whether it was sold in SPY or SPX (though a different number of
  contracts is needed to reach that $3,000 in each product); a 1-point IV
  move in either product produces the same dollar loss for the same
  dollar vega exposure. Summary lines from the text: "theta is theta,
  regardless of what product it is sold in" and "vega is vega, regardless
  of the product."

### 5.2 The Gamma-Weighting Mechanism in Full

Per Chen/Sebastian (ch.14): gamma itself isn't what needs weighting — the
*price movement* of the underlying is what needs weighting, and gamma
naturally follows once that's done correctly. Worked comparison: SPY drops
$3 (126→123, a ~2.5% move) — the 126-strike delta might fall from 50 to
30–40 (≈15-delta change, implying gamma ≈ 5). SPX drops the same $3
(1260→1257, only a ~0.25% move) — the 1260-strike delta might fall only
from 50 to 48.5 (≈1.5-delta change, implying gamma ≈ 0.3). The same
absolute point move produces very different delta/gamma effects purely
because of the difference in *percentage* move. Reconciling: SPX (at ~10x
SPY's level) would need to move roughly $30 to be percentage-equivalent to
SPY's $3 move; rechecking at that scale, SPY's `3 × 5 = 15` deltas and
SPX's `30 × 0.5 = 15` deltas now match. Conclusion, quoted directly: "the
gamma isn't weighted because the price movement of the underlying products
is!" — it is the percentage-equivalent point move that must be scaled
across products, not gamma as a standalone number. Named floor conversion
ratios used for this purpose (approximate, product-specific): roughly 2.23
OEX per 1 SPX, roughly 11 DIA per 1 [comparable unit], roughly a little
under 10 SPY per 1 [comparable unit].

### 5.3 Gamma and Implied Volatility for OTM Options (Chen/Sebastian, ch.14)

A separate but related lesson on how gamma itself responds to *changes* in
IV for options away from the money: OTM gamma can both increase and
decrease as IV rises, depending on the size of the IV move — it is not
monotonic. For options well OTM (below ~15 delta), a *moderate* IV increase
generally *increases* gamma (a condor shows more delta sensitivity on a
downturn early in an IV spike than the standalone Greeks would suggest at
the original IV level). A worked MNX-condor illustration: raising IV by 5%
made the position shorter gamma (the intuitive direction); raising IV
further, by 15%, made gamma *fall* (the counter-intuitive part).
Mechanism: as IV rises, an OTM option first behaves progressively more
like an ATM option (gaining gamma, since ATM options carry the most
gamma), but once IV has risen enough that the option is effectively
ATM-like, further IV increases start reducing its gamma, following the
normal ATM gamma-vs-IV relationship. Simplified rule: "way-out-of-the-money
options gain gamma with increases in volatility, until they are no longer
way-out-of-the-money options."

---

## 6. Delta-Neutral Trading: Long and Short Volatility (Bittman Ch.8)

Delta-neutral trading is a **non-directional** technique — it profits, loses, or breaks even based on the relationship between **implied volatility and realized volatility**, not on which way the underlying moves. It is the speculative counterpart to the market-maker use of delta-neutral hedging covered in `market-making-techniques.md` §2; this section covers the volatility-forecasting use case.

**Definition and construction**: a delta-neutral position is any combination of long/short stock, calls, and puts whose net delta is zero or near-zero (position delta = Σ over all legs of contracts × 100 × per-option delta). Two or more legs; the classic two-part forms are long calls + short stock, short calls + long stock, long puts + long stock, and short puts + short stock.

**The three-step process**: (1) establish a delta-neutral position; (2) as the underlying moves and gamma pulls net delta away from zero, make **adjusting stock trades** (buy or sell just enough stock to return delta to ~zero) on a predetermined schedule — time-based (e.g., once daily) or move-based (e.g., every $2 move, or every 1-SD move per §2 above); (3) close the whole position.

**Long volatility** (positive vega — options are owned) vs. **short volatility** (negative vega — options are written): both are illustrated in Bittman's worked multi-day examples with a hypothetical trader ("Tom") buying or selling calls delta-neutral and adjusting daily.

**The core theoretical result — breakeven when IV = realized volatility**: when a delta-neutral position is held and implied volatility stays constant and equals the volatility the underlying actually realizes over the holding period, the P&L from the option leg (time decay, working for or against the position depending on long/short) is *exactly offset* by the P&L from the adjusting stock trades — regardless of the specific path the stock took to get there. This holds symmetrically for both long-volatility positions (theta loss offset by stock-trading profit) and short-volatility positions (theta profit offset by stock-trading loss).

**Reality diverges from theory in two ways, and this is where the profit/loss actually comes from**:
- **Long volatility profits when realized volatility exceeds implied volatility** — the bigger the underlying's actual, frequent swings relative to the IV baked into the options at entry, the bigger the profit from the adjusting stock trades outrunning the option's time decay. (Worked example: a position showing $8,540 profit when the underlying's realized behavior implied ~94% volatility against options priced at 35% IV.)
- **Long volatility loses when implied volatility itself falls**, even if the directional/delta component of the trade is working correctly — a sharp IV decline can turn an otherwise-profitable move into a net loss, since the vega loss from falling IV can outweigh the delta gain from a favorable price move. This makes exit timing a genuine forecast about *where IV is headed*, not just where price is headed.
- Short-volatility positions face the mirror-image risks (below).

**Speculative risk profile**:
- **Long volatility — limited but substantial risk**: a pure IV decline (holding price fixed) costs `vega × (IV point-drop) × contracts × 100`, before any additional theta loss; maximum loss is capped at the full premium paid (options expire worthless if the underlying settles exactly at the strike).
- **Short volatility — unlimited risk**, from two separate sources: (1) rising IV, uncapped as IV keeps climbing; (2) a sudden large underlying move/gap (e.g., an overnight earnings surprise) — a "delta-neutral" position is only protected against *small* moves; a large enough gap can produce a large loss on both legs simultaneously despite having started perfectly hedged. **Delta-neutral is risk-reduced, not risk-free.**
- What counts as "high" or "low" volatility for judging whether to run a long- or short-volatility book is instrument-specific and requires the historic/implied-volatility context from §2 above.

**Market-maker use is different in kind, not just degree**: per `market-making-techniques.md` §2, a market maker's delta-neutral hedge is a defensive, no-forecast-implied step in a bid/ask-capture trade meant to last minutes to hours — not a volatility bet held for days to weeks like the speculative use described here.

---

## 7. Gamma Scalping

Per Chen/Sebastian (ch.14): the author, as a former market maker, had far
more hedging flexibility than most retail traders (any instrument, any
month, calls hedged with puts, etc.). The stated conclusion is that it
doesn't matter *what* instrument is used to hedge — it matters *how* the
hedging is done. Two methods, for two trader profiles:

### 6.1 "Pay the Decay" (for very active/full-time traders)

- **Concept**: use the position's theta to compute the daily underlying
  move (the "nut") required to offset that day's time decay, via the
  standard gamma/theta relationship.
- **Formula**: `7/5 × Theta = 0.5 × Gamma × X²`, solved for X (the required
  underlying move): `X = SQRT(2.8 × Theta / Gamma)`. The 7/5 factor
  partially accounts for weekend decay (see §1.4's weekend-decay lesson).
- Worked example: a straddle long 8.25 gamma, short 6.09 theta →
  `X = SQRT(2.8 × 6.09 / 8.25) ≈ $1.44` required move that day to offset
  decay. This must be recomputed every morning, since both gamma and
  theta grow as expiration approaches.
- **Two acknowledged problems with the raw formula**: it requires a fresh
  daily calculation (impractical alongside a full-time job), and it only
  gives the breakeven move size — it does not say *when* to actually
  scalp.
- **Actual practiced scalping rules**: don't wait for the full calculated
  move (that threshold is hit only about once every 3 days); instead set
  scalp trigger points at **50% of the required move**, sell all deltas
  there, and buy them back when the underlying returns to unchanged
  (typically producing two scalps, repeated roughly twice per day); zero
  out all deltas at end of day regardless; if the underlying gaps past the
  required move outright, sell all (or at least 75%, if momentum looks
  likely to continue) of the position's deltas immediately; if a scalp
  trigger is hit and the underlying keeps running, use the scalp point
  itself as the new reference for the next calculation (a trailing
  approach) — though in a clearly trending move, the author admits to
  letting the position run with trailing stops rather than mechanically
  scalping. Rationale for scalping at tighter (50%) intervals rather than
  waiting for the full theoretical move: "volatility predicts price
  movement, not direction" — smaller, more frequent scalps capture more of
  the realized movement than waiting for one large theoretical move that
  may not materialize exactly as calculated.

### 6.2 Delta/Gamma Ratio Hedging (for less active traders)

- **Method**: hedge based on a delta/gamma ratio, most commonly **1:1**
  for typical stocks — flatten deltas once accumulated delta equals gamma.
  For smaller positions or momentum-prone stocks, use a larger ratio (to
  account for commissions, or to intentionally let the position run with
  momentum).
- **Implementation**: each morning, determine the underlying price level
  at which delta would equal gamma on the upside and set a price alert (or
  rest a small order) there; do the same on the downside.
- **Execution rule when using options (not stock) to scalp**: always use
  front-month options to hedge, regardless of which month the underlying
  straddle sits in, since front-month options carry the "purest" deltas
  (least vega contamination). For larger positions, deep-ITM calls/puts
  can substitute for stock; for positions too small to justify a stock
  hedge, diagonals in front-month OTM options can be used instead
  (explicitly described as "not a very desirable way to manage deltas,"
  used only when position size forces it).
- **Case-study outcome**: a managed (hedged) position ended up making
  slightly less than an unhedged naked straddle would have, but with
  materially lower P&L volatility and a shallower maximum drawdown.
- **Overall caution**: gamma scalping is "really not for most retail
  traders" absent a strong grasp of the mechanics and a clear reason for
  wanting long-premium exposure in the underlying in the first place.
  Benefits when done properly: reduces P&L volatility, and reduces the
  "pain" of theta decay — which in turn allows staying in a position
  longer while a broader thesis plays out.

---

## 8. Where the Two Books Differ

| Topic | Per Bittman | Per Chen/Sebastian |
|---|---|---|
| Volatility's core structure | A single number (historic/implied/expected) plus a separate skew overlay | Inherently **three-dimensional**: ATM level, skew, and term structure must always be read together |
| Cause of skew | No firm theoretical basis; practical explanation via demand for cheap OTM "insurance" (insurance-deductible analogy) | Structural hedging-flow explanation: the market's natural long bias drives systematic put-buying/call-selling (collaring), which is *the* main driver of investment skew |
| What sets implied volatility | Presented mainly as a market-consensus forecast, analogous to a P/E ratio | Explicitly framed as the output of real-time price discovery driven by customer order flow — market makers merely react to it, they don't set it |
| Vega/gamma across a book | Single-underlying focus; Greeks presented per position without a cross-product/cross-expiration weighting layer | Explicit **weighted vega** (across expirations) and **weighted gamma/delta** (across underlyings of different price levels) — raw Greeks can mislead without this weighting |
| Gamma-scalping / hedging technique | Not covered as a named technique (delta-neutral adjustment trades are covered generally in ch.8, but without the "Pay the Decay" formula or delta/gamma ratio method) | Two fully worked retail-feasible methods ("Pay the Decay" and delta/gamma ratio hedging), from real floor practice |

Both books agree on the fundamentals: the definitions and sign conventions
of the five Greeks, the mean-reverting nature of volatility, the existence
and persistence of skew as a tradeable market feature, and the general
principle that a naive OTM option buyer is structurally disadvantaged by
skew.

---

## Cross-references

- Full market-making bid/ask mechanics that build on vega-repricing and
  IV-quoting: `market-making-techniques.md`.
- Position-Greek risk limits, neutralizing a book's Greeks, and sizing
  formulas for adjustment trades: `risk-management-and-position-sizing.md`.
- Full strategy construction, entry/adjustment/exit rules for verticals,
  iron condors, butterflies, calendars, ratio spreads, and the kite spread
  (including the complete Butterfly Trading Checklist referenced in §4.3):
  `spreads-and-combinations.md`.
- Synthetic equivalences and put-call parity (the basis for many
  same-strike call/put Greek-equality rules above): covered in
  `directional-strategies.md` and `income-strategies.md`.
- Trade-selection criteria that incorporate volatility/skew evaluation as
  one of several screens: `trading-business-framework.md`.
