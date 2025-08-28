from __future__ import annotations

from remotivelabs.broker._generated import recordingsession_api_pb2 as recordingsession__api__pb2
from remotivelabs.broker.recording_session.offset import PlaybackOffset
from remotivelabs.broker.recording_session.repeat import PlaybackRepeat
from remotivelabs.broker.recording_session.status import PlaybackStatus, RecordingSessionPlaybackStatus


def status_from_grpc(
    status: recordingsession__api__pb2.RecordingSessionPlaybackStatus,
) -> RecordingSessionPlaybackStatus:
    return RecordingSessionPlaybackStatus(
        path=status.path,
        status=PlaybackStatus(status.status),
        offset=PlaybackOffset(status.offset.offsetTime) if status.HasField("offset") else PlaybackOffset(0),
        repeat=PlaybackRepeat(
            cycle_start_time=status.repeat.cycleStartTime,
            cycle_end_time=status.repeat.cycleEndTime,
        )
        if status.HasField("repeat")
        else None,
    )
