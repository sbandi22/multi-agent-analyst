"""LangGraph supervisor: routes Query -> Visualization -> Narrative -> PDF."""
from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from agents import narrative_agent, query_agent, viz_agent
from orchestrator import pdf_builder
from orchestrator.state import AnalysisState


def _pdf_node(state: AnalysisState) -> AnalysisState:
    pdf_path = pdf_builder.build_pdf(state)
    return {**state, "pdf_path": pdf_path, "current_agent": "done"}


def build_graph():
    g = StateGraph(AnalysisState)
    g.add_node("query", query_agent.run)
    g.add_node("visualization", viz_agent.run)
    g.add_node("narrative", narrative_agent.run)
    g.add_node("assemble_pdf", _pdf_node)

    # Supervisor enforces a fixed, validated sequence.
    g.add_edge(START, "query")
    g.add_edge("query", "visualization")
    g.add_edge("visualization", "narrative")
    g.add_edge("narrative", "assemble_pdf")
    g.add_edge("assemble_pdf", END)
    return g.compile()


def run_pipeline(input_path: str, file_type: str = "csv") -> AnalysisState:
    graph = build_graph()
    return graph.invoke({"input_path": input_path, "file_type": file_type})
