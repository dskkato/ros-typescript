from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Optional


@dataclass
class MessageDefinitionField:
    type: str
    name: str
    is_array: bool = False
    array_length: Optional[int] = None
    is_constant: bool = False
    value: Any = None
    value_text: Optional[str] = None
    is_complex: bool = False


@dataclass
class MessageDefinition:
    name: Optional[str]
    definitions: List[MessageDefinitionField]


def is_msg_def_equal(a: MessageDefinition, b: MessageDefinition) -> bool:
    return a == b
