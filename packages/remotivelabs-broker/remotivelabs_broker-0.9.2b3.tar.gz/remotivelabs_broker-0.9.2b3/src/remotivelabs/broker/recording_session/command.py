from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from remotivelabs.broker.recording_session.offset import PlaybackOffset
from remotivelabs.broker.recording_session.repeat import PlaybackRepeat


@dataclass
class RecordingSessionPlaybackCommand:
    path: str
    command: PlaybackCommand
    offset: PlaybackOffset | None = None


@dataclass
class RecordingSessionRepeatCommand:
    path: str
    repeat: PlaybackRepeat | None = None


class PlaybackCommand(Enum):
    PLAYBACK_PLAY = 0
    """Play a file."""
    PLAYBACK_PAUSE = 1
    """Pause playback."""
    PLAYBACK_SEEK = 2
    """Seek to offset but keep current state."""
    PLAYBACK_CLOSE = 3
    """Stop and close playback."""
