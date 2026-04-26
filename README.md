# Robotics

ROS 2 robotics projects and experiments.

## Workspace

- [toy_robot_ws/](toy_robot_ws/) — main workspace: modular URDF robot description with 6-DOF arm, gripper, and camera

See [toy_robot_ws/README.md](toy_robot_ws/README.md) for build, launch, and detailed documentation.

## Quick Start

```bash
cd toy_robot_ws
source /opt/ros/jazzy/setup.bash
colcon build --packages-select toy_robot_description
source install/setup.bash
ros2 launch toy_robot_description display.launch.xml
```

## Requirements

- ROS 2 Jazzy
- xacro, robot_state_publisher, joint_state_publisher_gui, rviz2
