"""Chart 06: Housing metric distribution."""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

import config

TITLE = 'Housing metric distribution'
QUESTION = 'How is the housing metric distributed across ZIP/year observations?'


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

    column = config.HOUSING_METRIC_1_COLUMN
    if column not in df.columns:
        return _empty_figure("Housing metric column is missing.")
    return px.histogram(df, x=column, nbins=20, title=TITLE,
                        labels={column: "Housing activity"})
