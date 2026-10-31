# Projects

This repository is organized as a multi-project workspace for ROS 2 robotics experiments and demos.

## Layout

```text
Robotics/
├── README.md
├── docs/
├── projects/
│   └── toy_robot_ws/
├── scripts/
├── shared/
└── .gitignore
```

## Current project

- [toy_robot_ws/](toy_robot_ws/) — active ROS 2 workspace for the toy robot

## Quick start

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
