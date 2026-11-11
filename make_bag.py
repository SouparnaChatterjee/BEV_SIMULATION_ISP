#!/usr/bin/env python3
"""Pack the notebook's rtabmap_export/ folder into a rosbag2.
Usage: python3 make_bag.py rtabmap_export ghost_bag
Topics: /camera/image_raw (bgr8), /camera/depth (16UC1, mm), /camera/camera_info"""
import sys, json
from pathlib import Path
import cv2
import rosbag2_py
from rclpy.serialization import serialize_message
from sensor_msgs.msg import Image, CameraInfo

src, out = Path(sys.argv[1]), sys.argv[2]
cam = json.load(open(src / 'camera.json'))
rgb = [l.split() for l in open(src / 'rgb.txt').read().strip().splitlines()]
dep = [l.split() for l in open(src / 'depth.txt').read().strip().splitlines()]
FRAME, T0 = 'camera_optical_frame', 10.0          # offset so stamps are never 0

writer = rosbag2_py.SequentialWriter()
writer.open(rosbag2_py.StorageOptions(uri=out, storage_id='sqlite3'), rosbag2_py.ConverterOptions('', ''))
for name, typ in [('/camera/image_raw', 'sensor_msgs/msg/Image'), ('/camera/depth', 'sensor_msgs/msg/Image'),
                  ('/camera/camera_info', 'sensor_msgs/msg/CameraInfo')]:
    writer.create_topic(rosbag2_py.TopicMetadata(name=name, type=typ, serialization_format='cdr'))

def stamp(msg, t):
    ns = int((t + T0) * 1e9); msg.header.stamp.sec = ns // 10**9; msg.header.stamp.nanosec = ns % 10**9
    msg.header.frame_id = FRAME; return ns

def image(img, t, enc, bpp):
    m = Image(); ns = stamp(m, t)
    m.height, m.width, m.encoding, m.is_bigendian = img.shape[0], img.shape[1], enc, 0
    m.step = img.shape[1] * bpp; m.data = img.tobytes(); return m, ns

fx, fy, cx, cy = cam['fx'], cam['fy'], cam['cx'], cam['cy']
for (t, rp), (_, dp) in zip(rgb, dep):
    t = float(t)
    m, ns = image(cv2.imread(str(src / rp), cv2.IMREAD_COLOR), t, 'bgr8', 3); writer.write('/camera/image_raw', serialize_message(m), ns)
    m, ns = image(cv2.imread(str(src / dp), cv2.IMREAD_UNCHANGED), t, '16UC1', 2); writer.write('/camera/depth', serialize_message(m), ns)
    ci = CameraInfo(); stamp(ci, t); ci.width, ci.height = cam['width'], cam['height']
    ci.distortion_model = 'plumb_bob'; ci.d = [0.0] * 5
    ci.k = [fx, 0., cx, 0., fy, cy, 0., 0., 1.]; ci.r = [1., 0., 0., 0., 1., 0., 0., 0., 1.]
    ci.p = [fx, 0., cx, 0., 0., fy, cy, 0., 0., 0., 1., 0.]
    writer.write('/camera/camera_info', serialize_message(ci), ns)
print('wrote', out, len(rgb), 'frames')