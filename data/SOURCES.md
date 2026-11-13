# Data provenance

Both files are **secondary-source historical prices**. They are used only in Experiment E
(volatility calibration and one historical-path hedging backtest). Experiments A–D use
**simulated** prices only.

| File | Origin | Coverage | Frequency | Column used | SHA-256 |
|---|---|---|---|---|---|
| `vega_stocks_monthly.csv` | `stocks` dataset of the vega-datasets collection, saved from the Python package `vega_datasets` 0.9.0 (`from vega_datasets import data; data.stocks()`); the package's reference URL is https://cdn.jsdelivr.net/npm/vega-datasets@v1.29.0/data/stocks.csv | AAPL, AMZN, IBM, MSFT 2000-01 → 2010-03; GOOG 2004-08 → 2010-03 | one observation per month (the dataset's description says "daily", but the dates are monthly) | `price` | `e0cf2d720c043287738316a130e6b921c027a54719931644e100bd6dc048cd02` |
| `aapl_daily_plotly.csv` | plotly/datasets GitHub repository, file `finance-charts-apple.csv`, downloaded 13 Nov 2026 from https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv | AAPL 2015-02-17 → 2017-02-16 (506 trading days) | daily | `AAPL.Adjusted` (adjusted close) | `24c7604edfd5afe862ddb9f9535e2fd7351f43711bfc442bca52055e15e37bcd` |

The original vendor of the prices is not documented inside either file (they are commonly
described as Yahoo Finance extracts). They are adequate for a classroom illustration of
calibration and hedging along a real path. Do not cite them as an authoritative market-data source.
If your course requires primary data, download a series yourself (for example from an exchange
website), save it as CSV with `Date` and an adjusted-close column, and point
`hedging.realdata.load_aapl` at it.

## Preprocessing and conventions

* Log returns $x_i=\ln(S_i/S_{i-1})$ on consecutive observations. Missing values are dropped (none occur).
* Annualised volatility $\hat\sigma = \text{sd}(x)\sqrt{m}$ with $m=12$ (monthly) or $m=252$ (daily).
  Standard error $\hat\sigma/\sqrt{2n}$ assumes normal returns.
* Drift estimate $\hat\mu = 12\bar x+\hat\sigma^2/2$ (monthly; analogous for daily), with SE $\text{sd}(x)\,m/\sqrt n$.
* Prices in the vega file are **not** documented as dividend-adjusted; the AAPL file uses the adjusted close.
* Backtest: risk-free rate fixed at 0.5% p.a. (an assumption, not data); 63-trading-day options;
  hedge volatility = trailing 63-day realised volatility known at the start date.
