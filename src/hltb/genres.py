from __future__ import annotations

import pandas as pd


def _genre_tokens(df: pd.DataFrame) -> pd.Series:
    if "genres" not in df.columns:
        return pd.Series(dtype=str)
    tokens = (
        df["genres"]
        .fillna("")
        .astype(str)
        .str.split(",")
        .apply(
            lambda parts: list(
                dict.fromkeys(p.strip() for p in parts if p.strip())
            )
        )
        .explode()
    )
    return tokens.dropna()


def genre_counts(df: pd.DataFrame) -> pd.Series:
    tokens = _genre_tokens(df)
    if tokens.empty:
        return pd.Series(dtype=int)
    return tokens.value_counts()


def top_genre(df: pd.DataFrame) -> str:
    counts = genre_counts(df)
    if counts.empty:
        raise ValueError("No genres available to choose a top genre")
    return str(counts.index[0])


def filter_by_genre(df: pd.DataFrame, genre: str) -> pd.DataFrame:
    if "genres" not in df.columns:
        return df.iloc[0:0].copy()
    mask = (
        df["genres"]
        .fillna("")
        .astype(str)
        .str.split(",")
        .apply(lambda parts: genre in {p.strip() for p in parts if p.strip()})
    )
    return df.loc[mask].copy().reset_index(drop=True)


def eligible_genres(df: pd.DataFrame, *, min_games: int = 30) -> list[str]:
    counts = genre_counts(df)
    return [str(g) for g, n in counts.items() if int(n) >= min_games]
