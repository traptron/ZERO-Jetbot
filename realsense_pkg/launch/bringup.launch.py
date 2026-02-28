from launch import LaunchDescription
from launch_ros.actions import Node
import os
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # Если YAML лежит в пакете, получим путь
    package_name = 'realsense_pkg'
    config_file = os.path.join(
        get_package_share_directory(package_name),
        'config',
        'jetbot_set.yaml'
    )

    return LaunchDescription([
        Node(
            package='realsense2_camera',
            executable='realsense2_camera_node',
            name='camera',
            # namespace='camera',
            parameters=[config_file]   # загружаем параметры из файла
        )
    ])