Source: Chen/Sebastian, *The Option Trader's Hedge Fund*, Chapter 10 "Operating the Business: Putting Together TOMIC 1.0 from A to Z", physical pp. 148–157.

Note: this chapter closes **Part II ("Implementing the Business")**. The text ends with "Part III: Lessons from the Trading Floor," marking the transition into Part III (Chapters 11–14, the "lessons from the trading floor" chapters).

This chapter is an **end-to-end walkthrough tying together Chapters 1–9** — captured below as a sequential process/checklist rather than a topic list, per the task's instruction.

## Overview / Introduction (p.148)

Opens by referencing David Sandler's sales book *You Can't Teach a Kid to Ride a Bike at a Seminar* as an analogy: you can't fully learn to trade without actually trading repeatedly — consistency and profitability come from volume of practice, not just study.

Recaps the book's structure so far: reviewed the "ingredients" (the five most-used trades from Ch.9 — vertical spreads, calendar spreads, iron condors, butterflies, ratio spreads); this chapter shows how to combine them into a working portfolio ("recipe"). Restates the three insurance-company/TOMIC success factors from Ch.1 (**Trade selection, Risk management, Trade execution**) and the three supporting structures (**A trading plan, Trading infrastructure, A process for learning**).

Introduces the chapter's running example: a specific sample portfolio called **"TOMIC 1.0"** — explicitly framed as one example among many possible configurations; every trader's actual TOMIC portfolio will be unique to their own comfort level and style, and will evolve as skill progresses.

## Sequential Walkthrough: Building TOMIC 1.0

### Step 1 — Write the Trading Plan (heading: "Trading Plan")

Every TOMIC starts with a trading plan (per Ch.5) answering:
- What is the goal of TOMIC 1.0?
- Which markets will I trade?
- What strategies will I employ for each market?
- What are my risk management parameters?
- What is the best way to efficiently execute the trade?

**TOMIC 1.0's concrete answers, given as a worked example:**

- **Goals**: TOMIC 1.0 is explicitly framed as a *learning/conditioning* portfolio for developing the insurance-company management framework. Stated profitability goals: **do not lose money over any 12-month period**, target an **annual absolute return greater than 10%**, with a **monthly goal of ~1% return on total capital.**
- **Markets**: 10 named markets across indexes, ETFs, and equities: **SPX, RUT, NDX, RTH, OIH, AAPL, CAT, EXC, MCD, WMT.**
- **Strategies**: a deliberately limited starter set (with named variations):
  - Vertical spreads (credit and debit)
  - Iron butterflies (and their variation: **broken-wing butterflies**)
  - Iron condors (and their variation: **unbalanced condors**)
  - Calendar spreads
  - Ratio spreads
  - Table 10.1 ("Strategy Cheat Sheet") is referenced as mapping these five strategies to the conditions under which each should be used — table contents not machine-extractable beyond this description; conditions for each of these five strategies are given in full detail in Ch.9's extraction note.
- **Risk management parameters for TOMIC 1.0** (concrete numeric policy, echoing Ch.3's general rules):
  - Maximum loss allowed per trade: **2%**.
  - Maximum portfolio loss allowed per month: **6%**.
  - Portfolio concentration limit: **no more than 20% in any one industry sector** (note: stricter than Ch.3's general 25%-per-sector guidance).
  - Stay in cash if conditions are not favorable for any trade (no forced trading).
  - Trade duration: **less than 90 days.**
- **Execution**: use an online broker specializing in options, with an easy interface for complex order types (verticals, condors, butterflies, calendars). **Portfolio margin is explicitly not required for TOMIC 1.0 — a Reg-T margin account suffices** at this stage/scale.
- **Setup / infrastructure checklist for TOMIC 1.0** (echoing Ch.6):
  - Start with **$100,000** capital.
  - Keep a trading log in Excel.
  - Use a cellphone/cable Internet connection with the other as backup.
  - Use a laptop to trade, as a hedge against a power failure.
  - Program the broker's phone number and account number into your cellphone for emergency phone-in access if online access fails.
  - Figure 10.1 (referenced, an example trading-log entry for an AAPL vertical spread) illustrates the log format.

### Step 2 — Execute the Trading Plan (heading: "Executing the Trading Plan")

Starting capital: **$100,000**, monitoring the 10 named markets. Per-trade risk cap: 2% of $100,000 = **$2,000 maximum risk per trade.** Target cadence: **at least three trades per month**, conditions permitting.

**Worked example — AAPL vertical put spread (10-point width), referencing Figure 10.1:**
- Reg-T margin required: **$9,010** — this is the trade's theoretical maximum loss if held with no adjustment, and is checked against and confirmed within TOMIC 1.0's risk parameters.
- Credit received (after commissions): **$990.**
- **Maximum-loss exit rule applied**: set at **150% of credit received** = **$1,485** loss trigger — representing **1.49% of the $100,000 fund**, within the 2%-per-trade cap.
- Profit-side exit target was also set (implied from the outcome): the trade was actually closed for a **$710 profit**, having "hit your target" (a stated profit exit point of **$693** is referenced in the surrounding text as the win-side trigger).
- General principle drawn from the example: know both your loss exit and your profit exit *before* entering, and always confirm entry conditions are appropriate first.

**Portfolio construction process:**
1. Follow all monitored markets daily; assess the best available trade in each given current conditions (have a directional opinion; track implied and historical volatility per market to judge trade quality).
2. Maintain a running table of best available candidate trades — referenced as **Table 10.2, "List of Best Available Trades."**
3. From that candidate list, select trades to build a **balanced portfolio** appropriate to the overall market environment — referenced as **Table 10.3, "TOMIC 1.0 Portfolio Example."**

**TOMIC 1.0 example portfolio metrics** (as narrated, since Table 10.3's literal contents aren't machine-extractable):
- No single trade's maximum loss exceeded **$2,000 (2% of AUM)** — consistent with the per-trade risk cap.
- **Portfolio-level circuit breaker**: if the portfolio loses more than **6%** in the month, **close all trades and go flat**, then reassess strategy and restart fresh the following month (directly implements Ch.3's "piranha" monthly stop-loss rule at the whole-portfolio level).
- Total target win for the example portfolio: **$3,530**, representing a **4% return on AUM.**
- Average days-to-expiration across the portfolio (if held to expiration): **36 days** — but noted that in practice, trades are closed before expiration, and this type of portfolio's realistic **average days-in-trade is 25–30 days.**

### Step 3 — Manage and Rotate the Portfolio (ongoing process)

- **Exit discipline**: once a trade hits its exit target (win or loss), close it — "when you hit your profit target, close the trade. It locks in profits and reduces your exposure." No holding past target hoping for more, and no holding past the loss trigger hoping for a recovery.
- **Trade replacement / recycling**: once a position is closed, return to the "best available trades" list and select and place the next-best candidate, keeping the portfolio continuously working. **Exception**: if the environment is hostile and no good trades are available, do **not** force a replacement trade — wait for favorable conditions.

### Step 4 — Build the Feedback Loop (closing guidance)

To become proficient, you must actually trade repeatedly — analogy given: "It is like being a heart surgeon: the more operations you perform, the better you become." Concrete closing recommendations:
1. Write the trading plan with as much detail as possible (goals, risk parameters, strategies, entry/exit rules).
2. Execute the plan.
3. Create a feedback loop: keep a detailed trading log/notes on every trade (per Ch.7's Trading Journal practice).
4. At month-end, review performance and identify what to improve the following month.
5. Repeat this cycle continuously to become a better TOMIC manager.

## Notes on completeness

The task's known-headings list ("Trading Plan"; "Executing the Trading Plan") matches the two explicit headings actually present in the source text; this note captures both fully, structured as the sequential walkthrough the task instructed (rather than a flat topic list), since the chapter is explicitly a step-by-step, tie-everything-together example. Three referenced tables (10.1 "Strategy Cheat Sheet," 10.2 "List of Best Available Trades," 10.3 "TOMIC 1.0 Portfolio Example") and one figure (10.1, an AAPL vertical-spread trading-log entry) are OptionVue/Excel-style visual exhibits not machine-extractable as text from the PDF; their substance has been fully reconstructed from the surrounding narrative, which describes their contents in enough detail (specific dollar figures, percentages, and structure) that no numeric content appears to be missing. The chapter's closing line ("Part III: Lessons from the Trading Floor") marks the Part II→Part III transition and has been noted for context ahead of Chapters 11–14.
