"""Focused contract tests for Member 6's chart modules."""

import importlib.util
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

CHARTS_DIR = Path(__file__).resolve().parents[1] / "charts"


def load_chart(number: int):
    path = CHARTS_DIR / f"chart_{number:02d}.py"
    spec = importlib.util.spec_from_file_location(f"chart_{number:02d}", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sample_integrated_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "borough": ["Bronx", "Brooklyn", "Queens", "Brooklyn"],
            "year": [2022, 2022, 2023, 2024],
            "housing_category": [
                "New Construction", "Preservation", "No completions", "New Construction"
            ],
            "buildings_completed": [3, 2, 0, 5],
            "projects_completed": [2, 2, 0, 4],
            "total_units": [100, 60, 0, 180],
            "new_construction_units": [100, 0, 0, 180],
            "preservation_units": [0, 60, 0, 0],
            "deeply_affordable_units": [20, 15, 0, 30],
            "low_income_units": [40, 25, 0, 80],
            "units_started": [120, 30, 50, 210],
            "crash_count": [12, 8, 5, 15],
            "fatal_crashes": [1, 0, 1, 2],
            "fatalities": [1, 0, 1, 2],
            "severe_injuries": [13, 8, 5, 16],
            "non_severe_injuries": [2, 1, 0, 3],
            "transport_category": [
                "Fatal crash recorded", "Serious injuries only",
                "Fatal crash recorded", "Fatal crash recorded"
            ],
        }
    )


def test_chart_11_contract_and_heatmap():
    module = load_chart(11)
    frame = sample_integrated_data()
    figure = module.make_chart_11(frame)
    assert isinstance(figure, go.Figure)
    assert len(figure.data) == 1
    assert figure.data[0].type == "heatmap"
    assert callable(module.build_figure)
    assert isinstance(module.build_figure(frame, {}), go.Figure)
    assert isinstance(module.TITLE, str) and isinstance(module.QUESTION, str)


def test_chart_11_empty_dataframe_fallback():
    module = load_chart(11)
    figure = module.make_chart_11(pd.DataFrame())
    assert isinstance(figure, go.Figure)
    assert len(figure.layout.annotations) == 1


def test_chart_12_contract_and_treemap():
    module = load_chart(12)
    frame = sample_integrated_data()
    figure = module.make_chart_12(frame)
    assert isinstance(figure, go.Figure)
    assert len(figure.data) == 1
    assert figure.data[0].type == "treemap"
    assert callable(module.build_figure)
    assert isinstance(module.build_figure(frame, {}), go.Figure)
    assert isinstance(module.TITLE, str) and isinstance(module.QUESTION, str)


def test_chart_12_empty_and_no_crash_fallbacks():
    module = load_chart(12)
    empty_figure = module.make_chart_12(pd.DataFrame())
    no_crashes = sample_integrated_data().assign(crash_count=0)
    no_crashes_figure = module.make_chart_12(no_crashes)
    assert isinstance(empty_figure, go.Figure)
    assert isinstance(no_crashes_figure, go.Figure)
    assert len(empty_figure.layout.annotations) == 1
    assert len(no_crashes_figure.layout.annotations) == 1
