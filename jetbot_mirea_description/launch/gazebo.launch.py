from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess, DeclareLaunchArgument, TimerAction
from launch.substitutions import LaunchConfiguration, Command, PathJoinSubstitution, PythonExpression
from ament_index_python.packages import get_package_share_directory
import os
from launch.conditions import IfCondition


def generate_launch_description():
    
    launch_rviz_arg = DeclareLaunchArgument(
        'launch_rviz_description',
        default_value='True',
        description='Запускает / не запускает RViz2.',
        choices=['True', 'False']
    )

    rviz_condition = PythonExpression([
        '"', LaunchConfiguration('launch_rviz_description'), '" == "True"'
    ])
    
    pkg_path = get_package_share_directory('jetbot_mirea_description')
    urdf_file = os.path.join(pkg_path, 'urdf', 'jetbot_mirea_simple_gazebo.urdf.xacro')
    robot_desc = Command(['xacro ', urdf_file])
    
    rviz_config_dir = os.path.join(pkg_path, 'rviz', 'gazebo_set.rviz')

    
    # Базовый путь к мирам Gazebo (используем правильный путь)
    gazebo_world_path =  os.path.join(pkg_path, 'world', 'simple_labirint.world')
    
    gazebo = ExecuteProcess(
        cmd=['gazebo', '--verbose', '-s', 'libgazebo_ros_factory.so',gazebo_world_path],
        output='screen'
    )
    
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_desc,
                     'use_sim_time': True}]
    )
    
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-entity', 'jetbot', '-topic', 'robot_description', '-x', '0', '-y', '0', '-z', '0.1'],
        output='screen',
    )
    
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_dir],
        parameters=[{'use_sim_time': True}],
        condition=IfCondition(rviz_condition),
    )
    
    # Задержка для спавна (чтобы Gazebo успел запуститься)
    delayed_nodes = TimerAction(
        period=3.0,
        actions=[
            spawn_entity,
            rviz_node,
            
        ]
    )
    
    return LaunchDescription([
        launch_rviz_arg,

        gazebo,

        robot_state_publisher,
        delayed_nodes
        
    ])