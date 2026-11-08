"""NYC Housing & Transportation interactive dashboard."""
import logging

import pandas as pd
import plotly.graph_objects as go
from dash import Dash, Input, Output, State, dcc, html, no_update, ALL, ctx

import config
from search_parser import parse_query
from story_section import STORY_CONTENT
from chart_loader import build_chart_figure, discover_charts

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


def normalize_zip_codes(series: pd.Series) -> pd.Series:
    values = series.astype("string").str.strip()
    values = values.str.replace(r"\.0$", "", regex=True)
    digits = values.str.extract(r"(\d+)", expand=False)
    return digits.str.zfill(5)


def normalize_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    df = dataframe.copy()
    if config.ZIP_COLUMN in df.columns:
        df[config.ZIP_COLUMN] = normalize_zip_codes(df[config.ZIP_COLUMN])
    if config.YEAR_COLUMN in df.columns:
        df[config.YEAR_COLUMN] = pd.to_numeric(
            df[config.YEAR_COLUMN], errors="coerce"
        ).astype("Int64")

    for column in (config.BOROUGH_COLUMN, config.HOUSING_CATEGORY_COLUMN, config.TRANSPORT_CATEGORY_COLUMN):
        if column in df.columns: df[column] = df[column].astype("string")
    return df


def load_startup_data() -> pd.DataFrame:
    """Load the real integrated dataset (fails loudly if the file is missing)."""
    logger.info("Loading integrated dataset from %s", config.DATA_PATH)
    real_df = pd.read_csv(config.DATA_PATH, dtype={config.ZIP_COLUMN: "string"}, low_memory=False)
    return normalize_dataframe(real_df)


DATA = load_startup_data()
CHART_SPECS = discover_charts()


COLORWAY = ["#6366f1", "#ec4899", "#14b8a6", "#f59e0b", "#8b5cf6"]


def style_figure(figure: go.Figure) -> go.Figure:
    """Apply the dashboard theme to any chart. The card header already shows the
    chart title, so the in-figure title is removed to stop it overlapping the plot."""
    figure.update_layout(
        title=None,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#0f172a"),
        margin=dict(l=10, r=10, t=20, b=10),
        colorway=COLORWAY,
    )
    return figure

def dropdown_options(column_name: str):
    if column_name not in DATA.columns:
        values = []
    else:
        values = DATA[column_name].dropna().unique().tolist()
        values = sorted(values, key=lambda value: str(value))
    return [{"label": "All", "value": config.ALL_VALUE}] + [
        {"label": str(value), "value": value.item() if hasattr(value, "item") else value}
        for value in values
    ]


def make_filter_bar():
    year_values = sorted(int(value) for value in DATA[config.YEAR_COLUMN].dropna().unique()) if config.YEAR_COLUMN in DATA.columns else []
    return html.Div(
        [
            html.Div([
                html.Label("Borough", htmlFor="borough-filter"),
                dcc.Dropdown(id="borough-filter", options=dropdown_options(config.FILTER_COLUMNS["borough"]), value=config.ALL_VALUE, clearable=False),
            ], className="filter-control"),
            html.Div([
                html.Label("Year", htmlFor="year-filter"),
                dcc.Dropdown(id="year-filter", options=[{"label": "All", "value": config.ALL_VALUE}] + [{"label": str(year), "value": year} for year in year_values], value=[config.ALL_VALUE], multi=True, placeholder="Select years"),
            ], className="filter-control"),
            html.Div([
                html.Label("Housing Category", htmlFor="housing-category-filter"),
                dcc.Dropdown(id="housing-category-filter", options=dropdown_options(config.FILTER_COLUMNS["housing_category"]), value=config.ALL_VALUE, clearable=False),
            ], className="filter-control"),
            html.Div([
                html.Label("Transportation Category", htmlFor="transportation-category-filter"),
                dcc.Dropdown(id="transportation-category-filter", options=dropdown_options(config.FILTER_COLUMNS["transportation_category"]), value=config.ALL_VALUE, clearable=False),
            ], className="filter-control"),
        ], className="filter-bar",
    )


def make_chart_cards():
    cards = []
    for chart_spec in CHART_SPECS:
        initial_figure = style_figure(build_chart_figure(chart_spec, DATA, {}))
        
        cards.append(
            html.Div(
                [
                    html.Div([
                        html.H3(chart_spec["title"], className="chart-title"),
                        html.Button("⛶ Expand", id={"type": "expand-btn", "index": chart_spec["id"]}, className="expand-button")
                    ], className="chart-header-row"),
                    html.P(chart_spec["question"], className="chart-question"),
                    dcc.Graph(
                        id=f"{chart_spec['id']}-graph",
                        figure=initial_figure,
                        config={"displayModeBar": False, "responsive": True},
                        style={"height": "350px"} # Fixed height for grid alignment
                    ),
                ], className="chart-card",
            )
        )
    return cards


app = Dash(__name__, title="NYC Housing & Transportation", suppress_callback_exceptions=False)
server = app.server

app.layout = html.Div(
    [
        html.Header(
            [
                html.Div([
                    html.P("NYC Open Data Project", className="eyebrow"),
                    html.H1("Housing & Transportation"),
                    html.P("Explore how neighborhood development and transportation patterns intersect across New York City.", className="page-subtitle"),
                ], className="header-titles"),
            ], className="page-header",
        ),
        html.Main(
            [
                html.Section(
                    [
                        html.H2("Global Filters"),
                        make_filter_bar(),
                        html.Div(
                            [
                                dcc.Input(id="search-input", type="text", debounce=True, className="search-input",
                                          placeholder='Search, e.g. "Brooklyn 2022 new buildings", then press Enter'),
                                html.Button("Apply search", id="search-button", n_clicks=0, className="secondary-button"),
                                html.Div(id="search-feedback", className="report-hint"),
                            ], className="search-row",
                        ),
                        html.Div(
                            [
                                html.Div("Configure filters above, then apply them to refresh your dashboard.", className="report-hint"),
                                html.Button("Generate Report", id="generate-report-button", n_clicks=0, className="primary-button"),
                            ], className="report-action-row",
                        ),
                    ], className="control-panel",
                ),
                html.Section(
                    [
                        html.Div(id="report-summary", className="report-summary"),
                        dcc.Loading(
                            html.Div(make_chart_cards(), id="chart-grid", className="chart-grid"),
                            type="dot", color="#6366f1"
                        ),
                        html.Div(id="empty-results-message", className="empty-results"),
                    ], className="visualization-section",
                ),
                html.Section(STORY_CONTENT, className="story-section", id="story"),
            ], className="page-content",
        ),
        html.Footer("NYC Housing & Transportation Dashboard • Milestone 1"),
        
        # --- THE FIX: Modal Component Structure ---
        html.Div(
            [
                html.Div(
                    [
                        html.Button("✕", id="close-modal-btn", className="close-button"),
                        html.Div([
                            html.H2(id="modal-title", style={"margin": "0 0 8px 0", "fontSize": "28px", "fontWeight": "800", "color": "#0f172a"}),
                            html.P(id="modal-question", style={"margin": "0", "fontSize": "16px", "color": "#64748b"}),
                        ], className="modal-title-bar"),
                        
                        html.Div(
                            [
                                dcc.Graph(
                                    id="modal-graph", 
                                    figure=go.Figure(), 
                                    # Provide interactive toolbar for the fullscreen view
                                    config={"displayModeBar": True, "responsive": True},
                                    style={"height": "100%", "width": "100%"} 
                                )
                            ],
                            className="modal-graph-wrapper"
                        )
                    ],
                    className="modal-content"
                )
            ],
            id="chart-modal",
            className="modal-overlay" # Visibility controlled purely by CSS class
        )
    ],
    className="app-shell",
)


@app.callback(
    Output("borough-filter", "value"),
    Output("year-filter", "value"),
    Output("housing-category-filter", "value"),
    Output("transportation-category-filter", "value"),
    Output("search-feedback", "children"),
    Input("search-input", "value"),
    Input("search-button", "n_clicks"),
    prevent_initial_call=True,
)
def apply_search(query, _clicks):
    """Fill the dropdowns from the typed query. Charts update only on Generate Report."""
    filters, found = parse_query(query)
    if not (query or "").strip():
        message = "Filters reset."
    elif not found:
        message = "No filters recognized. Try a borough, a year (2022-2025) or words like new buildings, fatal."
    else:
        message = "Applied: " + ", ".join(found) + ". Click Generate Report."
    return (filters["borough"], filters["year"], filters["housing_category"],
            filters["transportation_category"], message)


def apply_filters(dataframe, filters):
    filtered = dataframe.copy()
    filters = filters or {}
    simple_filters = [("borough", config.BOROUGH_COLUMN), ("housing_category", config.HOUSING_CATEGORY_COLUMN), ("transportation_category", config.TRANSPORT_CATEGORY_COLUMN)]
    for filter_key, column_name in simple_filters:
        selected = filters.get(filter_key, config.ALL_VALUE)
        if column_name in filtered.columns and selected not in (None, "", config.ALL_VALUE):
            filtered = filtered[filtered[column_name].astype(str) == str(selected)]
    selected_years = filters.get("year", [config.ALL_VALUE])
    if selected_years is None:
        selected_years = [config.ALL_VALUE]
    if not isinstance(selected_years, list):
        selected_years = [selected_years]
    # If real years are picked alongside "All", the real years win
    real_years = [y for y in selected_years if y != config.ALL_VALUE]
    if config.YEAR_COLUMN in filtered.columns and real_years:
        numeric_years = pd.to_numeric(pd.Series(real_years), errors="coerce").dropna().astype(int)
        filtered = filtered[filtered[config.YEAR_COLUMN].isin(numeric_years)]
    return filtered


# --- THE FIX: Smart Modal Layout Callback ---
chart_outputs = [Output(f"chart_{number:02d}-graph", "figure") for number in range(1, 13)]
chart_states = [State(f"chart_{number:02d}-graph", "figure") for number in range(1, 13)]

@app.callback(
    Output("chart-modal", "className"),
    Output("modal-graph", "figure"),
    Output("modal-title", "children"),
    Output("modal-question", "children"),
    Input({"type": "expand-btn", "index": ALL}, "n_clicks"),
    Input("close-modal-btn", "n_clicks"),
    *chart_states,
    prevent_initial_call=True
)
def toggle_modal(expand_clicks, close_click, *figures):
    triggered = ctx.triggered_id
    
    if not triggered or triggered == "close-modal-btn":
        return "modal-overlay", no_update, no_update, no_update
        
    if isinstance(triggered, dict) and triggered.get("type") == "expand-btn":
        if not any(c for c in expand_clicks if c):
            return no_update, no_update, no_update, no_update

        chart_id = triggered["index"]
        chart_index = int(chart_id.split("_")[1]) - 1 
        
        # CRITICAL FIX: Convert the incoming dictionary back into a Plotly Figure
        raw_fig_dict = figures[chart_index]
        expanded_fig = go.Figure(raw_fig_dict) if raw_fig_dict else go.Figure()
        
        # Now we can safely use Plotly methods
        expanded_fig.update_layout(
            height=None,      
            autosize=True,    
            margin=dict(l=40, r=40, t=40, b=40) 
        )
        
        title = next((spec["title"] for spec in CHART_SPECS if spec["id"] == chart_id), "Expanded View")
        question = next((spec["question"] for spec in CHART_SPECS if spec["id"] == chart_id), "")
        
        return "modal-overlay visible", expanded_fig, title, question
        
    return "modal-overlay", no_update, no_update, no_update

@app.callback(
    chart_outputs + [Output("empty-results-message", "children"), Output("empty-results-message", "className"), Output("report-summary", "children")],
    Input("generate-report-button", "n_clicks"),
    State("borough-filter", "value"), State("year-filter", "value"), State("housing-category-filter", "value"), State("transportation-category-filter", "value"),
    prevent_initial_call=True,
)
def generate_report(_n_clicks, borough, years, housing_category, transportation_category):
    current_filters = {"borough": borough, "year": years, "housing_category": housing_category, "transportation_category": transportation_category}
    filtered_df = apply_filters(DATA, current_filters)

    figures = []
    for chart_spec in CHART_SPECS:
        figures.append(style_figure(build_chart_figure(chart_spec, filtered_df, current_filters)))

    if filtered_df.empty:
        return tuple(figures) + ("No results match the selected filters.", "empty-results visible", "No matching records.")
    
    summary = f"Showing {len(filtered_df):,} ZIP/year records across {filtered_df[config.ZIP_COLUMN].nunique():,} NYC ZIP codes."
    return tuple(figures) + ("", "empty-results", summary)

if __name__ == "__main__":
    import os
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8050)))