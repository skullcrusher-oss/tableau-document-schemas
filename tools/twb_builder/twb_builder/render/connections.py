"""Per-class <connection> attribute builders.

The <connection> element is declared `processContents="skip"` in the XSD, so
attributes here are not XSD-validated; they must match Tableau runtime
expectations empirically.
"""
from __future__ import annotations

from ..plan.schema import DataSourceSpec


def build_connection_attrs(ds: DataSourceSpec) -> dict[str, str]:
    """Return attribute map for the <connection> element."""
    user_attrs = {k: str(v) for k, v in (ds.connection or {}).items() if v is not None}
    if "class" in user_attrs:
        return user_attrs

    if ds.type == "csv":
        defaults = {
            "class": "textscan",
            "filename": ds.path,
            "directory": ds.path,
            "server": "",
        }
    elif ds.type == "excel":
        defaults = {
            "class": "excel-direct",
            "filename": ds.path,
            "header": "yes",
        }
    elif ds.type == "hyper":
        defaults = {
            "class": "hyper",
            "dbname": ds.path,
            "schema": "public",
            "server": "",
        }
    else:  # tds
        defaults = {"class": "sqlproxy"}

    defaults.update(user_attrs)
    return defaults
