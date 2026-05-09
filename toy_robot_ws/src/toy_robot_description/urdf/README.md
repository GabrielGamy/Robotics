# URDF and Xacro Guide

This folder contains the modular robot description for toy_robot_description.

## Files

- dimensions.xacro: single source of truth for shared dimensions, offsets, and masses.
- base_mobile.xacro: base_footprint and base_link.
- wheels.xacro: left/right drive wheels and front caster.
- camera.xacro: camera_link and camera_optical_frame.
- arm_6dof.xacro: 6-axis manipulator up to gripper_mount_link.
- gripper.xacro: palm, fingers, and tcp_link.
- gazebo_plugins.xacro: Gazebo materials, differential drive plugin, and camera sensor.
- toy_robot.urdf.xacro: top-level assembly with includes.

## Include Order

The top-level file includes modules in this order:

1. dimensions.xacro
2. base_mobile.xacro
3. wheels.xacro
4. camera.xacro
5. arm_6dof.xacro
6. gripper.xacro
7. gazebo_plugins.xacro

Keep this order so every module sees the required global properties.

## Parameter Dependencies

Key cross-module dependencies:

- camera_mount_x uses base_radius
- camera_mount_z uses base_height
- arm_mount_x uses base_radius
- arm_mount_z uses base_height
- tcp_joint z uses palm_z + finger_z

This means changing base dimensions automatically moves camera and arm mounting points.

## How To Modify Geometry Safely

1. Edit values only in dimensions.xacro.
2. Keep formulas in module files (avoid reintroducing hard-coded numbers).
3. Build after each change.
4. Validate in RViz using display.launch.xml.

## Build and Launch

### RViz visualization

```bash
cd /home/gabrielgamy/src/robotics/toy_robot_ws
source /opt/ros/jazzy/setup.bash
colcon build --packages-select toy_robot_description
source install/setup.bash
ros2 launch toy_robot_description display.launch.xml
```

### Gazebo simulation

```bash
cd /home/gabrielgamy/src/robotics/toy_robot_ws
source /opt/ros/jazzy/setup.bash
colcon build --packages-select toy_robot_description
source install/setup.bash
ros2 launch toy_robot_description gazebo.launch.xml
```

Without RViz:

```bash
ros2 launch toy_robot_description gazebo.launch.xml rviz:=false
```

## Notes

- Avoid using ':' in XML comments to prevent ROS launch YAML parsing issues.
- Keep inertial origins aligned with visual/collision origins when scaling links.
