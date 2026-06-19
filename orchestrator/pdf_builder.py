"""Assemble narrative + embedded charts into a PDF using ReportLab."""
from __future__ import annotations

import os
import re
from datetime import datetime

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer

from orchestrator.state import AnalysisState

OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "outputs")


def _styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("H1c", parent=styles["Heading1"], fontSize=18, spaceAfter=10))
    styles.add(ParagraphStyle("H2c", parent=styles["Heading2"], fontSize=14, spaceBefore=10))
    styles.add(ParagraphStyle("Bodyc", parent=styles["BodyText"], fontSize=10.5, leading=15))
    return styles


def _markdown_to_flowables(text: str, styles):
    flow = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            flow.append(Spacer(1, 6))
        elif line.startswith("### "):
            flow.append(Paragraph(line[4:], styles["H2c"]))
        elif line.startswith("## "):
            flow.append(Paragraph(line[3:], styles["H2c"]))
        elif line.startswith("# "):
            flow.append(Paragraph(line[2:], styles["H1c"]))
        else:
            line = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", line)
            line = re.sub(r"^[-*]\s+", "&bull; ", line)
            flow.append(Paragraph(line, styles["Bodyc"]))
    return flow


def build_pdf(state: AnalysisState, filename: str = "bi_report.pdf") -> str:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, filename)
    styles = _styles()

    doc = SimpleDocTemplate(path, pagesize=LETTER, title="BI Report")
    story = [
        Paragraph("Business Intelligence Report", styles["H1c"]),
        Paragraph(f"Generated {datetime.now():%Y-%m-%d %H:%M}", styles["Bodyc"]),
        Spacer(1, 12),
    ]
    story += _markdown_to_flowables(state.get("narrative", ""), styles)

    if state.get("charts"):
        story.append(Spacer(1, 16))
        story.append(Paragraph("Visualizations", styles["H2c"]))
        for chart in state["charts"]:
            if os.path.exists(chart["path"]):
                story.append(Spacer(1, 8))
                story.append(Image(chart["path"], width=6.2 * inch, height=3.6 * inch))
                story.append(Paragraph(chart["description"], styles["Bodyc"]))

    doc.build(story)
    return path
