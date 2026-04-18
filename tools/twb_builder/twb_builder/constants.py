"""Canonical string vocabularies and defaults for TWB generation."""

USER_NS = "http://www.tableausoftware.com/xml/user"
USER_NSMAP = {"user": USER_NS}

DEFAULT_SOURCE_BUILD = "20261.26.0211.1127"
DEFAULT_SOURCE_PLATFORM = "linux"

MARK_TYPES = {
    "Automatic", "Text", "Icon", "Shape", "Rectangle", "Bar", "GanttBar",
    "Square", "Circle", "Heatmap", "PolyLine", "Line", "Polygon", "Area",
    "Pie", "Multipolygon", "VizExtension",
}

FIELD_ROLES = {"dimension", "measure"}
FIELD_TYPES = {"nominal", "ordinal", "quantitative"}
DATATYPES = {"string", "integer", "real", "date", "datetime", "boolean", "spatial"}

AGG_TYPES = {"", "Sum", "Avg", "Count", "Countd", "Min", "Max", "Median", "Stdev", "Var"}

CONNECTION_CLASSES = {
    "csv": "textscan",
    "excel": "excel-direct",
    "hyper": "hyper",
    "tds": None,
}
