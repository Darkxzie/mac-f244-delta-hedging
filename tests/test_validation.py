"""pytest entry point: every validation check must pass.   Run:  pytest -q tests/"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np
import pytest
from hedging.validation import run_all, manual_example
from hedging import hedge_short_call

CHECKS, LEDGERS = run_all(seed=7)


@pytest.mark.parametrize("i", range(len(CHECKS)))
def test_check(i):
    row = CHECKS.iloc[i]
    assert row.passed, f"{row.check}: value {row.value} (tol {row.tolerance})"


def test_cost_linearity():
    """P&L(c) = P&L(0) - c * TV, exactly, because trades ignore costs."""
    path, p = manual_example()
    a = hedge_short_call(path[None, :], p["K"], p["T"], p["r"], p["sigma"], cost=0.0)
    b = hedge_short_call(path[None, :], p["K"], p["T"], p["r"], p["sigma"], cost=0.003)
    assert np.isclose(b["pnl"][0], a["pnl"][0] - 0.003 * a["traded_value_fv"][0], atol=1e-12)
