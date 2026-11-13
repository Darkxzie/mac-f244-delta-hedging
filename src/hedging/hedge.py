"""
Discrete, self-financing delta hedge of a SHORT European call.

Position of the hedger (the option seller), on rebalancing dates
t_k = k*dt, k = 0..N-1, dt = T/N:

    phi_k  shares held over (t_k, t_{k+1}]   = Delta(t_k, S_k; sigma_hedge)
    B_k    cash (bank account) just after rebalancing at t_k

Bookkeeping (report eqs (3)–(5)); c = proportional cost per unit of traded value:

    t_0 :  B_0 = V_0 - phi_0 S_0 - c |phi_0| S_0          (premium in, buy shares)
    t_k :  B_k = B_{k-1} e^{r dt} - (phi_k - phi_{k-1}) S_k - c |phi_k - phi_{k-1}| S_k
    T   :  liquidate shares and pay the option's cash payoff
           PnL_T = B_{N-1} e^{r dt} + phi_{N-1} S_T - c |phi_{N-1}| S_T - (S_T - K)^+

SIGN CONVENTION: PnL_T > 0 means the seller (hedger) ends with money left over;
PnL_T < 0 is a loss. PnL_T is measured in currency units at time T.

Because the trades do not depend on c (delta ignores costs), PnL is linear in c:
    PnL_T(c) = PnL_T(0) - c * TV,  TV = sum_k |trade_k| S_k e^{r(T - t_k)}  (incl. liquidation)
`traded_value_fv` below is TV, so one simulation serves every cost level.
"""
import numpy as np
import pandas as pd

from .black_scholes import call_price, call_delta, gamma


def hedge_short_call(paths, K, T, r, sigma_hedge, premium=None, cost=0.0,
                     step=1, liquidate_cost=True):
    """
    Delta-hedge a short call along each simulated path.

    paths         array (n_paths, M+1) on a fine grid t_j = j*T/M
    step          rebalance every `step` fine steps -> N = M/step rebalances
    sigma_hedge   volatility used to compute delta (and, by default, the premium)
    premium       price received at t=0; default = BS price at sigma_hedge
    cost          proportional cost per side (0.001 = 10 basis points)
    liquidate_cost  if True, the terminal sale of the stock also pays cost

    Returns dict with arrays (one entry per path):
        pnl              terminal hedging P&L in currency at T (seller's view)
        cost_fv          transaction costs paid, carried forward to T
        setup_unwind_cost_fv  part of cost_fv from the initial purchase and final sale
        traded_value_fv  TV, so that pnl(c') = pnl(0) - c' * TV
    and scalars premium, n_rebalances.
    """
    M = paths.shape[1] - 1
    if M % step != 0:
        raise ValueError("step must divide the number of fine time steps")
    S = paths[:, ::step]                     # prices on the rebalancing grid
    N = S.shape[1] - 1
    dt = T / N
    growth = np.exp(r * dt)                  # one period of interest on cash
    S0 = S[:, 0]
    if premium is None:
        premium = float(call_price(S0[0], K, T, r, sigma_hedge))

    cash = np.full(S.shape[0], premium, dtype=float)
    phi_prev = np.zeros(S.shape[0])
    cost_fv = np.zeros(S.shape[0])
    traded_fv = np.zeros(S.shape[0])

    for k in range(N):                       # rebalancing dates t_0 ... t_{N-1}
        t_k = k * dt
        S_k = S[:, k]
        phi = call_delta(S_k, K, T - t_k, r, sigma_hedge)
        trade = phi - phi_prev               # shares bought (+) or sold (-)
        trade_value = np.abs(trade) * S_k
        cash -= trade * S_k                  # pay for shares bought
        cash -= cost * trade_value           # proportional transaction cost
        fv_factor = np.exp(r * (T - t_k))
        cost_fv += cost * trade_value * fv_factor
        if k == 0:
            setup_unwind = cost * trade_value * fv_factor     # cost of the initial purchase
        traded_fv += trade_value * fv_factor
        cash *= growth                       # interest accrues to t_{k+1}
        phi_prev = phi

    S_T = S[:, -1]
    liquidation_value = phi_prev * S_T       # phi >= 0 for a call delta
    cash += liquidation_value
    traded_fv += liquidation_value
    if liquidate_cost:
        cash -= cost * liquidation_value
        cost_fv += cost * liquidation_value
        setup_unwind = setup_unwind + cost * liquidation_value
    payoff = np.maximum(S_T - K, 0.0)
    pnl = cash - payoff
    return {"pnl": pnl, "cost_fv": cost_fv, "traded_value_fv": traded_fv,
            "setup_unwind_cost_fv": setup_unwind,   # costs NOT due to rebalancing
            "premium": premium, "n_rebalances": N}


def pnl_gains_form(paths, K, T, r, sigma_hedge, premium=None, step=1):
    """
    Independent (frictionless) formula used only to VALIDATE the bookkeeping:
        PnL_T = V_0 e^{rT} + sum_k phi_k (S_{k+1} - S_k e^{r dt}) e^{r(T - t_{k+1})} - (S_T-K)^+
    i.e. premium grown at r plus the discounted-gains of the stock position.
    """
    S = paths[:, ::step]
    N = S.shape[1] - 1
    dt = T / N
    if premium is None:
        premium = float(call_price(S[0, 0], K, T, r, sigma_hedge))
    t = np.arange(N) * dt
    phi = call_delta(S[:, :-1], K, T - t, r, sigma_hedge)
    excess = S[:, 1:] - S[:, :-1] * np.exp(r * dt)
    weights = np.exp(r * (T - t - dt))
    gains = np.sum(phi * excess * weights, axis=1)
    return premium * np.exp(r * T) + gains - np.maximum(S[:, -1] - K, 0.0)


def hedge_ledger(path, K, T, r, sigma_hedge, premium=None, cost=0.0):
    """
    Step-by-step ledger for ONE path (1-D array of prices on the rebalancing
    grid). Used for the hand-checkable accounting example in the viva notes.
    """
    path = np.asarray(path, float)
    N = len(path) - 1
    dt = T / N
    if premium is None:
        premium = float(call_price(path[0], K, T, r, sigma_hedge))
    rows, cash, phi_prev = [], premium, 0.0
    for k in range(N + 1):
        t_k, S_k = k * dt, path[k]
        if k > 0:
            cash_in = cash
            cash = cash * np.exp(r * dt)
            interest = cash - cash_in
        else:
            interest = 0.0
        if k < N:
            phi = float(call_delta(S_k, K, T - t_k, r, sigma_hedge))
            payoff = 0.0
        else:                                  # maturity: sell everything
            phi = 0.0
            payoff = max(S_k - K, 0.0)
        trade = phi - phi_prev
        tc = cost * abs(trade) * S_k
        cash = cash - trade * S_k - tc - payoff
        rows.append(dict(k=k, t=t_k, S=S_k, delta=phi, trade=trade,
                         trade_cash=-trade * S_k, interest=interest,
                         tcost=tc, payoff=payoff, cash_after=cash))
        phi_prev = phi
    df = pd.DataFrame(rows)
    df.attrs["premium"] = premium
    df.attrs["pnl"] = cash                     # all stock sold: cash is the P&L
    return df


def predicted_pnl_misspecified(paths, K, T, r, sigma_true, sigma_hedge):
    """
    Continuous-hedging approximation when pricing AND hedging at sigma_hedge
    while the stock really has volatility sigma_true (El Karoui et al., 1998):
        PnL_T ~= 1/2 * int_0^T e^{r(T-t)} Gamma_h(t,S_t) S_t^2 (sigma_h^2 - sigma^2) dt
    evaluated as a left Riemann sum on the fine grid of `paths`.
    """
    M = paths.shape[1] - 1
    dt = T / M
    t = np.arange(M) * dt
    S = paths[:, :-1]
    G = gamma(S, K, T - t, r, sigma_hedge)
    integrand = 0.5 * np.exp(r * (T - t)) * G * S**2 * (sigma_hedge**2 - sigma_true**2)
    return np.sum(integrand * dt, axis=1)
