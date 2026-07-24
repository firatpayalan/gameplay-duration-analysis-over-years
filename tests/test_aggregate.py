import pandas as pd

from hltb.aggregate import yearly_main_story, yearly_main_story_all


def _games_for_years() -> pd.DataFrame:
    rows = []
    # 2010: 30 games, median should be 5.0 (hours 1..30 → median 15.5? use identical values)
    for i in range(30):
        rows.append({"release_year": 2010, "main_story": 5.0})
    # 2011: only 5 games → filtered when min_n=30
    for i in range(5):
        rows.append({"release_year": 2011, "main_story": 100.0})
    # 2012: 30 games at 10.0
    for i in range(30):
        rows.append({"release_year": 2012, "main_story": 10.0})
    return pd.DataFrame(rows)


def test_yearly_main_story_all_includes_thin_years():
    out = yearly_main_story_all(_games_for_years())
    assert list(out["year"]) == [2010, 2011, 2012]
    assert list(out["n"]) == [30, 5, 30]
    assert out.loc[out["year"] == 2010, "median_main_story"].iloc[0] == 5.0
    assert out.loc[out["year"] == 2011, "median_main_story"].iloc[0] == 100.0


def test_yearly_main_story_filters_thin_years():
    out = yearly_main_story(_games_for_years(), min_n=30)
    assert list(out["year"]) == [2010, 2012]
    assert list(out["median_main_story"]) == [5.0, 10.0]


def test_yearly_columns():
    out = yearly_main_story(_games_for_years())
    assert list(out.columns) == ["year", "median_main_story", "n"]
