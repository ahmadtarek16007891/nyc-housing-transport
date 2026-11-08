"""Chart 10: Share of deeply affordable units vs how injurious crashes are (Member 5)."""
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import config

TITLE = "Deeply affordable housing share vs injuries per crash, by ZIP"
QUESTION = ("In ZIP codes where a larger share of new units are deeply affordable, are the "
            "serious crashes more injurious?")

MIN_UNITS = 20    # skip ZIPs with a tiny housing base (unstable share)
MIN_CRASHES = 3   # skip ZIPs with too few crashes for a meaningful injuries-per-crash value
INJURY_COLUMNS = ["severe_injuries", "non_severe_injuries"]


def _empty_figure(message="No data available for this selection.") -> go.Figure:
    figure = go.Figure()
    figure.add_annotation(text=message, x=0.5, y=0.5, xref="paper", yref="paper",
                          showarrow=False, font={"size": 15, "color": "#64748b"})
    figure.update_layout(template="plotly_white", xaxis={"visible": False}, yaxis={"visible": False})
    return figure


def build_figure(df: pd.DataFrame, filters: dict) -> go.Figure:
    """One point per ZIP: units-weighted affordable share vs injuries per crash."""
    needed = [config.ZIP_COLUMN, config.BOROUGH_COLUMN, config.HOUSING_METRIC_1_COLUMN,
              config.HOUSING_METRIC_2_COLUMN, config.TRANSPORT_METRIC_1_COLUMN] + INJURY_COLUMNS
    if df.empty or any(col not in df.columns for col in needed):
        return _empty_figure()

    sum_columns = [config.HOUSING_METRIC_1_COLUMN, config.HOUSING_METRIC_2_COLUMN,
                   config.TRANSPORT_METRIC_1_COLUMN] + INJURY_COLUMNS
    per_zip = df.groupby([config.ZIP_COLUMN, config.BOROUGH_COLUMN], as_index=False)[sum_columns].sum()
    per_zip = per_zip[(per_zip[config.HOUSING_METRIC_1_COLUMN] >= MIN_UNITS)
                      & (per_zip[config.TRANSPORT_METRIC_1_COLUMN] >= MIN_CRASHES)].copy()
    if len(per_zip) < 3:
        return _empty_figure("Too few ZIP codes with enough housing and crashes in this selection.")

    per_zip["affordable_share_pct"] = (per_zip[config.HOUSING_METRIC_2_COLUMN]
                                       / per_zip[config.HOUSING_METRIC_1_COLUMN] * 100).round(1)
    per_zip["injuries_per_crash"] = ((per_zip["severe_injuries"] + per_zip["non_severe_injuries"])
                                     / per_zip[config.TRANSPORT_METRIC_1_COLUMN]).round(2)

    figure = px.scatter(
        per_zip, x="affordable_share_pct", y="injuries_per_crash", color=config.BOROUGH_COLUMN,
        size=config.HOUSING_METRIC_1_COLUMN, size_max=28,
        hover_name=config.ZIP_COLUMN,
        hover_data={config.HOUSING_METRIC_1_COLUMN: ":,", config.TRANSPORT_METRIC_1_COLUMN: ":,",
                    "affordable_share_pct": ":.1f", "injuries_per_crash": ":.2f"},
        labels={"affordable_share_pct": "Deeply affordable units (% of units completed)",
                "injuries_per_crash": "Injuries per serious crash",
                config.BOROUGH_COLUMN: "Borough",
                config.HOUSING_METRIC_1_COLUMN: "Units completed",
                config.TRANSPORT_METRIC_1_COLUMN: "Serious crashes"},
    )

    # Dashed trend line (least squares) and Spearman rank correlation, no extra libraries needed.
    slope, intercept = np.polyfit(per_zip["affordable_share_pct"], per_zip["injuries_per_crash"], 1)
    x_line = np.array([per_zip["affordable_share_pct"].min(), per_zip["affordable_share_pct"].max()])
    figure.add_trace(go.Scatter(x=x_line, y=slope * x_line + intercept, mode="lines",
                                line={"dash": "dash", "color": "#64748b"}, name="Trend", hoverinfo="skip"))
    rho = per_zip["affordable_share_pct"].corr(per_zip["injuries_per_crash"], method="spearman")
    figure.add_annotation(text=f"Spearman ρ = {rho:.2f} (n = {len(per_zip)} ZIPs). Association only, not cause.",
                          xref="paper", yref="paper", x=0.01, y=0.99, showarrow=False,
                          font={"size": 12, "color": "#475569"}, align="left")
    figure.update_layout(template="plotly_white", legend_title_text="Borough")
    return figure
