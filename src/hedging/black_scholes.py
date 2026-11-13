"""
Black–Scholes formulas for a European call/put on a non-dividend-paying stock.

Notation (matches the report, Section 2):
    S      spot price                         [currency units]
    K      strike                             [currency units]
    tau    time to maturity, T - t            [years]
    r      continuously compounded risk-free rate     [1/year]
    sigma  volatility of log-returns          [1/sqrt(year)]

    d1 = [ln(S/K) + (r + sigma^2/2) tau] / (sigma sqrt(tau))
    d2 = d1 - sigma sqrt(tau)

    Call  C = S N(d1) - K e^{-r tau} N(d2)
    Put   P = K e^{-r tau} N(-d2) - S N(-d1)
    Delta_call = dC/dS = N(d1)
    Gamma      = phi(d1) / (S sigma sqrt(tau))
    Vega       = S phi(d1) sqrt(tau)

Maturity (tau = 0) is handled explicitly: the price equals the payoff and the
delta equals the indicator 1{S > K} (we use 1/2 exactly at S = K; this value is
never used by the hedger, who does not rebalance at T).
All functions accept NumPy arrays and broadcast.
"""
import numpy as np
from scipy.stats import norm


def _d1_d2(S, K, tau, r, sigma):
    """Return (d1, d2). Caller must ensure tau > 0 and sigma > 0."""
    sqrt_tau = np.sqrt(tau)
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * tau) / (sigma * sqrt_tau)
    return d1, d1 - sigma * sqrt_tau


def call_price(S, K, tau, r, sigma):
    """Black–Scholes European call price; equals max(S-K,0) when tau == 0."""
    S, tau = np.asarray(S, float), np.asarray(tau, float)
    payoff = np.maximum(S - K, 0.0)
    live = tau > 0
    if not np.any(live):
        return payoff
    tau_safe = np.where(live, tau, 1.0)          # avoid divide-by-zero warnings
    d1, d2 = _d1_d2(S, K, tau_safe, r, sigma)
    price = S * norm.cdf(d1) - K * np.exp(-r * tau_safe) * norm.cdf(d2)
    return np.where(live, price, payoff)


def put_price(S, K, tau, r, sigma):
    """Black–Scholes European put price; equals max(K-S,0) when tau == 0."""
    S, tau = np.asarray(S, float), np.asarray(tau, float)
    payoff = np.maximum(K - S, 0.0)
    live = tau > 0
    if not np.any(live):
        return payoff
    tau_safe = np.where(live, tau, 1.0)
    d1, d2 = _d1_d2(S, K, tau_safe, r, sigma)
    price = K * np.exp(-r * tau_safe) * norm.cdf(-d2) - S * norm.cdf(-d1)
    return np.where(live, price, payoff)


def call_delta(S, K, tau, r, sigma):
    """dC/dS = N(d1); at maturity the limit 1{S>K} (1/2 at S == K)."""
    S, tau = np.asarray(S, float), np.asarray(tau, float)
    at_expiry = np.where(S > K, 1.0, np.where(S < K, 0.0, 0.5))
    live = tau > 0
    if not np.any(live):
        return at_expiry
    tau_safe = np.where(live, tau, 1.0)
    d1, _ = _d1_d2(S, K, tau_safe, r, sigma)
    return np.where(live, norm.cdf(d1), at_expiry)


def gamma(S, K, tau, r, sigma):
    """d^2C/dS^2 = phi(d1)/(S sigma sqrt(tau)); defined only for tau > 0."""
    d1, _ = _d1_d2(S, K, tau, r, sigma)
    return norm.pdf(d1) / (S * sigma * np.sqrt(tau))


def vega(S, K, tau, r, sigma):
    """dC/dsigma = S phi(d1) sqrt(tau); defined only for tau > 0."""
    d1, _ = _d1_d2(S, K, tau, r, sigma)
    return S * norm.pdf(d1) * np.sqrt(tau)


def leland_sigma(sigma, cost_per_side, dt):
    """
    Leland (1985) transaction-cost-adjusted volatility for a SHORT option position:
        sigma_L^2 = sigma^2 * (1 + sqrt(2/pi) * k / (sigma * sqrt(dt)))
    where k is the ROUND-TRIP proportional cost. Our simulator charges
    `cost_per_side` on each trade, so k = 2 * cost_per_side.
    """
    k = 2.0 * cost_per_side
    return sigma * np.sqrt(1.0 + np.sqrt(2.0 / np.pi) * k / (sigma * np.sqrt(dt)))
