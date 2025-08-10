import struct

import pytest
from rosmsg2_serialization import MessageReader
from rosmsg.parse import parse


def _serialize_string(string: str) -> bytes:
    data = string.encode("utf8")
    return struct.pack("<I", len(data) + 1) + data + b"\x00"


def test_primitive_fields():
    msg_def = """int32 a
string b
"""
    defs = parse(msg_def, ros2=True)
    data = b"\x00\x01\x00\x00" + struct.pack("<i", -42) + _serialize_string("hello")
    reader = MessageReader(defs)
    assert reader.read_message(data) == {"a": -42, "b": "hello"}


def test_array_field():
    msg_def = """int32[] values
"""
    defs = parse(msg_def, ros2=True)
    data = b"\x00\x01\x00\x00" + struct.pack("<I", 3) + struct.pack("<3i", 1, 2, 3)
    reader = MessageReader(defs)
    assert reader.read_message(data) == {"values": [1, 2, 3]}


def test_nested_time():
    msg_def = """builtin_interfaces/msg/Time stamp
================================================================================
MSG: builtin_interfaces/msg/Time
int32 sec
uint32 nanosec
"""
    defs = parse(msg_def, ros2=True)
    data = b"\x00\x01\x00\x00" + struct.pack("<iI", 1, 2)
    reader = MessageReader(defs)
    assert reader.read_message(data) == {"stamp": {"sec": 1, "nanosec": 2}}


def test_empty_message():
    msg_def = ""
    defs = parse(msg_def, ros2=True)
    reader = MessageReader(defs)
    assert reader.read_message(b"\x00\x01\x00\x00\x00") == {}


@pytest.mark.skip("ros2idl parser support pending")
def test_ros2idl_tf_message():
    from ros2idl_parser import parse_ros2idl

    buffer = bytes.fromhex(
        "0001000001000000286fae6169ddd73108000000747572746c6531000e000000"
        "747572746c65315f616865616400000000000000000000000000f03f00000000"
        "0000000000000000000000000000000000000000000000000000000000000000"
        "00000000000000000000f03f"
    )
    msg_def = """
================================================================================
IDL: geometry_msgs/msg/Transforms

module geometry_msgs {
  module msg {
    struct Transforms {
      sequence<geometry_msgs::msg::TransformStamped> transforms;
    };
  };
};
================================================================================
IDL: geometry_msgs/msg/TransformStamped

module geometry_msgs {
  module msg {
    struct TransformStamped {
      std_msgs::msg::Header header;
      string child_frame_id; // the frame id of the child frame
      geometry_msgs::msg::Transform transform;
    };
  };
};
================================================================================
IDL: std_msgs/msg/Header

module std_msgs {
  module msg {
    struct Header {
      builtin_interfaces::Time stamp;
      string frame_id;
    };
  };
};
================================================================================
IDL: geometry_msgs/msg/Transform

module geometry_msgs {
  module msg {
    struct Transform {
      geometry_msgs::msg::Vector3 translation;
      geometry_msgs::msg::Quaternion rotation;
    };
  };
};

================================================================================
IDL: geometry_msgs/msg/Vector3

module geometry_msgs {
  module msg {
    struct Vector3 {
      double x;
      double y;
      double z;
    };
  };
};

================================================================================
IDL: geometry_msgs/msg/Quaternion

module geometry_msgs {
  module msg {
    struct Quaternion {
      double x;
      double y;
      double z;
      double w;
    };
  };
};

================================================================================
IDL: builtin_interfaces/Time
// Normally added when generating idl schemas

module builtin_interfaces {
  struct Time {
    int32 sec;
    uint32 nsec;
  };
};
    """
    defs = parse_ros2idl(msg_def)
    reader = MessageReader(defs)
    read = reader.read_message(buffer)
    assert read == {
        "transforms": [
            {
                "header": {
                    "stamp": {"sec": 1638821672, "nsec": 836230505},
                    "frame_id": "turtle1",
                },
                "child_frame_id": "turtle1_ahead",
                "transform": {
                    "translation": {"x": 1.0, "y": 0.0, "z": 0.0},
                    "rotation": {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0},
                },
            }
        ]
    }
