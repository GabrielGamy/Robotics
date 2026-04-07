import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import random

class PerceptionNode(Node):
    def __init__(self):
        super().__init__('perception_node')

        self.publisher_ = self.create_publisher(String, 'detected_objects', 10)

        self.timer = self.create_timer(3.0, self.detect_object)

    def detect_object(self):
        objects = ["toy_car", "teddy_bear", "nothing"]
        detected = random.choice(objects)

        msg = String()
        msg.data = detected

        self.get_logger().info(f"Detected: {detected}")
        self.publisher_.publish(msg)

def main():
    rclpy.init()
    node = PerceptionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()