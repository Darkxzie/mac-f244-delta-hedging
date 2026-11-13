"""
Numerical experiments A–E. Each function returns pandas DataFrames; the
driver script `scripts/run_experiments.py` saves them to CSV and plots them.

Probability measures:
    Experiments A–D simulate the stock under the PHYSICAL measure P (drift mu),
    because hedging P&L is realised in the real world. Premiums and deltas are
    computed with Black–Scholes (risk-neutral pricing). Pricing checks in
    validation.py simulate under Q (drift r).

Common random numbers: in A, B and C every hedging strategy is applied to the
SAME simulated paths (fine grid of M steps, coarser rebalancing obtained by
sub-sampling), so differences between strategies are not sampling noise in the
paths themselves.
"""
from dataclasses import dataclass, field, asdict
import numpy as np
import pandas as pd

from .black_scholes import call_price, vega, leland_sigma
from .gbm import simulate_gbm
from .hedge import hedge_short_call, predicted_pnl_misspecified
from .stats import summarize, loglog_slope

TRADING_DAYS = 252


@dataclass
class Config:
    mode: str = "full"
    seed: int = 2026
    n_paths: int = 40_000          # paths per experiment
    batch: int = 5_000             # paths simulated at once (memory control)
    M: int = 1260                  # fine steps over T = 0.25 (20 per trading day)
    N_list: tuple = (3, 9, 21, 63, 126, 252, 630, 1260)
    # base contract and market (units: currency, years, per-year rates)
    S0: float = 100.0
    K: float = 100.0
    T: float = 0.25
    r: float = 0.05
    mu: float = 0.10
    sigma: float = 0.20
    sigma_hedge_list: tuple = (0.10, 0.15, 0.20, 0.25, 0.30)
    cost_list: tuple = (0.0, 0.0005, 0.001, 0.002, 0.005)
    leland_costs: tuple = (0.001, 0.005)
    mu_list: tuple = (0.05, 0.10, 0.25)
    regimes: dict = field(default_factory=lambda: {
        "Low-vol (sigma=15%, mu=8%)": {"sigma": 0.15, "mu": 0.08},
        "High-vol (sigma=45%, mu=12%)": {"sigma": 0.45, "mu": 0.12},
    })
    moneyness_K: tuple = (80.0, 90.0, 100.0, 110.0, 120.0)
    maturities: tuple = (1 / 12, 0.25, 0.5, 1.0)
    regime_cost: float = 0.001
    n_boot: int = 200

    @staticmethod
    def quick():
        return Config(mode="quick", n_paths=4_000, batch=4_000, M=252,
                      N_list=(3, 9, 21, 63, 126, 252), n_boot=100)


def _rngs(cfg, n):
    """Independent, reproducible generators derived from one master seed."""
    return [np.random.default_rng(s) for s in np.random.SeedSequence(cfg.seed).spawn(n)]


# --------------------------------------------------------------------------
# A, B, C share one set of base paths
# --------------------------------------------------------------------------
def run_base_experiments(cfg, log=print):
    rng_paths, rng_boot, rng_mu = _rngs(cfg, 3)
    S0, K, T, r, sig = cfg.S0, cfg.K, cfg.T, cfg.r, cfg.sigma
    n_batches = cfg.n_paths // cfg.batch
    N_list = [N for N in cfg.N_list if cfg.M % N == 0]

    pnl0 = {N: [] for N in N_list}           # frictionless P&L, sigma_hedge = sigma
    tv = {N: [] for N in N_list}             # traded value FV (for costs)
    batch_std = {N: [] for N in N_list}      # per-batch std -> replication of slope
    misspec = {}                             # (sigma_h, N) -> list of arrays
    misspec_fair = {}                        # same trades, premium at TRUE sigma
    predicted = {sh: [] for sh in cfg.sigma_hedge_list}
    leland = {}
    # misspecification is studied at daily rebalancing and at the finest grid
    N_mis = sorted(set([63 if 63 in N_list else N_list[len(N_list) // 2], cfg.M]))

    for b in range(n_batches):
        P = simulate_gbm(S0, cfg.mu, sig, T, cfg.M, cfg.batch, rng_paths)
        for N in N_list:
            out = hedge_short_call(P, K, T, r, sig, step=cfg.M // N)
            pnl0[N].append(out["pnl"]); tv[N].append(out["traded_value_fv"])
            batch_std[N].append(out["pnl"].std(ddof=1))
        fair = float(call_price(S0, K, T, r, sig))
        for sh in cfg.sigma_hedge_list:
            predicted[sh].append(predicted_pnl_misspecified(P, K, T, r, sig, sh))
            for N in N_mis:
                out = hedge_short_call(P, K, T, r, sh, step=cfg.M // N)
                misspec.setdefault((sh, N), []).append(out["pnl"])
                # premium at true sigma: shift by (fair - V_h) grown to T
                shift = (fair - out["premium"]) * np.exp(r * T)
                misspec_fair.setdefault((sh, N), []).append(out["pnl"] + shift)
        for c in cfg.leland_costs:
            for N in N_list:
                sL = leland_sigma(sig, c, T / N)
                out = hedge_short_call(P, K, T, r, sL, cost=c, step=cfg.M // N)
                leland.setdefault((c, N), []).append((out["pnl"], out["cost_fv"], sL, out["premium"],
                                                      out["setup_unwind_cost_fv"]))
        log(f"  base batch {b + 1}/{n_batches} done")

    cat = lambda d: {k: np.concatenate(v) for k, v in d.items()}
    pnl0, tv, misspec, misspec_fair, predicted = map(cat, (pnl0, tv, misspec, misspec_fair, predicted))

    # ---------------- A: rebalancing frequency ----------------
    vg = float(vega(S0, K, T, r, sig))
    rows = []
    for N in N_list:
        s = summarize(pnl0[N], rng_boot, cfg.n_boot)
        s.update(N=N, interval_days=TRADING_DAYS * T / N,
                 kamal_derman_std=np.sqrt(np.pi / 4) * vg * sig / np.sqrt(N))
        rows.append(s)
    A = pd.DataFrame(rows)
    slopes = [loglog_slope(np.array(N_list), np.array([batch_std[N][b] for N in N_list]))
              for b in range(n_batches)]
    A_slope = pd.DataFrame([{
        "slope_all_paths": loglog_slope(np.array(N_list), A["std"].values),
        "slope_mean_over_batches": np.mean(slopes),
        "slope_se_over_batches": np.std(slopes, ddof=1) / np.sqrt(n_batches) if n_batches > 1 else np.nan,
        "n_batches": n_batches, "theory": -0.5}])

    # A2: does the real-world drift matter? (N = daily)
    N_d = 63 if 63 in N_list else N_list[len(N_list) // 2]
    rows = []
    for mu in cfg.mu_list:
        P = simulate_gbm(S0, mu, sig, T, N_d, cfg.n_paths, rng_mu)
        s = summarize(hedge_short_call(P, K, T, r, sig)["pnl"])
        s.update(mu=mu, N=N_d)
        rows.append(s)
    A_mu = pd.DataFrame(rows)

    # ---------------- B: volatility misspecification ----------------
    rows = []
    for (sh, N), x in misspec.items():
        s = summarize(x, rng_boot, cfg.n_boot)
        pred = predicted[sh]
        s.update(sigma_hedge=sh, N=N,
                 premium=float(call_price(S0, K, T, r, sh)),
                 predicted_mean=pred.mean(), predicted_se=pred.std(ddof=1) / np.sqrt(len(pred)),
                 corr_with_predicted=np.corrcoef(x, pred)[0, 1] if sh != sig else np.nan,
                 mean_if_premium_at_true_sigma=misspec_fair[(sh, N)].mean(),
                 std_if_premium_at_true_sigma=misspec_fair[(sh, N)].std(ddof=1))
        rows.append(s)
    B = pd.DataFrame(rows).sort_values(["N", "sigma_hedge"]).reset_index(drop=True)

    # ---------------- C: transaction costs vs frequency ----------------
    rows = []
    for c in cfg.cost_list:
        for N in N_list:
            x = pnl0[N] - c * tv[N]          # exact: P&L is linear in c
            s = summarize(x)
            s.update(cost=c, N=N, interval_days=TRADING_DAYS * T / N,
                     mean_cost_fv=c * tv[N].mean(), strategy="BS delta (sigma)")
            rows.append(s)
    for (c, N), parts in leland.items():
        x = np.concatenate([p[0] for p in parts]); cf = np.concatenate([p[1] for p in parts])
        s = summarize(x)
        s.update(cost=c, N=N, interval_days=TRADING_DAYS * T / N, mean_cost_fv=cf.mean(),
                 strategy="Leland (sigma_L)", sigma_L=parts[0][2], premium=parts[0][3],
                 mean_setup_unwind_cost_fv=np.concatenate([p[4] for p in parts]).mean())
        rows.append(s)
    C = pd.DataFrame(rows)
    best = (C[C.strategy == "BS delta (sigma)"].loc[lambda d: d.groupby("cost")["rmse"].idxmin()]
            [["cost", "N", "interval_days", "rmse", "mean", "std", "mean_cost_fv"]]
            .rename(columns={"N": "N_min_rmse"}))

    arrays = {"A_pnl_N%d" % N: pnl0[N] for N in N_list}
    arrays.update({"B_pnl_sh%.2f_N%d" % k: v for k, v in misspec.items()})
    arrays.update({"B_pred_sh%.2f" % k: v for k, v in predicted.items()})
    return {"A_frequency": A, "A_slope": A_slope, "A_drift": A_mu,
            "B_misspecification": B, "C_costs": C, "C_best_frequency": best}, arrays


# --------------------------------------------------------------------------
# D: asset regimes x moneyness / maturity (daily rebalancing)
# --------------------------------------------------------------------------
def run_regime_experiments(cfg, log=print):
    rng = _rngs(cfg, 4)[3]
    r, S0, c = cfg.r, cfg.S0, cfg.regime_cost
    rows = []
    for name, p in cfg.regimes.items():
        sig, mu = p["sigma"], p["mu"]
        # D1: moneyness at T = 0.25, one set of paths shared across strikes
        T = 0.25; N = int(round(TRADING_DAYS * T))
        P = simulate_gbm(S0, mu, sig, T, N, cfg.n_paths, rng)
        for K in cfg.moneyness_K:
            out = hedge_short_call(P, K, T, r, sig)
            x0, xc = out["pnl"], out["pnl"] - c * out["traded_value_fv"]
            s0, sc = summarize(x0), summarize(xc)
            rows.append(dict(regime=name, sigma=sig, mu=mu, study="moneyness", K=K, T=T, N=N,
                             premium=out["premium"], mean=s0["mean"], std=s0["std"],
                             se_std=s0["se_std"], rmse=s0["rmse"], es05=s0["es05"],
                             std_over_premium=s0["std"] / out["premium"],
                             kamal_derman_std=np.sqrt(np.pi / 4) * float(vega(S0, K, T, r, sig)) * sig / np.sqrt(N),
                             mean_with_cost=sc["mean"], rmse_with_cost=sc["rmse"],
                             mean_cost_fv=c * out["traded_value_fv"].mean()))
        # D2: maturity, ATM, daily rebalancing
        for T in cfg.maturities:
            N = int(round(TRADING_DAYS * T))
            P = simulate_gbm(S0, mu, sig, T, N, cfg.n_paths, rng)
            out = hedge_short_call(P, S0, T, r, sig)
            x0, xc = out["pnl"], out["pnl"] - c * out["traded_value_fv"]
            s0, sc = summarize(x0), summarize(xc)
            rows.append(dict(regime=name, sigma=sig, mu=mu, study="maturity", K=S0, T=T, N=N,
                             premium=out["premium"], mean=s0["mean"], std=s0["std"],
                             se_std=s0["se_std"], rmse=s0["rmse"], es05=s0["es05"],
                             std_over_premium=s0["std"] / out["premium"],
                             kamal_derman_std=np.sqrt(np.pi / 4) * float(vega(S0, S0, T, r, sig)) * sig / np.sqrt(N),
                             mean_with_cost=sc["mean"], rmse_with_cost=sc["rmse"],
                             mean_cost_fv=c * out["traded_value_fv"].mean()))
        log(f"  regime done: {name}")
    return {"D_regimes": pd.DataFrame(rows)}
