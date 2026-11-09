"""Chart 03 (Member 2): serious crashes per year in each borough (line chart)."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import config

TITLE = "Serious crashes per year by borough"
QUESTION = ("How did the number of serious-injury and fatal crashes change from year to year "
            "in each borough, and which boroughs saw the biggest rise?")


def _empty_figure(message="No data available for this selection.") -> go.Figure:
    """Friendly placeholder so an empty filter never crashes the dashboard."""
    figure = go.Figure()
    figure.add_annotation(text=message, x=0.5, y=0.5, xref="paper", yref="paper",
                          showarrow=False, font={"size": 15, "color": "#64748b"})
    figure.update_layout(template="plotly_white", xaxis={"visible": False}, yaxis={"visible": False})
    return figure


def build_figure(df: pd.DataFrame, filters: dict) -> go.Figure:
    """df is already filtered by the app; we only aggregate ZIP-year rows to borough-year."""
    needed = [config.BOROUGH_COLUMN, config.YEAR_COLUMN, config.TRANSPORT_METRIC_1_COLUMN]
    if df.empty:
        return _empty_figure()
    if not all(c in df.columns for c in needed):
        return _empty_figure("Required columns are missing.")

    # Sum crashes of all ZIPs in a borough for each year
    by_year = (df.groupby([config.BOROUGH_COLUMN, config.YEAR_COLUMN], as_index=False, observed=True)
                 [config.TRANSPORT_METRIC_1_COLUMN].sum()
                 .rename(columns={config.TRANSPORT_METRIC_1_COLUMN: "crashes"}))
    if by_year["crashes"].sum() == 0:
        return _empty_figure("No serious crashes recorded for this selection.")

    # Change since the first selected year, shown on hover (counts, not rates: no traffic data)
    first = by_year.sort_values(config.YEAR_COLUMN).groupby(config.BOROUGH_COLUMN, observed=True)["crashes"].transform("first")
    by_year["change_pct"] = ((by_year["crashes"] - first) / first.where(first > 0) * 100).round(1)

    fig = px.line(by_year.sort_values(config.YEAR_COLUMN), x=config.YEAR_COLUMN, y="crashes",
                  color=config.BOROUGH_COLUMN, markers=True,
                  hover_data={"change_pct": ":+.1f", "crashes": ":,", config.YEAR_COLUMN: False},
                  labels={"crashes": "Serious-injury or fatal crashes", config.YEAR_COLUMN: "Year",
                          config.BOROUGH_COLUMN: "Borough", "change_pct": "Change vs first year (%)"})
    fig.update_xaxes(dtick=1)
    fig.update_layout(template="plotly_white", hovermode="x unified",
                      legend=dict(orientation="h", y=1.02, x=1, xanchor="right", yanchor="bottom"))
    return fig
