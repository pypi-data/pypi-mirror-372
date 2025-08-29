import numpy as np

def build_daily_B_like_original(
    Bhat_dh: np.ndarray,
    extras: list,   # [Bhat_d2, Bhat_d3, ... Bhat_d12] entries may be None
    K: int,
    p_d: int
) -> np.ndarray:
    """
    Recreate your exact B construction:
      - base quarter: weekly(4)*K, monthly(17)*K, rest(44)*K
      - extras up to p_d: each active extra is repeated 66 times
      - final B_full = [ Bhat_dh[:,:K] | expanded blocks ... ]
    """
    # base slices from Bhat_dh (first 4K)
    Bhat_base = Bhat_dh
    week   = Bhat_base[:, K:2*K]
    month  = Bhat_base[:, 2*K:3*K]
    rest   = Bhat_base[:, 3*K:4*K]

    Bhet_0 = np.hstack([week]*4)          # 4 days
    Bhet_1 = np.hstack([month]*(21-4))    # 17 days (5..21)
    Bhet_2 = np.hstack([rest]*(65-21))    # 44 days (22..65)

    B = np.hstack([Bhet_0, Bhet_1, Bhet_2])

    # extras for q=2..p_d
    extra_blocks = extras[:max(0, p_d-1)]
    for blk in extra_blocks:
        if blk is not None:
            B = np.hstack([B, np.hstack([blk]*66)])

    # prepend the first K (previous day) block
    B_full = np.hstack([Bhat_base[:, :K], B])
    return B_full
