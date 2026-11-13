# Presentation plan and speaker notes

Target: **about 16.5 minutes of planned speaking + about 3.5 minutes reserved for questions = 20 minutes** (the course allows 15–20 minutes). If the examiner wants 15 minutes in total, cut to the short version below.

| Slide | Title | Speaker (proposed) | Planned time | Cumulative |
|---|---|---|---|---|
| 1 | Delta Hedging of European Options | Member 1 | 0:30 | 0:30 |
| 2 | The seller's problem in plain English | Member 1 | 1:15 | 1:45 |
| 3 | Model: GBM under two measures | Member 1 | 1:15 | 3:00 |
| 4 | From Itô's lemma to the hedge ratio | Member 2 | 1:15 | 4:15 |
| 5 | The seller's books: discrete self-financing hedge | Member 2 | 1:30 | 5:45 |
| 6 | Why discrete hedging cannot be exact | Member 2 | 1:15 | 7:00 |
| 7 | Code mirrors the maths, and it is checked | Member 3 | 1:00 | 8:00 |
| 8 | More frequent trading: error falls like 1/√N | Member 3 | 1:30 | 9:30 |
| 9 | Wrong volatility: a bias that trading cannot remove | Member 4 | 1:30 | 11:00 |
| 10 | Costs: there is a best rebalancing frequency | Member 4 | 1:30 | 12:30 |
| 11 | Asset regimes, moneyness and maturity | Member 5 | 1:00 | 13:30 |
| 12 | Real prices (secondary source, illustration only) | Member 5 | 1:00 | 14:30 |
| 13 | What we learned | Member 5 | 1:00 | 15:30 |
| 14 | Limitations and next steps | All (Member 1 leads) | 0:45 | 16:15 |
| 15 | References, data and AI-assistance disclosure | Member 1 | 0:15 | 16:30 |
| — | **Questions** | all five | ~3:30 | 20:00 |

**Short (15-minute total) version, about 13:00 speaking + 2:00 questions:** merge slides 3 and 4 (−1:00); slide 7 in 0:30 (−0:30); slides 9 and 10 at 1:15 each (−0:30); slides 11 and 12 together in 1:00 (−1:00); slide 14 in 0:15 (−0:30). Total cut 3:30, so 16:30 → 13:00.

**Rehearsal rules.** Each member presents their slides *and* rehearses answering questions on everyone else's slides (see `viva_notes.pdf`, question bank). Run one full timed rehearsal with a stopwatch. Times above are plans, not measurements.

## Speaker notes (also embedded in `slides/deck.pptx`)

### Slide 1: Delta Hedging of European Options

SPEAKER: Member 1. TIME: 0:30 (cumulative 0:30).
Good morning. We studied what happens when a bank that sells an option tries to hedge it the way Black–Scholes says, but in a realistic world: trading only at discrete times, using a possibly wrong volatility, and paying transaction costs. All our code, data and results are reproducible from one folder.

### Slide 2: The seller's problem in plain English

SPEAKER: Member 1. TIME: 1:15 (cumulative 1:45).
Selling a call means we owe the payoff if the stock rises. To avoid betting, we hold delta shares; delta changes with the price, so we keep trading. Black–Scholes says this replicates the payoff exactly, but only under three idealisations. We relax each one: A discrete trading, B wrong volatility, C costs, and then we check how the answers change across assets (D) and on one real price series (E). Sign convention throughout: P&L at maturity, positive means the seller gains.

### Slide 3: Model: GBM under two measures

SPEAKER: Member 1. TIME: 1:15 (cumulative 3:00).
Two measures, two jobs. Under P the stock drifts at mu; that is where we live and where hedging profits and losses happen, so we simulate hedging paths under P. Under Q the drift is r; prices are discounted Q-expectations. Our validation shows this distinction matters numerically: the Monte Carlo price under Q matches Black–Scholes, the same estimator under P is wildly off. The log-price update is exact for any step size, so simulation adds no time-discretisation error. List the BS assumptions; units: currency with S0 = 100, years.

### Slide 4: From Itô's lemma to the hedge ratio

SPEAKER: Member 2. TIME: 1:15 (cumulative 4:15).
Walk down the four boxes. Itô gives dV. Holding the option and shorting V_S shares kills the dW term, so the portfolio is riskless and must earn r. That gives the PDE, and mu disappears, which is why the price does not depend on expected returns. The solution is the BS formula; delta is N(d1). Maturity: the formula divides by root tau, so the code sets the payoff and indicator delta at tau = 0 explicitly. Gamma explodes near expiry at the money; remember that for later.

### Slide 5: The seller's books: discrete self-financing hedge

SPEAKER: Member 2. TIME: 1:30 (cumulative 5:45).
This slide is the heart of the code. At t0 we receive the premium and buy delta shares, paying cost c. At each later date cash earns interest, then we trade the change in delta. At T we sell the shares and pay the cash-settled payoff; what is left is P&L. Self-financing means no other cash enters or leaves. Because delta does not depend on c, P&L is exactly linear in c. In the viva notes we work through a 4-step path by hand: premium 4.615, final P&L 1.349.

### Slide 6: Why discrete hedging cannot be exact

SPEAKER: Member 2. TIME: 1:15 (cumulative 7:00).
Taylor-expand the option over one step and use the PDE: what remains is half gamma S squared sigma squared dt times (1 minus Z squared). It has mean zero, so no bias, but variance, so noise. N independent steps of size T/N give variance proportional to 1/N, so sd proportional to 1/root N. In continuous time the realised variance equals sigma squared T exactly, which is why the BS argument works. Three formulas we will test: Kamal–Derman for the noise, the gamma-weighted variance gap for a wrong volatility, and Leland's cost-adjusted volatility.

### Slide 7: Code mirrors the maths, and it is checked

SPEAKER: Member 3. TIME: 1:00 (cumulative 8:00).
Each equation maps to one function; the hedge function follows the bookkeeping line by line. Before trusting any result we ran 22 checks, all pass, also as pytest. Key design choice: we simulate each path once on a fine grid and sub-sample it for every rebalancing frequency, so differences between frequencies are not caused by different random paths. Seeds are fixed via NumPy SeedSequence.

### Slide 8: More frequent trading: error falls like 1/√N

SPEAKER: Member 3. TIME: 1:30 (cumulative 9:30).
Left: same paths, three frequencies. All centred at zero, narrower with more trading. Right: log-log, slope minus 0.488 across 8 independent batches; the asymptotic theory says minus one half; coarse grids are outside the asymptotic regime, and from N = 63 upward the slope is minus 0.497. The Kamal–Derman line is within 1.4% for N ≥ 63. To halve the error you must trade four times as often. Tails are fat: expected shortfall is 2.3 sd versus 2.06 for a normal. What it cannot show: anything beyond the BS world. Also, not every statistic is monotone: the absolute mean is not.

### Slide 9: Wrong volatility: a bias that trading cannot remove

SPEAKER: Member 4. TIME: 1:30 (cumulative 11:00).
True sigma is 20%. If we price and hedge at 25%, we collect a bigger premium and on average keep about 0.99; at 15% we lose about 0.98. The line is the gamma-weighted variance-gap formula; it matches to two decimals. Crucially, the mean is the same at daily and at 20-times-daily trading: frequency cannot fix a wrong volatility. Right panel: path by path the realised P&L sits on the 45-degree line, correlation 0.965 to 0.992. If the premium is charged at the true sigma but delta uses the wrong one, the mean is about zero: the bias is a pricing error; the wrong delta adds risk, not expected loss.

### Slide 10: Costs: there is a best rebalancing frequency

SPEAKER: Member 4. TIME: 1:30 (cumulative 12:30).
Costs grow roughly with root N because each step trades about gamma times |dS|. Combined with hedging noise falling like 1/root N, RMSE becomes U-shaped; circles mark the minimum. At 10 bp the best is twice a day, N = 126; at 50 bp, every 3 trading days. At the optimum, bias from costs (0.47) dominates noise (0.34). Right: with Leland's volatility the extra premium pays for rebalancing; the remaining mean of minus 0.12 is exactly the cost of the initial purchase and final sale, 0.121, which Leland's model does not include. Our conclusion depends on choosing RMSE; a different risk criterion would move the optimum.

### Slide 11: Asset regimes, moneyness and maturity

SPEAKER: Member 5. TIME: 1:00 (cumulative 13:30).
Two stylised regimes, both hedged daily, simulated under P. Error scales with sigma, ratio 3.03, as Kamal–Derman predicts because ATM vega barely depends on sigma. Left, relative to premium: out-of-the-money options in calm markets are almost impossible to hedge in relative terms, because the premium is tiny while gamma can spike. Right: at fixed daily rebalancing the absolute error is flat in maturity, because vega grows like root T and N grows like T. Costs of 10 bp, however, grow with maturity: from 0.25 for one month to 0.62 for one year at 15% vol.

### Slide 12: Real prices (secondary source, illustration only)

SPEAKER: Member 5. TIME: 1:00 (cumulative 14:30).
The data are secondary-source price files with documented hashes, not option quotes; premiums are model prices. Calibrated volatilities range from 24% to 59%; drift has standard errors of 9 to 19% per year, so it is essentially unknowable, which is fine because the hedge does not use it. Backtest: sell a 63-day ATM AAPL call priced and hedged with trailing volatility, hedge daily along the real path. The P&L sign follows the variance gap, correlation 0.87, as the misspecification formula predicts. Caveat: 380 windows overlap heavily; only 7 are independent, so the average P&L is not interpretable.

### Slide 13: What we learned

SPEAKER: Member 5. TIME: 1:00 (cumulative 15:30).
Four take-aways, one per experiment family. Each one was predicted by a formula we derived and confirmed by simulation with standard errors.

### Slide 14: Limitations and next steps

SPEAKER: All (Member 1 leads). TIME: 0:45 (cumulative 16:15).
Be upfront: everything except E lives in the Black–Scholes world. Our optimum depends on RMSE. Real-data results are illustrations. Natural extensions: stochastic volatility, band rebalancing, real option quotes, gamma hedging.

### Slide 15: References, data and AI-assistance disclosure

SPEAKER: Member 1. TIME: 0:15 (cumulative 16:30). Then about 3:30 for questions (total 20:00).
All models and data are referenced; full list in the report. Invite questions; every member can answer any part.
