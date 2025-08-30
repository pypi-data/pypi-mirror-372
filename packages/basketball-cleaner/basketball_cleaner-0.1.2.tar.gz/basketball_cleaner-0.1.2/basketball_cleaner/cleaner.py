import pandas as pd
from typing import Optional

def safe_ratio(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    """
    Compute ratio, return NaN if denominator is zero or null.
    """
    ratio = numerator / denominator
    return ratio.where(denominator != 0)

def fill_dunks_ratio(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fill dunks_ratio = dunksmade / dunks missed
    dunksmiss_dunksmade = sum of dunks made + missed
    So dunks missed = dunksmiss_dunksmade - dunksmade
    """
    dunksmade = df["dunksmade"]
    dunks_missed = df["dunksmiss_dunksmade"] - dunksmade
    df["dunks_ratio"] = safe_ratio(dunksmade, dunks_missed)
    return df

def fill_rim_ratio(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fill rim_ratio = rimmade / shots missed at/near rim
    rimmade_rimmiss = total rim attempts
    """
    made = df["rimmade"]
    missed = df["rimmade_rimmiss"] - made
    df["rim_ratio"] = safe_ratio(made, missed)
    return df

def fill_mid_ratio(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fill mid_ratio = midmade / mid missed
    midmade_midmiss = total mid attempts
    """
    made = df["midmade"]
    missed = df["midmade_midmiss"] - made
    df["mid_ratio"] = safe_ratio(made, missed)
    return df

def fill_ast_tov(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fill ast_tov = AST_per / TO_per
    """
    ast = df["AST_per"]
    tov = df["TO_per"]
    df["ast_tov"] = safe_ratio(ast, tov)
    return df

def clean_training_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fill all null ratios in one go using corrected formulas.
    """
    df = fill_dunks_ratio(df)
    df = fill_rim_ratio(df)
    df = fill_mid_ratio(df)
    df = fill_ast_tov(df)
    return df
