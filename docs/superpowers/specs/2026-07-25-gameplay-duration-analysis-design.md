# Gameplay Duration Analysis Over Years — Design

**Date:** 2026-07-25  
**Status:** Approved for planning  
**Dataset:** HowLongToBeat-style `games.csv` (~35,922 rows)

## Goal

Answer whether main-story game lengths have changed over the years, document findings in a reproducible notebook, then surface the headline trend and notable findings in a small Streamlit dashboard.

**Out of scope (v1):** genre/platform filters, interactive deep exploration, coop/versus metrics, completions CSVs.

## Approach

Notebook-first with a shared cleaning module:

1. Shared `src/` package loads and cleans the CSV once for both notebook and app.
2. Jupyter notebook performs EDA and writes the analysis narrative.
3. Thin Streamlit app reuses the same cleaning/aggregation and presents the main trend plus notable findings.

## Architecture

```
gameplay-duration-analysis-over-years/
  data/raw/games.csv              # project copy of the source CSV
  src/hltb/                       # load, clean, aggregate
    __init__.py
    load.py                       # read CSV from data/raw
    clean.py                      # filters, release year, exclusions
    aggregate.py                  # yearly median / counts
  notebooks/01_analysis.ipynb     # EDA + written findings
  app/streamlit_app.py            # trend chart + notable findings
  findings/notable.md             # short bullets for the dashboard
  requirements.txt
  README.md
```

**Data flow:** `games.csv` → `load` → `clean` → `aggregate` → notebook charts/narrative and Streamlit UI.

Cleaning logic lives only in `src/hltb/`. The notebook and app must not reimplement filters.

## Data rules

| Rule | Detail |
|------|--------|
| Primary metric | `main_story` (hours) |
| Include | Non-null `main_story` and a parseable release year |
| Release year | First available of `release_na` → `release_eu` → `release_jp` (year only) |
| Exclude by type | When `type` is `DLC/Expansion`, `Mod`, or `ROM Hack`; blank `type` stays in |
| Trend statistic | Yearly **median** `main_story`; also compute game **count** per year |
| Thin years | Years with `n < 30` omitted from the main trend line; noted in the notebook |
| Outliers | Kept for medians; extreme values may be flagged in the notebook only |

## Notebook

`notebooks/01_analysis.ipynb` covers:

1. Load via shared module; report row counts before/after cleaning and missingness.
2. Distribution of `main_story`.
3. Yearly median trend and per-year game counts.
4. Optional one-offs: decade medians, top/bottom years by median length.
5. Written findings and caveats (missing `main_story` coverage, release-date region bias, late-year sample effects).

## Streamlit dashboard

Minimal v1 UI:

1. Title and 1–2 sentence summary of the headline finding.
2. One main chart: median `main_story` over years (game count as annotation or secondary series).
3. “Notable findings” section: bullets from `findings/notable.md` (authored from notebook conclusions).
4. Footer: data source and cleaning rules in plain language.

No genre/platform filters in v1.

## Dependencies

Python packages expected in `requirements.txt` (exact versions pinned at implementation time; ask before changing once pinned):

- `pandas`
- `numpy`
- `matplotlib` and/or `plotly` (notebook + Streamlit charts)
- `jupyter` / `ipykernel`
- `streamlit`

## Error handling

- Missing `data/raw/games.csv`: fail fast with a clear path/setup message in load and README.
- Empty post-clean dataset or no years meeting `n >= 30`: surface an explicit message in notebook and app instead of an empty chart.
- Unparseable dates: treated as missing year and dropped by the include rule.

## Testing

Light, focused checks (no heavy test suite in v1):

- Unit tests for release-year precedence and type exclusions.
- Smoke: cleaned frame has required columns; yearly aggregate has `year`, `median_main_story`, `n`.

## Success criteria

- Shared cleaning produces a documented analysis cohort.
- Notebook answers whether main-story lengths changed over years, with caveats.
- Streamlit shows the same trend and notable findings without duplicating cleaning logic.
- README explains how to install, run the notebook, and launch the app.
