# Differential Drive SLAM Runbook

Command-first runbook for mapping and localization with ROS 2 Jazzy, Gazebo, and SLAM Toolbox.

- **Workspace:** `/home/gabrielgamy/src/robotics/projects/differential_drive_ws`
- **ROS distribution:** Jazzy

## Environment Setup

Run this in every new terminal before using workspace ROS commands:

```bash
source /opt/ros/jazzy/setup.bash
source /home/gabrielgamy/src/robotics/projects/differential_drive_ws/install/setup.bash
```

For a clean launch terminal:

```bash
cd /home/gabrielgamy/src/robotics/projects/differential_drive_ws
unset AMENT_PREFIX_PATH CMAKE_PREFIX_PATH COLCON_PREFIX_PATH LD_LIBRARY_PATH
source /opt/ros/jazzy/setup.bash
source install/setup.bash
```

---

# Mapping

Use this workflow to explore the apartment with the LiDAR and build a new occupancy map.

The basic pipeline is:

```text
LiDAR /scan
     +
Odometry / TF
     ↓
SLAM Toolbox
     ↓
   /map
     ↓
slam_map.yaml + slam_map.pgm
```

## 1. Launch Simulation + SLAM + RViz

```bash
cd /home/gabrielgamy/src/robotics/projects/differential_drive_ws
unset AMENT_PREFIX_PATH CMAKE_PREFIX_PATH COLCON_PREFIX_PATH LD_LIBRARY_PATH
source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 launch differential_drive_bringup slam_mapping.launch.xml \
  world_name:=apartment \
  rviz:=true
```

Without RViz:

```bash
ros2 launch differential_drive_bringup slam_mapping.launch.xml \
  world_name:=apartment \
  rviz:=false
```

## 2. Drive the Robot

Open another terminal:

```bash
source /opt/ros/jazzy/setup.bash
source /home/gabrielgamy/src/robotics/projects/differential_drive_ws/install/setup.bash

ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args \
  -p stamped:=true \
  -p frame_id:=base_footprint \
  --remap cmd_vel:=/diff_drive_controller/cmd_vel
```

Drive slowly through the apartment and cover all rooms and hallways.

In RViz, verify that `/map` expands as new areas are observed by the LiDAR.

## 3. Save the Occupancy Map

Once the apartment has been sufficiently mapped:

```bash
source /opt/ros/jazzy/setup.bash
source /home/gabrielgamy/src/robotics/projects/differential_drive_ws/install/setup.bash

ros2 run nav2_map_server map_saver_cli \
  -f /home/gabrielgamy/src/robotics/projects/differential_drive_ws/src/differential_drive_robot/maps/slam_map
```

This creates:

```text
maps/
├── slam_map.yaml
└── slam_map.pgm
```

These files represent the saved occupancy map:

- `slam_map.pgm` — occupancy-grid image.
- `slam_map.yaml` — map metadata such as resolution, origin, and image path.

## 4. Save the SLAM Toolbox Pose Graph

If SLAM Toolbox pose-graph localization or continued SLAM will be used, also serialize the pose graph:

```bash
source /opt/ros/jazzy/setup.bash
source /home/gabrielgamy/src/robotics/projects/differential_drive_ws/install/setup.bash

ros2 service call /slam_toolbox/serialize_map \
  slam_toolbox/srv/SerializePoseGraph \
  "{filename: '/home/gabrielgamy/src/robotics/projects/differential_drive_ws/src/differential_drive_robot/maps/slam_posegraph'}"
```

## 5. Continue Mapping an Existing Map

Use this workflow when you want to load a previously saved SLAM Toolbox pose graph and extend it with new exploration.

Note: continuing SLAM requires the pose graph artifact (`slam_posegraph`), not only `slam_map.yaml` and `slam_map.pgm`.

### 1. Launch SLAM Mapping

```bash
cd /home/gabrielgamy/src/robotics/projects/differential_drive_ws
unset AMENT_PREFIX_PATH CMAKE_PREFIX_PATH COLCON_PREFIX_PATH LD_LIBRARY_PATH
source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 launch differential_drive_bringup slam_mapping.launch.xml \
  world_name:=apartment \
  rviz:=true
```

### 2. Deserialize the Previous Pose Graph

In a second terminal:

```bash
source /opt/ros/jazzy/setup.bash
source /home/gabrielgamy/src/robotics/projects/differential_drive_ws/install/setup.bash

ros2 service call /slam_toolbox/deserialize_map \
  slam_toolbox/srv/DeserializePoseGraph \
  "{filename: '/home/gabrielgamy/src/robotics/projects/differential_drive_ws/src/differential_drive_robot/maps/slam_posegraph'}"
```

### 3. Continue Driving and Extend Coverage

Use teleop as in the mapping section and drive into regions that were not fully covered before.

### 4. Re-save the Updated Map and Pose Graph

Save the updated occupancy map:

```bash
ros2 run nav2_map_server map_saver_cli \
  -f /home/gabrielgamy/src/robotics/projects/differential_drive_ws/src/differential_drive_robot/maps/slam_map
```

Re-serialize the updated pose graph:

```bash
ros2 service call /slam_toolbox/serialize_map \
  slam_toolbox/srv/SerializePoseGraph \
  "{filename: '/home/gabrielgamy/src/robotics/projects/differential_drive_ws/src/differential_drive_robot/maps/slam_posegraph'}"
```

### Occupancy Map vs. Pose Graph

These are two different artifacts:

```text
slam_map.yaml + slam_map.pgm
        │
        └── Final 2D occupancy map


slam_posegraph
        │
        └── SLAM Toolbox pose graph
            containing the SLAM graph information
```

The occupancy map is the format used by the standard `map_server` workflow.

The pose graph can be reloaded by SLAM Toolbox for workflows such as pose-graph localization or continued SLAM.

---

# Mapping Validation

These checks are useful if mapping does not behave as expected.

## Verify `/map`

```bash
ros2 topic info /map -v
```

To receive one occupancy-grid message:

```bash
timeout 12s ros2 topic echo /map \
  nav_msgs/msg/OccupancyGrid \
  --qos-reliability reliable \
  --qos-durability transient_local \
  --once
```

## Verify `map -> odom`

```bash
timeout 6s ros2 run tf2_ros tf2_echo map odom
```

During active SLAM, SLAM Toolbox should provide the relationship between the map and odometry frames.

---

# Localization

Mapping answers:

> What does the environment look like, and where am I while building it?

Localization answers:

> I already have a map. Where am I on that map?

Two localization workflows may exist in this project.

## Localization Option A — SLAM Toolbox Pose Graph

This workflow reloads the serialized SLAM Toolbox pose graph.

### 1. Configure the Pose Graph

Edit:

```text
src/differential_drive_robot/config/slam_toolbox_localization.yaml
```

Set:

```yaml
map_file_name: /home/gabrielgamy/src/robotics/projects/differential_drive_ws/src/differential_drive_robot/maps/slam_posegraph
```

### 2. Launch Pose-Graph Localization

```bash
cd /home/gabrielgamy/src/robotics/projects/differential_drive_ws
unset AMENT_PREFIX_PATH CMAKE_PREFIX_PATH COLCON_PREFIX_PATH LD_LIBRARY_PATH
source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 launch differential_drive_bringup \
  slam_localization_posegraph.launch.xml \
  world_name:=apartment \
  rviz:=true
```

### 3. Set the Initial Robot Pose

In RViz:

1. Select `2D Pose Estimate`.
2. Click approximately where the robot is located on the map.
3. Drag the arrow in the direction the robot is facing.

Then move the robot and verify that localization follows its movement.

## Localization Option B — Occupancy Map + AMCL

This is the standard Nav2-style localization workflow:

```text
slam_map.yaml + slam_map.pgm
             ↓
         map_server
             ↓
           /map
             │
             + /scan
             ↓
            AMCL
             ↓
        map -> odom
```

This workflow uses the occupancy map saved during mapping rather than the SLAM Toolbox pose graph.

Use this workflow when integrating the robot with the standard Nav2 localization stack.

---

# Localization Validation

## Verify the Localization Node

For SLAM Toolbox pose-graph localization:

```bash
ros2 node list
```

Verify that `/slam_toolbox` exists.

Then:

```bash
ros2 param get /slam_toolbox mode
```

## Verify the Map

```bash
ros2 topic echo /map --once
```

## Verify RViz `2D Pose Estimate`

Run:

```bash
ros2 topic echo /initialpose --once
```

Then click `2D Pose Estimate` in RViz and set the robot pose.

A message should appear on `/initialpose`.

## Verify the Robot Transform

```bash
ros2 run tf2_ros tf2_echo map base_footprint
```

After setting the initial pose and moving the robot, the transform should update consistently with the robot's movement.

---

# Troubleshooting

## Localization Does Not React to `2D Pose Estimate`

First verify:

```bash
ros2 topic echo /initialpose --once
```

Then use `2D Pose Estimate` in RViz.

If no message arrives, investigate the RViz pose tool or `/initialpose` topic configuration.

## `/slam_toolbox` Node Is Missing

Check:

```bash
ros2 node list
```

If `/slam_toolbox` is missing, inspect the localization launch terminal for startup or configuration errors.

## `map -> base_footprint` Appears Static

Check:

```bash
ros2 run tf2_ros tf2_echo map base_footprint
```

If the transform exists but remains constant, move the robot inside the mapped area before assuming localization is broken.

## `Invalid frame ID "map"` During Startup

A brief TF error during startup can occur before the localization or SLAM node begins publishing the `map` transform.

If the transform becomes available shortly afterward, the initial message can generally be ignored.

Verify with:

```bash
ros2 run tf2_ros tf2_echo map base_footprint
```

## Stale ROS/Gazebo Processes

If the launch behaves inconsistently, stop stale processes:

```bash
pkill -9 -f "ros2|gz sim|ros_gz|controller_manager|spawner|robot_state_publisher|ekf_node|slam_toolbox|teleop_twist_keyboard|rviz2" || true
```

Then start the stack again from a clean terminal.

## DDS Shared-Memory Lock Errors

If `RTPS_TRANSPORT_SHM` or Fast DDS shared-memory lock errors appear after processes have been stopped:

```bash
rm -f /dev/shm/fastrtps_port* /dev/shm/fastdds* 2>/dev/null || true
```

Then restart the ROS stack.

---

# Stop the Stack

Normally, stop the launch with:

```text
Ctrl+C
```

in the launch terminal.

If Gazebo, ROS, or RViz processes remain stuck:

```bash
pkill -9 -f "gz sim|ros_gz_bridge|controller_manager|spawner|robot_state_publisher|ekf_node|slam_toolbox|teleop_twist_keyboard|rviz2" || true
```

Only clear DDS shared-memory files if related errors persist:

```bash
rm -f /dev/shm/fastrtps_port* /dev/shm/fastdds* 2>/dev/null || true
```

---

# Quick Reference

## Mapping

```text
Launch SLAM
    ↓
Drive robot
    ↓
Build /map
    ↓
Save slam_map.yaml + slam_map.pgm
    ↓
Optionally serialize SLAM Toolbox pose graph
```

## Localization

```text
Option A
SLAM Toolbox pose graph
        ↓
SLAM Toolbox localization


Option B
slam_map.yaml + slam_map.pgm
        ↓
map_server + AMCL
        ↓
Nav2 localization
```

## Important Rules

- Source `/opt/ros/jazzy/setup.bash` and the workspace `install/setup.bash` in every new terminal.
- Use stamped `teleop_twist_keyboard` with `cmd_vel` remapped to `/diff_drive_controller/cmd_vel`.
- `slam_map.yaml` is an occupancy-map description; it is not the same thing as a SLAM Toolbox pose graph.
- Use occupancy-map + AMCL localization when following the standard Nav2 localization workflow.