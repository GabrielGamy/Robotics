# SLAM Maps

This directory is intended for saved SLAM Toolbox pose-graph files.

## Table of Contents

- [Save a Pose Graph](#save-a-pose-graph)
- [Use a Saved Pose Graph](#use-a-saved-pose-graph)

## Save a Pose Graph

Example save command while `slam_mapping.launch.xml` is running:

```bash
ros2 service call /slam_toolbox/serialize_map slam_toolbox/srv/SerializePoseGraph "{filename: '/home/gabrielgamy/src/robotics/projects/differential_drive_ws/src/differential_drive_robot/maps/apartment_posegraph'}"
```

## Use a Saved Pose Graph

Set `map_file_name` in `config/slam_toolbox_localization.yaml` to the same base path.