from pathlib import Path

import yaml

from .schema import Plan


def load_plan(path: Path) -> Plan:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return Plan.model_validate(data)


def save_plan(plan: Plan, path: Path) -> None:
    data = plan.model_dump(mode="json", exclude_none=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, default_flow_style=False)


__all__ = ["Plan", "load_plan", "save_plan"]
