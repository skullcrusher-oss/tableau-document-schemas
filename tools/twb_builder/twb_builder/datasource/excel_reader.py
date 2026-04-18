from pathlib import Path

import pandas as pd

from .base import DataProfile
from .inference import profile_series


def read_excel(path: Path, *, sheet: str | None = None) -> DataProfile:
    sheets = pd.read_excel(path, sheet_name=None, engine="openpyxl")
    if not sheets:
        raise ValueError(f"No sheets found in {path}")
    chosen = sheet if sheet in sheets else next(iter(sheets))
    df = sheets[chosen]
    fields = [profile_series(col, df[col]) for col in df.columns]
    return DataProfile(
        name=path.stem,
        source_type="excel",
        path=path,
        fields=fields,
        row_count=len(df),
        extra={"sheet": chosen},
    )
