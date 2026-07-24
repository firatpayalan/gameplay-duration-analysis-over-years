from __future__ import annotations

import pandas as pd


def yearly_main_story_all(df: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        df.groupby("release_year", dropna=True)["main_story"]
        .agg(median_main_story="median", n="count")
        .reset_index()
        .rename(columns={"release_year": "year"})
    )
    grouped["year"] = grouped["year"].astype(int)
    grouped["n"] = grouped["n"].astype(int)
    return grouped.sort_values("year").reset_index(drop=True)


def yearly_main_story(df: pd.DataFrame, *, min_n: int = 30) -> pd.DataFrame:
    all_years = yearly_main_story_all(df)
    return all_years.loc[all_years["n"] >= min_n].reset_index(drop=True)
