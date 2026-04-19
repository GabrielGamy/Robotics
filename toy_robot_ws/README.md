# Toy Robot Workspace (ROS 2)

This workspace contains the `toy_robot` ROS 2 package.

## Quick Start

Build, source, and launch:

```bash
cd /home/gabrielgamy/src/robotics/toy_robot_ws
colcon build --packages-select toy_robot --symlink-install
source install/setup.bash
ros2 launch toy_robot robot.launch.xml
```

## Documentation

Detailed references are in the `docs/` folder:

1. `docs/index.md`: entry point for all documentation.
2. `docs/development.md`: build, launch, run, and test commands.
3. `docs/architecture.md`: architecture, responsibilities, and data flow.
4. `docs/rviz_debug.md`: RViz setup, marker semantics, and debug checklist.

## Project Structure

Main workspace layout:

```text
toy_robot_ws/
├── docs/
├── src/
│   └── toy_robot/
│       ├── config/
│       ├── launch/
│       ├── test/
│       └── toy_robot/
│           ├── behavior/
│           ├── models/
│           ├── tf/
│           ├── visualization/
│           ├── brain_node.py
│           └── perception_node.py
├── build/
├── install/
└── log/
```

Code organization:

- `toy_robot/brain_node.py`: ROS 2 node that subscribes to detections, handles navigation goals, and connects ROS interfaces to the behavior layer.
- `toy_robot/perception_node.py`: simple perception simulator publishing detected object positions.
- `toy_robot/behavior/brain_controller.py`: pure state-machine logic for the robot behavior.
- `toy_robot/models/target.py`: data model for a detected target.
- `toy_robot/tf/transformer.py`: helper for TF coordinate transformations.
- `toy_robot/visualization/marker_visualizer.py`: RViz marker publisher for target/goal debug visualization.
- `launch/robot.launch.xml`: XML launch file to start the system.
- `config/robot_config.yaml`: runtime configuration values.
- `test/test_brain_controller.py`: unit tests for the behavior logic.
- `docs/`: dedicated detailed documentation and guides.