# Launch Files

This folder contains runtime entry points for visualization, simulation, and teleoperation.

## Files

- `display.launch.xml`
  - Purpose: URDF visualization flow (RViz + robot_state_publisher + joint_state_publisher_gui).
  - No Gazebo simulation.

- `gazebo.launch.xml`
  - Purpose: Full Gazebo simulation stack.
  - Starts Gazebo, publishes robot description, spawns the model, bridges ROS <-> Gazebo topics, and optionally starts RViz.

- `sim.launch.xml`
  - Purpose: High-level simulation entry point.
  - Thin wrapper around `gazebo.launch.xml` that forwards common args.

- `teleop.launch.xml`
  - Purpose: Keyboard teleop (`teleop_twist_keyboard`) with configurable `cmd_vel` topic remap.
  - Note: Keyboard teleop needs a real interactive TTY. This launch uses a terminal prefix by default.

## Common Commands

From workspace root:

```bash
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash
```

Run simulation:

```bash
ros2 launch differential_drive_robot sim.launch.xml
```

Run simulation without RViz:

```bash
ros2 launch differential_drive_robot sim.launch.xml rviz:=false
```

Run direct Gazebo launch (implementation file):

```bash
ros2 launch differential_drive_robot gazebo.launch.xml
```

Run teleop in another terminal while simulation is running:

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch differential_drive_robot teleop.launch.xml
```

If your desktop uses a different terminal emulator, override the prefix:

```bash
ros2 launch differential_drive_robot teleop.launch.xml terminal_prefix:="xfce4-terminal -e"
```

If you prefer running teleop directly in your current shell (no launch wrapper):

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Run pure display mode (no Gazebo):

```bash
ros2 launch differential_drive_robot display.launch.xml
```

## Key Arguments

`sim.launch.xml` and `gazebo.launch.xml`:
- `world`: SDF world path.
- `rviz`: `true` or `false`.
- `x`, `y`, `z`: spawn position.

`teleop.launch.xml`:
- `cmd_vel_topic`: target Twist topic (default `/cmd_vel`).
- `use_terminal_prefix`: run in a separate terminal to provide keyboard TTY.
- `terminal_prefix`: terminal command used as launch prefix.
