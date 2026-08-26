Source: Chen/Sebastian, *The Option Trader's Hedge Fund*, Chapter 3 "Risk Management", physical pp. 50–59.

## Overview / Introduction (p.50)

Opens with a Star Trek (Kirk) quote on risk and a Will Rogers quote ("You've got to go out on a limb sometimes because that's where the fruit is").

Core framing: TOMIC (like any hedge fund) is in the business of **risk taking, not risk avoidance** — it makes a living by taking on others' risk (subscribing risk) in exchange for premium. Risk cannot be avoided, only managed (street-crossing analogy: you manage risk by looking both ways, but can't eliminate it entirely). Ties back to Ch.2 (Trade Selection): TOMIC must ensure it's compensated enough for the risk it takes on, then must manage portfolio risk to avoid being blindsided by *unexpected* risk (as opposed to accepting losses from risks it deliberately took on, which is fine).

## Risk Management (heading present, p.50+)

Risk management is a continuous process spanning underwriting (trade selection), position sizing, and active money management — "should be ingrained in every TOMIC trader's DNA."

**Risk-management question checklist**, organized by trade lifecycle stage:

*Before the trade:*
- What is the risk/reward ratio of this trade?
- What is the probability of success of this trade?
- What is the maximum loss acceptable for this trade?
- What is the expected return and target profit of this trade?
- Does the new trade maintain the balance/diversification of the portfolio? Is it overexposed in any one sector?

*During the trade:*
- Has the trade reached the maximum allowed loss?
- Has the trade reached the target profit?
- Is the reward of keeping the trade open worth the risk?

*After the trade:*
- Did you follow the risk management rules on this trade?
- If not, why not?

Warren Buffett quote invoked: "Rule number one is never lose money. Rule number two is never forget rule number one" — the secret to following it is disciplined risk-management process.

**Five things TOMIC must do to manage risk** (maps directly to the chapter's remaining subsections):
1. Create a money management policy.
2. Define a position sizing policy.
3. Maintain a diversified portfolio.
4. Adjust trades or exit when a trade goes bad.
5. Buy portfolio insurance to protect against black swan events.

## Money Management (heading present)

Framing: many traders blow up accounts by funding an account and immediately trading without money-management rules in place first.

**"Sharks and piranhas" heuristic** (attributed to Dr. Alexander Elder, one of co-author Dennis's trading instructors):
- **Shark threat** — a single losing trade that takes a big bite out of the account (e.g., losing 35% of equity in one trade) — both financially and psychologically damaging.
- **Piranha threat** — a sequence of many small losses that cumulatively overwhelm the account (analogy: piranhas eating a cow via many small bites).

**Two core money-management rules given explicitly:**
1. **Never risk more than 2% of capital on any single trade** (protects against shark attacks).
2. **If the account loses more than 6% in any single month, stop trading for the rest of the month** (protects against piranha attacks — forces a pause to reassess strategy, setups, or changed market environment). Note: the 6% figure is explicitly called arbitrary — "your percentage could be 5%, 6%, 7%, 10%, or any percentage you can live with"; the key is having *some* stop-loss discipline at the monthly/portfolio level.

## Position Sizing (heading present)

Position sizing operationalizes the 2%-per-trade / 6%-per-month rules.

**Worked example (RUT iron condor):**
- Fund AUM: $2,000,000. 2% rule → max risk per trade = $40,000.
- RUT condor, 10-point wing spreads, uses $1,000 margin (Reg-T assumed) per condor.
- Naive interpretation: $40,000 / $1,000 = 40 condors (risking full margin/max loss per condor).
- **Refinement used in practice**: traders typically use a smaller allowed loss than max, not the full margin. Example given: profit target = 15% of margin, allowed loss = 20% of margin. So a condor's allowed loss = $200 (20% of $1,000), not the full $1,000.
- With a $200 actual risk per condor and a $40,000 total risk budget: $40,000 / $200 = **200 RUT condors** can be traded (5x more than the naive calculation, because the real per-trade risk is smaller than max theoretical loss).

**Does the 2% rule limit you to ~3 trades (since 3×2%=6%)?** No — explicitly addressed. Multiple trades can be held simultaneously under the 2% rule because not all trades are likely to go against you simultaneously *unless they are highly correlated* (which should be avoided — see Portfolio Diversification below). Illustrative math: with 15–20 concurrent trades and an assumed 80% success rate, on average 3–4 trades would go against you in a given month — so hitting the 6% monthly loss threshold is statistically unlikely (4 losing trades at 2% each = 8% gross loss, but this must be netted against contributions from winning trades, which would need to be small to still produce a net 6% loss).

## Portfolio Diversification (heading present)

Position sizing alone is insufficient if positions are correlated — example given: 2%-per-position sizing across Exxon-Mobil, Chevron, BP Amoco, ConocoPhillips, and Petrobras (all integrated oil companies) does not actually safeguard the portfolio because the positions are heavily correlated and would move together.

**Explicit diversification rules:**
- Include at least **five sectors** in the portfolio.
- No single sector should represent more than **25%** of the portfolio.
- Example diversified five-market mix: **SPX, AAPL, GS, FCX, BP.**
- Combined with the per-position rule: no single position should risk more than 2% of TOMIC's capital.

## Adjusting the Different Trades (heading present)

While trades are open, TOMIC must actively manage risk — reducing losses on trades going against it. "There will always be bad trades. No one can win 100% of the time. You can avoid losing only if you don't trade."

Adjustments are made to *protect capital and minimize losses*, not to make more money — made only when a trade is going against you, not when it's performing fine. Explicitly notes that **closing the trade completely is itself a valid adjustment** — "taking a loss early is sometimes better than staying in a losing trade."

Debate framing: some traders believe trade selection doesn't matter if you're an expert adjuster; others believe trade selection/entry matters more than exits. **The authors' stated position: trade selection is more important than trade exits, but adjustments still matter a great deal** — mastering entries, adjustments, and exits together is necessary for success.

## Addressable Risks (heading present)

Recap of the chapter's risk-management solutions so far:
- Money management
- Position sizing
- Diversification
- Unit insurance (introduced later in this chapter, see "Units Can Save Your Portfolio" below)
- Adjustments

**Four risk levels (macro to micro) to be aware of when selecting risk-management strategies:**

1. **Systemic risk** — risk of a financial-system collapse dragging down the broader economy. Example: the 2008 Lehman Brothers collapse, which froze global credit markets and nearly brought down the entire financial system. Very difficult to hedge — in a true systemic failure, even "paper" hedges (e.g., CDS protection backed by a firm like AIG) might not pay out if the counterparty itself fails. **The suggested hedge against true systemic risk is owning real/physical assets, such as physical gold and silver** (not paper hedges).
2. **Market risk** — macro events hitting the entire market (e.g., 9/11, the 2008 financial crisis) — nearly all stocks get hit regardless of individual quality. **Can be hedged with options** — e.g., buying portfolio insurance / index (unit) puts provides good protection.
3. **Sector risk** — events affecting a specific sector (e.g., defense-spending cuts hitting defense contractors; a new tax on financial institutions hitting the financial sector).
4. **Company risk** — events specific to one company (e.g., Enron's collapse, the BP Gulf oil spill, or the death of a key executive like Steve Jobs at Apple). **Can be hedged relatively easily** with options on that specific name, and via portfolio diversification.

A Table 3.1 ("Risk Mitigation Examples") is referenced mapping each risk level to example mitigation approaches (table contents not extractable as text from the PDF beyond what's narrated above).

## Insuring the Portfolio Against Black Swan Events (heading present)

TOMIC should manage catastrophic risk like a traditional insurer reinsures unwanted risk. Example: catastrophic risk defined as something like a **25% single-day market loss**. Reprises the Ch.1 earthquake-reinsurance analogy (ABC Insurance Co. in San Francisco reinsuring earthquake risk with General Re) as a direct parallel to TOMIC divesting catastrophic tail risk.

TOMIC is willing to bear normal market moves (e.g., ±5%) but should reinsure risk beyond that. **Two named reinsurance/hedge instruments:**
1. Buy **out-of-the-money puts on the S&P 500** to protect against a large (e.g., 25%) market downturn.
2. Alternatively/additionally, buy **out-of-the-money calls on the VIX**, on the premise that a large S&P 500 drop causes a large VIX spike. Choice between the two (or blending both) depends on relative pricing of SPX puts vs. VIX calls.

### Units Can Save Your Portfolio (sub-heading present in text, not listed among the task's "known headings" — flagged as additional content found)

Illustrative case: the May 2010 "flash crash." A fund held a May OEX butterfly that was underwater (~10% loss on the butterfly even after hedging/adjustment) as the market fell away from its short strikes going into early May. When the flash crash hit on May 6, the position ended up profitable overall — because the fund was also long **"units,"** which more than offset the butterfly's loss.

**Definition: a "unit"** is an inexpensive option with unpredictable/nonlinear Greek behavior in a crash. Units are cheap relative to the underlying's price level (e.g., in SPY an option becomes a "unit" around $0.20; in SPX, closer to $2.00). Units have **delta below 5** and little to no gamma or vega under normal conditions.

**Mechanism — why units behave nonlinearly in a violent down move:**
- Standard option-pricing models (especially retail-grade ones) assume a roughly uniform increase in volatility across strikes/expirations during a selloff — this is not what actually happens.
- In a violent down move: (1) front-month options increase in value far more than other expirations, relatively speaking; (2) downside puts gain far more value than models predict.
- Analogy used: the volatility curve in a strong down move behaves like an unevenly loaded seesaw — a big move at one end (fat guy jumping on one side) causes disproportionate, even reflexive, movement at the far end (the wood "bends upward" farther from the fulcrum).
- In practice: during a panic, the crowd buys ATM puts; option sellers/shorts scramble to buy cheap OTM "unit" puts to hedge their short exposure. This buying pressure bids up the unit's price, which increases its vega, which increases its delta, which increases its value further as the market keeps falling — a reflexive, self-reinforcing ("snowball") effect.

**Concrete worked example**: a fund bought OEX May 505 puts (units) as a hedge against a short iron butterfly, paying $1.20 each. When the market fell on May 6 (flash crash), these puts were worth almost $10; by May 7 close they were worth $14.50 — a return of **over 1,200%** on a $1.20 option.

**Practical sizing guidance for retail/ordinary traders**: allocate roughly **5%–10% of allocated trading money** (not total account value) into units (cheap OTM puts) as a standing hedge against a standard book of spread trades (condors, butterflies, time spreads). Sizing goal: after adjusting for the expected volatility spike, if the market drops 10% the combined position (spread book + units) should be breakeven-or-better; if the market drops 20%, the combined position should be making money.

Chapter close: understanding units properly requires understanding volatility (explicitly connects forward to Chapter 8, "Understanding Volatility," though not named as an explicit forward-reference the way Ch.2 did). Final framing line: "by properly implementing units, you are willing to bet that you will never have to sell your house because the market dropped 25%."

## Notes on completeness

All seven headings listed in the task ("Risk Management," "Money Management," "Position Sizing," "Portfolio Diversification," "Adjusting the Different Trades," "Addressable Risks," "Insuring the Portfolio Against Black Swan Events") are present and covered above. **One additional sub-heading was found in the source text that was not in the task's known-headings list: "Units Can Save Your Portfolio"** — this is a substantial, distinctive risk-management concept (the "unit" hedge / flash-crash case study) nested under "Insuring the Portfolio Against Black Swan Events," and has been captured in full above since it introduces a concrete, quantified hedging technique (units) that doesn't appear to recur by this name elsewhere in the book's early chapters but is directly relevant to `risk-management-and-position-sizing.md` synthesis.
