# Projects

This directory holds each independent robotics project as its own ROS workspace.

## Templates and active projects

- [project_template_ws/](project_template_ws/) — standard workspace template for all future ROS projects
- [toy_robot_ws/](toy_robot_ws/) — toy robot demo with URDF, custom interfaces, and behavior logic

## Rules for new projects

- create a separate workspace folder under this directory
- keep each project self-contained with its own `src/`, `launch/`, `config/`, and tests
- avoid mixing unrelated robot packages in a single workspace
- add a short README and quick-start notes for each new project
- follow the template naming convention: `<project_name>_ws`
