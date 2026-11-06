"""Chart 07: Housing vs transportation."""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

import config

TITLE = 'Housing vs transportation'
QUESTION = 'Do ZIP/year observations with higher housing activity also show higher transportation activity?'


def _empty_figure(message="No data available for this selection.") -> go.Figure:
    figure = go.Figure()
    figure.add_annotation(
        text=message, x=0.5, y=0.5, xref="paper", yref="paper",
        showarrow=False, font={"size": 15, "color": "#64748b"}
    )
    figure.update_layout(template="plotly_white", xaxis={"visible": False},
                         yaxis={"visible": False})
    return figure


def build_figure(df: pd.DataFrame, filters: dict) -> go.Figure:
    """Build this chart from the already-filtered dashboard DataFrame."""
    if df.empty:
        return _empty_figure()

    x_column = config.HOUSING_METRIC_1_COLUMN
    y_column = config.TRANSPORT_METRIC_1_COLUMN
    required = [x_column, y_column]
    if any(column not in df.columns for column in required):
        return _empty_figure("Housing/transport metric columns are missing.")
    plot_df = df[required + ([config.BOROUGH_COLUMN] if config.BOROUGH_COLUMN in df.columns else [])].dropna()
    if plot_df.empty:
        return _empty_figure()
    color = config.BOROUGH_COLUMN if config.BOROUGH_COLUMN in plot_df.columns else None
    return px.scatter(plot_df, x=x_column, y=y_column, color=color,
                      hover_data=[config.ZIP_COLUMN, config.YEAR_COLUMN] if config.ZIP_COLUMN in plot_df.columns and config.YEAR_COLUMN in plot_df.columns else None,
                      title=TITLE, labels={x_column: "Housing metric", y_column: "Transportation metric"})
