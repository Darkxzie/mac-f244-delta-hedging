# Delta Hedging of European Options
### How rebalancing frequency, volatility misspecification and transaction costs affect hedging errors
MAC F244, Semester I, AY 2026–27. Project topic 12. Group of five (names and IDs go in `docs/proposal.md` and the report title block).

## What is in this folder

| Path | Contents |
|---|---|
| `src/hedging/black_scholes.py` | BS call/put price, delta, gamma, vega, Leland volatility (maturity handled explicitly) |
| `src/hedging/gbm.py` | exact GBM simulation (P or Q depending on the drift passed) |
| `src/hedging/hedge.py` | self-financing discrete hedge of a short call; ledger for one path; gamma-formula prediction |
| `src/hedging/stats.py` | summary statistics with Monte Carlo standard errors |
| `src/hedging/experiments.py` | Experiments A–D (all parameters in the `Config` dataclass) |
| `src/hedging/realdata.py` | Experiment E: volatility calibration and AAPL historical-path backtest |
| `src/hedging/validation.py` | 22 validation checks |
| `src/hedging/plotting.py` | the five figures |
| `scripts/run_experiments.py` | runs everything and writes `results/<mode>/` |
| `scripts/run_validation.py` | runs checks and writes `results/validation/` |
| `tests/test_validation.py` | the same checks under pytest |
| `notebooks/demo.ipynb` | executed demonstration notebook (≈1 min) |
| `data/` | two small secondary-source price files + `SOURCES.md` (provenance, hashes, conventions) |
| `results/full/`, `results/quick/` | CSV tables, figures (PNG + PDF), `run_info.json` |
| `report/` | `report.tex` (editable) and `report.pdf` |
| `slides/` | `deck.pptx` (with speaker notes) and `deck.pdf` |
| `docs/` | checklist, proposal, viva notes, presentation plan, team split, references, AI disclosure |

## Reproduce

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python scripts/run_validation.py                 # 22 checks, ~2 s, exits non-zero if any fail
python -m pytest -q tests/                       # same checks + cost-linearity test
python scripts/run_experiments.py --mode quick   # ~10 s: 4,000 paths, fine grid M = 252
python scripts/run_experiments.py --mode full    # ~70 s: 40,000 paths, fine grid M = 1260
jupyter nbconvert --to notebook --execute notebooks/demo.ipynb --output demo.ipynb
cd report && latexmk -pdf report.tex            # needs a TeX installation
```

**Seeds.** Every experiment uses `np.random.SeedSequence(2026).spawn(...)`, so experiments get
independent but reproducible streams. Change the master seed with `--seed`. Validation uses seed 7.
The notebook uses seeds 1 and 2026. Results are bit-for-bit reproducible for the same NumPy version.
Different NumPy versions can change the random stream; in that case only Monte Carlo-sized
differences should appear.

**Timings** were measured on the cloud Linux machine used to build this project (Python 3.13). A
laptop should be comparable. Peak memory is about 60 MB per 5,000-path batch.

## Conventions (stated once, used everywhere)
* Money is in currency units with S0 = 100. Time is in years. Rates and volatilities are per year.
* The group is the **seller** of the call. **P&L > 0 means the seller gains.** P&L is measured at maturity T.
* Rebalancing at t_k = kT/N, k = 0…N−1. At T the stock is sold and the call is **cash-settled**.
* Proportional cost `c` per side, charged on |shares traded| × price, **including** the initial
  purchase and the final liquidation.
* Hedging paths are simulated under **P** (drift μ). Pricing checks are simulated under **Q** (drift r).
