import threading
import time

import pytest
import rclpy
from rclpy.action import ActionClient
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

HAS_INTERFACES = True
try:
    from action_msgs.msg import GoalStatus
    from geometry_msgs.msg import PointStamped
    from toy_robot.nodes.manipulation_node import ManipulationNode
    from toy_robot_interfaces.action import DropObject, PickObject
except ModuleNotFoundError:
    HAS_INTERFACES = False
    GoalStatus = None
    PointStamped = None
    ManipulationNode = None
    DropObject = None
    PickObject = None


def _wait_for(condition, timeout_sec=5.0, poll_sec=0.01):
    """Wait until condition() becomes True or timeout elapses."""
    deadline = time.monotonic() + timeout_sec
    while time.monotonic() < deadline:
        if condition():
            return True
        time.sleep(poll_sec)
    return condition()


@pytest.mark.skipif(
    not HAS_INTERFACES,
    reason='toy_robot_interfaces is not available in the active Python path',
)
class TestManipulationActionIntegration:
    """End-to-end tests for manipulation action transport and result contract."""

    def setup_method(self):
        rclpy.init()

        self.server_node = ManipulationNode()
        self.server_node._step_duration_sec = 0.0

        self.client_node = Node('test_pick_action_client')
        self.pick_client = ActionClient(self.client_node, PickObject, 'pick_object')
        self.drop_client = ActionClient(self.client_node, DropObject, 'drop_object')

        self.executor = MultiThreadedExecutor(num_threads=2)
        self.executor.add_node(self.server_node)
        self.executor.add_node(self.client_node)

        self.spin_thread = threading.Thread(target=self.executor.spin, daemon=True)
        self.spin_thread.start()

        assert self.pick_client.wait_for_server(timeout_sec=2.0)
        assert self.drop_client.wait_for_server(timeout_sec=2.0)

    def teardown_method(self):
        self.drop_client.destroy()
        self.pick_client.destroy()
        self.executor.shutdown()
        self.server_node.destroy_node()
        self.client_node.destroy_node()
        rclpy.shutdown()
        self.spin_thread.join(timeout=1.0)

    def _send_pick_goal(self, x=1.0, y=0.3):
        feedback_phases = []

        goal_msg = PickObject.Goal()
        goal_msg.target = PointStamped()
        goal_msg.target.header.frame_id = 'map'
        goal_msg.target.point.x = x
        goal_msg.target.point.y = y
        goal_msg.target.point.z = 0.0

        send_goal_future = self.pick_client.send_goal_async(
            goal_msg,
            feedback_callback=lambda msg: feedback_phases.append(msg.feedback.phase),
        )
        assert _wait_for(send_goal_future.done)

        goal_handle = send_goal_future.result()
        assert goal_handle.accepted

        get_result_future = goal_handle.get_result_async()
        assert _wait_for(get_result_future.done)

        return get_result_future.result(), feedback_phases

    def _send_drop_goal(self, x=0.0, y=0.0):
        feedback_phases = []

        goal_msg = DropObject.Goal()
        goal_msg.drop_zone = PointStamped()
        goal_msg.drop_zone.header.frame_id = 'map'
        goal_msg.drop_zone.point.x = x
        goal_msg.drop_zone.point.y = y
        goal_msg.drop_zone.point.z = 0.0

        send_goal_future = self.drop_client.send_goal_async(
            goal_msg,
            feedback_callback=lambda msg: feedback_phases.append(msg.feedback.phase),
        )
        assert _wait_for(send_goal_future.done)

        goal_handle = send_goal_future.result()
        assert goal_handle.accepted

        get_result_future = goal_handle.get_result_async()
        assert _wait_for(get_result_future.done)

        return get_result_future.result(), feedback_phases

    def test_pick_action_success_end_to_end(self):
        self.server_node._force_pick_too_far = False

        goal_result, feedback_phases = self._send_pick_goal()

        assert goal_result.status == GoalStatus.STATUS_SUCCEEDED
        assert goal_result.result.success is True
        assert goal_result.result.result_code == PickObject.Result.RESULT_SUCCESS
        assert feedback_phases == [
            PickObject.Feedback.PHASE_APPROACHING,
            PickObject.Feedback.PHASE_GRASPING,
            PickObject.Feedback.PHASE_LIFTING,
        ]

    def test_pick_action_too_far_end_to_end(self):
        self.server_node._force_pick_too_far = True

        goal_result, feedback_phases = self._send_pick_goal()

        assert goal_result.status == GoalStatus.STATUS_ABORTED
        assert goal_result.result.success is False
        assert goal_result.result.result_code == PickObject.Result.RESULT_TOO_FAR
        assert feedback_phases == []

    def test_drop_action_success_end_to_end(self):
        self.server_node._force_drop_too_far = False

        goal_result, feedback_phases = self._send_drop_goal()

        assert goal_result.status == GoalStatus.STATUS_SUCCEEDED
        assert goal_result.result.success is True
        assert goal_result.result.result_code == DropObject.Result.RESULT_SUCCESS
        assert feedback_phases == [
            DropObject.Feedback.PHASE_APPROACHING,
            DropObject.Feedback.PHASE_RELEASING,
            DropObject.Feedback.PHASE_RETREATING,
        ]

    def test_drop_action_too_far_end_to_end(self):
        self.server_node._force_drop_too_far = True

        goal_result, feedback_phases = self._send_drop_goal()

        assert goal_result.status == GoalStatus.STATUS_ABORTED
        assert goal_result.result.success is False
        assert goal_result.result.result_code == DropObject.Result.RESULT_TOO_FAR
        assert feedback_phases == []
