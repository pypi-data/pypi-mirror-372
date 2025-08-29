import numpy as np
from numpy.linalg import inv
from dataclasses import dataclass
from typing import Optional, Tuple

@dataclass
class HvarFit:
    # match your original returns
    Bhat_dh: np.ndarray      # first 4K block: [K | weekly | monthly | rest]
    Bhat_d2: Optional[np.ndarray]
    Bhat_d3: Optional[np.ndarray]
    Bhat_d4: Optional[np.ndarray]
    Bhat_d5: Optional[np.ndarray]
    Bhat_d6: Optional[np.ndarray]
    Bhat_d7: Optional[np.ndarray]
    Bhat_d8: Optional[np.ndarray]
    Bhat_d9: Optional[np.ndarray]
    Bhat_d10: Optional[np.ndarray]
    Bhat_d11: Optional[np.ndarray]
    Bhat_d12: Optional[np.ndarray]
    Sigma: np.ndarray
    Uhat: np.ndarray
    Traw: int
    K: int
    Zhet: np.ndarray
    corr_abs_mean: float
    p_d: int

def _p_days(p_d: int, ppq: int = 66) -> int:
    """Total daily lags depth in the state = 66 * p_d."""
    return ppq * int(p_d)

def _resolve_flags(p_d: int, flags: Tuple[int, ...]) -> Tuple[int, ...]:
    """
    Auto-activate Q2..Qp_d (1-based quarters) so user can set p_d only.
    `flags` = (Q2..Q12). We set the first (p_d-1) entries to 1.
    """
    lst = list(flags)
    need = max(0, min(p_d - 1, len(lst)))
    for i in range(need):
        lst[i] = 1
    return tuple(lst)

def _ridge_inverse(M: np.ndarray, lam: float) -> np.ndarray:
    """Tikhonov-regularized inverse for stability."""
    K = M.shape[0]
    return inv(M + lam * np.eye(K))

def HVARls1(y_d: np.ndarray,
            include_quarterly: int,
            p_d: int,
            Q2: int, Q3: int, Q4: int, Q5: int, Q6: int, Q7: int,
            Q8: int, Q9: int, Q10: int, Q11: int, Q12: int,
            ridge_lambda: float = 1e-8,
            use_pinv_fallback: bool = True) -> HvarFit:
    """
    HF-HVAR OLS with your original block structure:
      Z_het rows = [Z[0:K]; weekly(1..4); monthly(5..21); rest(22..65); Q2(66); Q3(66); ...].
    Auto-activates Q2..Qp_d so you can just set p_d.
    """
    y_d = np.asarray(y_d, dtype=np.float64)
    Traw, K = y_d.shape
    ppq = 66
    p_days = _p_days(p_d, ppq)

    # AUTO: turn on Q2..Qp_d
    flags = _resolve_flags(p_d, (Q2, Q3, Q4, Q5, Q6, Q7, Q8, Q9, Q10, Q11, Q12))

    if Traw <= p_days + 5:
        raise ValueError(f"Too few observations ({Traw}) for p_d={p_d} (needs > {p_days}).")

    # build stacked daily lags up to p_days
    r = y_d.copy()
    rhs = []
    pad = np.full((1, K), np.nan)
    for _ in range(p_days):
        r = np.vstack((pad, r))
        rhs.append(r[:Traw, :])
    Z = np.hstack(rhs)[p_days:, :].T   # (K*p_days, T-p_days)
    Y = y_d[p_days:, :].T              # (K, T-p_days)

    # drop any time columns with nans/infs
    mask = np.isfinite(Z).all(axis=0) & np.isfinite(Y).all(axis=0)
    if not mask.all():
        Z = Z[:, mask]
        Y = Y[:, mask]

    # heterogeneous sums matrix C
    # base quarter: 3 blocks (weekly 4, monthly 17, rest 44) = 65 days
    n_extra = max(0, p_d - 1)  # potential number of extra 66-day quarters
    n_blocks = 3 + sum(flags[:n_extra])  # only count active extra flags
    C = np.zeros((K*n_blocks, Z.shape[1]))

    def sum_block(start_mult: int, length: int, j: int, i: int) -> float:
        idx0 = start_mult*K + j
        s = 0.0
        for m in range(length):
            s += Z[idx0 + m*K, i]
        return s

    # base quarter (first 65 daily lags)
    # rows 0..K-1: weekly(1..4)
    # rows K..2K-1: monthly remainder(5..21)
    # rows 2K..3K-1: rest(22..65)
    for i in range(Z.shape[1]):
        for j in range(K):
            C[j, i]          = sum_block(1, 4,  j, i)   # 1..4
            C[K + j, i]      = sum_block(5, 17, j, i)   # 5..21
            C[2*K + j, i]    = sum_block(22, 44, j, i)  # 22..65

    # append extra quarters that are active in `flags`
    block_cursor = 3
    for q in range(2, p_d+1):
        flag = flags[q-2]  # Q2 is index 0
        if flag == 1:
            start_mult = 66*(q-1)
            for i in range(Z.shape[1]):
                for j in range(K):
                    C[(block_cursor*K)+j, i] = sum_block(start_mult, 66, j, i)
            block_cursor += 1

    Z_het = np.vstack((Z[0:K, :], C))
    if include_quarterly == 0:
        Z_het = Z_het[:K*3, :]

    # robust OLS
    ZZt = Z_het @ Z_het.T
    try:
        Ginv = _ridge_inverse(ZZt, ridge_lambda)
    except np.linalg.LinAlgError:
        if use_pinv_fallback:
            Ginv = np.linalg.pinv(ZZt, rcond=1e-12)
        else:
            raise

    Bhat = Y @ Z_het.T @ Ginv
    Uhat = Y - Bhat @ Z_het
    denom = max(1, (Y.shape[1] - Z_het.shape[0]//K))
    Sigma = (Uhat @ Uhat.T) / denom

    corr = np.array([Sigma[np.triu_indices(K, 1)[::-1]]]).T
    corr_mean = float(np.nanmean(np.abs(corr)))

    # split exactly like your original:
    # first 4K columns belong to the base quarter block set (K + 3K)
    Bhat_dh = Bhat[:, :4*K]

    # extras appear after 4K, one K-wide block per active quarter in order Q2..Q12
    extras = []
    offset = 4*K
    for qflag in flags:
        if qflag == 1:
            extras.append(Bhat[:, offset:offset+K])
            offset += K
        else:
            extras.append(None)

    return HvarFit(
        Bhat_dh=Bhat_dh,
        Bhat_d2=extras[0], Bhat_d3=extras[1], Bhat_d4=extras[2], Bhat_d5=extras[3],
        Bhat_d6=extras[4], Bhat_d7=extras[5], Bhat_d8=extras[6], Bhat_d9=extras[7],
        Bhat_d10=extras[8], Bhat_d11=extras[9], Bhat_d12=extras[10],
        Sigma=Sigma,
        Uhat=Uhat,
        Traw=Traw,
        K=K,
        Zhet=Z_het,
        corr_abs_mean=corr_mean,
        p_d=p_d
    )
