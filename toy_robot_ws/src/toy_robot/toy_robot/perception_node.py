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

        self.publisher_ = self.create_publisher(
            Point, 'detected_object_position', 10)
        self.timer = self.create_timer(10.0, self.detect_object)

    def detect_object(self):
        """Simulate object detection."""
        msg = Point()
        msg.x = random.uniform(0.5, 2.0)
        msg.y = random.uniform(-1.0, 1.0)
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
