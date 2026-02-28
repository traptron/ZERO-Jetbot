#!/bin/bash

sudo apt install \
    python3-pip \
    ros-$ROS_DISTRO-slam-toolbox \
    ros-$ROS_DISTRO-tf2-ros \
    ros-$ROS_DISTRO-nav2-map-server \
    ros-$ROS_DISTRO-navigation2 \
    ros-$ROS_DISTRO-nav2-bringup \
    ros-$ROS_DISTRO-xacro \
    ros-$ROS_DISTRO-robot-state-publisher \
    ros-$ROS_DISTRO-joint-state-publisher \
    ros-$ROS_DISTRO-gazebo-*


pip install \
    pyserial==3.5 \
    matplotlib==3.7.5 \
    pillow==10.4.0



