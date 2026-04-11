import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from rclpy.action import ActionClient
from geometry_msgs.msg import Point, PoseStamped
from nav2_msgs.action import NavigateToPose

class BrainNode(Node):
    def __init__(self):
        super().__init__('brain_node')

        self.subscription = self.create_subscription(
            Point,
            'detected_object_position',
            self.object_callback,
            10
        )        
        self.state = "SEARCHING"
        self.timer = self.create_timer(2.0, self.run_state_machine)          
        self._action_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')   
  
    def object_callback(self, msg):
        if self.state != "SEARCHING":
            return

        self.target_x = msg.x
        self.target_y = msg.y
        self.state = "GO_TO_OBJECT"

    def run_state_machine(self):
        if self.state == "SEARCHING":
            self.get_logger().info("🔍 Searching for objects...")

            if hasattr(self, 'target_x'):
                self.state = "GO_TO_OBJECT"

        elif self.state == "GO_TO_OBJECT":
            self.get_logger().info(f"🚗 Going to ({self.target_x:.2f}, {self.target_y:.2f})")

            goal_msg = NavigateToPose.Goal()

            goal_msg.pose = PoseStamped()
            goal_msg.pose.header.frame_id = 'map'
            goal_msg.pose.pose.position.x = self.target_x
            goal_msg.pose.pose.position.y = self.target_y
            goal_msg.pose.pose.orientation.w = 1.0

            self._action_client.wait_for_server()

            send_goal_future = self._action_client.send_goal_async(goal_msg)
            send_goal_future.add_done_callback(self.goal_response_callback)

            self.state = "WAIT_NAVIGATION"

        elif self.state == "WAIT_NAVIGATION":
            self.get_logger().info("⏳ Waiting for navigation...")

        elif self.state == "PICK":
            self.get_logger().info("🤖 Picking object...")
            self.state = "GO_TO_BOX"

        elif self.state == "GO_TO_BOX":
            self.get_logger().info("📦 Moving to box...")

            # 👉 pour l’instant on simule une position fixe
            goal_msg = NavigateToPose.Goal()

            goal_msg.pose = PoseStamped()
            goal_msg.pose.header.frame_id = 'map'
            goal_msg.pose.pose.position.x = 0.0
            goal_msg.pose.pose.position.y = 0.0
            goal_msg.pose.pose.orientation.w = 1.0

            send_goal_future = self._action_client.send_goal_async(goal_msg)
            send_goal_future.add_done_callback(self.goal_response_callback)

            self.state = "WAIT_NAVIGATION_TO_BOX"

        elif self.state == "WAIT_NAVIGATION_TO_BOX":
            self.get_logger().info("⏳ Going to box...")

        elif self.state == "DROP":
            self.get_logger().info("🧺 Dropping object...")

            del self.target_x
            del self.target_y

            self.state = "SEARCHING"

    def goal_response_callback(self, future):
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().info("❌ Goal rejected")
            self.state = "SEARCHING"
            return

        self.get_logger().info("✅ Goal accepted")

        get_result_future = goal_handle.get_result_async()
        get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        result = future.result().result

        self.get_logger().info(f"🏁 Navigation finished! - Current state: {self.state}")

        if self.state == "WAIT_NAVIGATION":
            self.state = "PICK"

        elif self.state == "WAIT_NAVIGATION_TO_BOX":
            self.state = "DROP"

def main():
    rclpy.init()
    node = BrainNode()
    rclpy.spin(node)
    rclpy.shutdown()