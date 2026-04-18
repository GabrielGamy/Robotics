from geometry_msgs.msg import PointStamped
import tf2_geometry_msgs  # noqa: F401

import math
import rclpy
from rclpy.time import Time


class CoordinateTransformer:
    """Utility for transforming coordinates between ROS frames."""

    def __init__(self, tf_buffer, logger):
        """Initialize transformer.

        Args:
            tf_buffer: tf2_ros.Buffer instance.
            logger: rclpy logger for warnings.
        """
        self.tf_buffer = tf_buffer
        self.logger = logger

    # Transform a detected point between configured TF frames.
    def point_to_map(
        self,
        point_msg,
        source_frame,
        target_frame='map',
        timeout_seconds=1.0,
    ):
        """Transform a Point from source_frame to target_frame.

        Args:
            point_msg: geometry_msgs.msg.Point
            source_frame: source frame name (e.g., 'camera_link')
            target_frame: destination frame name (e.g., 'map')
            timeout_seconds: timeout for TF lookup

        Returns:
            Transformed point as (x, y) tuple or None if transform fails.
        """
        try:
            point_stamped = PointStamped()
            point_stamped.header.frame_id = source_frame
            # Use time 0 to request the latest available TF transform.
            # This avoids system-time vs simulation-time extrapolation issues.
            point_stamped.header.stamp = Time().to_msg()
            point_stamped.point = point_msg

            timeout = rclpy.duration.Duration(seconds=timeout_seconds)
            transformed = self.tf_buffer.transform(
                point_stamped, target_frame, timeout=timeout)

            return (transformed.point.x, transformed.point.y)

        except Exception as e:
            self.logger.warn(f'TF transformation failed: {e} - Point({point_msg.x}, {point_msg.y}, {point_msg.z})')
            return None

    # Read the robot position from TF so goals can face the target.
    def lookup_robot_position(
        self,
        target_frame='map',
        robot_frame='base_link',
        timeout_seconds=1.0,
    ):
        """Return the robot position in the target frame.

        Args:
            target_frame: destination frame for the lookup.
            robot_frame: robot body frame.
            timeout_seconds: timeout for TF lookup.

        Returns:
            Tuple (x, y) or None if lookup fails.
        """
        try:
            timeout = rclpy.duration.Duration(seconds=timeout_seconds)
            transform = self.tf_buffer.lookup_transform(
                target_frame,
                robot_frame,
                Time(),
                timeout=timeout,
            )

            return (
                transform.transform.translation.x,
                transform.transform.translation.y,
            )

        except Exception as e:
            self.logger.warn(
                f'Robot pose lookup failed: {e} - '
                f'Frames({target_frame}, {robot_frame})'
            )
            return None

    # Compute a quaternion that makes the robot face a target point.
    def quaternion_to_face_target(self, robot_x, robot_y, target_x, target_y):
        """Return a planar quaternion facing the target point.

        Args:
            robot_x: current robot x coordinate.
            robot_y: current robot y coordinate.
            target_x: target x coordinate.
            target_y: target y coordinate.

        Returns:
            Tuple (qz, qw) for a yaw-only quaternion.
        """
        dx = target_x - robot_x
        dy = target_y - robot_y
        theta = math.atan2(dy, dx)

        qz = math.sin(theta / 2.0)
        qw = math.cos(theta / 2.0)
        return (qz, qw)

    # Compute a goal position that stops before the object to avoid crushing it.
    def approach_position(
        self, robot_x, robot_y, target_x, target_y, stop_distance
    ):
        """Return a goal position offset from the target along the approach axis.

        Backs off from the target by stop_distance along the robot→target
        direction, so the robot halts in front of the object rather than
        on top of it.  The orientation goal should still be computed using
        the original target coordinates so the robot faces the object.

        Args:
            robot_x: current robot x coordinate.
            robot_y: current robot y coordinate.
            target_x: target x coordinate.
            target_y: target y coordinate.
            stop_distance: metres to stay away from the target.

        Returns:
            Tuple (goal_x, goal_y) offset from the target.
        """
        dx = target_x - robot_x
        dy = target_y - robot_y
        dist = math.hypot(dx, dy)

        if dist <= stop_distance:
            # Already within stop distance; stay put.
            return (robot_x, robot_y)

        ux = dx / dist
        uy = dy / dist
        return (target_x - ux * stop_distance, target_y - uy * stop_distance)
