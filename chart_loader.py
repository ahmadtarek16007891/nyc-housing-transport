"""Discover chart modules and safely build chart figures."""
import importlib.util
import logging
from pathlib import Path
from typing import Any, Dict, List

import plotly.graph_objects as go

import config

logger = logging.getLogger(__name__)
REQUIRED_ATTRIBUTES = ("TITLE", "QUESTION", "build_figure")


def _placeholder_figure(message: str, sub_message: str = "Awaiting teammate integration") -> go.Figure:
    """Return a modern, styled empty-state figure."""
    figure = go.Figure()
    
    # Modern UI empty state styling
    figure.add_annotation(
        text=f"<b>{message}</b><br><span style='font-size:13px; color:#64748b;'>{sub_message}</span>",
        x=0.5, y=0.5,
        xref="paper", yref="paper",
        showarrow=False,
        font=dict(size=16, color="#0f172a", family="Inter, sans-serif"),
        align="center",
        bgcolor="#f8fafc",
        bordercolor="#e2e8f0",
        borderwidth=1,
        borderpad=20,
        opacity=0.8
    )
    
    figure.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        margin=dict(l=20, r=20, t=25, b=20),
    )
    return figure


def discover_charts(charts_dir: Path = config.CHARTS_DIR) -> List[Dict[str, Any]]:
    """Load chart_*.py files in numeric order; missing files become placeholders."""
    chart_specs = []
    for chart_number in range(1, 13):
        chart_id = f"chart_{chart_number:02d}"
        module_path = charts_dir / f"{chart_id}.py"
        spec = {
            "id": chart_id,
            "number": chart_number,
            "title": f"Chart {chart_number:02d}",
            "question": "Research question pending.",
            "build_figure": None,
            "available": False,
            "error": None,
        }

        if not module_path.exists():
            spec["error"] = "Chart file is missing."
            logger.warning("%s: %s", chart_id, spec["error"])
            chart_specs.append(spec)
            continue

        try:
            module_spec = importlib.util.spec_from_file_location(chart_id, module_path)
            if module_spec is None or module_spec.loader is None:
                raise ImportError("Could not create an import specification.")

            module = importlib.util.module_from_spec(module_spec)
            module_spec.loader.exec_module(module)

            missing = [name for name in REQUIRED_ATTRIBUTES if not hasattr(module, name)]
            if missing:
                raise AttributeError(f"Missing required attributes: {', '.join(missing)}")

            if not isinstance(module.TITLE, str) or not isinstance(module.QUESTION, str):
                raise TypeError("TITLE and QUESTION must both be strings.")
            if not callable(module.build_figure):
                raise TypeError("build_figure must be callable.")

            spec.update({
                "title": module.TITLE,
                "question": module.QUESTION,
                "build_figure": module.build_figure,
                "available": True,
            })
            logger.info("Loaded %s", chart_id)
        except Exception as exc:
            spec["error"] = f"{type(exc).__name__}: {exc}"
            logger.exception("Could not load %s", chart_id)

        chart_specs.append(spec)

    return chart_specs


def build_chart_figure(chart_spec: Dict[str, Any], df, filters) -> go.Figure:
    """Build one figure and turn any chart failure into a visible placeholder."""
    if not chart_spec["available"]:
        return _placeholder_figure(f"{chart_spec['id'].replace('_', ' ').title()} Unavailable")

    try:
        figure = chart_spec["build_figure"](df.copy(), filters or {})
        if not isinstance(figure, go.Figure):
            raise TypeError("build_figure must return plotly.graph_objects.Figure.")
        return figure
    except Exception as exc:
        logger.exception("Error while building %s", chart_spec["id"])
        return _placeholder_figure(
            f"Error Rendering {chart_spec['id'].replace('_', ' ').title()}", 
            sub_message="Check terminal logs for traceback"
        )