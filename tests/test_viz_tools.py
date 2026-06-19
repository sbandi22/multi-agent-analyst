import os

import pandas as pd

from tools import viz_tools


def test_create_bar_chart(tmp_path, monkeypatch):
    monkeypatch.setattr(viz_tools, "OUTPUT_DIR", str(tmp_path))
    df = pd.DataFrame({"cat": ["a", "b", "c"], "val": [3, 1, 2]})
    path = viz_tools.create_bar_chart(df, "cat", "val", "Test", "bar.png")
    assert os.path.exists(path)
    assert os.path.getsize(path) > 0


def test_create_heatmap(tmp_path, monkeypatch):
    monkeypatch.setattr(viz_tools, "OUTPUT_DIR", str(tmp_path))
    corr = pd.DataFrame({"a": [1.0, 0.5], "b": [0.5, 1.0]}, index=["a", "b"])
    path = viz_tools.create_heatmap(corr, "Corr", "heat.png")
    assert os.path.exists(path)
