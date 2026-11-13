---
title: "Project Proposal and Progress Statement — MAC F244 (Semester I, AY 2026–27)"
date: "Prepared 13 November 2026"
geometry: margin=2.2cm
fontsize: 11pt
---

> **Date note (please read).** The course document asks for the proposal and progress
> statement by **31 October 2026** and the final submission by **15 November**. This document was
> prepared on 13 November 2026 and is **not backdated**. If your group already submitted a proposal,
> keep that version; this one can serve as a record or be discarded. Instructor approval of the
> topic is **not** claimed here.

## Group members

| # | Name | ID number |
|---|---|---|
| 1 | [Name] | [ID] |
| 2 | [Name] | [ID] |
| 3 | [Name] | [ID] |
| 4 | [Name] | [ID] |
| 5 | [Name] | [ID] |

## Title
**Delta Hedging of European Options: How Rebalancing Frequency, Volatility Misspecification,
and Transaction Costs Affect Hedging Errors** (suggested topic 12 in the course list).

## Problem
An option seller receives a premium and must pay the option's payoff at maturity. Delta hedging
(holding ∂C/∂S shares, adjusted over time) removes this risk perfectly only under the Black–Scholes
ideal: continuous trading, no costs, known volatility. We measure the hedging error that remains when
(i) the seller rebalances only N times, (ii) uses the wrong volatility, (iii) pays proportional
transaction costs. We also measure (iv) how the answers change across asset volatility regimes, moneyness and maturity.

## Mathematical model
* Stock: geometric Brownian motion dS = μS dt + σS dW under the physical measure P (simulation of
  hedging P&L); drift r under the risk-neutral measure Q (pricing).
* Option: European call, Black–Scholes price and delta from Itô's lemma, replication and the BS PDE.
* Hedge: discrete self-financing portfolio of stock and a cash account earning r; proportional cost c
  per side on every trade, including initial purchase and final liquidation.
* Analytic benchmarks: Kamal–Derman approximation sd ≈ √(π/4)·vega·σ/√N; gamma-weighted
  variance-gap formula for misspecified volatility; Leland's cost-adjusted volatility.

## Computational methodology
Python (NumPy, SciPy, pandas, Matplotlib). Exact GBM simulation on a fine grid. Every rebalancing frequency
is applied to the same simulated paths (common random numbers). Monte Carlo standard errors are reported for every statistic.
Validation covers put–call parity, finite-difference delta, Q-Monte-Carlo price, a hand-checked ledger,
boundary cases and timestep refinement. A small real-data part estimates volatility from historical prices
and runs one historical-path backtest.

## Expected outcomes
* Error spread ∝ N^(−1/2) with mean ≈ 0 when σ is correct.
* A bias proportional to (σ_h² − σ²) that does not disappear with more frequent trading.
* An interior optimal rebalancing frequency once costs are included.
* Larger relative errors for out-of-the-money, short-dated, low-volatility options.

## Progress status (as of 13 November 2026)
**Completed (verified by running the code):** core library; 22 validation checks (all pass);
experiments A–E in quick and full modes; figures and CSV tables; executed notebook; 4-page report and
slides (drafts for the group to review).
**Remaining for the group:** insert names/IDs; check every derivation and number; adapt the text to
your own words; check AI-use policy; rehearse the viva (≈15 min talk + ≈5 min questions).
