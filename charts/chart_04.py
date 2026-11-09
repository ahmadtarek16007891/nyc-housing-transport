"""Chart 04 (Member 2): injuries per serious crash, borough x year (heatmap)."""
import pandas as pd
import plotly.graph_objects as go

import config

TITLE = "Injuries per serious crash: borough by year"
QUESTION = ("In which borough and year do serious crashes injure the most people per crash, "
            "and is the pattern changing over time?")


def _empty_figure(message="No data available for this selection.") -> go.Figure:
    """Friendly placeholder so an empty filter never crashes the dashboard."""
    figure = go.Figure()
    figure.add_annotation(text=message, x=0.5, y=0.5, xref="paper", yref="paper",
                          showarrow=False, font={"size": 15, "color": "#64748b"})
    figure.update_layout(template="plotly_white", xaxis={"visible": False}, yaxis={"visible": False})
    return figure


def build_figure(df: pd.DataFrame, filters: dict) -> go.Figure:
    injury_cols = ["severe_injuries", "non_severe_injuries"]
    needed = [config.BOROUGH_COLUMN, config.YEAR_COLUMN, config.TRANSPORT_METRIC_1_COLUMN] + injury_cols
    if df.empty:
        return _empty_figure()
    if not all(c in df.columns for c in needed):
        return _empty_figure("Required columns are missing.")

    grouped = (df.groupby([config.BOROUGH_COLUMN, config.YEAR_COLUMN], observed=True)
                 [[config.TRANSPORT_METRIC_1_COLUMN] + injury_cols].sum().reset_index())
    grouped = grouped[grouped[config.TRANSPORT_METRIC_1_COLUMN] > 0].copy()   # a ratio needs at least 1 crash
    if grouped.empty:
        return _empty_figure("No serious crashes recorded for this selection.")

    crashes = grouped[config.TRANSPORT_METRIC_1_COLUMN]
    # Ratio of sums (not mean of ZIP ratios) so big ZIPs weigh more, as they should
    grouped["injuries_per_crash"] = (grouped[injury_cols].sum(axis=1) / crashes).round(2)

    rate = grouped.pivot(index=config.BOROUGH_COLUMN, columns=config.YEAR_COLUMN, values="injuries_per_crash")
    count = grouped.pivot(index=config.BOROUGH_COLUMN, columns=config.YEAR_COLUMN,
                          values=config.TRANSPORT_METRIC_1_COLUMN).reindex(index=rate.index, columns=rate.columns)

    fig = go.Figure(go.Heatmap(
        z=rate.values, x=[str(c) for c in rate.columns], y=list(rate.index),
        customdata=count.values, colorscale="YlOrRd", colorbar=dict(title="Injuries<br>per crash"),
        text=rate.round(2).astype(str).values, texttemplate="%{text}",
        hovertemplate=("Borough: %{y}<br>Year: %{x}<br>Injuries per crash: %{z:.2f}"
                       "<br>Serious crashes behind it: %{customdata:,.0f}<extra></extra>")))
    fig.update_layout(template="plotly_white", xaxis_title="Year", yaxis_title="Borough")
    return fig
