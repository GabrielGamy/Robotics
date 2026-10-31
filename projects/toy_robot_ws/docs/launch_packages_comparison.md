# Launch Files Comparison (toy_robot / toy_robot_description / toy_robot_bringup)

## Application Package: `robot.launch.xml`

- **Role**: launch the robot business-logic nodes (brain, perception, manipulation).
- **Content**: only ROS 2 nodes from the `toy_robot` package.
- **Does not include**: Gazebo, bridge, RViz, SLAM, Nav2.
- **Use when**: you want to run application logic independently from simulation/navigation.

## Description Package: `display.launch.xml`

- **Role**: static URDF visualization.
- **Content**: `robot_state_publisher` + `joint_state_publisher(_gui)` + RViz.
- **Does not include**: Gazebo physics simulation, `ros_gz` bridge, real simulated sensors.
- **Use when**: you want to validate the URDF model, joints, frames, and visuals.

## Description Package: `gazebo.launch.xml`

- **Role**: complete low-level simulation launch.
- **Content**: Gazebo, robot spawn, `robot_state_publisher`, `ros_gz_bridge`, optional RViz.
- **Note**: this is the technical base launch that other launch files can build on.
- **Use when**: you want to test simulation and sensors directly without Nav2 orchestration.

## Bringup Package: `simulation.launch.xml`

- **Role**: project-level simulation entrypoint.
- **Content**: includes `gazebo.launch.xml`, then applies bringup RViz config.
- **Added value**: standardizes how the team launches simulation.

## Bringup Package: `slam.launch.xml`

- **Role**: simulation + SLAM ready for mapping.
- **Content**: `gazebo.launch.xml` + `slam_toolbox` + SLAM RViz config.
- **Parameters**: `slam_params.yaml`.

## Bringup Package: `navigation.launch.xml`

- **Role**: simulation + Nav2 (AMCL/planning/costmaps) with a map.
- **Content**: `gazebo.launch.xml` + `nav2_bringup` + navigation RViz config.
- **Parameters**: `nav2_params.yaml`.
- **Map behavior**: uses the packaged demo/reference map by default, but you can override it with `map:=/path/to/other_map.yaml`.

## About `display.launch.xml`

- Yes, `display.launch.xml` is still useful.
- It is the fastest way to validate the robot model without Gazebo simulation overhead.
- It is not a duplicate of SLAM/Nav2 flows; it is a URDF debugging tool.

## Recommended Architecture (Standard Practice)

- `toy_robot`: robot logic.
- `toy_robot_description`: assets and low-level technical launch files.
- `toy_robot_bringup`: high-level scenario-oriented launches (simulation, SLAM, navigation).

## Launch Selection Matrix (6 Common Cases)

Use this quick matrix to decide which launch file to run first based on your objective.

| Objective | Recommended launch command | Why this is the best fit |
| --- | --- | --- |
| 1. URDF check (model, joints, frames, visuals) | `ros2 launch toy_robot_description display.launch.xml` | Fast static validation without simulation overhead. |
| 2. Sensor check (camera, LiDAR, /odom, /tf) | `ros2 launch toy_robot_bringup simulation.launch.xml` | Starts full simulation stack with consistent project RViz setup. |
| 3. Teleop driving test in simulation | `ros2 launch toy_robot_bringup simulation.launch.xml` | Provides Gazebo + bridge + robot_state_publisher; teleop can publish to `/cmd_vel`. |
| 4. Mapping (build a map with SLAM) | `ros2 launch toy_robot_bringup slam.launch.xml` | Adds `slam_toolbox` on top of simulation for real-time map building. |
| 5. Navigation on a saved map | `ros2 launch toy_robot_bringup navigation.launch.xml` | Starts Nav2 stack (AMCL, planners, costmaps, behaviors) with the packaged demo/reference map. Override with `map:=/absolute/path/to/map.yaml` when needed. |
| 6. Full application behavior stack | `ros2 launch toy_robot robot.launch.xml` | Runs robot business logic nodes (brain/perception/manipulation) independently of simulation bringup. |

### Notes

- For day-to-day simulation work, prefer `toy_robot_bringup` launch files.
- Use `toy_robot_description/gazebo.launch.xml` when you need low-level debugging of the simulation plumbing.
- Use `toy_robot/robot.launch.xml` when validating application logic and state-machine behavior.
