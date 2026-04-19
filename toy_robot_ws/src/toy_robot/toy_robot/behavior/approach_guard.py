class ApproachGuard:
    """Track re-approach attempts and compute effective distance threshold."""

    def __init__(self, threshold, margin, stop_distance, max_attempts):
        """Configure guard with distance parameters and attempt limit."""
        self._threshold = float(threshold)
        self._margin = float(margin)
        self._stop_distance = float(stop_distance)
        self._max_attempts = int(max_attempts)
        self._attempts = 0

    @property
    def effective_threshold(self):
        """Return the stricter of the configured threshold and stop+margin."""
        return max(self._threshold, self._stop_distance + self._margin)

    @property
    def attempts(self):
        """Return current number of re-approach attempts."""
        return self._attempts

    @property
    def max_attempts(self):
        """Return maximum allowed re-approach attempts."""
        return self._max_attempts

    def is_close_enough(self, distance):
        """Return True if distance is within effective threshold."""
        return distance <= self.effective_threshold

    def register_attempt(self):
        """Increment attempt counter and return True if limit is exceeded."""
        self._attempts += 1
        return self._attempts > self._max_attempts

    def reset(self):
        """Reset attempt counter."""
        self._attempts = 0
