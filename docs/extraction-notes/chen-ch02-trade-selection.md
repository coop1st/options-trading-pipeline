Source: Chen/Sebastian, *The Option Trader's Hedge Fund*, Chapter 2 "Trade Selection", physical pp. 37–49.

## Overview / Introduction (pp.37–38)

Trade selection at TOMIC = the underwriting function at an insurance company. If underwriting is done correctly and risk is priced fairly, the business is sound (premiums collected adequately compensate for risk taken); if done poorly, premiums may not cover realized risk.

**Contrasting case study — good vs. bad underwriting (carried forward from Ch.1's AIG example, now paired with a success case):**

- **Hurricane Katrina (2005)** — good underwriting example. Per a 2008 CRS report to Congress (Rawle King, cited as Endnote 1): catastrophe-insured losses in 2005 totaled $66.1B from 24 disasters; Katrina alone caused an estimated $43.6B in insured losses from 1.75 million claims. Despite this, the P&C insurance industry's solvency and claims-paying ability were not threatened — insurers had benefited from favorable prior conditions and grew policyholder surplus, in fact earning record profits in 2004–2006. Attributed to sound underwriting built on prior experience (e.g., Hurricane Andrew) that let insurers price risk and premiums correctly.
- **AIG / CDS (2008)** — bad underwriting example (revisits Ch.1's AIG case with more mechanism detail). AIG sold $450B of CDS coverage without understanding how the risk behaved. Key structural point: CDS/mortgage-backed-security risk is **correlated**, unlike fire insurance — "if a house in a neighborhood burns down, it doesn't increase the risk of a house ten miles away burning down," but if one mortgage-backed security fails due to macro conditions (e.g., rising unemployment), others tend to fail too. AIG mispriced this correlation risk, didn't manage its portfolio correctly, and required a government bailout.

Conclusion: trade selection (underwriting) is the single most important TOMIC function — "TOMIC cannot insure what it doesn't know." Five decisions to make when selecting a trade:
1. Which market(s) to trade.
2. Best available strategy for that market.
3. Duration of the trade.
4. Impact of volatility on the trade.
5. Price at which to enter.

## Market Selection (pp.38–41, heading present)

Each market behaves differently (e.g., GLD vs. SPY behave very differently). Analogy: insurance specialists (AFLAC — disability/workers' comp) vs. generalists (State Farm/Allstate — multi-line). TOMIC operators must decide whether to specialize in one or two markets or diversify across many.

**TOMIC's four market classes:**
1. **Indexes**: SPX, NDX, RUT, OEX.
2. **Exchange-traded funds**: SPY, QQQ, IWM, OIH, RTH, XLF, XLE.
3. **Equities**: AAPL, IBM, MCD, WMT, GS, FCX.
4. **Futures**: explicitly *not covered* in this book; noted that they can be traded via diversified commodities indexes or ETCs (exchange-traded commodities).

### Indexes (sub-section)

Tax advantage: **IRC Section 1256** governs broad-based, cash-settled equity index options — gains are treated as 60% long-term capital gain / 40% short-term capital gain **regardless of holding period** and regardless of long/short. This yields a blended max tax rate of ~23% (vs. 35% top ordinary rate) — a significant discount. Caveat given in-text: tax code changes, consult a tax advisor.

Recommended indexes: **SPX, NDX, RUT, DJX, OEX.**

Ticker list of "Primary Tax Advantaged Index Options":
- **DJX** — Dow Jones Industrial Average
- **OEX** — S&P 100 Index Options (American style)
- **XEO** — S&P 100 Index Options (European style)
- **SPX** — S&P 500 Index Options
- **XSP** — Mini-S&P 500 Index Options
- **NDX** — NASDAQ 100 Index Options
- **MNX** — CBOE Mini-NDX Index Options
- **RUT** — Russell 2000 Index Options

60-40 Tax Treatment summary (bullet list from text):
- Applies to broad-based, cash-settled index options (IRC §1256 contracts).
- Regardless of holding period, profits treated as 60% long-term / 40% short-term.
- Reported on Form 6781 and Schedule D.
- Positions are "marked to market" at year-end and taxed as if closed; year-end prices become the cost basis for the next tax year.

Liquidity check: verify option open interest (Figure 2.1, sourced from cboe.com/data/IntraDayVol.aspx). **SPX has the most open interest** of the indexes and "should be on top of your list" for liquidity.

### Exchange-Traded Funds (ETFs) (sub-section)

ETFs = baskets of equities trading like a stock, may mirror an index. Use liquid ETFs with options. Sample list given (from CBOE), reproduced in full since it's a concrete underlying-selection reference:

DIA, DVY, EEM, EWZ, FXE, FXI, GLD, IBB, ILF, IWM, IYR, IYT, KRE, MDY, MOO, OIH, QQQ, RTH, SPY, SLV, TLT, USO, XBI, XES, XHB, XLB, XLE, XLF, XLI, XLK, XLP, XLU, XLV, XLY, XME, XOP, XRT.

Liquidity rule of thumb for ETF options: **open interest > 500 per strike**, plus adequate daily ETF trading volume (volume data from CBOE or other exchanges).

### Options on Equities (sub-section)

Use liquid equities (sufficient trading volume + options availability). Check CBOE average daily volume (Table 2.1 references a top-50 list by avg. daily volume, April 2011 sample — not reproduced verbatim in source beyond the table reference).

**Liquidity rule of thumb for equity options: daily volume > 50,000 contracts** = considered liquid.

Guidance: select a few equities and follow them closely to learn behavior; diversify across industries/sectors. Example five-market diversified selection given: **AAPL, JPM, FCX, LVS, BP**.

## Strategy Selection (p.41+, heading present)

"Strategy selection and trade construction are the crux of the business." Five questions to answer when selecting a strategy:
1. Which market(s) are you trading?
2. What is the direction?
3. What is the time frame?
4. What is the volatility of the underlying and its options?
5. What is the risk/reward?

**Market/price effects on strategy:** underlying price and liquidity determine strike availability and strike spacing (e.g., a $15 stock is harder to trade vertical spreads in than a $300 stock).

**Direction:** three possibilities — up, down, sideways. Having a directional view matters for strategy choice, but you can still profit without being 100% right on direction. Traders use technical analysis, fundamental analysis, or a combination — "study both and use what is most comfortable for you."

## Time Frame (heading present)

Opens with a Miyamoto Musashi quote: "You win battles by knowing the enemy's timing, and using a timing which the enemy does not expect."

Insurance analogy: policy duration affects price (annual policies cost less per day than six-month policies). TOMIC time frames: weeks, months, quarters, semesters, or years. Weekly options are available on many indexes/stocks (CBOE offers weeklies on SPX and select equities like AAPL); monthly options and LEAPS out to 30 months also available.

Time-frame decision depends on the trader's forecast of underlying behavior and the relative volatility across time frames. Examples: if SPX is expected to move sideways for a year with a stable relationship across months' volatility, a **calendar spread** may work well; alternatively, a shorter-duration trade such as a **monthly iron condor or butterfly** may suit, depending on volatility.

## Volatility (heading present)

Insurance analogy: hurricane insurance pricing in Florida (hit every ~12 years, per 150 years of data) vs. the Cayman Islands (hit every ~2 years) should not be priced the same — Cayman coverage should cost more. Analogously, volatility affects market selection and the "price of insurance" (option premium).

Most traders ignore this factor in strategy selection, but it should inform choices — e.g., deciding between a calendar spread and a butterfly in a sideways market should be driven by volatility. Relevant volatility measures: volatility of the underlying itself, the **volatility curve** (volatility across different strikes — i.e., skew), and the **term structure** (volatility across different expirations).

Risk/reward: "defines your edge" — reward should correspond to risk taken, but occasionally an **asymmetric risk/reward** opportunity exists where reward is disproportionately good for the risk taken — this asymmetry is the edge, a major factor in trade selection. Explicitly flagged: covered in more detail in **Chapter 8, "Understanding Volatility."**

## Pricing (heading present)

Price (buy or sell) is the final trade-selection factor. Volatility and price move together — an option's price should be directly proportional to volatility, all else equal (continuing the Florida-vs.-Cayman example: if hurricanes cause equal damage, Cayman insurance should theoretically be priced ~6x Florida's, given the 12-year vs. 2-year hit frequency).

Because insurance/options prices are market-based (not fixed), a mispricing shows up as an edge: if Cayman insurance is priced at only 2x Florida's instead of the "fair" 6x, something is mispriced — the correct trade is to **sell Cayman insurance and buy Florida insurance** (i.e., sell the relatively overpriced/underpriced-for-risk option, buy the cheap one). Same reasoning applies to every TOMIC trade: pricing determines whether a trade is taken, and pricing itself is driven by underlying, strategy, time frame, and volatility.

Chapter close: "you select a trade... underwrite the risk and decide what to insure and at what price in order to make a profit."

## Endnote (heading present)

1. Rawle King, 1/31/2008, CRS Report to Congress, "Hurricane Katrina: Insurance Losses and National Capacities for Financing Disaster Risks," summary.

## Notes on completeness

All six headings from the task list are present and covered: Market Selection, Strategy Selection, Time Frame, Volatility, Pricing, Endnote. No additional headings found beyond these plus the unheaded chapter introduction (captured above as "Overview / Introduction").
