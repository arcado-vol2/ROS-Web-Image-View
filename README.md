# ROS Web Image View

This is simple laconic Flask [ROS Noetic](https://wiki.ros.org/noetic) app to stream raw image topic to web browser, so you can check what see your camera whitout headaches.

![Padge sample](https://github.com/arcado-vol2/ROS-Web-Image-View/blob/main/imgs/preview.jpg)

#### Depends on:
- [ROS Noetic](https://wiki.ros.org/noetic)
- [OpenCV](https://github.com/opencv/opencv) for image convertation
- [cv_bridge](https://index.ros.org/p/cv_bridge/) for connection between ROS and OpenCV
- [Flask](https://github.com/pallets/flask) for server

---
#### Config breakdown
- `ROS_topic` - topic of your camera
- `WEB_host` - IP where server will started
- `WEB_port` - port of server
- `JPEG_quality` - how much image will be compressed, less value - more compression => more speed, less quality
- `max_framerate` - target framerate i.e. how often server will check for new frame
