# Glossary

Alphabetical index of every defined term and named formula extracted from
both source books. Each entry gives a one-line definition and points to the
source chapter(s) where the fuller treatment lives — cite these as
`bittman-chNN` / `chen-chNN` extraction notes under `docs/extraction-notes/`,
or the eventual sibling `references/*.md` topic file once written.

---

### A

- **Absolute Maximum Loss** — a hard, never-exceed loss ceiling (Chen/Sebastian suggest setting it at the value of credit received on a spread); distinct from the softer "maximum loss" exit target. *See Chen/Sebastian ch.9.*
- **Account Equity (formula)** — `Account equity = Account value − Margin debt`; the capital actually at risk in a margin account. *See Bittman ch.1.*
- **American-style exercise** — an option that can be exercised any time up to expiration; priced with a binomial model since early exercise must be modeled. *See Bittman ch.2.*
- **Annualized Yield (formula)** — correct compounding formula for turning a per-trade/period yield into an annual rate: `(1 + yield)^(365.25 / days) − 1`; naively dividing by days and multiplying by 365 is the common error it corrects. *See Chen/Sebastian ch.7.*
- **Arbitrage** — buying in one market and selling in another (here, real stock vs. its synthetic option-built equivalent) to lock in a nearly riskless profit net of costs. *See Bittman ch.6.*
- **Ask (Offer)** — the lowest price a seller currently offers to sell at. *See Bittman ch.1.*
- **Assignment** — the (probabilistic, OCC-driven) process that selects a specific short-option holder to fulfill the contract obligation when a counterparty exercises. *See Bittman ch.1.*
- **ATM (At-the-Money)** — an option whose strike equals (or, colloquially, sits closest to) the current underlying price. *See Bittman ch.1.*
- **Average True Range (ATR)** — a moving average (typically 14-day) of "true range," used as a volatility yardstick when judging whether option IV is rich versus how much the underlying actually moves. *See Chen/Sebastian ch.9 (Endnote 1).*

### B

- **Back Ratio Spread** — buy 2, sell 1 (e.g., 2 OTM longs vs. 1 ATM short); adds a directional dimension beyond skew/volatility; the retail-accessible ratio-spread variant without portfolio margin. *See Chen/Sebastian ch.9.*
- **Bear Call Spread** — a short call vertical spread (sell lower strike, buy higher strike call); net credit, limited risk/profit. *See Bittman ch.1.*
- **Bear Put Spread** — a debit put vertical spread expressing a bearish view. *See Chen/Sebastian ch.9; Bittman ch.6 (box spread component).*
- **Beta Weighting (of Greeks)** — scaling delta and gamma across different underlyings by their relative price level/percentage-move sensitivity so cross-product positions can be compared on equal footing; vega and theta need no such weighting since they're tied to dollar premium, not price level. *See Chen/Sebastian ch.14.*
- **Bid** — the highest price a buyer currently offers to pay; also the "buy" side of a market maker's quote. *See Bittman ch.1, ch.9.*
- **Binomial Model** — a discrete-time-step option pricing model (Cox/Ross/Rubinstein) used for American-style options where early exercise must be considered. *See Bittman ch.2, ch.3.*
- **Black-Scholes Model** — the closed-form option pricing formula for European-style options (Black & Scholes, 1973). *See Bittman ch.2, ch.3.*
- **Book Orders** — resting customer limit orders that can distort a quoted bid-ask midpoint away from the "true" theoretical midpoint. *See Chen/Sebastian ch.4.*
- **Box Spread (Long/Short)** — a 4-leg, stock-free arbitrage combining a long call + short put at one strike with a short call + long put at another; long box (net debit) or short box (net credit), each locking in the strike-price spread if priced correctly; carries double pin risk. *See Bittman ch.6.*
- **Broken-Wing Butterfly** — an asymmetric-wing variation of the iron butterfly named as part of TOMIC 1.0's starter strategy set. *See Chen/Sebastian ch.10.*
- **Bull Call Spread** — a long call vertical spread (buy lower strike, sell higher strike); net debit, limited risk/profit. *See Bittman ch.1, ch.10.*
- **Bull Put Spread** — a credit put vertical spread expressing a bullish, theta-positive view. *See Chen/Sebastian ch.9.*
- **Butterfly Spread (Long, with Calls)** — buy 1 lower-strike call, sell 2 middle-strike calls, buy 1 higher-strike call at equidistant strikes; net debit, limited risk/profit. *See Bittman ch.1; Bittman ch.9 (built via 3 market-making trades).*
- **Butterfly Trading Checklist** — three-item pre-entry checklist (butterfly's own IV percentile, inter-month skew width, intra-month skew) for judging whether a butterfly entry is favorable. *See Chen/Sebastian ch.13.*

### C

- **Calendar Spread (Time Spread)** — sell one option, buy the same strike in a different (later) expiration; a "term swap" trading the relationship between two months' IV rather than a single-expiration structure; long or short variants. *See Chen/Sebastian ch.9, ch.11.*
- **Call Option** — the right to buy the underlying at the strike price until expiration; the writer is obligated to sell if exercised. *See Bittman ch.1.*
- **Card Game Value** — the residual (~$0.10–$0.25) value a deep-OTM/near-worthless option retains far longer than pricing models predict, because a one-shot option position (unlike a repeated-play "house edge" game) offers no chance to recoup a single bad outcome; underpins a rule to exit credit spreads before they decay to pure Card Game Value. *See Chen/Sebastian ch.12.*
- **Cash Account** — a brokerage account where purchases are fully paid in cash (no margin borrowing). *See Bittman ch.1.*
- **Cash-Settled Option** — an option where only cash (not the underlying) changes hands at exercise/assignment (e.g., index options). *See Bittman ch.1.*
- **Claims Processing** — the insurance-value-chain function of determining loss cost and paying claims; TOMIC's analogue is being assigned/exercised on a written option. *See Chen/Sebastian ch.1.*
- **Collar** — buying downside puts and selling upside calls against a long stock position to finance the puts; the institutional hedging flow the authors cite as the main driver of equity index "investment skew." *See Chen/Sebastian ch.4, ch.8.*
- **Complex Order** — a multi-leg spread order submitted and priced as a single unit rather than leg-by-leg; generally the safer way for less experienced traders to enter delta-neutral spreads. *See Chen/Sebastian ch.4.*
- **Cone of Feasibility** — the price/time window in which an option is still logically capable of finishing ITM; option value is shed fastest as it exits this window, which is why far-OTM options decay more linearly than ATM ones. *See Chen/Sebastian ch.9 (crediting Bittman ch.3).*
- **Conversion** — the foundational stock-option arbitrage: long stock + long put + short call, same strike/expiration; profitable when call time value exceeds put time value by enough to cover carry/costs/target profit. *See Bittman ch.6.*
- **Cost of Carry** — the net financing cost/benefit (interest net of dividends) of holding the underlying; drives the gap between call and put time value in put-call parity and the profitability math of conversions/reverse conversions. *See Bittman ch.5, ch.6; Chen/Sebastian ch.13 (shortened to "K").*
- **Covered Call** — long stock + short call; risk/payoff-equivalent to a short put via put-call parity/synthetic relationships. *See Bittman ch.5; Chen/Sebastian ch.13.*
- **Credit (position/spread)** — a position established for a net cash inflow; profits as its value decreases. *See Bittman ch.4.*
- **Credit Spread** — a vertical (or other) spread sold for a net credit, theta-positive; TOMIC's core income-generating building block. *See Chen/Sebastian ch.9.*

### D

- **Daily Return (formula)** — `(closing price today − closing price yesterday) / closing price yesterday`; the base unit of historic volatility calculation. *See Bittman ch.7.*
- **Debit (position/spread)** — a position established for a net cash outflow; profits as its value increases. *See Bittman ch.4.*
- **Delta** — an option's (or position's) estimated value change per one-unit change in the underlying's price; calls positive, puts negative; position delta sums quantity-weighted deltas across legs. *See Bittman ch.3, ch.4, ch.8, ch.10.*
- **Delta-Neutral** — a multi-leg position (any mix of long/short stock, calls, puts) whose combined net delta is zero (or near-zero); profits/losses based on the gap between implied and realized volatility, not direction. *See Bittman ch.8, ch.9.*
- **Delta/Gamma Ratio Hedging** — a retail-feasible gamma-scalping method that flattens delta once accumulated delta reaches a set ratio (commonly 1:1) to gamma, rather than continuously recalculating a decay-offsetting move size. *See Chen/Sebastian ch.14.*
- **De-risking** — deliberately reducing portfolio exposure in response to defined trigger conditions (e.g., hitting loss limits, an unreadable new market regime). *See Chen/Sebastian ch.12.*
- **Diagonal Spread (Double Diagonal)** — sell front-month OTM call and put, buy further-out OTM call and put in a later expiration; used to trade the front-month "smile" cheaply and is sensitive to weighted-vega effects. *See Chen/Sebastian ch.11.*
- **Discounted Present Value (DPV) of Strike (formula)** — `DPV = strike × [1 − (rate × days/365)]`, the T-bill-like present-value concept underlying conversion/reverse-conversion/box-spread pricing (borrowing rate for conversions/long boxes, lending rate for reverse conversions/short boxes; adjusted for dividends by using DPV of strike+dividend). *See Bittman ch.6.*
- **Dividend Yield** — the continuous-yield way index options model dividends in a pricing calculator (vs. discrete dated dividends for equities). *See Bittman ch.2.*
- **Double Diagonal** — see Diagonal Spread.
- **Double Pin Risk** — the box-spread version of pin risk: landing exactly on either of the box's two strikes at expiration creates unpredictable stock positions from both legs simultaneously. *See Bittman ch.6.*

### E

- **Effective (Stock) Price** — the true implied stock price once option premium is factored in (e.g., exercising a call bought for 2.00 gives an effective long price of strike+2.00); with zero rates/dividends, `synthetic stock price = strike + call price − put price`. *See Bittman ch.5.*
- **European-style exercise** — an option that can only be exercised at expiration; priced with Black-Scholes since no early-exercise branch is needed. *See Bittman ch.2.*
- **Ex-Dividend Date** — the first day a new buyer does not receive an upcoming dividend, determined by working back from the record date given T+3 settlement. *See Bittman ch.6.*
- **Exercise** — the action taken by an option's owner to invoke the contract's right (buy for calls, sell for puts). *See Bittman ch.1.*
- **Expected Volatility** — a trader's forecast of future realized or implied volatility; whatever number is entered into a pricing calculator's volatility input, by definition. *See Bittman ch.7.*
- **Expiration Date** — the last day an option can be exercised; unexercised options expire worthless after this date. *See Bittman ch.1.*

### F

- **FINRA / SIPC** — regulatory/insurance memberships to confirm when selecting a broker, as a check on broker reputation/solvency risk. *See Chen/Sebastian ch.6.*
- **Float** — an insurance company's (or TOMIC's) premiums/reserves held and invested before claims are paid; a secondary profit source beyond underwriting. *See Chen/Sebastian ch.1.*
- **Forward Volatility** — the one option-pricing input (of five) that is never actually known in advance; its uncertainty is framed as the options trader's core edge. *See Chen/Sebastian ch.8.*
- **Front Spread (One-by-Two)** — sell 2, buy 1 (opposite ratio from a back spread); requires portfolio margin; must be entered for a net credit; profits as the underlying moves away from the two short strikes. *See Chen/Sebastian ch.9.*

### G

- **Gamma** — the sensitivity of delta itself to a one-unit change in the underlying's price (delta's rate of change); always positive for both calls and puts; largest ATM. *See Bittman ch.4, ch.10; Chen/Sebastian ch.14.*
- **Gamma Scalping** — actively trading the underlying (or options) around a long-gamma position to monetize its delta oscillation as the underlying moves; two named retail-adaptable methods are "Pay the Decay" and Delta/Gamma Ratio Hedging. *See Chen/Sebastian ch.14.*

### H

- **Hedge** — a position (typically stock, traded against an option fill) established to offset another position's short-term market risk; the mechanism underlying market-maker delta-neutral trading. *See Bittman ch.8, ch.9.*
- **Historic Volatility** — the annualized standard deviation of daily returns over a specified past observation period. *See Bittman ch.7.*
- **Human Risk** — the real-world unwillingness (for good reason) of traders to sell extremely cheap ("lottery ticket") options naked, since a rare huge move can produce catastrophic percentage losses pricing models don't anticipate; underlies the "never short options worth $0.10 or less" rule. *See Chen/Sebastian ch.8.*

### I

- **Implied Volatility (IV)** — the volatility percentage that, plugged into a pricing formula, reproduces an option's actual market price; functions like a stock's P/E ratio as a market-determined comparison metric. *See Bittman ch.7; Chen/Sebastian ch.8.*
- **Insurance** — the equitable transfer of risk from one party to another in exchange for a premium; the foundational analogy (via TOMIC) for the entire Chen/Sebastian business framework. *See Chen/Sebastian ch.1.*
- **Intrinsic Value** — the in-the-money portion of an option's price (option price minus time value). *See Bittman ch.1.*
- **Investment Skew** — the typical equity/equity-index skew pattern (OTM puts trade at higher IV than ATM, OTM calls lower) attributed to the market's structural long-stock bias driving collar-hedging demand. *See Chen/Sebastian ch.8.*
- **IRC Section 1256 / 60-40 Tax Treatment** — U.S. tax rule for broad-based cash-settled index options: gains treated as 60% long-term / 40% short-term capital gain regardless of holding period, yielding a lower blended tax rate. *See Chen/Sebastian ch.2.*
- **Iron Butterfly (ATM)** — two vertical spreads centered ATM (short ATM straddle + protective long strangle); profits if the underlying stays near the center strike; skew is the single most important entry factor. *See Chen/Sebastian ch.9.*
- **Iron Condor** — two OTM vertical spreads (a short call spread above, a short put spread below) set where the underlying is unlikely to reach; profitable when IV exceeds realized/expected movement (ATR). *See Chen/Sebastian ch.9.*
- **ITM (In-the-Money)** — a call with underlying price above strike, or a put with underlying price below strike. *See Bittman ch.1.*

### K

- **Kite Spread** — an iron-condor upside adjustment: buy a long call below an existing short spread, then sell more of the original spread at a richer (further-OTM) credit, using the added credit to help pay for the new long; similar to a ratio spread but with less vega and more explosive gamma. *See Chen/Sebastian, Appendix D.*
- **Kurtosis** — alternate term used for volatility skew (the shape of the IV curve across strikes). *See Chen/Sebastian ch.8.*

### L

- **Leverage** — the effect by which a smaller equity base (vs. account value) in a margin account produces a larger percentage equity swing for a given percentage price move. *See Bittman ch.1.*
- **Loss Ratio** — the insurance-industry actuarial concept (expected claims as a fraction of premium); TOMIC's mirror is an option's model-derived probability of expiring worthless. *See Chen/Sebastian ch.1.*
- **Long Straddle** — buy a call and put at the same strike/expiration; unlimited profit potential above/below two breakevens; a high-volatility strategy. *See Bittman ch.1.*
- **Long Strangle** — buy an OTM put and OTM call at different strikes; cheaper than a comparable straddle, wider breakevens. *See Bittman ch.1.*

### M

- **Maintenance Margin** — the equity level (above minimum margin, generally below initial margin) a margin call must restore an account to. *See Bittman ch.1.*
- **Maker-Taker Model** — an exchange pricing model that pays rebates to liquidity providers and charges liquidity takers; generally to be avoided when routing orders unless actually hitting a bid/lifting an offer. *See Chen/Sebastian ch.4.*
- **Margin Account** — a brokerage account where the broker lends money ("margin debt") against marginable positions, subject to initial/maintenance margin rules. *See Bittman ch.1.*
- **Margin Call** — a broker's demand to restore equity to maintenance margin after it falls below minimum margin. *See Bittman ch.1.*
- **Margin Debt / Margin Deposit** — the loan amount extended by a broker in a margin transaction, and the customer's own required equity contribution, respectively. *See Bittman ch.1.*
- **Market Maker** — an exchange-member, SEC-registered broker-dealer obligated to maintain continuous two-sided quotes within maximum spreads/minimum size, in exchange for lower margin requirements. *See Bittman ch.1, ch.8, ch.9.*
- **Married Put** — long stock + long put; a worked example of how portfolio margin can dramatically reduce required margin versus Reg-T for an offsetting position. *See Chen/Sebastian ch.6.*
- **Mean Reversion (of volatility)** — the assumption underlying most option-selling strategy: unusually fast-moving markets tend to slow, and unusually calm markets tend to speed up, so IV extremes tend to normalize. *See Chen/Sebastian ch.4.*
- **Minimum Margin** — the equity percentage floor that, if breached, triggers a margin call. *See Bittman ch.1.*
- **Multiplier (option contract)** — the shares/units one option contract represents (usually 100 shares or 1 futures contract); must stay consistent across legs of a position or after corporate actions (splits, etc.) for correct Greek/exposure math. *See Bittman ch.2, ch.8.*

### N

- **National Best Bid and Offer (NBBO)** — the aggregated best bid and best offer for a security across all exchanges/market makers/public quotes at a given moment; exchanges cannot execute outside it. *See Bittman ch.1.*

### O

- **One-by-Two Spread** — see Front Spread.
- **Op-Eval Pro** — the bundled analytical software from Bittman's book; not itself reusable, but its underlying concepts (single-option calculator, spread/portfolio Greeks aggregation, theoretical price tables, one-standard-deviation distribution screen) are. *See Bittman ch.2.*
- **OTM (Out-of-the-Money)** — a call with underlying price below strike, or a put with underlying price above strike. *See Bittman ch.1.*
- **Over-Adjusting Disease** — the (named, common) trader failure mode of adjusting a position that is merely near trouble rather than actually in trouble, needlessly extending trade duration/exposure/cost. *See Chen/Sebastian ch.12.*
- **Overvalued / Undervalued** — an option is overvalued when its market-implied volatility exceeds the trader's own expected volatility forecast (undervalued when the reverse); inherently subjective since expected volatility is a personal forecast. *See Bittman ch.7.*

### P

- **Parity** — an option trading at 100% intrinsic value with zero time value. *See Bittman ch.1.*
- **"Pay the Decay" (formula)** — a gamma-scalping trigger-sizing method: `X = SQRT(2.8 × Theta / Gamma)` gives the underlying move needed that day to offset time decay (the 2.8 factor partly accounts for weekend decay); scalp at ~50% of X rather than waiting for the full move. *See Chen/Sebastian ch.14.*
- **Payment for Order Flow** — the practice of exchanges/market makers paying brokers for order routing priority; generally disadvantageous to the retail customer since it can route orders away from the deepest/best-quoted venue. *See Chen/Sebastian ch.13.*
- **Physical-Delivery Option** — an option where exercise/assignment transfers the actual underlying (e.g., 100 shares for an equity option). *See Bittman ch.1.*
- **Pin Risk** — the risk of the underlying closing exactly at an arbitrage position's strike at expiration, making assignment of short options unpredictable and creating unavoidable weekend stock-position exposure. *See Bittman ch.6.*
- **Portfolio Margin (PM)** — a margin methodology that stress-tests the whole portfolio (rather than summing per-position Reg-T requirements), often dramatically reducing required margin for hedged/offsetting positions. *See Chen/Sebastian ch.6.*
- **Position Greeks** — the quantity-weighted sum, across every leg of a position, of each individual option's Greek; translates single-option sensitivities into whole-position profit/loss estimates. *See Bittman ch.4, ch.10.*
- **Premium** — the price of an option (term borrowed from insurance, where it denotes the price of a policy). *See Bittman ch.1; Chen/Sebastian ch.1.*
- **Price Discovery** — the supply-and-demand process (not market-maker fiat) that actually sets implied volatility levels; market makers merely take the other side of order flow. *See Chen/Sebastian ch.8.*
- **Protective Put** — long put + long stock; risk/payoff-equivalent to a long call via put-call parity. *See Chen/Sebastian ch.13.*
- **Public Trader** — a market participant who is not an exchange member/broker-dealer (retail, funds); subject to standard margin requirements. *See Bittman ch.1.*
- **Put Option** — the right to sell the underlying at the strike price until expiration; the writer is obligated to buy if exercised. *See Bittman ch.1.*
- **Put-Call Parity** — the no-arbitrage relationship linking stock, call, and put prices, enabling any one to be synthesized from the other two; base equation `Stock = Call − Put` (zero-rate case); Chen/Sebastian's real-world form: `C − P = S − X + (I − D)`. *See Bittman ch.5; Chen/Sebastian ch.13.*

### R

- **Ratio Spread (Back/Front)** — see Back Ratio Spread and Front Spread.
- **Realized Volatility** — the volatility that actually occurs over a future period; historic volatility computed retroactively over a period that hasn't happened yet at the time of the forecast. *See Bittman ch.7.*
- **Record Date** — the date by which an investor must be a shareholder of record to receive a declared dividend. *See Bittman ch.6.*
- **Reg-T Margin** — the default, per-position margin calculation methodology (as opposed to portfolio margin's whole-portfolio stress test); recommended for beginners. *See Chen/Sebastian ch.6.*
- **Reinsurance** — an insurer offloading unwanted/catastrophic risk to another party; TOMIC's analogue is buying deep-OTM index puts or VIX calls as portfolio insurance. *See Chen/Sebastian ch.1, ch.3.*
- **Relative Pricing** — using a known call-minus-put time-value gap (from a conversion/box) plus two of {stock, call, put} prices to solve for the third. *See Bittman ch.6.*
- **Reverse Conversion ("the Reversal")** — short stock + short put + long call, same strike/expiration; the mirror of a conversion, established for a net credit invested at the risk-free rate. *See Bittman ch.6.*
- **Rho** — an option's (or position's) estimated value change per one-percentage-point change in interest rates; positive for calls, negative for puts. *See Bittman ch.4.*

### S

- **Scaling In** — a market-maker technique of executing a growing position in successive increments at progressively worse prices for the counterparty (better for the market maker) as size builds, bounded by a hard breakeven limit `(2 × spread − increment) / increment`. *See Bittman ch.9.*
- **Sector Risk / Company Risk / Market Risk / Systemic Risk** — the four named risk levels (macro to micro) TOMIC must account for when choosing hedges; systemic risk is hedged with real assets, market risk with index puts, sector/company risk with diversification and single-name options. *See Chen/Sebastian ch.3.*
- **Sharks and Piranhas Heuristic** — a risk framing where "shark" losses are single catastrophic trades (mitigated by the 2%-per-trade rule) and "piranha" losses are many small cumulative losses (mitigated by the 6%-per-month stop). *See Chen/Sebastian ch.3.*
- **Short Box Spread** — see Box Spread.
- **Short Stock Rebate** — the interest income (split between broker and stock lender) earned on cash proceeds from a short sale; a factor in arbitrage strategy pricing. *See Bittman ch.1.*
- **Short Straddle** — sell a call and put at the same strike/expiration; a low-volatility strategy, profit limited to premium received. *See Bittman ch.1.*
- **Short Strangle** — sell an OTM put and OTM call at different strikes; profits if the underlying stays between the two strikes. *See Bittman ch.1.*
- **Skew (Volatility Skew)** — same-underlying, same-expiration options at different strikes trading at different implied volatilities; structurally disadvantages naive OTM option buyers (Bittman) and is driven by institutional collar-hedging demand (Chen/Sebastian). *See Bittman ch.7; Chen/Sebastian ch.4, ch.8, ch.11.*
- **Stages of Skew (Five Phases)** — a named skew life-cycle framework: Calm, Calm Before the Storm, The Typhoon, The Calming Storm, and a residual Phase 5 before returning to Calm. *See Chen/Sebastian ch.11.*
- **Standard Deviation (annualized volatility, formula)** — `SD for period = annual volatility × √(days in period / days per year)`; converts annual volatility to any time period for price-range estimation. *See Bittman ch.7.*
- **Stop-Loss Point** — a predetermined exit level (in $, option price, or underlying price) set below theoretical max loss, especially critical for directional and short-option positions. *See Bittman ch.10.*
- **Strategy Learning Sequence** — a complexity-graded recommended order for learning the book's option strategies (like earning karate belts). *See Chen/Sebastian, Appendix B.*
- **Strike Price (Exercise Price)** — the price at which the underlying can be bought (call) or sold (put) under the option contract. *See Bittman ch.1.*
- **Synthetic Position** — a two-instrument combination that replicates a third real position's risk/breakeven/profit profile via put-call parity (six equivalences: synthetic long/short stock, synthetic long/short call, synthetic long/short put). *See Bittman ch.5.*

### T

- **Term Structure** — the relationship of implied volatility across different expiration months for the same underlying; a core driver of calendar-spread trade selection. *See Bittman ch.7 (implicit); Chen/Sebastian ch.2, ch.4, ch.8, ch.11.*
- **Theta** — an option's (or position's) estimated value change per one-unit change in time to expiration; usually negative for long options (decay). *See Bittman ch.3, ch.4, ch.10.*
- **Third Third Third Rule** — an iron-condor risk-management rule: first adjustment at 1/3 of maximum loss, second at 2/3, exit at the full maximum loss. *See Chen/Sebastian ch.9.*
- **Time Value** — an option's price minus its intrinsic value; equal for same-strike/expiration calls and puts only in the zero-interest-rate case. *See Bittman ch.1, ch.5.*
- **TOMIC (The One Man Insurance Company)** — Chen/Sebastian's central framework: running an individual options-selling operation using an insurance company's functional structure (trade selection = underwriting, risk management = reinsurance/claims, trade execution = distribution). *See Chen/Sebastian ch.1.*
- **Trader's Short Hand** — simplified rules of thumb for judging assignment risk without full put-call-parity math (comparing cost-of-carry to the opposing option's value). *See Chen/Sebastian ch.13.*
- **Trading Journal** — a per-trade log (win/loss, days-in-trade, yield, etc.) used as the feedback mechanism for continuous improvement; recommended review cadence is monthly/quarterly/annually against a benchmark. *See Chen/Sebastian ch.7.*
- **Trading Plan** — the written document specifying a trader's goals, markets, strategies, risk-management parameters, and entry/exit rules; the foundational TOMIC support function. *See Chen/Sebastian ch.5, ch.10.*
- **Tranching (Flies)** — repeatedly adding more butterflies to an existing losing position as an "adjustment"; explicitly warned against as a common cause of major losses. *See Chen/Sebastian ch.9.*
- **True Range** — the greatest of: current high minus current low; |current high − previous close|; |current low − previous close|; the building block of ATR. *See Chen/Sebastian ch.9 (Endnote 1).*

### U

- **Underwriting** — the insurance-value-chain function of defining/selecting/pricing risk; TOMIC's analogue is trade selection (choosing markets, strategies, strikes, and pricing). *See Chen/Sebastian ch.1, ch.2.*
- **Units** — cheap (near "lottery ticket priced") OTM options held as standing tail-risk insurance; behave nonlinearly (reflexively) in a violent selloff because vega/delta feed on each other as panic buying hits them; recommended sizing ~5–10% of allocated trading capital. *See Chen/Sebastian ch.3, ch.8, ch.9.*

### V

- **Vega** — an option's (or position's) estimated value change per one-percentage-point change in implied volatility; always positive for both calls and puts; largest ATM; "vega" is not an actual Greek letter. *See Bittman ch.4.*
- **Vega Neutralizer** — the effect by which front-month IV's greater "frenetic" movement can overwhelm/neutralize a calendar spread's theoretically long raw vega position. *See Chen/Sebastian ch.11.*
- **Vertical Spread** — a long and short option at different strikes, same expiration (bull/bear, call/debit or put/credit variants); the foundational spread building block for iron condors/butterflies. *See Bittman ch.1, ch.10; Chen/Sebastian ch.9.*
- **VIX** — the CBOE volatility index; used both as a market-fear gauge and as its own option-tradable underlying (with distinct mean-reversion pricing behavior versus spot). *See Chen/Sebastian ch.3, ch.4, ch.11.*
- **Volatility** — price change magnitude without regard to direction; the annualized standard deviation of returns. *See Bittman ch.7.*
- **Vomma** — front-month (and generally shorter-dated) options' outsized sensitivity to changes in implied volatility itself, versus longer-dated options that hold more raw vega but react less to IV changes. *See Chen/Sebastian ch.8.*

### W

- **Weighted Vega (and Weighted Delta/Gamma)** — adjusting raw Greek exposures for the fact that different expirations/products/strikes don't move proportionally with each other (front-month IV moves more than back-month; different underlyings' point-moves carry different percentage significance); a position that looks Greek-flat unweighted can be significantly net long or short once properly weighted. *See Chen/Sebastian ch.9, ch.11, ch.14.*
- **Wing Width Guidelines** — four rules for sizing a butterfly/condor's long "wing" strikes (don't buy wings worth under $0.25, target at least 1:1 risk/reward, check whether moving a wing in saves meaningful margin relative to profit given up, exit or tighten once wing value decays under $0.25). *See Chen/Sebastian ch.13.*
