#!/usr/bin/env python3
# BSD-2 Author: Arcado (Peter Gulia)

import threading
import time
import os

import cv2
from cv_bridge import CvBridge
from flask import Flask, Response, render_template
import rospy
from sensor_msgs.msg import Image
from ros_web_image_view.config_helper import Config

config = Config()
config.read_data()


latest_frame = None
latest_text = f"Waiting for image on topic {config.ROS_topic}..."
frame_lock = threading.Lock()
bridge = CvBridge()
app = Flask(
    "RVIW",
    template_folder=os.path.join(os.path.dirname(__file__), 'padges'),
    static_folder=os.path.join(os.path.dirname(__file__), 'padges/static')
)


def img_callback(msg):
    global latest_frame, latest_text, config
    try:
        cv_image = bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        success, jpeg = cv2.imencode('.jpg', cv_image, [int(cv2.IMWRITE_JPEG_QUALITY), config.JPEG_quality])
        if not success:
            return
        
        jpeg_bytes = jpeg.tobytes()
        text = (
            f"Topic: {config.ROS_topic}\n"
            f"Width: {msg.width}\n"
            f"Height: {msg.height}\n"
            f"Encoding: {msg.encoding}\n"
            f"Header seq: {msg.header.seq}\n"
            f"Timestamp: {msg.header.stamp.to_sec()}\n"
            f"Frame ID: {msg.header.frame_id}\n"
            f"Step: {msg.step}\n"
            f"Big endian: {msg.is_bigendian}\n"
        )

        with frame_lock:
            latest_frame = jpeg_bytes
            latest_text = text
    except Exception as e:
        rospy.logerr(f"[RWIV] img reading error: '{e}'")
    

def mjpeg_generator():
    global latest_frame
    while True:
        frame = None
        
        with frame_lock:
            if latest_frame is not None:
                frame = latest_frame
        if frame:
           yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' +
                frame +
                b'\r\n'
            )
        time.sleep(0.03)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/video_feed")
def video_feed():
    return Response(
        mjpeg_generator(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@app.route("/meta")
def meta():
    global latest_text
    with frame_lock:
        return latest_text




def flash_thread():
    app.run(
        host=config.WEB_host,
        port=config.WEB_port,
        threaded=True,
        use_reloader=False,
        debug=False
    )


def main():
    rospy.init_node('RWIV', anonymous=True)
    server_thread = threading.Thread(target=flash_thread, daemon=True)
    server_thread.start()
    rospy.loginfo(f"[RWIV] Server started")
    rospy.Subscriber(
        config.ROS_topic,
        Image,
        img_callback,
        queue_size=1,
        buff_size=2**24
    )
    rospy.loginfo(f"[RWIV] Subscriped to: {config.ROS_topic}")
    rospy.spin()
    