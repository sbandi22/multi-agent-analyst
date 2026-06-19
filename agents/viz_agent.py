"""Visualization Agent: turn query results into 3-5 Plotly charts saved as PNG."""
from __future__ import annotations

import pandas as pd

from agents.query_agent import get_frame
from orchestrator.state import AnalysisState
from tools import data_tools, viz_tools


def _pick_columns(df: pd.DataFrame):
    numeric = list(df.select_dtypes("number").columns)
    categorical = [
        c for c in df.columns
        if df[c].dtype == "object" and 1 < df[c].nunique() <= 30
    ]
    datetime = list(df.select_dtypes("datetime").columns)
    return numeric, categorical, datetime


def run(state: AnalysisState) -> AnalysisState:
    df = get_frame(state["input_path"])
    numeric, categorical, datetime = _pick_columns(df)
    charts: list[dict[str, str]] = []

    # 1. Bar: top categories by first numeric measure.
    if categorical and numeric:
        cat, val = categorical[0], numeric[0]
        top = data_tools.top_categories(df, cat, val, n=10)
        path = viz_tools.create_bar_chart(
            top, x=cat, y=val, title=f"Top {cat} by {val}", filename="01_bar.png"
        )
        charts.append({"path": path, "description": f"Top {cat} ranked by total {val}."})

    # 2. Line: trend over time.
    if datetime and numeric:
        dt, val = datetime[0], numeric[0]
        trend = df.groupby(df[dt].dt.to_period("M").dt.to_timestamp())[val].sum().reset_index()
        path = viz_tools.create_line_chart(
            trend, x=dt, y=val, title=f"{val} over time", filename="02_line.png"
        )
        charts.append({"path": path, "description": f"Monthly trend of {val} over {dt}."})

    # 3. Scatter: relationship between two numeric measures.
    if len(numeric) >= 2:
        color = categorical[0] if categorical else None
        path = viz_tools.create_scatter_plot(
            df, x=numeric[0], y=numeric[1],
            title=f"{numeric[0]} vs {numeric[1]}", filename="03_scatter.png", color=color,
        )
        charts.append({"path": path, "description": f"Relationship between {numeric[0]} and {numeric[1]}."})

    # 4. Heatmap: numeric correlations.
    if len(numeric) >= 2:
        corr = df[numeric].corr(numeric_only=True)
        path = viz_tools.create_heatmap(corr, title="Correlation heatmap", filename="04_heatmap.png")
        charts.append({"path": path, "description": "Correlation matrix of numeric features."})

    # 5. Secondary bar for a different measure (keeps us in the 3-5 range).
    if categorical and len(numeric) >= 2:
        cat, val = categorical[0], numeric[1]
        top = data_tools.top_categories(df, cat, val, n=10)
        path = viz_tools.create_bar_chart(
            top, x=cat, y=val, title=f"Top {cat} by {val}", filename="05_bar2.png"
        )
        charts.append({"path": path, "description": f"Top {cat} ranked by total {val}."})

    return {**state, "charts": charts[:5], "current_agent": "visualization"}
