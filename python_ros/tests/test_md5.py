from rosmsg import md5, parse

MD5_TESTS = [
    ("std_msgs/Bool", "bool data", "8b94c1b53db61fb6aed406028ad6332a"),
    ("Int8Array", "int8[] data", "ac9c931aaf6ce145ea0383362e83c70b"),
    ("BoolFalseConstant", "bool A=False", "d3011fbf97518e43e51a9ef7f5f352f1"),
    (
        "sensor_msgs/PointCloud2",
        """# This message holds a collection of N-dimensional points, which may
  # contain additional information such as normals, intensity, etc. The
  # point data is stored as a binary blob, its layout described by the
  # contents of the \"fields\" array.

  # The point cloud data may be organized 2d (image-like) or 1d
  # (unordered). Point clouds organized as 2d images may be produced by
  # camera depth sensors such as stereo or time-of-flight.

  # Time of sensor data acquisition, and the coordinate frame ID (for 3d
  # points).
  Header header

  # 2D structure of the point cloud. If the cloud is unordered, height is
  # 1 and width is the length of the point cloud.
  uint32 height
  uint32 width

  # Describes the channels and their layout in the binary data blob.
  PointField[] fields

  bool    is_bigendian # Is this data bigendian?
  uint32  point_step   # Length of a point in bytes
  uint32  row_step     # Length of a row in bytes
  uint8[] data         # Actual point data, size is (row_step*height)

  bool is_dense        # True if there are no invalid points

  =============================================================================
  MSG: std_msgs/Header
  # Standard metadata for higher-level stamped data types.
  # This is generally used to communicate timestamped data
  # in a particular coordinate frame.
  #
  # sequence ID: consecutively increasing ID
  uint32 seq
  #Two-integer timestamp that is expressed as:
  # * stamp.sec: seconds (stamp_secs) since epoch (in Python the variable is called 'secs')
  # * stamp.nsec: nanoseconds since stamp_secs (in Python the variable is called 'nsecs')
  # time-handling sugar is provided by the client library
  time stamp
  #Frame this data is associated with
  string frame_id

  =============================================================================
  MSG: sensor_msgs/PointField
  # This message holds the description of one point entry in the
  # PointCloud2 message format.
  uint8 INT8    = 1
  uint8 UINT8   = 2
  uint8 INT16   = 3
  uint8 UINT16  = 4
  uint8 INT32   = 5
  uint8 UINT32  = 6
  uint8 FLOAT32 = 7
  uint8 FLOAT64 = 8

  string name      # Name of field
  uint32 offset    # Offset from start of point struct
  uint8  datatype  # Datatype enumeration, see above
  uint32 count     # How many elements in the field
  """,
        "1158d486dd51d683ce2f1be655c3c181",
    ),
]


def test_md5():
    for _name, msg_def, expected in MD5_TESTS:
        assert md5(parse(msg_def)) == expected
