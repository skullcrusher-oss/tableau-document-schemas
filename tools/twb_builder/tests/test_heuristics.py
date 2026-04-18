from pathlib import Path

from twb_builder.datasource import read_source
from twb_builder.plan.heuristics import build_heuristic_plan


def test_heuristic_produces_expected_sheets(sales_csv: Path) -> None:
    profile = read_source(sales_csv)
    plan = build_heuristic_plan(profile)

    marks = {s.mark for s in plan.sheets}
    assert "Text" in marks    # KPI
    assert "Bar" in marks     # by low-card dim
    assert "Line" in marks    # over time
    assert "Circle" in marks  # scatter

    # No duplicate sheet names (XSD unique constraint)
    names = [s.name for s in plan.sheets]
    assert len(names) == len(set(names))

    # Zones in the default dashboard match the sheets
    dash = plan.dashboards[0]
    zone_sheets = {z.sheet for z in dash.zones}
    assert zone_sheets <= set(names)

    # Every referenced field exists in datasource.fields
    source_names = {f.name for f in plan.datasource.fields}
    assert plan.referenced_fields() <= source_names
