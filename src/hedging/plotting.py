"""
Figures for the report and slides. Every axis is labelled with units.
Colour order is fixed (validated categorical palette): blue, orange, aqua,
yellow, magenta. Money is in currency units with S0 = 100.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PALETTE = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#6250d6"]
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"

plt.rcParams.update({
    "font.size": 9, "axes.titlesize": 9.5, "axes.labelsize": 9,
    "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False,
    "legend.frameon": False, "legend.fontsize": 8, "lines.linewidth": 1.8,
    "savefig.dpi": 220, "savefig.bbox": "tight", "font.family": "DejaVu Sans",
})


def _save(fig, out, name):
    fig.savefig(out / f"{name}.png")
    fig.savefig(out / f"{name}.pdf")
    plt.close(fig)


def fig_frequency(A, arrays, out, T=0.25):
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.8))
    show = [N for N in (9, 63, 252) if f"A_pnl_N{N}" in arrays]
    bins = np.linspace(-3, 3, 121)
    for i, N in enumerate(show):
        ax[0].hist(arrays[f"A_pnl_N{N}"], bins=bins, density=True, histtype="step",
                   lw=1.6, color=PALETTE[i], label=f"N = {N} (Δt = {252 * T / N:g} trading day" + ("" if N == 63 else "s") + ")")
    ax[0].set_xlabel("Terminal hedging P&L (currency, S0 = 100)")
    ax[0].set_ylabel("Density")
    ax[0].set_title("(a) Same paths, different rebalancing")
    ax[0].legend(loc="upper right", fontsize=7)
    ax[0].set_ylim(0, 3.0)
    ax[1].errorbar(A["N"], A["std"], yerr=1.96 * A["se_std"], fmt="o", ms=4, color=PALETTE[0],
                   label="Simulated std (95% CI)")
    ax[1].plot(A["N"], A["kamal_derman_std"], "--", color=PALETTE[1], lw=1.4,
               label=r"Kamal–Derman $\sqrt{\pi/4}\,\mathcal{V}\sigma/\sqrt{N}$")
    ax[1].set_xscale("log"); ax[1].set_yscale("log")
    ax[1].set_xlabel("Number of rebalances N over T = 3 months (log)")
    ax[1].set_ylabel("Std of P&L (currency, log)")
    ax[1].set_title("(b) Error shrinks like $N^{-1/2}$")
    ax[1].legend(loc="lower left")
    fig.tight_layout()
    _save(fig, out, "fig1_frequency")


def fig_misspecification(B, arrays, out, sigma_true=0.2, M=1260):
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.8))
    Ns = sorted(B["N"].unique())
    for i, N in enumerate(Ns):
        d = B[B.N == N]
        off = (i - 0.5) * 0.004
        ax[0].errorbar(d.sigma_hedge + off, d["mean"], yerr=d["std"], fmt="o", ms=4, capsize=2,
                       color=PALETTE[i], label=f"Simulated, N = {N} (mean ± 1 std)")
    d = B[B.N == Ns[-1]]
    ax[0].plot(d.sigma_hedge, d.predicted_mean, "-", color=INK2, lw=1.0,
               label=r"Theory: $\frac{1}{2}\int e^{r(T-t)}\Gamma_h S^2(\sigma_h^2-\sigma^2)dt$")
    ax[0].axvline(sigma_true, color=GRID, lw=1.2, zorder=0)
    ax[0].axhline(0, color=INK2, lw=0.6)
    ax[0].set_xlabel(r"Hedge (and pricing) volatility $\sigma_h$  (true $\sigma$ = 20%)")
    ax[0].set_ylabel("Terminal P&L (currency)")
    ax[0].set_title("(a) Wrong volatility creates a bias")
    ax[0].legend(loc="lower right", fontsize=7)
    for i, sh in enumerate((0.15, 0.25)):
        key = f"B_pnl_sh{sh:.2f}_N{M}"
        if key not in arrays:
            continue
        x, y = arrays[f"B_pred_sh{sh:.2f}"][:3000], arrays[key][:3000]
        ax[1].scatter(x, y, s=4, alpha=0.35, color=PALETTE[i + 2], lw=0,
                      label=rf"$\sigma_h$ = {sh:.0%}")
    lim = np.array(ax[1].get_xlim())
    ax[1].plot(lim, lim, color=INK2, lw=0.8, label="45° line")
    ax[1].set_xlabel("Predicted P&L from gamma formula (currency)")
    ax[1].set_ylabel(f"Simulated P&L, N = {M} (currency)")
    ax[1].set_title("(b) Path by path: P&L tracks gamma exposure")
    ax[1].legend(loc="upper left", markerscale=3)
    fig.tight_layout()
    _save(fig, out, "fig2_misspecification")


def fig_costs(C, out):
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.8))
    bs = C[C.strategy == "BS delta (sigma)"]
    costs = sorted(bs.cost.unique())
    colour = {c: PALETTE[i] for i, c in enumerate(costs)}
    for c in costs:
        d = bs[bs.cost == c].sort_values("N")
        ax[0].plot(d.N, d.rmse, "-o", ms=3, color=colour[c], label=f"c = {c * 1e4:g} bp")
        j = d.rmse.idxmin()
        ax[0].plot(d.N[j], d.rmse[j], "o", ms=8, mfc="none", mec=colour[c], mew=1.4)
    ax[0].set_xscale("log"); ax[0].set_yscale("log")
    ax[0].set_xlabel("Number of rebalances N (log)")
    ax[0].set_ylabel("RMSE of P&L (currency, log)")
    ax[0].set_title("(a) Costs turn the curve into a U (circle = min)")
    ax[0].legend(loc="upper center", ncol=2, fontsize=7)
    lel = C[C.strategy == "Leland (sigma_L)"]
    for c in sorted(lel.cost.unique()):
        d = bs[bs.cost == c].sort_values("N")
        ax[1].plot(d.N, d["mean"], "-o", ms=3, color=colour[c], label=f"BS delta, c = {c * 1e4:g} bp")
        d = lel[lel.cost == c].sort_values("N")
        ax[1].plot(d.N, d["mean"], "--s", ms=3, color=colour[c], label=f"Leland, c = {c * 1e4:g} bp")
    ax[1].axhline(0, color=INK2, lw=0.6)
    ax[1].set_xscale("log")
    ax[1].set_xlabel("Number of rebalances N (log)")
    ax[1].set_ylabel("Mean P&L (currency)")
    ax[1].set_title("(b) Leland's volatility removes most of the drag")
    ax[1].legend(loc="lower left", fontsize=7)
    fig.tight_layout()
    _save(fig, out, "fig3_costs")


def fig_regimes(D, out):
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.8))
    for i, (name, d) in enumerate(D.groupby("regime", sort=False)):
        m = d[d.study == "moneyness"].sort_values("K")
        ax[0].plot(m.K / 100, m.std_over_premium * 100, "-o", ms=3.5, color=PALETTE[i], label=name)
        t = d[d.study == "maturity"].sort_values("T")
        ax[1].plot(t["T"] * 12, t["std"], "-o", ms=3.5, color=PALETTE[i], label=name + ", simulated")
        ax[1].plot(t["T"] * 12, t.kamal_derman_std, ":", color=PALETTE[i], lw=1.4,
                   label=name.split(" (")[0] + ", Kamal–Derman")
    ax[0].set_xlabel("Strike / spot  K/S0  (T = 3 months, daily rebalancing)")
    ax[0].set_ylabel("Std of P&L / premium (%)")
    ax[0].set_yscale("log")
    ax[0].set_title("(a) Relative error explodes out of the money")
    ax[0].legend(loc="upper left", fontsize=7)
    ax[1].set_xlabel("Maturity T (months), ATM, daily rebalancing")
    ax[1].set_ylabel("Std of P&L (currency)")
    ax[1].set_title("(b) Absolute error ~ flat in T, scales with σ")
    ax[1].legend(loc="center right", fontsize=6.5)
    ax[1].set_ylim(bottom=0)
    fig.tight_layout()
    _save(fig, out, "fig4_regimes")


def fig_realdata(bt, out):
    import pandas as pd
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.8))
    d = pd.to_datetime(bt.start)
    ax[0].plot(d, bt.sigma_hedge * 100, color=PALETTE[0], lw=1.4, label="Hedge σ: trailing 63-day (known at start)")
    ax[0].plot(d, bt.sigma_realised * 100, color=PALETTE[1], lw=1.4, label="Realised σ over option life (known after)")
    ax[0].set_ylabel("Annualised volatility (%)")
    ax[0].set_xlabel("Option start date (AAPL, daily data)")
    ax[0].set_title("(a) Volatility used vs volatility delivered")
    ax[0].set_ylim(5, 37)
    ax[0].legend(loc="lower left", fontsize=7)
    ax[0].tick_params(axis="x", rotation=30)
    ax[1].scatter(bt.var_gap * 100, bt.pnl_over_premium * 100, s=8, color=PALETTE[0], alpha=0.6, lw=0,
                  label="One window per start day (overlapping)")
    nono = bt.iloc[::63]
    ax[1].scatter(nono.var_gap * 100, nono.pnl_over_premium * 100, s=40, facecolor="none",
                  edgecolor=PALETTE[1], lw=1.4, label="Non-overlapping windows")
    ax[1].axhline(0, color=INK2, lw=0.6); ax[1].axvline(0, color=INK2, lw=0.6)
    ax[1].set_xlabel(r"$\sigma_h^2-\sigma_{realised}^2$  (×100)")
    ax[1].set_ylabel("Hedge P&L / premium (%)")
    ax[1].set_title("(b) Sign of P&L follows the variance gap")
    ax[1].legend(loc="upper left", fontsize=7)
    fig.tight_layout()
    _save(fig, out, "fig5_realdata")
