import math

from action_msgs.msg import GoalStatus
from geometry_msgs.msg import Point, PoseStamped
from nav2_msgs.action import NavigateToPose, Spin
import rclpy
from rclpy.action import ActionClient
from rclpy.duration import Duration
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from tf2_ros import Buffer, TransformListener

from toy_robot.behavior.brain_controller import BrainController
from toy_robot.config.node_config import BrainNodeConfig, MarkerConfig
from toy_robot.models.target import Target
from toy_robot.tf.transformer import CoordinateTransformer
from toy_robot.visualization.marker_visualizer import MarkerVisualizer


class BrainNode(Node):
    """ROS2 node for robot behavior control."""

    def __init__(self):
        """Initialize brain node."""
        super().__init__('brain_node')

        self._declare_parameters()
        brain_node_config = self._load_parameters()

        self.source_frame = brain_node_config.source_frame
        self.target_frame = brain_node_config.target_frame
        self.cycle_time_sec = brain_node_config.cycle_time_sec
        self.tf_timeout_sec = brain_node_config.tf_timeout_sec
        self.stop_distance = brain_node_config.stop_distance
        self.pick_distance_threshold = brain_node_config.pick_distance_threshold
        self.pick_distance_margin = brain_node_config.pick_distance_margin
        self.max_pick_reapproach_attempts = (
            brain_node_config.max_pick_reapproach_attempts
        )
        self.search_spin_yaw = brain_node_config.search_spin_yaw
        self.search_spin_time_allowance_sec = brain_node_config.search_spin_time_allowance_sec
        self.max_search_attempts = brain_node_config.max_search_attempts
        self.show_direction_line = brain_node_config.marker.show_direction_line
        self._pick_reapproach_attempts = 0

        # ROS infrastructure
        self.subscription = self.create_subscription(
            Point,
            'detected_object_position',
            self.object_callback,
            10
        )
        self.timer = self.create_timer(self.cycle_time_sec, self.run_state_machine)
        self._action_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self._spin_client = ActionClient(self, Spin, 'spin')
        self._spin_goal_handle = None
        self._search_triggered = False

        # TF2
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # Logic layer (pure, testable)
        self.brain = BrainController(
            box_x=brain_node_config.box_x,
            box_y=brain_node_config.box_y,
            max_search_attempts=self.max_search_attempts,
        )

        self.tf_transformer = CoordinateTransformer(
            self.tf_buffer, self.get_logger())
        self.marker_visualizer = self._try_create_marker_visualizer(
            brain_node_config.marker)

        self.get_logger().info(
            f'🤖 Brain initialized with box at ('
            f'{brain_node_config.box_x}, {brain_node_config.box_y}), '
            f'frames=({self.source_frame}->{self.target_frame}), '
            f'cycle={self.cycle_time_sec:.2f}s')

    def _declare_parameters(self):
        """Declare all ROS parameters with safe defaults."""
        defaults = {
            'source_frame': 'camera_link',
            'target_frame': 'map',
            'cycle_time_ms': 2000,
            'tf_timeout_ms': 1000,
            'box_x': 0.0,
            'box_y': 0.0,
            'stop_distance': 0.3,
            'pick_distance_threshold': 0.4,
            'pick_distance_margin': 0.15,
            'max_pick_reapproach_attempts': 3,
            'search_spin_yaw': math.pi / 2.0,
            'search_spin_time_allowance_sec': 10.0,
            'max_search_attempts': 8,
            'visualization_enabled': True,
            'marker_lifetime_sec': 0.0,
            'target_marker_scale': 0.15,
            'goal_marker_length': 0.35,
            'goal_marker_width': 0.07,
            'show_direction_line': True,
            'direction_line_width': 0.03,
        }
        for name, value in defaults.items():
            self.declare_parameter(name, value)

    def _load_parameters(self):
        """Read ROS parameters and convert them to typed runtime config."""
        cycle_time_ms = self.get_parameter('cycle_time_ms').value
        tf_timeout_ms = self.get_parameter('tf_timeout_ms').value

        marker_config = MarkerConfig(
            enabled=self.get_parameter('visualization_enabled').value,
            lifetime_sec=self.get_parameter('marker_lifetime_sec').value,
            target_scale=self.get_parameter('target_marker_scale').value,
            goal_length=self.get_parameter('goal_marker_length').value,
            goal_width=self.get_parameter('goal_marker_width').value,
            show_direction_line=self.get_parameter('show_direction_line').value,
            direction_line_width=self.get_parameter('direction_line_width').value,
        )

        return BrainNodeConfig(
            source_frame=self.get_parameter('source_frame').value,
            target_frame=self.get_parameter('target_frame').value,
            cycle_time_sec=float(cycle_time_ms) / 1000.0,
            tf_timeout_sec=float(tf_timeout_ms) / 1000.0,
            box_x=self.get_parameter('box_x').value,
            box_y=self.get_parameter('box_y').value,
            stop_distance=self.get_parameter('stop_distance').value,
            pick_distance_threshold=self.get_parameter('pick_distance_threshold').value,
            pick_distance_margin=self.get_parameter('pick_distance_margin').value,
            max_pick_reapproach_attempts=self.get_parameter(
                'max_pick_reapproach_attempts').value,
            search_spin_yaw=self.get_parameter('search_spin_yaw').value,
            search_spin_time_allowance_sec=self.get_parameter(
                'search_spin_time_allowance_sec').value,
            max_search_attempts=self.get_parameter('max_search_attempts').value,
            marker=marker_config,
        )

    def _try_create_marker_visualizer(self, marker_config):
        """Create marker visualizer when debug visualization is enabled."""
        if not marker_config.enabled:
            return None

        return MarkerVisualizer(
            self,
            frame_id=self.target_frame,
            topic='visualization_marker',
            lifetime_sec=marker_config.lifetime_sec,
            target_scale=marker_config.target_scale,
            goal_length=marker_config.goal_length,
            goal_width=marker_config.goal_width,
            direction_line_width=marker_config.direction_line_width,
        )

    def _publish_detection_markers(self, x, y):
        """Publish target and optional direction markers for debug."""
        if self.marker_visualizer is None:
            return

        self.marker_visualizer.publish_target(x, y)

        if not self.show_direction_line:
            return

        robot_position = self.tf_transformer.lookup_robot_position(
            target_frame=self.target_frame,
            timeout_seconds=self.tf_timeout_sec,
        )
        if robot_position is None:
            return

        robot_x, robot_y = robot_position
        self.marker_visualizer.publish_direction_line(robot_x, robot_y, x, y)

    def object_callback(self, msg):
        """Handle detected object position from perception."""
        if not self.brain.can_accept_detection():
            return

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

        # Notify brain controller
        if self.brain.on_object_detected(target):
            self._publish_detection_markers(x, y)
            self._cancel_search_spin()
            self._pick_reapproach_attempts = 0
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
            pick_distance = self._compute_pick_distance()
            if pick_distance is None:
                self._handle_pick_reapproach(pick_distance)
                return

            effective_threshold = max(
                self.pick_distance_threshold,
                self.stop_distance + self.pick_distance_margin,
            )
            if pick_distance > effective_threshold:
                self._handle_pick_reapproach(
                    pick_distance, effective_threshold=effective_threshold)
                return

            self.get_logger().info('🤖 Picking object...')
            self._pick_reapproach_attempts = 0
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

        if self.marker_visualizer is not None:
            self.marker_visualizer.publish_goal(goal_x, goal_y, qz, qw)

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

    def _compute_pick_distance(self):
        """Return robot-to-target distance for pick, or None if unavailable."""
        if self.brain.target is None:
            return None

        robot_position = self.tf_transformer.lookup_robot_position(
            target_frame=self.target_frame,
            timeout_seconds=self.tf_timeout_sec,
        )
        if robot_position is None:
            return None

        robot_x, robot_y = robot_position
        target_x, target_y = self.brain.target.x, self.brain.target.y
        return math.hypot(target_x - robot_x, target_y - robot_y)

    def _handle_pick_reapproach(self, pick_distance, effective_threshold=None):
        """Retry approach before pick and abort cleanly after max attempts."""
        self._pick_reapproach_attempts += 1

        if self._pick_reapproach_attempts > self.max_pick_reapproach_attempts:
            self.get_logger().warn(
                '⚠️ Pick failed after max re-approach attempts. '
                'Dropping target and returning to SEARCHING.'
            )
            self._pick_reapproach_attempts = 0
            self.brain.on_pick_failed()
            self._search_triggered = False
            return

        if pick_distance is None:
            self.get_logger().warn(
                f'⚠️ Pick distance unavailable, re-approaching '
                f'({self._pick_reapproach_attempts}/'
                f'{self.max_pick_reapproach_attempts}).'
            )
        else:
            self.get_logger().warn(
                f'⚠️ Too far from target to pick '
                f'(dist={pick_distance:.2f}m, '
                f'threshold={effective_threshold:.2f}m). '
                f'Re-approaching '
                f'({self._pick_reapproach_attempts}/'
                f'{self.max_pick_reapproach_attempts}).'
            )

        self.brain.on_pick_too_far()

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
        goal_result = future.result()
        status = goal_result.status

        if status != GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().warn(
                f'⚠️ Navigation ended with status={status}, '
                'returning to SEARCHING.'
            )
            self.brain.on_navigation_rejected()
            self._search_triggered = False
            self._pick_reapproach_attempts = 0
            return

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
