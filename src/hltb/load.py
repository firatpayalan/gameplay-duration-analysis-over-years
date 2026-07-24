from __future__ import annotations

from pathlib import Path

import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parents[2]


def repo_root() -> Path:
    return _REPO_ROOT


def default_games_path() -> Path:
    return repo_root() / "data" / "raw" / "games.csv"


def load_games(path: Path | None = None) -> pd.DataFrame:
    csv_path = Path(path) if path is not None else default_games_path()
    if not csv_path.is_file():
        raise FileNotFoundError(
            f"Games CSV not found at {csv_path}. "
            "Copy games.csv into data/raw/ (see README)."
        )
    return pd.read_csv(csv_path, low_memory=False)
