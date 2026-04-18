# Toy Robot Workspace (ROS 2)

This workspace contains the `toy_robot` ROS 2 package.

## Build And Run Workflow

After each code change, use this workflow:

1. Save the file.
2. Rebuild the package.
3. Reload the environment.
4. Restart the node you want to test.

Commands:

```bash
cd /home/gabrielgamy/src/robotics/toy_robot_ws
colcon build --packages-select toy_robot --symlink-install
source install/setup.bash
```

Notes:

- Open a new terminal: run `source install/setup.bash` again.
- If you modify `setup.py`, `package.xml`, add a new node, or add launch/config files, rebuild and source again.
- `--symlink-install` is recommended during development so Python source changes are reflected more easily.

## Launch The Project

Launch the full toy robot stack:

```bash
cd /home/gabrielgamy/src/robotics/toy_robot_ws
source install/setup.bash
ros2 launch toy_robot robot.launch.xml
```

Launch with custom box coordinates:

```bash
# Option 1: use the default config file
ros2 launch toy_robot robot.launch.xml

# Option 2: launch with a custom config file (recommended)
# Create a copy and change:
# brain_node.ros__parameters.box_x
# brain_node.ros__parameters.box_y
cp src/toy_robot/config/robot_config.yaml /tmp/robot_config_custom.yaml
ros2 launch toy_robot robot.launch.xml config_file:=/tmp/robot_config_custom.yaml
```

If you are using TurtleBot3 with Nav2 simulation, start the simulation stack separately:

```bash
export RMW_FASTRTPS_TRANSPORT=udp
export TURTLEBOT3_MODEL=burger
ros2 launch nav2_bringup tb3_simulation_launch.py slam:=True
```

## Run Individual Nodes

Run the brain node:

```bash
cd /home/gabrielgamy/src/robotics/toy_robot_ws
source install/setup.bash
ros2 run toy_robot brain_node
```

Run the perception node:

```bash
cd /home/gabrielgamy/src/robotics/toy_robot_ws
source install/setup.bash
ros2 run toy_robot perception_node
```

## Run Tests

Run all tests for the package:

```bash
cd /home/gabrielgamy/src/robotics/toy_robot_ws
colcon test --packages-select toy_robot
colcon test-result --verbose
```

Run the Python unit tests directly with pytest:

```bash
cd /home/gabrielgamy/src/robotics/toy_robot_ws/src/toy_robot
python3 -m pytest test/test_brain_controller.py -v
```

## Documentation

Detailed design and debugging references are in the dedicated docs folder:

- `docs/architecture.md`: architecture, responsibilities, and data flow.
- `docs/rviz_debug.md`: RViz setup, marker semantics, and debug checklist.

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
- `docs/architecture.md`: architecture and separation-of-concerns documentation.
- `docs/rviz_debug.md`: RViz visualization setup and troubleshooting guide.

## Current Behavior Summary

The project currently follows this simplified flow:

1. `perception_node` publishes a detected object position.
2. `brain_node` transforms the point into the `map` frame.
3. The behavior controller switches from `SEARCHING` to `GO_TO_OBJECT`.
4. The brain sends a `NavigateToPose` goal.
5. After navigation completes, the robot simulates pick, go-to-box, and drop transitions.