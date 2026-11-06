"""Chart 02: Yearly Trend of Units and Crashes."""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import config

TITLE = "Yearly Trend Analysis"
QUESTION = "Do crashes rise or fall in years when more affordable units are completed?"

def build_figure(df, filters):
    """Q2: City totals with units as bars and crashes as a line on a second axis."""
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data for the selected filters", showarrow=False)
        return fig

    year_col = config.YEAR_COLUMN
    units_col = config.HOUSING_METRIC_1_COLUMN
    crashes_col = config.TRANSPORT_METRIC_1_COLUMN

    if not all(c in df.columns for c in [year_col, units_col, crashes_col]):
        fig = go.Figure()
        fig.add_annotation(text="Data schema mismatch.", showarrow=False)
        return fig

    d = df.groupby(year_col, as_index=False).agg(
        total_units=(units_col, 'sum'),
        crash_count=(crashes_col, 'sum')
    )
    
    fig = make_subplots(specs=[[{'secondary_y': True}]])
    
    fig.add_bar(
        x=d[year_col], y=d['total_units'], 
        name='Affordable units completed', 
        secondary_y=False,
        marker_color="#4f46e5"
    )
    fig.add_scatter(
        x=d[year_col], y=d['crash_count'], 
        name='SIRTA crashes', 
        mode='lines+markers',
        secondary_y=True,
        line=dict(color="#e11d48", width=3)
    )
    
    fig.update_layout(
        hovermode='x unified',
        margin=dict(t=10, b=10, l=10, r=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig.update_yaxes(title_text='Total Units', secondary_y=False)
    fig.update_yaxes(title_text='Crash Count', secondary_y=True)
    
    return fig