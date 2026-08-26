# Trading Business Framework: The One Man Insurance Company (TOMIC)

**Source:** Chen & Sebastian, *The Option Trader's Hedge Fund* — entirely. This
framework is not addressed anywhere in Bittman's *Trading Options as a
Professional*, which is a market-maker mechanics book, not a business-of-trading
book. Primary chapters: Ch.1 (The Insurance Business), Ch.5 (The Trading Plan),
Ch.6 (Trading Infrastructure), Ch.7 (Learning Processes), Ch.10 (Operating the
Business: TOMIC 1.0 from A to Z), Ch.15 (The Beginning), with supporting
material from Ch.12–13 (Part III "Lessons from the Trading Floor").

This file treats trading as a **business to be run**, not just a set of trades
to place. Strategy mechanics, greeks, and per-trade risk math live in the other
reference files; this file is about the operating structure that wraps around
them.

---

## 1. The Core Analogy: Trading as an Insurance Business

The book's central metaphor: an individual options-selling operation should be
run using the same functional structure as an insurance company. **TOMIC** —
"The One Man Insurance Company" — is the name for that individual (or small)
operation.

**Definition of insurance:** the equitable transfer of risk from one party to
another in exchange for compensation (a premium). An insurer profits by taking
on others' risk in exchange for premium; TOMIC profits by selling options
(collecting premium) and taking on the risk of the underlying's future price
moves, earning most of its profit from time decay.

### The traditional insurance-company value chain

A generic insurer has six functions:

1. **Underwriting** — defining and selecting which risks to insure (statistical
   segmentation of risk pools).
2. **Pricing** — setting premium to generate a positive expected return on the
   risk taken.
3. **Reinsurance** — divesting/redistributing unwanted concentrated or
   catastrophic risk to a specialist.
4. **Claims processing** — determining and paying the cost of a loss.
5. **Customer acquisition** — selling policies through agents/brokers/marketing.
6. **Investment operations** — investing premiums and reserves ("float") for
   additional profit (Buffett/Berkshire's GEICO float is the canonical
   example).

Two profit sources follow from this: **underwriting profit** (premiums minus
claims) and **investment profit** (income on the float). TOMIC makes almost
all of its money from the underwriting side; float investment is explicitly
out of scope (TOMIC keeps reserves in cash/money-market funds, not actively
invested).

### The point-by-point auto-insurance ↔ option-selling mapping

| Auto insurance | Option selling |
|---|---|
| Asset insured = the car | Asset insured = the stock/index/future |
| Policy has a fixed term (e.g., 12 months) | Option has an expiration (days to ~30 months) |
| Insured amount = vehicle value | Strike price defines the insured amount |
| Deductible: owner absorbs first $X of damage | Selling an OTM put: buyer absorbs the first portion of a decline |
| Premium paid for the policy | Premium paid for the option |
| Loss ratio from actuarial tables | Probability of expiring worthless from the pricing model |
| Insurer pays a claim on a loss, keeps premium if claims-free | Seller buys stock at strike if ITM at expiration, keeps premium if OTM |
| Insurer reinsures catastrophic risk (earthquake, hurricane) | Seller "reinsures" via deep-OTM puts on the name or a broad index (S&P 500) against tail events |

**Bottom line:** "The business of a one-man insurance company is to collect
premiums from option buyers in exchange for the risks of losses in the
underlying markets of the options and earn profits from the time decay of the
options."

### How insurance companies (and TOMIC) lose money

Two failure modes: losses on investments (not TOMIC's focus), or losses on
**underwriting** — when claims paid exceed premiums collected because risk was
mispriced or underestimated. Underwriting is called the single most important
function for exactly this reason.

**Cautionary case study — AIG and the 2008 financial crisis:** AIG sold
roughly $450 billion of credit default swaps (a form of credit insurance) on
mortgage-backed securities without correctly modeling the **correlation** in
that risk — unlike fire insurance, where one house burning doesn't raise the
odds of a house ten miles away burning, mortgage-backed securities tend to
fail together under the same macro conditions (e.g., rising unemployment).
When defaults began, AIG lacked the liquidity to pay claims and required a
government bailout. Root cause: poor underwriting — mispricing a correlated,
tail-risk exposure. Contrast case: the P&C insurance industry survived
Hurricane Katrina's $43.6B in insured losses without solvency threats, because
decades of prior catastrophe experience (e.g., Hurricane Andrew) had let
insurers price that risk correctly. The lesson for TOMIC: correlated,
underpriced tail exposure is the mechanism that kills an options-selling
book, not garden-variety losing trades.

### Success drivers of the insurance business

1. **Risk selection** — underwriting and pricing skill.
2. **Risk management** — managing exposure, reinsuring unwanted risk, handling
   claims/losses well.
3. **Risk acquisition** — the sales/distribution channel.
4. **Investment operations** — returns on float (deliberately simplified for
   TOMIC — cash/money-market only).

### TOMIC's simplified value chain: three primary functions

The insurer's six functions collapse into three for TOMIC:

1. **Trade Selection** (= underwriting + pricing) — selecting markets,
   strategies, and timeframes; covered in `spreads-and-combinations.md`,
   `income-strategies.md`, and `directional-strategies.md` for the mechanics,
   and below (§2) for the planning layer.
2. **Risk Management** (= reinsurance + claims + money management) —
   continuous monitoring, position sizing, hedging, adjustment. Full
   quantitative treatment is in `risk-management-and-position-sizing.md`;
   this file covers only the business-process wrapper around it.
3. **Trade Execution** (= customer acquisition, but via an exchange/broker
   instead of a sales force) — going to options exchanges via a broker to
   sell options. Order-routing and fill-quality mechanics are covered in
   `market-making-techniques.md`; broker *selection* as an infrastructure
   decision is covered below (§3).

### The three supporting functions

Every business needs infrastructure before it can operate (analogy: a
fast-food franchise needs real estate, stoves, and phones before it needs
recipes). TOMIC's three supporting structures — each gets its own section
below:

1. **A Trading Plan** (§2) — the operational plan: goals, markets, strategies,
   risk parameters, entries/exits.
2. **Trading Infrastructure** (§3) — brokers, execution/analysis software,
   information resources, portfolio margin, risk capital, physical space,
   backup systems.
3. **Learning Processes** (§4) — the feedback loop: trading journal, sounding
   board (trading group / coach), continuing education.

Chapter 10 (§5 below) walks through building all of this into one concrete
example portfolio ("TOMIC 1.0"), and Chapter 15 closes the book by restating
this exact value chain as the thing to keep coming back to.

---

## 2. The Trading Plan

**Core claim:** not every business needs a formal business plan, but every
successful trader needs a trading plan. It provides a framework, defines
parameters, maintains focus, and — critically — guards against emotional
decision-making while trading. Analogy: a casino gives blackjack dealers fixed
rules (stay on 17, hit below 17) to guarantee consistency and preserve the
house's edge; a trading plan does the same for a TOMIC trader, except the
rules are self-imposed. "In trading you make your own rules, but the key is
to be consistent. If your rules do not work, get new ones... the only way you
will know whether they work is by sticking to the plan and evaluating your
performance continuously." Described as "like a flight plan and an emergency
plan in one."

### The mind-set: five required traits

1. **Dedicated** — commitment to carry through the emotional ups and downs of
   running the business.
2. **Disciplined** — the fix for the single biggest cause of blown-up
   accounts: not taking losses early enough, because the emotional pain of
   realizing a loss causes traders to freeze even when the plan says to cut
   it.
3. **Bold/decisive** — needed both to act when opportunities are abundant and
   to *not* trade when they are scarce.
4. **Flexible** — one of the most underrated traits; needed to shift a
   portfolio's net exposure (e.g., long to short) when the market regime
   flips.
5. **Humble** — near-100% win rates are unrealistic; even Warren Buffett has
   had bad investments (Salomon Brothers, US Airways, silver). Bad trades are
   feedback, not personal failure — "if there were no losses, no one would
   need to insure and then TOMIC would be out of business."

**Have worst-case scenarios planned in advance** — a checklist mentality, like
a commercial pilot's emergency checklist. Case study: Captain Chesley
Sullenberger's Hudson River ditching (US Airways Flight 1549, Jan 15, 2009) —
because he had trained for emergencies and had a plan, he executed it under
pressure and saved everyone aboard. A trading plan gives you scenarios mapped
out in advance so you act instead of freezing.

### Process over outcome

Framing question: is it better to stick to a process, or go with your gut? "It
is better to be lucky than to be good" — but luck doesn't hold indefinitely.
Worked blackjack illustration: player has 18, dealer shows a 6 (dealer likely
to bust); correct play is to stay, but the player hits, draws a 3, and wins
with 21 — a lucky but statistically bad decision. Judge decisions by whether
the odds justified the risk, not by the single-instance outcome. Explicit
time-horizon framing: **"Over the short term, process takes precedence over
outcomes, but in the long term the outcomes take precedence over the
process."** Short-run losses don't necessarily mean the process is wrong, but
consistently bad long-run outcomes mean the process itself must be revised.

**Checklists save lives — the case for process discipline.** Dr. Peter
Pronovost's five-item central-line catheter checklist (wash hands, full
barrier precautions, chlorhexidine skin prep, avoid certain insertion sites,
remove unnecessary catheters) cut a group of Michigan hospitals' ICU
catheter-infection rate by 66% in one year, reaching zero per 1,000
catheter-days versus a 5.2 national average — saving an estimated 1,500+
lives and nearly $200 million against a $500,000 program cost. Applied
conclusion: a checklist-driven process for trade decisions similarly protects
and grows capital. TOMIC has a checklist for each function (trade selection,
risk management, trade execution — see the per-chapter checklists in
`risk-management-and-position-sizing.md` and `market-making-techniques.md`).
Framing line: **"You are the casino, not the gambler."**

### Questions every trading plan should answer

Reproduced in full — this is the direct, reusable checklist:

- What is the goal of your TOMIC?
- What markets are you going to trade?
- Which strategies are you going to use?
- What are the conditions needed to put on a trade?
- What are the conditions that will make you close a trade?
- What are your risk management parameters?
- How are you going to execute the trades?

**Expanded follow-up questions per category:**

- **Goals** — Is TOMIC meant to replace current income? Produce a consistent
  20% annual return? Serve as a learning tool? Expected to always produce
  positive returns regardless of market conditions?
- **Strategies** — Which strategies will be used? Theta-positive only, or both
  theta-positive and theta-negative? Primarily iron condors, butterflies,
  calendars? What are your three most comfortable strategies, and under what
  conditions do you use them? Which strategies should be avoided, and when?
- **Entry parameters** — for each chosen strategy, what specific conditions
  must be met to enter?
- **Exit parameters** — what winning or losing conditions trigger an exit?
- **Risk management** — what conditions trigger an adjustment? What safety
  limits are set? (E.g.: what do you do if a position loses more than 2% of
  portfolio equity? What do you do if the portfolio loses more than 6% in a
  month? — see `risk-management-and-position-sizing.md` for the full
  quantitative treatment of these thresholds.)
- **Trading journal** — what information will the journal capture? Is it
  sufficient for a meaningful after-action review? Will dedicated software be
  used?

Closing guidance: "No trading plan is set in stone, but it is the first
'stone' that you will need to build a successful TOMIC." §5 below (Chapter 10)
walks through a complete worked example of a plan built on exactly these
questions.

---

## 3. Trading Infrastructure

Infrastructure = the back-office elements needed to actually implement TOMIC:
risk capital, broker, trading platform, analytical software, portfolio
margin, information sources, dedicated space, and backup plans.

### Risk capital and experience levels

TOMIC is explicitly framed as a **scalable business** — it can start small and
grow without changing its fundamental model; what changes with scale is the
operator's *skill*. Minimum starting capital cited: **as little as $5,000**;
start small and add capital as experience and consistent profitability
accumulate.

**Four operator experience levels** (these define appropriate risk-capital
scale and management style):

- **Level 0 — Beginner**: learning basic mechanics (placing/removing orders).
  Should trade a small real-money account (not a paper account — see below)
  with small lots.
- **Level 1 — Intermediate**: good grasp of options basics and strategy
  "anatomy" (butterflies, condors, calendars, diagonals); has some
  trade-selection judgment. "Knows enough to get in trouble, and enough to
  get out of trouble most of the time."
- **Level 2 — Semiprofessional**: good mastery of strategies and when to apply
  each; skilled at trade management/adjustment; manages TOMIC part-time
  (has another job or is retired) but a meaningful share of income derives
  from it. "Master at managing trades."
- **Level 3 — Professional**: operates TOMIC for a living; manages the entire
  portfolio (portfolio-level greeks, not just per-position greeks) — "like a
  general managing the entire battlefield." Notable: professional-level
  returns are **not necessarily higher** than semipro returns, but are **more
  consistent** — portfolio-level management smooths peaks and valleys.

**On paper trading:** brokers and the CBOE offer simulated accounts, useful
for learning a platform's *mechanics* but explicitly **not useful for
learning how to operate TOMIC**, because the psychological stress of real
money is fundamentally different from paper money. Recommendation: even
beginners should trade a real-money account, just a small one.

### Choosing a broker and trading platform

TOMIC is a one-person operation with no trading desk — the operator is
simultaneously trader, underwriter, chief executive, and "the janitor of the
entire company." A good platform saves time and prevents costly execution
errors.

**Broker-selection criteria** (overall fit — distinct from the per-order
routing criteria covered in `market-making-techniques.md`):

1. **Option specialist** — a broker that specializes in options, not one that
   merely allows options trading, since this affects both tools and margin
   terms.
2. **Understanding of complex order margin** — e.g., correctly margining an
   iron condor as one side's worth of margin, not both verticals, since only
   one vertical can lose at a time.
3. **Customer service.**
4. **Reputation** — a broker unlikely to fail; confirm FINRA and SIPC
   membership.
5. **Trading platform** — a good online interface for options trading.
6. **Trading desk** — a live desk to call when the platform or internet is
   down.

**Trading-platform checklist:**

1. Trade analysis tools (graphical risk-graph plotting).
2. Charts for the underlying.
3. Ease of use (most brokers offer a paper-trading version of the UI to test
   before committing).
4. Customizable layouts.
5. External links to Excel (not a must-have, but useful for pulling real-time
   data into custom calculations and monitoring).

Third-party, broker-agnostic platforms (named: Obsidian, Derivix, Microhedge,
Real Tick) become worth considering above roughly **$1 million** in account
size.

### Portfolio margin

**Reg-T margin** is the default/near-universal methodology and was the only
option available to retail accounts before 2007. **Portfolio margin (PM)**
became available to some retail accounts after 2007, subject to broker-set
minimums. Reg-T margins each position individually and sums the results; PM
instead **stress-tests the entire portfolio** and bases the requirement on the
stress-test outcome, so offsetting/hedged positions can require dramatically
less margin.

**Worked example — married put, Reg-T vs. PM** (long 100 sh AAPL @ $330 + long
1 put, Oct 320 strike @ $18):

- Reg-T: 50% of equity cost ($33,000) = $16,500, plus 100% of put premium
  ($1,800) → **$17,300 total.**
- PM: max loss if stock falls 15% = $4,950, offset by the put's theoretical
  gain of $3,950 → net = $1,000 → **$1,000 total.**
- **$16,300 of capital liberated** under PM with no change to the position's
  actual risk.

Caveats: a conservative broker may apply additional "haircuts" beyond
standard PM rules (e.g., for sector overconcentration). Having PM available
doesn't mean using it to the maximum — always actively track total exposure.
**Recommendation: beginners should use the more conservative Reg-T standard**
until skilled enough at whole-portfolio risk management to responsibly handle
PM's added leverage. (TOMIC 1.0's worked example in §5 deliberately stays on
Reg-T for this reason.)

### Information resources and analytical tools

Framing: easy to get information-overloaded. Useful sites named: bloomberg.com,
finance.yahoo.com, seekingalpha.com, stocktwits.com, thestreet.com,
theflyonthewall.com, tradethenews.com, livevol.com, cboe.com, ivolatility.com
— a mix of free and paid; choice depends on trading style/products.

On broker-provided Greeks: these depend on the broker's chosen pricing model
(some omit dividends), which may matter for sophisticated traders — a reason
to consider a third-party data provider whose model assumptions you trust
more. Skew/term-structure tools named: livevolpro.com, ivolatility.com.
Backtesting/simulation tools (more useful for systematic than discretionary
traders): ThinkorSwim (broker-integrated) and Optionvue (standalone).

### Dedicated space

Argues against the "I can trade from anywhere with a laptop" mindset for
anyone trading for a living. A dedicated workspace should be: quiet, free of
interruptions, equipped with high-speed internet, comfortable, and calm.

### Backup plans

For anyone trading for a living, redundant systems are essential:

- Redundant internet connections (cable, cellphone, and/or phone-line
  providers).
- Battery backup for the computer.
- **Use at least two brokers.**
- **Use at least two computers** — a primary desktop plus a backup notebook.
- Program the broker's trade desk number into speed dial in case the trading
  platform fails.
- **Maintain a futures account** to buy/short S&P 500 futures as an emergency
  hedge — know how many S&P 500 deltas the portfolio holds so you can quickly
  "go flat" via futures if needed.
- Have a backup physical location (Starbucks, a library, a hotel, an airport
  lounge — anywhere with internet) in case the primary office becomes
  unusable (burst pipes, gas leak, power outage, A/C failure).

"Having a backup plan is important even though you probably won't need to use
it, but occasionally you will be glad you have one."

### How much capital does it take to trade for a living? (Ch.13 lesson)

A distinct, more personal capital calculation than the "risk capital" scaling
above — this is about funding a full-time trading livelihood, not just
funding a trading account:

1. Know your annual living expenses (example: $60,000/year).
2. Save **at least two years of living expenses** liquid before starting
   full-time (example: $120,000).
3. Know your historical average trading return from part-time trading
   *first* — the text explicitly requires prior track record before going
   full-time (example trader: 2%/month on Reg-T margin over two prior years).
4. Realistic annualization: 2%/month compounds toward ~24%/year only if fully
   invested; realistic capital utilization is **40–60%** (the example uses
   50%).
5. Required working capital: to generate $5,000/month at 2%/month you'd need
   $250,000 fully invested — but at 50% average deployment, required working
   capital doubles to **$500,000**.
6. **Total capital needed to trade for a living (worked example): $120,000
   (savings) + $500,000 (working capital) = $620,000.**

Self-assessment after two years: covering expenses *and* growing savings =
doing very well; covering expenses with savings flat = doing fine; savings
depleted and expenses uncovered = seriously reconsider whether trading for a
living is right for you — and if still determined to continue, the explicit
recommendation is to **hire a coach and reread the book.**

### Vacation discipline (Ch.12 lesson)

Operational rule that belongs with infrastructure/process, not risk math:
**go flat before vacation** unless positions are genuinely long-term and need
no active monitoring — assume no reliable internet will be available. If
going fully flat isn't feasible, **arrange a trading partner** to manage the
portfolio while away, rather than trying to manage it remotely. "It is no fun
to be on vacation and trade at the same time. That is why it is called a
vacation."

---

## 4. Learning Processes: The Feedback Loop

Opens with a Darwin paraphrase on adaptability. A successful TOMIC manager
must learn and adapt as conditions change; every durable business (Coca-Cola,
GE, Apple) survives long-term by acting on feedback. Three elements make up
TOMIC's learning process: a trading journal, a sounding board, and a
continuing education plan.

### The trading journal

"The trading diary is your black box recorder" — designed purely to provide
feedback and improve the business, the same way an airplane's black box
exists to prevent recurrence of a failure, not for dramatic reporting.
Recommended practice: a real-time-linked Excel spreadsheet tracking open
TOMIC positions; analyze results monthly, quarterly, and annually against a
chosen benchmark index.

**Trading-journal review questions (reproduced in full):**

1. How many trades did you enter this month, quarter, and year?
2. How many trades were profitable?
3. How many were losing trades?
4. What was your win rate?
5. What were your average days in the trade?
6. How much was your average win?
7. How much was your average loss?
8. How much did you win or lose on average per trade?
9. What is your average yield (realized profit / margin used) per trade?

**Worked monthly example (the book's "TOMIC" fund):**

- 9 losing trades, total losses $(15,445), average loss $(1,716).
- Win ratio = **94%**.
- Total capital risked = **$1,833,878**.
- Average days in trade = **26**.
- Average monthly yield = **3.6%** ($66,417 / $1,833,878).
- **Annualized yield = 63.8%** (via the compounding formula below, not naive
  multiplication).

**Win rate isn't everything on its own.** Illustrative comparison: if win
rate fell from 94% to 90%, is that necessarily worse? Not if the loss/win
size ratio improves enough — the book works an example where at 94% win rate
the $loss/$win ratio is 3.2, but at 90% win rate it falls to 1.0 (e.g.,
average loss $500 vs. average win $500), and the **expected payout per trade
actually rises from $0.75 to $0.80** despite the lower win rate. Judge
performance on the joint combination of win rate *and* the loss/win size
ratio (expected value), never on win rate alone.

**Tie the journal back to the plan:** the journal is how you check actual
performance against the plan's stated targets (in the worked example, a
stated goal of 2–4% monthly return, with 3.6% realized confirming the goal
is being hit — a miss would instead signal a need to adjust approach).

**Correct annualized-yield formula** (a commonly-made error the book flags
explicitly — do not annualize by dividing period yield by days held and
multiplying by 365):

```
Annualized yield = (1 + period_yield)^(365.25 / days_held) - 1
```

This is the formula behind the 63.8% figure above (from a 3.6% monthly yield
over a 26-day average holding period).

### Sounding board: trading group and/or coach

Trading is "a lonely profession"; staying grounded requires outside feedback.
Watching CNBC talking heads is explicitly **not** being part of a trading
group. Two named mechanisms:

**Questions to ask when choosing a trading group:**

- What are the goals of the trading group?
- How will interactions happen — in person, online, by phone/chat tool?
- How often will the group meet? How many members?
- What are the members' experience levels? If everyone is a novice, is this
  "the blind leading the blind"? If experience varies, will more experienced
  members actually share with less experienced ones?
- What do *you* bring to the group?
- Does the group keep a meeting log (and can you review past logs)?
- Do members pool resources? Does the group have a coach?

**Questions to ask when hiring a trading coach:**

- What can I learn from this coach? Can they provide references?
- How available are they — how easily can you reach them if you get in
  trouble? How much weekly interaction time will you get, and via what
  medium (e.g., WebEx, GoToMeeting)?
- Does the coach know enough to actually challenge you and push improvement?
- Is the coach an individual or part of a larger organization? Do they run
  "student" trading groups you could join?
- Does the coach still actively trade real money, and how is their
  performance? How good are their communication skills?

### Continuing education

Every skilled profession (doctors, dentists, lawyers, engineers) requires
ongoing education; TOMIC managers should do the same via books, seminars, and
classes. Named example coaching service: **OptionPit.com** (see the
extraction note for Appendix C for the full service-tier breakdown; its
stated three pillars — Trade Structure, Risk Management, Efficient Use of
Capital — mirror TOMIC's own Trade Selection / Risk Management / Trade
Execution framing). Book recommendations are catalogued in the extraction
note for Chen/Sebastian's Appendix A, organized by skill level from beginner
through advanced/mathematical.

---

## 5. Operating the Business End-to-End: TOMIC 1.0 from A to Z

Chapter 10 ties together everything above (and the strategy/risk material in
the other reference files) into one concrete worked example — a specific
sample portfolio the authors call **"TOMIC 1.0."** It is explicitly one
example among many possible configurations; every trader's actual TOMIC will
be unique to their own comfort level and evolve with skill.

Opening framing (via a sales-book analogy): you can't fully learn to trade
without actually trading repeatedly — consistency and profitability come from
volume of practice, not just study ("It is like being a heart surgeon: the
more operations you perform, the better you become").

### Step 1 — Write the trading plan

Answering the §2 questions concretely for TOMIC 1.0:

- **Goals**: framed as a *learning/conditioning* portfolio. Do not lose money
  over any 12-month period; target annual absolute return > 10%, with a
  monthly goal of ~1% return on total capital.
- **Markets**: SPX, RUT, NDX, RTH, OIH, AAPL, CAT, EXC, MCD, WMT (10 named
  markets across indexes, ETFs, and equities).
- **Strategies**: a deliberately limited starter set — vertical spreads
  (credit and debit), iron butterflies (and broken-wing butterflies), iron
  condors (and unbalanced condors), calendar spreads, ratio spreads. (Full
  construction/adjustment detail for each is in `spreads-and-combinations.md`
  and `income-strategies.md`.)
- **Risk management parameters**:
  - Maximum loss per trade: **2%** of capital.
  - Maximum portfolio loss per month: **6%**.
  - Sector concentration limit: **no more than 20%** in any one sector
    (stricter than the general 25% guideline used elsewhere in the book).
  - Stay in cash if conditions favor no trade — never force a trade.
  - Trade duration: less than 90 days.
- **Execution**: an online broker specializing in options with an easy
  interface for complex orders. **Portfolio margin is explicitly not
  required for TOMIC 1.0** — a Reg-T account suffices at this scale.
- **Infrastructure setup**: start with **$100,000** capital; keep an Excel
  trading log; primary + backup internet connections; a laptop as a power-
  failure hedge; broker phone/account numbers programmed into your cellphone
  for emergency phone-in access.

### Step 2 — Execute the trading plan

Per-trade risk cap on $100,000 capital: **$2,000 max risk per trade** (the 2%
rule). Target cadence: **at least three trades per month**, conditions
permitting.

**Worked example — AAPL 10-point vertical put spread:**

- Reg-T margin required (= the trade's theoretical max loss): $9,010.
- Credit received after commissions: $990.
- Loss-exit rule: **150% of credit received** = $1,485 (1.49% of the
  $100,000 fund — within the 2% cap).
- Outcome in the example: closed for a **$710 profit**, having hit a stated
  profit target (~$693).
- General principle: know both your loss exit and your profit exit *before*
  entering, and confirm entry conditions are appropriate first.

**Building the portfolio:**

1. Follow all monitored markets daily; assess the best available trade in
   each given current conditions (directional opinion, plus tracking implied
   and historical volatility per market).
2. Maintain a running "List of Best Available Trades."
3. From that list, select trades to build a balanced portfolio appropriate
   to the current market environment.

**Example portfolio metrics:**

- No single trade's max loss exceeded $2,000 (2% of AUM).
- **Portfolio-level circuit breaker**: if the portfolio loses more than 6% in
  the month, close all trades, go flat, reassess, and restart fresh the
  following month — the whole-portfolio implementation of the 2%/6%
  "sharks and piranhas" rule (see `risk-management-and-position-sizing.md`
  for the full rule).
- Total target win for the example portfolio: $3,530 (4% return on AUM).
- Average days-to-expiration if held to expiration: 36 days; realistic
  average days-in-trade in practice (trades usually close before expiration):
  25–30 days.

### Step 3 — Manage and rotate the portfolio (ongoing)

- **Exit discipline**: once a trade hits its exit target (win or loss), close
  it — "when you hit your profit target, close the trade. It locks in
  profits and reduces your exposure." Never hold past target hoping for more,
  and never hold past the loss trigger hoping for a recovery.
- **Trade replacement**: once a position closes, return to the "best
  available trades" list and place the next-best candidate, keeping the
  portfolio continuously working — **except** when the environment is
  hostile and no good trades are available, in which case do not force a
  replacement trade.

### Step 4 — Close the feedback loop

1. Write the trading plan in as much detail as possible (goals, risk
   parameters, strategies, entry/exit rules).
2. Execute the plan.
3. Keep a detailed trading log on every trade (§4's Trading Journal
   practice).
4. Review performance at month-end and identify what to improve next month.
5. Repeat continuously.

---

## 6. Closing Framing (Ch.15)

The book's final chapter restates the full value chain one last time as the
checklist to keep returning to:

- **Primary functions**: Trade selection, Risk management, Trade execution.
- **Supporting functions**: Trading plan, Trading infrastructure, A process
  for learning.

It reiterates that understanding volatility (see `greeks-and-volatility.md`)
is essential to an edge, and that in practice most traders converge on a
small subset of strategies used most of the time — the authors name their own
core five (mirroring TOMIC 1.0's starter set above): **vertical spreads, iron
condors, butterflies, calendar spreads, and ratio spreads.**

Candid closing note: the framework "seems simple enough" but "this business
is not for everyone" — most readers will set it aside without following
through. For readers who like the philosophy but don't want to do the
underwriting/risk-management work themselves, the explicit alternative is to
**seek out funds with a similar investment philosophy and outsource the
work**, rather than running TOMIC personally. For those who do build their
own: "This is the beginning of your journey... Never stop learning and
improving your skills."

---

## Cross-references

- Per-trade and per-strategy risk math (the 2%/6% rules, sector-diversification
  limits, black-swan/"units" hedging, adjustment rules) →
  `risk-management-and-position-sizing.md`.
- Strategy construction and selection mechanics referenced throughout this
  file (vertical spreads, iron condors, butterflies, calendars, ratio
  spreads) → `spreads-and-combinations.md` and `income-strategies.md`.
- Order-routing, broker fill-quality mechanics, and market microstructure
  referenced under Trade Execution → `market-making-techniques.md`.
- Volatility concepts referenced throughout (mean reversion, three-dimensional
  volatility, skew, term structure) → `greeks-and-volatility.md`.
