from pathlib import Path

import pytest
from lxml import etree

from twb_builder.datasource import read_source
from twb_builder.errors import ValidationError
from twb_builder.plan.heuristics import build_heuristic_plan
from twb_builder.render import render_twb
from twb_builder.validate import validate_twb


def test_end_to_end_xsd_valid(sales_csv: Path) -> None:
    profile = read_source(sales_csv)
    plan = build_heuristic_plan(profile)
    twb_bytes = render_twb(plan)
    validate_twb(twb_bytes)  # raises on failure


def test_rendered_xml_shape(sales_csv: Path) -> None:
    profile = read_source(sales_csv)
    plan = build_heuristic_plan(profile)
    twb_bytes = render_twb(plan)
    root = etree.fromstring(twb_bytes)

    assert root.tag == "workbook"
    assert root.get("version") == plan.twb_version
    assert root.find("datasources/datasource") is not None
    assert root.find("worksheets/worksheet") is not None
    assert root.find("dashboards/dashboard") is not None
    # Each worksheet has a uuid
    for ws in root.findall("worksheets/worksheet"):
        assert ws.find("simple-id") is not None
    # Dashboard root zone wrapping user zones
    root_zone = root.find("dashboards/dashboard/zones/zone")
    assert root_zone is not None
    assert root_zone.get("id") == "3"


def test_validation_catches_bad_xml() -> None:
    bad = b"<workbook version='26.1'></workbook>"  # missing source-build
    with pytest.raises(ValidationError):
        validate_twb(bad)
