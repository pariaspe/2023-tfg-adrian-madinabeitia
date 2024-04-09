from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument

namespace = "drone0"
sim_time = "true"

env_vars = {
    'AEROSTACK2_SIMULATION_DRONE_ID': namespace
}

def generate_launch_description():

    controller = Node(
        package='ds4_driver',
        executable='ds4_driver_node.py',
    )

    out_dir = DeclareLaunchArgument(
        'out_dir',
        default_value="./outDir"
    )

    control = Node(
        package='tello_driver',
        executable='remoteControl.py',
        output='screen',
        arguments=[
            '--output_directory', LaunchConfiguration('out_dir'),
        ]
    )

    return LaunchDescription([
        out_dir,
        controller,
        control,
    ])