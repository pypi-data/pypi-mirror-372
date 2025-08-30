import pandas as pd

def safe_ratio(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    """
    Compute ratio safely. Returns NaN where denominator is zero.
    """
    ratio = numerator / denominator
    return ratio.mask(denominator == 0)

def fill_dunks_ratio(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fill dunks_ratio = dunksmade / dunks missed
    dunksmiss_dunksmade = sum of dunks made + missed
    """
    df["dunksmade"] = df["dunksmade"].fillna(0)
    df["dunksmiss_dunksmade"] = df["dunksmiss_dunksmade"].fillna(0)
    missed = df["dunksmiss_dunksmade"] - df["dunksmade"]
    df["dunks_ratio"] = safe_ratio(df["dunksmade"], missed)
    return df

def fill_rim_ratio(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fill rim_ratio = rimmade / shots missed at/near rim
    rimmade_rimmiss = total rim attempts
    """
    df["rimmade"] = df["rimmade"].fillna(0)
    df["rimmade_rimmiss"] = df["rimmade_rimmiss"].fillna(0)
    missed = df["rimmade_rimmiss"] - df["rimmade"]
    df["rim_ratio"] = safe_ratio(df["rimmade"], missed)
    return df

def fill_mid_ratio(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fill mid_ratio = midmade / mid missed
    midmade_midmiss = total mid attempts
    """
    df["midmade"] = df["midmade"].fillna(0)
    df["midmade_midmiss"] = df["midmade_midmiss"].fillna(0)
    missed = df["midmade_midmiss"] - df["midmade"]
    df["mid_ratio"] = safe_ratio(df["midmade"], missed)
    return df

def clean_training_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fill all null ratios in one go (dunks_ratio, rim_ratio, mid_ratio).
    """
    df = fill_dunks_ratio(df)
    df = fill_rim_ratio(df)
    df = fill_mid_ratio(df)
    return df
