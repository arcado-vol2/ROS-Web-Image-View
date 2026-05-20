__all__ = ["Config"]

from pathlib import Path
import rospy

class _ConfigMeta(type):
    _instances = {}
    
    def __call__(cls, *args, **kwds):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwds)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Config(metaclass=_ConfigMeta):
    '''
    Naive singletone ros config wrapper
    '''
    def __init__(self):
        self.ROS_topic: str = "/usb_cam/image_raw"
        self.WEB_host: str = "0.0.0.0"
        self.WEB_port: int = 8080
        self.JPEG_quality: int = 80
    
    def read_data(self, namespace="~"):
        '''
        Reads ros config into itself
        '''
        self.ROS_topic = rospy.get_param("ROS_topic", "/cam/image_raw")
        self.WEB_host = rospy.get_param("WEB_host", "0.0.0.0")
        self.WEB_port = rospy.get_param("WEB_port", 8000)
        self.JPEG_quality = rospy.get_param("JPEG_quality", 80)

        