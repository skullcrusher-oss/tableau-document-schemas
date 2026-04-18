from __future__ import annotations

import re

from lxml import etree

from ..plan.schema import DataSourceSpec, FieldSpec, Plan, SheetSpec
from .xml_utils import el, new_uuid


_FIELD_RE = re.compile(r"\[[^\[\]]+\]")
_AGG_RE = re.compile(r"^(SUM|AVG|COUNT|COUNTD|MIN|MAX|MEDIAN|STDEV|VAR)\((\[[^\[\]]+\])\)$", re.I)
_DATE_RE = re.compile(r"^(YEAR|QUARTER|MONTH|WEEK|DAY|HOUR|MINUTE|SECOND)\((\[[^\[\]]+\])\)$", re.I)


def build_worksheet(sheet: SheetSpec, plan: Plan) -> etree._Element:
    ws = el("worksheet", name=sheet.name)
    ws.append(_build_table(sheet, plan))
    ws.append(el("simple-id", uuid=new_uuid()))
    return ws


def _build_table(sheet: SheetSpec, plan: Plan) -> etree._Element:
    ds = plan.datasource
    table = el("table")
    table.append(_build_view(sheet, ds))
    table.append(etree.Element("style"))
    table.append(_build_panes(sheet, ds))
    table.append(_build_rows(sheet))
    table.append(_build_cols(sheet))
    return table


def _build_view(sheet: SheetSpec, ds: DataSourceSpec) -> etree._Element:
    view = el("view")
    datasources = el("datasources")
    datasources.append(el("datasource", name=ds.name, caption=ds.caption or ds.name))
    view.append(datasources)

    deps = el("datasource-dependencies", datasource=ds.name)
    referenced = _referenced_field_names(sheet)
    ds_field_map = {f.name: f for f in ds.fields}
    for fname in sorted(referenced):
        f = ds_field_map.get(fname)
        if f is None:
            continue
        deps.append(_dep_column(f))
    view.append(deps)

    view.append(el("aggregation", value="true"))
    return view


def _dep_column(f: FieldSpec) -> etree._Element:
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


def _build_panes(sheet: SheetSpec, ds: DataSourceSpec) -> etree._Element:
    panes = el("panes")
    pane = el("pane")
    inner_view = el("view")
    inner_view.append(el("breakdown", value="auto"))
    pane.append(inner_view)
    pane.append(el("mark", **{"class": sheet.mark}))

    enc = sheet.encodings
    if any([enc.color, enc.size, enc.text, enc.tooltip]):
        encs = el("encodings")
        if enc.color:
            encs.append(el("color", column=_ref_token(enc.color, ds)))
        if enc.size:
            encs.append(el("size", column=_ref_token(enc.size, ds)))
        if enc.text:
            encs.append(el("text", column=_ref_token(enc.text, ds)))
        pane.append(encs)

    panes.append(pane)
    return panes


def _build_rows(sheet: SheetSpec) -> etree._Element:
    e = etree.Element("rows")
    e.text = " ".join(_shelf_expr(x, sheet) for x in sheet.rows)
    return e


def _build_cols(sheet: SheetSpec) -> etree._Element:
    e = etree.Element("cols")
    e.text = " ".join(_shelf_expr(x, sheet) for x in sheet.cols)
    return e


def _shelf_expr(expr: str, sheet: SheetSpec) -> str:
    """Return the raw expression; Tableau accepts these exact strings in rows/cols."""
    return expr


def _ref_token(expr: str, ds: DataSourceSpec) -> str:
    """Fallback: just return the bracketed field name or the first field ref within."""
    m = _FIELD_RE.search(expr)
    return m.group(0) if m else expr


def _referenced_field_names(sheet: SheetSpec) -> set[str]:
    names: set[str] = set()
    for expr in (*sheet.cols, *sheet.rows, *sheet.filters):
        names |= set(_FIELD_RE.findall(expr))
    enc = sheet.encodings
    for s in (enc.color, enc.size, enc.text):
        if s:
            names |= set(_FIELD_RE.findall(s))
    for t in enc.tooltip:
        names |= set(_FIELD_RE.findall(t))
    return names
