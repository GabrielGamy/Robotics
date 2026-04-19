from geometry_msgs.msg import Point
from rclpy.duration import Duration
from visualization_msgs.msg import Marker


class MarkerVisualizer:
    """Publish RViz markers for debugging target and goal positions."""

    def __init__(
        self,
        node,
        frame_id='map',
        topic='visualization_marker',
        lifetime_sec=0.0,
        target_scale=0.15,
        goal_length=0.35,
        goal_width=0.07,
        direction_line_width=0.03,
    ):
        """Create marker publisher bound to a node and frame."""
        self._node = node
        self._frame_id = frame_id
        self._lifetime_sec = float(lifetime_sec)
        self._target_scale = float(target_scale)
        self._goal_length = float(goal_length)
        self._goal_width = float(goal_width)
        self._direction_line_width = float(direction_line_width)
        self._pub = node.create_publisher(Marker, topic, 10)

        self.clear_all()

    def clear_all(self):
        """Clear all markers in RViz for a clean startup."""
        marker = Marker()
        marker.action = Marker.DELETEALL
        self._pub.publish(marker)

    def publish_target(self, x, y):
        """Publish target marker (green sphere)."""
        marker = self._base_marker('target', 0, Marker.SPHERE)
        marker.pose.position.x = float(x)
        marker.pose.position.y = float(y)
        marker.pose.position.z = 0.05
        marker.pose.orientation.w = 1.0

        marker.scale.x = self._target_scale
        marker.scale.y = self._target_scale
        marker.scale.z = self._target_scale

        marker.color.a = 1.0
        marker.color.r = 0.1
        marker.color.g = 0.9
        marker.color.b = 0.1

        self._pub.publish(marker)

    def publish_goal(self, x, y, qz, qw):
        """Publish goal marker (blue arrow with orientation)."""
        marker = self._base_marker('goal', 0, Marker.ARROW)
        marker.pose.position.x = float(x)
        marker.pose.position.y = float(y)
        marker.pose.position.z = 0.05
        marker.pose.orientation.z = float(qz)
        marker.pose.orientation.w = float(qw)

        marker.scale.x = self._goal_length
        marker.scale.y = self._goal_width
        marker.scale.z = self._goal_width

        marker.color.a = 1.0
        marker.color.r = 0.2
        marker.color.g = 0.4
        marker.color.b = 1.0

        self._pub.publish(marker)

    def publish_direction_line(self, robot_x, robot_y, target_x, target_y):
        """Publish robot-to-target direction line (orange line strip)."""
        marker = self._base_marker('direction', 0, Marker.LINE_STRIP)
        marker.pose.orientation.w = 1.0
        marker.scale.x = self._direction_line_width

        marker.color.a = 1.0
        marker.color.r = 1.0
        marker.color.g = 0.5
        marker.color.b = 0.1

        start = Point()
        start.x = float(robot_x)
        start.y = float(robot_y)
        start.z = 0.05

        end = Point()
        end.x = float(target_x)
        end.y = float(target_y)
        end.z = 0.05

        marker.points = [start, end]
        self._pub.publish(marker)

    def remove_target_marker(self):
        """Remove target marker from RViz."""
        self._delete_marker('target', 0)

    def remove_direction_marker(self):
        """Remove direction marker from RViz."""
        self._delete_marker('direction', 0)

    def _delete_marker(self, namespace, marker_id):
        """Publish a DELETE marker for a namespace/id pair."""
        marker = Marker()
        marker.header.frame_id = self._frame_id
        marker.header.stamp = self._node.get_clock().now().to_msg()
        marker.ns = namespace
        marker.id = int(marker_id)
        marker.action = Marker.DELETE
        self._pub.publish(marker)

    def _base_marker(self, namespace, marker_id, marker_type):
        """Build a marker with common header and lifecycle fields."""
        marker = Marker()
        marker.header.frame_id = self._frame_id
        marker.header.stamp = self._node.get_clock().now().to_msg()
        marker.ns = namespace
        marker.id = int(marker_id)
        marker.type = marker_type
        marker.action = Marker.ADD

        if self._lifetime_sec > 0.0:
            marker.lifetime = Duration(seconds=self._lifetime_sec).to_msg()

        return marker
