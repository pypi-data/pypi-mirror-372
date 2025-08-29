# src/hfhvar/bootstrap.py
import numpy as np
from typing import Tuple
from .estimation import HVARls1
from .identification import build_daily_B_like_original
from .simulation import simulate_irf
from .config import ModelConfig

# try tqdm; fallback to simple prints
try:
    from tqdm.auto import tqdm
    _HAS_TQDM = True
except Exception:
    _HAS_TQDM = False

def _progress_iter(n: int, enabled: bool):
    if not enabled:
        return range(n)
    if _HAS_TQDM:
        return tqdm(range(n), desc="Bootstrap", total=n)
    # simple fallback
    class _Iter:
        def __init__(self, n):
            self.n = n
            self.i = 0
        def __iter__(self):
            return self
        def __next__(self):
            if self.i >= self.n:
                print()  # newline at end
                raise StopIteration
            if self.i == 0:
                print(f"Bootstrapping {self.n} draws...", end="", flush=True)
            self.i += 1
            # update inline every draw
            print(f"\rBootstrapping {self.n} draws... {self.i}/{self.n}", end="", flush=True)
            return self.i - 1
    return _Iter(n)

def residual_bootstrap_irf(y: np.ndarray, cfg: ModelConfig) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    fit = HVARls1(
        y, 1, cfg.p_d,
        cfg.Q2, cfg.Q3, cfg.Q4, cfg.Q5, cfg.Q6, cfg.Q7,
        cfg.Q8, cfg.Q9, cfg.Q10, cfg.Q11, cfg.Q12,
        cfg.ridge_lambda, cfg.use_pinv_fallback
    )

    extras = [fit.Bhat_d2, fit.Bhat_d3, fit.Bhat_d4, fit.Bhat_d5, fit.Bhat_d6,
              fit.Bhat_d7, fit.Bhat_d8, fit.Bhat_d9, fit.Bhat_d10, fit.Bhat_d11, fit.Bhat_d12]

    B_full = build_daily_B_like_original(fit.Bhat_dh, extras, fit.K, cfg.p_d)

    # Baseline IRF
    irf = simulate_irf(
        B_full, fit.Sigma, fit.K, cfg.periods_per_quarter, cfg.p_d,
        cfg.period_display_quarters, cfg.shock_index, cfg.shock_size
    )

    P = cfg.periods_per_quarter * cfg.period_display_quarters
    draws = cfg.bootstrap_draws
    boot = np.empty((draws, P, fit.K))
    rng = np.random.default_rng(cfg.seed)

    # center residuals
    U = fit.Uhat
    U_c = (U.T - U.mean(axis=1)).T

    p_days = cfg.periods_per_quarter * cfg.p_d
    width = fit.K * p_days

    for b in _progress_iter(draws, cfg.show_progress):
        choices = rng.integers(low=0, high=U_c.shape[1], size=y.shape[0])
        U_star = U_c[:, choices]

        y_b = y.copy()
        Z = np.zeros((width, y.shape[0]))
        Z[:, 0] = y[:p_days, :][::-1].reshape(width)

        for t in range(p_days, y.shape[0]):
            y_b[t, :] = B_full @ Z[:, t - p_days] + U_star[:, t-1]
            Z[:, t - p_days + 1] = y_b[t - p_days + 1:t+1, :][::-1].reshape(width)

        fit_b = HVARls1(
            y_b, 1, cfg.p_d,
            cfg.Q2, cfg.Q3, cfg.Q4, cfg.Q5, cfg.Q6, cfg.Q7,
            cfg.Q8, cfg.Q9, cfg.Q10, cfg.Q11, cfg.Q12,
            cfg.ridge_lambda, cfg.use_pinv_fallback
        )
        extras_b = [fit_b.Bhat_d2, fit_b.Bhat_d3, fit_b.Bhat_d4, fit_b.Bhat_d5, fit_b.Bhat_d6,
                    fit_b.Bhat_d7, fit_b.Bhat_d8, fit_b.Bhat_d9, fit_b.Bhat_d10, fit_b.Bhat_d11, fit_b.Bhat_d12]
        B_full_b = build_daily_B_like_original(fit_b.Bhat_dh, extras_b, fit_b.K, cfg.p_d)

        irf_b = simulate_irf(
            B_full_b, fit.Sigma, fit.K, cfg.periods_per_quarter, cfg.p_d,
            cfg.period_display_quarters, cfg.shock_index, cfg.shock_size
        ).T
        boot[b, :, :] = irf_b

    lo = np.percentile(boot, cfg.ci_low, axis=0)
    hi = np.percentile(boot, cfg.ci_high, axis=0)
    return irf, lo, hi
