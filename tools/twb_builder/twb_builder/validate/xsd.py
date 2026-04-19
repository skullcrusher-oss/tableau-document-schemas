from __future__ import annotations

import functools
from pathlib import Path

from lxml import etree

from .. import XSD_PATH
from ..errors import ValidationError

_USER_NS_STUB = Path(__file__).parent / "user_ns.xsd"
_XML_NS_STUB = Path(__file__).parent / "xml_ns.xsd"

_NS_STUBS = {
    "http://www.tableausoftware.com/xml/user": _USER_NS_STUB,
    "http://www.w3.org/XML/1998/namespace": _XML_NS_STUB,
}


_XS = "http://www.w3.org/2001/XMLSchema"
_NS = {"xs": _XS}


@functools.lru_cache(maxsize=1)
def get_schema() -> etree.XMLSchema:
    """Load the TWB XSD, supplying local stubs for imported namespaces and
    patching a few content-model gaps where the published XSD is stricter
    than Tableau Desktop.

    The public TWB XSD imports `user` and `xml` namespaces without
    schemaLocation but references declarations from them. We patch each
    import in memory to point to a local stub so validation works offline.

    We also relax two constraints to match Tableau Desktop reality:
      * `<mark>` accepts a `type` attribute (Desktop requires it, XSD omits)
      * `<worksheet>` accepts a `<worksheet-number>` child (Desktop requires
        it, XSD's WorksheetDocPtr sequence does not list it)
    """
    tree = etree.parse(str(XSD_PATH))
    root = tree.getroot()
    for imp in root.findall("xs:import", _NS):
        stub = _NS_STUBS.get(imp.get("namespace"))
        if stub is not None:
            imp.set("schemaLocation", stub.resolve().as_uri())
    _patch_mark_allow_type(root)
    _patch_worksheet_allow_number(root)
    return etree.XMLSchema(tree)


def _patch_mark_allow_type(root: etree._Element) -> None:
    for grp in root.iter(f"{{{_XS}}}group"):
        if grp.get("name") != "PaneSpecification-Mark-G":
            continue
        for mark in grp.iter(f"{{{_XS}}}element"):
            if mark.get("name") != "mark":
                continue
            ct = mark.find(f"{{{_XS}}}complexType")
            if ct is None:
                continue
            attr = etree.SubElement(ct, f"{{{_XS}}}attribute")
            attr.set("name", "type")
            attr.set("type", "xs:string")


def _patch_worksheet_allow_number(root: etree._Element) -> None:
    for grp in root.iter(f"{{{_XS}}}group"):
        if grp.get("name") != "Workbook-WorksheetDocPtr-G":
            continue
        for ws in grp.iter(f"{{{_XS}}}element"):
            if ws.get("name") != "worksheet":
                continue
            seq = ws.find(f"{{{_XS}}}complexType/{{{_XS}}}sequence")
            if seq is None:
                continue
            extra = etree.SubElement(seq, f"{{{_XS}}}element")
            extra.set("name", "worksheet-number")
            extra.set("minOccurs", "0")
            ct = etree.SubElement(extra, f"{{{_XS}}}complexType")
            a = etree.SubElement(ct, f"{{{_XS}}}attribute")
            a.set("name", "number")
            a.set("type", "xs:int")
            a.set("use", "required")


def validate_twb(twb_bytes: bytes) -> None:
    doc = etree.fromstring(twb_bytes)
    schema = get_schema()
    if not schema.validate(doc):
        errors = "\n".join(
            f"  line {e.line}, col {e.column}: {e.message}"
            for e in schema.error_log
        )
        raise ValidationError(f"TWB failed XSD validation:\n{errors}")
