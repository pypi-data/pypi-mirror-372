from dataclasses import dataclass


@dataclass
class PlaybackRepeat:
    """Playback repeat settings."""

    cycle_start_time: int = 0
    """Current cycle start in micro seconds."""
    cycle_end_time: int = 0
    """Current cycle end in micro seconds."""
