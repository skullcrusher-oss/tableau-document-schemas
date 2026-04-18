from pathlib import Path

TWB_VERSION = "26.1"
XSD_PATH = (
    Path(__file__).resolve().parents[3]
    / "schemas"
    / "2026_1"
    / "twb_2026.1.0.xsd"
)

__all__ = ["TWB_VERSION", "XSD_PATH"]
