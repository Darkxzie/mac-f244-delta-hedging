# Proposed five-person responsibility split

**Status: PROPOSED.** This is a suggested division of ownership for reviewing, adapting and
presenting the project. It does **not** describe work already performed by any member. Replace
"Member n" with real names once the group agrees.

Every member must be able to explain the **whole** project. Ownership means "first to answer and
responsible for checking", not "the only one who understands it".

| Member | Owns (checks line by line, can re-derive) | Presents (slides) | Viva backup for |
|---|---|---|---|
| 1 | Problem framing; GBM, P vs Q, BS assumptions; `gbm.py`; references and data provenance (`data/SOURCES.md`) | 1–3, 14 (lead), 15 | Member 5 (real data) |
| 2 | Itô → PDE → BS formula, maturity handling; bookkeeping eqs (3)–(5); hand ledger; `black_scholes.py`, `hedge.py` | 4–6 | Member 3 (code) |
| 3 | Code structure, seeds, common random numbers, Monte Carlo SEs; validation suite; Experiment A; `stats.py`, `validation.py`, notebook | 7–8 | Member 2 (derivations) |
| 4 | Experiments B and C: misspecification formula, cost linearity, Leland and the setup/unwind residual; `experiments.py` | 9–10 | Member 1 (theory) |
| 5 | Experiment D (regimes, moneyness, maturity) and E (calibration, backtest); report editing to 3–4 pages; final consistency check of numbers | 11–13 | Member 4 (B, C) |

## Suggested checklist before 15 November (proposed, not done)
1. Everyone: run `python scripts/run_validation.py` and `python scripts/run_experiments.py --mode quick` on their own laptop.
2. Owners: re-derive their equations on paper, compare every number in report and slides with `results/full/tables/*.csv`.
3. Insert names and IDs (report title block, slide 1, `docs/proposal.md`).
4. Rewrite any sentence you could not defend in your own words.
5. One timed rehearsal; swap roles for the Q&A drill using `viva_notes.pdf`.
6. Check the course AI-use policy and finalise `docs/ai_disclosure.md`.
