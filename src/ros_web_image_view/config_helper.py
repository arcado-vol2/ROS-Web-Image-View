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
        self.sleep_dt = 0.005
    
    def _get_param_warn(self, name, default):
        if rospy.has_param(name):
            return rospy.get_param(name)

        rospy.logwarn(f"[RWIV] Param '{name}' not found — using default: {default}")
        return default
        

    def read_data(self, namespace="~"):
        '''
        Reads ros config into itself
        ---
        namespace: ROS param namespace
        '''
        self.ROS_topic    = self._get_param_warn(f"{namespace}ROS_topic", "/usb_cam/image_raw")
        self.WEB_host     = self._get_param_warn(f"{namespace}WEB_host", "0.0.0.0")
        self.WEB_port     = self._get_param_warn(f"{namespace}WEB_port", 8080)
        self.JPEG_quality = self._get_param_warn(f"{namespace}JPEG_quality", 80)

        max_framerate     = self._get_param_warn(f"{namespace}max_framerate", 30)

        self.sleep_dt = round(1 / max_framerate / 2, 4)



        