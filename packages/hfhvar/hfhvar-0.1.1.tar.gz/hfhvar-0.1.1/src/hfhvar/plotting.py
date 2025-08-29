# src/hfhvar/plotting.py
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Optional, Tuple

def _safe_limits(*arrays: np.ndarray, pad: float = 0.1) -> Tuple[float, float]:
    data = np.concatenate([np.ravel(a[np.isfinite(a)]) for a in arrays if a is not None])
    if data.size == 0:
        return (-1.0, 1.0)
    lo, hi = float(data.min()), float(data.max())
    if lo == hi:
        span = 1.0 if lo == 0.0 else abs(lo) * 0.1
        return lo - span, hi + span
    span = hi - lo
    return lo - pad * span, hi + pad * span

def _align_bands(irf: np.ndarray, band: np.ndarray) -> np.ndarray:
    """Ensure band has same shape as irf (K x P). If it's (P x K), transpose."""
    if band.shape == irf.shape:
        return band
    if band.shape == irf.shape[::-1]:
        return band.T
    raise ValueError(f"Band shape {band.shape} not compatible with IRF {irf.shape}")

def plot_irfs(
    irf: np.ndarray,
    lo: np.ndarray,
    hi: np.ndarray,
    periods_per_quarter: int = 66,
    var_names: Optional[List[str]] = None,
    mode: str = "quarterly",   # 'quarterly' or 'daily'
    pad: float = 0.1,
    ci_label: str = "68% CI"   # legend label for the shaded band
):
    """
    Plot IRFs with shaded confidence bands (gray). Accepts IRF as (K x P).
    Bands can be (K x P) or (P x K); auto-aligned.
    mode='quarterly' → sample every `periods_per_quarter`; 'daily' → full path.
    """
    if mode not in ("quarterly", "daily"):
        raise ValueError("mode must be 'quarterly' or 'daily'")

    irf = np.asarray(irf)
    lo = _align_bands(irf, np.asarray(lo))
    hi = _align_bands(irf, np.asarray(hi))

    K, P = irf.shape
    for k in range(K):
        if mode == "quarterly":
            x_idx = np.arange(0, P, periods_per_quarter)
            y  = irf[k, x_idx]
            yl = lo[k,  x_idx]
            yh = hi[k,  x_idx]
            x = np.arange(y.size)
            xlabel = "Quarters"
        else:
            x = np.arange(P)
            y  = irf[k, :]
            yl = lo[k,  :]
            yh = hi[k,  :]
            xlabel = "Days"

        ylo, yhi = _safe_limits(y, yl, yh, pad=pad)

        fig, ax = plt.subplots(figsize=(7, 4))
        ax.grid(True, alpha=0.3)
        # shaded CI in gray
        ax.fill_between(x, yl, yh, alpha=0.3, color="0.7", label=ci_label, linewidth=0)
        # IRF line
        ax.plot(x, y, label='IRF')
        ax.axhline(0.0, linestyle=':', color='k', linewidth=1)
        ax.set_ylim(ylo, yhi)
        ax.set_xlabel(xlabel)
        title = var_names[k] if var_names else f"Variable {k}"
        ax.set_title(title)
        ax.legend()
        plt.tight_layout()
        plt.show()
