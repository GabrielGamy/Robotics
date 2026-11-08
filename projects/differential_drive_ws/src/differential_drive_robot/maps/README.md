# SLAM Maps

This directory is intended for saved SLAM Toolbox pose-graph files.

Example save command while `slam_mapping.launch.xml` is running:

```bash
ros2 service call /slam_toolbox/serialize_map slam_toolbox/srv/SerializePoseGraph "{filename: '/home/gabrielgamy/src/robotics/projects/differential_drive_ws/src/differential_drive_robot/maps/apartment_posegraph'}"
```

Then set `map_file_name` in `config/slam_toolbox_localization.yaml` to the same base path.