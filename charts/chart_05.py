"""Chart 05: ZIP/year activity heatmap."""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

import config

TITLE = 'ZIP/year activity heatmap'
QUESTION = 'Which borough-year combinations show higher housing activity?'


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

    value_column = config.HOUSING_METRIC_1_COLUMN
    if value_column not in df.columns or config.YEAR_COLUMN not in df.columns or config.BOROUGH_COLUMN not in df.columns:
        return _empty_figure("Required columns for the heatmap are missing.")
    pivot = df.pivot_table(index=config.BOROUGH_COLUMN, columns=config.YEAR_COLUMN,
                           values=value_column, aggfunc="sum")
    if pivot.empty:
        return _empty_figure()
    return px.imshow(pivot, aspect="auto", color_continuous_scale="Blues",
                     title=TITLE, labels={"x": "Year", "y": "Borough", "color": "Housing activity"})
