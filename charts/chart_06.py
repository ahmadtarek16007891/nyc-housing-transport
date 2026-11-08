"""Chart 06 (Member 3): map of new affordable housing vs change in serious crashes, per ZIP."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import config

TITLE = "Where new affordable housing is going, and whether serious crashes there are rising"
QUESTION = ("Is new affordable housing being completed in ZIP codes where serious crashes are "
            "rising, or where they are falling?")


def _empty_figure(message="No data available for this selection.") -> go.Figure:
    figure = go.Figure()
    figure.add_annotation(text=message, x=0.5, y=0.5, xref="paper", yref="paper",
                          showarrow=False, font={"size": 15, "color": "#64748b"})
    figure.update_layout(template="plotly_white", xaxis={"visible": False}, yaxis={"visible": False})
    return figure


def crash_change_by_zip(df: pd.DataFrame) -> pd.DataFrame:
    """Per ZIP: units completed, and crashes in the last selected year minus the first."""
    year = config.YEAR_COLUMN
    first, last = df[year].min(), df[year].max()
    keys = [config.ZIP_COLUMN, config.BOROUGH_COLUMN, "latitude", "longitude"]
    per_zip = (df.groupby(keys, as_index=False, observed=True)
                 .agg(total_units=("total_units", "sum"), crashes=("crash_count", "sum")))
    first_c = df[df[year] == first].groupby(config.ZIP_COLUMN)["crash_count"].sum()
    last_c = df[df[year] == last].groupby(config.ZIP_COLUMN)["crash_count"].sum()
    per_zip["crash_change"] = per_zip[config.ZIP_COLUMN].map(last_c - first_c)
    per_zip["period"] = f"{first} to {last}"
    return per_zip


def build_figure(df: pd.DataFrame, filters: dict) -> go.Figure:
    needed = [config.ZIP_COLUMN, config.BOROUGH_COLUMN, config.YEAR_COLUMN,
              "latitude", "longitude", "total_units", "crash_count"]
    if df.empty:
        return _empty_figure()
    if not all(c in df.columns for c in needed):
        return _empty_figure("Required columns are missing.")
    if df[config.YEAR_COLUMN].nunique() < 2:
        return _empty_figure("Select at least two years to see how crashes changed.")

    per_zip = crash_change_by_zip(df).dropna(subset=["latitude", "longitude", "crash_change"])
    if per_zip.empty:
        return _empty_figure()
    # Bubble size = units; ZIPs with 0 units still appear as small dots
    per_zip["bubble"] = per_zip["total_units"].clip(lower=20)
    limit = max(1, per_zip["crash_change"].abs().quantile(0.95))

    fig = px.scatter_map(
        per_zip, lat="latitude", lon="longitude", size="bubble", size_max=32,
        color="crash_change", color_continuous_scale="RdBu_r", range_color=[-limit, limit],
        hover_name=config.ZIP_COLUMN,
        hover_data={config.BOROUGH_COLUMN: True, "total_units": ":,", "crash_change": True,
                    "period": True, "bubble": False, "latitude": False, "longitude": False},
        labels={"crash_change": "Change in serious crashes", "total_units": "Units completed",
                "period": "Compared"},
        zoom=9.2, center={"lat": 40.70, "lon": -73.94}, map_style="carto-positron", title=TITLE)
    fig.update_layout(margin={"l": 0, "r": 0, "t": 50, "b": 0},
                      coloraxis_colorbar={"title": "Crash change<br>(red = rising)"})
    return fig
