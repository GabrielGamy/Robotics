# differential_drive_gazebo_ros2_control_baseline_ws

Known-good baseline workspace for differential drive simulation using Gazebo + ros2_control.

## Purpose

- Preserve a stable, reproducible simulation reference before real hardware migration work.
- Keep this workspace focused on simulation validation and regression checks.

## Source Snapshot

- Copied from `projects/differential_drive_ws`
- Baseline commit: `7f55601`

## Build

```bash
source /opt/ros/jazzy/setup.bash
cd /home/gabrielgamy/src/robotics/projects/differential_drive_gazebo_ros2_control_baseline_ws
colcon build --symlink-install
source install/setup.bash
```

## Run

```bash
ros2 launch differential_drive_bringup sim.launch.xml
```

## Notes

- This workspace intentionally excludes `build/`, `install/`, and `log/` from the copied snapshot.
- Keep architecture as Gazebo-hosted controller manager via `gz_ros2_control` in simulation.
