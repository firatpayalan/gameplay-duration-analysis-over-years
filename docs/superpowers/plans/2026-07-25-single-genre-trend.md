# Single-Genre Trend + Streamlit Picker Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add shared genre helpers, a notebook section for the top genre’s median main_story trend, and a Streamlit genre dropdown (default = top genre).

**Architecture:** New `src/hltb/genres.py` owns genre token counting, top genre, filtering, and eligibility. Notebook and Streamlit call these after `clean_games` and before `yearly_main_story`. No cleaning rules duplicated outside `src/hltb/`.

**Tech Stack:** Existing — pandas, pytest, matplotlib (notebook), streamlit, plotly

## Global Constraints

- Primary metric: `main_story` hours only (v1)
- Multi-label: game matches if selected token appears in comma-separated `genres`
- Notebook: top genre only — no picker
- Streamlit: dropdown; default = `top_genre`
- Trend: yearly median; omit years with `n < 30`
- `findings/notable.md` stays overall narrative (not rewritten per genre)
- Ask before changing pinned dependency versions
- Cleaning logic lives only in `src/hltb/`

---

## File Structure

| Path | Responsibility |
|------|----------------|
| `src/hltb/genres.py` | `genre_counts`, `top_genre`, `filter_by_genre`, `eligible_genres` |
| `tests/test_genres.py` | Unit tests for genre helpers |
| `src/hltb/__init__.py` | Export new APIs |
| `notebooks/01_analysis.ipynb` | Top-genre trend section |
| `app/streamlit_app.py` | Genre picker + filtered chart |

---

### Task 1: Genre helpers + tests

**Files:**
- Create: `src/hltb/genres.py`
- Create: `tests/test_genres.py`
- Modify: `src/hltb/__init__.py`

**Interfaces:**
- Consumes: cleaned (or any) `DataFrame` with optional `genres` column
- Produces:
  - `genre_counts(df) -> pd.Series` (index=genre token, values=counts, descending)
  - `top_genre(df) -> str`
  - `filter_by_genre(df, genre: str) -> pd.DataFrame` (reset_index)
  - `eligible_genres(df, *, min_games: int = 30) -> list[str]`

- [ ] **Step 1: Write failing tests**

`tests/test_genres.py`:

```python
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
```

- [ ] **Step 2: Run tests — expect fail**

```bash
.venv/bin/pytest tests/test_genres.py -v
```

Expected: import failure for `hltb.genres`.

- [ ] **Step 3: Implement `src/hltb/genres.py`**

```python
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
        .explode()
        .str.strip()
    )
    return tokens[tokens != ""]


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
```

Update `src/hltb/__init__.py` to export the four functions (keep existing exports).

- [ ] **Step 4: Run tests — expect pass**

```bash
.venv/bin/pytest tests/ -q
```

Expected: all passed (including prior 11).

- [ ] **Step 5: Commit**

```bash
git add src/hltb/genres.py src/hltb/__init__.py tests/test_genres.py
git commit -m "$(cat <<'EOF'
Add genre count, filter, and eligibility helpers.

EOF
)"
```

---

### Task 2: Notebook top-genre section

**Files:**
- Modify: `notebooks/01_analysis.ipynb`

**Interfaces:**
- Consumes: `top_genre`, `filter_by_genre`, `yearly_main_story`
- Produces: notebook cells charting top-genre median trend

- [ ] **Step 1: Append cells after the overall findings**

Markdown:

```markdown
## Top-genre trend

Single-genre view (default = most common genre in the cleaned cohort) to reduce genre-mix confounding. Multi-label games still count if they include that genre.
```

Code:

```python
from hltb import filter_by_genre, top_genre

g = top_genre(cleaned)
genre_df = filter_by_genre(cleaned, g)
genre_trend = yearly_main_story(genre_df, min_n=30)
print(f"Top genre: {g}")
print(f"Games tagged {g}: {len(genre_df):,}")
print(f"Years with n≥30: {len(genre_trend)}")

if genre_trend.empty:
    print(f"No years with at least 30 {g} games after filtering — nothing to chart.")
else:
    fig, ax1 = plt.subplots(figsize=(10, 4))
    ax1.plot(genre_trend["year"], genre_trend["median_main_story"], marker="o")
    ax1.set_xlabel("release year")
    ax1.set_ylabel("median main_story (hours)")
    ax1.set_title(f"Median main_story over years — {g} (n ≥ 30)")
    ax2 = ax1.twinx()
    ax2.bar(genre_trend["year"], genre_trend["n"], alpha=0.2)
    ax2.set_ylabel("games (n)")
    plt.show()
```

- [ ] **Step 2: Execute notebook (or run the new cells via a short script) to confirm no errors**

```bash
.venv/bin/python - <<'PY'
from hltb import clean_games, filter_by_genre, load_games, top_genre, yearly_main_story
cleaned = clean_games(load_games())
g = top_genre(cleaned)
gt = yearly_main_story(filter_by_genre(cleaned, g), min_n=30)
print(g, len(gt), gt.iloc[0].to_dict(), gt.iloc[-1].to_dict())
PY
```

- [ ] **Step 3: Commit**

```bash
git add notebooks/01_analysis.ipynb
git commit -m "$(cat <<'EOF'
Add top-genre median trend section to the analysis notebook.

EOF
)"
```

---

### Task 3: Streamlit genre picker

**Files:**
- Modify: `app/streamlit_app.py`
- Modify: `README.md` (one line noting the genre filter)

**Interfaces:**
- Consumes: `eligible_genres`, `filter_by_genre`, `top_genre`, `yearly_main_story`
- Produces: dropdown-driven filtered chart; overall findings unchanged

- [ ] **Step 1: Replace cache + main chart path**

Change cached loader to return cleaned frame (not only overall trend):

```python
@st.cache_data
def load_cleaned() -> pd.DataFrame:
    return clean_games(load_games())
```

In `main()`:

1. `cleaned = load_cleaned()`
2. `genres = eligible_genres(cleaned, min_games=30)`
3. If empty: warn and return
4. `default = top_genre(cleaned)`; if default not in genres, use `genres[0]`
5. `selected = st.selectbox("Genre", genres, index=genres.index(default))`
6. `subset = filter_by_genre(cleaned, selected)`
7. `trend = yearly_main_story(subset, min_n=30)`
8. Summary + chart titles include `selected`
9. Caption notes genre filter + multi-label rule
10. Keep overall Notable findings from `findings/notable.md`

Empty `trend` after filter: show warning for that genre.

- [ ] **Step 2: Smoke-check**

```bash
.venv/bin/python - <<'PY'
from hltb import clean_games, eligible_genres, filter_by_genre, load_games, top_genre, yearly_main_story
c = clean_games(load_games())
g = top_genre(c)
assert g in eligible_genres(c, min_games=30)
t = yearly_main_story(filter_by_genre(c, g), min_n=30)
assert not t.empty
print('ok', g, len(t))
PY
.venv/bin/pytest -q
```

- [ ] **Step 3: README — add under Dashboard**

```markdown
The dashboard includes a genre dropdown (default: most common genre in the cleaned cohort). Multi-label games match if they include the selected genre.
```

- [ ] **Step 4: Commit**

```bash
git add app/streamlit_app.py README.md
git commit -m "$(cat <<'EOF'
Add Streamlit genre picker for single-genre duration trends.

EOF
)"
```

---

## Self-review (plan vs spec)

| Spec item | Task |
|-----------|------|
| `genre_counts` / `top_genre` / `filter_by_genre` / `eligible_genres` | Task 1 |
| Notebook top-genre section | Task 2 |
| Streamlit dropdown defaulting to top genre | Task 3 |
| Overall findings unchanged | Task 3 |
| Unit tests for multi-label | Task 1 |
| No dependency pin changes | Honored |
