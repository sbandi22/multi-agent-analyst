import os

from orchestrator import pdf_builder


def test_build_pdf(tmp_path, monkeypatch):
    monkeypatch.setattr(pdf_builder, "OUTPUT_DIR", str(tmp_path))
    state = {
        "narrative": "## Executive Summary\nAll good.\n\n## Key Findings\n- Point one",
        "charts": [],
    }
    path = pdf_builder.build_pdf(state, filename="out.pdf")
    assert os.path.exists(path)
    assert os.path.getsize(path) > 0


def test_build_pdf_with_missing_chart(tmp_path, monkeypatch):
    monkeypatch.setattr(pdf_builder, "OUTPUT_DIR", str(tmp_path))
    state = {
        "narrative": "# Report\nBody text.",
        "charts": [{"path": "/does/not/exist.png", "description": "missing"}],
    }
    # Should not raise even when a chart file is absent.
    path = pdf_builder.build_pdf(state, filename="out2.pdf")
    assert os.path.exists(path)
