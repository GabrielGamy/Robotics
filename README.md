# Robotics

A multi-project repository for ROS 2 robotics experiments, robot demos, and simulation work.

## Repository layout

The repo is now organized around independent projects rather than a single monolithic workspace:

```text
Robotics/
├── README.md
├── docs/
├── projects/
│   ├── toy_robot_ws/
│   ├── arm_demo_ws/
│   ├── mobile_base_ws/
│   └── ...
├── scripts/
├── shared/
└── .gitignore
```

## Projects

- [projects/toy_robot_ws/](projects/toy_robot_ws/) — the current ROS 2 toy robot workspace
  - `toy_robot_description`: modular URDF/xacro robot description
  - `toy_robot_interfaces`: custom ROS 2 interfaces
  - `toy_robot`: behavior, perception, navigation, and debugging logic

See [projects/toy_robot_ws/README.md](projects/toy_robot_ws/README.md) for the project-specific build and launch instructions.

## Design goals

- keep each robot or experiment in its own workspace
- avoid cross-project package collisions
- make new robotic efforts easy to add without reworking the repo
- keep shared docs and scripts separate from project-specific ROS packages

## Current project quick start

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

## Documentation

- [projects/toy_robot_ws/docs/index.md](projects/toy_robot_ws/docs/index.md)
- [projects/toy_robot_ws/docs/development.md](projects/toy_robot_ws/docs/development.md)
- [projects/toy_robot_ws/docs/architecture.md](projects/toy_robot_ws/docs/architecture.md)
- [projects/toy_robot_ws/docs/rviz_debug.md](projects/toy_robot_ws/docs/rviz_debug.md)
- [projects/toy_robot_ws/src/toy_robot_description/urdf/README.md](projects/toy_robot_ws/src/toy_robot_description/urdf/README.md)
