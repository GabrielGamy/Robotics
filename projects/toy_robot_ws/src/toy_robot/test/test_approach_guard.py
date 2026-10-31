import pytest

from toy_robot.behavior.approach_guard import ApproachGuard


class TestApproachGuard:
    """Unit tests for ApproachGuard."""

    def _make_guard(self, threshold=0.5, margin=0.1, stop_distance=0.3, max_attempts=3):
        return ApproachGuard(
            threshold=threshold,
            margin=margin,
            stop_distance=stop_distance,
            max_attempts=max_attempts,
        )

    def test_effective_threshold_uses_configured_when_larger(self):
        """Threshold should be used when it is larger than stop+margin."""
        guard = self._make_guard(threshold=0.55, margin=0.15, stop_distance=0.3)

        assert guard.effective_threshold == pytest.approx(0.55)

    def test_effective_threshold_uses_stop_plus_margin_when_larger(self):
        """stop+margin should be used when it exceeds the configured threshold."""
        guard = self._make_guard(threshold=0.3, margin=0.15, stop_distance=0.3)

        assert guard.effective_threshold == pytest.approx(0.45)

    def test_is_close_enough_when_within_threshold(self):
        """Should return True when distance is within threshold."""
        guard = self._make_guard(threshold=0.55)

        assert guard.is_close_enough(0.4) is True

    def test_is_not_close_enough_when_beyond_threshold(self):
        """Should return False when distance exceeds threshold."""
        guard = self._make_guard(threshold=0.55)

        assert guard.is_close_enough(0.7) is False

    def test_register_attempt_returns_false_before_limit(self):
        """register_attempt should return False while under the limit."""
        guard = self._make_guard(max_attempts=3)

        assert guard.register_attempt() is False  # attempt 1
        assert guard.register_attempt() is False  # attempt 2
        assert guard.register_attempt() is False  # attempt 3

    def test_register_attempt_returns_true_when_limit_exceeded(self):
        """register_attempt should return True when over the limit."""
        guard = self._make_guard(max_attempts=3)

        for _ in range(3):
            guard.register_attempt()

        assert guard.register_attempt() is True  # attempt 4 > max

    def test_reset_clears_attempts(self):
        """reset() should bring attempt counter back to zero."""
        guard = self._make_guard(max_attempts=3)

        for _ in range(3):
            guard.register_attempt()

        guard.reset()

        assert guard.attempts == 0
        assert guard.register_attempt() is False  # back to normal
