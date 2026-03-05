# Copyright (c) 2026 Lev Romanov RTU MIREA (Russia)
# SPDX-License-Identifier: MIT
# Details in the LICENSE file in the root of the package.

"""
Launch file for PC side teleoperation.
Starts keyboard teleoperation node that publishes to /cmd_vel topic.
Commands are sent to robot over network via ROS2 topics.
"""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    """Generate launch description for PC teleoperation."""
    
    # Keyboard teleoperation node
    teleop_keyboard_node = Node(
        package='teleop_jetbot',
        executable='teleop_keyboard',
        name='teleop_keyboard',
        output='screen',
        parameters=[{
            'use_sim_time': False,
        }],
    )

    return LaunchDescription([
        teleop_keyboard_node,
    ])
