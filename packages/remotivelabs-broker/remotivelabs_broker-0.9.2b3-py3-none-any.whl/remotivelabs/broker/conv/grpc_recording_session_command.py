from __future__ import annotations

from remotivelabs.broker._generated import recordingsession_api_pb2 as recordingsession__api__pb2
from remotivelabs.broker.recording_session.command import RecordingSessionPlaybackCommand, RecordingSessionRepeatCommand


def command_to_grpc(command: RecordingSessionPlaybackCommand) -> recordingsession__api__pb2.RecordingSessionPlaybackCommand:
    return recordingsession__api__pb2.RecordingSessionPlaybackCommand(
        path=command.path,
        command=command.command.name,
        offset=recordingsession__api__pb2.PlaybackOffset(offsetTime=command.offset.offset_time) if command.offset is not None else None,
    )


def repeat_to_grpc(command: RecordingSessionRepeatCommand) -> recordingsession__api__pb2.RecordingSessionRepeatCommand:
    return recordingsession__api__pb2.RecordingSessionRepeatCommand(
        path=command.path,
        repeat=recordingsession__api__pb2.PlaybackRepeat(
            cycleStartTime=command.repeat.cycle_start_time, cycleEndTime=command.repeat.cycle_end_time
        )
        if command.repeat is not None
        else None,
    )
