# twb-builder

Generate XSD-valid Tableau `.twb` workbooks from CSV, Excel, Hyper, or TDS
data sources. Two-step flow:

1. `plan` profiles the source and emits a reviewable YAML plan (optionally
   refined by Claude).
2. `build` renders the plan into a `.twb`, validating against the official XSD
   before writing.

## Install

```
cd tools/twb_builder
pip install -e ".[dev]"           # add ,hyper for .hyper support
```

## Quick start

```
# Generate a plan from a CSV
twb-builder plan examples/sales.csv --out examples/sales.plan.yaml

# (Optional) refine the plan with Claude
export ANTHROPIC_API_KEY=sk-ant-...
twb-builder plan examples/sales.csv --out examples/sales.plan.yaml --llm

# Edit examples/sales.plan.yaml by hand if you like, then render
twb-builder build examples/sales.plan.yaml --out examples/sales.twb

# XSD-validate an existing workbook
twb-builder build some.twb --validate-only
```

Open `examples/sales.twb` in Tableau Desktop. The workbook references the
source CSV by absolute path, so keep it in place (or edit the `connection`
entry in the plan before building).

## Plan file

See `examples/sales.plan.yaml` for a generated example. The plan is
pydantic-validated; every field, mark type, datatype, and aggregation must be
a known value. Keys are snake_case.

## How XSD validation works

The official TWB schema at `schemas/2026_1/twb_2026.1.0.xsd` imports two
namespaces (`user`, `xml`) without schemaLocation. We ship minimal local stubs
(`twb_builder/validate/user_ns.xsd`, `xml_ns.xsd`) and patch the imports in
memory before loading the schema, so validation runs fully offline.

XSD validation confirms structural validity. It does not guarantee Tableau
Desktop will open the file: some elements (notably `<connection>`) are
declared `processContents="skip"` and the XSD is intentionally permissive.

## Tests

```
pytest
```
