# Differential Drive Gazebo Workspace

This workspace is the Gazebo-based drivetrain workspace for the project.

Purpose:
- Keep a complete working path based on Gazebo DiffDrive + Gazebo JointStatePublisher.
- Evolve Gazebo-based simulation features in parallel with a separate ros2_control workspace.
- Enable side-by-side comparison between the Gazebo-driven and ros2_control-driven architectures.

Workspace:
- `src/` contains source packages.
- `build/`, `install/`, and `log/` are local artifacts and should not be committed.

## Build and Run

```bash
source /opt/ros/jazzy/setup.bash
cd /home/gabrielgamy/src/robotics/projects/differential_drive_gazebo_baseline_ws
colcon build --symlink-install
source install/setup.bash
ros2 launch differential_drive_robot sim.launch.xml
```

## Teleop

In another terminal:

```bash
source /opt/ros/jazzy/setup.bash
cd /home/gabrielgamy/src/robotics/projects/differential_drive_gazebo_baseline_ws
source install/setup.bash
ros2 launch differential_drive_robot teleop.launch.xml
```

## Notes

- This workspace owns the Gazebo-native drivetrain path.
- Keep both workspaces aligned on robot dimensions and frame naming so behavior comparisons remain meaningful.
