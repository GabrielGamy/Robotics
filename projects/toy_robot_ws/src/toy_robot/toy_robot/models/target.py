from dataclasses import dataclass


@dataclass
class Target:
    """Represents a detected object target in the map frame."""

    x: float
    y: float
    source: str = 'camera'  # origin of detection

    def __repr__(self):
        """Return string representation."""
        return f'Target(x={self.x:.2f}, y={self.y:.2f}, source={self.source})'
