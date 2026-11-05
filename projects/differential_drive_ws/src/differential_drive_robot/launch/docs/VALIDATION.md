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
ros2 topic list | grep -E '^/clock$|^/joint_states$|^/tf$|^/tf_static$|^/diff_drive_controller/cmd_vel$|^/diff_drive_controller/odom$|^/odom$'
```

Expected topics present:
- `/clock`
- `/joint_states`
- `/tf`
- `/tf_static`
- `/diff_drive_controller/cmd_vel`
- `/diff_drive_controller/odom`
- `/odom`

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
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -p stamped:=true -p frame_id:=base_link -r /cmd_vel:=/diff_drive_controller/cmd_vel
```

Expected:
- Keyboard commands move robot in Gazebo.
- Wheels rotate in RViz.

## 5. Verify Odometry and Joint States

```bash
ros2 topic echo /diff_drive_controller/odom --once
ros2 topic echo /odom --once
ros2 topic echo /joint_states --once
```

Expected:
- `/diff_drive_controller/odom` publishes valid pose/twist data while moving.
- `/odom` mirrors controller odometry for compatibility.
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

## 7. Verify IMU Bridge

```bash
ros2 topic info /imu/data
ros2 topic echo /imu/data --once
```

Expected:
- `/imu/data` type is `sensor_msgs/msg/Imu`.
- Publisher count is at least 1.
- A message is received with non-empty `header.frame_id` and populated angular velocity / linear acceleration values.

## 8. Verify LiDAR Bridge

```bash
ros2 topic info /scan
ros2 topic echo /scan --once
```

Expected:
- `/scan` type is `sensor_msgs/msg/LaserScan`.
- Publisher count is at least 1.
- A message is received with finite `range_min` / `range_max` and populated `ranges`.

## 9. LiDAR Tuning Pass (Balanced Profile)

Current tuned profile in simulation:
- Horizontal FOV: 270 deg (`min_angle=-2.35619`, `max_angle=2.35619`)
- Samples: `720`
- Range: `0.15 m` to `8.0 m`
- Update rate: `12 Hz`
- Gaussian noise stddev: `0.01 m`

Quick checks:

```bash
ros2 topic hz /scan
ros2 topic echo /scan --once
```

Expected:
- `/scan` frequency is around 12 Hz (typically about 10 to 12 Hz under normal simulator load).
- `angle_min` / `angle_max` reflect a 270 deg scan.
- `range_min` / `range_max` are `0.15` and `8.0`.
- `ranges` values show small realistic jitter from noise, without NaN-only output.

## 10. LiDAR Profile Comparison (Balanced vs Light)

Run balanced profile (default):

```bash
ros2 launch differential_drive_robot sim.launch.xml rviz:=false lidar_profile:=balanced
```

In another terminal:

```bash
source /opt/ros/jazzy/setup.bash
cd /home/gabrielgamy/src/robotics/projects/differential_drive_ws
source install/setup.bash
ros2 topic hz /scan
ros2 topic echo /scan --once
```

Then run light profile:

```bash
ros2 launch differential_drive_robot sim.launch.xml rviz:=false lidar_profile:=light
```

Expected profile deltas:
- `balanced`: ~270 deg, 720 samples, 0.15 m to 8.0 m, target 12 Hz.
- `light`: ~180 deg, 360 samples, 0.20 m to 6.0 m, target 10 Hz.
- Light profile should reduce sensor cost while keeping stable `/scan` publication.

## Pass Criteria

Simulation is considered healthy when:
- Robot spawns correctly.
- `/cmd_vel` commands produce motion.
- `/diff_drive_controller/cmd_vel` commands produce motion.
- `/diff_drive_controller/odom`, `/odom`, `/joint_states`, and `/tf` update correctly.
- `/imu/data` publishes `sensor_msgs/msg/Imu` messages.
- `/scan` publishes `sensor_msgs/msg/LaserScan` messages.
- RViz shows moving wheel links without missing transform errors.
