import os.path

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, TimerAction
from launch.conditions import IfCondition
from launch.substitutions import EnvironmentVariable, LaunchConfiguration, PathJoinSubstitution

from launch_ros.actions import Node


def generate_launch_description():
    package_path = get_package_share_directory('fast_lio_robosense')
    default_config_path = os.path.join(package_path, 'config')
    default_rviz_config_path = os.path.join(package_path, 'rviz', 'fastlio.rviz')

    use_sim_time = LaunchConfiguration('use_sim_time')
    config_path = LaunchConfiguration('config_path')
    config_file = LaunchConfiguration('config_file')
    rviz_use = LaunchConfiguration('rviz')
    rviz_cfg = LaunchConfiguration('rviz_cfg')
    map_file_path = LaunchConfiguration('map_file_path')
    play_bag = LaunchConfiguration('play_bag')
    bag_path = LaunchConfiguration('bag_path')
    system_library_path = [
        '/lib/x86_64-linux-gnu:/usr/lib/x86_64-linux-gnu:',
        EnvironmentVariable('LD_LIBRARY_PATH', default_value=''),
    ]

    fast_lio_node = Node(
        package='fast_lio_robosense',
        executable='fastlio_mapping',
        parameters=[
            PathJoinSubstitution([config_path, config_file]),
            {
                'use_sim_time': use_sim_time,
                'map_file_path': map_file_path,
            },
        ],
        additional_env={'LD_LIBRARY_PATH': system_library_path},
        output='screen',
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_cfg],
        condition=IfCondition(rviz_use),
    )

    bag_play = TimerAction(
        period=2.0,
        actions=[
            ExecuteProcess(
                cmd=[
                    'ros2', 'bag', 'play', bag_path,
                    '--topics', '/rslidar_rear/points', '/rslidar_rear/imu_data',
                ],
                output='screen',
                condition=IfCondition(play_bag),
            )
        ],
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation clock if true.',
        ),
        DeclareLaunchArgument(
            'config_path',
            default_value=default_config_path,
            description='Yaml config directory.',
        ),
        DeclareLaunchArgument(
            'config_file',
            default_value='gigaai_airy_rear.yaml',
            description='Yaml config file.',
        ),
        DeclareLaunchArgument(
            'rviz',
            default_value='true',
            description='Start RViz.',
        ),
        DeclareLaunchArgument(
            'rviz_cfg',
            default_value=default_rviz_config_path,
            description='RViz config file path.',
        ),
        DeclareLaunchArgument(
            'map_file_path',
            default_value='',
            description='Path to save the map PCD file.',
        ),
        DeclareLaunchArgument(
            'play_bag',
            default_value='false',
            description='Play the GigaAI bag from this launch file.',
        ),
        DeclareLaunchArgument(
            'bag_path',
            default_value='/home/sax/rosbags/GigaAI/airy_points_imu_20260512_175121',
            description='ROS bag directory to play when play_bag is true.',
        ),
        fast_lio_node,
        rviz_node,
        bag_play,
    ])
