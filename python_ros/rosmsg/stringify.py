from __future__ import annotations

import json
from typing import Any, List

from ..message_definition import MessageDefinition


def _stringify_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return json.dumps(value)
    if isinstance(value, float):
        return format(value, "g")
    return str(value)


def stringify_default_value(value: Any) -> str:
    if isinstance(value, list):
        return "[" + ", ".join(_stringify_value(x) for x in value) + "]"
    return _stringify_value(value)


def stringify(msg_defs: List[MessageDefinition]) -> str:
    lines: List[str] = []
    for i, msg_def in enumerate(msg_defs):
        constants = [d for d in msg_def.definitions if getattr(d, "is_constant", False)]
        variables = [
            d for d in msg_def.definitions if not getattr(d, "is_constant", False)
        ]

        if i > 0:
            lines.append("")
            lines.append("=" * 80)
            lines.append(f"MSG: {msg_def.name or ''}")
        for const in constants:
            value = (
                const.value_text
                if const.value_text is not None
                else _stringify_value(const.value)
            )
            lines.append(f"{const.type} {const.name} = {value}")
        if variables:
            if lines:
                lines.append("")
            for var in variables:
                upper_bound = (
                    f"<={var.upper_bound}" if var.upper_bound is not None else ""
                )
                if var.array_length is not None:
                    array_len = str(var.array_length)
                elif var.array_upper_bound is not None:
                    array_len = f"<={var.array_upper_bound}"
                else:
                    array_len = ""
                array_suffix = (
                    f"[{array_len}]" if getattr(var, "is_array", False) else ""
                )
                default_value = (
                    f" {stringify_default_value(var.default_value)}"
                    if var.default_value is not None
                    else ""
                )
                lines.append(
                    f"{var.type}{upper_bound}{array_suffix} {var.name}{default_value}"
                )
    return "\n".join(lines).rstrip()
