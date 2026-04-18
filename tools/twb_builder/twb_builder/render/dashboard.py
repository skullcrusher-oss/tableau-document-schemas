from __future__ import annotations

from lxml import etree

from ..plan.schema import DashboardSpec
from .xml_utils import el, new_uuid


def build_dashboard(dash: DashboardSpec) -> etree._Element:
    node = el("dashboard", name=dash.name)

    size = el(
        "size",
        **{
            "sizing-mode": dash.size.sizing_mode,
            "minwidth": dash.size.minwidth,
            "minheight": dash.size.minheight,
            "maxwidth": dash.size.maxwidth,
            "maxheight": dash.size.maxheight,
        },
    )
    node.append(size)
    node.append(el("datasources"))

    zones = el("zones")
    root_zone = el("zone", id=3, x=0, y=0, w=1000, h=1000)
    root_zone.set("type-v2", "layout-basic")
    for z in dash.zones:
        root_zone.append(
            el("zone", id=z.id, x=z.x, y=z.y, w=z.w, h=z.h, name=z.sheet)
        )
    zones.append(root_zone)
    node.append(zones)

    node.append(el("simple-id", uuid=new_uuid()))
    return node
