import numpy as np
import pandas as pd

# ---------- odds helpers (your formulas, vectorized) ----------
def is_series(x):
    return isinstance(x, pd.Series)

def american_to_prob_int(num: int):
    if num < 100:
        return (-1 * num) / (100 - num)
    else:
        return 100 / (100 + num)

def american_to_prob_vector(series: pd.Series):
    return np.where(
        series < 100,
        (-1 * series) / (100 - series),
        100 / (100 + series)
    )

def american_to_prob(odds):
    if is_series(odds):
        return pd.Series(american_to_prob_vector(odds), index=odds.index, dtype=float)
    else:
        return american_to_prob_int(odds)

def american_to_hold_adj_prob(over_odds, under_odds):
    p_over  = american_to_prob(over_odds)
    p_under = american_to_prob(under_odds)
    combo = p_over + p_under
    if is_series(combo):
        return (
            (p_over / combo).where(combo != 0, np.nan),
            (p_under / combo).where(combo != 0, np.nan),
            combo - 1.0
        )
    else:
        return (
            (p_over / combo) if combo else np.nan,
            (p_under / combo) if combo else np.nan,
            combo - 1.0
        )