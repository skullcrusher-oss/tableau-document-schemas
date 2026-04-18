from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class FieldProfile:
    name: str            # bracketed, e.g. "[sales]"
    caption: str
    role: str            # dimension | measure
    datatype: str        # string | integer | real | date | datetime | boolean | spatial
    field_type: str      # nominal | ordinal | quantitative
    aggregation: str = ""
    cardinality: int = 0
    sample_values: list[str] = field(default_factory=list)
    null_pct: float = 0.0
    raw_name: str = ""   # unescaped original column name


@dataclass
class DataProfile:
    name: str
    source_type: str     # csv | excel | hyper | tds
    path: Path
    fields: list[FieldProfile]
    row_count: int = 0
    extra: dict = field(default_factory=dict)
