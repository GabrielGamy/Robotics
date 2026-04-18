import math

import rclpy
from geometry_msgs.msg import Point, PoseStamped
from nav2_msgs.action import NavigateToPose, Spin
from rclpy.action import ActionClient
from rclpy.duration import Duration
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
        self.declare_parameter('source_frame', 'camera_link')
        self.declare_parameter('target_frame', 'map')
        self.declare_parameter('cycle_time_ms', 2000)
        self.declare_parameter('tf_timeout_ms', 1000)
        self.declare_parameter('box_x', 0.0)
        self.declare_parameter('box_y', 0.0)
        self.declare_parameter('stop_distance', 0.3)
        self.declare_parameter('search_spin_yaw', math.pi / 2.0)
        self.declare_parameter('search_spin_time_allowance_sec', 10.0)
        self.declare_parameter('max_search_attempts', 8)

        # Get parameter values
        self.source_frame = self.get_parameter('source_frame').value
        self.target_frame = self.get_parameter('target_frame').value
        cycle_time_ms = self.get_parameter('cycle_time_ms').value
        tf_timeout_ms = self.get_parameter('tf_timeout_ms').value
        box_x = self.get_parameter('box_x').value
        box_y = self.get_parameter('box_y').value
        self.stop_distance = self.get_parameter('stop_distance').value
        self.search_spin_yaw = self.get_parameter('search_spin_yaw').value
        self.search_spin_time_allowance_sec = self.get_parameter(
            'search_spin_time_allowance_sec').value
        self.max_search_attempts = self.get_parameter(
            'max_search_attempts').value
        self.cycle_time_sec = float(cycle_time_ms) / 1000.0
        self.tf_timeout_sec = float(tf_timeout_ms) / 1000.0

        # ROS infrastructure
        self.subscription = self.create_subscription(
            Point,
            'detected_object_position',
            self.object_callback,
            10
        )
        self.timer = self.create_timer(self.cycle_time_sec, self.run_state_machine)
        self._action_client = ActionClient(
            self, NavigateToPose, 'navigate_to_pose')
        self._spin_client = ActionClient(self, Spin, 'spin')
        self._spin_goal_handle = None
        self._search_triggered = False

        # TF2
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # Logic layer (pure, testable)
        self.brain = BrainController(
            box_x=box_x,
            box_y=box_y,
            max_search_attempts=self.max_search_attempts,
        )
        self.tf_transformer = CoordinateTransformer(
            self.tf_buffer, self.get_logger())

        self.get_logger().info(
            f'🤖 Brain initialized with box at ({box_x}, {box_y}), '
            f'frames=({self.source_frame}->{self.target_frame}), '
            f'cycle={self.cycle_time_sec:.2f}s')

    def object_callback(self, msg):
        """Handle detected object position from perception."""
        # Transform point from camera frame to map frame
        result = self.tf_transformer.point_to_map(
            msg,
            self.source_frame,
            target_frame=self.target_frame,
            timeout_seconds=self.tf_timeout_sec,
        )

        if result is None:
            return

        x, y = result
        target = Target(x=x, y=y, source='camera')

        self._cancel_search_spin()

        # Notify brain controller
        if self.brain.on_object_detected(target):
            self._search_triggered = False
            self.get_logger().info(f'🧭 Target acquired: {target}')

    def run_state_machine(self):
        """Execute state machine transitions."""
        state = self.brain.state.value

        if state == 'SEARCHING':
            self.get_logger().info('🔍 Searching for objects...')
            if not self._search_triggered:
                self.brain.on_search_cycle()
                self._search_triggered = True

        elif state == 'GO_TO_SEARCH_SPIN':
            self.get_logger().info('🔄 Spinning to scan for objects...')
            self._send_search_spin_goal(self.search_spin_yaw)

        elif state == 'GO_TO_OBJECT':
            self.get_logger().info(f'🚗 Going to {self.brain.target}')
            self._send_navigation_goal(
                self.brain.target.x, self.brain.target.y,
                stop_distance=self.stop_distance)

        elif state == 'WAIT_NAVIGATION':
            self.get_logger().info('⏳ Waiting for navigation...')

        elif state == 'WAIT_SEARCH_SPIN':
            self.get_logger().info('⏳ Waiting for spin to complete...')

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
        self._cancel_search_spin()

        goal_x, goal_y = x, y
        qz = 0.0
        qw = 1.0

        # Face the original target; optionally stop before it.
        robot_position = self.tf_transformer.lookup_robot_position(
            target_frame=self.target_frame,
            timeout_seconds=self.tf_timeout_sec,
        )
        if robot_position is not None:
            robot_x, robot_y = robot_position
            if stop_distance > 0.0:
                goal_x, goal_y = self.tf_transformer.approach_position(
                    robot_x, robot_y, x, y, stop_distance)
            qz, qw = self.tf_transformer.quaternion_to_face_target(
                robot_x, robot_y, x, y)

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = PoseStamped()
        goal_msg.pose.header.frame_id = self.target_frame
        goal_msg.pose.pose.position.x = goal_x
        goal_msg.pose.pose.position.y = goal_y
        goal_msg.pose.pose.orientation.z = qz
        goal_msg.pose.pose.orientation.w = qw

        self._action_client.wait_for_server()
        send_goal_future = self._action_client.send_goal_async(goal_msg)
        send_goal_future.add_done_callback(self.goal_response_callback)

    def _send_search_spin_goal(self, yaw):
        """Send a spin action goal for search scan."""
        goal_msg = Spin.Goal()
        goal_msg.target_yaw = float(yaw)
        goal_msg.time_allowance = Duration(
            seconds=self.search_spin_time_allowance_sec).to_msg()

        self._spin_client.wait_for_server()
        send_goal_future = self._spin_client.send_goal_async(goal_msg)
        send_goal_future.add_done_callback(self.spin_goal_response_callback)

    def _cancel_search_spin(self):
        """Cancel an active search spin to avoid behavior conflicts."""
        if self._spin_goal_handle is not None:
            self._spin_goal_handle.cancel_goal_async()
            self._spin_goal_handle = None

    def spin_goal_response_callback(self, future):
        """Handle spin goal response."""
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().info('❌ Spin rejected')
            self.brain.on_spin_rejected()
            self._search_triggered = False
            return

        self.get_logger().info('✅ Spin accepted')
        self._spin_goal_handle = goal_handle
        self.brain.on_spin_accepted()

        get_result_future = goal_handle.get_result_async()
        get_result_future.add_done_callback(self.spin_result_callback)

    def spin_result_callback(self, future):
        """Handle spin completion."""
        result = future.result().result
        if result.error_code != 0:
            self.get_logger().warn(
                f'Spin failed: code={result.error_code}, msg={result.error_msg}')

        self._spin_goal_handle = None
        self.brain.on_spin_finished()
        self._search_triggered = False

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
