"""
Run experiments A–E, save machine-readable tables and figures.

    python scripts/run_experiments.py --mode quick    # ~10-20 s, 4,000 paths
    python scripts/run_experiments.py --mode full     # ~1-3 min, 40,000 paths

Outputs go to results/<mode>/ : tables/*.csv, figures/*.png|pdf,
arrays.npz (raw P&L samples, full mode), run_info.json (config, versions, time).
"""
import argparse
import json
import platform
import sys
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np
import pandas as pd
import scipy
import matplotlib

from hedging.experiments import Config, run_base_experiments, run_regime_experiments
from hedging.realdata import run_calibration, run_backtest
from hedging import plotting


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["quick", "full"], default="quick")
    ap.add_argument("--seed", type=int, default=2026)
    args = ap.parse_args()
    cfg = Config.quick() if args.mode == "quick" else Config()
    cfg.seed = args.seed

    out = ROOT / "results" / args.mode
    (out / "tables").mkdir(parents=True, exist_ok=True)
    (out / "figures").mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    log = lambda m: print(f"[{time.time() - t0:6.1f}s] {m}", flush=True)

    log(f"mode={cfg.mode} paths={cfg.n_paths} fine steps M={cfg.M} seed={cfg.seed}")
    tables, arrays = run_base_experiments(cfg, log)
    tables.update(run_regime_experiments(cfg, log))
    tables["E_calibration"] = run_calibration(ROOT / "data/vega_stocks_monthly.csv",
                                              ROOT / "data/aapl_daily_plotly.csv")
    bt, bt_summary = run_backtest(ROOT / "data/aapl_daily_plotly.csv")
    tables["E_backtest_windows"], tables["E_backtest_summary"] = bt, bt_summary
    log("real-data example done")

    # Which statistics happen to be monotone in N in THIS sample? (reported, not assumed)
    A = tables["A_frequency"].sort_values("N")
    tables["A_monotonicity"] = pd.DataFrame([{
        "stat": s, "monotone_decreasing_in_N": bool(np.all(np.diff(v) < 0))}
        for s, v in [("std", A["std"]), ("rmse", A["rmse"]), ("abs_mean", A["mean"].abs()),
                     ("abs_q05", A["q05"].abs()), ("abs_es05", A["es05"].abs())]])

    for name, df in tables.items():
        df.to_csv(out / "tables" / f"{name}.csv", index=False)
    if args.mode == "full":
        np.savez_compressed(out / "arrays.npz", **arrays)

    fig = out / "figures"
    plotting.fig_frequency(tables["A_frequency"], arrays, fig, cfg.T)
    plotting.fig_misspecification(tables["B_misspecification"], arrays, fig, cfg.sigma, cfg.M)
    plotting.fig_costs(tables["C_costs"], fig)
    plotting.fig_regimes(tables["D_regimes"], fig)
    plotting.fig_realdata(bt, fig)
    log("figures written")

    info = {"config": {k: (v if not isinstance(v, tuple) else list(v)) for k, v in asdict(cfg).items()},
            "runtime_seconds": round(time.time() - t0, 1),
            "finished_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "python": platform.python_version(), "numpy": np.__version__,
            "scipy": scipy.__version__, "pandas": pd.__version__,
            "matplotlib": matplotlib.__version__, "platform": platform.platform()}
    (out / "run_info.json").write_text(json.dumps(info, indent=2, default=str))
    log(f"done -> {out}")


if __name__ == "__main__":
    main()
