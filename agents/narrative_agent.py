"""Narrative Writer Agent: produce a 500-800 word BI report via OpenAI (with fallback)."""
from __future__ import annotations

import json
import os

from orchestrator.state import AnalysisState


def _build_prompt(state: AnalysisState) -> str:
    chart_lines = "\n".join(f"- {c['description']}" for c in state.get("charts", []))
    return (
        "You are a senior business intelligence analyst. Write a professional "
        "500-800 word report based on the data below. Use these sections with markdown "
        "headers: Executive Summary, Key Findings, Trends, Recommendations.\n\n"
        f"DATA SUMMARY:\n{state.get('data_summary', '')}\n\n"
        f"SCHEMA:\n{json.dumps(state.get('schema', {}), default=str)[:2500]}\n\n"
        f"STATISTICS:\n{json.dumps(state.get('statistics', {}), default=str)[:2500]}\n\n"
        f"CHARTS PRODUCED:\n{chart_lines}\n"
    )


def _fallback(state: AnalysisState) -> str:
    """Deterministic report so the system runs even without an API key (e.g. in tests)."""
    charts = "\n".join(f"- {c['description']}" for c in state.get("charts", []))
    return (
        "## Executive Summary\n"
        f"{state.get('data_summary', '')}\n\n"
        "## Key Findings\n"
        "Automated analysis examined the dataset structure, distributions, and "
        "relationships between numeric measures.\n\n"
        "## Trends\n"
        "Time-based and categorical aggregations were generated where applicable.\n\n"
        "## Recommendations\n"
        "Review the highlighted outliers and top-performing categories below.\n\n"
        f"### Charts\n{charts}\n"
    )


def run(state: AnalysisState) -> AnalysisState:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return {**state, "narrative": _fallback(state), "current_agent": "narrative"}

    try:
        from langchain_openai import ChatOpenAI

        model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        llm = ChatOpenAI(model=model, temperature=0.3, api_key=api_key)
        resp = llm.invoke(_build_prompt(state))
        text = resp.content if hasattr(resp, "content") else str(resp)
        return {**state, "narrative": text, "current_agent": "narrative"}
    except Exception as exc:  # network/key issues should not break the pipeline
        return {
            **state,
            "narrative": _fallback(state) + f"\n\n_(LLM unavailable: {exc})_",
            "current_agent": "narrative",
        }
