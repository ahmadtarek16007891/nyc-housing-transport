"""Chart 10: Transportation category mix."""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

import config

TITLE = 'Transportation category mix'
QUESTION = 'How are transportation observations distributed across categories?'


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

    column = config.TRANSPORT_CATEGORY_COLUMN
    if column not in df.columns:
        return _empty_figure("Transportation category column is missing.")
    counts = df[column].dropna().value_counts().rename_axis("category").reset_index(name="records")
    if counts.empty:
        return _empty_figure()
    return px.pie(counts, names="category", values="records", title=TITLE)
