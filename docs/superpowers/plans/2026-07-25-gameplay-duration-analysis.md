# Gameplay Duration Analysis Over Years Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a shared cleaning package, analysis notebook, and minimal Streamlit dashboard that show whether HowLongToBeat `main_story` lengths changed over years.

**Architecture:** Copy `games.csv` into `data/raw/`. Put load/clean/aggregate logic in `src/hltb/` so the notebook and Streamlit app share one cohort definition. Notebook documents findings; `findings/notable.md` feeds the dashboard bullets.

**Tech Stack:** Python 3.11+, pandas, numpy, matplotlib, plotly, jupyter, ipykernel, streamlit, pytest

## Global Constraints

- Primary metric: `main_story` hours only (v1)
- Release year precedence: `release_na` → `release_eu` → `release_jp`
- Exclude types: `DLC/Expansion`, `Mod`, `ROM Hack`; blank `type` stays in
- Main trend uses yearly median; omit years with `n < 30`
- No genre/platform filters in v1
- Cleaning logic lives only in `src/hltb/` — notebook and app must not reimplement filters
- Ask the user before changing dependency versions after they are pinned in `requirements.txt`

---

## File Structure

| Path | Responsibility |
|------|----------------|
| `data/raw/games.csv` | Source dataset copy |
| `src/hltb/__init__.py` | Package exports |
| `src/hltb/load.py` | Read CSV; fail fast if missing |
| `src/hltb/clean.py` | Release year, type filter, analysis cohort |
| `src/hltb/aggregate.py` | Yearly median + counts; thin-year filter |
| `tests/test_load.py` | Missing-file and load smoke tests |
| `tests/test_clean.py` | Year precedence, type exclusion, cohort filters |
| `tests/test_aggregate.py` | Median/count and `min_n` behavior |
| `tests/conftest.py` | `sys.path` + sample fixtures |
| `notebooks/01_analysis.ipynb` | EDA + written findings |
| `findings/notable.md` | Dashboard bullets authored from notebook |
| `app/streamlit_app.py` | Headline, chart, findings, footer |
| `requirements.txt` | Pinned deps |
| `pyproject.toml` | Editable install of `hltb` |
| `README.md` | Install, notebook, Streamlit |

---

### Task 1: Project scaffold and data copy

**Files:**
- Create: `requirements.txt`
- Create: `pyproject.toml`
- Create: `src/hltb/__init__.py`
- Create: `tests/conftest.py`
- Create: `data/raw/games.csv` (copy from Downloads)
- Create: `README.md` (stub; full text in Task 6)

**Interfaces:**
- Consumes: source CSV at `/Users/firat/Downloads/archive/games.csv`
- Produces: installable package `hltb`; pytest can import `hltb`

- [ ] **Step 1: Create directories and copy the dataset**

```bash
cd /Users/firat/gameplay-duration-analysis-over-years
mkdir -p data/raw src/hltb tests notebooks findings app
cp /Users/firat/Downloads/archive/games.csv data/raw/games.csv
wc -l data/raw/games.csv
```

Expected: line count `35923` (header + 35922 rows).

- [ ] **Step 2: Write `requirements.txt`**

```text
pandas==2.2.3
numpy==2.1.3
matplotlib==3.9.3
plotly==5.24.1
jupyter==1.1.1
ipykernel==6.29.5
streamlit==1.41.1
pytest==8.3.4
```

- [ ] **Step 3: Write `pyproject.toml`**

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "hltb"
version = "0.1.0"
description = "HowLongToBeat gameplay duration analysis helpers"
requires-python = ">=3.11"
dependencies = [
  "pandas==2.2.3",
  "numpy==2.1.3",
]

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

- [ ] **Step 4: Write package stub and conftest**

`src/hltb/__init__.py`:

```python
"""HowLongToBeat analysis helpers."""

__all__: list[str] = []
```

`tests/conftest.py`:

```python
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
```

- [ ] **Step 5: Write README stub**

```markdown
# Gameplay Duration Analysis Over Years

Analysis of HowLongToBeat `main_story` lengths over release years.

See `docs/superpowers/specs/2026-07-25-gameplay-duration-analysis-design.md`.

Setup instructions will be completed after the app lands.
```

- [ ] **Step 6: Install package and verify pytest discovers nothing yet**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements.txt
python -c "import hltb; print(hltb.__file__)"
```

Expected: prints a path under `src/hltb`.

- [ ] **Step 7: Commit**

```bash
git add requirements.txt pyproject.toml src/hltb/__init__.py tests/conftest.py README.md data/raw/games.csv
git commit -m "$(cat <<'EOF'
Scaffold project, package layout, and raw games data.

EOF
)"
```

Note: if `data/raw/games.csv` is large and you prefer not to commit binary/data, add `data/raw/` to `.gitignore` and document the copy command in README instead — **prefer committing** for reproducibility unless the user objects. Default for this plan: **commit the CSV**.

---

### Task 2: Load CSV with fail-fast missing path

**Files:**
- Create: `src/hltb/load.py`
- Create: `tests/test_load.py`
- Modify: `src/hltb/__init__.py`

**Interfaces:**
- Consumes: CSV path (default `data/raw/games.csv` relative to repo root)
- Produces:
  - `repo_root() -> Path`
  - `default_games_path() -> Path`
  - `load_games(path: Path | None = None) -> pd.DataFrame`
  - Raises `FileNotFoundError` with message containing the missing path when file absent

- [ ] **Step 1: Write the failing tests**

`tests/test_load.py`:

```python
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
    with pytest.raises(FileNotFoundError, match=str(missing)):
        load_games(missing)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
source .venv/bin/activate
pytest tests/test_load.py -v
```

Expected: FAIL with `ModuleNotFoundError` or `cannot import name 'load_games'`.

- [ ] **Step 3: Implement `src/hltb/load.py`**

```python
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
```

Update `src/hltb/__init__.py`:

```python
"""HowLongToBeat analysis helpers."""

from hltb.load import default_games_path, load_games, repo_root

__all__ = [
    "default_games_path",
    "load_games",
    "repo_root",
]
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_load.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add src/hltb/load.py src/hltb/__init__.py tests/test_load.py
git commit -m "$(cat <<'EOF'
Add CSV loader with clear missing-file errors.

EOF
)"
```

---

### Task 3: Clean cohort (release year, type filter, main_story)

**Files:**
- Create: `src/hltb/clean.py`
- Create: `tests/test_clean.py`
- Modify: `src/hltb/__init__.py`

**Interfaces:**
- Consumes: raw `pd.DataFrame` from `load_games`
- Produces:
  - `EXCLUDED_TYPES: frozenset[str] = frozenset({"DLC/Expansion", "Mod", "ROM Hack"})`
  - `derive_release_year(df: pd.DataFrame) -> pd.Series` — Int64 nullable years
  - `clean_games(df: pd.DataFrame) -> pd.DataFrame` — rows with non-null `main_story`, non-null `release_year`, type not in excluded set; adds `release_year` column; resets index

- [ ] **Step 1: Write the failing tests**

`tests/test_clean.py`:

```python
import pandas as pd

from hltb.clean import EXCLUDED_TYPES, clean_games, derive_release_year


def test_derive_release_year_prefers_na_then_eu_then_jp(sample_raw_df: pd.DataFrame):
    years = derive_release_year(sample_raw_df)
    assert list(years) == [2010, 2011, 2012, 2013, 2014]


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


def test_clean_games_drops_missing_main_story_and_excluded_types(sample_raw_df: pd.DataFrame):
    cleaned = clean_games(sample_raw_df)
    # row0: keep; row1 DLC drop; row2 missing main_story drop; row3 Mod drop; row4 keep
    assert set(cleaned["title"]) == {"A", "E"}
    assert list(cleaned["release_year"]) == [2010, 2014]


def test_excluded_types_constant():
    assert EXCLUDED_TYPES == frozenset({"DLC/Expansion", "Mod", "ROM Hack"})
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_clean.py -v
```

Expected: FAIL importing `hltb.clean`.

- [ ] **Step 3: Implement `src/hltb/clean.py`**

```python
from __future__ import annotations

import pandas as pd

EXCLUDED_TYPES: frozenset[str] = frozenset({"DLC/Expansion", "Mod", "ROM Hack"})

_DATE_COLS = ("release_na", "release_eu", "release_jp")


def _year_from_series(series: pd.Series) -> pd.Series:
    parsed = pd.to_datetime(series, errors="coerce", format="mixed")
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
```

Update `src/hltb/__init__.py` to also export `EXCLUDED_TYPES`, `clean_games`, `derive_release_year`.

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_clean.py tests/test_load.py -v
```

Expected: all passed.

- [ ] **Step 5: Commit**

```bash
git add src/hltb/clean.py src/hltb/__init__.py tests/test_clean.py
git commit -m "$(cat <<'EOF'
Add cleaning rules for main_story cohort and release year.

EOF
)"
```

---

### Task 4: Yearly median aggregation with thin-year filter

**Files:**
- Create: `src/hltb/aggregate.py`
- Create: `tests/test_aggregate.py`
- Modify: `src/hltb/__init__.py`

**Interfaces:**
- Consumes: cleaned `pd.DataFrame` with `release_year`, `main_story`
- Produces:
  - `yearly_main_story(df: pd.DataFrame, *, min_n: int = 30) -> pd.DataFrame`
  - Columns: `year` (int), `median_main_story` (float), `n` (int)
  - Sorted by `year` ascending
  - Rows with `n < min_n` removed
  - Also: `yearly_main_story_all(df) -> pd.DataFrame` same columns but **no** `min_n` filter (for notebook thin-year notes)

- [ ] **Step 1: Write the failing tests**

`tests/test_aggregate.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_aggregate.py -v
```

Expected: FAIL importing `hltb.aggregate`.

- [ ] **Step 3: Implement `src/hltb/aggregate.py`**

```python
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
```

Export both functions from `src/hltb/__init__.py`.

- [ ] **Step 4: Run full unit suite**

```bash
pytest tests/ -v
```

Expected: all passed.

- [ ] **Step 5: Commit**

```bash
git add src/hltb/aggregate.py src/hltb/__init__.py tests/test_aggregate.py
git commit -m "$(cat <<'EOF'
Add yearly median main_story aggregation with min_n filter.

EOF
)"
```

---

### Task 5: Analysis notebook + notable findings file

**Files:**
- Create: `notebooks/01_analysis.ipynb`
- Create: `findings/notable.md`

**Interfaces:**
- Consumes: `load_games`, `clean_games`, `yearly_main_story`, `yearly_main_story_all`
- Produces: written conclusions; `findings/notable.md` with 3–5 markdown bullets for the dashboard

- [ ] **Step 1: Create the notebook with these cells (in order)**

Cell 0 (markdown):

```markdown
# Main-story length over years

HowLongToBeat `main_story` hours by release year. Cleaning rules live in `hltb` — do not re-filter here.
```

Cell 1 (code):

```python
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import pandas as pd

# editable install preferred; fallback for ad-hoc kernels:
repo = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
sys.path.insert(0, str(repo / "src"))

from hltb import clean_games, load_games, yearly_main_story, yearly_main_story_all

raw = load_games()
cleaned = clean_games(raw)
print(f"raw rows: {len(raw):,}")
print(f"cleaned rows: {len(cleaned):,}")
print(f"main_story coverage in raw: {raw['main_story'].notna().mean():.1%}")
print(cleaned[["main_story", "release_year"]].describe())
```

Cell 2 (code) — distribution:

```python
ax = cleaned["main_story"].clip(upper=cleaned["main_story"].quantile(0.99)).hist(bins=40)
ax.set_xlabel("main_story hours (clipped at p99 for display)")
ax.set_ylabel("games")
ax.set_title("Distribution of main_story")
plt.show()
```

Cell 3 (code) — trend:

```python
trend = yearly_main_story(cleaned, min_n=30)
all_years = yearly_main_story_all(cleaned)
thin = all_years.loc[all_years["n"] < 30]

fig, ax1 = plt.subplots(figsize=(10, 4))
ax1.plot(trend["year"], trend["median_main_story"], marker="o")
ax1.set_xlabel("release year")
ax1.set_ylabel("median main_story (hours)")
ax1.set_title("Median main_story over years (n ≥ 30)")

ax2 = ax1.twinx()
ax2.bar(trend["year"], trend["n"], alpha=0.2)
ax2.set_ylabel("games (n)")
plt.show()

print("Thin years excluded from main trend:")
display(thin)
```

Cell 4 (code) — optional one-offs:

```python
decade = cleaned.copy()
decade["decade"] = (decade["release_year"] // 10) * 10
decade_med = decade.groupby("decade")["main_story"].median()
print("Decade medians:")
print(decade_med)

print("Longest median years:")
display(trend.nlargest(5, "median_main_story"))
print("Shortest median years:")
display(trend.nsmallest(5, "median_main_story"))
```

Cell 5 (markdown) — findings template (fill with real numbers after running):

```markdown
## Findings

1. **Headline:** After cleaning, median `main_story` from YYYY–YYYY [rose / fell / stayed roughly flat], from about Xh to Yh.
2. **Sample:** Cleaning keeps N games; raw `main_story` coverage is ~P%.
3. **Caveats:** Missing durations are common; release year prefers NA→EU→JP; years with n<30 are excluded from the main trend; late years may be incomplete in this 2020-dated dump.

Update `findings/notable.md` with the same bullets (shorter).
```

- [ ] **Step 2: Run the notebook end-to-end**

```bash
source .venv/bin/activate
cd /Users/firat/gameplay-duration-analysis-over-years
python -c "import nbformat; print('ok')" 2>/dev/null || true
jupyter nbconvert --to notebook --execute notebooks/01_analysis.ipynb --output 01_analysis.executed.ipynb
```

Expected: executes without error. Then replace Cell 5 markdown with actual computed headline numbers from the output, and delete `01_analysis.executed.ipynb` (do not commit the executed copy unless useful).

If `nbconvert` is awkward, run the cells manually in Jupyter and paste real figures into Cell 5.

- [ ] **Step 3: Write `findings/notable.md` from the notebook conclusions**

Example shape (replace with real values from Step 2):

```markdown
- Median main-story length [rose/fell/held] from about **Xh** in early covered years to about **Yh** in later years (years with fewer than 30 games excluded).
- The cleaned cohort has **N** games with both `main_story` and a parseable release year.
- Roughly **P%** of raw rows lack `main_story`, so trends reflect games with recorded times only.
- Release year uses NA, then EU, then JP dates; regional gaps can shift a game’s year.
- This dataset dump ends around **2020**, so recent years may be incomplete.
```

- [ ] **Step 4: Commit**

```bash
git add notebooks/01_analysis.ipynb findings/notable.md
git commit -m "$(cat <<'EOF'
Add analysis notebook and notable findings for the dashboard.

EOF
)"
```

---

### Task 6: Streamlit app + README

**Files:**
- Create: `app/streamlit_app.py`
- Modify: `README.md`

**Interfaces:**
- Consumes: `load_games`, `clean_games`, `yearly_main_story`; `findings/notable.md`
- Produces: runnable dashboard (`streamlit run app/streamlit_app.py`)

- [ ] **Step 1: Implement `app/streamlit_app.py`**

```python
from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from hltb import clean_games, load_games, repo_root, yearly_main_story

ROOT = repo_root()
FINDINGS = ROOT / "findings" / "notable.md"


@st.cache_data
def load_trend() -> tuple[pd.DataFrame, int]:
    raw = load_games()
    cleaned = clean_games(raw)
    trend = yearly_main_story(cleaned, min_n=30)
    return trend, len(cleaned)


def main() -> None:
    st.set_page_config(page_title="Gameplay Duration Over Years", layout="wide")
    st.title("Gameplay duration over years")

    try:
        trend, n_cleaned = load_trend()
    except FileNotFoundError as exc:
        st.error(str(exc))
        return

    if trend.empty:
        st.warning("No years with at least 30 games after cleaning — nothing to chart.")
        return

    first = trend.iloc[0]
    last = trend.iloc[-1]
    st.write(
        f"Among **{n_cleaned:,}** cleaned games, median main-story length moved from "
        f"**{first['median_main_story']:.1f}h** in {int(first['year'])} to "
        f"**{last['median_main_story']:.1f}h** in {int(last['year'])} "
        f"(years with fewer than 30 games omitted)."
    )

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(
            x=trend["year"],
            y=trend["median_main_story"],
            mode="lines+markers",
            name="Median main_story (h)",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Bar(
            x=trend["year"],
            y=trend["n"],
            name="Games (n)",
            opacity=0.3,
        ),
        secondary_y=True,
    )
    fig.update_layout(title="Median main_story hours by release year", hovermode="x unified")
    fig.update_yaxes(title_text="Median hours", secondary_y=False)
    fig.update_yaxes(title_text="Game count", secondary_y=True)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Notable findings")
    if FINDINGS.is_file():
        st.markdown(FINDINGS.read_text(encoding="utf-8"))
    else:
        st.info("Add findings/notable.md after running the analysis notebook.")

    st.divider()
    st.caption(
        "Source: HowLongToBeat-style games.csv. "
        "Cohort: non-null main_story, parseable release year (NA→EU→JP), "
        "excluding DLC/Expansion, Mod, and ROM Hack. "
        "Trend uses yearly median; years with n < 30 are omitted."
    )


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Smoke-run the app**

```bash
source .venv/bin/activate
cd /Users/firat/gameplay-duration-analysis-over-years
streamlit run app/streamlit_app.py --server.headless true
```

Expected: starts without traceback; open the local URL and confirm title, chart, findings bullets, and footer. Stop with Ctrl+C.

- [ ] **Step 3: Replace `README.md` with full instructions**

```markdown
# Gameplay Duration Analysis Over Years

Do main-story game lengths change over release years? This repo answers that with a shared cleaning package, a Jupyter notebook, and a small Streamlit dashboard.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements.txt
```

Ensure `data/raw/games.csv` exists (copied from the HowLongToBeat archive).

## Tests

```bash
pytest -q
```

## Notebook

```bash
jupyter notebook notebooks/01_analysis.ipynb
```

After updating conclusions, refresh `findings/notable.md`.

## Dashboard

```bash
streamlit run app/streamlit_app.py
```

## Cleaning rules (v1)

- Metric: `main_story` hours
- Release year: first of NA → EU → JP
- Drop DLC/Expansion, Mod, ROM Hack
- Trend: yearly median; omit years with fewer than 30 games

Design: `docs/superpowers/specs/2026-07-25-gameplay-duration-analysis-design.md`
```

- [ ] **Step 4: Commit**

```bash
git add app/streamlit_app.py README.md
git commit -m "$(cat <<'EOF'
Add Streamlit dashboard and project README.

EOF
)"
```

---

## Self-review (plan vs spec)

| Spec requirement | Task |
|------------------|------|
| Shared `src/hltb` load/clean/aggregate | Tasks 2–4 |
| `data/raw/games.csv` | Task 1 |
| Notebook EDA + findings + caveats | Task 5 |
| Streamlit headline + chart + notable + footer | Task 6 |
| `findings/notable.md` | Task 5 |
| Unit tests: year precedence, type exclusion, aggregate columns | Tasks 3–4 |
| Fail fast missing CSV | Task 2 + Task 6 |
| Empty trend message | Task 6 |
| README install / notebook / app | Task 6 |
| No genre/platform filters | Honored (not built) |
| Ask before changing pinned deps | Global Constraints |

No TBD/placeholder steps remain. Interface names are consistent: `load_games`, `clean_games`, `yearly_main_story`, `yearly_main_story_all`, `repo_root`.
