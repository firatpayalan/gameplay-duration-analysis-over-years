# Gameplay Duration Analysis Over Years

Do main-story game lengths change over release years? This repo answers that with a shared cleaning package, a Jupyter notebook, and a small Streamlit dashboard.

## Setup

Python 3.11 or newer is required. Create the virtual environment with a Python 3.11+ interpreter; your system `python3` may be older.

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

The dashboard includes a genre dropdown (default: most common genre in the cleaned cohort). Multi-label games match if they include the selected genre.

## Cleaning rules (v1)

- Metric: `main_story` hours
- Release year: first of NA → EU → JP
- Drop DLC/Expansion, Mod, ROM Hack
- Trend: yearly median; omit years with fewer than 30 games

Design: `docs/superpowers/specs/2026-07-25-gameplay-duration-analysis-design.md`
