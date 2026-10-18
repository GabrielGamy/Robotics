# Development Workflow

This guide contains build, launch, run, and test commands for daily development.

## Build And Reload

```bash
cd ~/Robotics/projects/toy_robot_ws
colcon build --packages-select toy_robot --symlink-install
source install/setup.bash
```

Notes:

1. In every new terminal, run `source install/setup.bash` again.
2. After changes to `setup.py`, `package.xml`, launch/config files, or node entry points, rebuild and source again.
3. `--symlink-install` is recommended in development.

## Launch The Project

```bash
cd ~/Robotics/projects/toy_robot_ws
source install/setup.bash
ros2 launch toy_robot robot.launch.xml
```

## Launch With Custom Configuration

```bash
# Option 1: use default config file
ros2 launch toy_robot robot.launch.xml

# Option 2: override using a custom config file
cp src/toy_robot/config/robot_config.yaml /tmp/robot_config_custom.yaml
# Edit values under brain_node.ros__parameters (for example box_x and box_y)
ros2 launch toy_robot robot.launch.xml config_file:=/tmp/robot_config_custom.yaml
```

## Optional: TurtleBot3 Nav2 Simulation

```bash
export RMW_FASTRTPS_TRANSPORT=udp
export TURTLEBOT3_MODEL=burger
ros2 launch nav2_bringup tb3_simulation_launch.py slam:=True
```

## Run Individual Nodes

Brain node:

```bash
cd ~/Robotics/projects/toy_robot_ws
source install/setup.bash
ros2 run toy_robot brain_node
```

Perception node:

```bash
cd ~/Robotics/projects/toy_robot_ws
source install/setup.bash
ros2 run toy_robot perception_node
```

## Run Tests

All package tests:

```bash
cd ~/Robotics/projects/toy_robot_ws
colcon test --packages-select toy_robot
colcon test-result --verbose
```

Targeted pytest examples:

```bash
cd ~/Robotics/projects/toy_robot_ws/src/toy_robot
python3 -m pytest test/test_brain_controller.py -v
python3 -m pytest test/test_brain_controller.py test/test_marker_visualizer.py -v
```
