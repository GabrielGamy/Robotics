import time

import rclpy
from rclpy.action import ActionServer
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node

from toy_robot_interfaces.action import DropObject, PickObject


class ManipulationNode(Node):
    """Simulated manipulation action servers for pick and drop."""

    def __init__(self):
        """Initialize manipulation action servers."""
        super().__init__('manipulation_node')

        self.declare_parameter('simulation_step_duration_sec', 0.5)
        self.declare_parameter('force_pick_too_far', False)
        self.declare_parameter('force_drop_too_far', False)

        self._step_duration_sec = float(
            self.get_parameter('simulation_step_duration_sec').value)
        self._force_pick_too_far = bool(self.get_parameter('force_pick_too_far').value)
        self._force_drop_too_far = bool(self.get_parameter('force_drop_too_far').value)

        self._pick_server = ActionServer(
            self,
            PickObject,
            'pick_object',
            execute_callback=self._execute_pick,
        )
        self._drop_server = ActionServer(
            self,
            DropObject,
            'drop_object',
            execute_callback=self._execute_drop,
        )

        self.get_logger().info('Manipulation node ready: /pick_object, /drop_object')

    def destroy_node(self):
        """Release action server resources before node destruction."""
        self._pick_server.destroy()
        self._drop_server.destroy()
        super().destroy_node()

    def _execute_pick(self, goal_handle):
        """Simulate a pick action execution."""
        target = goal_handle.request.target.point
        self.get_logger().info(
            f'Received pick goal at ({target.x:.2f}, {target.y:.2f})')

        if self._force_pick_too_far:
            goal_handle.abort()
            result = PickObject.Result()
            result.success = False
            result.result_code = PickObject.Result.RESULT_TOO_FAR
            result.message = 'Target too far to pick'
            return result

        for phase in (
            PickObject.Feedback.PHASE_APPROACHING,
            PickObject.Feedback.PHASE_GRASPING,
            PickObject.Feedback.PHASE_LIFTING,
        ):
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                result = PickObject.Result()
                result.success = False
                result.result_code = PickObject.Result.RESULT_CANCELED
                result.message = 'Pick goal canceled'
                return result

            feedback = PickObject.Feedback()
            feedback.phase = phase
            goal_handle.publish_feedback(feedback)
            time.sleep(self._step_duration_sec)

        goal_handle.succeed()
        result = PickObject.Result()
        result.success = True
        result.result_code = PickObject.Result.RESULT_SUCCESS
        result.message = 'Pick completed successfully'
        return result

    def _execute_drop(self, goal_handle):
        """Simulate a drop action execution."""
        drop_zone = goal_handle.request.drop_zone.point
        self.get_logger().info(
            f'Received drop goal at ({drop_zone.x:.2f}, {drop_zone.y:.2f})')

        if self._force_drop_too_far:
            goal_handle.abort()
            result = DropObject.Result()
            result.success = False
            result.result_code = DropObject.Result.RESULT_TOO_FAR
            result.message = 'Drop zone too far'
            return result

        for phase in (
            DropObject.Feedback.PHASE_APPROACHING,
            DropObject.Feedback.PHASE_RELEASING,
            DropObject.Feedback.PHASE_RETREATING,
        ):
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                result = DropObject.Result()
                result.success = False
                result.result_code = DropObject.Result.RESULT_CANCELED
                result.message = 'Drop goal canceled'
                return result

            feedback = DropObject.Feedback()
            feedback.phase = phase
            goal_handle.publish_feedback(feedback)
            time.sleep(self._step_duration_sec)

        goal_handle.succeed()
        result = DropObject.Result()
        result.success = True
        result.result_code = DropObject.Result.RESULT_SUCCESS
        result.message = 'Drop completed successfully'
        return result


def main():
    """Entry point."""
    rclpy.init()
    node = ManipulationNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()