from __future__ import annotations

from lxml import etree

from ..plan.schema import DataSourceSpec, FieldSpec
from .. import TWB_VERSION
from .connections import build_connection_attrs
from .xml_utils import el


def build_datasource(ds: DataSourceSpec) -> etree._Element:
    node = el(
        "datasource",
        name=ds.name,
        caption=ds.caption or ds.name,
        inline="true",
        version=TWB_VERSION,
    )

    conn_attrs = build_connection_attrs(ds)
    conn = el("connection", **conn_attrs)
    node.append(conn)

    for f in ds.fields:
        node.append(_build_column(f))

    return node


def _build_column(f: FieldSpec) -> etree._Element:
    attrs = {
        "name": f.name,
        "caption": f.caption or f.name.strip("[]"),
        "role": f.role,
        "type": f.type,
        "datatype": f.datatype,
    }
    if f.role == "measure" and f.aggregation:
        attrs["aggregation"] = f.aggregation
    return el("column", **attrs)
