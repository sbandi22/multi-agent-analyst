"""Streamlit UI: upload CSV, watch agent status live, download the PDF."""
from __future__ import annotations

import os
import sys
import tempfile

# Allow `streamlit run ui/app.py` from repo root.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from dotenv import load_dotenv

from agents import narrative_agent, query_agent, viz_agent
from orchestrator import pdf_builder

load_dotenv()

st.set_page_config(page_title="Multi-Agent Data Analyst", page_icon="*", layout="centered")
st.title("Multi-Agent Data Analyst")
st.caption("Query - Visualization - Narrative agents orchestrated with LangGraph")

uploaded = st.file_uploader("Upload a CSV or SQLite file", type=["csv", "db", "sqlite"])

if uploaded and st.button("Generate Report", type="primary"):
    suffix = os.path.splitext(uploaded.name)[1]
    file_type = "sqlite" if suffix in (".db", ".sqlite") else "csv"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded.getbuffer())
        path = tmp.name

    status = st.status("Starting pipeline...", expanded=True)
    state = {"input_path": path, "file_type": file_type}

    # Run each agent explicitly so the UI can reflect live status.
    status.update(label="Data Query Agent running...")
    state = query_agent.run(state)
    st.write("Query complete - " + state["data_summary"])

    status.update(label="Visualization Agent running...")
    state = viz_agent.run(state)
    st.write(f"{len(state['charts'])} charts generated")
    cols = st.columns(min(3, len(state["charts"])) or 1)
    for i, chart in enumerate(state["charts"]):
        cols[i % len(cols)].image(chart["path"], caption=chart["description"])

    status.update(label="Narrative Writer Agent running...")
    state = narrative_agent.run(state)
    st.markdown(state["narrative"])

    status.update(label="Assembling PDF...")
    pdf_path = pdf_builder.build_pdf(state)
    status.update(label="Done!", state="complete")

    with open(pdf_path, "rb") as f:
        st.download_button("Download PDF Report", f, file_name="bi_report.pdf", mime="application/pdf")
