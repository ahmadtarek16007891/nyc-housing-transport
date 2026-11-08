"""Chart 05 (Member 3): serious crashes by housing-activity tier, box plot."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import config

TITLE = "Serious crashes in ZIPs with no, some, or a lot of new affordable housing"
QUESTION = ("Do ZIP codes that received the most new affordable housing face more serious "
            "and fatal crashes than ZIP codes that received none?")

TIER_ORDER = ["No new units", "1-499 units", "500+ units"]


def _empty_figure(message="No data available for this selection.") -> go.Figure:
    figure = go.Figure()
    figure.add_annotation(text=message, x=0.5, y=0.5, xref="paper", yref="paper",
                          showarrow=False, font={"size": 15, "color": "#64748b"})
    figure.update_layout(template="plotly_white", xaxis={"visible": False}, yaxis={"visible": False})
    return figure


def housing_tiers(df: pd.DataFrame) -> pd.DataFrame:
    """One row per ZIP over the filtered years: total units, average yearly crashes, tier."""
    per_zip = (df.groupby([config.ZIP_COLUMN, config.BOROUGH_COLUMN], as_index=False, observed=True)
                 .agg(total_units=("total_units", "sum"),
                      crashes=("crash_count", "sum"),
                      fatal_crashes=("fatal_crashes", "sum"),
                      years=(config.YEAR_COLUMN, "nunique")))
    # Average per year, so a 1-year filter and a 4-year filter are on the same scale
    per_zip["crashes_per_year"] = per_zip["crashes"] / per_zip["years"]
    per_zip["tier"] = pd.cut(per_zip["total_units"], bins=[-1, 0, 499, float("inf")], labels=TIER_ORDER)
    return per_zip


def build_figure(df: pd.DataFrame, filters: dict) -> go.Figure:
    needed = [config.ZIP_COLUMN, config.BOROUGH_COLUMN, config.YEAR_COLUMN,
              "total_units", "crash_count", "fatal_crashes"]
    if df.empty:
        return _empty_figure()
    if not all(c in df.columns for c in needed):
        return _empty_figure("Required columns are missing.")

    per_zip = housing_tiers(df)
    if per_zip.empty:
        return _empty_figure()

    fig = px.box(per_zip, x="tier", y="crashes_per_year", points="all",
                 category_orders={"tier": TIER_ORDER}, color="tier",
                 color_discrete_sequence=["#94a3b8", "#60a5fa", "#1d4ed8"],
                 hover_name=config.ZIP_COLUMN,
                 hover_data={"tier": False, config.BOROUGH_COLUMN: True, "total_units": ":,",
                             "fatal_crashes": True, "crashes_per_year": ":.1f"},
                 labels={"tier": "Affordable units completed in the ZIP (selected years)",
                         "crashes_per_year": "Serious crashes per year",
                         "total_units": "Units completed", "fatal_crashes": "Fatal crashes"},
                 title=TITLE)
    # Show the number of ZIPs under each box so small groups are visible
    counts = per_zip["tier"].value_counts()
    fig.update_xaxes(ticktext=[f"{t}<br>({counts.get(t, 0)} ZIPs)" for t in TIER_ORDER], tickvals=TIER_ORDER)
    fig.update_layout(template="plotly_white", showlegend=False)
    return fig
