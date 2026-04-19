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
        """PICK state should transition to GO_TO_BOX."""
        target = Target(x=0.5, y=0.3, source='camera')
        self.brain.on_object_detected(target)
        self.brain.on_navigation_accepted()
        self.brain.on_navigation_finished()

        assert self.brain.state == RobotState.PICK

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

        # Navigation succeeds, transition to pick
        self.brain.on_navigation_finished()
        assert self.brain.state == RobotState.PICK

        # Pick completed, go to box
        self.brain.on_pick_completed()
        assert self.brain.state == RobotState.GO_TO_BOX

        # Send navigation to box
        self.brain.on_navigation_accepted()
        assert self.brain.state == RobotState.WAIT_NAVIGATION_TO_BOX

        # Navigation to box succeeds, drop
        self.brain.on_navigation_finished()
        assert self.brain.state == RobotState.DROP

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
        self.brain.on_pick_completed()
        self.brain.on_navigation_accepted()
        self.brain.on_navigation_finished()
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

        assert self.brain.state == RobotState.PICK

        self.brain.on_pick_too_far()

        assert self.brain.state == RobotState.GO_TO_OBJECT
        assert self.brain.target == target
