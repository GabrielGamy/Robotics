from types import SimpleNamespace

import pytest
import rclpy

HAS_INTERFACES = True
try:
    from toy_robot_interfaces.action import DropObject, PickObject
    from toy_robot.nodes.manipulation_node import ManipulationNode
except ModuleNotFoundError:
    HAS_INTERFACES = False
    DropObject = None
    PickObject = None
    ManipulationNode = None


class FakeGoalHandle:
    """Minimal action goal handle test double."""

    def __init__(self, request, cancel_immediately=False):
        self.request = request
        self._cancel_requested = cancel_immediately
        self.status = None
        self.feedback_phases = []

    @property
    def is_cancel_requested(self):
        return self._cancel_requested

    def publish_feedback(self, feedback):
        self.feedback_phases.append(feedback.phase)

    def succeed(self):
        self.status = 'succeeded'

    def abort(self):
        self.status = 'aborted'

    def canceled(self):
        self.status = 'canceled'


def _make_pick_goal_handle(x=1.0, y=0.2, cancel_immediately=False):
    request = SimpleNamespace(
        target=SimpleNamespace(
            point=SimpleNamespace(x=x, y=y, z=0.0)
        )
    )
    return FakeGoalHandle(request, cancel_immediately=cancel_immediately)


def _make_drop_goal_handle(x=0.0, y=0.0, cancel_immediately=False):
    request = SimpleNamespace(
        drop_zone=SimpleNamespace(
            point=SimpleNamespace(x=x, y=y, z=0.0)
        )
    )
    return FakeGoalHandle(request, cancel_immediately=cancel_immediately)


@pytest.mark.skipif(
    not HAS_INTERFACES,
    reason='toy_robot_interfaces is not available in the active Python path',
)
class TestManipulationNode:
    """Contract tests for manipulation action execute callbacks."""

    def setup_method(self):
        rclpy.init()
        self.node = ManipulationNode()
        self.node._step_duration_sec = 0.0

    def teardown_method(self):
        self.node.destroy_node()
        rclpy.shutdown()

    def test_pick_success_reports_expected_phases_and_result(self):
        goal_handle = _make_pick_goal_handle()

        result = self.node._execute_pick(goal_handle)

        assert goal_handle.status == 'succeeded'
        assert goal_handle.feedback_phases == [
            PickObject.Feedback.PHASE_APPROACHING,
            PickObject.Feedback.PHASE_GRASPING,
            PickObject.Feedback.PHASE_LIFTING,
        ]
        assert result.success is True
        assert result.result_code == PickObject.Result.RESULT_SUCCESS

    def test_pick_too_far_returns_expected_result_code(self):
        self.node._force_pick_too_far = True
        goal_handle = _make_pick_goal_handle()

        result = self.node._execute_pick(goal_handle)

        assert goal_handle.status == 'aborted'
        assert result.success is False
        assert result.result_code == PickObject.Result.RESULT_TOO_FAR

    def test_pick_cancel_returns_canceled_result_code(self):
        goal_handle = _make_pick_goal_handle(cancel_immediately=True)

        result = self.node._execute_pick(goal_handle)

        assert goal_handle.status == 'canceled'
        assert result.success is False
        assert result.result_code == PickObject.Result.RESULT_CANCELED

    def test_drop_success_reports_expected_phases_and_result(self):
        goal_handle = _make_drop_goal_handle()

        result = self.node._execute_drop(goal_handle)

        assert goal_handle.status == 'succeeded'
        assert goal_handle.feedback_phases == [
            DropObject.Feedback.PHASE_APPROACHING,
            DropObject.Feedback.PHASE_RELEASING,
            DropObject.Feedback.PHASE_RETREATING,
        ]
        assert result.success is True
        assert result.result_code == DropObject.Result.RESULT_SUCCESS

    def test_drop_too_far_returns_expected_result_code(self):
        self.node._force_drop_too_far = True
        goal_handle = _make_drop_goal_handle()

        result = self.node._execute_drop(goal_handle)

        assert goal_handle.status == 'aborted'
        assert result.success is False
        assert result.result_code == DropObject.Result.RESULT_TOO_FAR

    def test_drop_cancel_returns_canceled_result_code(self):
        goal_handle = _make_drop_goal_handle(cancel_immediately=True)

        result = self.node._execute_drop(goal_handle)

        assert goal_handle.status == 'canceled'
        assert result.success is False
        assert result.result_code == DropObject.Result.RESULT_CANCELED
