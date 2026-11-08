"""Chart 07 (Member 4): crashes per 100 completed affordable units, borough by year."""
import pandas as pd
import plotly.graph_objects as go

import config

TITLE = "Crashes per 100 affordable units, by borough and year"
QUESTION = ("In which boroughs, and in which years, were serious crashes highest "
            "relative to the amount of new affordable housing completed?")


def _empty_figure(message="No data available for this selection.") -> go.Figure:
    figure = go.Figure()
    figure.add_annotation(text=message, x=0.5, y=0.5, xref="paper", yref="paper",
                          showarrow=False, font={"size": 15, "color": "#64748b"})
    figure.update_layout(template="plotly_white", xaxis={"visible": False}, yaxis={"visible": False})
    return figure


def build_figure(df: pd.DataFrame, filters: dict) -> go.Figure:
    needed = [config.BOROUGH_COLUMN, config.YEAR_COLUMN, "total_units", "crash_count"]
    if df.empty:
        return _empty_figure()
    if not all(c in df.columns for c in needed):
        return _empty_figure("Required columns are missing.")

    # Only ZIP-years that completed units: the rate is undefined (divide by zero) otherwise
    with_units = df[df["total_units"] > 0]
    if with_units.empty:
        return _empty_figure("No affordable units were completed for this selection.")

    grouped = (with_units.groupby([config.BOROUGH_COLUMN, config.YEAR_COLUMN], observed=True)
                         .agg(crashes=("crash_count", "sum"), units=("total_units", "sum"),
                              zips=(config.ZIP_COLUMN, "nunique"))
                         .reset_index())
    # Ratio of sums (not mean of per-ZIP rates), so small ZIPs do not dominate
    grouped["rate"] = grouped["crashes"] / grouped["units"] * 100

    rate = grouped.pivot(index=config.BOROUGH_COLUMN, columns=config.YEAR_COLUMN, values="rate")
    crashes = grouped.pivot(index=config.BOROUGH_COLUMN, columns=config.YEAR_COLUMN, values="crashes")
    units = grouped.pivot(index=config.BOROUGH_COLUMN, columns=config.YEAR_COLUMN, values="units")
    rate = rate.reindex([b for b in config.BOROUGHS if b in rate.index])
    crashes, units = crashes.reindex(rate.index), units.reindex(rate.index)
    years = [str(y) for y in rate.columns]
    # Rates on tiny unit counts (< 200) are unstable: mark them and keep them out of the colour scale
    low_base = units < 200
    stable = rate.where(~low_base)
    zmax = float(stable.max().max()) if stable.notna().any().any() else float(rate.max().max())

    fig = go.Figure(go.Heatmap(
        z=rate.values, x=years, y=list(rate.index), colorscale="YlOrRd", zmin=0, zmax=zmax,
        text=[[("" if pd.isna(v) else f"{v:.1f}" + ("*" if low_base.iat[i, j] else ""))
               for j, v in enumerate(row)] for i, row in enumerate(rate.values)],
        texttemplate="%{text}",
        customdata=[[[crashes.iat[i, j], units.iat[i, j]] for j in range(rate.shape[1])]
                    for i in range(rate.shape[0])],
        hovertemplate=("%{y}, %{x}<br>%{z:.1f} crashes per 100 units"
                       "<br>%{customdata[0]:,.0f} crashes / %{customdata[1]:,.0f} units<extra></extra>"),
        colorbar={"title": "Crashes per<br>100 units"}))
    fig.update_xaxes(type="category", title="Year")
    fig.update_yaxes(title="Borough", autorange="reversed")
    fig.update_layout(template="plotly_white")
    fig.add_annotation(
        text="* under 200 units completed: rate unstable, colour capped. ZIP-years with 0 units excluded.",
        xref="paper", yref="paper", x=0, y=-0.02, xanchor="left", yanchor="top",
        showarrow=False, font={"size": 10, "color": "#64748b"})
    return fig