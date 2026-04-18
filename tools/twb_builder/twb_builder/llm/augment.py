from __future__ import annotations

import os
import re
import sys
from typing import Optional

import yaml

from ..datasource.base import DataProfile
from ..errors import PlanError
from ..plan.schema import Plan
from .prompts import SYSTEM_PROMPT, USER_TEMPLATE


def augment_plan(
    plan: Plan,
    profile: DataProfile,
    *,
    model: str = "claude-opus-4-7",
    strict: bool = False,
) -> Plan:
    """Refine a starter plan via the Anthropic API.

    Falls back to the input plan on any failure unless `strict=True`.
    """
    try:
        import anthropic
    except ImportError as exc:
        raise PlanError("anthropic SDK not installed") from exc

    if not os.getenv("ANTHROPIC_API_KEY"):
        msg = "ANTHROPIC_API_KEY is not set; skipping LLM augmentation."
        if strict:
            raise PlanError(msg)
        print(msg, file=sys.stderr)
        return plan

    starter_yaml = yaml.safe_dump(
        plan.model_dump(mode="json", exclude_none=True),
        sort_keys=False,
    )
    profile_table = _profile_markdown(profile)
    user_text = USER_TEMPLATE.format(
        profile_table=profile_table,
        starter_yaml=starter_yaml,
    )

    client = anthropic.Anthropic()
    resp = client.messages.create(
        model=model,
        max_tokens=8000,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": [{"type": "text", "text": user_text}]}],
    )

    text = "".join(
        block.text for block in resp.content if getattr(block, "type", None) == "text"
    )
    yaml_text = _strip_code_fences(text)
    try:
        data = yaml.safe_load(yaml_text)
        refined = Plan.model_validate(data)
    except Exception as exc:
        if strict:
            raise PlanError(f"LLM returned invalid plan: {exc}\n\n{yaml_text[:2000]}") from exc
        print(f"LLM output invalid ({exc}); falling back to heuristic plan.", file=sys.stderr)
        return plan

    # Field-existence sanity check
    source_names = {f.name for f in refined.datasource.fields}
    referenced = refined.referenced_fields()
    unknown = referenced - source_names
    if unknown:
        if strict:
            raise PlanError(f"LLM referenced unknown fields: {sorted(unknown)}")
        print(f"LLM referenced unknown fields {sorted(unknown)}; using heuristic plan.", file=sys.stderr)
        return plan

    return refined


def _strip_code_fences(text: str) -> str:
    m = re.search(r"```(?:ya?ml)?\n(.*?)```", text, re.DOTALL)
    return m.group(1).strip() if m else text.strip()


def _profile_markdown(profile: DataProfile) -> str:
    header = "| name | datatype | role | cardinality | null % | samples |\n|---|---|---|---|---|---|"
    lines = [header]
    for f in profile.fields:
        samples = ", ".join(f.sample_values[:5])
        lines.append(
            f"| {f.name} | {f.datatype} | {f.role} | {f.cardinality} | {f.null_pct:.1%} | {samples} |"
        )
    return "\n".join(lines)
