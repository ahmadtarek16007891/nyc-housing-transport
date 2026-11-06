"""Chart 09: Transportation activity over time."""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

import config

TITLE = 'Transportation activity over time'
QUESTION = 'How has transportation activity changed across years?'


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

    column = config.TRANSPORT_METRIC_1_COLUMN
    if column not in df.columns or config.YEAR_COLUMN not in df.columns:
        return _empty_figure("Transportation metric or year column is missing.")
    grouped = df.groupby(config.YEAR_COLUMN, as_index=False)[column].mean()
    return px.line(grouped, x=config.YEAR_COLUMN, y=column, markers=True,
                   title=TITLE, labels={column: "Average transportation activity", config.YEAR_COLUMN: "Year"})
