from pathlib import Path

import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_CSV = REPO_ROOT / "data" / "raw" / "games.csv"


@pytest.fixture
def sample_raw_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "title": ["A", "B", "C", "D", "E"],
            "main_story": [10.0, 20.0, None, 5.0, 8.0],
            "type": ["", "DLC/Expansion", "", "Mod", ""],
            "release_na": ["2010-01-01", "2011-06-01", "2012-01-01", "", ""],
            "release_eu": ["", "", "", "2013-03-01", ""],
            "release_jp": ["", "", "", "", "2014-07-01"],
        }
    )
