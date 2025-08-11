from __future__ import annotations

import pytest
from rosmsg2_serialization import MessageReader, MessageWriter
from rosmsg.parse import parse

from .test_cases import test_cases


@pytest.mark.parametrize("tc", test_cases, ids=lambda tc: tc.name)
def test_new_reader(benchmark, tc) -> None:
    defs = parse(tc.msg_def)
    benchmark(MessageReader, defs)


@pytest.mark.parametrize("tc", test_cases, ids=lambda tc: tc.name)
def test_read_message(benchmark, tc) -> None:
    defs = parse(tc.msg_def)
    writer = MessageWriter(defs)
    msg_data = writer.write_message(tc.msg)
    reader = MessageReader(defs)
    benchmark(reader.read_message, msg_data)


@pytest.mark.parametrize("tc", test_cases, ids=lambda tc: tc.name)
def test_read_last_field(benchmark, tc) -> None:
    defs = parse(tc.msg_def)
    writer = MessageWriter(defs)
    msg_data = writer.write_message(tc.msg)
    reader = MessageReader(defs)
    benchmark(lambda: tc.last_field(reader.read_message(msg_data)))


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__]))
