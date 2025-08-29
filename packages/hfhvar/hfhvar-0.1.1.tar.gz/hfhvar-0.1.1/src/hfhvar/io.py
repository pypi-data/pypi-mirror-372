import pandas as pd

def load_wide_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, index_col=0, parse_dates=True)
    return df

def as_numpy(df: pd.DataFrame):
    return df.to_numpy(), list(df.columns)
