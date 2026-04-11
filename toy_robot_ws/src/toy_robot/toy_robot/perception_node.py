import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point
import random

class PerceptionNode(Node):
    def __init__(self):
        super().__init__('perception_node')

        self.publisher_ = self.create_publisher(Point, 'detected_object_position', 10)
        self.timer = self.create_timer(10.0, self.detect_object)

    def detect_object(self):
        msg = Point()
        msg.x = random.uniform(0.5, 2.0)
        msg.y = random.uniform(-1.0, 1.0)
        msg.z = 0.0

        self.get_logger().info(f"📍 Detected object at ({msg.x:.2f}, {msg.y:.2f})")
        self.publisher_.publish(msg)

def main():
    rclpy.init()
    node = PerceptionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()