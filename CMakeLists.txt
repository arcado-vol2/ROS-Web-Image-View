cmake_minimum_required(VERSION 3.0.2)

project(ros_web_image_view)

find_package(catkin REQUIRED COMPONENTS
  rospy
  sensor_msgs
  cv_bridge
)

catkin_package()

include_directories(
  ${catkin_INCLUDE_DIRS}
)

catkin_python_setup()

catkin_install_python(PROGRAMS
  scripts/rwiv_node.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)