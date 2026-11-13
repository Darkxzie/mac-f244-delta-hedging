"""
Summary statistics of hedging P&L with Monte Carlo standard errors.

Standard errors (n i.i.d. paths):
    mean : s / sqrt(n)
    std  : delta method, SE(s) ~= sqrt((m4 - s^4)/n) / (2 s)   (no normality assumed)
    RMSE : delta method on mean(x^2):  SE ~= sd(x^2) / (2 RMSE sqrt(n))
    q05 / ES05 : nonparametric bootstrap (B resamples)
ES05 = average P&L over the worst 5% of paths (a tail-loss measure).
"""
import numpy as np


def expected_shortfall(x, alpha=0.05):
    """Mean of the lowest alpha-fraction of outcomes (P&L, so low = bad)."""
    x = np.sort(np.asarray(x))
    k = max(1, int(np.floor(alpha * len(x))))
    return x[:k].mean()


def summarize(x, rng=None, n_boot=200):
    x = np.asarray(x, float)
    n = len(x)
    mean, std = x.mean(), x.std(ddof=1)
    m4 = np.mean((x - mean) ** 4)
    rmse = np.sqrt(np.mean(x**2))
    out = {
        "n_paths": n,
        "mean": mean, "se_mean": std / np.sqrt(n),
        "std": std, "se_std": np.sqrt(max(m4 - std**4, 0.0) / n) / (2 * std) if std > 0 else 0.0,
        "rmse": rmse, "se_rmse": np.std(x**2, ddof=1) / (2 * rmse * np.sqrt(n)) if rmse > 0 else 0.0,
        "q01": np.quantile(x, 0.01), "q05": np.quantile(x, 0.05),
        "q50": np.quantile(x, 0.50), "q95": np.quantile(x, 0.95),
        "q99": np.quantile(x, 0.99), "es05": expected_shortfall(x, 0.05),
    }
    if rng is not None and n_boot > 0:
        idx = rng.integers(0, n, size=(n_boot, n))
        boot = x[idx]
        out["se_q05"] = np.std(np.quantile(boot, 0.05, axis=1), ddof=1)
        boot.sort(axis=1)
        k = max(1, int(np.floor(0.05 * n)))
        out["se_es05"] = np.std(boot[:, :k].mean(axis=1), ddof=1)
    return out


def loglog_slope(N, y):
    """Least-squares slope of log(y) on log(N)."""
    return np.polyfit(np.log(N), np.log(y), 1)[0]
