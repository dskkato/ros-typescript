from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Mapping, MutableMapping, Sequence

from message_definition import MessageDefinition, MessageDefinitionField

from cdr import CdrReader

from .message_definition_has_data_fields import message_definition_has_data_fields

Ros1Time = Dict[str, int]
Ros2Time = Dict[str, int]

Deserializer = Callable[[CdrReader], Any]
ArrayDeserializer = Callable[[CdrReader, int], Any]


@dataclass
class MessageReaderOptions:
    timeType: str = "sec,nanosec"


class MessageReader:
    _root_definition: Sequence[MessageDefinitionField]
    _definitions: Mapping[str, Sequence[MessageDefinitionField]]
    _use_ros1_time: bool

    def __init__(
        self,
        definitions: Sequence[MessageDefinition],
        options: MessageReaderOptions | None = None,
    ):
        opts = options or MessageReaderOptions()
        time_type = opts.timeType

        # ros2idl modules could have constant modules before the root struct
        root_def = next((d for d in definitions if not _is_constant_module(d)), None)
        if root_def is None:
            raise ValueError("MessageReader initialized with no root MessageDefinition")
        self._root_definition = root_def.definitions
        self._definitions = {d.name or "": d.definitions for d in definitions}
        self._use_ros1_time = time_type == "sec,nsec"

    def read_message(self, buffer: bytes | bytearray | memoryview) -> Any:
        reader = CdrReader(buffer)
        return self._read_complex_type(self._root_definition, reader)

    def _read_complex_type(
        self, definition: Sequence[MessageDefinitionField], reader: CdrReader
    ) -> MutableMapping[str, Any]:
        msg: MutableMapping[str, Any] = {}

        if not message_definition_has_data_fields(definition):
            # For empty message definitions ROS2 adds a uint8 placeholder
            reader.uint8()
            return msg

        for field in definition:
            if field.isConstant is True:
                continue
            if field.isComplex is True:
                nested_def = self._definitions.get(field.type)
                if nested_def is None:
                    raise ValueError(f"Unrecognized complex type {field.type}")
                if field.isArray:
                    array_len = field.arrayLength or reader.sequence_length()
                    array: List[Any] = []
                    for _ in range(array_len):
                        array.append(self._read_complex_type(nested_def, reader))
                    msg[field.name] = array
                else:
                    msg[field.name] = self._read_complex_type(nested_def, reader)
            else:
                if field.isArray:
                    deser = (
                        _ros1_typed_array_deserializers
                        if self._use_ros1_time
                        else _typed_array_deserializers
                    ).get(field.type)
                    if deser is None:
                        raise ValueError(
                            f"Unrecognized primitive array type {field.type}[]"
                        )
                    array_len = field.arrayLength or reader.sequence_length()
                    msg[field.name] = deser(reader, array_len)
                else:
                    deser = (
                        _ros1_deserializers if self._use_ros1_time else _deserializers
                    ).get(field.type)
                    if deser is None:
                        raise ValueError(f"Unrecognized primitive type {field.type}")
                    msg[field.name] = deser(reader)
        return msg


def _is_constant_module(defn: MessageDefinition) -> bool:
    return len(defn.definitions) > 0 and all(f.isConstant for f in defn.definitions)


def _read_bool_array(reader: CdrReader, count: int) -> List[bool]:
    data = reader.int8_array(count)
    return [bool(x) for x in data]


def _read_string_array(reader: CdrReader, count: int) -> List[str]:
    # CdrReader already supports string_array
    return list(reader.string_array(count))


def _read_ros1_time_array(reader: CdrReader, count: int) -> List[Ros1Time]:
    arr: List[Ros1Time] = []
    for _ in range(count):
        sec = reader.int32()
        nsec = reader.uint32()
        arr.append({"sec": sec, "nsec": nsec})
    return arr


def _read_time_array(reader: CdrReader, count: int) -> List[Ros2Time]:
    arr: List[Ros2Time] = []
    for _ in range(count):
        sec = reader.int32()
        nanosec = reader.uint32()
        arr.append({"sec": sec, "nanosec": nanosec})
    return arr


def _throw_on_wstring(*_args: Any, **_kwargs: Any) -> Any:
    raise RuntimeError("wstring is implementation-defined and therefore not supported")


_deserializers: Dict[str, Deserializer] = {
    "bool": lambda r: bool(r.int8()),
    "int8": lambda r: r.int8(),
    "uint8": lambda r: r.uint8(),
    "int16": lambda r: r.int16(),
    "uint16": lambda r: r.uint16(),
    "int32": lambda r: r.int32(),
    "uint32": lambda r: r.uint32(),
    "int64": lambda r: r.int64(),
    "uint64": lambda r: r.uint64(),
    "float32": lambda r: r.float32(),
    "float64": lambda r: r.float64(),
    "string": lambda r: r.string(),
    "wstring": _throw_on_wstring,
    "time": lambda r: {"sec": r.int32(), "nanosec": r.uint32()},
    "duration": lambda r: {"sec": r.int32(), "nanosec": r.uint32()},
}

_ros1_deserializers: Dict[str, Deserializer] = dict(_deserializers)
_ros1_deserializers.update(
    {
        "time": lambda r: {"sec": r.int32(), "nsec": r.uint32()},
        "duration": lambda r: {"sec": r.int32(), "nsec": r.uint32()},
    }
)

_typed_array_deserializers: Dict[str, ArrayDeserializer] = {
    "bool": _read_bool_array,
    "int8": lambda r, c: list(r.int8_array(c)),
    "uint8": lambda r, c: list(r.uint8_array(c)),
    "int16": lambda r, c: list(r.int16_array(c)),
    "uint16": lambda r, c: list(r.uint16_array(c)),
    "int32": lambda r, c: list(r.int32_array(c)),
    "uint32": lambda r, c: list(r.uint32_array(c)),
    "int64": lambda r, c: list(r.int64_array(c)),
    "uint64": lambda r, c: list(r.uint64_array(c)),
    "float32": lambda r, c: list(r.float32_array(c)),
    "float64": lambda r, c: list(r.float64_array(c)),
    "string": _read_string_array,
    "wstring": _throw_on_wstring,
    "time": _read_time_array,
    "duration": _read_time_array,
}

_ros1_typed_array_deserializers: Dict[str, ArrayDeserializer] = dict(
    _typed_array_deserializers
)
_ros1_typed_array_deserializers.update(
    {"time": _read_ros1_time_array, "duration": _read_ros1_time_array}
)

__all__ = ["MessageReader", "MessageReaderOptions"]
