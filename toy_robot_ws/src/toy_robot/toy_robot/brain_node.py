import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class BrainNode(Node):
    def __init__(self):
        super().__init__('brain_node')

        self.subscription = self.create_subscription(
            String,
            'detected_objects',
            self.listener_callback,
            10
        )

        self.state = "SEARCHING"

    def listener_callback(self, msg):
        detected = msg.data

        if detected != "nothing":
            self.state = "OBJECT_DETECTED"
            self.get_logger().info(f"Found: {detected}")
        else:
            self.state = "SEARCHING"
            self.get_logger().info("Still searching...")

    def run_cycle(self):
        msg = String()
        msg.data = f"State: {self.state}"

        self.get_logger().info(msg.data)
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = BrainNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()