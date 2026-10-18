# RViz Debug Guide

This guide explains how to visualize target and goal markers in RViz.

## Purpose

The RViz markers help validate:

1. TF transform correctness.
2. Stop distance offset behavior.
3. Goal orientation sent to Nav2.
4. Robot-to-target direction alignment.

## Published Marker Semantics

Topic:

- `visualization_marker`

Markers:

1. Target marker

- Namespace: `target`
- Type: `SPHERE`
- Color: green
- Meaning: transformed object position in target frame

2. Goal marker

- Namespace: `goal`
- Type: `ARROW`
- Color: blue
- Meaning: actual goal sent to navigation (after stop-distance offset)

3. Direction marker (optional)

- Namespace: `direction`
- Type: `LINE_STRIP`
- Color: orange
- Meaning: line from robot pose to transformed target

## Prerequisites

1. Build and source workspace.
2. Launch the robot stack.

Commands:

```bash
cd ~/Robotics/projects/toy_robot_ws
colcon build --packages-select toy_robot --symlink-install
source install/setup.bash
ros2 launch toy_robot robot.launch.xml
```

## RViz Setup

1. Start RViz2.
2. Set `Fixed Frame` to `map`.
3. Add `Marker` display.
4. Set marker topic to `visualization_marker`.

## Parameters for Visualization

Defined under `brain_node.ros__parameters` in `src/toy_robot/config/robot_config.yaml`:

1. `visualization_enabled`: enable or disable all marker publishing.
2. `marker_lifetime_sec`: marker persistence (`0.0` means persistent).
3. `target_marker_scale`: target sphere size.
4. `goal_marker_length`: goal arrow length.
5. `goal_marker_width`: goal arrow width/thickness.
6. `show_direction_line`: enable robot-to-target line.
7. `direction_line_width`: line thickness.

## Typical Debug Checks

1. Target appears where expected in `map` frame.
2. Goal appears slightly before target when `stop_distance > 0`.
3. Goal arrow points toward target.
4. Direction line is coherent with goal orientation and TF.

## Common Issues

1. No markers visible

- Ensure `visualization_enabled: true`.
- Check RViz topic is exactly `visualization_marker`.
- Confirm `Fixed Frame` matches target frame (`map`).

2. Markers in wrong place

- Verify source/target frame parameters.
- Verify TF tree is available and stable.

3. Old markers remain

- Set non-zero `marker_lifetime_sec` for auto-expire if preferred.
