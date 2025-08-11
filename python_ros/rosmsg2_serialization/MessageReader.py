from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Mapping, Sequence

from message_definition import MessageDefinition, MessageDefinitionField
from omgidl_parser import IDLMessageDefinition, IDLUnionDefinition

from cdr import CdrReader

from .message_definition_has_data_fields import message_definition_has_data_fields

Ros2Time = Dict[str, int]
Ros1Time = Dict[str, int]

Deserializer = Callable[[CdrReader], Any]
ArrayDeserializer = Callable[[CdrReader, int], Any]


@dataclass
class MessageReaderOptions:
    timeType: str = "sec,nanosec"  # "sec,nanosec" or "sec,nsec"


class MessageReader:
    _root_definition: Any
    _definitions: Mapping[str, Any]
    _use_ros1_time: bool

    def __init__(
        self,
        definitions: Sequence[MessageDefinition | IDLMessageDefinition],
        options: MessageReaderOptions | None = None,
    ) -> None:
        opts = options or MessageReaderOptions()
        time_type = opts.timeType

        # ros2idl modules could have constant modules before the root struct used
        # to decode message
        root_definition = next(
            (
                d
                for d in definitions
                if hasattr(d, "definitions") and not _is_constant_module(d)
            ),
            None,
        )
        if root_definition is None:
            root_definition = next(
                (d for d in definitions if isinstance(d, IDLUnionDefinition)), None
            )
        if root_definition is None:
            raise ValueError("MessageReader initialized with no root MessageDefinition")
        if hasattr(root_definition, "definitions"):
            self._root_definition = list(root_definition.definitions)
        else:
            self._root_definition = root_definition
        defs: Dict[str, Any] = {}
        for d in definitions:
            name = getattr(d, "name", "") or ""
            if isinstance(d, IDLUnionDefinition):
                defs[name] = d
            else:
                defs[name] = list(d.definitions)
        self._definitions = defs
        self._use_ros1_time = time_type == "sec,nsec"

    def read_message(self, buffer: bytes | bytearray | memoryview) -> Any:
        reader = CdrReader(buffer)
        return self._read_definition(self._root_definition, reader)

    def _read_definition(self, definition: Any, reader: CdrReader) -> Any:
        if isinstance(definition, IDLUnionDefinition):
            return self._read_union(definition, reader)
        return self._read_complex_type(definition, reader)

    def _read_complex_type(
        self, definition: Sequence[MessageDefinitionField], reader: CdrReader
    ) -> Dict[str, Any]:
        msg: Dict[str, Any] = {}

        if not message_definition_has_data_fields(definition):
            # In case a message definition definition is empty, ROS 2 adds a
            # `uint8 structure_needs_at_least_one_member` field when converting to IDL,
            # to satisfy the requirement from IDL of not being empty.
            reader.uint8()
            return msg

        for field in definition:
            if field.isConstant is True:
                continue

            if field.isComplex is True:
                nested_definition = self._definitions.get(field.type)
                if nested_definition is None:
                    raise ValueError(f"Unrecognized complex type {field.type}")
                if field.isArray is True:
                    array_length = field.arrayLength or reader.sequence_length()
                    array = []
                    for _ in range(array_length):
                        array.append(self._read_definition(nested_definition, reader))
                    msg[field.name] = array
                else:
                    msg[field.name] = self._read_definition(nested_definition, reader)
            else:
                if field.isArray is True:
                    deser_map = (
                        _ros1_typed_array_deserializers
                        if self._use_ros1_time
                        else _typed_array_deserializers
                    )
                    deser = deser_map.get(field.type)
                    if deser is None:
                        raise ValueError(
                            f"Unrecognized primitive array type {field.type}[]"
                        )
                    array_length = field.arrayLength or reader.sequence_length()
                    msg[field.name] = deser(reader, array_length)
                else:
                    deser_map = (
                        _ros1_deserializers if self._use_ros1_time else _deserializers
                    )
                    deser = deser_map.get(field.type)
                    if deser is None:
                        raise ValueError(f"Unrecognized primitive type {field.type}")
                    msg[field.name] = deser(reader)

        return msg

    def _read_union(
        self, defn: IDLUnionDefinition, reader: CdrReader
    ) -> Dict[str, Any]:
        deser_map = _ros1_deserializers if self._use_ros1_time else _deserializers
        deser = deser_map.get(defn.switchType)
        if deser is None:
            raise ValueError(f"Unrecognized primitive type {defn.switchType}")
        switch_val = deser(reader)

        field_def: MessageDefinitionField | None = None
        for case in defn.cases:
            if switch_val in case.predicates:
                field_def = case.type
                break
        if field_def is None:
            field_def = defn.defaultCase
        if field_def is None:
            return {}

        value: Any
        if field_def.isComplex:
            nested_definition = self._definitions.get(field_def.type)
            if nested_definition is None:
                raise ValueError(f"Unrecognized complex type {field_def.type}")
            if field_def.isArray is True:
                array_length = field_def.arrayLength or reader.sequence_length()
                value = [
                    self._read_definition(nested_definition, reader)
                    for _ in range(array_length)
                ]
            else:
                value = self._read_definition(nested_definition, reader)
        else:
            if field_def.isArray is True:
                deser_arr_map = (
                    _ros1_typed_array_deserializers
                    if self._use_ros1_time
                    else _typed_array_deserializers
                )
                deser_arr = deser_arr_map.get(field_def.type)
                if deser_arr is None:
                    raise ValueError(
                        f"Unrecognized primitive array type {field_def.type}[]"
                    )
                array_length = field_def.arrayLength or reader.sequence_length()
                value = deser_arr(reader, array_length)
            else:
                deser_prim = deser_map.get(field_def.type)
                if deser_prim is None:
                    raise ValueError(f"Unrecognized primitive type {field_def.type}")
                value = deser_prim(reader)

        return {field_def.name: value}


def _is_constant_module(defn: Any) -> bool:
    return (
        hasattr(defn, "definitions")
        and len(defn.definitions) > 0
        and all(f.isConstant for f in defn.definitions)
    )


def _read_bool_array(reader: CdrReader, count: int) -> List[bool]:
    return [bool(reader.int8()) for _ in range(count)]


def _read_string_array(reader: CdrReader, count: int) -> List[str]:
    return [reader.string() for _ in range(count)]


def _read_ros1_time_array(reader: CdrReader, count: int) -> List[Ros1Time]:
    array: List[Ros1Time] = []
    for _ in range(count):
        sec = reader.int32()
        nsec = reader.uint32()
        array.append({"sec": sec, "nsec": nsec})
    return array


def _read_time_array(reader: CdrReader, count: int) -> List[Ros2Time]:
    array: List[Ros2Time] = []
    for _ in range(count):
        sec = reader.int32()
        nanosec = reader.uint32()
        array.append({"sec": sec, "nanosec": nanosec})
    return array


def _throw_on_wstring(*_: Any) -> None:
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

_ros1_deserializers: Dict[str, Deserializer] = {
    **_deserializers,
    "time": lambda r: {"sec": r.int32(), "nsec": r.uint32()},
    "duration": lambda r: {"sec": r.int32(), "nsec": r.uint32()},
}

_typed_array_deserializers: Dict[str, ArrayDeserializer] = {
    "bool": _read_bool_array,
    "int8": lambda r, c: r.int8_array(c).tolist(),
    "uint8": lambda r, c: r.uint8_array(c).tolist(),
    "int16": lambda r, c: r.int16_array(c).tolist(),
    "uint16": lambda r, c: r.uint16_array(c).tolist(),
    "int32": lambda r, c: r.int32_array(c).tolist(),
    "uint32": lambda r, c: r.uint32_array(c).tolist(),
    "int64": lambda r, c: r.int64_array(c).tolist(),
    "uint64": lambda r, c: r.uint64_array(c).tolist(),
    "float32": lambda r, c: r.float32_array(c).tolist(),
    "float64": lambda r, c: r.float64_array(c).tolist(),
    "string": _read_string_array,
    "wstring": _throw_on_wstring,
    "time": _read_time_array,
    "duration": _read_time_array,
}

_ros1_typed_array_deserializers: Dict[str, ArrayDeserializer] = {
    **_typed_array_deserializers,
    "time": _read_ros1_time_array,
    "duration": _read_ros1_time_array,
}

__all__ = ["MessageReader", "MessageReaderOptions"]
