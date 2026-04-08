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
        self.object_detected = None

        self.timer = self.create_timer(2.0, self.run_state_machine)

    def listener_callback(self, msg):
        if msg.data != "nothing":
            self.object_detected = msg.data

    def run_state_machine(self):
        if self.state == "SEARCHING":
            self.get_logger().info("Searching for objects...")
            if self.object_detected:
                self.state = "OBJECT_DETECTED"

        elif self.state == "OBJECT_DETECTED":
            self.get_logger().info(f"Object detected: {self.object_detected}")
            self.state = "GO_TO_OBJECT"

        elif self.state == "GO_TO_OBJECT":
            self.get_logger().info("Moving to object...")
            self.state = "PICK"

        elif self.state == "PICK":
            self.get_logger().info("Picking object...")
            self.state = "GO_TO_BOX"

        elif self.state == "GO_TO_BOX":
            self.get_logger().info("Moving to box...")
            self.state = "DROP"

        elif self.state == "DROP":
            self.get_logger().info("Dropping object...")
            self.object_detected = None
            self.state = "SEARCHING"

def main():
    rclpy.init()
    node = BrainNode()
    rclpy.spin(node)
    rclpy.shutdown()