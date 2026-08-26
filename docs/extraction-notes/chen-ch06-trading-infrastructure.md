Source: Chen/Sebastian, *The Option Trader's Hedge Fund*, Chapter 6 "Trading Infrastructure", physical pp. 80–87.

## Overview / Introduction (p.80)

Trading infrastructure = the back-office elements needed to implement TOMIC: risk capital, broker, trading platform, analytical software, portfolio margin, information sources, dedicated space, and backup plans.

## Risk Capital (heading present)

TOMIC is explicitly framed as a **scalable business** — it can start small and grow without fundamentally changing; what changes with scale is the operator's *skill*, not the underlying model.

Capital analogy: every business needs starting capital (even a lemonade stand needs money for lemons/sugar/ice); TOMIC needs capital to cover margin requirements, which are the direct equivalent of an insurance company's reserves (capital held to be able to cover claims against policies written).

**Minimum starting capital cited: as little as $5,000.** Guidance: start small, add capital as experience and consistent profits accumulate.

**Four operator experience levels defining appropriate risk-capital scale** (Level 0–3):

- **Level 0 — Beginner**: just starting to learn options trading mechanics — placing/removing orders, basic trade execution. Should start with a small account trading small lots. Note on paper trading: brokers (and the CBOE) offer paper/simulated accounts, useful for learning the *platform* but explicitly **not useful for learning how to operate TOMIC** — the psychological stress of real money is fundamentally different from paper money. Recommendation: beginners should trade with a real-money account despite the small size.
- **Level 1 — Intermediate**: good grasp of options basics and the "anatomy" of different strategies (butterflies, condors, calendars, diagonals named as examples); understands strategy use cases and has some trade-selection judgment. Characterized as "knows enough to get in trouble, and enough to get out of trouble most of the time."
- **Level 2 — Semiprofessional**: more experience; good mastery of option strategies and when to apply each; knows which trades offer the best risk/reward; skilled at trade management and adjustments. Manages TOMIC part-time (has another job or is retired), but a good portion of income derives from TOMIC. "Master at managing trades."
- **Level 3 — Professional**: operates TOMIC for a living; all or most income derives from it; may be trading personal capital or managing others' money. Manages the **entire portfolio**, not just individual trades — including portfolio-level Greeks, not just per-position Greeks. Analogy: "like a general in a battle; you manage the entire battlefield." Portfolios are typically larger with more concurrent trades than Levels 0–2. Notable distinction: professional-level returns are **not necessarily higher** than semipro returns, but are **more consistent** — portfolio-level management smooths peaks and valleys.

## The Trading Platform (Broker) (heading present)

A good trading platform is essential — TOMIC (a one-person operation) has no trading desk of staff to execute orders; the operator is simultaneously trader, underwriter, chief executive, and "the janitor of the entire company." A good platform saves time and prevents costly execution errors.

**Broker-selection characteristics** (distinct list from Ch.4's broker-routing criteria — this one is about overall broker fit, not per-order routing):

1. **Option specialist** — prefer a broker that specializes in options (not just "allows" options trading) since this affects both the tools offered and the margin terms available.
2. **Understanding of complex order margin** — an options-savvy broker will margin an iron condor correctly: only one side's worth of margin (since only one vertical of the condor can lose at a time), rather than requiring margin for both verticals.
3. **Customer service.**
4. **Reputation** — choose a broker unlikely to fail; confirm **FINRA and SIPC** membership.
5. **Trading platform** — a good online platform for trading options easily.
6. **Trading desk** — a live desk to call when the platform or Internet is down.

Platform selection follows broker selection (the platform is usually broker-tied) unless the account is large enough to justify a third-party platform.

**Trading-platform checklist (what a good platform should have):**
1. **Trade analysis tools** — graphical risk-graph plotting for analyzing an option trade.
2. **Charts** — basic charting capability for the underlying market.
3. **Easy to use** — most brokers offer a paper-trading version of their platform to test the UI before committing.
4. **Customizable layouts** — ability to arrange information to speed up data gathering and decision-making.
5. **External links to Excel** (not a "must-have" but very useful) — pulling real-time platform data into Excel for custom calculations, trade-hunting, and real-time position monitoring.

**Third-party (broker-agnostic) platforms** become worth considering for accounts above roughly **$1 million**. Named examples: **Obsidian, Derivix, Microhedge, Real Tick.**

## Portfolio Margin (heading present)

**Reg-T margin** is the default/near-universal option account margin methodology and was the *only* option available to retail customers before 2007. **Portfolio margin (PM)** became available to some retail accounts after 2007 (broker-specific minimum account requirements apply).

Mechanism difference: Reg-T calculates margin per individual position and sums them; PM instead **stress-tests the entire portfolio** and bases the margin requirement on the stress-test outcome — meaning offsetting/hedged positions can require dramatically less margin under PM.

**Worked numeric example — married put (Reg-T vs. PM):**
- Position: Long 100 shares AAPL @ $330; long 1 put, AAPL Oct 320 strike @ $18.
- **Reg-T requirement**: 50% of equity purchase cost ($33,000) = $16,500, **plus** 100% of put premium = $1,800 → **Total Reg-T margin = $17,300.**
- **PM requirement**: maximum loss if stock falls 15% = $4,950, offset by the theoretical gain in the put of $3,950 → net loss = $1,000 → **Total PM = $1,000.**
- **Difference: $16,300 of capital liberated** under PM with no change to the position's actual risk profile. Text notes not every position sees such dramatic savings, but this illustrates the potential magnitude.

Caveats: a more conservative broker may apply additional "haircuts" on top of standard PM requirements (e.g., increasing the requirement for a portfolio overconcentrated in one sector) — understand your specific broker's PM rules. **Caution**: having PM available doesn't mean you must use it to the maximum — always actively track and manage total exposure. **Recommendation: beginners should use the more conservative Reg-T standard** until skilled enough at whole-portfolio risk management to handle PM's added leverage responsibly.

## Information Resources and Other Analytical Tools (heading present)

Framing: easy to get information-overloaded in the Internet age.

**List of information sites cited as useful** (reproduced verbatim):
- www.bloomberg.com
- finance.yahoo.com
- www.seekingalpha.com
- www.stocktwits.com
- www.thestreet.com
- www.theflyonthewall.com
- www.tradethenews.com
- www.livevol.com
- www.cboe.com
- www.ivolatility.com

Mix of free and paid sites; choice depends on trading style/products/markets traded.

**On broker-provided analytics/Greeks**: broker-calculated Greeks depend on the broker's chosen pricing model — some brokers simplify their models (e.g., omitting dividends from the Greeks calculation), which may matter for more sophisticated traders. This is a reason to consider buying data from a third-party provider whose model assumptions you trust more.

**Skew/term-structure analysis tools**: named examples **livevolpro.com** and **ivolatility.com**, useful for trade selection.

**Backtesting/simulation tools**: a simulator or "back trader" tests new strategies and simulates behavior/adjustment rules. More useful for systematic traders building rules-based systems than for discretionary traders. Named platforms with integrated backtrading: **ThinkorSwim** (broker-integrated) and **Optionvue** (standalone software package, described as a "popular option backtrading tool").

## Dedicated Space (heading present)

Argues against the "I can trade from anywhere with a laptop" mindset for anyone trading for a living — a dedicated workspace (a separate office, home office, or even a basement desk) that allows focus/concentration is recommended.

**Checklist for the trading space** — should be:
- Quiet, allowing concentration.
- Free of interruptions (explicit examples: screaming children, vacuum cleaner noise).
- Equipped with high-speed Internet.
- Comfortable.
- A calm, serene environment.

## Backup Plans (heading present)

For anyone trading for a living, redundant systems are essential. **Checklist of backup-plan elements:**

- Redundant Internet connections (cable, cellphone, and/or phone-line providers).
- Battery backup for the computer.
- **Use at least two brokers.**
- **Use at least two computers** — a primary desktop plus a backup notebook.
- Program the broker's trade desk number into speed dial / cellphone contacts in case the trading platform fails.
- **Maintain a futures account** to buy/short S&P 500 futures as an emergency hedge — know how many S&P 500 deltas the portfolio holds so you can quickly "go flat" via futures if needed.
- Have a backup physical location in case the primary office becomes unusable (examples given: burst pipes, gas leaks, power outages, A/C failure) — suggested alternatives: Starbucks, Barnes & Noble, a library, a hotel, an airport lounge — anywhere with Internet connectivity.

Closing line: "Having a backup plan is important even though you probably won't need to use it, but occasionally you will be glad you have one."

## Notes on completeness

All six headings from the task's known list ("Risk Capital," "The Trading Platform (Broker)," "Portfolio Margin," "Information Resources and Other Analytical Tools," "Dedicated Space," "Backup Plans") are present and fully covered above, along with the short unheaded chapter introduction. No additional headings found beyond these. Broker/tool/platform selection criteria have been captured explicitly and completely per the task's instruction.
