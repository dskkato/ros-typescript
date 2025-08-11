from __future__ import annotations

from typing import List

from message_definition import MessageDefinitionField
from omgidl_parser import (
    Case,
    IDLMessageDefinition,
    IDLModuleDefinition,
    IDLStructDefinition,
    IDLUnionDefinition,
    parse_idl_message_definitions,
)


def parse_ros2idl(text: str) -> List[IDLMessageDefinition]:
    """Parse ROS 2 IDL text into message definition objects."""

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

    definitions: List[IDLMessageDefinition] = []
    for defn in idl_defs:
        if isinstance(defn, IDLUnionDefinition):
            cases: List[Case] = []
            for c in defn.cases:
                field = MessageDefinitionField(
                    **{**vars(c.type), "type": convert_name(c.type.type)}
                )
                cases.append(Case(predicates=list(c.predicates), type=field))

            default_case = None
            if defn.defaultCase is not None:
                default_case = MessageDefinitionField(
                    **{
                        **vars(defn.defaultCase),
                        "type": convert_name(defn.defaultCase.type),
                    }
                )

            definitions.append(
                IDLUnionDefinition(
                    name=convert_name(defn.name) or "",
                    switchType=convert_name(defn.switchType) or "",
                    cases=cases,
                    defaultCase=default_case,
                    annotations=defn.annotations,
                )
            )
        else:
            fields = [
                MessageDefinitionField(**{**vars(f), "type": convert_name(f.type)})
                for f in defn.definitions
            ]
            name = convert_name(defn.name)
            if isinstance(defn, IDLModuleDefinition):
                definitions.append(
                    IDLModuleDefinition(
                        name=name or "",
                        definitions=fields,
                        annotations=defn.annotations,
                    )
                )
            else:
                definitions.append(
                    IDLStructDefinition(
                        name=name or "",
                        definitions=fields,
                        annotations=defn.annotations,
                    )
                )

    return definitions


__all__ = [
    "parse_ros2idl",
]
