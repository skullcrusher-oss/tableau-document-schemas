from pathlib import Path

from typer.testing import CliRunner

from twb_builder.cli import app


def test_plan_then_build(tmp_path: Path, sales_csv: Path) -> None:
    runner = CliRunner()
    plan_path = tmp_path / "plan.yaml"
    twb_path = tmp_path / "out.twb"

    result = runner.invoke(app, ["plan", str(sales_csv), "--out", str(plan_path)])
    assert result.exit_code == 0, result.output
    assert plan_path.exists()

    result = runner.invoke(app, ["build", str(plan_path), "--out", str(twb_path)])
    assert result.exit_code == 0, result.output
    assert twb_path.exists() and twb_path.stat().st_size > 0


def test_validate_only(tmp_path: Path, sales_csv: Path) -> None:
    runner = CliRunner()
    plan_path = tmp_path / "plan.yaml"
    twb_path = tmp_path / "out.twb"

    runner.invoke(app, ["plan", str(sales_csv), "--out", str(plan_path)])
    runner.invoke(app, ["build", str(plan_path), "--out", str(twb_path)])

    result = runner.invoke(app, ["build", str(twb_path), "--validate-only"])
    assert result.exit_code == 0
    assert "XSD valid" in result.output
