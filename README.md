# Robotics

ROS 2 robotics projects and experiments.

## Repository layout

This repository is organized as a multi-project workspace:

```text
Robotics/
├── README.md
├── docs/
│   ├── differential_drive_ws/
│   └── toy_robot_ws/
├── images/
├── projects/
│   ├── differential_drive_ws/
│   ├── differential_drive_gazebo_baseline_ws/
│   ├── differential_drive_gazebo_ros2_control_baseline_ws/
│   └── toy_robot_ws/
└── .gitignore
```

Each ROS workspace keeps its own source packages and generated build, install, and log directories.

## Projects

### Differential-drive robot

[projects/differential_drive_ws/](projects/differential_drive_ws/) — differential-drive simulation, SLAM, localization, and Nav2 navigation with ROS 2 Jazzy and Gazebo Harmonic.

- `differential_drive_robot`: robot model, sensors, ros2_control configuration, EKF, worlds, maps, and RViz settings.
- `differential_drive_bringup`: XML launch files and Nav2 configuration for mapping and localization/navigation.
- The apartment world contains a bedroom and open living/dining area, with an SUV outside.
- Simulation currently uses Gazebo's ros2_control backend; physical hardware integration is not yet implemented.

See the [Differential Drive SLAM Runbook](docs/differential_drive_ws/differential_drive_slam_runbook.md) for environment setup, mapping, map saving, localization, and navigation commands.

#### Gazebo apartment simulation

![Differential-drive robot in the Gazebo apartment with a bedroom, living area, and SUV outside](images/differential_drive_ws%202026-11-09%2002-43-49.png)

#### RViz map visualization

![RViz showing the apartment occupancy map and differential-drive robot](images/differential_drive_ws%202026-11-09%2002-44-13.png)

### Toy robot

- [projects/toy_robot_ws/](projects/toy_robot_ws/) — ROS 2 workspace for the toy robot project
  - `toy_robot_description`: modular URDF/xacro robot model, Gazebo world, and launch files
  - `toy_robot_interfaces`: custom ROS 2 interfaces for runtime nodes
  - `toy_robot`: runtime behavior, perception, navigation, and visualization stack

See [projects/toy_robot_ws/README.md](projects/toy_robot_ws/README.md) for project-specific build and launch instructions.

## Toy Robot Quick Start

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
- Gazebo Harmonic, ros_gz, ros2_control, gz_ros2_control, robot_localization, SLAM Toolbox, and Nav2 for the differential-drive workspace
- xacro, robot_state_publisher, joint_state_publisher_gui, rviz2
- nav2 (for the full toy_robot launch flow)

## Documentation

- [Differential Drive SLAM Runbook](docs/differential_drive_ws/differential_drive_slam_runbook.md) — differential-drive simulation, mapping, localization, and navigation
- [Toy Robot Architecture](docs/toy_robot_ws/toy_robots-architecture.odt) — architecture document
- [projects/toy_robot_ws/docs/index.md](projects/toy_robot_ws/docs/index.md) — documentation entry point
- [projects/toy_robot_ws/docs/development.md](projects/toy_robot_ws/docs/development.md) — build, launch, and test workflow
- [projects/toy_robot_ws/docs/architecture.md](projects/toy_robot_ws/docs/architecture.md) — runtime architecture and data flow
- [projects/toy_robot_ws/docs/rviz_debug.md](projects/toy_robot_ws/docs/rviz_debug.md) — marker semantics and troubleshooting
- [projects/toy_robot_ws/src/toy_robot_description/urdf/README.md](projects/toy_robot_ws/src/toy_robot_description/urdf/README.md) — URDF/xacro modularization and dimension dependencies
