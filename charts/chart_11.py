"""Chart 11: cross-domain Spearman correlation heatmap.

The dashboard chart loader expects TITLE, QUESTION and build_figure(df, filters).
The course team interface also asks for make_chart_11(df), so both interfaces
are provided here.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import plotly.graph_objects as go

TITLE = "Housing Activity and Serious-Crash Correlations"
QUESTION = (
    "Across ZIP-year observations, which affordable-housing production indicators "
    "have the strongest monotonic association with serious crashes and injury outcomes?"
)

HOUSING_METRICS: Dict[str, str] = {
    "buildings_completed": "Buildings completed",
    "projects_completed": "Projects completed",
    "total_units": "Affordable units completed",
    "new_construction_units": "New-construction units",
    "preservation_units": "Preservation units",
    "deeply_affordable_units": "Deeply affordable units",
    "low_income_units": "Low-income units",
    "units_started": "Units in projects started",
}

TRANSPORT_METRICS: Dict[str, str] = {
    "crash_count": "Serious crashes",
    "fatal_crashes": "Fatal crashes",
    "fatalities": "Fatalities",
    "severe_injuries": "Severe injuries",
    "non_severe_injuries": "Non-severe injuries",
}


def _empty_figure(message: str = "No data for these filters") -> go.Figure:
    figure = go.Figure()
    figure.add_annotation(
        text=message,
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font={"size": 16, "color": "#64748b"},
    )
    figure.update_layout(
        template="plotly_white",
        xaxis={"visible": False},
        yaxis={"visible": False},
        margin={"l": 20, "r": 20, "t": 35, "b": 20},
    )
    return figure


def _pairwise_spearman(
    dataframe: pd.DataFrame,
    housing_columns: List[str],
    transport_columns: List[str],
) -> Tuple[np.ndarray, np.ndarray]:
    """Calculate pairwise Spearman rho and pair counts, using valid values only."""
    rho_values = np.full((len(housing_columns), len(transport_columns)), np.nan)
    pair_counts = np.zeros((len(housing_columns), len(transport_columns)), dtype=int)

    for row_index, housing_column in enumerate(housing_columns):
        for column_index, transport_column in enumerate(transport_columns):
            pair = dataframe[[housing_column, transport_column]].apply(
                pd.to_numeric, errors="coerce"
            ).dropna()
            pair_counts[row_index, column_index] = len(pair)

            # At least three observations and variation in both variables are
            # needed for an interpretable rank correlation.
            if (
                len(pair) >= 3
                and pair[housing_column].nunique() > 1
                and pair[transport_column].nunique() > 1
            ):
                rho_values[row_index, column_index] = pair[housing_column].corr(
                    pair[transport_column], method="spearman"
                )

    return rho_values, pair_counts


def make_chart_11(df: pd.DataFrame) -> go.Figure:
    """Return a Plotly heatmap of housing-to-transport Spearman correlations.

    Only cross-domain pairs are shown. ZIP code, year, coordinates, category
    labels and derived ratios are intentionally excluded from the matrix.
    """
    if df is None or df.empty:
        return _empty_figure()

    housing_columns = [
        column
        for column in HOUSING_METRICS
        if column in df.columns and pd.to_numeric(df[column], errors="coerce").nunique() > 1
    ]
    transport_columns = [
        column
        for column in TRANSPORT_METRICS
        if column in df.columns and pd.to_numeric(df[column], errors="coerce").nunique() > 1
    ]

    if not housing_columns or not transport_columns:
        return _empty_figure(
            "Required housing and transportation metrics are not available"
        )

    rho_values, pair_counts = _pairwise_spearman(
        df, housing_columns, transport_columns
    )
    if not np.isfinite(rho_values).any():
        return _empty_figure("Not enough variation to calculate correlations")

    row_labels = [HOUSING_METRICS[column] for column in housing_columns]
    column_labels = [TRANSPORT_METRICS[column] for column in transport_columns]
    text_values = [
        ["—" if not np.isfinite(value) else f"{value:.2f}" for value in row]
        for row in rho_values
    ]

    figure = go.Figure(
        data=go.Heatmap(
            z=rho_values,
            x=column_labels,
            y=row_labels,
            zmin=-1,
            zmax=1,
            zmid=0,
            colorscale="RdBu",
            colorbar={"title": {"text": "Spearman ρ"}},
            text=text_values,
            texttemplate="%{text}",
            customdata=pair_counts,
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Transportation metric: %{x}<br>"
                "Spearman ρ: %{z:.3f}<br>"
                "Valid ZIP-year pairs: %{customdata:,}"
                "<extra></extra>"
            ),
        )
    )
    figure.update_layout(
        title=TITLE,
        template="plotly_white",
        xaxis_title="Transportation outcome (ZIP-year totals)",
        yaxis_title="Affordable-housing activity (ZIP-year totals)",
        xaxis={"side": "bottom", "tickangle": -15},
        margin={"l": 175, "r": 35, "t": 65, "b": 105},
        height=max(560, 48 * len(row_labels) + 170),
    )
    return figure


def build_figure(df: pd.DataFrame, filters: dict | None = None) -> go.Figure:
    """Adapter used by the existing dashboard chart_loader.py."""
    return make_chart_11(df)
