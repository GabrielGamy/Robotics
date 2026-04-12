from enum import Enum

from toy_robot.models.target import Target


class RobotState(Enum):
    """State machine states."""

    SEARCHING = 'SEARCHING'
    GO_TO_OBJECT = 'GO_TO_OBJECT'
    WAIT_NAVIGATION = 'WAIT_NAVIGATION'
    PICK = 'PICK'
    GO_TO_BOX = 'GO_TO_BOX'
    WAIT_NAVIGATION_TO_BOX = 'WAIT_NAVIGATION_TO_BOX'
    DROP = 'DROP'


class BrainController:
    """Pure logic for the robot's behavior state machine (no ROS dependencies)."""

    def __init__(self, box_x=0.0, box_y=0.0):
        """Initialize controller.

        Args:
            box_x: X coordinate of the drop-off box in map frame.
            box_y: Y coordinate of the drop-off box in map frame.
        """
        self.state = RobotState.SEARCHING
        self.target: Target = None
        self.box_x = box_x
        self.box_y = box_y

    def on_object_detected(self, target: Target):
        """Handle a new object detection."""
        if self.state != RobotState.SEARCHING:
            return False  # ignore if not searching

        self.target = target
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
        self.state = RobotState.SEARCHING
        self.target = None

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
        self.target = None
        self.state = RobotState.SEARCHING

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
