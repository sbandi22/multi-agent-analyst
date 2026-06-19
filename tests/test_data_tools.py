import pandas as pd
import pytest

from tools import data_tools


@pytest.fixture
def df():
    return pd.DataFrame(
        {
            "region": ["N", "S", "N", "S", "N"],
            "sales": [100, 200, 150, 9999, 120],  # 9999 is an outlier
            "units": [1, 2, 3, 4, 5],
        }
    )


def test_get_schema(df):
    schema = data_tools.get_schema(df)
    assert schema["row_count"] == 5
    assert set(schema["columns"]) == {"region", "sales", "units"}
    assert schema["columns"]["region"]["unique"] == 2


def test_compute_statistics_detects_anomaly():
    big = pd.DataFrame({"x": [1, 1, 1, 1, 1, 1, 1, 1, 1, 100]})
    stats = data_tools.compute_statistics(big)
    assert "x" in stats["anomalies"]
    assert stats["anomalies"]["x"]["count"] >= 1


def test_top_categories(df):
    top = data_tools.top_categories(df, "region", "sales", n=2)
    assert list(top.columns) == ["region", "sales"]
    assert top.iloc[0]["sales"] >= top.iloc[1]["sales"]
