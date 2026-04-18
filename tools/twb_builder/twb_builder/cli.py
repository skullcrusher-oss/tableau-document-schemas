from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from .datasource import read_source
from .errors import ValidationError
from .plan import load_plan, save_plan
from .plan.heuristics import build_heuristic_plan
from .render import render_twb
from .validate import validate_twb

app = typer.Typer(
    help="twb-builder: heuristic + LLM Tableau workbook generator",
    no_args_is_help=True,
)


@app.command()
def plan(
    source: Path = typer.Argument(..., exists=True, readable=True,
                                  help="CSV, XLSX, Hyper, or TDS file"),
    out: Path = typer.Option("plan.yaml", "--out", "-o"),
    llm: bool = typer.Option(False, "--llm", help="Refine the plan via Claude"),
    model: str = typer.Option("claude-opus-4-7", "--model"),
    sheet: Optional[str] = typer.Option(None, help="Excel sheet name"),
    table: Optional[str] = typer.Option(None, help="Hyper schema.table"),
    llm_strict: bool = typer.Option(False, "--llm-strict",
                                    help="Fail if LLM output is invalid"),
) -> None:
    """Profile a data source and emit a YAML plan."""
    profile = read_source(source, sheet=sheet, table=table)
    p = build_heuristic_plan(profile)
    if llm:
        from .llm import augment_plan
        p = augment_plan(p, profile, model=model, strict=llm_strict)
    save_plan(p, out)
    typer.echo(f"Wrote plan with {len(p.sheets)} sheets -> {out}")


@app.command()
def build(
    plan_file: Path = typer.Argument(..., exists=True, readable=True,
                                     help="Plan YAML, or a .twb with --validate-only"),
    out: Path = typer.Option("dashboard.twb", "--out", "-o"),
    validate_only: bool = typer.Option(
        False, "--validate-only",
        help="Treat plan_file as an existing .twb and only XSD-validate it."
    ),
) -> None:
    """Render a plan into a .twb (or validate an existing one)."""
    if validate_only:
        twb_bytes = plan_file.read_bytes()
        try:
            validate_twb(twb_bytes)
        except ValidationError as exc:
            typer.echo(str(exc), err=True)
            raise typer.Exit(code=1)
        typer.echo(f"{plan_file}: XSD valid")
        return

    p = load_plan(plan_file)
    twb_bytes = render_twb(p)
    try:
        validate_twb(twb_bytes)
    except ValidationError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1)
    out.write_bytes(twb_bytes)
    typer.echo(f"Wrote XSD-valid workbook -> {out}")


if __name__ == "__main__":
    app()
