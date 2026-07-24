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
