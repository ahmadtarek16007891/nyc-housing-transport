"""Chart 02 (Member 1): yearly trend of affordable units and crashes."""
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import config

TITLE = "Yearly Trend Analysis"
QUESTION = "Do crashes rise or fall in years when more affordable units are completed?"


def _empty_figure(message="No data available for this selection.") -> go.Figure:
    figure = go.Figure()
    figure.add_annotation(text=message, x=0.5, y=0.5, xref="paper", yref="paper",
                          showarrow=False, font={"size": 15, "color": "#64748b"})
    figure.update_layout(template="plotly_white", xaxis={"visible": False}, yaxis={"visible": False})
    return figure


def build_figure(df, filters):
    needed = [config.YEAR_COLUMN, "total_units", "crash_count"]
    if df.empty:
        return _empty_figure()
    if not all(c in df.columns for c in needed):
        return _empty_figure("Required columns are missing.")

    yearly = (df.groupby(config.YEAR_COLUMN, as_index=False)
                .agg(total_units=("total_units", "sum"), crash_count=("crash_count", "sum")))

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_bar(x=yearly[config.YEAR_COLUMN], y=yearly["total_units"],
                name="Affordable units completed", marker_color="#4f46e5", secondary_y=False)
    fig.add_scatter(x=yearly[config.YEAR_COLUMN], y=yearly["crash_count"],
                    name="Serious crashes", mode="lines+markers",
                    line=dict(color="#e11d48", width=3), secondary_y=True)
    fig.update_layout(
        template="plotly_white", hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig.update_xaxes(type="category")  # whole years only, no 2022.5 ticks
    # Both axes start at zero so neither trend is exaggerated
    fig.update_yaxes(title_text="Units completed", rangemode="tozero", secondary_y=False)
    fig.update_yaxes(title_text="Serious crashes", rangemode="tozero", secondary_y=True)
    fig.add_annotation(
        text="Only a few years of data: shows co-movement, not cause",
        xref="paper", yref="paper", x=0.01, y=0.01, xanchor="left", yanchor="bottom",
        showarrow=False, font={"size": 10, "color": "#64748b"})
    return fig