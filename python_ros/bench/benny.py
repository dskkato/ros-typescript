from __future__ import annotations

import time
from typing import Callable, Dict

from rosmsg2_serialization import MessageReader, MessageWriter
from rosmsg.parse import parse

from .test_cases import test_cases


def benchmark(fn: Callable[[], None], duration: float = 1.0) -> float:
    """Run `fn` repeatedly for at least `duration` seconds.

    Returns operations per second."""

    count = 0
    start = time.perf_counter()
    end = start
    while end - start < duration:
        fn()
        count += 1
        end = time.perf_counter()
    return count / (end - start)


def run_suite(name: str, cases: Dict[str, Callable[[], None]]) -> None:
    print(f'Running "{name}" suite...')
    results = []
    for label, fn in cases.items():
        ops = benchmark(fn)
        results.append((label, ops))
        print(f"  {label}: {ops:,.0f} ops/s")
    fastest = max(results, key=lambda t: t[1])[0]
    slowest = min(results, key=lambda t: t[1])[0]
    print(f"Finished {len(cases)} cases!")
    print(f"  Fastest: {fastest}")
    print(f"  Slowest: {slowest}")


def main() -> None:
    for tc in test_cases:
        defs = parse(tc.msg_def)
        writer = MessageWriter(defs)
        msg_data = writer.write_message(tc.msg)

        run_suite(
            f"{tc.name} - new reader",
            {
                "Reg": lambda: MessageReader(defs),
            },
        )

        reader = MessageReader(defs)
        run_suite(
            f"{tc.name} - read message",
            {
                "Reg": lambda: reader.read_message(msg_data),
            },
        )

        reader2 = MessageReader(defs)
        run_suite(
            f"{tc.name} - read last field",
            {
                "Reg": lambda: tc.last_field(reader2.read_message(msg_data)),
            },
        )
        print("---------------------------------------")


if __name__ == "__main__":
    main()
