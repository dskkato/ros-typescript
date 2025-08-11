from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Mapping, Sequence

from message_definition import AggregatedKind, MessageDefinition, MessageDefinitionField

from cdr import CdrReader

from .message_definition_has_data_fields import message_definition_has_data_fields

Ros2Time = Dict[str, int]
Ros1Time = Dict[str, int]

Deserializer = Callable[[CdrReader], Any]
ArrayDeserializer = Callable[[CdrReader, int], Any]


@dataclass
class MessageReaderOptions:
    timeType: str = "sec,nanosec"  # "sec,nanosec" or "sec,nsec"
    enumsAsStrings: bool = False


class MessageReader:
    _root_definition: MessageDefinition
    _definitions: Mapping[str, MessageDefinition]
    _use_ros1_time: bool
    _enum_types: Dict[str, str]
    _enum_mappings: Dict[str, Dict[int, str]]
    _enums_as_strings: bool

    def __init__(
        self,
        definitions: Sequence[MessageDefinition],
        options: MessageReaderOptions | None = None,
    ) -> None:
        opts = options or MessageReaderOptions()
        time_type = opts.timeType
        self._enums_as_strings = opts.enumsAsStrings

        # ros2idl modules could have constant modules before the root struct used
        # to decode message. Find the first struct definition to use as the root.
        root_definition = next(
            (
                d
                for d in definitions
                if not _is_constant_module(d)
                and d.aggregatedKind == AggregatedKind.STRUCT
            ),
            None,
        )
        if root_definition is None:
            raise ValueError("MessageReader initialized with no root MessageDefinition")
        self._root_definition = root_definition
        self._definitions = {d.name or "": d for d in definitions}
        self._use_ros1_time = time_type == "sec,nsec"

        # Build enum mappings for constant modules so enum values can be
        # converted to their named representation on read.
        self._enum_types = {}
        self._enum_mappings = {}
        for defn in definitions:
            if defn.name and _is_constant_module(defn):
                if not defn.definitions:
                    continue
                base_type = defn.definitions[0].type
                mapping: Dict[int, str] = {}
                for f in defn.definitions:
                    if f.value is not None:
                        try:
                            mapping[int(f.value)] = f.name
                        except (TypeError, ValueError):
                            continue
                if mapping:
                    self._enum_types[defn.name] = base_type
                    self._enum_mappings[defn.name] = mapping

    def read_message(self, buffer: bytes | bytearray | memoryview) -> Any:
        reader = CdrReader(buffer)
        return self._read_complex_type(self._root_definition, reader)

    def _read_complex_type(
        self, definition: MessageDefinition, reader: CdrReader
    ) -> Dict[str, Any]:
        if definition.aggregatedKind == AggregatedKind.UNION:
            return self._read_union(definition, reader)

        msg: Dict[str, Any] = {}

        if not message_definition_has_data_fields(definition.definitions):
            # In case a message definition definition is empty, ROS 2 adds a
            # `uint8 structure_needs_at_least_one_member` field when converting to IDL,
            # to satisfy the requirement from IDL of not being empty.
            reader.uint8()
            return msg

        for field in definition.definitions:
            if field.isConstant is True:
                continue
            msg[field.name] = self._read_field_value(field, reader)

        return msg

    def _read_field_value(
        self, field: MessageDefinitionField, reader: CdrReader
    ) -> Any:
        if field.isComplex is True:
            nested_definition = self._definitions.get(field.type)
            if nested_definition is None:
                raise ValueError(f"Unrecognized complex type {field.type}")
            if field.isArray is True:
                array_length = field.arrayLength or reader.sequence_length()
                return [
                    self._read_complex_type(nested_definition, reader)
                    for _ in range(array_length)
                ]
            return self._read_complex_type(nested_definition, reader)

        if field.isArray is True:
            deser_map = (
                _ros1_typed_array_deserializers
                if self._use_ros1_time
                else _typed_array_deserializers
            )
            if field.type in self._enum_types:
                base_type = self._enum_types[field.type]
                mapping = self._enum_mappings[field.type]
                deser = deser_map.get(base_type)
                if deser is None:
                    raise ValueError(f"Unrecognized primitive array type {base_type}[]")
                array_length = field.arrayLength or reader.sequence_length()
                values = deser(reader, array_length)
                if self._enums_as_strings:
                    return [mapping.get(int(v), v) for v in values]
                return list(values)
            deser = deser_map.get(field.type)
            if deser is None:
                raise ValueError(f"Unrecognized primitive array type {field.type}[]")
            array_length = field.arrayLength or reader.sequence_length()
            return deser(reader, array_length)

        deser_map = _ros1_deserializers if self._use_ros1_time else _deserializers
        if field.type in self._enum_types:
            base_type = self._enum_types[field.type]
            mapping = self._enum_mappings[field.type]
            deser = deser_map.get(base_type)
            if deser is None:
                raise ValueError(f"Unrecognized primitive type {base_type}")
            value = deser(reader)
            if self._enums_as_strings:
                return mapping.get(int(value), value)
            return value
        deser = deser_map.get(field.type)
        if deser is None:
            raise ValueError(f"Unrecognized primitive type {field.type}")
        return deser(reader)

    def _read_union(
        self, definition: MessageDefinition, reader: CdrReader
    ) -> Dict[str, Any]:
        discr_type = definition.switchType or ""
        deser_map = _ros1_deserializers if self._use_ros1_time else _deserializers
        mapping: Dict[int, str] | None = None
        if discr_type in self._enum_types:
            base_type = self._enum_types[discr_type]
            mapping = self._enum_mappings[discr_type]
        else:
            base_type = discr_type
        deser = deser_map.get(base_type)
        if deser is None:
            raise ValueError(f"Unrecognized union discriminator type {discr_type}")
        raw_disc = deser(reader)
        if mapping and self._enums_as_strings:
            discriminator: Any = mapping.get(int(raw_disc), raw_disc)
        else:
            discriminator = raw_disc

        field_for_case: MessageDefinitionField | None = None
        default_field: MessageDefinitionField | None = None
        for f in definition.definitions:
            preds = f.casePredicates or []
            if any(int(raw_disc) == int(p) for p in preds):
                field_for_case = f
                break
            if f.isDefaultCase:
                default_field = f
        if field_for_case is None:
            field_for_case = default_field

        result: Dict[str, Any] = {"discriminator": discriminator}
        if field_for_case is not None:
            result[field_for_case.name] = self._read_field_value(field_for_case, reader)
        return result


def _is_constant_module(defn: MessageDefinition) -> bool:
    return len(defn.definitions) > 0 and all(f.isConstant for f in defn.definitions)


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
