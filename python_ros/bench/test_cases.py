from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List


@dataclass
class TestCase:
    name: str
    msg_def: str
    msg: Dict[str, Any]
    last_field: Callable[[Any], None]


test_cases: List[TestCase] = [
    TestCase(
        name="int8 array",
        msg_def="int8[] arr",
        msg={"arr": [3] * 100000},
        last_field=lambda msg: msg["arr"][99999],
    ),
    TestCase(
        name="float32 array",
        msg_def="float32[] arr",
        msg={"arr": [3.0] * 100000},
        last_field=lambda msg: msg["arr"][99999],
    ),
    TestCase(
        name="std_msgs/Header",
        msg_def="""
        uint32 seq
        time stamp
        string frame_id
        """,
        msg={
            "seq": 0,
            "stamp": {"sec": 0, "nsec": 0},
            "frame_id": "frame id",
        },
        last_field=lambda msg: msg["frame_id"],
    ),
    TestCase(
        name="sensor_msgs/PointCloud2",
        msg_def="""
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
        msg={
            "header": {
                "seq": 0,
                "stamp": {"sec": 0, "nsec": 0},
                "frame_id": "frame id",
            },
            "height": 100,
            "width": 100,
            "fields": [
                {"name": "field 1", "offset": 0, "datatype": 0, "count": 0},
                {"name": "field 2", "offset": 0, "datatype": 0, "count": 0},
                {"name": "field 3", "offset": 0, "datatype": 0, "count": 0},
                {"name": "field 4", "offset": 0, "datatype": 0, "count": 0},
            ],
            "is_bigendian": False,
            "point_step": 0,
            "row_step": 0,
            "data": bytearray(1000000),
            "is_dense": False,
        },
        last_field=lambda msg: msg["is_dense"],
    ),
    TestCase(
        name="diagnostic_msgs/DiagnosticArray",
        msg_def="""
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
        msg={
            "header": {
                "seq": 0,
                "stamp": {"sec": 0, "nsec": 0},
                "frame_id": "frame id",
            },
            "status": [
                {
                    "level": 0,
                    "name": "some name",
                    "message": "some message usually longer",
                    "hardware_id": "some hardware id",
                    "values": [
                        {"key": "a key", "value": "some value"} for _ in range(20)
                    ],
                }
                for _ in range(20)
            ],
        },
        last_field=lambda msg: msg["status"][19]["values"][19]["value"],
    ),
]
