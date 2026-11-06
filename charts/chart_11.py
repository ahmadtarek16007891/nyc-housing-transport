"""Chart 11: Housing and transport metric relationship."""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

import config

TITLE = 'Housing and transport metric relationship'
QUESTION = 'How does a second housing measure vary with transportation activity?'


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

    x_column = config.HOUSING_METRIC_2_COLUMN
    y_column = config.TRANSPORT_METRIC_2_COLUMN
    if x_column not in df.columns or y_column not in df.columns:
        return _empty_figure("Second housing/transport metric columns are missing.")
    plot_df = df[[x_column, y_column]].dropna()
    if plot_df.empty:
        return _empty_figure()
    return px.scatter(plot_df, x=x_column, y=y_column,
                      title=TITLE, labels={x_column: "Housing metric 2", y_column: "Transportation metric 2"})
