from toy_robot.behavior.brain_controller import BrainController, RobotState
from toy_robot.models.target import Target


class TestBrainController:
    """Unit tests for BrainController (pure logic, no ROS)."""

    def setup_method(self):
        """Create a fresh brain controller for each test."""
        self.brain = BrainController(box_x=1.0, box_y=2.0)

    def test_initial_state(self):
        """Brain should start in SEARCHING state."""
        assert self.brain.state == RobotState.SEARCHING
        assert self.brain.target is None

    def test_object_detection_while_searching(self):
        """Should accept object detection while searching."""
        target = Target(x=0.5, y=0.3, source='camera')

        result = self.brain.on_object_detected(target)

        assert result is True
        assert self.brain.state == RobotState.GO_TO_OBJECT
        assert self.brain.target == target

    def test_object_detection_ignored_while_navigating(self):
        """Should ignore object detections while navigating."""
        # First detection
        target1 = Target(x=0.5, y=0.3, source='camera')
        self.brain.on_object_detected(target1)
        assert self.brain.state == RobotState.GO_TO_OBJECT

        # Second detection (should be ignored)
        target2 = Target(x=1.5, y=1.3, source='camera')
        result = self.brain.on_object_detected(target2)

        assert result is False
        assert self.brain.target == target1  # Still the first target

    def test_navigation_accepted(self):
        """State should transition to WAIT_NAVIGATION when goal accepted."""
        target = Target(x=0.5, y=0.3, source='camera')
        self.brain.on_object_detected(target)

        self.brain.on_navigation_accepted()

        assert self.brain.state == RobotState.WAIT_NAVIGATION

    def test_navigation_rejected(self):
        """Should return to SEARCHING when goal rejected."""
        target = Target(x=0.5, y=0.3, source='camera')
        self.brain.on_object_detected(target)

        self.brain.on_navigation_rejected()

        assert self.brain.state == RobotState.SEARCHING
        assert self.brain.target is None

    def test_pick_transitions_to_go_to_box(self):
        """Pick action success should transition to GO_TO_BOX."""
        target = Target(x=0.5, y=0.3, source='camera')
        self.brain.on_object_detected(target)
        self.brain.on_navigation_accepted()
        self.brain.on_navigation_finished()

        assert self.brain.state == RobotState.SEND_PICK_ACTION

        self.brain.on_pick_action_accepted()
        assert self.brain.state == RobotState.WAIT_PICK_RESULT

        self.brain.on_pick_completed()

        assert self.brain.state == RobotState.GO_TO_BOX

    def test_complete_cycle(self):
        """Test a complete search -> navigate -> pick -> drop cycle."""
        # Start searching
        assert self.brain.state == RobotState.SEARCHING

        # Detect object
        target = Target(x=0.5, y=0.3, source='camera')
        self.brain.on_object_detected(target)
        assert self.brain.state == RobotState.GO_TO_OBJECT

        # Send navigation goal
        self.brain.on_navigation_accepted()
        assert self.brain.state == RobotState.WAIT_NAVIGATION

        # Navigation succeeds, transition to pick action send
        self.brain.on_navigation_finished()
        assert self.brain.state == RobotState.SEND_PICK_ACTION

        # Pick action accepted, wait for result
        self.brain.on_pick_action_accepted()
        assert self.brain.state == RobotState.WAIT_PICK_RESULT

        # Pick completed, go to box
        self.brain.on_pick_completed()
        assert self.brain.state == RobotState.GO_TO_BOX

        # Send navigation to box
        self.brain.on_navigation_accepted()
        assert self.brain.state == RobotState.WAIT_NAVIGATION_TO_BOX

        # Navigation to box succeeds, transition to drop action send
        self.brain.on_navigation_finished()
        assert self.brain.state == RobotState.SEND_DROP_ACTION

        # Drop action accepted, wait for result
        self.brain.on_drop_action_accepted()
        assert self.brain.state == RobotState.WAIT_DROP_RESULT

        # Drop completed, back to searching
        self.brain.on_drop_completed()
        assert self.brain.state == RobotState.SEARCHING
        assert self.brain.target is None

    def test_get_navigation_goal_to_object(self):
        """Should return correct goal coordinates when going to object."""
        target = Target(x=1.5, y=0.8, source='camera')
        self.brain.on_object_detected(target)

        goal = self.brain.get_navigation_goal()

        assert goal == (1.5, 0.8, False)

    def test_get_navigation_goal_to_box(self):
        """Should return box coordinates when going to box."""
        # Simulate state transition to GO_TO_BOX
        self.brain.state = RobotState.GO_TO_BOX

        goal = self.brain.get_navigation_goal()

        assert goal == (1.0, 2.0, True)

    def test_get_navigation_goal_while_searching(self):
        """Should return None when searching (no goal)."""
        goal = self.brain.get_navigation_goal()

        assert goal is None

    def test_multiple_detections_cycle(self):
        """Should properly handle detecting multiple objects in sequence."""
        # First object
        target1 = Target(x=0.5, y=0.3, source='camera')
        self.brain.on_object_detected(target1)
        self.brain.on_navigation_accepted()
        self.brain.on_navigation_finished()
        self.brain.on_pick_action_accepted()
        self.brain.on_pick_completed()
        self.brain.on_navigation_accepted()
        self.brain.on_navigation_finished()
        self.brain.on_drop_action_accepted()
        self.brain.on_drop_completed()

        # Should be back to searching
        assert self.brain.state == RobotState.SEARCHING

        # Second object
        target2 = Target(x=1.2, y=-0.5, source='camera')
        self.brain.on_object_detected(target2)

        assert self.brain.state == RobotState.GO_TO_OBJECT
        assert self.brain.target == target2

    def test_can_accept_detection_only_in_search_states(self):
        """Detection gating helper should match allowed search states."""
        assert self.brain.can_accept_detection() is True

        self.brain.state = RobotState.GO_TO_OBJECT
        assert self.brain.can_accept_detection() is False

    def test_on_pick_too_far_reapproaches_target(self):
        """When pick is too far, controller should go back to object approach."""
        target = Target(x=0.6, y=-0.2, source='camera')
        self.brain.on_object_detected(target)
        self.brain.on_navigation_accepted()
        self.brain.on_navigation_finished()
        self.brain.on_pick_action_accepted()

        assert self.brain.state == RobotState.WAIT_PICK_RESULT

        self.brain.on_pick_too_far()

        assert self.brain.state == RobotState.GO_TO_OBJECT
        assert self.brain.target == target


class TestDropController:
    """Unit tests for drop-related BrainController events."""

    def setup_method(self):
        """Create a brain in WAIT_DROP_RESULT state."""
        self.brain = BrainController(box_x=1.0, box_y=2.0)
        target = Target(x=0.6, y=-0.2, source='camera')
        self.brain.on_object_detected(target)
        self.brain.on_navigation_accepted()
        self.brain.on_navigation_finished()
        self.brain.on_pick_action_accepted()
        self.brain.on_pick_completed()
        self.brain.on_navigation_accepted()
        self.brain.on_navigation_finished()
        self.brain.on_drop_action_accepted()
        assert self.brain.state == RobotState.WAIT_DROP_RESULT

    def test_on_drop_too_far_reapproaches_box(self):
        """When drop is too far, controller should go back to box approach."""
        self.brain.on_drop_too_far()

        assert self.brain.state == RobotState.GO_TO_BOX

    def test_rejected_pick_action_resets_to_searching(self):
        """Pick action rejection should reset to SEARCHING."""
        brain = BrainController(box_x=1.0, box_y=2.0)
        target = Target(x=0.5, y=0.3, source='camera')
        brain.on_object_detected(target)
        brain.on_navigation_accepted()
        brain.on_navigation_finished()

        assert brain.state == RobotState.SEND_PICK_ACTION

        brain.on_pick_action_rejected()

        assert brain.state == RobotState.SEARCHING
        assert brain.target is None

    def test_rejected_drop_action_resets_to_searching(self):
        """Drop action rejection should reset to SEARCHING."""
        self.brain.on_drop_action_rejected()

        assert self.brain.state == RobotState.SEARCHING
        assert self.brain.target is None

    def test_on_drop_failed_resets_to_searching(self):
        """Drop failure should reset to SEARCHING and clear target."""
        self.brain.on_drop_failed()

        assert self.brain.state == RobotState.SEARCHING
        assert self.brain.target is None
