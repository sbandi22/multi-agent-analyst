"""Data Query Agent: load data, understand schema, extract stats/trends/anomalies."""
from __future__ import annotations

import pandas as pd

from orchestrator.state import AnalysisState
from tools import data_tools

# In-process cache so the viz agent can reuse the loaded frame without re-parsing.
_FRAME_CACHE: dict[str, pd.DataFrame] = {}


def get_frame(path: str) -> pd.DataFrame:
    return _FRAME_CACHE[path]


def run(state: AnalysisState) -> AnalysisState:
    path = state["input_path"]
    file_type = state.get("file_type", "csv")

    df = data_tools.load_sqlite(path) if file_type == "sqlite" else data_tools.load_csv(path)
    _FRAME_CACHE[path] = df

    schema = data_tools.get_schema(df)
    stats = data_tools.compute_statistics(df)

    numeric_cols = list(df.select_dtypes("number").columns)
    anomaly_note = (
        f"{len(stats['anomalies'])} column(s) contain statistical outliers."
        if stats["anomalies"]
        else "No significant outliers detected."
    )
    summary = (
        f"Dataset has {schema['row_count']} rows and {len(schema['columns'])} columns. "
        f"Numeric columns: {', '.join(numeric_cols) or 'none'}. {anomaly_note}"
    )

    return {
        **state,
        "schema": schema,
        "statistics": stats,
        "data_summary": summary,
        "current_agent": "query",
    }
