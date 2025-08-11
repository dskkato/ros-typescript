from __future__ import annotations

import timeit

from . import parse

TEST_CASES = [
    (
        "int8 array",
        "int8[] arr",
    ),
    (
        "float32 array",
        "float32[] arr",
    ),
    (
        "std_msgs/Header",
        """
        uint32 seq
        time stamp
        string frame_id
        """,
    ),
    (
        "sensor_msgs/PointCloud2",
        """
        Header header
        uint32 height
        uint32 width
        PointField[] fields
        bool    is_bigendian
        uint32  point_step
        uint32  row_step
        uint8[] data
        bool is_dense
        ===================
        MSG: std_msgs/Header
        uint32 seq
        time stamp
        string frame_id
        ===================
        MSG: sensor_msgs/PointField
        string name
        uint32 offset
        uint8  datatype
        uint32 count
        """,
    ),
    (
        "diagnostic_msgs/DiagnosticArray",
        """
    Header header
    DiagnosticStatus[] status
    ======================
    MSG: std_msgs/Header
    uint32 seq
    time stamp
    string frame_id
    ================
    MSG: misc/DiagnosticStatus
    byte level
    string name
    string message
    string hardware_id
    KeyValue[] values
    ================
    MSG: misc/KeyValue
    string key
    string value
    """,
    ),
]


def run(iterations: int = 1000) -> None:
    for name, msg_def in TEST_CASES:
        duration = timeit.timeit(lambda: parse(msg_def), number=iterations)
        print(f"{name}: {duration:.4f}s for {iterations} parses")


if __name__ == "__main__":
    run()
