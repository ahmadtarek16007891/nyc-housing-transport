"""Chart 08 (Member 4): how deadly are crashes in ZIP-years by housing type?"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import config

TITLE = "Crash severity by type of housing activity"
QUESTION = ("Are serious crashes more likely to be fatal in ZIP-years dominated by new "
            "construction than by preservation, or with no completions?")

CATEGORY_ORDER = ["New Construction", "Preservation", "No completions"]


def _empty_figure(message="No data available for this selection.") -> go.Figure:
    figure = go.Figure()
    figure.add_annotation(text=message, x=0.5, y=0.5, xref="paper", yref="paper",
                          showarrow=False, font={"size": 15, "color": "#64748b"})
    figure.update_layout(template="plotly_white", xaxis={"visible": False}, yaxis={"visible": False})
    return figure


def build_figure(df: pd.DataFrame, filters: dict) -> go.Figure:
    needed = [config.HOUSING_CATEGORY_COLUMN, "crash_count", "fatal_crashes"]
    if df.empty:
        return _empty_figure()
    if not all(c in df.columns for c in needed):
        return _empty_figure("Required columns are missing.")

    grouped = (df.groupby(config.HOUSING_CATEGORY_COLUMN, observed=True)
                 .agg(crashes=("crash_count", "sum"), fatal=("fatal_crashes", "sum"),
                      zip_years=(config.ZIP_COLUMN, "size"))
                 .reset_index())
    grouped = grouped[grouped["crashes"] > 0].copy()
    if grouped.empty:
        return _empty_figure()
    # Pooled share (total fatal / total crashes): stable even when single ZIP-years are small
    grouped["fatal_pct"] = grouped["fatal"] / grouped["crashes"] * 100

    # Approximate 95% confidence interval for a proportion.
    # This treats individual crashes as independent observations.
    p = grouped["fatal"] / grouped["crashes"]
    grouped["ci"] = 1.96 * (p * (1 - p) / grouped["crashes"]) ** 0.5 * 100
    grouped["label"] = grouped.apply(
        lambda r: f"{r[config.HOUSING_CATEGORY_COLUMN]}<br>({r['zip_years']:,} ZIP-years)", axis=1)
    order = {c: i for i, c in enumerate(CATEGORY_ORDER)}
    grouped = grouped.sort_values(config.HOUSING_CATEGORY_COLUMN, key=lambda s: s.map(order))

    fig = px.bar(grouped, x="label", y="fatal_pct", color=config.HOUSING_CATEGORY_COLUMN,
                 color_discrete_map={"New Construction": "#6366f1", "Preservation": "#14b8a6",
                                     "No completions": "#94a3b8"},
                 text=grouped["fatal_pct"].map(lambda v: f"{v:.1f}%"),
                 error_y="ci",
                 hover_data={"crashes": ":,", "fatal": ":,", "fatal_pct": ":.1f", "ci": ":.1f", "label": False},
                 labels={"fatal_pct": "Fatal crashes (% of serious crashes)", "label": "",
                         "crashes": "Serious crashes", "fatal": "Fatal crashes"})
    fig.update_traces(textposition="inside")  # outside text would collide with the error bars
    fig.update_yaxes(rangemode="tozero")
    fig.update_layout(template="plotly_white", showlegend=False)
    fig.add_annotation(text="Error bars: approximate 95% confidence interval",
                    xref="paper", yref="paper", x=0.99, y=0.99, xanchor="right", yanchor="top",
                    showarrow=False, font={"size": 10, "color": "#64748b"})
    return fig