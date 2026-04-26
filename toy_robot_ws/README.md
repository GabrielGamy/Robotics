# Toy Robot Workspace (ROS 2 Jazzy)

This workspace contains the package toy_robot_description with a modular URDF/xacro robot model.

## Quick Start

Build, source, and launch RViz display:

```bash
cd /home/gabrielgamy/src/robotics/toy_robot_ws
source /opt/ros/jazzy/setup.bash
colcon build --packages-select toy_robot_description
source install/setup.bash
ros2 launch toy_robot_description display.launch.xml
```

## URDF Documentation

The detailed URDF guide is in:

- src/toy_robot_description/urdf/README.md

This guide explains:

- file modularization
- global parameter system in dimensions.xacro
- dependencies between base, camera, arm, and gripper dimensions
- safe workflow for geometry updates

## Workspace Structure

```text
toy_robot_ws/
├── src/
│   └── toy_robot_description/
│       ├── launch/
│       └── urdf/
├── build/
├── install/
└── log/
```