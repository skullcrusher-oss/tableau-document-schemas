from __future__ import annotations

from lxml import etree

from ..constants import USER_NSMAP
from ..plan.schema import Plan
from .dashboard import build_dashboard
from .datasource import build_datasource
from .worksheet import build_worksheet
from .xml_utils import el, to_bytes


def render_twb(plan: Plan) -> bytes:
    root = etree.Element(
        "workbook",
        attrib={
            "original-version": plan.twb_version,
            "source-build": plan.source_build,
            "source-platform": plan.source_platform,
            "version": plan.twb_version,
        },
        nsmap=USER_NSMAP,
    )

    manifest = etree.SubElement(root, "document-format-change-manifest")
    etree.SubElement(manifest, "ManifestByVersion")

    # <datasources>
    datasources = etree.SubElement(root, "datasources")
    datasources.append(build_datasource(plan.datasource))

    # <worksheets>
    if plan.sheets:
        worksheets = etree.SubElement(root, "worksheets")
        for s in plan.sheets:
            worksheets.append(build_worksheet(s, plan))

    # <dashboards>
    if plan.dashboards:
        dashboards = etree.SubElement(root, "dashboards")
        for d in plan.dashboards:
            dashboards.append(build_dashboard(d))

    # <explain-data> required per XSD WorkbookFile-CT
    explain = el("explain-data")
    explain.set("enabled-for-viewer", "true")
    explain.set("extreme-values-enabled-for-all", "true")
    etree.SubElement(explain, "explanation-types")
    root.append(explain)

    return to_bytes(root)
