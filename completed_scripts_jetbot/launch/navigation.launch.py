# Copyright (c) 2025 Alice Zenina and Alexander Grachev RTU MIREA (Russia)
# SPDX-License-Identifier: MIT
# Details in the LICENSE file in the root of the package.

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import TimerAction


def generate_launch_description():

    path_to_pkg = get_package_share_directory('completed_scripts_jetbot')

    nav2_yaml = os.path.join(path_to_pkg, 'config', 'navigation', 'amcl_config.yaml')
    map_file = os.path.join(path_to_pkg, 'maps', 'map.yaml')
    map_file = os.path.join(path_to_pkg, 'maps', 'G210_with_boxes_map.yaml')



    return LaunchDescription([
        
        Node(
            package='nav2_amcl',
            executable='amcl',
            name='amcl',
            output='screen',
            parameters=[nav2_yaml]
        ),


        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager',
            output='screen',
            parameters=[{'autostart': True},
                        {'node_names': ['map_server',
                                        'amcl',

                                        ]}]),
        TimerAction(
            period=2.0,  # Задержка в секундах
            actions=[
                Node(
                    package='nav2_map_server',
                    executable='map_server',
                    name='map_server',
                    output='screen',
                    parameters=[{'use_sim_time': True},
                                {'yaml_filename': map_file}]
                ),
            ]
        )
    ])