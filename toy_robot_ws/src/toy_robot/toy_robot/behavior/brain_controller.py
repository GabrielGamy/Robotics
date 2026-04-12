from enum import Enum

from toy_robot.models.target import Target


class RobotState(Enum):
    """State machine states."""

    SEARCHING = 'SEARCHING'
    GO_TO_SEARCH_SPIN = 'GO_TO_SEARCH_SPIN'
    WAIT_SEARCH_SPIN = 'WAIT_SEARCH_SPIN'
    GO_TO_OBJECT = 'GO_TO_OBJECT'
    WAIT_NAVIGATION = 'WAIT_NAVIGATION'
    PICK = 'PICK'
    GO_TO_BOX = 'GO_TO_BOX'
    WAIT_NAVIGATION_TO_BOX = 'WAIT_NAVIGATION_TO_BOX'
    DROP = 'DROP'


class BrainController:
    """Pure logic for the robot's behavior state machine (no ROS dependencies)."""

    def __init__(self, box_x=0.0, box_y=0.0, max_search_attempts=8):
        """Initialize controller.

        Args:
            box_x: X coordinate of the drop-off box in map frame.
            box_y: Y coordinate of the drop-off box in map frame.
            max_search_attempts: maximum scan spins before resetting cycle.
        """
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

    def on_object_detected(self, target: Target):
        """Handle a new object detection."""
        if self.state not in (
            RobotState.SEARCHING,
            RobotState.GO_TO_SEARCH_SPIN,
            RobotState.WAIT_SEARCH_SPIN,
        ):
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
            self.state = RobotState.PICK
        elif self.state == RobotState.WAIT_NAVIGATION_TO_BOX:
            self.state = RobotState.DROP

    def on_pick_completed(self):
        """Handle successful object pickup."""
        self.state = RobotState.GO_TO_BOX

    def on_drop_completed(self):
        """Handle successful object drop."""
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
