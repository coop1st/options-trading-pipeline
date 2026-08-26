# Risk Management and Position Sizing

Synthesized from both books' risk-management material. **Bittman** (market-maker
perspective) supplies the quantitative, Greeks-based machinery for measuring and
neutralizing *position*-level risk. **Chen/Sebastian** (retail-hedge-fund
perspective) supplies the *portfolio*-and-business-level rules: money management,
diversification, black-swan insurance, and a set of hard-won trading-floor
lessons about discipline. The two layers are complementary — Bittman tells you
how much risk a given position actually carries and how to dial it down;
Chen/Sebastian tells you how much of your total capital any one position (or the
whole book) should be allowed to put at risk in the first place.

Primary sources: Bittman ch.10 "Managing Position Risk"; Chen/Sebastian ch.3
"Risk Management"; Chen/Sebastian ch.12 "Lessons from the Trading Floor on Risk
Management." Supporting sources: Bittman ch.1 (margin/leverage fundamentals),
Bittman ch.8 (delta-neutral risk reality), Chen/Sebastian ch.8 ("units"),
Chen/Sebastian ch.11 (tail-hedge timing), Chen/Sebastian ch.13 ("The Importance
of Good Exits," capital needed to trade for a living).

---

## 1. Foundations: Capital, Leverage, and the Subjective Risk-Tolerance Question

**Per Bittman** (ch.1) — every risk-management framework sits on top of basic
margin mechanics:

- `Account equity = Account value − Margin debt`. Because equity is smaller
  than account value in a margin account, a given percentage move in the
  underlying causes a *larger* percentage change in equity than in a cash
  account — this is leverage, and it is the reason margin positions carry more
  risk per dollar of committed capital than the same position paid in full.
- **Initial margin** is the equity percentage required to open a position;
  **minimum margin** is the floor that must be maintained. Falling below it
  triggers a **margin call**, forcing a deposit or a forced close. Worked
  example: stock bought at $50 with a $2,500 fixed margin loan falls to $35 →
  equity is $1,000 of $3,500 value (28.6%); if minimum margin is 35%, this
  triggers a call.
- Whether a given options strategy is "speculative" or "conservative" is
  substantially a function of how much equity supports it relative to its
  total risk — the same strategy can be either, depending on sizing.

**Per Bittman** (ch.10) — after all the quantitative machinery below, the
single most important input to any risk framework is not calculable at all:

> "How much of an adverse dollar (or percentage) swing can I tolerate and
> still trade rationally?"

No "scientific" universal risk limit exists. Position sizing, Greek limits,
and stop-loss placement all flow from this personal, subjective answer —
Chen/Sebastian's more prescriptive percentage rules (Section 6) are one
concrete way of answering it, not a universal law.

---

## 2. Calculating Position Risk with the Greeks

**Per Bittman** (ch.10). Position Greeks generalize the position-delta concept
(introduced for delta-neutral trading, see `greeks-and-volatility.md`) to
gamma, vega, and theta as well:

```
position risk (for a given Greek) = per-option Greek × 100 (multiplier) × number of contracts
```

summed across every leg of a multi-part position. **Rho is excluded** from
this chapter's risk framework — small short-term rate moves don't materially
affect short-term option positions.

Worked example (Table 10-1): 20 long 70 Calls (delta 0.535, gamma 0.059, vega
0.087, 7-day theta −0.310) →

| Position Greek | Value | Meaning |
|---|---|---|
| Position price | $5,640 | Capital committed |
| Position delta | 1,070 | Share-equivalent exposure — a $1 stock move ≈ ±$1,070 P&L |
| Position gamma | 118 | How much position delta itself shifts per $1 stock move |
| Position vega | 174 | $ P&L per 1-point IV change |
| Position theta | −620 | $ lost over the next 7 days if nothing else changes |

**Theta vs. vega as risk measures**: theta gives a firm, near-certain estimate
(time passes at a known rate), so it can be combined directly with a dollar
risk limit to decide how long to hold a position before a decay-driven loss
becomes unacceptable. Vega only tells you the *dollar impact* of a 1-point IV
move — not the likelihood or typical size of such a move, which requires
separately studying historic/implied volatility context. "Forecasting
volatility is an art, not a science."

**Risk of short options is asymmetric, not just sign-flipped.** The Greeks of
a long and short option are mathematically opposite, but the *practical* risk
is not simply mirrored: an uncovered short call carries **unlimited** risk;
an uncovered short put carries **substantial but bounded** risk (the
underlying can't go below zero). Real markets can gap 30%+ overnight on
unexpected news, so a short option's realistic risk exceeds simple modeled
assumptions. There is no uniform rule for "how many short options is too
many" — an individual, subjective judgment, which is exactly why Section 6's
portfolio-level percentage rules exist as a backstop.

**Delta-neutral is not risk-free.** Per Bittman ch.10's stock-hedged spread
example: adding a stock hedge to zero out delta only protects against price
moves *within a finite range* (roughly the spread's own strike range) —
outside that range the position still loses meaningfully, and gamma/vega/theta
are completely unaffected by the stock hedge (they must be managed
separately). Per Bittman ch.8, this generalizes further: short-volatility
delta-neutral positions carry unlimited risk from two distinct sources — rising
IV, and a sudden gap in the underlying. Worked example: a delta-neutral short-call
position hedged with 3,000 long shares lost a **net $18,000** on an overnight
gap from $42 to $49, despite having been "delta-neutral" at the close of the
prior session — the hedge only neutralizes small/instantaneous moves, not gap
risk, and gamma/vega exposure remains fully live throughout. (Full delta-neutral
mechanics: see `greeks-and-volatility.md`.)

---

## 3. Managing Directional Risk with Delta

**Per Bittman** (ch.10). For a directional position, the dominant risk is
delta, and the standard technique for a long-option position is to actively
trim/add around a target delta band rather than simply buy-and-hold:

- **Technique**: because stock prices move in a choppy pattern rather than a
  straight line, and long options have positive gamma (delta rises as price
  rises, falls as price falls), a trader can sell part of a long-call position
  when a rally pushes delta above a threshold, and buy back when a pullback
  drops delta below a lower threshold — keeping position delta roughly
  centered on a target throughout the trade.
- **Sizing formula**: `contracts to trade = |target delta − current delta| / (option delta × 100)`.
- Worked example ("Grace"): actively managing delta through a 16-day, 6-point
  choppy walk produced **$12,625 profit** vs. **$10,900 from naive buy-and-hold**
  of the same starting position — a $1,725 improvement, *but only because the
  path was genuinely choppy*. The technique underperforms buy-and-hold when
  prices trend with below-average volatility, and it is not risk-free: a sharp
  early drop would have forced buying *more* calls into a losing position
  under the same rules, with loss potential exceeding the original investment
  if everything ultimately expired worthless.

**Vertical spreads carry structurally lower risk than the equivalent outright
long option** — every Greek (delta, gamma, vega, theta) is reduced by adding
the short leg (Table 10-3: outright 70 Call position delta 1,070/gamma
118/vega 174/theta −620 vs. the 70-75 spread's 546/20/42/−170). This also
makes verticals more resilient in falling-IV environments specifically: in a
worked two-scenario comparison, an outright long call lost relative
performance when IV dropped (profit 1.03 vs. 1.29 with IV flat), while the
vertical spread actually profited *more* under the same IV decline (1.25 vs.
1.12) because its short leg partially offsets the long leg's vega exposure.
(Full spread construction/strategy detail: see `spreads-and-combinations.md`.)

**A position's risk profile is not static — it can flip sign entirely as
price moves.** The same 70-75 bull call spread that is bullish/long-vol/theta-negative
when the stock sits at the lower (long) strike becomes bullish-but-theta-positive/short-vol
once the stock reaches the upper (short) strike — a $5 move flipped gamma,
vega, and theta from positive to negative while delta stayed directionally
similar. Practical lesson: "if you do not know how your risks have changed,
you cannot react to changing market conditions within your pre-established
limits" — risk snapshots must be re-checked regularly, not assumed static from
entry.

---

## 4. Neutralizing Position Greeks

**Per Bittman** (ch.10). Sizing a Greek-neutralizing trade:

```
contracts needed = position Greek being neutralized / that option's individual Greek
```

(sign determines buy vs. sell), followed by an offsetting stock trade to
restore delta-neutrality given the option trade's own delta impact.

**Zero-interest-rate case**: neutralizing *any one* of gamma, vega, or theta
via the same option leg requires the *identical* contract quantity in all
three cases — when rates are zero (a case that applies generally to options
on futures), neutralizing one of these three Greeks automatically neutralizes
the other two as well. A trader doesn't need to choose which Greek to target.

**Positive-interest-rate case**: gamma and vega remain linked (same
neutralizing quantity for both), but **theta requires a different quantity** —
the theta/gamma/vega link breaks once carrying costs enter the picture. Why:
when a position carries a meaningful stock component, the net debit or credit
accrues real interest cost/income, and the position's residual theta (after
neutralizing gamma/vega) is explained almost exactly by that financing cost —
a positive theta offsets a debit position's interest expense; a negative theta
offsets a credit position's interest income. This interest-theta linkage only
applies when the position has a meaningful stock component; for stock-free
option combinations, theta must instead be reasoned about via its usual
inverse relationship with gamma/vega.

---

## 5. Establishing Risk Limits by Position Type

**Per Bittman** (ch.10), three position types call for three different
risk-limit approaches:

1. **Delta-neutral with a stock component**: set a limit on **gamma or vega**
   (not both — they're linked per Section 4), since theta "takes care of
   itself" via the interest relationship. Method: judge a "normal" IV move
   size from historic/implied volatility context, multiply by the position's
   vega to get a "normal" dollar swing, and compare that to your chosen
   dollar risk limit. Worked example: a $1,000 limit and a judged-"normal"
   3-point IV move implies a vega limit of 1,000/3 ≈ **333**.
2. **Delta-neutral without a stock component**: theta can't be tied to an
   interest calculation here, but is still mechanically tied to gamma/vega
   (opposite sign, same-expiration options). The real decision becomes
   strategic: net option buyer (profits from a big move/rising IV, pays
   theta) or net option seller (profits from decay, risks a big move/rising
   IV)? Set the vega or theta limit accordingly once that choice is made.
3. **Directional positions**: the dominant risk is delta — "how much delta
   can I take on?" is the first question, answered via individually-chosen
   **stop-loss points** (in $ amount, option price, or underlying price) set
   below the theoretical max loss, since few traders want to risk 100% of a
   long option's premium, and a losing short-option position's negative gamma
   makes losses accelerate as the market moves further against it (making
   stop-losses especially critical for short directional trades). Attempting
   to also manage gamma/vega/theta on a directional trade usually just
   perturbs delta further and is generally not worth the side effects —
   directional risk management should stay centered on delta first.

---

## 6. Money Management Rules

**Per Chen/Sebastian** (ch.3). TOMIC is explicitly framed as being in the
business of **risk-taking, not risk avoidance** — it profits by taking on
others' risk in exchange for premium, and the goal of risk management is to
avoid being blindsided by *unexpected* risk, not to eliminate the deliberate
risk the business is built on.

**Risk-management question checklist**, by trade lifecycle stage:

- *Before*: What is the risk/reward ratio? Probability of success? Maximum
  acceptable loss? Expected return and target profit? Does the trade maintain
  portfolio balance/diversification?
- *During*: Has the trade hit its maximum allowed loss? Its target profit? Is
  the reward of staying in worth the risk?
- *After*: Did you follow the risk-management rules? If not, why not?

**Five things TOMIC must do to manage risk**: (1) create a money-management
policy; (2) define a position-sizing policy; (3) maintain a diversified
portfolio; (4) adjust or exit trades that go bad; (5) buy portfolio insurance
against black-swan events. Sections below map directly to these five.

### The "Sharks and Piranhas" Heuristic

Attributed to Dr. Alexander Elder:

- **Shark threat** — one losing trade that takes a big bite out of the
  account (e.g., a single 35% equity loss) — financially and psychologically
  damaging.
- **Piranha threat** — many small losses that cumulatively overwhelm the
  account.

**Two core rules:**

1. **Never risk more than 2% of capital on any single trade** (guards against
   shark attacks).
2. **If the account loses more than 6% in any single month, stop trading for
   the rest of the month** (guards against piranha attacks). The 6% figure is
   explicitly called arbitrary — "your percentage could be 5%, 6%, 7%, 10%, or
   any percentage you can live with." The point is having *some* stop-loss
   discipline at the monthly/portfolio level.

### Position Sizing

Worked example (RUT iron condor, $2,000,000 AUM):

- 2% rule → max risk per trade = $40,000.
- Naive sizing: condor margin $1,000/contract → $40,000/$1,000 = 40 condors
  (assumes full margin is the realistic loss).
- **Refined sizing**: traders typically use a smaller *allowed* loss than the
  full margin (e.g., profit target 15% of margin, allowed loss 20% of margin
  → actual risk = $200/condor). $40,000 / $200 = **200 RUT condors** — 5x the
  naive figure, because realized per-trade risk is smaller than max
  theoretical loss.

**Does the 2% rule limit you to ~3 concurrent trades?** No — multiple trades
can be held simultaneously because not all trades are likely to go against
you simultaneously *unless they are correlated* (see Diversification below).
With 15–20 concurrent trades and an assumed 80% success rate, on average only
3–4 would go against you in a given month, making the 6% monthly threshold
statistically unlikely to be hit purely from position count.

### Adjusting Trades / Exit Discipline

Adjustments are made to *protect capital and minimize losses*, not to make
more money — applied only when a trade is going against you. **Closing the
trade completely is itself a valid adjustment**: "taking a loss early is
sometimes better than staying in a losing trade." The authors' stated
position: **trade selection matters more than trade exits**, but exits and
adjustments still matter a great deal — mastering entries, adjustments, and
exits together is necessary.

**Per Chen/Sebastian ch.13** ("The Importance of Good Exits") — this
principle is elaborated with two concrete rules that generalize across every
strategy in `spreads-and-combinations.md`:

- **Define two exit points before entry, always**: (1) the exit for when the
  trade is going against you, (2) the exit for when it's going in your favor.
  Football/defense analogy: entries are the offense, exits are the defense.
- **On losing exits**: take them without hesitation once triggered — hesitation
  (hoping for a reversal) can turn a small loss into an unrecoverable one.
  "The best loss is the first loss."
- **On winning exits**: predefine these too, since holding for "just a bit
  more" risks a reversal wiping out accumulated profit. **Recommended
  trigger: a percentage of margin** — worked example, an iron condor with a
  loss exit at 20% of margin and a gain exit at 15% of margin; once either
  threshold is hit, exit without exception. (A related staged-threshold rule
  — the iron condor's "Third-Third-Third" adjustment ladder at 1/3, 2/3, and
  full maximum loss — is covered in `spreads-and-combinations.md`.)

---

## 7. Portfolio Diversification

**Per Chen/Sebastian** (ch.3). Position sizing alone is insufficient if
positions are correlated: sizing five integrated-oil names (Exxon, Chevron,
BP, ConocoPhillips, Petrobras) at 2% each does not actually protect the
portfolio, since they move together.

**Explicit diversification rules:**

- Include at least **five sectors**.
- No single sector should exceed **25%** of the portfolio.
- Example diversified mix: **SPX, AAPL, GS, FCX, BP.**
- Combined with the per-position rule: no single position risks more than 2%
  of capital.

### Four Risk Levels (Macro to Micro)

| Level | Description | Example | Hedge |
|---|---|---|---|
| **Systemic** | Financial-system collapse dragging down the broader economy | 2008 Lehman collapse | Very difficult to hedge — even paper hedges (e.g., CDS backed by a firm like AIG) can fail if the counterparty fails. Suggested hedge: **real/physical assets** (physical gold and silver), not paper. |
| **Market** | Macro events hitting the entire market | 9/11, 2008 financial crisis | Can be hedged with options — portfolio insurance / index (unit) puts. |
| **Sector** | Events hitting one sector | Defense-spending cuts; a new tax on financial institutions | Reduce/hedge sector-specific exposure. |
| **Company** | Events specific to one company | Enron collapse; BP Gulf spill; loss of a key executive | Relatively easy to hedge with options on that name, plus diversification. |

---

## 8. Insuring the Portfolio Against Black Swan Events

**Per Chen/Sebastian** (ch.3, extended by ch.8 and ch.11). TOMIC should manage
catastrophic risk the way an insurer reinsures unwanted risk (the earthquake-reinsurance
analogy from ch.1): willing to bear normal market moves (e.g., ±5%), but should
"reinsure" risk beyond a defined catastrophic threshold (example given: a 25%
single-day market loss).

**Two named reinsurance instruments:**

1. Buy **out-of-the-money puts on the S&P 500** to protect against a large
   market downturn.
2. Buy **out-of-the-money calls on the VIX**, on the premise that a large
   S&P 500 drop causes a large VIX spike. The choice between (or blend of)
   the two depends on relative pricing of SPX puts vs. VIX calls.

### "Units" — Cheap, Nonlinear Crash Hedges

A **"unit"** is an inexpensive option with unpredictable/nonlinear Greek
behavior in a crash — cheap relative to the underlying's price level (roughly
$0.20 in SPY, $2.00 in SPX), with delta below 5 and little gamma/vega under
normal conditions.

**Why units behave nonlinearly in a violent down move**: standard
pricing-model assumptions (a roughly uniform IV increase across strikes) break
down in a real selloff — front-month options and downside puts gain far more
value than models predict, because a panicking market bids up cheap
protection while short sellers scramble to cover, in a reflexive,
self-reinforcing cycle (vega up → delta up → value up further as the market
keeps falling).

**Case study (May 2010 flash crash)**: a fund's May OEX butterfly was down
~10% going into the crash, but the fund's long OEX 505-put "units" (bought at
$1.20) rose to nearly $10 that day and $14.50 by the next close — a **1,200%+
return** — more than offsetting the butterfly's loss and turning the combined
position profitable overall.

**Practical sizing**: allocate roughly **5–10% of allocated trading money**
(not total account value) into units as a standing hedge against a book of
spread trades. Sizing goal: after adjusting for the expected volatility spike,
a 10% market drop should leave the combined position breakeven-or-better; a
20% drop should leave it profitable.

**Per Chen/Sebastian ch.8**, the same concept is given three explicit,
quotable rules (the "human risk" of shorting extremely cheap options, since a
$0.10 option that moves to $15.00 is a 1,500% loss that pricing models don't
anticipate):

1. **Never short options worth $0.10 or less.**
2. **If already short an option worth less than $0.10, buy it to close even
   if a commission applies to that closing purchase.**
3. **A hedge fund that sells premium should always be net long these
   "units."**

**Per Chen/Sebastian ch.11**, the timing discipline that makes units actually
work: buy tail protection *before* it's needed, because it becomes
unavailable or unaffordable exactly when you need it most. Quoting broker
Kevin Kennedy: **"Buy 'em when you can, not when you have to! Because when you
have to buy them, you can't!!!"**

Closing framing (ch.3): "by properly implementing units, you are willing to
bet that you will never have to sell your house because the market dropped
25%."

---

## 9. Trading-Floor Risk Lessons

**Per Chen/Sebastian** (ch.12), a set of standalone lessons on risk discipline
that don't reduce to a formula.

### Cash Is a Position

Cash is itself an active position choice, not the absence of one. Worked
comparison (Table 12.1): $10,000 traded in iron condors every month for a
year returned **7%**; the identical strategy but skipping one bad-setup month
(staying in cash) returned **13%** — nearly double, from that single decision.
Guidance: resist the pressure to trade when nothing attractive is available —
"if you do not like what you see, skip trading." Counter-caution: there is
usually *something* worth trading; if nothing looks good, that may mean your
knowledge base needs expanding rather than that no opportunity exists.

### The Card Game Value

A distinctive risk-sizing heuristic explaining why cheap options resist final
decay and why credit-spread sellers get burned holding to the bitter end.

**The illustration**: two men play a card game once — 100 cards, 99 worth $0,
one worth $1,000. Fair value = $10. If played *repeatedly*, a rational
operator charges only slightly above fair value (e.g., $11), since the law of
large numbers guarantees a long-run edge. But played only *once*, the odds are
identical yet there's no opportunity to earn back the loss through repetition
if the $1,000 card comes up — it would take far more than $11 to get someone
to actually agree to a single-shot version of this game.

**Mapping onto cheap options**: probability-based pricing models say a very
cheap option should be worth close to nothing, but such options persistently
hold a residual value of roughly **$0.10–$0.25** for an unusually long time.
The option seller is functionally the "house" — profitable over many
repetitions in theory, but any single option's life is a single "play," and if
that particular trade goes bad, there's no chance to "run it back" within that
contract. Worse than the card game: the seller typically faces
**undefined/open-ended risk**, unlike the game's fixed $1,000 payout.

**Practical rule**: exit credit spreads once they've decayed to the point of
trading purely on Card Game Value (stuck around $0.10–$0.25) rather than
waiting for full decay to zero — this frees capital for positions the pricing
model can still meaningfully value. "Credit spreads are a great way to make
money, but it takes only one bad draw to wipe you out. Don't get caught
playing cards."

### Over-Adjusting Disease

Anecdote-driven lesson: the harder skill after proper trade setup is knowing
when *not* to adjust. **"Over-adjusting disease"** — adjusting a position that
isn't actually in trouble, merely *near* a point where it might start to be —
is described as killing more trades than the market itself, because every
adjustment extends time-in-trade (more commission, more exposure to a genuine
multi-standard-deviation move). Small moves can often self-correct without
adjustment; it's the large, sudden multi-standard-deviation moves that
actually kill trades, and adjustment often can't prevent that damage anyway.

**Practical decision test**: mentally push the position forward 3 days, then
ask whether you'd likely make money or break even if (a) the underlying stays
here, (b) rallies one standard deviation, or (c) falls one standard deviation.
**If the answer is yes for at least 2 of the 3 scenarios, do nothing.**
Otherwise, consider an adjustment.

### Weekend Theta Decay

Common retail mistake: expecting linear weekend decay (Friday-to-Monday theta
credited as if 2.5 calendar days passed). **Weekend theta is actually
front-loaded into Friday's close.** If prices didn't already reflect this,
arbitrageurs would sell premium Friday afternoon and buy it back Monday
morning to harvest 2.5 days of decay for one overnight of real risk.

**How market makers prevent this**: they begin decaying the entire weekend
into prices as early as Thursday midday, by advancing their pricing software's
"theoretical day" forward (lowering theoretical IV, or advancing the
theoretical expiration date) — by Friday's close, the system is effectively
set to 4 p.m. Sunday, leaving only one genuine overnight of real decay still
priced in.

**Practical rule**: if a position is already near its exit target on a Friday
afternoon, exit then — don't hold over the weekend expecting extra decay,
since it isn't there to capture (it's already priced out), and most retail
platforms don't model this correctly. "There is no 'weekend edge.' There is
only the trader's edge."

### When Is the Time to De-Risk Your Portfolio?

De-risking = taking action to lower portfolio risk, usually by reducing
positions/exposure. **Six explicit trigger conditions:**

- The portfolio is so volatile you can't sleep at night.
- The market environment has changed and you don't have a read on the new
  environment.
- You have hit your portfolio trading loss limits.
- Your trading model is not working in the current market environment.
- You need to rebalance the portfolio.
- Your positions have hit their target profits.

"Know when to pull the parachute cord. Don't hesitate in pulling it. It is
better to be safe than sorry."

### How to Trade When You Go on Vacation

Core rule: **go flat before vacation**, unless positions are genuinely
long-term and need no active monitoring — assume no reliable connectivity will
be available, and don't try to trade and vacation simultaneously. If going
fully flat isn't feasible, **arrange a trading partner** to manage the
portfolio rather than attempting to manage it remotely.

---

## 10. Capital Sufficiency to Trade for a Living

**Per Chen/Sebastian** (ch.13). A money-management question distinct from
per-trade sizing: how much total capital is needed before attempting to trade
options full-time, as a business. Worked calculation:

1. Know annual living expenses (example: **$60,000/year**).
2. Save **at least two years'** worth liquid before starting (example:
   **$120,000**).
3. Know your historical average return from prior part-time trading — the
   text explicitly requires this track record before going full-time (example:
   **2%/month** on Reg-T margin, over two prior years).
4. Realistic annualization accounts for capital utilization typically being
   only **40–60%** deployed (not 100%) — example assumes 50%.
5. **Required working capital**: to generate $5,000/month at a 2%/month
   return needs $250,000 if fully invested, doubling to **$500,000** at 50%
   deployment.
6. **Total capital needed**: $120,000 (savings) + $500,000 (working capital) =
   **$620,000**, in this worked example.

**Self-assessment after two years**: covering expenses *and* growing savings
is doing very well; covering expenses while savings stay flat is doing fine;
depleted savings with expenses uncovered is a signal to seriously reconsider
whether trading for a living is the right path — the explicit fallback
recommendation is to hire a coach and revisit the fundamentals rather than
push forward undercapitalized.

---

## Cross-References

- Full Greeks mechanics (delta/gamma/vega/theta/rho definitions, position
  Greeks, delta-neutral trading theory) — `greeks-and-volatility.md`.
- Strategy-specific risk/exit rules (iron condor "Third-Third-Third" loss
  ladder, butterfly wing-width guidelines, calendar spread 10% stop) —
  `spreads-and-combinations.md`.
- Assignment risk and put-call-parity-based assignment tests — `market-making-techniques.md`.
- Portfolio margin mechanics, broker/infrastructure risk-capital tiers, and
  backup-plan checklists — `trading-business-framework.md`.
- Pin risk and weekend stock-position risk in arbitrage strategies (conversions,
  reverse conversions, box spreads) — `spreads-and-combinations.md`.
