# Projects

This repository is organized as a multi-project workspace for ROS 2 robotics experiments, embedded firmware, and demos.

## Table of Contents

- [Layout](#layout)
- [Projects](#projects-1)
- [Toy robot quick start](#toy-robot-quick-start)
- [Notes](#notes)

## Layout

```text
Robotics/
├── README.md
├── docs/
│   ├── differential_drive_ws/
│   └── toy_robot_ws/
├── images/
├── projects/
│   ├── differential_drive_esp32/
│   ├── differential_drive_ws/
│   ├── differential_drive_gazebo_baseline_ws/
│   ├── differential_drive_gazebo_ros2_control_baseline_ws/
│   └── toy_robot_ws/
└── .gitignore
```

## Projects

- [differential_drive_ws/](differential_drive_ws/) — differential-drive robot with Gazebo simulation, ros2_control, SLAM, AMCL localization, and Nav2 navigation. See the [SLAM runbook and screenshots](../docs/differential_drive_ws/differential_drive_slam_runbook.md).
- [differential_drive_esp32/](differential_drive_esp32/) — PlatformIO/Arduino firmware project for the physical differential-drive robot's ESP32. Currently a USB/serial bring-up test; motor control and ROS 2 hardware integration are not yet implemented. See the [ESP32 + MDD10A hardware guide](../docs/differential_drive_ws/ESP32_MDD10A_HARDWARE_GUIDE.md) and [hardware plan](../docs/differential_drive_ws/HARDWARE.md).
- [differential_drive_gazebo_baseline_ws/](differential_drive_gazebo_baseline_ws/) — Gazebo baseline workspace.
- [differential_drive_gazebo_ros2_control_baseline_ws/](differential_drive_gazebo_ros2_control_baseline_ws/) — Gazebo/ros2_control baseline workspace.
- [toy_robot_ws/](toy_robot_ws/) — ROS 2 workspace for the toy robot.

## Toy robot quick start

```bash
cd ~/Robotics/projects/toy_robot_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash
ros2 launch toy_robot robot.launch.xml
```

## Notes

- Keep each robot or experiment in its own workspace or firmware project under `projects/`.
- Repository-level project documentation lives in `docs/<workspace_name>/`; support scripts remain shared across projects.
- Project-specific build, install, and launch commands live in the workspace itself.
