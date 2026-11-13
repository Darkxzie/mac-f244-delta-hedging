"""
Exact simulation of geometric Brownian motion (GBM).

    dS_t = m S_t dt + sigma S_t dW_t
    =>  S_{t+dt} = S_t * exp((m - sigma^2/2) dt + sigma sqrt(dt) Z),  Z ~ N(0,1)

This update is EXACT in distribution for any step size (no discretisation
error), because ln S is Brownian motion with drift.

Which probability measure?
    m = mu  (real-world drift)  -> physical measure P   (used for hedging P&L)
    m = r   (risk-free rate)    -> risk-neutral measure Q (used for pricing checks)
"""
import numpy as np


def simulate_gbm(S0, m, sigma, T, n_steps, n_paths, rng):
    """
    Return an array of shape (n_paths, n_steps + 1) with column 0 equal to S0.

    rng : numpy.random.Generator (pass a seeded one for reproducibility)
    """
    dt = T / n_steps
    Z = rng.standard_normal((n_paths, n_steps))
    log_increments = (m - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z
    log_paths = np.concatenate(
        [np.zeros((n_paths, 1)), np.cumsum(log_increments, axis=1)], axis=1
    )
    return S0 * np.exp(log_paths)


def time_grid(T, n_steps):
    """t_k = k * T / n_steps, k = 0..n_steps."""
    return np.linspace(0.0, T, n_steps + 1)
