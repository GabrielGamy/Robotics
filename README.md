# Robotics

ROS 2 robotics projects and experiments.

## Workspace

- [toy_robot_ws/](toy_robot_ws/) — main ROS 2 workspace containing:
  - toy_robot_description: modular URDF/xacro robot description (mobile base, camera, 6-DOF arm, gripper)
  - toy_robot_interfaces: custom ROS 2 interfaces used by runtime nodes
  - toy_robot: runtime behavior stack (perception, state machine, navigation integration, RViz debug markers)

See [toy_robot_ws/README.md](toy_robot_ws/README.md) for build, launch, and detailed documentation.

## Quick Start

```bash
cd toy_robot_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash
ros2 launch toy_robot robot.launch.xml
```

URDF-only visualization:

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
- nav2 (for full toy_robot launch flow)

## Documentation

- [toy_robot_ws/docs/index.md](toy_robot_ws/docs/index.md) — documentation entry point
- [toy_robot_ws/docs/development.md](toy_robot_ws/docs/development.md) — build, launch, and test workflow
- [toy_robot_ws/docs/architecture.md](toy_robot_ws/docs/architecture.md) — runtime architecture and data flow
- [toy_robot_ws/docs/rviz_debug.md](toy_robot_ws/docs/rviz_debug.md) — marker semantics and troubleshooting
- [toy_robot_ws/src/toy_robot_description/urdf/README.md](toy_robot_ws/src/toy_robot_description/urdf/README.md) — URDF/xacro modularization and dimension dependencies
