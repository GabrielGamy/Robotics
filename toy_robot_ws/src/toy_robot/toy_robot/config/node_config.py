from dataclasses import dataclass


@dataclass
class MarkerConfig:
    """Marker visualization configuration."""

    enabled: bool
    lifetime_sec: float
    target_scale: float
    goal_length: float
    goal_width: float
    show_direction_line: bool
    direction_line_width: float


@dataclass
class BrainNodeConfig:
    """Runtime configuration for BrainNode."""

    source_frame: str
    target_frame: str
    cycle_time_sec: float
    tf_timeout_sec: float
    box_x: float
    box_y: float
    stop_distance: float
    pick_distance_threshold: float
    pick_distance_margin: float
    max_pick_reapproach_attempts: int
    drop_distance_threshold: float
    drop_distance_margin: float
    max_drop_reapproach_attempts: int
    search_spin_yaw: float
    search_spin_time_allowance_sec: float
    max_search_attempts: int
    marker: MarkerConfig
