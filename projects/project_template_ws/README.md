# Project Template Workspace

This directory is the standard template for new ROS 2 robot projects in this repository.

## Purpose

Use this workspace as a starting point when creating a new robotics project. It gives each project a consistent layout, predictable package structure, and a repeatable quick-start workflow.

## Standard structure

```text
<project_name>_ws/
├── README.md
├── src/
│   ├── <package_1>/
│   ├── <package_2>/
│   └── ...
├── config/
├── launch/
├── docs/
├── build/
├── install/
├── log/
└── .gitignore
```

## Typical package pattern

```text
src/<package_name>/
├── package.xml
├── setup.py
├── CMakeLists.txt   # for C++ packages
├── config/
├── launch/
├── test/
├── <package_name>/
│   ├── __init__.py
│   ├── nodes/
│   ├── behavior/
│   ├── models/
│   ├── tf/
│   └── visualization/
```

## Typical workflow

```bash
cd <repo-root>/projects/<project_name>_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash
```

## Rules for new projects

- workspace name must end with `_ws`
- keep project packages isolated inside that workspace
- store project docs under the workspace `docs/` folder
- keep ROS config and launch files local to the project
- avoid mixing multiple unrelated robot projects in one workspace

## Recommended first package set

- `description` or `<robot>_description`
- `<robot>_interfaces`
- `<robot>_control` or `<robot>`

This keeps the structure aligned with the existing toy robot project in this repo.
