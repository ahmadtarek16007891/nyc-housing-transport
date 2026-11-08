"""Chart 01 (Member 1): affordable units completed vs serious crashes, per ZIP."""
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import config

TITLE = "Affordable housing completed vs serious crashes, by ZIP"
QUESTION = "Do ZIPs that completed more affordable units also have more serious crashes?"


def _empty_figure(message="No data available for this selection.") -> go.Figure:
    figure = go.Figure()
    figure.add_annotation(text=message, x=0.5, y=0.5, xref="paper", yref="paper",
                          showarrow=False, font={"size": 15, "color": "#64748b"})
    figure.update_layout(template="plotly_white", xaxis={"visible": False}, yaxis={"visible": False})
    return figure


def build_figure(df: pd.DataFrame, filters: dict) -> go.Figure:
    needed = [config.ZIP_COLUMN, config.BOROUGH_COLUMN, "total_units", "crash_count"]
    if df.empty:
        return _empty_figure()
    if not all(c in df.columns for c in needed):
        return _empty_figure("Required columns are missing.")

    # One dot per ZIP, summed over the filtered years
    per_zip = (df.groupby([config.ZIP_COLUMN, config.BOROUGH_COLUMN], as_index=False, observed=True)
                 .agg(total_units=("total_units", "sum"), crash_count=("crash_count", "sum")))
    total_zips = len(per_zip)
    # Log axes cannot show zeros, so those ZIPs are excluded (and reported below)
    shown = per_zip[(per_zip["total_units"] > 0) & (per_zip["crash_count"] > 0)].copy()
    if shown.empty:
        return _empty_figure()

    fig = px.scatter(
        shown, x="total_units", y="crash_count", color=config.BOROUGH_COLUMN,
        hover_name=config.ZIP_COLUMN, log_x=True, log_y=True,
        labels={"total_units": "Affordable units completed (log scale)",
                "crash_count": "Serious crashes (log scale)"},
    )

    # Trend line fitted in log-log space so it matches what the axes show
    if len(shown) >= 3 and shown["total_units"].nunique() > 1:
        log_x, log_y = np.log10(shown["total_units"]), np.log10(shown["crash_count"])
        slope, intercept = np.polyfit(log_x, log_y, 1)
        r_value = np.corrcoef(log_x, log_y)[0, 1]
        xs = np.linspace(log_x.min(), log_x.max(), 50)
        fig.add_trace(go.Scatter(x=10 ** xs, y=10 ** (slope * xs + intercept), mode="lines",
                                 line={"color": "black", "width": 2},
                                 name=f"Trend (log-log r = {r_value:.2f})"))

    fig.add_annotation(
        text=f"Showing {len(shown)} of {total_zips} ZIPs<br>(ZIPs with 0 units or 0 crashes can't show on log axes)",
        xref="paper", yref="paper", x=0.99, y=0.02, xanchor="right", yanchor="bottom",
        showarrow=False, font={"size": 10, "color": "#64748b"}, align="right",
        bgcolor="rgba(255,255,255,0.8)")
    fig.update_layout(template="plotly_white")
    return fig