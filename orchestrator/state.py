"""Shared graph state passed between agents."""
from __future__ import annotations

from typing import Any, TypedDict


class AnalysisState(TypedDict, total=False):
    input_path: str
    file_type: str          # "csv" | "sqlite"
    schema: dict[str, Any]
    statistics: dict[str, Any]
    data_summary: str
    charts: list[dict[str, str]]   # [{"path": ..., "description": ...}]
    narrative: str
    pdf_path: str
    current_agent: str
    error: str
