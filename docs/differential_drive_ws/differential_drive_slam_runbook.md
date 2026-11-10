# Differential Drive SLAM Runbook

Command-first runbook for mapping, localization, and Nav2 navigation with ROS 2 Jazzy, Gazebo Harmonic, and SLAM Toolbox.

- **Workspace:** `/home/gabrielgamy/src/robotics/projects/differential_drive_ws`
- **ROS distribution:** Jazzy

## Table of Contents

- [Simulation and Map Preview](#simulation-and-map-preview)
- [Environment Setup](#environment-setup)
- [Mapping](#mapping)
- [Mapping Validation](#mapping-validation)
- [Localization](#localization)
- [Waypoint Navigation in RViz](#waypoint-navigation-in-rviz)
- [Localization Validation](#localization-validation)
- [Troubleshooting](#troubleshooting)
- [Stop the Stack](#stop-the-stack)
- [Quick Reference](#quick-reference)

## Simulation and Map Preview

The apartment world contains a bedroom and an open living/dining area. The table and chairs remain inside, and the SUV remains outside.

### Gazebo Apartment

![Differential-drive robot in the Gazebo apartment with bedroom furniture, a living area, and an SUV outside](../../images/differential_drive_ws%202026-11-09%2002-43-49.png)

### RViz Occupancy Map

![Apartment occupancy map and differential-drive robot displayed in RViz](../../images/differential_drive_ws%202026-11-09%2002-44-13.png)

These screenshots illustrate the simulation and map visualization; they are not a substitute for the validation checks below. Regenerate the saved map and pose graph whenever the world's layout changes.

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

### 1. Launch Nav2 Localization

```bash
cd /home/gabrielgamy/src/robotics/projects/differential_drive_ws
unset AMENT_PREFIX_PATH CMAKE_PREFIX_PATH COLCON_PREFIX_PATH LD_LIBRARY_PATH
source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 launch differential_drive_bringup \
  slam_localization_nav2.launch.xml \
  world_name:=apartment \
  rviz:=true
```

Note: this launch seeds AMCL with a startup initial pose at `(x=0.0, y=0.0, yaw=0.0)`. The `map -> odom` transform becomes available after scans and odometry TF arrive; it is not immediate.
If you spawn the robot somewhere else, set `2D Pose Estimate` in RViz to correct AMCL.

### 2. (Optional) Correct the Initial Pose

In RViz:

1. Select `2D Pose Estimate`.
2. Click approximately where the robot is located on the map.
3. Drag the arrow in the direction the robot is facing.

Use this when the robot is not spawned at `(0,0,0)` or if localization drifts after startup.

If RViz `2D Pose Estimate` is not available, publish one initial pose from a terminal:

```bash
source /opt/ros/jazzy/setup.bash
source /home/gabrielgamy/src/robotics/projects/differential_drive_ws/install/setup.bash

ros2 topic pub --once /initialpose geometry_msgs/msg/PoseWithCovarianceStamped \
  "{header: {frame_id: map}, pose: {pose: {position: {x: 0.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

### 3. Send a Navigation Goal

In RViz:

1. Select `2D Goal Pose` (or the Nav2 Goal tool if configured).
2. Click the target location in free space on the map.
3. Drag to set the goal heading.

Nav2 uses native `geometry_msgs/msg/TwistStamped` commands throughout this chain:

```text
controller_server / behavior_server
  -> /cmd_vel_nav -> velocity_smoother
  -> /cmd_vel_smoothed -> collision_monitor
  -> /diff_drive_controller/cmd_vel -> diff_drive_controller
```

There is no command conversion relay. Recovery behaviors also use stamped commands,
and the velocity smoother timestamps its outputs at smoothing time.

### 4. Expected Behavior

- Global path appears in RViz.
- The robot moves toward the goal while avoiding obstacles.
- AMCL pose remains stable and follows motion.

The launch combines upstream AMCL localization with the project's
[minimal navigation launch](../../projects/differential_drive_ws/src/differential_drive_bringup/launch/navigation_minimal.launch.xml).
The XML launch starts and lifecycle-manages only the seven navigation nodes used
here; route, waypoint-follower, and docking servers are intentionally excluded.
Keep it alongside the robot-specific Nav2 parameters. The configured goal checker
allows a position tolerance of 0.25 m, so the robot can stop short of the exact target.

---

# Waypoint Navigation in RViz

Waypoint following visits a sequence of poses using the existing Nav2 navigation
stack. The minimal XML launch does not start the waypoint follower; the workflow
below starts and activates it manually. Repeat that setup after restarting the
follower. Do not start a second follower if one is already running.

## 1. Start Navigation

In terminal A, source the environment and launch occupancy-map + AMCL navigation:

```bash
source /opt/ros/jazzy/setup.bash
source /home/gabrielgamy/src/robotics/projects/differential_drive_ws/install/setup.bash

ros2 launch differential_drive_bringup slam_localization_nav2.launch.xml \
  world_name:=apartment rviz:=true
```

Keep an existing instance if it is already running. Confirm localization is
correct and a single navigation goal works before trying a sequence.

## 2. Start the Waypoint Follower

In terminal B:

```bash
source /opt/ros/jazzy/setup.bash
source /home/gabrielgamy/src/robotics/projects/differential_drive_ws/install/setup.bash

ros2 run nav2_waypoint_follower waypoint_follower --ros-args \
  --params-file /home/gabrielgamy/src/robotics/projects/differential_drive_ws/src/differential_drive_bringup/config/nav2_params.yaml \
  -p use_sim_time:=true \
  -p stop_on_failure:=true
```

Leave this terminal occupied. `Waiting on external lifecycle transitions to
activate` is expected, not a startup failure. The configuration pauses for 200 ms
at each waypoint; the command overrides the saved failure policy to stop the
sequence if a waypoint fails.

## 3. Configure and Activate

In terminal C:

```bash
source /opt/ros/jazzy/setup.bash
source /home/gabrielgamy/src/robotics/projects/differential_drive_ws/install/setup.bash

ros2 lifecycle get /waypoint_follower --no-daemon --spin-time 5
```

For `unconfigured [1]`, configure it:

```bash
ros2 lifecycle set /waypoint_follower configure --no-daemon --spin-time 5
```

Wait for `Transitioning successful`, then activate it:

```bash
ros2 lifecycle set /waypoint_follower activate --no-daemon --spin-time 5
ros2 lifecycle get /waypoint_follower --no-daemon --spin-time 5
```

Expect `active [3]`. If the initial state was `inactive [2]`, skip configuration;
if already active, skip both transitions. Do not continue after a failed
transition: inspect terminal B first.

## 4. Collect and Display Waypoints

1. In RViz, set **Global Options -> Fixed Frame** to `map`.
2. Open **Panels -> Add New Panel -> Navigation 2** if the panel is missing.
3. Click **Waypoint Mode** in the Navigation 2 panel. The panel should show
  **Cancel Accumulation**, **Start Nav Through Poses**, and **Start Waypoint Following**.
4. Select **Nav2 Goal** in the toolbar, not the standard **2D Goal Pose** tool.
  If missing, use the toolbar's **+** button to add `nav2_rviz_plugins/GoalTool`.
5. Press and hold the left mouse button in mapped free space, drag to set the
  heading, then release. Select **Nav2 Goal** again for each additional pose.
6. If collected points are invisible, click **Add** in the Displays panel, open
  **By topic**, select the waypoint-related **MarkerArray** display, and click
  **OK**. Keep the display checked.

Start with two nearby, reachable points away from walls and furniture. The robot
should not move while collecting poses. **Poses remaining: 0** is execution
feedback, not proof that accumulation failed.

## 5. Execute, Save, and Stop

Leave **Num of loops** at `0` for a single pass, then click **Start Waypoint
Following**. The robot should visit the poses in placement order and pause briefly
at each stop. **Start Nav Through Poses** uses a different navigation action;
use waypoint following for this workflow.

Watch terminal B for progress and failures. `Completed all waypoints requests`
is the completion message observed in this session; also confirm the robot
actually visited the intended stops.

Use **Save WPs** to save the sequence and **Load WPs** to reuse it with the same
map. Use the panel's **Cancel** control to cancel execution. Do not send separate
goals or teleoperation commands while the sequence is running. After cancellation
or completion, stop terminal B with `Ctrl+C` when the follower is no longer needed.

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

For Nav2 occupancy-map localization:

```bash
ros2 node list
```

Verify that these nodes exist:

- `/amcl`
- `/map_server`
- `/planner_server`
- `/controller_server`
- `/bt_navigator`
- `/lifecycle_manager_localization`
- `/lifecycle_manager_navigation`

For Nav2 occupancy-map localization, verify AMCL and map server are active:

```bash
ros2 lifecycle get /amcl
ros2 lifecycle get /map_server
```

Both should report `active [3]`.

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

Then verify AMCL is active and subscribed:

```bash
ros2 lifecycle get /amcl
ros2 topic info /initialpose -v
```

`/amcl` should be `active [3]`, and `/initialpose` should list one subscriber from AMCL.

After sending `2D Pose Estimate`, confirm AMCL publishes pose updates:

```bash
ros2 topic echo /amcl_pose --once
ros2 run tf2_ros tf2_echo map odom
```

If `/amcl_pose` and `map -> odom` do not update, relaunch from a clean terminal and re-send `2D Pose Estimate`.

## Robot Does Not React to `2D Goal Pose`

Use `slam_localization_nav2.launch.xml` for navigation. Mapping and pose-graph
localization alone do not start the Nav2 navigation servers. Make sure Gazebo is
not paused, and choose a goal in mapped free space more than 0.25 m from the
robot's current position; goals within the configured tolerance may finish without
visible movement.

### Verify the RViz Goal Reaches Nav2

For RViz's standard `2D Goal Pose` tool, run this before clicking a goal:

```bash
timeout 20s ros2 topic echo /goal_pose geometry_msgs/msg/PoseStamped --once
```

The message should use `header.frame_id: map`. If nothing arrives, check the RViz
goal tool's topic is `/goal_pose` and its Fixed Frame is `map`.
The Nav2 Goal tool can send an action directly instead of publishing `/goal_pose`,
so absence of this topic message alone does not indicate failure with that tool.

Check that the navigation action server exists:

```bash
ros2 action info /navigate_to_pose
```

Expect one action server from `/bt_navigator`. For the standard topic-based tool,
also check that `/bt_navigator` subscribes to `/goal_pose`:

```bash
ros2 topic info /goal_pose -v
```

### Verify Localization and Navigation Are Ready

```bash
timeout 6s ros2 run tf2_ros tf2_echo map base_footprint
for node in amcl map_server controller_server smoother_server planner_server behavior_server velocity_smoother collision_monitor bt_navigator; do
  ros2 lifecycle get /"$node"
done
```

The transform must be available, and every listed node should report `active [3]`.
If localization is incorrect, correct it with `2D Pose Estimate` first.
If navigation activation already failed while waiting for `map -> odom`, inspect
the launch errors and relaunch once the map and startup pose are correct.

To bypass the RViz tool, send a goal directly, replacing the example coordinates
with a reachable point in your map:

```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
  "{pose: {header: {frame_id: map}, pose: {position: {x: 0.6, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}" \
  --feedback
```

If this works, investigate the RViz goal tool configuration. If the goal is
rejected or aborted, inspect the action result and launch terminal for TF,
planning, costmap, or controller errors.

### Verify Velocity Commands Reach the Controller

While a goal is executing, run these checks in separate terminals:

```bash
timeout 10s ros2 topic echo /cmd_vel_nav geometry_msgs/msg/TwistStamped --once
timeout 10s ros2 topic echo /cmd_vel_smoothed geometry_msgs/msg/TwistStamped --once
timeout 10s ros2 topic echo /diff_drive_controller/cmd_vel geometry_msgs/msg/TwistStamped --once
```

Look for nonzero `twist.linear.x` or `twist.angular.z` over multiple messages;
a single zero command may simply occur during a stop. If commands disappear
between stages, inspect the corresponding velocity smoother or collision monitor
logs. Collision monitoring may intentionally stop motion because of obstacles or
missing/stale sensor data; resolve the cause instead of bypassing it.

If nonzero commands reach the controller but the robot stays still, check:

```bash
ros2 control list_controllers
```

`diff_drive_controller` should be `active`. Inspect controller logs for stale
command timestamps, and confirm simulation time is advancing. Keep the chain
stamped end to end; do not add an unstamped command conversion relay.

## Waypoint Navigation Does Not Work

### Waypoint Follower Reports `Node not found`

In this session, daemon-backed commands returned an incomplete node list while
direct discovery found the follower and the rest of Nav2. Check without restarting
the simulation:

```bash
ros2 node list --no-daemon --spin-time 5
pgrep -a -u "$USER" -f '[w]aypoint_follower'
```

If the node appears, use the direct-discovery lifecycle commands in
[Configure and Activate](#3-configure-and-activate). If no follower process exists,
inspect its terminal for an exit or error and restart only that follower.

If the process exists but direct discovery still cannot find it, compare discovery
settings in the follower's launch shell and the diagnostic terminal:

```bash
printenv | sort | grep -E '^(ROS_DOMAIN_ID|ROS_LOCALHOST_ONLY|ROS_AUTOMATIC_DISCOVERY_RANGE|ROS_STATIC_PEERS|RMW_IMPLEMENTATION|CYCLONEDDS_URI|FASTRTPS_DEFAULT_PROFILES_FILE|FASTDDS_DEFAULT_PROFILES_FILE)='
```

The settings should match. Stop only the follower with `Ctrl+C` if necessary to
inspect its launch shell, then restart it after correcting any mismatch. An empty
environment listing is valid when both terminals use the same defaults. Do not
clear shared-memory files solely because a node is missing.

### Nav2 Goal Clicks Produce No Visible Points

Confirm accumulation is enabled: **Cancel Accumulation** should be visible in the
Navigation 2 panel. Use **Nav2 Goal**, click and drag to set the heading, and enable
the waypoint **MarkerArray** display through **Displays -> Add -> By topic**.
This display was needed to make the collected points visible during this session.
Check its status for errors and keep RViz's Fixed Frame set to `map`.

If each placement immediately sends the robot toward that pose, stop the current
goal and enable **Waypoint Mode** before collecting the sequence again.

### Start Waypoint Following Does Not Move the Robot

Verify both the follower and navigator are active:

```bash
ros2 lifecycle get /waypoint_follower --no-daemon --spin-time 5
ros2 lifecycle get /bt_navigator --no-daemon --spin-time 5
```

Both should report `active [3]`. Confirm points were collected and click **Start
Waypoint Following**, not **Start Nav Through Poses**. Keep Gazebo unpaused.
Inspect terminal B for goal acceptance or failure messages and the navigation
launch terminal for planning, TF, or controller errors.

If execution starts but motion does not, cancel the sequence and test a single
goal using [Robot Does Not React to 2D Goal Pose](#robot-does-not-react-to-2d-goal-pose).
Waypoint following depends on that same navigation and stamped velocity chain.
With `stop_on_failure:=true`, one unreachable waypoint stops the sequence; correct
the waypoint or underlying navigation failure before retrying.

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

A brief TF error can still appear during startup while Nav2 nodes initialize.

If this error persists and Nav2 lifecycle reports planner activation failure, AMCL has not produced `map -> odom` yet.
Set a valid `2D Pose Estimate` and relaunch if needed.

Verify with:

```bash
ros2 run tf2_ros tf2_echo map base_footprint
```

## Stale ROS/Gazebo Processes

If the launch behaves inconsistently, first stop its launch terminal with `Ctrl+C`.
Inspect remaining processes before stopping anything else:

```bash
ps -eo pid,ppid,args | grep -E '[r]os2 launch|/opt/ros/jazzy/lib/|[g]z sim'
```

Send `SIGTERM` only to identified stale PIDs belonging to this stack. Use `SIGKILL`
only for those specific PIDs if graceful termination fails. Broad `pkill -f`
patterns can terminate unrelated processes and miss orphaned Nav2 executables.
Verify that no old stack instances remain, then relaunch from a clean terminal.

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

If Gazebo, ROS, or RViz processes remain stuck, follow the targeted PID inspection
and termination procedure in **Stale ROS/Gazebo Processes** above.

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
