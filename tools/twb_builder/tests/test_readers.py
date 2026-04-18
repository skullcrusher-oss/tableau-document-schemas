from pathlib import Path

import pytest

from twb_builder.datasource import read_source
from twb_builder.datasource.tds_reader import read_tds


def test_csv_reader_infers_roles(sales_csv: Path) -> None:
    profile = read_source(sales_csv)
    by_name = {f.raw_name: f for f in profile.fields}

    assert by_name["sales"].role == "measure"
    assert by_name["sales"].datatype == "real"
    assert by_name["sales"].aggregation == "Sum"

    assert by_name["region"].role == "dimension"
    assert by_name["region"].datatype == "string"

    # Date column parsed via to_datetime fallback (object dtype in csv)
    assert by_name["order_date"].datatype in {"date", "datetime"}

    assert profile.row_count == 100


def test_excel_reader(sales_xlsx: Path) -> None:
    profile = read_source(sales_xlsx)
    names = {f.raw_name for f in profile.fields}
    assert names == {"order_date", "region", "product", "sales", "profit"}


def test_tds_reader(tmp_path: Path) -> None:
    tds = tmp_path / "mini.tds"
    tds.write_text(
        """<?xml version='1.0'?>
<datasource name='mini' version='26.1'>
  <connection class='sqlproxy'/>
  <column name='[id]' role='dimension' type='ordinal' datatype='integer'/>
  <column name='[amount]' role='measure' type='quantitative' datatype='real' aggregation='Sum'/>
</datasource>"""
    )
    profile = read_tds(tds)
    assert [f.name for f in profile.fields] == ["[id]", "[amount]"]
    assert profile.fields[1].aggregation == "Sum"
