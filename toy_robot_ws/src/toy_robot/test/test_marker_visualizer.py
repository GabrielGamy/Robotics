from visualization_msgs.msg import Marker

from toy_robot.visualization.marker_visualizer import MarkerVisualizer


class FakeNow:
    """Minimal now() object returning a marker-compatible timestamp."""

    def to_msg(self):
        """Return a timestamp-like object used by marker headers."""
        return object()


class FakeClock:
    """Minimal clock object for testing."""

    def now(self):
        """Return a deterministic now-like object."""
        return FakeNow()


class FakePublisher:
    """Collect published ROS messages for assertions."""

    def __init__(self):
        """Initialize message storage."""
        self.published = []

    def publish(self, msg):
        """Store each published message in order."""
        self.published.append(msg)


class FakeNode:
    """Minimal Node interface required by MarkerVisualizer."""

    def __init__(self):
        """Create fake node with one marker publisher."""
        self.publisher = FakePublisher()

    def create_publisher(self, _msg_type, _topic, _queue_size):
        """Return the fake publisher used in tests."""
        return self.publisher

    def get_clock(self):
        """Return fake clock for timestamp generation."""
        return FakeClock()


class TestMarkerVisualizer:
    """Targeted unit tests for RViz marker publication logic."""

    def setup_method(self):
        """Create a visualizer instance per test."""
        self.node = FakeNode()
        self.visualizer = MarkerVisualizer(
            self.node,
            frame_id='map',
            lifetime_sec=2.0,
            target_scale=0.2,
            goal_length=0.5,
            goal_width=0.1,
            direction_line_width=0.04,
        )

    def test_init_publishes_deleteall(self):
        """Visualizer startup should clear stale markers once."""
        assert len(self.node.publisher.published) == 1
        assert self.node.publisher.published[0].action == Marker.DELETEALL

    def test_publish_target_marker(self):
        """Target marker should be a green sphere with configured scale."""
        self.visualizer.publish_target(1.2, -0.4)

        marker = self.node.publisher.published[-1]
        assert marker.ns == 'target'
        assert marker.id == 0
        assert marker.type == Marker.SPHERE
        assert marker.pose.position.x == 1.2
        assert marker.pose.position.y == -0.4
        assert marker.scale.x == 0.2
        assert marker.scale.y == 0.2
        assert marker.scale.z == 0.2
        assert marker.color.g == 0.9

    def test_publish_goal_marker(self):
        """Goal marker should be a blue arrow with given orientation."""
        self.visualizer.publish_goal(0.3, 0.7, qz=0.5, qw=0.866)

        marker = self.node.publisher.published[-1]
        assert marker.ns == 'goal'
        assert marker.id == 0
        assert marker.type == Marker.ARROW
        assert marker.pose.position.x == 0.3
        assert marker.pose.position.y == 0.7
        assert marker.pose.orientation.z == 0.5
        assert marker.pose.orientation.w == 0.866
        assert marker.scale.x == 0.5
        assert marker.scale.y == 0.1
        assert marker.scale.z == 0.1
        assert marker.color.b == 1.0

    def test_publish_direction_line(self):
        """Direction marker should draw a 2-point line strip."""
        self.visualizer.publish_direction_line(-1.0, 0.5, 2.0, -0.5)

        marker = self.node.publisher.published[-1]
        assert marker.ns == 'direction'
        assert marker.id == 0
        assert marker.type == Marker.LINE_STRIP
        assert marker.scale.x == 0.04
        assert len(marker.points) == 2
        assert marker.points[0].x == -1.0
        assert marker.points[0].y == 0.5
        assert marker.points[1].x == 2.0
        assert marker.points[1].y == -0.5

    def test_positive_lifetime_sets_duration(self):
        """Configured positive lifetime should be copied to markers."""
        self.visualizer.publish_target(0.0, 0.0)

        marker = self.node.publisher.published[-1]
        assert marker.lifetime.sec == 2
