"""
Experiment E: small real-data example (SECONDARY-SOURCE historical prices).

Data (copied into data/, provenance and SHA-256 hashes in data/SOURCES.md):
  * data/vega_stocks_monthly.csv : vega-datasets `stocks.csv` (via the Python
    package vega_datasets 0.9.0): MONTHLY prices of AAPL, AMZN, GOOG, IBM, MSFT,
    Jan-2000 .. Mar-2010. The file's own description says "daily", but the
    observations are one per month; we treat them as monthly (annualise with 12).
  * data/aapl_daily_plotly.csv : plotly/datasets `finance-charts-apple.csv`,
    DAILY AAPL OHLC + "AAPL.Adjusted", 17-Feb-2015 .. 16-Feb-2017.

E1  Volatility calibration: log returns, sigma_hat = sd * sqrt(periods/year),
    SE(sigma_hat) ~= sigma_hat / sqrt(2 n) (normal approximation).
E2  Historical-path hedge backtest (AAPL daily): on each start day we SELL a
    63-trading-day at-the-money call, priced and hedged with sigma_hedge =
    trailing 63-day historical volatility, and rebalance daily ALONG THE ACTUAL
    PRICE PATH. No market option quotes are used: the premium is a model price,
    so this measures hedging error versus realised volatility, not trading profit.
"""
import numpy as np
import pandas as pd

from .black_scholes import call_price
from .hedge import hedge_short_call


def calibrate(prices, periods_per_year, label, source):
    lr = np.diff(np.log(np.asarray(prices, float)))
    n = len(lr)
    sd = lr.std(ddof=1)
    sig = sd * np.sqrt(periods_per_year)
    mu_hat = lr.mean() * periods_per_year + 0.5 * sig**2      # GBM drift estimate
    return dict(asset=label, source=source, n_returns=n,
                sigma_annual=sig, se_sigma=sig / np.sqrt(2 * n),
                # SE of the drift = sigma / sqrt(years of data): drift is hard to estimate
                mu_annual=mu_hat, se_mu=sd * periods_per_year / np.sqrt(n),
                periods_per_year=periods_per_year)


def load_vega(path):
    df = pd.read_csv(path, parse_dates=["date"])
    return df.pivot(index="date", columns="symbol", values="price")


def load_aapl(path):
    df = pd.read_csv(path, parse_dates=["Date"]).set_index("Date")
    return df["AAPL.Adjusted"].astype(float)


def run_calibration(vega_path, aapl_path):
    rows = []
    wide = load_vega(vega_path)
    for sym in ["AAPL", "AMZN", "GOOG", "IBM", "MSFT"]:
        s = wide[sym].dropna()
        row = calibrate(s.values, 12, sym, "vega-datasets stocks.csv (monthly)")
        row.update(start=s.index[0].date(), end=s.index[-1].date())
        rows.append(row)
    a = load_aapl(aapl_path)
    row = calibrate(a.values, 252, "AAPL", "plotly/datasets (daily, adjusted)")
    row.update(start=a.index[0].date(), end=a.index[-1].date())
    rows.append(row)
    return pd.DataFrame(rows)


def run_backtest(aapl_path, window=63, r=0.005, cost=0.001):
    a = load_aapl(aapl_path)
    S = a.values
    lr = np.diff(np.log(S))
    T = window / 252
    rows = []
    for i in range(window, len(S) - window):
        sig_h = lr[i - window:i].std(ddof=1) * np.sqrt(252)       # known at start
        path = S[i:i + window + 1][None, :]                        # 64 prices
        sig_real = lr[i:i + window].std(ddof=1) * np.sqrt(252)     # known after
        out = hedge_short_call(path, S[i], T, r, sig_h)
        pnl0 = out["pnl"][0]
        pnlc = pnl0 - cost * out["traded_value_fv"][0]
        rows.append(dict(start=a.index[i].date(), S0=S[i], sigma_hedge=sig_h,
                         sigma_realised=sig_real, premium=out["premium"],
                         pnl=pnl0, pnl_with_cost=pnlc, pnl_over_premium=pnl0 / out["premium"],
                         var_gap=sig_h**2 - sig_real**2))
    bt = pd.DataFrame(rows)
    non_overlap = bt.iloc[::window]
    summ = pd.DataFrame([{
        "n_windows_overlapping": len(bt), "n_windows_non_overlapping": len(non_overlap),
        "r_assumed": r, "cost_per_side": cost, "window_days": window,
        "mean_pnl_over_premium": bt.pnl_over_premium.mean(),
        "frac_positive": (bt.pnl > 0).mean(),
        "corr_pnl_vs_var_gap": np.corrcoef(bt.pnl, bt.var_gap)[0, 1],
        "mean_pnl_over_premium_nonoverlap": non_overlap.pnl_over_premium.mean(),
        "corr_nonoverlap": np.corrcoef(non_overlap.pnl, non_overlap.var_gap)[0, 1],
        "mean_cost_drag": (bt.pnl - bt.pnl_with_cost).mean(),
    }])
    return bt, summ
