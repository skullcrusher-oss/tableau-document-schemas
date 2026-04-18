from pathlib import Path

from lxml import etree

from ..errors import SourceReadError
from .base import DataProfile, FieldProfile


def read_tds(path: Path) -> DataProfile:
    tree = etree.parse(str(path))
    root = tree.getroot()
    if root.tag != "datasource":
        raise SourceReadError(f"Expected <datasource> root in {path}, got <{root.tag}>")

    fields: list[FieldProfile] = []
    for col in root.iter("column"):
        name = col.get("name") or ""
        if not name.startswith("["):
            continue
        fields.append(
            FieldProfile(
                name=name,
                caption=col.get("caption") or name.strip("[]"),
                role=col.get("role") or "dimension",
                datatype=col.get("datatype") or "string",
                field_type=col.get("type") or "nominal",
                aggregation=col.get("aggregation") or "",
                raw_name=name.strip("[]"),
            )
        )
    if not fields:
        raise SourceReadError(f"No <column> elements found in {path}")

    return DataProfile(
        name=path.stem,
        source_type="tds",
        path=path,
        fields=fields,
        row_count=0,
    )
