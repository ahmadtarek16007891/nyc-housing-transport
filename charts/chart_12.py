"""Chart 12: borough and housing-category serious-crash treemap.

The dashboard chart loader expects TITLE, QUESTION and build_figure(df, filters).
The course team interface also asks for make_chart_12(df), so both interfaces
are provided here.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

TITLE = "Serious-Crash Burden by Borough and Housing Activity"
QUESTION = (
    "How does the serious-crash burden and fatal-crash share vary across boroughs "
    "and the dominant affordable-housing activity in each ZIP-year?"
)

REQUIRED_COLUMNS = {
    "borough",
    "housing_category",
    "crash_count",
    "fatal_crashes",
    "fatalities",
    "total_units",
    "severe_injuries",
    "non_severe_injuries",
}


def _empty_figure(message: str = "No data for these filters") -> go.Figure:
    figure = go.Figure()
    figure.add_annotation(
        text=message,
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font={"size": 16, "color": "#64748b"},
    )
    figure.update_layout(
        template="plotly_white",
        xaxis={"visible": False},
        yaxis={"visible": False},
        margin={"l": 20, "r": 20, "t": 35, "b": 20},
    )
    return figure


def make_chart_12(df: pd.DataFrame) -> go.Figure:
    """Build a treemap sized by serious-crash count and colored by fatal share.

    Each input row is one ZIP-year. The grouping pools counts before computing
    the fatal-crash share, so borough/category colors use a ratio of sums rather
    than an unweighted average of ZIP-year percentages.
    """
    if df is None or df.empty:
        return _empty_figure()

    missing = sorted(REQUIRED_COLUMNS.difference(df.columns))
    if missing:
        return _empty_figure("Missing required columns: " + ", ".join(missing))

    work = df.copy()
    numeric_columns = [
        "crash_count",
        "fatal_crashes",
        "fatalities",
        "total_units",
        "severe_injuries",
        "non_severe_injuries",
    ]
    for column in numeric_columns:
        work[column] = pd.to_numeric(work[column], errors="coerce")

    work = work.dropna(subset=["borough", "housing_category", "crash_count"])
    # Zero-crash ZIP-years have no area in a crash-burden treemap, so omit them.
    work = work[work["crash_count"] > 0]
    if work.empty:
        return _empty_figure("No serious crashes are recorded for these filters")

    grouped = (
        work.groupby(["borough", "housing_category"], observed=True, as_index=False)
        .agg(
            crash_count=("crash_count", "sum"),
            fatal_crashes=("fatal_crashes", "sum"),
            fatalities=("fatalities", "sum"),
            total_units=("total_units", "sum"),
            severe_injuries=("severe_injuries", "sum"),
            non_severe_injuries=("non_severe_injuries", "sum"),
            zip_year_records=("crash_count", "size"),
        )
    )

    grouped["fatal_crash_share_pct"] = (
        grouped["fatal_crashes"] / grouped["crash_count"] * 100
    )
    grouped["injuries_per_crash"] = (
        (grouped["severe_injuries"] + grouped["non_severe_injuries"])
        / grouped["crash_count"]
    )

    figure = px.treemap(
        grouped,
        path=["borough", "housing_category"],
        values="crash_count",
        color="fatal_crash_share_pct",
        color_continuous_scale="YlOrRd",
        range_color=(0, max(10, float(grouped["fatal_crash_share_pct"].max()))),
        custom_data=[
            "fatal_crash_share_pct",
            "fatal_crashes",
            "fatalities",
            "total_units",
            "severe_injuries",
            "non_severe_injuries",
            "zip_year_records",
            "injuries_per_crash",
        ],
        labels={
            "crash_count": "Serious crashes",
            "fatal_crash_share_pct": "Fatal-crash share (%)",
            "housing_category": "Dominant housing activity",
        },
        title=TITLE,
    )
    figure.update_traces(
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Serious crashes: %{value:,.0f}<br>"
            "Fatal-crash share: %{customdata[0]:.1f}%<br>"
            "Fatal crashes: %{customdata[1]:,.0f}<br>"
            "Fatalities: %{customdata[2]:,.0f}<br>"
            "Affordable units completed: %{customdata[3]:,.0f}<br>"
            "Severe injuries: %{customdata[4]:,.0f}<br>"
            "Non-severe injuries: %{customdata[5]:,.0f}<br>"
            "ZIP-year records: %{customdata[6]:,.0f}<br>"
            "Injuries per serious crash: %{customdata[7]:.2f}"
            "<extra></extra>"
        ),
        tiling={"pad": 3},
        textinfo="label+value",
    )
    figure.update_layout(
        template="plotly_white",
        coloraxis_colorbar={"title": {"text": "Fatal-crash share (%)"}},
        margin={"l": 10, "r": 10, "t": 65, "b": 10},
        height=620,
    )
    return figure


def build_figure(df: pd.DataFrame, filters: dict | None = None) -> go.Figure:
    """Adapter used by the existing dashboard chart_loader.py."""
    return make_chart_12(df)
