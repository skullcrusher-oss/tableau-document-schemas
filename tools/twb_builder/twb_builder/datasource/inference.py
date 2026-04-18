"""pandas dtype + sample heuristics -> Tableau role/datatype/aggregation."""
from __future__ import annotations

import re

import pandas as pd

from .base import FieldProfile

_ID_RE = re.compile(r"(^|_)(id|code|key|year|month|quarter|day)$", re.I)


def _tableau_name(raw: str) -> str:
    escaped = raw.replace("]", "]]")
    return f"[{escaped}]"


def _caption(raw: str) -> str:
    return raw.replace("_", " ").strip().title()


def profile_series(raw_name: str, series: pd.Series) -> FieldProfile:
    s = series
    non_null = s.dropna()
    card = int(non_null.nunique()) if len(non_null) else 0
    n = len(s)
    null_pct = float(1 - len(non_null) / n) if n else 0.0
    samples = [str(v) for v in non_null.unique()[:5]]

    datatype, role, field_type, aggregation = _infer(raw_name, s, card)

    return FieldProfile(
        name=_tableau_name(raw_name),
        caption=_caption(raw_name),
        role=role,
        datatype=datatype,
        field_type=field_type,
        aggregation=aggregation,
        cardinality=card,
        sample_values=samples,
        null_pct=round(null_pct, 4),
        raw_name=raw_name,
    )


def _infer(raw_name: str, s: pd.Series, card: int) -> tuple[str, str, str, str]:
    dtype = s.dtype

    if pd.api.types.is_bool_dtype(dtype):
        return "boolean", "dimension", "nominal", ""

    if pd.api.types.is_datetime64_any_dtype(dtype):
        has_time = bool((s.dropna().dt.time != pd.Timestamp("1970-01-01").time()).any()) if len(s.dropna()) else False
        return ("datetime" if has_time else "date"), "dimension", "ordinal", ""

    if pd.api.types.is_integer_dtype(dtype):
        if card and card < 20 or _ID_RE.search(raw_name or ""):
            return "integer", "dimension", "ordinal", ""
        return "integer", "measure", "quantitative", "Sum"

    if pd.api.types.is_float_dtype(dtype):
        return "real", "measure", "quantitative", "Sum"

    if pd.api.types.is_object_dtype(dtype) or pd.api.types.is_string_dtype(dtype):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            parsed = pd.to_datetime(
                s.dropna().head(500), errors="coerce", utc=False, format="mixed"
            )
        if len(parsed) and parsed.notna().mean() > 0.8:
            return "date", "dimension", "ordinal", ""
        return "string", "dimension", "nominal", ""

    return "string", "dimension", "nominal", ""
