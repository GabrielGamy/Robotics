from enum import Enum

from toy_robot.models.target import Target


class RobotState(Enum):
    """State machine states."""

    # Idle search mode: wait for a valid perception target.
    SEARCHING = 'SEARCHING'
    # Trigger a spin navigation goal to scan the surroundings.
    GO_TO_SEARCH_SPIN = 'GO_TO_SEARCH_SPIN'
    # Spin goal was sent; wait for completion/rejection.
    WAIT_SEARCH_SPIN = 'WAIT_SEARCH_SPIN'
    # Send a navigation goal toward the detected object.
    GO_TO_OBJECT = 'GO_TO_OBJECT'
    # Navigation to object is in progress.
    WAIT_NAVIGATION = 'WAIT_NAVIGATION'
    # Send manipulation pick action goal.
    SEND_PICK_ACTION = 'SEND_PICK_ACTION'
    # Pick goal accepted; wait for action result.
    WAIT_PICK_RESULT = 'WAIT_PICK_RESULT'
    # Send a navigation goal toward the drop box.
    GO_TO_BOX = 'GO_TO_BOX'
    # Navigation to box is in progress.
    WAIT_NAVIGATION_TO_BOX = 'WAIT_NAVIGATION_TO_BOX'
    # Send manipulation drop action goal.
    SEND_DROP_ACTION = 'SEND_DROP_ACTION'
    # Drop goal accepted; wait for action result.
    WAIT_DROP_RESULT = 'WAIT_DROP_RESULT'


class BrainController:
    """Pure logic for the robot's behavior state machine (no ROS dependencies)."""

    def __init__(self, box_x=0.0, box_y=0.0, max_search_attempts=8):
        """Initialize controller with box coordinates and scan attempt limit."""
        self.state = RobotState.SEARCHING
        self.target: Target = None
        self.box_x = box_x
        self.box_y = box_y
        self.search_attempts = 0
        self.max_search_attempts = max_search_attempts

    def on_search_cycle(self):
        """Trigger one scan cycle while searching."""
        if self.state == RobotState.SEARCHING:
            self.state = RobotState.GO_TO_SEARCH_SPIN

    def on_spin_accepted(self):
        """Handle spin goal acceptance."""
        if self.state == RobotState.GO_TO_SEARCH_SPIN:
            self.state = RobotState.WAIT_SEARCH_SPIN

    def on_spin_rejected(self):
        """Handle spin goal rejection."""
        if self.state in (RobotState.GO_TO_SEARCH_SPIN, RobotState.WAIT_SEARCH_SPIN):
            self.state = RobotState.SEARCHING

    def on_spin_finished(self):
        """Handle spin completion and capped retry loop."""
        if self.state != RobotState.WAIT_SEARCH_SPIN:
            return

        self.search_attempts += 1
        if self.search_attempts >= self.max_search_attempts:
            self.state = RobotState.SEARCHING
            self.search_attempts = 0
        else:
            self.state = RobotState.GO_TO_SEARCH_SPIN

    def can_accept_detection(self):
        """Return whether a new detection can be accepted now."""
        return self.state in (
            RobotState.SEARCHING,
            RobotState.GO_TO_SEARCH_SPIN,
            RobotState.WAIT_SEARCH_SPIN,
        )

    def on_object_detected(self, target: Target):
        """Handle a new object detection."""
        if not self.can_accept_detection():
            return False  # ignore if not searching

        self.target = target
        self.search_attempts = 0
        self.state = RobotState.GO_TO_OBJECT
        return True

    def on_navigation_accepted(self):
        """Handle Nav2 accepting a goal."""
        if self.state == RobotState.GO_TO_OBJECT:
            self.state = RobotState.WAIT_NAVIGATION
        elif self.state == RobotState.GO_TO_BOX:
            self.state = RobotState.WAIT_NAVIGATION_TO_BOX

    def on_navigation_rejected(self):
        """Handle Nav2 rejecting a goal."""
        self._reset_search_mode()

    def on_navigation_finished(self):
        """Handle Nav2 finishing a goal."""
        if self.state == RobotState.WAIT_NAVIGATION:
            self.state = RobotState.SEND_PICK_ACTION
        elif self.state == RobotState.WAIT_NAVIGATION_TO_BOX:
            self.state = RobotState.SEND_DROP_ACTION

    def on_pick_action_accepted(self):
        """Handle pick action goal acceptance."""
        if self.state == RobotState.SEND_PICK_ACTION:
            self.state = RobotState.WAIT_PICK_RESULT

    def on_pick_action_rejected(self):
        """Handle pick action goal rejection."""
        self._reset_search_mode()

    def on_pick_completed(self):
        """Handle successful object pickup."""
        if self.state in (RobotState.SEND_PICK_ACTION, RobotState.WAIT_PICK_RESULT):
            self.state = RobotState.GO_TO_BOX

    def on_pick_failed(self):
        """Abort current target after too many failed pick attempts."""
        self._reset_search_mode()

    def on_pick_too_far(self):
        """Re-approach target when manipulation reports target too far."""
        if self.state not in (RobotState.SEND_PICK_ACTION, RobotState.WAIT_PICK_RESULT):
            return

        if self.target is None:
            self._reset_search_mode()
            return

        self.state = RobotState.GO_TO_OBJECT

    def on_drop_action_accepted(self):
        """Handle drop action goal acceptance."""
        if self.state == RobotState.SEND_DROP_ACTION:
            self.state = RobotState.WAIT_DROP_RESULT

    def on_drop_action_rejected(self):
        """Handle drop action goal rejection."""
        self._reset_search_mode()

    def on_drop_failed(self):
        """Abort drop after too many failed attempts."""
        self._reset_search_mode()

    def on_drop_too_far(self):
        """Re-approach box when manipulation reports drop zone too far."""
        if self.state not in (RobotState.SEND_DROP_ACTION, RobotState.WAIT_DROP_RESULT):
            return

        self.state = RobotState.GO_TO_BOX

    def on_drop_completed(self):
        """Handle successful object drop."""
        if self.state in (RobotState.SEND_DROP_ACTION, RobotState.WAIT_DROP_RESULT):
            self._reset_search_mode()

    def _reset_search_mode(self):
        """Reset controller to a clean searching state."""
        self.state = RobotState.SEARCHING
        self.target = None
        self.search_attempts = 0

    def get_navigation_goal(self):
        """Return navigation goal (x, y, is_box_goal)."""
        if self.state == RobotState.GO_TO_OBJECT and self.target:
            return (self.target.x, self.target.y, False)
        elif self.state == RobotState.GO_TO_BOX:
            return (self.box_x, self.box_y, True)
        return None

    def __repr__(self):
        """Return string representation."""
        return f'BrainController(state={self.state.value}, target={self.target})'
