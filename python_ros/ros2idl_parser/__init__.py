from __future__ import annotations

from typing import List

from message_definition import MessageDefinition, MessageDefinitionField
from omgidl_parser import parse_idl_message_definitions


def parse_ros2idl(text: str) -> List[MessageDefinition]:
    """Parse ROS 2 IDL text into MessageDefinition objects."""

    blocks: List[str] = []
    current: List[str] = []
    for line in text.splitlines():
        if line.startswith("==="):
            if current:
                blocks.append("\n".join(current))
                current = []
        elif line.startswith("IDL:"):
            continue
        else:
            current.append(line)
    if current:
        blocks.append("\n".join(current))

    combined = "\n".join(blocks)
    idl_defs = parse_idl_message_definitions(combined)

    def convert_name(name: str | None) -> str | None:
        return name.replace("::", "/") if name else None

    definitions: List[MessageDefinition] = []
    for defn in idl_defs:
        fields = [
            MessageDefinitionField(**{**vars(f), "type": convert_name(f.type)})
            for f in defn.definitions
        ]
        definitions.append(
            MessageDefinition(name=convert_name(defn.name), definitions=fields)
        )

    return definitions


__all__ = ["parse_ros2idl"]
