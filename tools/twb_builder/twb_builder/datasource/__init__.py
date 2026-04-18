from pathlib import Path

from ..errors import SourceReadError
from .base import DataProfile, FieldProfile


def read_source(
    path: Path,
    *,
    sheet: str | None = None,
    table: str | None = None,
) -> DataProfile:
    """Dispatch to a reader based on file extension."""
    path = Path(path)
    ext = path.suffix.lower()
    if ext == ".csv":
        from .csv_reader import read_csv
        return read_csv(path)
    if ext in {".xlsx", ".xlsm", ".xls"}:
        from .excel_reader import read_excel
        return read_excel(path, sheet=sheet)
    if ext == ".hyper":
        from .hyper_reader import read_hyper
        return read_hyper(path, table=table)
    if ext == ".tds":
        from .tds_reader import read_tds
        return read_tds(path)
    raise SourceReadError(f"Unsupported source extension: {ext}")


__all__ = ["read_source", "DataProfile", "FieldProfile"]
