import pandas as pd

from hltb.clean import EXCLUDED_TYPES, clean_games, derive_release_year


def test_derive_release_year_prefers_na_then_eu_then_jp(sample_raw_df: pd.DataFrame):
    years = derive_release_year(sample_raw_df)
    assert list(years.iloc[:6]) == [2010, 2011, 2012, 2013, 2014, 2015]
    assert pd.isna(years.iloc[6])


def test_derive_release_year_unparseable_becomes_na():
    df = pd.DataFrame(
        {
            "release_na": ["not-a-date"],
            "release_eu": [""],
            "release_jp": [None],
        }
    )
    years = derive_release_year(df)
    assert pd.isna(years.iloc[0])


def test_derive_release_year_does_not_treat_numeric_year_as_epoch_offset():
    df = pd.DataFrame(
        {
            "release_na": [2010],
            "release_eu": [None],
            "release_jp": [None],
        }
    )
    years = derive_release_year(df)
    assert years.iloc[0] == 2010


def test_clean_games_drops_missing_main_story_and_excluded_types(sample_raw_df: pd.DataFrame):
    cleaned = clean_games(sample_raw_df)
    # A/E keep; B/D/F isolate each excluded type; C lacks duration; G lacks year.
    assert set(cleaned["title"]) == {"A", "E"}
    assert list(cleaned["release_year"]) == [2010, 2014]


def test_excluded_types_constant():
    assert EXCLUDED_TYPES == frozenset({"DLC/Expansion", "Mod", "ROM Hack"})
