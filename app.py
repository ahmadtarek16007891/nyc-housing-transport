"""NYC Housing & Transportation interactive dashboard."""
import logging
import copy # Used to perfectly duplicate and resize the chart for the modal

import pandas as pd
import plotly.graph_objects as go
from dash import Dash, Input, Output, State, dcc, html, no_update, ALL, ctx

import config
from chart_loader import build_chart_figure, discover_charts
from mock_data import create_mock_data
from search_parser import parse_query

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


def load_startup_data():
    if config.DATA_PATH.exists():
        try:
            logger.info("Loading integrated dataset from %s", config.DATA_PATH)
            real_df = pd.read_csv(config.DATA_PATH, dtype={config.ZIP_COLUMN: "string"}, low_memory=False)
            return normalize_dataframe(real_df), False
        except Exception:
            logger.exception("Could not load the integrated CSV; using mock data.")

    logger.warning("Integrated CSV not found. The app is using mock data.")
    return normalize_dataframe(create_mock_data()), True


DATA, USING_MOCK_DATA = load_startup_data()
CHART_SPECS = discover_charts()


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
        initial_figure = build_chart_figure(chart_spec, DATA, {})
        initial_figure.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter, sans-serif", color="#0f172a"),
            margin=dict(l=10, r=10, t=20, b=10),
            # Default Plotly colors to match new vibrant theme
            colorway=["#6366f1", "#ec4899", "#14b8a6", "#f59e0b", "#8b5cf6"]
        )
        
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
                html.Div(["⚠️ Using Mock Data"] if USING_MOCK_DATA else "", id="mock-data-banner", className="mock-data-banner" if USING_MOCK_DATA else "hidden"),
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
                                dcc.Input(id="search-input", type="text", placeholder='Try searching "Brooklyn 2022 new buildings"...', debounce=False, className="search-input"),
                                html.Button("Parse Search", id="search-button", n_clicks=0, className="secondary-button"),
                                html.Div(id="search-feedback", className="search-feedback"),
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
                html.Section(
                    [
                        html.H2("Project Overview"),
                        html.Div([
                            html.H3("Research Question"), html.P("How do housing and development patterns relate to transportation activity across NYC ZIP codes and years?"),
                            html.H3("Data Integration"), html.P("The project combines one housing dataset and one transportation dataset at ZIP-code-by-year granularity."),
                        ], className="story-content"),
                    ], className="story-section",
                ),
            ], className="page-content",
        ),
        html.Footer("NYC Housing & Transportation Dashboard • Phase 1 Deliverable"),
        
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


def apply_filters(dataframe, filters):
    filtered = dataframe.copy()
    filters = filters or {}
    simple_filters = [("borough", config.BOROUGH_COLUMN), ("housing_category", config.HOUSING_CATEGORY_COLUMN), ("transportation_category", config.TRANSPORT_CATEGORY_COLUMN)]
    for filter_key, column_name in simple_filters:
        selected = filters.get(filter_key, config.ALL_VALUE)
        if column_name in filtered.columns and selected not in (None, "", config.ALL_VALUE):
            filtered = filtered[filtered[column_name].astype(str) == str(selected)]
    selected_years = filters.get("year", [config.ALL_VALUE])
    if selected_years is None: selected_years = [config.ALL_VALUE]
    if not isinstance(selected_years, list): selected_years = [selected_years]
    if config.YEAR_COLUMN in filtered.columns and selected_years and config.ALL_VALUE not in selected_years:
        numeric_years = pd.to_numeric(pd.Series(selected_years), errors="coerce").dropna()
        filtered = filtered[filtered[config.YEAR_COLUMN].isin(numeric_years.astype(int))]
    return filtered


@app.callback(
    Output("borough-filter", "value"), Output("year-filter", "value"), Output("housing-category-filter", "value"),
    Output("transportation-category-filter", "value"), Output("search-feedback", "children"),
    Input("search-button", "n_clicks"), State("search-input", "value"), prevent_initial_call=True,
)
def apply_search_query(_n_clicks, query):
    if not query or not query.strip(): return (no_update, no_update, no_update, no_update, "Enter a search query first.")
    parsed = parse_query(query)
    borough = parsed.get("borough", config.ALL_VALUE)
    years = parsed.get("year", [config.ALL_VALUE])
    if not isinstance(years, list): years = [years]
    borough_values = {option["value"] for option in dropdown_options(config.BOROUGH_COLUMN)}
    if borough not in borough_values: borough = config.ALL_VALUE
    available_years = {option["value"] for option in ([{"label": "All", "value": config.ALL_VALUE}] + [{"label": str(y), "value": y} for y in sorted(int(v) for v in DATA[config.YEAR_COLUMN].dropna().unique())])}
    years = [year for year in years if year in available_years]
    if not years: years = [config.ALL_VALUE]
    return (borough, years, parsed.get("housing_category", config.ALL_VALUE), parsed.get("transportation_category", config.ALL_VALUE), "✓ Search parsed. Click Generate Report.")


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
        fig = build_chart_figure(chart_spec, filtered_df, current_filters)
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
            font=dict(family="Inter, sans-serif", color="#0f172a"), 
            margin=dict(l=10, r=10, t=20, b=10),
            colorway=["#6366f1", "#ec4899", "#14b8a6", "#f59e0b", "#8b5cf6"]
        )
        figures.append(fig)

    if filtered_df.empty:
        return tuple(figures) + ("No results match the selected filters.", "empty-results visible", "No matching records.")
    
    summary = f"Showing {len(filtered_df):,} ZIP/year records across {filtered_df[config.ZIP_COLUMN].nunique():,} NYC ZIP codes."
    return tuple(figures) + ("", "empty-results", summary)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)