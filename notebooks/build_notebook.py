"""Builds notebooks/demo.ipynb (run once; the executed notebook is committed)."""
import nbformat as nbf
from pathlib import Path

md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
cells = [
md("""# Delta hedging a European call — demonstration notebook
MAC F244 project (topic 12). This notebook runs in about a minute on a laptop. It walks through the
mathematics → code correspondence and reproduces small versions of each experiment.
The full results (40,000 paths) are produced by `python scripts/run_experiments.py --mode full`
and are loaded at the end.

**Measures.** Paths for hedging experiments are simulated under the *physical* measure **P**
(drift μ). Prices and deltas use Black–Scholes (risk-neutral **Q**) formulas. The pricing check
in §1 simulates under **Q** (drift r)."""),
code("""import sys, numpy as np, pandas as pd
from pathlib import Path
ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
sys.path.insert(0, str(ROOT / "src"))
from hedging import *
pd.set_option("display.width", 140, "display.precision", 4)
S0, K, T, r, sigma, mu = 100.0, 100.0, 0.25, 0.05, 0.20, 0.10
print("BS call price C0 =", round(float(call_price(S0, K, T, r, sigma)), 4),
      "| delta0 =", round(float(call_delta(S0, K, T, r, sigma)), 4),
      "| vega =", round(float(vega(S0, K, T, r, sigma)), 4))"""),
md("""## 1. Pricing checks
Put–call parity $C-P=S-Ke^{-r\\tau}$, delta vs finite difference, and Monte Carlo under **Q** vs **P**."""),
code("""S = np.linspace(60, 140, 9)
parity = call_price(S, K, T, r, sigma) - put_price(S, K, T, r, sigma) - (S - K*np.exp(-r*T))
fd = (call_price(S+1e-4, K, T, r, sigma) - call_price(S-1e-4, K, T, r, sigma)) / 2e-4
print("max parity error:", np.abs(parity).max(), "| max delta FD error:", np.abs(fd - call_delta(S, K, T, r, sigma)).max())
rng = np.random.default_rng(1)
for m, label in [(r, "Q (drift r)"), (mu, "P (drift mu)")]:
    ST = simulate_gbm(S0, m, sigma, T, 1, 1_000_000, rng)[:, -1]
    x = np.exp(-r*T) * np.maximum(ST - K, 0)
    se = x.std() / np.sqrt(len(x))
    z = (x.mean() - call_price(S0, K, T, r, sigma)) / se
    print(f"{label:13s} discounted mean payoff = {x.mean():.4f} (SE {se:.4f}), z vs BS = {z:+.2f}")"""),
md("""Read the z-scores: under **Q** a value with |z| below about 3 is consistent with the BS price (note that any
single 95% interval misses 1 time in 20, so an occasional |z| near 2–2.5 is expected). Under **P** the
z-score is far outside that range: pricing requires the risk-neutral measure even though hedging P&L is
realised under **P**.

## 2. Hedge accounting on a path you can check by hand
Four rebalances (Δt = 1/16 year). Columns: delta held after trading, trade (shares), cash paid for the trade,
interest earned since the last date, transaction cost, option payoff, and cash after all of that."""),
code("""from hedging.validation import manual_example
path, p = manual_example()
led = hedge_ledger(path, p["K"], p["T"], p["r"], p["sigma"], cost=0.0)
print("premium received:", round(led.attrs["premium"], 6), "| terminal P&L:", round(led.attrs["pnl"], 6))
led.round(4)"""),
code("""# The same number from an independent formula: premium grown at r + discounted stock gains − payoff
print(pnl_gains_form(path[None, :], p["K"], p["T"], p["r"], p["sigma"])[0])"""),
md("""## 3. Experiment A (small): rebalancing frequency on shared paths"""),
code("""rng = np.random.default_rng(2026)
P = simulate_gbm(S0, mu, sigma, T, 252, 5000, rng)
rows = []
for N in [3, 9, 21, 63, 126, 252]:
    out = hedge_short_call(P, K, T, r, sigma, step=252 // N)
    s = summarize(out["pnl"]); s["N"] = N
    s["kamal_derman"] = np.sqrt(np.pi/4) * vega(S0, K, T, r, sigma) * sigma / np.sqrt(N)
    rows.append(s)
A = pd.DataFrame(rows)[["N", "mean", "se_mean", "std", "se_std", "kamal_derman", "q05", "es05"]]
print("log-log slope of std vs N:", round(loglog_slope(A.N, A["std"]), 3), "(theory −0.5)")
A"""),
md("""## 4. Experiment B (small): hedging with the wrong volatility
Premium and delta both use σ_h; the true σ is 20%. The theory column is the gamma-weighted variance gap."""),
code("""rows = []
for sh in [0.15, 0.20, 0.25]:
    out = hedge_short_call(P, K, T, r, sh, step=1)
    pred = predicted_pnl_misspecified(P, K, T, r, sigma, sh)
    rows.append(dict(sigma_h=sh, mean=out["pnl"].mean(), std=out["pnl"].std(), theory_mean=pred.mean()))
pd.DataFrame(rows)"""),
md("""## 5. Experiment C (small): costs make more trading worse beyond a point
P&L is linear in the cost rate: $\\text{PnL}(c)=\\text{PnL}(0)-c\\cdot TV$, so one simulation serves every c."""),
code("""rows = []
for N in [3, 9, 21, 63, 126, 252]:
    out = hedge_short_call(P, K, T, r, sigma, step=252 // N)
    for c in [0, 0.001, 0.005]:
        x = out["pnl"] - c * out["traded_value_fv"]
        rows.append(dict(N=N, cost_bp=c*1e4, mean=x.mean(), rmse=np.sqrt(np.mean(x**2))))
pd.DataFrame(rows).pivot(index="N", columns="cost_bp", values="rmse").round(3)"""),
md("""## 6. Full-mode results (40,000 paths) and figures
Produced by `scripts/run_experiments.py --mode full`; loaded here, not recomputed."""),
code("""full = ROOT / "results" / "full" / "tables"
if full.exists():
    display(pd.read_csv(full / "A_frequency.csv")[["N", "mean", "se_mean", "std", "se_std", "rmse", "q05", "es05", "kamal_derman_std"]])
    display(pd.read_csv(full / "C_best_frequency.csv"))
else:
    print("Run: python scripts/run_experiments.py --mode full")"""),
code("""from IPython.display import Image, display
figdir = ROOT / "results" / "full" / "figures"
for f in sorted(figdir.glob("fig*.png")):
    print(f.name); display(Image(filename=str(f), width=760))"""),
md("""### What these plots can and cannot show
* They show behaviour **inside the Black–Scholes world** (constant σ, no jumps, continuous prices) except
  §E, which uses one historical AAPL path segment with *model* premiums (no market option quotes).
* Monte Carlo standard errors quantify sampling noise only, not model error.
* Finite-sample statistics need not be monotone in N (e.g. |mean| is not); see `A_monotonicity.csv`."""),
]
nb = nbf.v4.new_notebook(cells=cells, metadata={"kernelspec": {"name": "python3", "display_name": "Python 3"}})
nbf.write(nb, Path(__file__).with_name("demo.ipynb"))
print("written")
