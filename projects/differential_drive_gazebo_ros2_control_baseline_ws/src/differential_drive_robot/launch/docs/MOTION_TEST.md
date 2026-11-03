# Motion Test Profiles

Use these tests to validate RC6 behavior, wheel motion, and odometry consistency.

## Prerequisites

Terminal A (simulation):

```bash
source /opt/ros/jazzy/setup.bash
cd /home/gabrielgamy/src/robotics/projects/differential_drive_gazebo_ros2_control_baseline_ws
source install/setup.bash
ros2 launch differential_drive_robot sim.launch.xml
```

Terminal B (monitor):

```bash
source /opt/ros/jazzy/setup.bash
cd /home/gabrielgamy/src/robotics/projects/differential_drive_gazebo_ros2_control_baseline_ws
source install/setup.bash
ros2 topic echo /odom
```

Terminal C (commands):

```bash
source /opt/ros/jazzy/setup.bash
cd /home/gabrielgamy/src/robotics/projects/differential_drive_gazebo_ros2_control_baseline_ws
source install/setup.bash
```

## Test 1: Forward Motion (3s)

```bash
ros2 topic pub -r 10 /diff_drive_controller/cmd_vel geometry_msgs/msg/TwistStamped "{header: {frame_id: 'base_link'}, twist: {linear: {x: 0.30}, angular: {z: 0.0}}}"
```

Run for about 3 seconds, then stop with `Ctrl+C` and publish stop:

```bash
ros2 topic pub --once /diff_drive_controller/cmd_vel geometry_msgs/msg/TwistStamped "{header: {frame_id: 'base_link'}, twist: {linear: {x: 0.0}, angular: {z: 0.0}}}"
```

Expected:
- Robot moves straight forward.
- `/odom` linear.x is positive during motion.

## Test 2: In-Place Rotation (3s)

```bash
ros2 topic pub -r 10 /diff_drive_controller/cmd_vel geometry_msgs/msg/TwistStamped "{header: {frame_id: 'base_link'}, twist: {linear: {x: 0.0}, angular: {z: 0.6}}}"
```

Stop the same way:

```bash
ros2 topic pub --once /diff_drive_controller/cmd_vel geometry_msgs/msg/TwistStamped "{header: {frame_id: 'base_link'}, twist: {linear: {x: 0.0}, angular: {z: 0.0}}}"
```

Expected:
- Robot rotates in place.
- `/odom` angular.z is positive during rotation.

## Test 3: Arc Trajectory (4s)

```bash
ros2 topic pub -r 10 /diff_drive_controller/cmd_vel geometry_msgs/msg/TwistStamped "{header: {frame_id: 'base_link'}, twist: {linear: {x: 0.20}, angular: {z: 0.35}}}"
```

Stop afterward:

```bash
ros2 topic pub --once /diff_drive_controller/cmd_vel geometry_msgs/msg/TwistStamped "{header: {frame_id: 'base_link'}, twist: {linear: {x: 0.0}, angular: {z: 0.0}}}"
```

Expected:
- Robot follows a smooth curve.
- `/odom` shows both linear and angular components.

## Optional Quick Health Checks

```bash
ros2 topic echo /joint_states --once
ros2 topic echo /odom --once
ros2 topic list | grep -E '^/diff_drive_controller/cmd_vel$|^/diff_drive_controller/odom$|^/odom$|^/joint_states$|^/tf$'
```

## Pass Criteria

- Robot responds quickly to `/diff_drive_controller/cmd_vel`.
- Motion direction matches command sign.
- Stop command reliably halts the robot.
- `/odom` and `/joint_states` update continuously while moving.
