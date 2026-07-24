# Single-Genre Main-Story Trend + Streamlit Picker — Design

**Date:** 2026-07-25  
**Status:** Approved for planning  
**Extends:** `2026-07-25-gameplay-duration-analysis-design.md`

## Goal

Reduce genre-mix confounding when reading main-story length over years by analyzing one genre at a time. Notebook covers the default (top) genre; Streamlit adds a genre picker.

## Decisions

| Choice | Decision |
|--------|----------|
| Default genre | Most common genre token in the cleaned cohort (`top_genre`) — currently Action |
| Multi-label genres | A game matches if the selected token appears in its comma-separated `genres` list |
| Notebook | Top genre only — no interactive picker |
| Streamlit | Dropdown of eligible genres; default = `top_genre` |
| Trend stats | Unchanged: yearly median `main_story`, omit years with `n < 30` |
| Overall findings | `findings/notable.md` stays the overall narrative; UI notes when a genre filter is active |

## Shared API (`src/hltb/`)

Add to the package (exact names locked for planning):

- `genre_counts(df: pd.DataFrame) -> pd.Series` — count of games per genre token (explode comma-separated `genres`)
- `top_genre(df: pd.DataFrame) -> str` — mode of `genre_counts`
- `filter_by_genre(df: pd.DataFrame, genre: str) -> pd.DataFrame` — rows whose genre list contains `genre` (case-sensitive match to dataset tokens)
- `eligible_genres(df: pd.DataFrame, *, min_games: int = 30) -> list[str]` — genres with at least `min_games` cleaned rows, sorted by count descending

Reuse existing `clean_games` and `yearly_main_story`. Genre filtering happens **after** clean, **before** aggregate.

## Notebook

New section after the overall trend:

1. Compute `g = top_genre(cleaned)`
2. `genre_df = filter_by_genre(cleaned, g)`
3. Plot `yearly_main_story(genre_df)` with title naming `g`
4. Short markdown: single-genre view reduces mix effects; games tagged with multiple genres still count if they include `g`

## Streamlit

1. Load/clean once (cached)
2. Build dropdown from `eligible_genres(cleaned)`; default index = `top_genre(cleaned)`
3. On selection: filter → yearly median chart + summary sentence for that genre
4. Caption: filtered to selected genre; multi-label inclusion rule; `n ≥ 30` years only
5. Keep existing overall “Notable findings” from `findings/notable.md` (not rewritten per genre)

## Out of scope

- Multi-genre overlay / comparison charts
- Platform filters
- Changing pinned dependency versions without asking

## Testing

- Unit tests: `genre_counts` / `top_genre` / `filter_by_genre` on a small fixture with multi-label rows
- `eligible_genres` respects `min_games`
- Existing load/clean/aggregate tests still pass

## Success criteria

- Notebook shows top-genre median trend
- Streamlit genre picker changes the chart and summary
- Default selection is the top genre
- Cleaning rules remain solely in `src/hltb/`
