import argparse
import numpy as np
from .config import ModelConfig
from .io import load_wide_csv, as_numpy
from .bootstrap import residual_bootstrap_irf
from .plotting import plot_irfs

def main():
    p = argparse.ArgumentParser(prog="hfhvar", description="HF-HVAR IRFs with bootstrap CIs (flags + p_d)")
    p.add_argument("--data", required=True)
    p.add_argument("--p_d", type=int, default=1)
    # flags
    for q in range(2, 13):
        p.add_argument(f"--Q{q}", action="store_true", help=f"Include Q{q} 66-day block")
    p.add_argument("--shock", type=int, default=0)
    p.add_argument("--shock-size", type=float, default=90.0)
    p.add_argument("--draws", type=int, default=20)
    p.add_argument("--quarters", type=int, default=40)
    p.add_argument("--no-plot", action="store_true")
    args = p.parse_args()

    cfg = ModelConfig(
        periods_per_quarter=66,
        p_d=args.p_d,
        Q2=int(args.Q2), Q3=int(args.Q3), Q4=int(args.Q4), Q5=int(args.Q5), Q6=int(args.Q6),
        Q7=int(args.Q7), Q8=int(args.Q8), Q9=int(args.Q9), Q10=int(args.Q10), Q11=int(args.Q11), Q12=int(args.Q12),
        shock_index=args.shock,
        shock_size=args.shock_size,
        bootstrap_draws=args.draws,
        period_display_quarters=args.quarters
    )

    df = load_wide_csv(args.data)
    Y, names = as_numpy(df)
    irf, lo, hi = residual_bootstrap_irf(Y, cfg)

    if not args.no_plot:
        plot_irfs(irf, lo, hi, cfg.periods_per_quarter, names)

    import pathlib
    out = pathlib.Path(args.data).with_suffix(".irf.npz")
    np.savez(out, irf=irf, lo=lo, hi=hi, names=names)
    print(f"Saved {out}")
