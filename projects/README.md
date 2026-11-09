# Projects

This repository is organized as a multi-project workspace for ROS 2 robotics experiments and demos.

## Layout

```text
Robotics/
├── README.md
├── docs/
├── images/
├── projects/
│   ├── differential_drive_ws/
│   ├── differential_drive_gazebo_baseline_ws/
│   ├── differential_drive_gazebo_ros2_control_baseline_ws/
│   └── toy_robot_ws/
└── .gitignore
```

## Projects

- [differential_drive_ws/](differential_drive_ws/) — differential-drive robot with Gazebo simulation, ros2_control, SLAM, AMCL localization, and Nav2 navigation. See the [SLAM runbook and screenshots](../docs/differential_drive_slam_runbook.md).
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

- Keep each robot or experiment in its own workspace under `projects/`.
- Root-level docs and support scripts remain shared across projects.
- Project-specific build, install, and launch commands live in the workspace itself.
