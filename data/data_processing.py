"""Data processing and merging utilities."""

import pandas as pd


def merge_rule5_with_savant(rule5_df: pd.DataFrame, savant_df: pd.DataFrame) -> pd.DataFrame:
    """Merge Rule 5 eligible players with ProspectSavant data."""
    aaa_rule5 = rule5_df[rule5_df["Level"] == "AAA"].copy()

    if aaa_rule5.empty or savant_df.empty:
        return pd.DataFrame()

    # Normalize names for matching
    aaa_rule5["name_norm"] = aaa_rule5["Player"].str.strip().str.lower()
    savant_df["name_norm"] = savant_df["Player"].str.strip().str.lower()

    merged = aaa_rule5.merge(savant_df, on="name_norm", how="inner", suffixes=("", "_savant"))
    merged = merged.drop(columns=["name_norm", "Age_savant", "Position_savant"], errors="ignore")

    return merged


def apply_filters(df: pd.DataFrame, search: str = None, teams: list = None,
                  positions: list = None, levels: list = None, age_range: tuple = None) -> pd.DataFrame:
    """Apply multiple filters to the dataframe."""
    filtered_df = df.copy()

    if search:
        filtered_df = filtered_df[filtered_df["Player"].str.contains(search, case=False, na=False)]

    if teams:
        filtered_df = filtered_df[filtered_df["Current Org"].isin(teams)]

    if positions:
        filtered_df = filtered_df[filtered_df["Position"].isin(positions)]

    if levels:
        filtered_df = filtered_df[filtered_df["Level"].isin(levels)]

    if age_range:
        filtered_df = filtered_df[filtered_df["Age"].between(age_range[0], age_range[1])]

    return filtered_df