from geometry_msgs.msg import PointStamped
import tf2_geometry_msgs  # noqa: F401

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

    def point_to_map(self, point_msg, source_frame, timeout_seconds=1.0):
        """Transform a Point from source_frame to 'map' frame.

        Args:
            point_msg: geometry_msgs.msg.Point
            source_frame: source frame name (e.g., 'camera_link')
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
                point_stamped, 'map', timeout=timeout)

            return (transformed.point.x, transformed.point.y)

        except Exception as e:
            self.logger.warn(f'TF transformation failed: {e} - Point({point_msg.x}, {point_msg.y}, {point_msg.z})')
            return None
