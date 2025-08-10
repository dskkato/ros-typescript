from __future__ import annotations

from typing import Any, Callable, Dict, Mapping, Sequence

from message_definition import DefaultValue, MessageDefinition, MessageDefinitionField

from cdr import CdrWriter

from .message_definition_has_data_fields import message_definition_has_data_fields

PrimitiveWriter = Callable[[Any, DefaultValue, CdrWriter, int | None], None]
PrimitiveArrayWriter = Callable[[Any, DefaultValue, CdrWriter, int | None], None]

PRIMITIVE_SIZES: Dict[str, int] = {
    "bool": 1,
    "int8": 1,
    "uint8": 1,
    "int16": 2,
    "uint16": 2,
    "int32": 4,
    "uint32": 4,
    "int64": 8,
    "uint64": 8,
    "float32": 4,
    "float64": 8,
    "time": 8,
    "duration": 8,
}


def throw_on_wstring(*_args: Any, **_kwargs: Any) -> None:
    raise RuntimeError("wstring is implementation-defined and therefore not supported")


# Primitive value writers -----------------------------------------------------


def bool_(
    value: Any, default: DefaultValue, writer: CdrWriter, _len: int | None = None
) -> None:
    val = bool(value) if isinstance(value, bool) else bool(default or False)
    writer.int8(1 if val else 0)


def int8_(
    value: Any, default: DefaultValue, writer: CdrWriter, _len: int | None = None
) -> None:
    writer.int8(int(value if isinstance(value, (int,)) else default or 0))


def uint8_(
    value: Any, default: DefaultValue, writer: CdrWriter, _len: int | None = None
) -> None:
    writer.uint8(int(value if isinstance(value, (int,)) else default or 0))


def int16_(
    value: Any, default: DefaultValue, writer: CdrWriter, _len: int | None = None
) -> None:
    writer.int16(int(value if isinstance(value, (int,)) else default or 0))


def uint16_(
    value: Any, default: DefaultValue, writer: CdrWriter, _len: int | None = None
) -> None:
    writer.uint16(int(value if isinstance(value, (int,)) else default or 0))


def int32_(
    value: Any, default: DefaultValue, writer: CdrWriter, _len: int | None = None
) -> None:
    writer.int32(int(value if isinstance(value, (int,)) else default or 0))


def uint32_(
    value: Any, default: DefaultValue, writer: CdrWriter, _len: int | None = None
) -> None:
    writer.uint32(int(value if isinstance(value, (int,)) else default or 0))


def int64_(
    value: Any, default: DefaultValue, writer: CdrWriter, _len: int | None = None
) -> None:
    if isinstance(value, int):
        writer.int64(value)
    else:
        writer.int64(int(default or 0))


def uint64_(
    value: Any, default: DefaultValue, writer: CdrWriter, _len: int | None = None
) -> None:
    if isinstance(value, int):
        writer.uint64(value)
    else:
        writer.uint64(int(default or 0))


def float32_(
    value: Any, default: DefaultValue, writer: CdrWriter, _len: int | None = None
) -> None:
    writer.float32(float(value if isinstance(value, (int, float)) else default or 0.0))


def float64_(
    value: Any, default: DefaultValue, writer: CdrWriter, _len: int | None = None
) -> None:
    writer.float64(float(value if isinstance(value, (int, float)) else default or 0.0))


def string_(
    value: Any, default: DefaultValue, writer: CdrWriter, _len: int | None = None
) -> None:
    writer.string(str(value) if isinstance(value, str) else str(default or ""))


def time_(
    value: Any, _default: DefaultValue, writer: CdrWriter, _len: int | None = None
) -> None:
    if value is None:
        writer.int32(0)
        writer.uint32(0)
    else:
        obj = value if isinstance(value, Mapping) else {}
        writer.int32(int(obj.get("sec", 0)))
        writer.uint32(int(obj.get("nsec", obj.get("nanosec", 0))))


PRIMITIVE_WRITERS: Dict[str, PrimitiveWriter] = {
    "bool": bool_,
    "int8": int8_,
    "uint8": uint8_,
    "int16": int16_,
    "uint16": uint16_,
    "int32": int32_,
    "uint32": uint32_,
    "int64": int64_,
    "uint64": uint64_,
    "float32": float32_,
    "float64": float64_,
    "string": string_,
    "time": time_,
    "duration": time_,
    "wstring": throw_on_wstring,
}


# Primitive array writers -----------------------------------------------------


def bool_array(
    value: Any, default: DefaultValue, writer: CdrWriter, array_len: int | None = None
) -> None:
    if isinstance(value, Sequence):
        writer.int8Array([1 if bool(v) else 0 for v in value])
    else:
        writer.int8Array(
            [1 if bool(v) else 0 for v in (default or [0] * (array_len or 0))]
        )


def int8_array(
    value: Any, default: DefaultValue, writer: CdrWriter, array_len: int | None = None
) -> None:
    if isinstance(value, Sequence):
        writer.int8Array(list(value))
    else:
        writer.int8Array(list(default or [0] * (array_len or 0)))


def uint8_array(
    value: Any, default: DefaultValue, writer: CdrWriter, array_len: int | None = None
) -> None:
    if isinstance(value, (bytes, bytearray)):
        writer.uint8Array(value)
    elif isinstance(value, Sequence):
        writer.uint8Array(list(value))
    else:
        writer.uint8Array(list(default or [0] * (array_len or 0)))


def int16_array(
    value: Any, default: DefaultValue, writer: CdrWriter, array_len: int | None = None
) -> None:
    if isinstance(value, Sequence):
        writer.int16Array(list(value))
    else:
        writer.int16Array(list(default or [0] * (array_len or 0)))


def uint16_array(
    value: Any, default: DefaultValue, writer: CdrWriter, array_len: int | None = None
) -> None:
    if isinstance(value, Sequence):
        writer.uint16Array(list(value))
    else:
        writer.uint16Array(list(default or [0] * (array_len or 0)))


def int32_array(
    value: Any, default: DefaultValue, writer: CdrWriter, array_len: int | None = None
) -> None:
    if isinstance(value, Sequence):
        writer.int32Array(list(value))
    else:
        writer.int32Array(list(default or [0] * (array_len or 0)))


def uint32_array(
    value: Any, default: DefaultValue, writer: CdrWriter, array_len: int | None = None
) -> None:
    if isinstance(value, Sequence):
        writer.uint32Array(list(value))
    else:
        writer.uint32Array(list(default or [0] * (array_len or 0)))


def int64_array(
    value: Any, default: DefaultValue, writer: CdrWriter, array_len: int | None = None
) -> None:
    if isinstance(value, Sequence):
        writer.int64Array(list(value))
    else:
        writer.int64Array(list(default or [0] * (array_len or 0)))


def uint64_array(
    value: Any, default: DefaultValue, writer: CdrWriter, array_len: int | None = None
) -> None:
    if isinstance(value, Sequence):
        writer.uint64Array(list(value))
    else:
        writer.uint64Array(list(default or [0] * (array_len or 0)))


def float32_array(
    value: Any, default: DefaultValue, writer: CdrWriter, array_len: int | None = None
) -> None:
    if isinstance(value, Sequence):
        writer.float32Array(list(value))
    else:
        writer.float32Array(list(default or [0.0] * (array_len or 0)))


def float64_array(
    value: Any, default: DefaultValue, writer: CdrWriter, array_len: int | None = None
) -> None:
    if isinstance(value, Sequence):
        writer.float64Array(list(value))
    else:
        writer.float64Array(list(default or [0.0] * (array_len or 0)))


def string_array(
    value: Any, default: DefaultValue, writer: CdrWriter, array_len: int | None = None
) -> None:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for item in value:
            writer.string(str(item) if isinstance(item, str) else "")
    else:
        arr = list(default or [""] * (array_len or 0))
        for item in arr:
            writer.string(item)


def time_array(
    value: Any, default: DefaultValue, writer: CdrWriter, array_len: int | None = None
) -> None:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for item in value:
            time_(item, None, writer)
    else:
        arr = [None] * (array_len or 0)
        for item in arr:
            time_(item, None, writer)


PRIMITIVE_ARRAY_WRITERS: Dict[str, PrimitiveArrayWriter] = {
    "bool": bool_array,
    "int8": int8_array,
    "uint8": uint8_array,
    "int16": int16_array,
    "uint16": uint16_array,
    "int32": int32_array,
    "uint32": uint32_array,
    "int64": int64_array,
    "uint64": uint64_array,
    "float32": float32_array,
    "float64": float64_array,
    "string": string_array,
    "time": time_array,
    "duration": time_array,
    "wstring": throw_on_wstring,
}


class MessageWriter:
    _root_definition: Sequence[MessageDefinitionField]
    _definitions: Mapping[str, Sequence[MessageDefinitionField]]

    def __init__(self, definitions: Sequence[MessageDefinition]):
        root_def = next((d for d in definitions if not _is_constant_module(d)), None)
        if root_def is None:
            raise ValueError("MessageReader initialized with no root MessageDefinition")
        self._root_definition = root_def.definitions
        self._definitions = {d.name or "": d.definitions for d in definitions}

    def calculate_byte_size(self, message: Any) -> int:
        return self._byte_size(self._root_definition, message, 4)

    def write_message(self, message: Any, output: bytearray | None = None) -> bytes:
        writer = CdrWriter(buffer=output) if output is not None else CdrWriter()
        self._write(self._root_definition, message, writer)
        return bytes(writer.data)

    # Internal helpers -----------------------------------------------------

    def _byte_size(
        self, definition: Sequence[MessageDefinitionField], message: Any, offset: int
    ) -> int:
        msg = message or {}
        new_offset = offset

        if not message_definition_has_data_fields(definition):
            return offset + self._get_primitive_size("uint8")

        for field in definition:
            if field.isConstant:
                continue
            nested_msg = msg.get(field.name)
            if field.isArray:
                array_length = field.arrayLength or _field_length(nested_msg)
                data_is_array = isinstance(nested_msg, Sequence) and not isinstance(
                    nested_msg, (str, bytes, bytearray)
                )
                data_array = nested_msg if data_is_array else []

                if field.arrayLength is None:
                    new_offset += _padding(new_offset, 4)
                    new_offset += 4

                if field.isComplex:
                    nested_def = self._get_definition(field.type)
                    for i in range(array_length):
                        entry = data_array[i] if i < len(data_array) else {}
                        new_offset = self._byte_size(nested_def, entry, new_offset)
                elif field.type == "string":
                    for i in range(array_length):
                        entry = data_array[i] if i < len(data_array) else ""
                        new_offset += _padding(new_offset, 4)
                        new_offset += 4 + len(entry) + 1
                else:
                    entry_size = self._get_primitive_size(field.type)
                    alignment = 4 if field.type in ("time", "duration") else entry_size
                    new_offset += _padding(new_offset, alignment)
                    new_offset += entry_size * array_length
            else:
                if field.isComplex:
                    nested_def = self._get_definition(field.type)
                    entry = nested_msg or {}
                    new_offset = self._byte_size(nested_def, entry, new_offset)
                elif field.type == "string":
                    entry = nested_msg if isinstance(nested_msg, str) else ""
                    new_offset += _padding(new_offset, 4)
                    new_offset += 4 + len(entry) + 1
                else:
                    entry_size = self._get_primitive_size(field.type)
                    alignment = 4 if field.type in ("time", "duration") else entry_size
                    new_offset += _padding(new_offset, alignment)
                    new_offset += entry_size
        return new_offset

    def _write(
        self,
        definition: Sequence[MessageDefinitionField],
        message: Any,
        writer: CdrWriter,
    ) -> None:
        msg = message or {}

        if not message_definition_has_data_fields(definition):
            uint8_(0, 0, writer)
            return

        for field in definition:
            if field.isConstant:
                continue
            nested_msg = msg.get(field.name)
            if field.isArray:
                array_length = field.arrayLength or _field_length(nested_msg)
                data_is_array = isinstance(nested_msg, Sequence) and not isinstance(
                    nested_msg, (str, bytes, bytearray)
                )
                data_array = nested_msg if data_is_array else []
                if field.arrayLength is None:
                    writer.sequenceLength(array_length)
                if field.arrayLength is not None and nested_msg is not None:
                    given_length = _field_length(nested_msg)
                    if given_length != field.arrayLength:
                        raise ValueError(
                            (
                                "Expected "
                                f"{field.arrayLength} items for fixed-length "
                                "array field "
                                f"{field.name} but "
                                f"received {given_length}"
                            )
                        )
                if field.isComplex:
                    nested_def = self._get_definition(field.type)
                    for i in range(array_length):
                        entry = data_array[i] if i < len(data_array) else {}
                        self._write(nested_def, entry, writer)
                else:
                    array_writer = self._get_primitive_array_writer(field.type)
                    array_writer(
                        nested_msg, field.defaultValue, writer, field.arrayLength
                    )
            else:
                if field.isComplex:
                    nested_def = self._get_definition(field.type)
                    entry = nested_msg or {}
                    self._write(nested_def, entry, writer)
                else:
                    prim_writer = self._get_primitive_writer(field.type)
                    prim_writer(nested_msg, field.defaultValue, writer, None)

    def _get_definition(self, datatype: str) -> Sequence[MessageDefinitionField]:
        nested = self._definitions.get(datatype)
        if nested is None:
            raise ValueError(f"Unrecognized complex type {datatype}")
        return nested

    def _get_primitive_size(self, primitive: str) -> int:
        size = PRIMITIVE_SIZES.get(primitive)
        if size is None:
            if primitive == "wstring":
                throw_on_wstring()
            raise ValueError(f"Unrecognized primitive type {primitive}")
        return size

    def _get_primitive_writer(self, primitive: str) -> PrimitiveWriter:
        writer = PRIMITIVE_WRITERS.get(primitive)
        if writer is None:
            raise ValueError(f"Unrecognized primitive type {primitive}")
        return writer

    def _get_primitive_array_writer(self, primitive: str) -> PrimitiveArrayWriter:
        writer = PRIMITIVE_ARRAY_WRITERS.get(primitive)
        if writer is None:
            raise ValueError(f"Unrecognized primitive type {primitive}[]")
        return writer


def _is_constant_module(defn: MessageDefinition) -> bool:
    return len(defn.definitions) > 0 and all(f.isConstant for f in defn.definitions)


def _field_length(value: Any) -> int:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return len(value)
    return 0


def _padding(offset: int, byte_width: int) -> int:
    alignment = (offset - 4) % byte_width
    return byte_width - alignment if alignment > 0 else 0


__all__ = ["MessageWriter"]
