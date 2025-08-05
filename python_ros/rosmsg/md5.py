from __future__ import annotations

import hashlib
from typing import Dict, List

from ..message_definition import MessageDefinition

BUILTIN_TYPES = {
    "int8",
    "uint8",
    "int16",
    "uint16",
    "int32",
    "uint32",
    "int64",
    "uint64",
    "float32",
    "float64",
    "string",
    "bool",
    "char",
    "byte",
    "time",
    "duration",
}


def md5(msg_defs: List[MessageDefinition]) -> str:
    if not msg_defs:
        raise ValueError("Cannot produce md5sum for empty msgDefs")
    sub_defs: Dict[str, MessageDefinition] = {
        d.name: d for d in msg_defs if d.name is not None
    }
    first = msg_defs[0]
    return _compute_md5(first, sub_defs)


def _compute_md5(
    msg_def: MessageDefinition, sub_defs: Dict[str, MessageDefinition]
) -> str:
    constants = [d for d in msg_def.definitions if d.is_constant]
    variables = [d for d in msg_def.definitions if not d.is_constant]
    lines: List[str] = []
    for d in constants:
        value_text = d.value_text if d.value_text is not None else str(d.value)
        lines.append(f"{d.type} {d.name}={value_text}")
    for d in variables:
        if _is_builtin(d.type):
            array_len = str(d.array_length) if d.array_length is not None else ""
            array = f"[{array_len}]" if d.is_array else ""
            lines.append(f"{d.type}{array} {d.name}")
        else:
            sub = sub_defs.get(d.type)
            if sub is None:
                raise ValueError(f'Missing definition for submessage type "{d.type}"')
            sub_md5 = _compute_md5(sub, sub_defs)
            lines.append(f"{sub_md5} {d.name}")
    text = "\n".join(lines)
    return hashlib.md5(text.encode()).hexdigest()


def _is_builtin(type_name: str) -> bool:
    return type_name in BUILTIN_TYPES
