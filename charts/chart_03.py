"""Chart 03 (Member 2): affordable units by borough, new construction vs preservation."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import config

TITLE = "New construction vs preservation by borough"
QUESTION = ("Is affordable housing in each borough mostly newly built, "
            "or preserved from existing buildings?")


def _empty_figure(message="No data available for this selection.") -> go.Figure:
    figure = go.Figure()
    figure.add_annotation(text=message, x=0.5, y=0.5, xref="paper", yref="paper",
                          showarrow=False, font={"size": 15, "color": "#64748b"})
    figure.update_layout(template="plotly_white", xaxis={"visible": False}, yaxis={"visible": False})
    return figure


def build_figure(df: pd.DataFrame, filters: dict) -> go.Figure:
    unit_cols = ["new_construction_units", "preservation_units"]
    if df.empty:
        return _empty_figure()
    if not all(c in df.columns for c in [config.BOROUGH_COLUMN] + unit_cols):
        return _empty_figure("Required columns are missing.")

    by_borough = df.groupby(config.BOROUGH_COLUMN, as_index=False, observed=True)[unit_cols].sum()
    if by_borough[unit_cols].to_numpy().sum() == 0:
        return _empty_figure("No affordable units were completed for this selection.")

    long = by_borough.melt(id_vars=config.BOROUGH_COLUMN, var_name="type", value_name="units")
    long["type"] = long["type"].map({"new_construction_units": "New construction",
                                     "preservation_units": "Preservation"})
    fig = px.bar(long, x=config.BOROUGH_COLUMN, y="units", color="type", barmode="stack",
                 color_discrete_map={"New construction": "#6366f1", "Preservation": "#14b8a6"},
                 labels={"units": "Affordable units completed", config.BOROUGH_COLUMN: "Borough",
                         "type": "Type"})
    fig.update_layout(template="plotly_white", legend=dict(orientation="h", y=1.02, x=1,
                                                           xanchor="right", yanchor="bottom"))
    return fig