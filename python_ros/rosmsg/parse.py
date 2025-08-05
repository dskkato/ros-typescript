from __future__ import annotations

import re
from typing import List, Optional

from ..message_definition import (
    MessageDefinition,
    MessageDefinitionField,
    is_msg_def_equal,
)

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


def parse(
    message_definition: str, ros2: bool = False, skip_type_fixup: bool = False
) -> List[MessageDefinition]:
    if ros2:
        raise NotImplementedError("ROS2 parsing not yet implemented")

    lines = [line.strip() for line in message_definition.splitlines() if line.strip()]
    definition_lines: List[str] = []
    types: List[MessageDefinition] = []
    for line in lines:
        if line.startswith("#"):
            continue
        if line.startswith("=="):
            types.append(_build_type(definition_lines))
            definition_lines = []
        else:
            definition_lines.append(line)
    types.append(_build_type(definition_lines))

    unique: List[MessageDefinition] = []
    for t in types:
        if not any(is_msg_def_equal(t, other) for other in unique):
            unique.append(t)

    if not skip_type_fixup:
        fixup_types(unique)

    return unique


def fixup_types(types: List[MessageDefinition]) -> None:
    for msg in types:
        namespace = "/".join(msg.name.split("/")[:-1]) if msg.name else None
        for field in msg.definitions:
            if field.is_complex:
                found = _find_type_by_name(types, field.type, namespace)
                if found.name is None:
                    raise ValueError(f"Missing type definition for {field.type}")
                field.type = found.name


def _build_type(lines: List[str]) -> MessageDefinition:
    definitions: List[MessageDefinitionField] = []
    complex_type_name: Optional[str] = None
    for line in lines:
        if line.startswith("MSG:"):
            complex_type_name = line.split(":", 1)[1].strip()
            continue
        line = re.sub(r"#.*", "", line).strip()
        if not line:
            continue
        m = re.match(
            r"(?P<type>[^\s]+)\s+(?P<name>[^\s=]+)(\s*=\s*(?P<value>.*))?", line
        )
        if not m:
            raise ValueError(f"Could not parse line: '{line}'")
        type_name = normalize_type(m.group("type"))
        name = m.group("name")
        value_text = m.group("value")
        is_array = False
        array_length: Optional[int] = None
        array_match = re.match(r"^(?P<base>[^\[]+)\[(?P<len>\d*)\]$", type_name)
        if array_match:
            type_name = array_match.group("base")
            is_array = True
            length = array_match.group("len")
            if length:
                array_length = int(length)
        is_complex = not _is_builtin(type_name)
        field = MessageDefinitionField(
            type=type_name,
            name=name,
            is_array=is_array,
            array_length=array_length,
            is_constant=value_text is not None,
            value_text=value_text.strip() if value_text is not None else None,
            is_complex=is_complex,
        )
        definitions.append(field)
    return MessageDefinition(name=complex_type_name, definitions=definitions)


def _find_type_by_name(
    types: List[MessageDefinition], name: str, type_namespace: Optional[str]
) -> MessageDefinition:
    matches: List[MessageDefinition] = []
    for t in types:
        type_name = t.name or ""
        if not name:
            if not type_name:
                matches.append(t)
        elif "/" in name:
            if type_name == name:
                matches.append(t)
        elif name == "Header":
            if type_name == "std_msgs/Header":
                matches.append(t)
        elif type_namespace:
            if type_name == f"{type_namespace}/{name}":
                matches.append(t)
        else:
            if type_name.endswith(f"/{name}"):
                matches.append(t)
    if not matches:
        raise ValueError(
            f"Expected 1 top level type definition for '{name}' "
            f"but found {len(matches)}"
        )
    if len(matches) > 1:
        raise ValueError(
            f"Cannot unambiguously determine fully-qualified type name for '{name}'"
        )
    return matches[0]


def normalize_type(type_name: str) -> str:
    if type_name == "char":
        return "uint8"
    if type_name == "byte":
        return "int8"
    return type_name


def _is_builtin(type_name: str) -> bool:
    return type_name in BUILTIN_TYPES
