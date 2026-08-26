Source: Bittman, *Trading Options as a Professional*, Chapter 1 "Option Market Fundamentals", printed pp. 1–29.

## Fundamental Terms

- **Call option**: buyer's right to *buy* the underlying at the strike price until expiration; seller (writer) is obligated to sell if exercised.
- **Put option**: buyer's right to *sell* the underlying at the strike price until expiration; seller (writer) is obligated to buy if exercised.
- **Underlying**: stock, futures contract, physical commodity, or a cash value based on an index.
- **Strike price / exercise price**: the price at which the underlying can be bought or sold.
- **Expiration date**: last day the option can be exercised; unexercised options expire worthless.
- Example notation: "XYZ December 50 Call" at 3.00 → underlying XYZ (100 shares), December expiration (3rd Friday of the month for US stock options), strike 50, price 3.00/share = $300 total premium.
- **Premium**: the price of an option; term borrowed from insurance. Bittman explicitly draws the analogy: option volatility ≈ insurance risk; option payoffs ≈ insurance claims; option time decay ≈ insurance premiums varying with coverage length.
- **Buyer / long / owner** are interchangeable; **seller / short / writer** are interchangeable (writer also borrowed from insurance terminology).

### Stock Trades Compared with Option Trades (p.2–5)

- A stock order needs 4 pieces of information: **action** (Buy long / Buy to cover / Sell long / Sell short), **quantity**, **ticker**, **price**.
- An option order needs 7: **action** (Buy to open / Buy to close / Sell to open / Sell to close), **quantity** (contracts), **underlying**, **expiration**, **strike price**, **option type** (call/put), **price**.
  - *Buy to open*: new long position. *Buy to close*: closes an existing short. *Sell to open*: new short position (requires margin deposit, since the seller is only creating an obligation, not borrowing shares like a stock short sale). *Sell to close*: closes an existing long.
  - Stock options usually stop trading the 3rd Friday of the expiration month and expire the following Saturday. Cash-settled index options typically stop trading the Thursday before the 3rd Friday, settled off Friday morning opening prices.
- **Exercise**: action taken by the option owner to invoke the contract right. **Assignment**: the process that selects a specific short-option holder to fulfill the obligation (via the OCC, then a broker-dealer, then a specific customer — random at each stage).

### Categories of Options (p.7–8)

- **Physical-delivery options**: exercise/assignment transfers the underlying itself (e.g., equity options → 100 shares).
- **Cash-settled options**: only cash changes hands. Example: SPX Dec 1500 Call exercised at SPX=1520 → writer pays 20 points × $100/point = $2,000 to the owner.

### In-the-Money / At-the-Money / Out-of-the-Money (p.8)

- Call ITM: underlying price > strike. Call OTM: underlying price < strike. ATM: underlying price = strike (in practice, whichever strike is *closest* to underlying price is colloquially called "the ATM option" even if slightly ITM/OTM).
- Put ITM: underlying price < strike. Put OTM: underlying price > strike.

### Intrinsic Value and Time Value (p.9–10)

- **Intrinsic value** = the ITM portion of an option's price. **Time value** = option price − intrinsic value.
- Worked example (stock = 67.00): 65 Call priced 3.50 = 2.00 intrinsic (67−65) + 1.50 time value.
- **Parity**: an option trading at 100% intrinsic value, 0 time value (e.g., 55 Call at 12.00 when stock is 67.00 — theoretically indifferent to owning stock outright, though transaction costs make stock preferable in practice).
- Near-the-money options carry the *most* time value; deep ITM / far OTM options carry the least. (Elaborated further in Ch.3.)

## The Market — Definition 1 (a place) (p.10–11)

- Historically: physical exchange floors (NYSE, AMEX, regionals) using open outcry, floor brokers negotiating on customers' behalf. OTC market was the first stock market without a physical location (still negotiated verbally by phone). Pre-1973 (before listed options), options traded via the Over-the-Counter Put and Call Broker Dealer Association — a phone-brokered network.
- Today: computerized order matching; human negotiation role diminished but human decision-making (this book's focus) remains essential.

## The Market — Definition 2 (bid/ask/size) (p.11–13)

- **Bid**: highest price a buyer currently offers to pay. **Size**: quantity at that price.
- **Ask/offer**: lowest price a seller currently offers to sell at.
- Trading shorthand: bidding states price before quantity ("2.20 for 40"); offering states quantity before price ("20 at 2.30"). A "market" is quoted as "bid-ask, bid-size by ask-size" (e.g., "2.20-2.30, 40 by 20").
- **Public trader**: not an exchange member/broker-dealer (retail investors, mutual/pension funds, hedge funds); subject to standard Reg-T/exchange/OCC margin requirements; can post/withdraw quotes freely.
- **Market maker**: exchange member, SEC-registered broker-dealer; obligated to maintain two-sided quotes within maximum spreads and minimum size (under normal market conditions, varies by exchange/class); exists to guarantee liquidity for public traders; receives lower margin requirements in exchange for this continuous-quoting obligation.

### National Best Bid and Best Offer (NBBO) (p.13–16)

- With multiple exchanges/market makers/public traders quoting simultaneously, the NBBO aggregates the best bid and best offer across all venues.
- Worked example (Table 1-3): 3 exchanges each with market maker(s)/public traders quoting XYZ 50 Calls at various bid/ask/size combinations. NBBO resolves to **3.70 bid for 75 contracts, 3.90 ask for 60 contracts** — computed by summing size at the single best bid price across venues, and size at the single best ask price across venues (marked with `*` for NBBO participants).
- SEC rule: exchanges cannot execute trades outside the NBBO. If a public trader's exchange doesn't have contracts at the NBBO price, the order is either filled by a local market maker improving its quote, or routed/split to the exchange(s) actually quoting the NBBO price.

## Margin Accounts and Related Terms (p.16–19)

- **Cash account**: purchases fully paid in cash. **Margin account**: broker lends money for "marginable transactions"; the loan amount is **margin debt**; **margin deposit** is the customer's required equity.
- Formula: `Account equity = Account value − Margin debt`.
- **Leverage**: because equity is smaller than account value in a margin account, the same % price move causes a larger % change in equity than in a cash account.
- Short stock: broker borrows shares on customer's behalf, sells at market; customer pays nothing upfront (except commissions) but must post margin to guarantee covering losses.
- **Initial margin**: minimum equity % required to open a marginable position (e.g., stock purchases: 50% initial margin under Reg T — buying 100 sh. of $50 stock requires $2,500 equity + commissions, with $2,500 borrowed).
- **Minimum margin**: the equity % floor that must be maintained; falling below it triggers a **margin call**, requiring the customer to restore equity to **maintenance margin** (a level > minimum margin, generally < initial margin) by depositing funds/securities or closing the position.
  - Worked example: stock bought at $50 (margin loan $2,500 fixed) falls to $35 → account value $3,500, equity $1,000 = 28.6% (1,000/3,500). If minimum margin is 35%, this triggers a margin call.
- Key takeaway: the equity supporting a position is central to capital management, and how an investor manages capital determines whether a strategy is speculative or conservative — a theme developed throughout the book.

### Short Stock Rebate (p.18–19)

- When stock is shorted, the sale proceeds go to the **stock lender** (not the seller), held as escrow collateral, invested in T-bills/cash-like instruments; the interest earned is split between the brokerage firm and the stock lender.
- Public traders do *not* share in this interest. **Professional traders/broker-dealers (including market makers) do** — this portion is the **short stock rebate**, and it affects the pricing of option arbitrage strategies (see Ch.6).
- Typical split: option market maker receives ~80% of net interest generated, stock lender 20%.
  - Worked example: 100 shares shorted at $90 → $9,000 cash generated; at 4% annual rate, weekly interest = $9,000 × 0.04 / 52 = $6.92; market maker's 80% share = $5.53/week. Scales materially at institutional position sizes.
- Escrow must equal 100% of current stock value daily; falling stock prices free up capital for market makers (lower costs), rising prices increase escrow/borrowing needs (can raise costs faster than interest earned).

## Profit/Loss Diagrams (p.19–29)

P/L diagrams show three things: **maximum profit potential**, **maximum risk**, **break-even point(s)**. Figures plot P/L at expiration (straight line) and at 60/30 days prior to expiration (curved lines).

Four basic building-block strategies (Figures 1-1 to 1-4):
- **Long call**: unlimited profit potential, risk limited to premium paid, breakeven = strike + premium paid. Example: 100 Call bought at 4.00 → max risk 4.00, breakeven 104.
- **Short call**: mirror image — profit limited to premium received, unlimited risk, same breakeven formula (strike + premium received). Example: 100 Call sold at 4.00 → max profit 4.00, breakeven 104, unlimited loss above breakeven.
- **Long put**: risk limited to premium paid, large profit potential as underlying falls toward zero, breakeven = strike − premium paid. Example: 100 Put bought at 3.00 → max risk 3.00, breakeven 97.
- **Short put**: limited profit (premium received), substantial risk as underlying falls, breakeven = strike − premium received. Example: 100 Put sold at 3.00 → max profit 3.00, breakeven 97, substantial loss below breakeven.

Two-part combinations (Figures 1-5 to 1-8):
- **Long straddle** (buy call + put, same strike/expiration): two breakevens (strike ± total premium); unlimited profit above upper breakeven, substantial profit below lower breakeven; risk limited to total premium paid. "High-volatility strategy" — needs a big move either direction.
- **Short straddle**: mirror image; profit limited to premiums received; "low-volatility strategy" — losses accelerate outside the two breakevens.
- **Long strangle** (buy OTM put + OTM call, different strikes): cheaper than a comparable straddle; breakevens further apart than a straddle; profits above upper breakeven or below lower breakeven. Example: long 95-105 strangle = buy 95 Put @1.50 + buy 105 Call @2.00, total cost 3.50.
- **Short strangle**: mirror image; profits if underlying stays between the two strikes/breakevens.
- **Straddle vs. strangle — 3 differences** (p.24–26): (1) straddle costs more than a comparable strangle; (2) straddle breakevens are closer together, so it starts profiting sooner on a big move; (3) straddle has a smaller chance of *max* loss (requires landing exactly at the strike) vs. a strangle (max loss occurs anywhere between/including the two strikes).

Vertical spreads (Figures 1-9, 1-10):
- **Long call vertical spread ("bull call spread")**: buy lower-strike call, sell higher-strike call, same underlying/expiration; net debit; limited risk and limited profit. Breakeven = lower strike + net premium paid. Example: buy 100 Call @5.00, sell 110 Call @2.00 → net debit 3.00 = max risk; max profit 7.00; breakeven 103.
- **Short call vertical spread ("bear call spread")**: mirror image, net credit, same breakeven formula; profits below breakeven, losses above.

Advanced strategies (Figures 1-11, 1-12), introduced briefly (detail deferred to later chapters):
- **Long butterfly spread with calls**: net debit; buy 1 lower-strike call, sell 2 middle-strike calls, buy 1 higher-strike call; strikes equidistant (e.g., 100-105-110 or 100-110-120); limited risk and limited profit.
- **Long condor spread with calls**: net debit; buy 1 lowest-strike call, sell 1 call at next strike up, sell 1 call at next strike up again, buy 1 highest-strike call; 4 equidistant strikes (e.g., 100-105-110-115); limited risk/profit; involves multiple bid-ask spreads and commissions, so suited only to experienced traders trading at low transaction costs.

## Summary

Options are rights/obligations contracts, not direct ownership — but exercise/assignment creates real stock transactions. Option orders require 7 decisions vs. 4 for stock orders. "The market" has two meanings (a venue; and the bid/ask/size complex) and, in the US, aggregates across many competing market makers/exchanges into the NBBO. Margin-account mechanics matter because many option strategies must be established in margin accounts, and broker-dealers (including market makers) earn short stock rebate income that factors into arbitrage strategy pricing (Ch.6).
