#!/usr/bin/env python3
import sys, numpy as np
import rosbag2_py
from rclpy.serialization import serialize_message
from nav_msgs.msg import Odometry
from scipy.spatial.transform import Rotation as R

T0 = 10.0
Tbc = np.eye(4)
Tbc[:3, :3] = R.from_euler('ZYX', [-1.5707963, 0, -1.5707963]).as_matrix()
Tcb = np.linalg.inv(Tbc)

w = rosbag2_py.SequentialWriter()
w.open(rosbag2_py.StorageOptions(uri=sys.argv[2], storage_id='sqlite3'), rosbag2_py.ConverterOptions('', ''))
w.create_topic(rosbag2_py.TopicMetadata(id=0, name='/odom', type='nav_msgs/msg/Odometry', serialization_format='cdr'))
n = 0
for line in open(sys.argv[1]):
    if line.startswith('#') or not line.strip(): continue
    t, tx, ty, tz, qx, qy, qz, qw = map(float, line.split()[:8])
    Toc = np.eye(4); Toc[:3, :3] = R.from_quat([qx, qy, qz, qw]).as_matrix(); Toc[:3, 3] = [tx, ty, tz]
    Tob = Tbc @ Toc @ Tcb
    q = R.from_matrix(Tob[:3, :3]).as_quat()
    m = Odometry(); ns = int((t + T0) * 1e9)
    m.header.stamp.sec, m.header.stamp.nanosec = ns // 10**9, ns % 10**9
    m.header.frame_id, m.child_frame_id = 'odom', 'base_link'
    p = m.pose.pose; p.position.x, p.position.y, p.position.z = Tob[:3, 3]
    p.orientation.x, p.orientation.y, p.orientation.z, p.orientation.w = q
    m.pose.covariance = [0.01 if i % 7 == 0 else 0.0 for i in range(36)]
    w.write('/odom', serialize_message(m), ns); n += 1
print('wrote', sys.argv[2], n, 'poses')
