import rclpy
from geometry_msgs.msg import Point, PoseStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from tf2_ros import Buffer, TransformListener

from toy_robot.behavior.brain_controller import BrainController
from toy_robot.models.target import Target
from toy_robot.tf.transformer import CoordinateTransformer

class BrainNode(Node):
    """ROS2 node for robot behavior control."""

    def __init__(self):
        """Initialize brain node."""
        super().__init__('brain_node')

        # Declare parameters from launch file
        self.declare_parameter('box_x', 0.0)
        self.declare_parameter('box_y', 0.0)
        self.declare_parameter('stop_distance', 0.3)

        # Get parameter values
        box_x = self.get_parameter('box_x').value
        box_y = self.get_parameter('box_y').value
        self.stop_distance = self.get_parameter('stop_distance').value

        # ROS infrastructure
        self.subscription = self.create_subscription(
            Point,
            'detected_object_position',
            self.object_callback,
            10
        )
        self.timer = self.create_timer(2.0, self.run_state_machine)
        self._action_client = ActionClient(
            self, NavigateToPose, 'navigate_to_pose')

        # TF2
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # Logic layer (pure, testable)
        self.brain = BrainController(box_x=box_x, box_y=box_y)
        self.tf_transformer = CoordinateTransformer(
            self.tf_buffer, self.get_logger())

        self.get_logger().info(
            f'🤖 Brain initialized with box at ({box_x}, {box_y})')

    def object_callback(self, msg):
        """Handle detected object position from perception."""
        # Transform point from camera frame to map frame
        result = self.tf_transformer.point_to_map(msg, 'camera_link')

        if result is None:
            return

        x, y = result
        target = Target(x=x, y=y, source='camera')

        # Notify brain controller
        if self.brain.on_object_detected(target):
            self.get_logger().info(f'🧭 Target acquired: {target}')

    def run_state_machine(self):
        """Execute state machine transitions."""
        state = self.brain.state.value

        if state == 'SEARCHING':
            self.get_logger().info('🔍 Searching for objects...')

        elif state == 'GO_TO_OBJECT':
            self.get_logger().info(f'🚗 Going to {self.brain.target}')
            self._send_navigation_goal(
                self.brain.target.x, self.brain.target.y,
                stop_distance=self.stop_distance)

        elif state == 'WAIT_NAVIGATION':
            self.get_logger().info('⏳ Waiting for navigation...')

        elif state == 'PICK':
            self.get_logger().info('🤖 Picking object...')
            self.brain.on_pick_completed()

        elif state == 'GO_TO_BOX':
            self.get_logger().info(
                f'📦 Moving to box ({self.brain.box_x:.1f}, '
                f'{self.brain.box_y:.1f})')
            self._send_navigation_goal(self.brain.box_x, self.brain.box_y)

        elif state == 'WAIT_NAVIGATION_TO_BOX':
            self.get_logger().info('⏳ Going to box...')

        elif state == 'DROP':
            self.get_logger().info('🧺 Dropping object...')
            self.brain.on_drop_completed()

    def _send_navigation_goal(self, x, y, stop_distance=0.0):
        """Send a navigation goal to Nav2."""
        goal_x, goal_y = x, y
        qz = 0.0
        qw = 1.0

        # Face the original target; optionally stop before it.
        robot_position = self.tf_transformer.lookup_robot_position()
        if robot_position is not None:
            robot_x, robot_y = robot_position
            if stop_distance > 0.0:
                goal_x, goal_y = self.tf_transformer.approach_position(
                    robot_x, robot_y, x, y, stop_distance)
            qz, qw = self.tf_transformer.quaternion_to_face_target(
                robot_x, robot_y, x, y)

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = PoseStamped()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.pose.position.x = goal_x
        goal_msg.pose.pose.position.y = goal_y
        goal_msg.pose.pose.orientation.z = qz
        goal_msg.pose.pose.orientation.w = qw

        self._action_client.wait_for_server()
        send_goal_future = self._action_client.send_goal_async(goal_msg)
        send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        """Handle Nav2 goal response."""
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().info('❌ Goal rejected')
            self.brain.on_navigation_rejected()
            return

        self.get_logger().info('✅ Goal accepted')
        self.brain.on_navigation_accepted()

        get_result_future = goal_handle.get_result_async()
        get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        """Handle Nav2 goal completion."""
        future.result().result
        self.get_logger().info('🏁 Navigation finished!')
        self.brain.on_navigation_finished()


def main():
    """Entry point."""
    rclpy.init()
    node = BrainNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
