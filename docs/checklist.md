# Requirement → deliverable checklist

Source of requirements: "Project Component: Expectations and Evaluation Guidelines", MAC F244,
Semester I, AY 2026–27 (the course PDF), plus the group's own brief. Status as of 13 Nov 2026.
✅ = produced and checked by running. ⚠️ = needs action by the group.

## Course document requirements
| Requirement (course PDF) | Where it is met | Status |
|---|---|---|
| Groups of five | Placeholders: report title, slide 1, `docs/proposal.md`; split in `docs/team_split.md` | ⚠️ insert names/IDs |
| Topic from list or own (topic 12 used) | Title everywhere | ✅ (no approval claimed) |
| Proposal by 31 Oct 2026: title, problem, model, methodology, outcomes, names/IDs | `docs/proposal.md/.pdf`, dated 13 Nov 2026, not backdated | ⚠️ deadline already passed |
| Final submission by 15 Nov | everything below | ⚠️ due in 2 days |
| Source code, well structured and commented (R/Python) | `src/hedging/*.py`, `scripts/`, `tests/` | ✅ |
| Report, 3–4 pages: model, methodology, results, conclusions | `report/report.pdf` (4 pages incl. references), `report.tex` | ✅ |
| 15–20 min viva on formulation and key findings | `slides/deck.pptx/.pdf`, `docs/presentation_plan.md`, `docs/viva_notes.pdf` | ✅ rehearsal ⚠️ |
| Marks: report 5 / maths 5 / results 5 / viva 5 | report §2–3 (maths), §5 (results), slides + viva notes | ✅ |
| Clear link theory ↔ implementation | report §4, slide 7, code docstrings cite equation numbers | ✅ |
| Real data encouraged | Experiment E (secondary-source prices, labelled as such) | ✅ (limited) |
| Investigate changes in data or assets | Experiment D (two regimes × moneyness × maturity), E (five stocks, two periods) | ✅ |
| Not mere reproduction: meaningful analysis | Analytic predictions tested (Kamal–Derman, gamma formula, Leland residual = setup/unwind cost), optimal frequencies | ✅ |
| Reference models, algorithms, datasets | report references, `docs/references.md`, `data/SOURCES.md` | ✅ |

## Group brief requirements
| Requirement | Where | Status |
|---|---|---|
| Plain-language problem first | report §1, slide 2, viva notes §1 | ✅ |
| Every variable with units | report §2, viva notes §2 table | ✅ |
| GBM; P vs Q distinguished | report §2, slide 3; validation z-scores | ✅ |
| BS assumptions; Itô, replication, PDE, delta | report §2, slide 4, viva notes §3.2 | ✅ |
| Call price and delta, maturity handling | `black_scholes.py`, report eq. (2) | ✅ |
| Discrete self-financing bookkeeping (premium, holdings, cash, interest, rebalancing, settlement) | report eqs (3)–(5), `hedge.py`, slide 5 | ✅ |
| Sign convention | README, report §3, slide 5 | ✅ |
| Cost convention incl. initial and terminal trades | report §3, `hedge_short_call(liquidate_cost=True)` | ✅ |
| Why continuous result ≠ discrete exactness | report §3, slide 6, viva notes §3.6 | ✅ |
| Exact GBM; BS price/delta; transparent simulator; frictionless and cost cases; seeds; shared paths | `src/`, `experiments.py` | ✅ |
| A frequency / B misspecification / C costs / D ≥2 regimes + moneyness + maturity | `results/full/tables/A_*–D_*`, figs 1–4 | ✅ |
| Simulated vs empirical clearly distinguished | labels on fig 5, report §5E, `data/SOURCES.md` | ✅ |
| Mean, sd, RMSE, quantiles, costs, MC uncertainty, measure stated | `stats.summarize`, tables | ✅ |
| Validation: parity, FD delta, MC price, hand ledger, boundaries, refinement, no monotonicity claim | `results/validation/`, `A_monotonicity.csv` | ✅ (22/22) |
| Quick and full modes | `run_experiments.py --mode quick` and `--mode full` | ✅ |
| Executable notebook | `notebooks/demo.ipynb` (executed) | ✅ |
| Dependencies, seeds, reproduction commands | `README.md`, `requirements.txt`, `run_info.json` | ✅ |
| Editable report + PDF | `report/report.tex`, `report.pdf` | ✅ |
| Editable deck (PPTX) + PDF | `slides/deck.pptx`, `deck.pdf` | ✅ |
| Speaker notes + timed plan (speaking vs questions) | notes in PPTX; `docs/presentation_plan.md` | ✅ |
| Proposed five-person split | `docs/team_split.md` (labelled proposed) | ✅ |
| Viva preparation | `docs/viva_notes.pdf` (derivations, worked ledger, 25 Q&As) | ✅ |
| References + AI disclosure | `docs/references.md`, `docs/ai_disclosure.md` | ⚠️ check course policy |
