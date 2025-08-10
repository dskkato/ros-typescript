from rosmsg2_serialization import MessageReader, MessageWriter
from rosmsg.parse import parse


def roundtrip(msg_def: str, message):
    defs = parse(msg_def, ros2=True)
    writer = MessageWriter(defs)
    data = writer.write_message(message)
    reader = MessageReader(defs)
    return reader.read_message(data)


def test_primitive_roundtrip():
    msg_def = """
int32 a
string b
"""
    msg = {"a": -42, "b": "hello"}
    assert roundtrip(msg_def, msg) == msg


def test_array_roundtrip():
    msg_def = """
int32[] values
"""
    msg = {"values": [1, 2, 3]}
    assert roundtrip(msg_def, msg) == msg


def test_nested_and_time():
    msg_def = """
builtin_interfaces/msg/Time stamp
================================================================================
MSG: builtin_interfaces/msg/Time
int32 sec
uint32 nanosec
"""
    msg = {"stamp": {"sec": 1, "nanosec": 2}}
    assert roundtrip(msg_def, msg) == msg


def test_empty_message():
    msg_def = """"""
    msg = {}
    assert roundtrip(msg_def, msg) == msg
