export type Testcase = {
  name: string;
  msgDef: string;
};

export const testCases: Testcase[] = [
  {
    name: "int8 array",
    msgDef: `int8[] arr`,
  },
  {
    name: "float32 array",
    msgDef: `float32[] arr`,
  },
  {
    name: "std_msgs/Header",
    msgDef: `
      uint32 seq
      time stamp
      string frame_id
    `,
  },
  {
    name: "sensor_msgs/PointCloud2",
    msgDef: `
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
          `,
  },
  {
    name: "diagnostic_msgs/DiagnosticArray",
    msgDef: `
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
    `,
  },
];
