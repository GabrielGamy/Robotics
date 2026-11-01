# Simulation Validation Checklist

Use this checklist after changes to launch files, URDF, bridge mappings, or plugins.

## 1. Build

```bash
source /opt/ros/jazzy/setup.bash
cd /home/gabrielgamy/src/robotics/projects/differential_drive_ws
colcon build --symlink-install
source install/setup.bash
```

Expected: build completes without errors.

## 2. Start Simulation

```bash
ros2 launch differential_drive_robot sim.launch.xml
```

Expected:
- Gazebo starts.
- RViz starts (unless `rviz:=false`).
- Robot appears in Gazebo and RViz.

## 3. Check Core Topics

```bash
ros2 topic list | grep -E '^/clock$|^/joint_states$|^/tf$|^/tf_static$|^/odom$|^/cmd_vel$'
```

Expected topics present:
- `/clock`
- `/joint_states`
- `/tf`
- `/tf_static`
- `/odom`
- `/cmd_vel`

## 4. Drive the Robot

In another terminal:

```bash
source /opt/ros/jazzy/setup.bash
cd /home/gabrielgamy/src/robotics/projects/differential_drive_ws
source install/setup.bash
ros2 launch differential_drive_robot teleop.launch.xml
```

If terminal prefix is incompatible:

```bash
ros2 launch differential_drive_robot teleop.launch.xml terminal_prefix:="xfce4-terminal -e"
```

Fallback (direct run):

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Expected:
- Keyboard commands move robot in Gazebo.
- Wheels rotate in RViz.

## 5. Verify Odometry and Joint States

```bash
ros2 topic echo /odom --once
ros2 topic echo /joint_states --once
```

Expected:
- `/odom` publishes valid pose/twist data while moving.
- `/joint_states` publishes wheel joint names and changing positions/velocities.

## 6. Verify TF Tree

```bash
ros2 run tf2_tools view_frames
```

Expected frame connectivity includes:
- `odom -> base_footprint`
- `base_footprint -> base_link`
- `base_link -> left_wheel_link`
- `base_link -> right_wheel_link`

## Pass Criteria

Simulation is considered healthy when:
- Robot spawns correctly.
- `/cmd_vel` commands produce motion.
- `/odom`, `/joint_states`, and `/tf` update correctly.
- RViz shows moving wheel links without missing transform errors.
