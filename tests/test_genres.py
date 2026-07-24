import pandas as pd
import pytest

from hltb.genres import eligible_genres, filter_by_genre, genre_counts, top_genre


@pytest.fixture
def genre_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "title": ["A", "B", "C", "D", "E"],
            "genres": [
                "Action, Role-Playing",
                "Action",
                "Adventure",
                "Action, Adventure",
                "",
            ],
        }
    )


def test_genre_counts_explodes_multi_label(genre_df: pd.DataFrame):
    counts = genre_counts(genre_df)
    assert counts["Action"] == 3
    assert counts["Adventure"] == 2
    assert counts["Role-Playing"] == 1
    assert "" not in counts.index


def test_top_genre(genre_df: pd.DataFrame):
    assert top_genre(genre_df) == "Action"


def test_filter_by_genre_includes_multi_label(genre_df: pd.DataFrame):
    out = filter_by_genre(genre_df, "Action")
    assert set(out["title"]) == {"A", "B", "D"}


def test_eligible_genres_min_games(genre_df: pd.DataFrame):
    assert eligible_genres(genre_df, min_games=3) == ["Action"]
    assert eligible_genres(genre_df, min_games=2) == ["Action", "Adventure"]
