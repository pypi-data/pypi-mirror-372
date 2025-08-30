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
    Fill dunks_ratio = dunksmade / (dunksmade + dunksmiss_dunksmade)
    """
    dunksmade = df["dunksmade"]
    dunksmiss = df["dunksmiss_dunksmade"]
    df["dunks_ratio"] = safe_ratio(dunksmade, dunksmade + dunksmiss)
    return df

def fill_rim_ratio(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fill rim_ratio = rimmade / (rimmade + rimmade_rimmiss)
    """
    made = df["rimmade"]
    miss = df["rimmade_rimmiss"]
    df["rim_ratio"] = safe_ratio(made, made + miss)
    return df

def fill_mid_ratio(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fill mid_ratio = midmade / (midmade + midmade_midmiss)
    """
    made = df["midmade"]
    miss = df["midmade_midmiss"]
    df["mid_ratio"] = safe_ratio(made, made + miss)
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
    Fill all null ratios in one go.
    """
    df = fill_dunks_ratio(df)
    df = fill_rim_ratio(df)
    df = fill_mid_ratio(df)
    df = fill_ast_tov(df)
    return df
