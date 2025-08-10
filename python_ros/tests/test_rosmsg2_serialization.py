from ros2idl_parser import parse_ros2idl
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


def test_ros2idl_tf_message_roundtrip():
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
    writer = MessageWriter(defs)
    written = writer.write_message(read)
    assert written == buffer


def test_ros2idl_non_constant_root():
    msg_def = """
module a {
  module b {
    const int8 STATUS_ONE = 1;
    const int8 STATUS_TWO = 2;
  };
  struct c {
   int8 status;
  };
};
    """
    defs = parse_ros2idl(msg_def)
    buffer = bytes([0, 1, 0, 0, 0x02])
    reader = MessageReader(defs)
    assert reader.read_message(buffer) == {"status": 2}
    writer = MessageWriter(defs)
    assert writer.write_message({"status": 2}) == buffer
