# Robotics

ROS 2 robotics projects and experiments.

## Repository layout

This repository is organized as a multi-project workspace:

```text
Robotics/
├── README.md
├── docs/
├── projects/
│   └── toy_robot_ws/
├── scripts/
├── shared/
├── build/
├── install/
├── log/
└── maps/
```

## Active project

- [projects/toy_robot_ws/](projects/toy_robot_ws/) — main ROS 2 workspace for the toy robot project
  - `toy_robot_description`: modular URDF/xacro robot model, Gazebo world, and launch files
  - `toy_robot_interfaces`: custom ROS 2 interfaces for runtime nodes
  - `toy_robot`: runtime behavior, perception, navigation, and visualization stack

See [projects/toy_robot_ws/README.md](projects/toy_robot_ws/README.md) for project-specific build and launch instructions.

## Quick Start

```bash
cd ~/Robotics/projects/toy_robot_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash
ros2 launch toy_robot robot.launch.xml
```

URDF-only visualization:

```bash
cd ~/Robotics/projects/toy_robot_ws
source /opt/ros/jazzy/setup.bash
colcon build --packages-select toy_robot_description
source install/setup.bash
ros2 launch toy_robot_description display.launch.xml
```

## Requirements

- ROS 2 Jazzy
- xacro, robot_state_publisher, joint_state_publisher_gui, rviz2
- nav2 (for the full toy_robot launch flow)

## Documentation

- [projects/toy_robot_ws/docs/index.md](projects/toy_robot_ws/docs/index.md) — documentation entry point
- [projects/toy_robot_ws/docs/development.md](projects/toy_robot_ws/docs/development.md) — build, launch, and test workflow
- [projects/toy_robot_ws/docs/architecture.md](projects/toy_robot_ws/docs/architecture.md) — runtime architecture and data flow
- [projects/toy_robot_ws/docs/rviz_debug.md](projects/toy_robot_ws/docs/rviz_debug.md) — marker semantics and troubleshooting
- [projects/toy_robot_ws/src/toy_robot_description/urdf/README.md](projects/toy_robot_ws/src/toy_robot_description/urdf/README.md) — URDF/xacro modularization and dimension dependencies
