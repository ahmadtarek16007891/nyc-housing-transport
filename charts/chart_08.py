"""Chart 08: Housing activity by category."""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

import config

TITLE = 'Housing activity by category'
QUESTION = 'How does housing activity vary across housing categories?'


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
    category = config.HOUSING_CATEGORY_COLUMN
    if column not in df.columns or category not in df.columns:
        return _empty_figure("Housing metric/category columns are missing.")
    plot_df = df[[column, category]].dropna()
    if plot_df.empty:
        return _empty_figure()
    return px.box(plot_df, x=category, y=column, points="outliers", title=TITLE,
                  labels={column: "Housing activity", category: "Housing category"})
