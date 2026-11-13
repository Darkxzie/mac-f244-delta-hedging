"""
Run all validation checks and save results.

    python scripts/run_validation.py          # writes results/validation/*
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd
from hedging.validation import run_all

out = ROOT / "results" / "validation"
out.mkdir(parents=True, exist_ok=True)
checks, ledgers = run_all(seed=7)
checks.to_csv(out / "validation_checks.csv", index=False)
for c, df in ledgers.items():
    df.to_csv(out / f"manual_ledger_cost{c}.csv", index=False)

pd.set_option("display.width", 160, "display.max_colwidth", 60)
print(checks.to_string(index=False))
for c, df in ledgers.items():
    print(f"\nManual ledger, cost per side = {c}, premium = {df.attrs['premium']:.6f}, "
          f"terminal P&L = {df.attrs['pnl']:.6f}")
    print(df.round(6).to_string(index=False))
n_fail = (~checks.passed).sum()
print(f"\n{len(checks) - n_fail}/{len(checks)} checks passed")
sys.exit(1 if n_fail else 0)
