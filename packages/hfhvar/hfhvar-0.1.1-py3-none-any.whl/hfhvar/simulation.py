import numpy as np

def simulate_irf(B_full: np.ndarray,
                 Sigma: np.ndarray,
                 K: int,
                 periods_per_quarter: int,
                 p_d: int,
                 period_display_quarters: int,
                 shock_index: int,
                 shock_size: float) -> np.ndarray:
    p_days = periods_per_quarter * p_d
    width = K * p_days
    assert B_full.shape[1] == width, f"B_full width {B_full.shape[1]} != expected {width}"

    T = (period_display_quarters * periods_per_quarter) + p_days + 1
    Z = np.zeros((width, T - periods_per_quarter))
    y = np.zeros((T, K))

    chol = np.linalg.cholesky(Sigma)
    U = np.zeros(width)
    U[shock_index] = shock_size / chol[shock_index, shock_index]
    U[:K] = chol @ U[:K]

    Z[:, 0] = U
    y[p_days - 1, :] = U[:K]

    for t in range(p_days, T-1):
        y[t, :] = B_full @ Z[:, t - p_days]
        Z[:, t - p_days + 1] = y[t - p_days + 1:t+1, :][::-1].reshape(width)

    y = y.T[:, p_days - 1:]
    return y[:, :periods_per_quarter * period_display_quarters]
