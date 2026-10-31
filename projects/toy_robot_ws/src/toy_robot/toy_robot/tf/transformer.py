import math

from geometry_msgs.msg import PointStamped
import rclpy
from rclpy.time import Time
import tf2_geometry_msgs  # noqa: F401


class CoordinateTransformer:
    """Utility for transforming coordinates between ROS frames."""

    def __init__(self, tf_buffer, logger):
        """Initialize transformer with a TF buffer and logger."""
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
        """Transform a point from source_frame to target_frame."""
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
            self.logger.warn(
                f'TF transformation failed: {e} - '
                f'Point({point_msg.x}, {point_msg.y}, {point_msg.z})'
            )
            return None

    # Read the robot position from TF so goals can face the target.
    def lookup_robot_position(
        self,
        target_frame='map',
        robot_frame='base_link',
        timeout_seconds=1.0,
    ):
        """Return the robot (x, y) position in target_frame, or None."""
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
        """Return a yaw-only quaternion that faces the target point."""
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
        """Return a target offset that keeps stop_distance from the object."""
        dx = target_x - robot_x
        dy = target_y - robot_y
        dist = math.hypot(dx, dy)

        if dist <= stop_distance:
            # Already within stop distance; stay put.
            return (robot_x, robot_y)

        ux = dx / dist
        uy = dy / dist
        return (target_x - ux * stop_distance, target_y - uy * stop_distance)
