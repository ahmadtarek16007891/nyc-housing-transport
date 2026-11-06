"""Chart 12: Illustrative borough-level map using approximate centroids."""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

import config

TITLE = "Housing activity by NYC borough (illustrative map)"
QUESTION = "How does housing activity vary geographically across the five boroughs?"


# Approximate borough centroids for a borough-level overview only. These are
# not ZIP-code coordinates and must not be interpreted as precise locations.
BOROUGH_CENTROIDS = {
    "Bronx": (40.85, -73.87),
    "Brooklyn": (40.65, -73.95),
    "Manhattan": (40.78, -73.97),
    "Queens": (40.73, -73.79),
    "Staten Island": (40.58, -74.15),
}


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
    """Plot borough aggregates at approximate borough centroid coordinates."""
    metric = config.HOUSING_METRIC_2_COLUMN
    borough_column = config.BOROUGH_COLUMN
    if metric not in df.columns or borough_column not in df.columns:
        return _empty_figure("Housing metric or borough column is missing.")

    grouped = df.groupby(borough_column, as_index=False)[metric].sum()
    grouped["latitude"] = grouped[borough_column].map(
        lambda borough: BOROUGH_CENTROIDS.get(str(borough), (None, None))[0]
    )
    grouped["longitude"] = grouped[borough_column].map(
        lambda borough: BOROUGH_CENTROIDS.get(str(borough), (None, None))[1]
    )
    grouped = grouped.dropna(subset=["latitude", "longitude", metric])
    if grouped.empty:
        return _empty_figure("No recognized NYC boroughs in the selected data.")

    figure = px.scatter_geo(
        grouped,
        lat="latitude",
        lon="longitude",
        size=metric,
        color=metric,
        hover_name=borough_column,
        hover_data={metric: True, "latitude": False, "longitude": False},
        title=TITLE,
        projection="natural earth",
        labels={metric: "Housing activity"},
        size_max=42,
    )
    figure.update_geos(
        scope="north america",
        center={"lat": 40.72, "lon": -73.94},
        projection_scale=18,
        showcountries=True,
        showland=True,
        landcolor="#f1f5f9",
    )
    figure.add_annotation(
        text="Approximate borough centroids — not ZIP-level locations",
        x=0.5, y=0.02, xref="paper", yref="paper", showarrow=False,
        font={"size": 10, "color": "#64748b"},
    )
    return figure
