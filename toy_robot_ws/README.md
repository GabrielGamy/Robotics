# Toy Robot Workspace (ROS 2 Jazzy)

This workspace contains three ROS 2 packages:

1. toy_robot_description: modular URDF/xacro robot model.
2. toy_robot_interfaces: custom interfaces used by runtime behavior nodes.
3. toy_robot: behavior/control stack with perception simulation, state machine, TF transform helpers, Nav2 actions, and RViz debug markers.

## Quick Start

Build all packages, source, and launch the full runtime stack:

```bash
cd /home/gabrielgamy/src/robotics/toy_robot_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash
ros2 launch toy_robot robot.launch.xml
```

URDF-only RViz visualization:

```bash
cd /home/gabrielgamy/src/robotics/toy_robot_ws
source /opt/ros/jazzy/setup.bash
colcon build --packages-select toy_robot_description
source install/setup.bash
ros2 launch toy_robot_description display.launch.xml
```

## Detailed Documentation

The docs folder contains implementation and operations details for the runtime stack:

1. docs/index.md: documentation entry point.
2. docs/development.md: build, launch, run, and test commands.
3. docs/architecture.md: component responsibilities and data flow.
4. docs/rviz_debug.md: RViz marker semantics and troubleshooting.
5. docs/simulation_validation_commands.md: simulation validation commands used for Gazebo, RViz, TF, camera, and teleop checks.

## URDF Documentation

The detailed URDF guide is in:

- src/toy_robot_description/urdf/README.md

This guide explains:

- file modularization
- global parameter system in dimensions.xacro
- dependencies between base, camera, arm, and gripper dimensions
- safe workflow for geometry updates

## Package Structure

```text
toy_robot_ws/src/
├── toy_robot/
│   ├── config/
│   ├── launch/
│   ├── test/
│   └── toy_robot/
│       ├── behavior/
│       ├── models/
│       ├── tf/
│       ├── visualization/
│       ├── brain_node.py
│       └── perception_node.py
├── toy_robot_description/
│   ├── launch/
│   ├── meshes/
│   ├── rviz/
│   └── urdf/
└── toy_robot_interfaces/
```

## Core Runtime Files

- src/toy_robot/toy_robot/brain_node.py: ROS interface node, Nav2 actions, and behavior orchestration.
- src/toy_robot/toy_robot/perception_node.py: simulated detections publisher.
- src/toy_robot/toy_robot/behavior/brain_controller.py: pure state-machine logic.
- src/toy_robot/toy_robot/tf/transformer.py: frame transform and pose/yaw helpers.
- src/toy_robot/toy_robot/visualization/marker_visualizer.py: RViz marker publisher.
- src/toy_robot/launch/robot.launch.xml: launch entrypoint.
- src/toy_robot/config/robot_config.yaml: runtime parameters.
- src/toy_robot_interfaces: custom message/action/service definitions.

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