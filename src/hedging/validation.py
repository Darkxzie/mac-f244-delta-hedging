"""
Validation checks. Each check returns a row: what was tested, the measured
value, the tolerance, and whether it passed. Run via scripts/run_validation.py
or `pytest tests/`.
"""
import numpy as np
import pandas as pd

from .black_scholes import call_price, put_price, call_delta
from .gbm import simulate_gbm
from .hedge import hedge_short_call, pnl_gains_form, hedge_ledger
from .stats import summarize, loglog_slope


def _row(name, value, tol, passed, note=""):
    return dict(check=name, value=float(value), tolerance=tol, passed=bool(passed), note=note)


def manual_example():
    """A 4-step path anyone can check with a calculator (T = 0.25, dt = 1/16)."""
    path = np.array([100.0, 103.0, 98.0, 101.0, 104.0])
    return path, dict(K=100.0, T=0.25, r=0.05, sigma=0.20)


def run_all(seed=7):
    rng = np.random.default_rng(seed)
    rows = []
    r = 0.05

    # 1. put–call parity  C - P = S - K e^{-r tau}
    S = np.linspace(50, 150, 41)[:, None]
    K, tau, sig = 100.0, np.array([0.01, 0.25, 1.0, 5.0])[None, :], 0.3
    err = np.abs(call_price(S, K, tau, r, sig) - put_price(S, K, tau, r, sig) - (S - K * np.exp(-r * tau)))
    rows.append(_row("Put–call parity, max abs error", err.max(), 1e-10, err.max() < 1e-10,
                     "41 spots x 4 maturities"))

    # 2. delta vs central finite difference
    h = 1e-4
    fd = (call_price(S + h, K, tau, r, sig) - call_price(S - h, K, tau, r, sig)) / (2 * h)
    err = np.abs(fd - call_delta(S, K, tau, r, sig))
    rows.append(_row("Delta vs central finite difference, max abs error", err.max(), 1e-6,
                     err.max() < 1e-6, "h = 1e-4"))

    # 3. MC price under Q vs Black–Scholes (exact one-step GBM)
    S0, T, sigma, n = 100.0, 0.25, 0.2, 1_000_000
    ST = simulate_gbm(S0, r, sigma, T, 1, n, rng)[:, -1]
    disc = np.exp(-r * T) * np.maximum(ST - K, 0)
    bs = float(call_price(S0, K, T, r, sigma))
    z = (disc.mean() - bs) / (disc.std(ddof=1) / np.sqrt(n))
    rows.append(_row("MC price under Q vs BS, z-score", z, 3.0, abs(z) < 3,
                     f"MC {disc.mean():.4f} vs BS {bs:.4f}, n={n:,}"))
    STp = simulate_gbm(S0, 0.25, sigma, T, 1, n, rng)[:, -1]
    discp = np.exp(-r * T) * np.maximum(STp - K, 0)
    zp = (discp.mean() - bs) / (discp.std(ddof=1) / np.sqrt(n))
    rows.append(_row("Same estimator under P (mu=25%) is NOT the price, z-score", zp, 3.0, abs(zp) > 3,
                     f"MC {discp.mean():.4f}: pricing needs Q, not P"))

    # 4. hand-checkable ledger agrees with vectorised simulator and gains form
    path, p = manual_example()
    for c in (0.0, 0.001):
        led = hedge_ledger(path, p["K"], p["T"], p["r"], p["sigma"], cost=c)
        vec = hedge_short_call(path[None, :], p["K"], p["T"], p["r"], p["sigma"], cost=c)["pnl"][0]
        rows.append(_row(f"Ledger vs simulator P&L (c={c})", abs(led.attrs["pnl"] - vec), 1e-12,
                         abs(led.attrs["pnl"] - vec) < 1e-12, f"P&L = {vec:.6f}"))
    gf = pnl_gains_form(path[None, :], p["K"], p["T"], p["r"], p["sigma"])[0]
    rows.append(_row("Ledger vs gains-form P&L (c=0)", abs(gf - vec_frictionless(path, p)), 1e-12,
                     abs(gf - vec_frictionless(path, p)) < 1e-12))

    # 5. bookkeeping vs gains form on many random paths
    P = simulate_gbm(100, 0.1, 0.2, 0.25, 63, 5000, rng)
    d = np.abs(hedge_short_call(P, 100, 0.25, r, 0.2)["pnl"] - pnl_gains_form(P, 100, 0.25, r, 0.2))
    rows.append(_row("Cash bookkeeping vs gains form, 5000 paths, max diff", d.max(), 1e-9, d.max() < 1e-9))

    # 6. boundary cases
    tiny = 1e-12
    rows.append(_row("tau->0: price -> payoff", abs(call_price(105, 100, tiny, r, 0.2) - 5.0), 1e-6,
                     abs(call_price(105, 100, tiny, r, 0.2) - 5.0) < 1e-6))
    rows.append(_row("tau->0: delta -> 1{S>K}", abs(call_delta(105, 100, tiny, r, 0.2) - 1)
                     + abs(call_delta(95, 100, tiny, r, 0.2)), 1e-9,
                     abs(call_delta(105, 100, tiny, r, 0.2) - 1) + abs(call_delta(95, 100, tiny, r, 0.2)) < 1e-9))
    deep = call_price(1000, 100, 1, r, 0.2) - (1000 - 100 * np.exp(-r))
    rows.append(_row("Deep ITM: C -> S - K e^{-rT}", abs(deep), 1e-8, abs(deep) < 1e-8))
    rows.append(_row("Deep OTM: C -> 0", call_price(1, 100, 1, r, 0.2), 1e-12, call_price(1, 100, 1, r, 0.2) < 1e-12))
    s0 = abs(call_price(110, 100, 1, r, 1e-9) - (110 - 100 * np.exp(-r)))
    rows.append(_row("sigma->0: C -> (S - K e^{-rT})^+", s0, 1e-8, s0 < 1e-8))
    Sg = np.linspace(1, 300, 600)
    C = call_price(Sg, 100, 0.5, r, 0.3); D = call_delta(Sg, 100, 0.5, r, 0.3)
    ok = (np.all(C >= np.maximum(Sg - 100 * np.exp(-r * 0.5), 0) - 1e-12) and np.all(C <= Sg)
          and np.all((D >= 0) & (D <= 1)) and np.all(np.diff(D) >= -1e-15))
    rows.append(_row("No-arbitrage bounds; 0<=delta<=1, delta increasing in S", 0, 0, ok))
    # deep OTM call (K = 300): premium ~ 0, delta ~ 0, so hedge P&L ~ 0 on every path
    Pz = simulate_gbm(100, 0.1, 0.2, 0.25, 63, 2000, rng)
    otm = np.abs(hedge_short_call(Pz, 300, 0.25, r, 0.2)["pnl"]).max()
    rows.append(_row("Deep OTM hedge (K=300): max |P&L|", otm, 1e-8, otm < 1e-8,
                     "nothing to hedge, nothing to pay"))
    # very high frequency on a nearly deterministic stock: replication ~ exact
    Pz = simulate_gbm(100, 0.1, 0.01, 0.25, 1260, 500, rng)
    tiny_sig = np.abs(hedge_short_call(Pz, 100, 0.25, r, 0.01)["pnl"]).max()
    rows.append(_row("sigma=1%, N=1260: max |P&L| small", tiny_sig, 0.02, tiny_sig < 0.02))

    # 7. timestep refinement
    #  (a) exact GBM: distribution of S_T does not depend on the number of steps
    S1 = simulate_gbm(100, 0.1, 0.2, 0.25, 1, 200_000, rng)[:, -1]
    S252 = simulate_gbm(100, 0.1, 0.2, 0.25, 252, 20_000, rng)[:, -1]
    target = 100 * np.exp(0.1 * 0.25)
    z1 = (S1.mean() - target) / (S1.std() / np.sqrt(len(S1)))
    z2 = (S252.mean() - target) / (S252.std() / np.sqrt(len(S252)))
    rows.append(_row("Exact GBM: E[S_T] with 1 step, z", z1, 3, abs(z1) < 3))
    rows.append(_row("Exact GBM: E[S_T] with 252 steps, z", z2, 3, abs(z2) < 3))
    vlog = np.log(S252 / 100).var(ddof=1); se_v = vlog * np.sqrt(2 / (len(S252) - 1))
    rows.append(_row("Exact GBM: Var(ln S_T) = sigma^2 T, z", (vlog - 0.04 * 0.25) / se_v, 3,
                     abs((vlog - 0.04 * 0.25) / se_v) < 3))
    #  (b) hedge error shrinks like N^{-1/2} under refinement of the rebalancing grid
    P = simulate_gbm(100, 0.1, 0.2, 0.25, 1008, 4000, rng)
    Ns = np.array([14, 28, 56, 112, 252, 504, 1008])
    sds = np.array([hedge_short_call(P, 100, 0.25, r, 0.2, step=1008 // N)["pnl"].std() for N in Ns])
    sl = loglog_slope(Ns, sds)
    rows.append(_row("Refinement: log-log slope of P&L std vs N", sl, "[-0.6,-0.4]", -0.6 < sl < -0.4,
                     "theory -1/2"))

    # 8. seed robustness: two independent seeds agree within MC error
    st = []
    for s in (101, 202):
        Pz = simulate_gbm(100, 0.1, 0.2, 0.25, 63, 20000, np.random.default_rng(s))
        st.append(summarize(hedge_short_call(Pz, 100, 0.25, r, 0.2)["pnl"]))
    z = (st[0]["std"] - st[1]["std"]) / np.hypot(st[0]["se_std"], st[1]["se_std"])
    rows.append(_row("Seed robustness: P&L std, seed 101 vs 202, z", z, 3, abs(z) < 3,
                     f"{st[0]['std']:.4f} vs {st[1]['std']:.4f}"))
    zm = st[0]["mean"] / st[0]["se_mean"]
    rows.append(_row("Correct sigma, daily, no costs: mean P&L = 0? z", zm, 3, abs(zm) < 3,
                     "discrete hedging is unbiased to first order"))

    path, p = manual_example()
    ledgers = {c: hedge_ledger(path, p["K"], p["T"], p["r"], p["sigma"], cost=c) for c in (0.0, 0.001)}
    return pd.DataFrame(rows), ledgers


def vec_frictionless(path, p):
    return hedge_short_call(path[None, :], p["K"], p["T"], p["r"], p["sigma"])["pnl"][0]
