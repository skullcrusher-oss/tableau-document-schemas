from pathlib import Path

import pandas as pd

from .base import DataProfile
from .inference import profile_series


def read_csv(path: Path) -> DataProfile:
    sample = pd.read_csv(path, nrows=10_000)
    row_count = sum(1 for _ in open(path, "rb")) - 1  # subtract header
    fields = [profile_series(col, sample[col]) for col in sample.columns]
    return DataProfile(
        name=path.stem,
        source_type="csv",
        path=path,
        fields=fields,
        row_count=max(row_count, 0),
    )
