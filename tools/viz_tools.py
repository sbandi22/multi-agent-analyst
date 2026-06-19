"""Charting tools for the Visualization Agent (Plotly -> PNG)."""
from __future__ import annotations

import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "outputs")


def _save(fig: go.Figure, filename: str) -> str:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, filename)
    fig.update_layout(template="plotly_white", title_x=0.5, width=900, height=520)
    fig.write_image(path, scale=2)  # requires kaleido
    return path


def create_bar_chart(df: pd.DataFrame, x: str, y: str, title: str, filename: str) -> str:
    fig = px.bar(df, x=x, y=y, title=title, color=x)
    fig.update_layout(showlegend=False)
    return _save(fig, filename)


def create_line_chart(df: pd.DataFrame, x: str, y: str, title: str, filename: str) -> str:
    plot_df = df.sort_values(x)
    fig = px.line(plot_df, x=x, y=y, title=title, markers=True)
    return _save(fig, filename)


def create_scatter_plot(
    df: pd.DataFrame, x: str, y: str, title: str, filename: str, color: str | None = None
) -> str:
    fig = px.scatter(df, x=x, y=y, color=color, title=title)
    return _save(fig, filename)


def create_heatmap(corr: pd.DataFrame, title: str, filename: str) -> str:
    fig = go.Figure(
        data=go.Heatmap(
            z=corr.values,
            x=list(corr.columns),
            y=list(corr.index),
            colorscale="RdBu",
            zmid=0,
            text=corr.round(2).values,
            texttemplate="%{text}",
        )
    )
    fig.update_layout(title=title)
    return _save(fig, filename)
