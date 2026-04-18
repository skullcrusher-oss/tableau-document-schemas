from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def sales_df() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    n = 100
    return pd.DataFrame({
        "order_date": pd.date_range("2025-01-01", periods=n, freq="D"),
        "region": rng.choice(["West", "East", "South", "North"], n),
        "product": rng.choice(["A", "B", "C"], n),
        "sales": rng.uniform(10, 1000, n).round(2),
        "profit": rng.uniform(-50, 500, n).round(2),
    })


@pytest.fixture
def sales_csv(tmp_path: Path, sales_df: pd.DataFrame) -> Path:
    p = tmp_path / "sales.csv"
    sales_df.to_csv(p, index=False)
    return p


@pytest.fixture
def sales_xlsx(tmp_path: Path, sales_df: pd.DataFrame) -> Path:
    p = tmp_path / "sales.xlsx"
    sales_df.to_excel(p, index=False, engine="openpyxl")
    return p
