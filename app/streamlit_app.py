from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from hltb import (
    clean_games,
    eligible_genres,
    filter_by_genre,
    load_games,
    repo_root,
    top_genre,
    yearly_main_story,
)

ROOT = repo_root()
FINDINGS = ROOT / "findings" / "notable.md"


@st.cache_data
def load_cleaned() -> pd.DataFrame:
    return clean_games(load_games())


def main() -> None:
    st.set_page_config(page_title="Gameplay Duration Over Years", layout="wide")
    st.title("Gameplay duration over years")

    try:
        cleaned = load_cleaned()
    except FileNotFoundError as exc:
        st.error(str(exc))
        return

    genres = eligible_genres(cleaned, min_games=30)
    if not genres:
        st.warning("No genres have at least 30 cleaned games — nothing to chart.")
        return

    default = top_genre(cleaned)
    if default not in genres:
        default = genres[0]
    selected = st.selectbox("Genre", genres, index=genres.index(default))
    subset = filter_by_genre(cleaned, selected)
    trend = yearly_main_story(subset, min_n=30)

    if trend.empty:
        st.warning(f"No years have at least 30 cleaned {selected} games — nothing to chart.")
        return

    first = trend.iloc[0]
    last = trend.iloc[-1]
    st.write(
        f"For **{selected}**, among **{len(subset):,}** cleaned games, the included "
        "annual medians run from "
        f"**{first['median_main_story']:.1f}h** in {int(first['year'])} to "
        f"**{last['median_main_story']:.1f}h** in {int(last['year'])}. "
        "Treat those endpoints cautiously: they can be sensitive to sample "
        "composition and thin years in this genre cohort. "
        "Years with fewer than 30 games are omitted."
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
    fig.update_layout(
        title=f"{selected}: median main_story hours by release year",
        hovermode="x unified",
    )
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
        f"Filtered to games tagged {selected}; multi-label games count if they include "
        "the selected genre. Trend uses yearly median; years with n < 30 are omitted."
    )


if __name__ == "__main__":
    main()
