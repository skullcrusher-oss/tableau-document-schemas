"""Default dashboard layouts as 1000x1000 grid zones."""
from __future__ import annotations

from .schema import ZoneSpec


def default_layout(sheet_names: list[str]) -> list[ZoneSpec]:
    n = len(sheet_names)
    if n == 0:
        return []
    if n == 1:
        return [ZoneSpec(id=4, x=0, y=0, w=1000, h=1000, sheet=sheet_names[0])]
    if n == 2:
        return [
            ZoneSpec(id=4, x=0,   y=0, w=500, h=1000, sheet=sheet_names[0]),
            ZoneSpec(id=5, x=500, y=0, w=500, h=1000, sheet=sheet_names[1]),
        ]
    if n == 3:
        return [
            ZoneSpec(id=4, x=0,   y=0,   w=500,  h=500, sheet=sheet_names[0]),
            ZoneSpec(id=5, x=500, y=0,   w=500,  h=500, sheet=sheet_names[1]),
            ZoneSpec(id=6, x=0,   y=500, w=1000, h=500, sheet=sheet_names[2]),
        ]
    if n == 4:
        return [
            ZoneSpec(id=4, x=0,   y=0,   w=500, h=500, sheet=sheet_names[0]),
            ZoneSpec(id=5, x=500, y=0,   w=500, h=500, sheet=sheet_names[1]),
            ZoneSpec(id=6, x=0,   y=500, w=500, h=500, sheet=sheet_names[2]),
            ZoneSpec(id=7, x=500, y=500, w=500, h=500, sheet=sheet_names[3]),
        ]
    # 5-6: top strip of KPI-ish sheets at h=200, rest in 2x2 below
    top = sheet_names[:2]
    rest = sheet_names[2:6]
    zones: list[ZoneSpec] = []
    zones.append(ZoneSpec(id=4, x=0,   y=0, w=500, h=200, sheet=top[0]))
    zones.append(ZoneSpec(id=5, x=500, y=0, w=500, h=200, sheet=top[1]))
    positions = [(0, 200), (500, 200), (0, 600), (500, 600)]
    for i, (name, (x, y)) in enumerate(zip(rest, positions)):
        h = 400
        zones.append(ZoneSpec(id=6 + i, x=x, y=y, w=500, h=h, sheet=name))
    return zones
