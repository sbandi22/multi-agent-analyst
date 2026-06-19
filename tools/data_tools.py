"""Data access + analysis tools for the Query Agent."""
from __future__ import annotations

import sqlite3
from typing import Any

import numpy as np
import pandas as pd


def load_csv(path: str) -> pd.DataFrame:
    """Load a CSV file into a DataFrame, parsing obvious date columns."""
    df = pd.read_csv(path)
    for col in df.columns:
        if df[col].dtype == "object":
            parsed = pd.to_datetime(df[col], errors="coerce", format="mixed")
            if parsed.notna().mean() > 0.8:
                df[col] = parsed
    return df


def load_sqlite(path: str, table: str | None = None) -> pd.DataFrame:
    """Load a table from a SQLite database. Uses the first table if none given."""
    conn = sqlite3.connect(path)
    try:
        if table is None:
            tables = pd.read_sql_query(
                "SELECT name FROM sqlite_master WHERE type='table'", conn
            )
            if tables.empty:
                raise ValueError("No tables found in SQLite database.")
            table = tables.iloc[0]["name"]
        return pd.read_sql_query(f"SELECT * FROM '{table}'", conn)
    finally:
        conn.close()


def get_schema(df: pd.DataFrame) -> dict[str, Any]:
    """Return column names, dtypes, null counts, and sample values."""
    schema: dict[str, Any] = {"row_count": int(len(df)), "columns": {}}
    for col in df.columns:
        series = df[col]
        schema["columns"][col] = {
            "dtype": str(series.dtype),
            "null_count": int(series.isna().sum()),
            "unique": int(series.nunique(dropna=True)),
            "sample": [
                None if pd.isna(v) else (v.isoformat() if hasattr(v, "isoformat") else v)
                for v in series.dropna().head(3).tolist()
            ],
        }
    return schema


def run_query(df: pd.DataFrame, expression: str) -> pd.DataFrame:
    """Run a pandas .query() expression. Returns the filtered DataFrame."""
    return df.query(expression)


def compute_statistics(df: pd.DataFrame) -> dict[str, Any]:
    """Summary stats, correlations, and simple anomaly detection (z-score > 3)."""
    numeric = df.select_dtypes(include=[np.number])
    stats: dict[str, Any] = {
        "numeric_summary": numeric.describe().round(3).to_dict() if not numeric.empty else {},
        "correlations": {},
        "anomalies": {},
    }

    if numeric.shape[1] >= 2:
        stats["correlations"] = numeric.corr(numeric_only=True).round(3).to_dict()

    for col in numeric.columns:
        series = numeric[col].dropna()
        if series.std(ddof=0) == 0 or series.empty:
            continue
        z = (series - series.mean()) / series.std(ddof=0)
        outliers = series[z.abs() > 3]
        if not outliers.empty:
            stats["anomalies"][col] = {
                "count": int(len(outliers)),
                "values": outliers.round(3).head(5).tolist(),
            }
    return stats


def top_categories(df: pd.DataFrame, group_col: str, value_col: str, n: int = 10) -> pd.DataFrame:
    """Aggregate a value column by a category column and return the top N."""
    grouped = (
        df.groupby(group_col, dropna=True)[value_col]
        .sum()
        .sort_values(ascending=False)
        .head(n)
        .reset_index()
    )
    return grouped
