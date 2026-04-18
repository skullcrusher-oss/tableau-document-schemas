from pathlib import Path

import pandas as pd

from ..errors import SourceReadError
from .base import DataProfile
from .inference import profile_series


def read_hyper(path: Path, *, table: str | None = None) -> DataProfile:
    try:
        from tableauhyperapi import Connection, HyperProcess, Telemetry
    except ImportError as exc:
        raise SourceReadError(
            "tableauhyperapi is required to read .hyper files. "
            "Install with `pip install 'twb-builder[hyper]'`."
        ) from exc

    with HyperProcess(Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as hyper:
        with Connection(endpoint=hyper.endpoint, database=str(path)) as conn:
            schemas = list(conn.catalog.get_schema_names())
            target_schema, target_table = None, None
            if table and "." in table:
                schema_name, table_name = table.split(".", 1)
                target_schema = next((s for s in schemas if str(s) == schema_name), None)
                if not target_schema:
                    raise SourceReadError(f"Schema {schema_name!r} not found")
                target_table = next(
                    (t for t in conn.catalog.get_table_names(target_schema) if str(t.name) == table_name),
                    None,
                )
            else:
                for s in schemas:
                    tables = list(conn.catalog.get_table_names(s))
                    if tables:
                        target_schema, target_table = s, tables[0]
                        break
            if target_table is None:
                raise SourceReadError("No tables found in hyper file")

            table_def = conn.catalog.get_table_definition(target_table)
            col_names = [str(c.name).strip('"') for c in table_def.columns]
            with conn.execute_query(f"SELECT * FROM {target_table} LIMIT 10000") as result:
                rows = [list(r) for r in result]
            df = pd.DataFrame(rows, columns=col_names)
            fields = [profile_series(col, df[col]) for col in df.columns]
            return DataProfile(
                name=path.stem,
                source_type="hyper",
                path=path,
                fields=fields,
                row_count=len(df),
                extra={"schema": str(target_schema), "table": str(target_table.name)},
            )
