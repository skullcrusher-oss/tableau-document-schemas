"""Rules for turning a DataProfile into a starter Plan."""
from __future__ import annotations

from pathlib import Path

from .. import TWB_VERSION
from ..constants import DEFAULT_SOURCE_BUILD, DEFAULT_SOURCE_PLATFORM
from ..datasource.base import DataProfile, FieldProfile
from .layout import default_layout
from .schema import (
    DashboardSize,
    DashboardSpec,
    DataSourceSpec,
    EncodingSpec,
    FieldSpec,
    Plan,
    SheetSpec,
    SortSpec,
)


def build_heuristic_plan(profile: DataProfile) -> Plan:
    fields = profile.fields
    dates = [f for f in fields if f.datatype in {"date", "datetime"}]
    measures = [f for f in fields if f.role == "measure"]
    dims = [f for f in fields if f.role == "dimension" and f not in dates]
    low_card_dims = [d for d in dims if 2 <= d.cardinality <= 25]

    sheets: list[SheetSpec] = []

    # 1) KPI big number
    if measures:
        m0 = measures[0]
        sheets.append(SheetSpec(
            name=f"Total {m0.caption}"[:60],
            mark="Text",
            rows=[f"SUM({m0.name})"],
            cols=[],
        ))

    # 2) Bar per low-card dim x first measure
    if measures and low_card_dims:
        m0 = measures[0]
        for d in low_card_dims[:3]:
            sheets.append(SheetSpec(
                name=f"{m0.caption} by {d.caption}"[:60],
                mark="Bar",
                cols=[d.name],
                rows=[f"SUM({m0.name})"],
                encodings=EncodingSpec(color=d.name),
                sort=SortSpec(field=d.name, direction="descending", by=f"SUM({m0.name})"),
            ))

    # 3) Line over time
    if measures and dates:
        m0 = measures[0]
        dt = dates[0]
        sheets.append(SheetSpec(
            name=f"{m0.caption} over Time"[:60],
            mark="Line",
            cols=[f"YEAR({dt.name})", f"MONTH({dt.name})"],
            rows=[f"SUM({m0.name})"],
        ))

    # 4) Scatter with two measures
    if len(measures) >= 2:
        m1, m2 = measures[0], measures[1]
        color = low_card_dims[0].name if low_card_dims else None
        sheets.append(SheetSpec(
            name=f"{m2.caption} vs {m1.caption}"[:60],
            mark="Circle",
            cols=[f"SUM({m1.name})"],
            rows=[f"SUM({m2.name})"],
            encodings=EncodingSpec(color=color),
        ))

    # 5) Heatmap across two low-card dims
    if measures and len(low_card_dims) >= 2:
        m0 = measures[0]
        d1, d2 = low_card_dims[0], low_card_dims[1]
        sheets.append(SheetSpec(
            name=f"{m0.caption}: {d1.caption} x {d2.caption}"[:60],
            mark="Square",
            cols=[d1.name],
            rows=[d2.name],
            encodings=EncodingSpec(color=f"SUM({m0.name})"),
        ))

    # Fallback: a single table-like sheet if nothing produced
    if not sheets:
        first_dim = dims[0] if dims else (fields[0] if fields else None)
        if first_dim:
            sheets.append(SheetSpec(
                name="Overview",
                mark="Text",
                rows=[],
                cols=[first_dim.name],
            ))

    sheets = sheets[:6]
    _dedupe_names(sheets)

    dash = DashboardSpec(
        name="Overview",
        size=DashboardSize(),
        zones=default_layout([s.name for s in sheets]),
    )

    return Plan(
        version=1,
        twb_version=TWB_VERSION,
        source_build=DEFAULT_SOURCE_BUILD,
        source_platform=DEFAULT_SOURCE_PLATFORM,
        datasource=_build_datasource_spec(profile),
        sheets=sheets,
        dashboards=[dash],
    )


def _dedupe_names(sheets: list[SheetSpec]) -> None:
    seen: dict[str, int] = {}
    for s in sheets:
        if s.name not in seen:
            seen[s.name] = 1
        else:
            seen[s.name] += 1
            s.name = f"{s.name} ({seen[s.name]})"


def _build_datasource_spec(profile: DataProfile) -> DataSourceSpec:
    path_str = str(profile.path)
    directory = str(Path(path_str).resolve().parent)
    abspath = str(Path(path_str).resolve())

    if profile.source_type == "csv":
        connection = {
            "class": "textscan",
            "filename": abspath,
            "directory": directory,
            "server": "",
        }
    elif profile.source_type == "excel":
        connection = {
            "class": "excel-direct",
            "filename": abspath,
            "sheet": profile.extra.get("sheet", ""),
        }
    elif profile.source_type == "hyper":
        connection = {
            "class": "hyper",
            "dbname": abspath,
            "schema": profile.extra.get("schema", "public"),
            "server": "",
        }
    else:  # tds
        connection = {}

    return DataSourceSpec(
        name=profile.name,
        caption=f"{profile.name} ({profile.source_type})",
        type=profile.source_type,
        path=path_str,
        connection=connection,
        fields=[_field_to_spec(f) for f in profile.fields],
    )


def _field_to_spec(f: FieldProfile) -> FieldSpec:
    return FieldSpec(
        name=f.name,
        caption=f.caption,
        role=f.role,
        datatype=f.datatype,
        type=f.field_type,
        aggregation=f.aggregation,
    )
