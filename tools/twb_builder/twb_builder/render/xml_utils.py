from __future__ import annotations

import re
import uuid as _uuid

from lxml import etree

_BRACKETED = re.compile(r"^\[.+\]$")


def new_uuid() -> str:
    return f"{{{_uuid.uuid4()}}}"


def unbracket(name: str) -> str:
    if _BRACKETED.match(name):
        return name[1:-1].replace("]]", "]")
    return name


def ensure_bracketed(name: str) -> str:
    if _BRACKETED.match(name):
        return name
    return f"[{name.replace(']', ']]')}]"


def el(tag: str, **attrs) -> etree._Element:
    attrs = {k.replace("_", "-"): str(v) for k, v in attrs.items() if v is not None}
    return etree.Element(tag, attrib=attrs)


def to_bytes(root: etree._Element) -> bytes:
    return etree.tostring(
        root,
        xml_declaration=True,
        encoding="utf-8",
        pretty_print=True,
        standalone=False,
    )


AGG_PREFIX = {
    "Sum": "sum",
    "Avg": "avg",
    "Count": "ctn",
    "Countd": "ctd",
    "Min": "min",
    "Max": "max",
    "Median": "med",
    "Stdev": "stdev",
    "Var": "var",
    "": "none",
}


def derivation_suffix(aggregation: str, datatype: str) -> str:
    prefix = AGG_PREFIX.get(aggregation, "none")
    kind = "qk" if datatype in {"real", "integer"} and aggregation else "nk"
    return f"{prefix}:{kind}"
