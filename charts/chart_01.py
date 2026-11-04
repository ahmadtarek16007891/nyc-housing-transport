"""Member 1 charts. Input: integrated_zip_year.csv as a DataFrame.
Expected columns (adjust names to Member 3's data dictionary):
  postcode, year, borough, total_units (affordable units completed that ZIP-year),
  crash_count (SIRTA crashes in that ZIP-year), crashes_per_1000_units (optional)
"""
import numpy as np
import plotly.express as px


def chart_01_units_vs_crashes(df):
    """Q1: Do ZIPs that completed more affordable units also have more serious crashes?
    Scatter, one dot per ZIP, summed over the filtered years, log axes."""
    d = (df.groupby(['postcode', 'borough'], as_index=False)
           .agg(total_units=('total_units', 'sum'), crash_count=('crash_count', 'sum')))
    d = d[(d['total_units'] > 0) & (d['crash_count'] > 0)]
    if d.empty:
        return px.scatter(title='No data for the selected filters')
    fig = px.scatter(d, x='total_units', y='crash_count', color='borough',
                     hover_name='postcode', log_x=True, log_y=True, trendline='ols',
                     trendline_scope='overall', trendline_color_override='black',
                     labels={'total_units': 'Affordable units completed (log)',
                             'crash_count': 'SIRTA crashes (log)'},
                     title='Affordable housing completed vs serious crashes, by ZIP')
    return fig


def chart_02_yearly_trend(df):
    """Q2: Do crashes rise or fall in years when more affordable units are completed?
    Two lines (indexed to 100 at first year) per borough would be busy, so use city totals
    with units as bars and crashes as a line on a second axis."""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    d = df.groupby('year', as_index=False).agg(total_units=('total_units', 'sum'),
                                               crash_count=('crash_count', 'sum'))
    fig = make_subplots(specs=[[{'secondary_y': True}]])
    fig.add_bar(x=d['year'], y=d['total_units'], name='Affordable units completed', secondary_y=False)
    fig.add_scatter(x=d['year'], y=d['crash_count'], name='SIRTA crashes', mode='lines+markers',
                    secondary_y=True)
    fig.update_layout(title='Affordable units completed and crashes per year', hovermode='x unified')
    fig.update_yaxes(title_text='Units', secondary_y=False)
    fig.update_yaxes(title_text='Crashes', secondary_y=True)
    return fig
