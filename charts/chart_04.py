"""Chart 04 (Member 2): how severe are crashes in each borough?"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import config

TITLE = "Crash severity by borough"
QUESTION = "In which boroughs is a serious crash most likely to be fatal, and is that changing?"


def _empty_figure(message="No data available for this selection.") -> go.Figure:
    figure = go.Figure()
    figure.add_annotation(text=message, x=0.5, y=0.5, xref="paper", yref="paper",
                          showarrow=False, font={"size": 15, "color": "#64748b"})
    figure.update_layout(template="plotly_white", xaxis={"visible": False}, yaxis={"visible": False})
    return figure


def build_figure(df: pd.DataFrame, filters: dict) -> go.Figure:
    needed = [config.BOROUGH_COLUMN, config.YEAR_COLUMN, "crash_count", "fatal_crashes"]
    if df.empty:
        return _empty_figure()
    if not all(c in df.columns for c in needed):
        return _empty_figure("Required columns are missing.")

    grouped = (df.groupby([config.BOROUGH_COLUMN, config.YEAR_COLUMN], as_index=False, observed=True)
                 .agg(crashes=("crash_count", "sum"), fatal=("fatal_crashes", "sum")))
    grouped = grouped[grouped["crashes"] > 0].copy()
    if grouped.empty:
        return _empty_figure()
    # Share of crashes that were fatal, so big and small boroughs compare fairly
    grouped["fatal_pct"] = grouped["fatal"] / grouped["crashes"] * 100
    grouped["year_label"] = grouped[config.YEAR_COLUMN].astype(str)

    fig = px.bar(grouped, x=config.BOROUGH_COLUMN, y="fatal_pct", color="year_label",
                 barmode="group", category_orders={"year_label": sorted(grouped["year_label"].unique())},
                 hover_data={"crashes": ":,", "fatal": ":,", "fatal_pct": ":.1f", "year_label": False},
                 labels={"fatal_pct": "Fatal crashes (% of serious crashes)",
                         config.BOROUGH_COLUMN: "Borough", "year_label": "Year",
                         "crashes": "Serious crashes", "fatal": "Fatal crashes"})
    fig.update_layout(template="plotly_white", legend=dict(orientation="h", y=1.02, x=1,
                                                           xanchor="right", yanchor="bottom"))
    return fig