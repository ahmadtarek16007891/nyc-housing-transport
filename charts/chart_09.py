"""Chart 09: ZIP codes with the most serious crashes per 100 affordable units (Member 5)."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import config

TITLE = "ZIP codes with the most serious crashes per 100 affordable units"
QUESTION = ("Which ZIP codes had the most serious crashes relative to the amount of "
            "affordable housing they completed?")

MIN_UNITS = 100  # ZIPs with fewer completed units give unstable rates, so they are skipped
TOP_N = 10


def _empty_figure(message="No data available for this selection.") -> go.Figure:
    figure = go.Figure()
    figure.add_annotation(text=message, x=0.5, y=0.5, xref="paper", yref="paper",
                          showarrow=False, font={"size": 15, "color": "#64748b"})
    figure.update_layout(template="plotly_white", xaxis={"visible": False}, yaxis={"visible": False})
    return figure


def build_figure(df: pd.DataFrame, filters: dict) -> go.Figure:
    """Sum crashes and units per ZIP over the selected rows, then rank the rate."""
    needed = [config.ZIP_COLUMN, config.BOROUGH_COLUMN,
              config.HOUSING_METRIC_1_COLUMN, config.TRANSPORT_METRIC_1_COLUMN]
    if df.empty or any(col not in df.columns for col in needed):
        return _empty_figure()

    # Sum first, divide after: averaging yearly rates would overweight tiny years.
    per_zip = (df.groupby([config.ZIP_COLUMN, config.BOROUGH_COLUMN], as_index=False)
                 [[config.HOUSING_METRIC_1_COLUMN, config.TRANSPORT_METRIC_1_COLUMN]].sum())
    per_zip = per_zip[per_zip[config.HOUSING_METRIC_1_COLUMN] >= MIN_UNITS].copy()
    if per_zip.empty:
        return _empty_figure(f"No ZIP code completed at least {MIN_UNITS} units in this selection.")

    per_zip["rate"] = (per_zip[config.TRANSPORT_METRIC_1_COLUMN]
                       / per_zip[config.HOUSING_METRIC_1_COLUMN] * 100).round(1)
    top = per_zip.nlargest(TOP_N, "rate").sort_values("rate")
    top["zip_label"] = "ZIP " + top[config.ZIP_COLUMN].astype(str)

    figure = px.bar(
        top, x="rate", y="zip_label", color=config.BOROUGH_COLUMN, orientation="h",
        hover_data={config.HOUSING_METRIC_1_COLUMN: ":,", config.TRANSPORT_METRIC_1_COLUMN: ":,",
                    "rate": ":.1f", "zip_label": False, config.BOROUGH_COLUMN: False},
        labels={"rate": "Serious crashes per 100 affordable units", "zip_label": "",
                config.BOROUGH_COLUMN: "Borough",
                config.HOUSING_METRIC_1_COLUMN: "Units completed",
                config.TRANSPORT_METRIC_1_COLUMN: "Serious crashes"},
    )
    figure.update_layout(template="plotly_white", legend_title_text="Borough")
    return figure
