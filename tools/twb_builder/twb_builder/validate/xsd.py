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


@functools.lru_cache(maxsize=1)
def get_schema() -> etree.XMLSchema:
    """Load the TWB XSD, supplying local stubs for imported namespaces.

    The public TWB XSD imports `user` and `xml` namespaces without
    schemaLocation but references declarations from them. We patch each
    import in memory to point to a local stub so validation works offline.
    """
    tree = etree.parse(str(XSD_PATH))
    root = tree.getroot()
    ns = {"xs": "http://www.w3.org/2001/XMLSchema"}
    for imp in root.findall("xs:import", ns):
        stub = _NS_STUBS.get(imp.get("namespace"))
        if stub is not None:
            imp.set("schemaLocation", stub.resolve().as_uri())
    return etree.XMLSchema(tree)


def validate_twb(twb_bytes: bytes) -> None:
    doc = etree.fromstring(twb_bytes)
    schema = get_schema()
    if not schema.validate(doc):
        errors = "\n".join(
            f"  line {e.line}, col {e.column}: {e.message}"
            for e in schema.error_log
        )
        raise ValidationError(f"TWB failed XSD validation:\n{errors}")
