# Architecture Overview

This document explains how the toy robot package is structured and why each component exists.

## Design Principles

1. Keep business logic independent from ROS interfaces.
2. Isolate coordinate transforms and geometry helpers.
3. Keep visualization concerns separate from control decisions.
4. Drive runtime behavior with ROS parameters.

## Main Components

### brain_node

File: `src/toy_robot/toy_robot/brain_node.py`

Responsibilities:

1. Reads ROS parameters.
2. Subscribes to detections and forwards events to the behavior controller.
3. Sends Nav2 actions (`NavigateToPose`, `Spin`).
4. Uses TF utilities to transform points and compute orientation.
5. Publishes debug markers through the visualization module.

### behavior controller

File: `src/toy_robot/toy_robot/behavior/brain_controller.py`

Responsibilities:

1. Holds the state machine.
2. Handles transitions between searching, navigating, pick, box drop flow.
3. Contains no ROS node code, no publishers/subscribers, no actions.

### TF transformer

File: `src/toy_robot/toy_robot/tf/transformer.py`

Responsibilities:

1. Transforms detected points between frames.
2. Looks up robot pose in the target frame.
3. Computes yaw quaternion to face a target.
4. Computes offset approach goal using stop distance.

### visualization module

File: `src/toy_robot/toy_robot/visualization/marker_visualizer.py`

Responsibilities:

1. Publishes RViz markers for target and navigation goal.
2. Publishes optional robot-to-target direction line.
3. Handles marker setup details (namespace, id, color, scale, lifetime).

### perception_node

File: `src/toy_robot/toy_robot/perception_node.py`

Responsibilities:

1. Simulates object detections.
2. Publishes detection points using configurable ranges and rate.

## Data Flow

1. `perception_node` publishes `detected_object_position`.
2. `brain_node` transforms detection from source frame to target frame.
3. `brain_controller` updates state according to event and current state.
4. `brain_node` computes navigation goal and orientation.
5. `brain_node` sends Nav2 action goals.
6. `marker_visualizer` publishes RViz markers for debugging.

## Parameter Source of Truth

1. Runtime parameters are defined in `src/toy_robot/config/robot_config.yaml`.
2. Launch loads this file via `src/toy_robot/launch/robot.launch.xml`.
3. Nodes declare parameters with safe defaults, then read effective values at startup.

## Why This Separation Helps

1. You can unit-test state transitions without ROS middleware.
2. TF/geometric math can evolve without touching business logic.
3. RViz debug features can change without affecting navigation behavior.
4. Configuration changes do not require code edits.
