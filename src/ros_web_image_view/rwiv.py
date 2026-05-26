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


class Streamer:
    def __init__(self, config: Config):
        self.config = config
        self._bridge = CvBridge()

        self._msg_lock = threading.Lock()
        self._latest_msg = None
        self._msg_event = threading.Event()

        self._frame_lock = threading.Lock()
        self._latest_frame = None
        self._frame_idx = 0
        self._latest_meta = f"Waiting for image on topic {self.config.ROS_topic}"

        self._shutdown = threading.Event()
    
    def img_callback(self, msg):
        with self._msg_lock:
            self._latest_msg = msg
        self._msg_event.set()
    
    def decoder_loop(self):
        while not self._shutdown.is_set():
            if not self._msg_event.wait(timeout=self.config.sleep_dt):
                continue
            self._msg_event.clear()
            with self._msg_lock:
                msg = self._latest_msg
            if msg is None:
                continue
            try:
                cv_image = self._bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
                success, jpeg = cv2.imencode('.jpg', cv_image, [int(cv2.IMWRITE_JPEG_QUALITY), self.config.JPEG_quality])
                if not success:
                    rospy.logwarn("[RWIV] Unable to decode img to jpeg")
                    continue
                
                text = (
                    f"Topic: {self.config.ROS_topic}\n"
                    f"Width: {msg.width}\n"
                    f"Height: {msg.height}\n"
                    f"Encoding: {msg.encoding}\n"
                    f"Header seq: {msg.header.seq}\n"
                    f"Timestamp: {msg.header.stamp.to_sec()}\n"
                    f"Frame ID: {msg.header.frame_id}\n"
                    f"Step: {msg.step}\n"
                    f"Big endian: {msg.is_bigendian}\n"
                    f"Frame: {self._frame_idx}"
                )

                with self._frame_lock:
                    self._latest_frame = jpeg.tobytes()
                    self._frame_idx += 1
                    self._latest_meta = text
            except Exception as e:
                rospy.logerr(f"[RWIV] img reading error: '{e}'")

    def get_frame_if_new(self, last_idx):
        with self._frame_lock:
            if self._latest_frame is None or self._frame_idx == last_idx:
                return None, last_idx
            return self._latest_frame, self._frame_idx
        
    def get_meta(self):
        with self._frame_lock:
            return self._latest_meta
    
    def shutdown(self):
        self._shutdown.set()
        self._msg_event.set()


def build_app(streamer: Streamer):
    here = os.path.join(os.path.dirname(__file__))
    app = Flask(
        "RVIW",
        template_folder=os.path.join(here, 'padges'),
        static_folder=os.path.join(here, 'padges/static')
    )

    @app.route("/")
    def index():
        return render_template('index.html')
    
    @app.route("/video_feed")
    def video_feed():
        def mjpeg_generator():
            last_idx = -1
            while True:
                frame, last_idx = streamer.get_frame_if_new(last_idx)
                if frame is not None:
                    yield (
                            b'--frame\r\n'
                            b'Content-Type: image/jpeg\r\n\r\n' +
                            frame +
                            b'\r\n'
                          )
                else:
                    time.sleep(streamer.config.sleep_dt)

        return Response(
            mjpeg_generator(),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )

    @app.route("/meta")
    def meta():
        return streamer.get_meta()
    
    return app

def flask_thread(streamer: Streamer):
    app = build_app(streamer)
    app.run(
        host=streamer.config.WEB_host,
        port=streamer.config.WEB_port,
        threaded=True,
        use_reloader=False,
        debug=True
    )

def main():
    rospy.init_node('RWIV', anonymous=True)

    config = Config()
    config.read_data()

    streamer = Streamer(config)

    threading.Thread(target=flask_thread, args=(streamer,) , daemon=True, name="flask server").start()
    rospy.loginfo(f"[RWIV] Server started at {config.WEB_host}:{config.WEB_port}")
    
    threading.Thread(target=streamer.decoder_loop, daemon=True, name="decoder").start()

    rospy.Subscriber(
        config.ROS_topic,
        Image,
        streamer.img_callback,
        queue_size=1,
        buff_size=2**24
    )
    rospy.loginfo(f"[RWIV] Subscriped to: {config.ROS_topic}")
    try:
        rospy.spin()
    finally:
        streamer.shutdown()
    