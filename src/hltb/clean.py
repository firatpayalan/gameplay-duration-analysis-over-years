from __future__ import annotations

import pandas as pd

EXCLUDED_TYPES: frozenset[str] = frozenset({"DLC/Expansion", "Mod", "ROM Hack"})

_DATE_COLS = ("release_na", "release_eu", "release_jp")


def _year_from_series(series: pd.Series) -> pd.Series:
    parsed = pd.to_datetime(series.astype("string"), errors="coerce", format="mixed")
    years = parsed.dt.year
    return years.astype("Int64")


def derive_release_year(df: pd.DataFrame) -> pd.Series:
    years = pd.Series(pd.NA, index=df.index, dtype="Int64")
    for col in _DATE_COLS:
        if col not in df.columns:
            continue
        candidate = _year_from_series(df[col])
        years = years.fillna(candidate)
    return years


def clean_games(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["release_year"] = derive_release_year(out)

    type_col = out["type"] if "type" in out.columns else pd.Series("", index=out.index)
    type_normalized = type_col.fillna("").astype(str).str.strip()
    excluded = type_normalized.isin(EXCLUDED_TYPES)

    main_story = pd.to_numeric(out["main_story"], errors="coerce")
    keep = main_story.notna() & out["release_year"].notna() & ~excluded

    out = out.loc[keep].copy()
    out["main_story"] = pd.to_numeric(out["main_story"], errors="coerce")
    return out.reset_index(drop=True)
