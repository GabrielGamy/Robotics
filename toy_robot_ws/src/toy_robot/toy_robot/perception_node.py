import random

import rclpy
from geometry_msgs.msg import Point
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node

class PerceptionNode(Node):
    """ROS2 node for object detection simulation."""

    def __init__(self):
        """Initialize perception node."""
        super().__init__('perception_node')

        self.declare_parameter('publish_rate_hz', 0.1)
        self.declare_parameter('detection_x_min', 0.5)
        self.declare_parameter('detection_x_max', 2.0)
        self.declare_parameter('detection_y_min', -1.0)
        self.declare_parameter('detection_y_max', 1.0)

        publish_rate_hz = float(self.get_parameter('publish_rate_hz').value)
        self.detection_x_min = float(self.get_parameter('detection_x_min').value)
        self.detection_x_max = float(self.get_parameter('detection_x_max').value)
        self.detection_y_min = float(self.get_parameter('detection_y_min').value)
        self.detection_y_max = float(self.get_parameter('detection_y_max').value)

        period_sec = 1.0 / max(publish_rate_hz, 0.01)

        self.publisher_ = self.create_publisher(
            Point, 'detected_object_position', 10)
        self.timer = self.create_timer(period_sec, self.detect_object)

    def detect_object(self):
        """Simulate object detection."""
        msg = Point()
        msg.x = random.uniform(self.detection_x_min, self.detection_x_max)
        msg.y = random.uniform(self.detection_y_min, self.detection_y_max)
        msg.z = 0.0

        self.get_logger().info(
            f'📍 Detected object at ({msg.x:.2f}, {msg.y:.2f})')
        self.publisher_.publish(msg)


def main():
    """Entry point."""
    rclpy.init()
    node = PerceptionNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
