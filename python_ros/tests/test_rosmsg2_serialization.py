from __future__ import annotations

from rosmsg import parse
from rosmsg2_serialization import MessageReader, MessageWriter


def roundtrip(def_text: str, message: dict) -> bytes:
    defs = parse(def_text)
    writer = MessageWriter(defs)
    data = writer.write_message(message)
    reader = MessageReader(defs)
    assert reader.read_message(data) == message
    return data


def test_primitives_round_trip():
    roundtrip("int8 sample", {"sample": -12})
    roundtrip("uint32 count", {"count": 4294967295})
    roundtrip("float64 value", {"value": 0.125})


def test_arrays_round_trip():
    roundtrip("int32[] values", {"values": [3, 7]})
    roundtrip("float32[2] arr", {"arr": [1.5, 2.5]})
    roundtrip("string[] names", {"names": ["one", "two"]})


def test_complex_round_trip():
    definition = (
        "CustomType custom\n"
        "===============\n"
        "MSG: custom_type/CustomType\n"
        "uint8 first"
    )
    roundtrip(definition, {"custom": {"first": 2}})


def test_ignores_constants():
    definition = "int8 A=1\nint8 value"
    roundtrip(definition, {"value": 2})


def test_time_round_trip():
    definition = "time stamp"
    msg = {"stamp": {"sec": 1, "nanosec": 2}}
    roundtrip(definition, msg)
