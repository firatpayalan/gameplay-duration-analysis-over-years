import re
from pathlib import Path

import pandas as pd
import pytest

from hltb.load import default_games_path, load_games


def test_default_games_path_points_at_raw_csv():
    path = default_games_path()
    assert path.name == "games.csv"
    assert path.parent.name == "raw"


def test_load_games_returns_dataframe_with_expected_columns():
    df = load_games()
    assert isinstance(df, pd.DataFrame)
    for col in ("id", "title", "main_story", "type", "release_na", "release_eu", "release_jp"):
        assert col in df.columns
    assert len(df) > 0


def test_load_games_missing_file_raises_clear_error(tmp_path: Path):
    missing = tmp_path / "nope.csv"
    expected = rf"{re.escape(str(missing))}.*Copy games\.csv into data/raw/"
    with pytest.raises(FileNotFoundError, match=expected):
        load_games(missing)
