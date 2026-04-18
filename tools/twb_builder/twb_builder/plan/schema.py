from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ..constants import (
    AGG_TYPES,
    DATATYPES,
    DEFAULT_SOURCE_BUILD,
    DEFAULT_SOURCE_PLATFORM,
    FIELD_ROLES,
    FIELD_TYPES,
    MARK_TYPES,
)
from .. import TWB_VERSION


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class FieldSpec(_Strict):
    name: str  # bracketed, e.g. "[sales]"
    caption: Optional[str] = None
    role: Literal["dimension", "measure"] = "dimension"
    datatype: str = "string"
    type: str = "nominal"
    aggregation: str = ""

    @field_validator("datatype")
    @classmethod
    def _dt(cls, v: str) -> str:
        if v not in DATATYPES:
            raise ValueError(f"datatype must be one of {sorted(DATATYPES)}, got {v!r}")
        return v

    @field_validator("type")
    @classmethod
    def _ft(cls, v: str) -> str:
        if v not in FIELD_TYPES:
            raise ValueError(f"type must be one of {sorted(FIELD_TYPES)}, got {v!r}")
        return v

    @field_validator("aggregation")
    @classmethod
    def _agg(cls, v: str) -> str:
        if v not in AGG_TYPES:
            raise ValueError(f"aggregation must be one of {sorted(AGG_TYPES)}, got {v!r}")
        return v


class DataSourceSpec(_Strict):
    name: str
    caption: Optional[str] = None
    type: Literal["csv", "excel", "hyper", "tds"]
    path: str
    connection: dict = Field(default_factory=dict)
    fields: list[FieldSpec]


class EncodingSpec(_Strict):
    color: Optional[str] = None
    size: Optional[str] = None
    text: Optional[str] = None
    tooltip: list[str] = Field(default_factory=list)


class SortSpec(_Strict):
    field: str
    direction: Literal["ascending", "descending"] = "descending"
    by: Optional[str] = None


class SheetSpec(_Strict):
    name: str
    mark: str = "Automatic"
    cols: list[str] = Field(default_factory=list)
    rows: list[str] = Field(default_factory=list)
    encodings: EncodingSpec = Field(default_factory=EncodingSpec)
    filters: list[str] = Field(default_factory=list)
    sort: Optional[SortSpec] = None

    @field_validator("mark")
    @classmethod
    def _m(cls, v: str) -> str:
        if v not in MARK_TYPES:
            raise ValueError(f"mark must be one of {sorted(MARK_TYPES)}, got {v!r}")
        return v


class ZoneSpec(_Strict):
    id: int
    x: int
    y: int
    w: int
    h: int
    sheet: str


class DashboardSize(_Strict):
    sizing_mode: str = "automatic"
    minwidth: int = 800
    minheight: int = 600
    maxwidth: int = 1600
    maxheight: int = 1200


class DashboardSpec(_Strict):
    name: str
    size: DashboardSize = Field(default_factory=DashboardSize)
    zones: list[ZoneSpec]


class Plan(_Strict):
    version: int = 1
    twb_version: str = TWB_VERSION
    source_build: str = DEFAULT_SOURCE_BUILD
    source_platform: str = DEFAULT_SOURCE_PLATFORM
    datasource: DataSourceSpec
    sheets: list[SheetSpec]
    dashboards: list[DashboardSpec]

    def referenced_fields(self) -> set[str]:
        """All bracketed field names referenced anywhere in sheets."""
        names: set[str] = set()
        for s in self.sheets:
            for expr in (*s.cols, *s.rows, *s.filters):
                names |= _extract_field_names(expr)
            for enc in (s.encodings.color, s.encodings.size, s.encodings.text):
                if enc:
                    names |= _extract_field_names(enc)
            for t in s.encodings.tooltip:
                names |= _extract_field_names(t)
        return names


def _extract_field_names(expr: str) -> set[str]:
    import re
    return set(re.findall(r"\[[^\[\]]+\]", expr))
