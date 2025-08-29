from dataclasses import dataclass
from typing import Optional

@dataclass
class ModelConfig:
    periods_per_quarter: int = 66

    # number of quarters of daily lags used in the state (1..12)
    p_d: int = 1

    # you must set Q2..Qp_d = 1 to include those quarters
    Q2: int = 0
    Q3: int = 0
    Q4: int = 0
    Q5: int = 0
    Q6: int = 0
    Q7: int = 0
    Q8: int = 0
    Q9: int = 0
    Q10: int = 0
    Q11: int = 0
    Q12: int = 0

    period_display_quarters: int = 40

    # shock
    shock_index: int = 0
    shock_size: float = 90.0

    # bootstrap + CIs
    bootstrap_draws: int = 20
    ci_low: float = 16.0
    ci_high: float = 84.0

    # numerics
    ridge_lambda: float = 1e-8
    use_pinv_fallback: bool = True

    seed: Optional[int] = 42
    show_progress: bool = True
