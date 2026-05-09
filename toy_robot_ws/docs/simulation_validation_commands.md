# Simulation Validation Commands

This guide is a quick reference for the commands used to validate the robot in Gazebo and RViz.

## 0) Workspace Setup

Use in each new terminal:

```bash
cd /home/gabrielgamy/src/robotics/toy_robot_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
```

Build after description/launch/world changes:

```bash
colcon build --packages-select toy_robot_description
source install/setup.bash
```

## 1) Launch Simulation

Launch Gazebo + robot + bridge + RViz:

```bash
ros2 launch toy_robot_description gazebo.launch.xml
```

Launch without RViz:

```bash
ros2 launch toy_robot_description gazebo.launch.xml rviz:=false
```

## 2) Motion Check (/cmd_vel)

Publish forward velocity continuously:

```bash
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.0}}"
```

Send a stop command once:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0}, angular: {z: 0.0}}"
```

Inspect command topic details:

```bash
ros2 topic info /cmd_vel
```

## 3) Odometry Check (/odom)

Echo odometry:

```bash
ros2 topic echo /odom
```

Expected: changing pose and orientation while robot moves.

## 4) TF Check

Generate TF graph (PDF):

```bash
ros2 run tf2_tools view_frames
```

Open latest generated PDF:

```bash
xdg-open "$(ls -t frames_*.pdf | head -1)"
```

Expected chain:

- odom -> base_footprint -> base_link

## 5) Camera Check

List camera/image topics:

```bash
ros2 topic list | grep -E "camera|image"
```

Check ROS camera publisher details:

```bash
ros2 topic info /camera/image_raw -v
```

Get one ROS image message:

```bash
ros2 topic echo --once /camera/image_raw
```

Check camera rate from ROS side:

```bash
ros2 topic hz /camera/image_raw
```

Check camera topics from Gazebo side:

```bash
gz topic -l | grep camera
```

Echo Gazebo camera stream:

```bash
gz topic -e -t /camera/image_raw
```

Visual check in GUI:

```bash
ros2 run rqt_image_view rqt_image_view
```

Then select `/camera/image_raw` in the topic dropdown.

## 6) Keyboard Teleop

Run keyboard teleop:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Common keys:

- i: forward
- ,: backward
- j: rotate left
- l: rotate right
- k: stop
- u: forward + left

## 7) Typical Validation Order

1. Launch simulation
2. Validate /cmd_vel motion
3. Validate /odom
4. Validate TF chain
5. Validate camera topics and image stream
6. Validate keyboard teleop

## 8) Quick Troubleshooting Notes

- If robot moves in Gazebo but looks static in RViz:
  set RViz Fixed Frame to `odom` (not `base_footprint`).
- If `/camera/image_raw` exists but no messages are received:
  verify Gazebo camera stream first with `gz topic -e -t /camera/image_raw`.
- If Gazebo world fails because of missing `model://...` URIs:
  use a world file that does not depend on unavailable remote models.
