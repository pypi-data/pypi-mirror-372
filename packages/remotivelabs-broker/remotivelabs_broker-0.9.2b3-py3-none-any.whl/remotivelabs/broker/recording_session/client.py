from __future__ import annotations

from typing import AsyncIterator

from grpc.aio import AioRpcError

from remotivelabs.broker._generated import common_pb2
from remotivelabs.broker._generated import recordingsession_api_pb2 as recordingsession__api__pb2
from remotivelabs.broker.client import BrokerClient
from remotivelabs.broker.conv.grpc_recording_session_command import command_to_grpc
from remotivelabs.broker.conv.grpc_recording_session_file import file_from_grpc
from remotivelabs.broker.conv.grpc_recording_session_status import status_from_grpc
from remotivelabs.broker.recording_session.command import RecordingSessionPlaybackCommand
from remotivelabs.broker.recording_session.file import File
from remotivelabs.broker.recording_session.status import RecordingSessionPlaybackError, RecordingSessionPlaybackStatus


class RecordingSessionClient(BrokerClient):
    """
    TODO: We probably dont want to inherit from BrokerClient, but rather use composition to hide functionality not relevant for recording
    session operations. However, this will do for now.
    """

    async def __aenter__(self) -> RecordingSessionClient:
        await super().__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await super().__aexit__(exc_type, exc_value, traceback)

    async def list_recording_files(self, path: str | None = None) -> list[File]:
        """
        List recording files in a directory.

        Args:
            path: Optional path to the subdirectory containing the recording files.
        """
        res = await self._recording_session_service.ListRecordingFiles(recordingsession__api__pb2.FileListingRequest(path=path))
        return [file_from_grpc(file) for file in res.files]

    def playback_status(self) -> AsyncIterator[list[RecordingSessionPlaybackStatus]]:
        """
        Get continuous status of all open recording sessions.
        """
        stream = self._recording_session_service.PlaybackStatus(common_pb2.Empty())

        async def async_generator() -> AsyncIterator[list[RecordingSessionPlaybackStatus]]:
            async for statuses in stream:
                status_list: list[recordingsession__api__pb2.RecordingSessionPlaybackStatus] = statuses.items
                yield [status_from_grpc(status) for status in status_list]

        return async_generator()

    async def perform_playback(
        self, command: RecordingSessionPlaybackCommand
    ) -> RecordingSessionPlaybackStatus | RecordingSessionPlaybackError:
        """
        Perform playback command.
        """
        grpc_command = command_to_grpc(command)
        try:
            res = await self._recording_session_service.PerformPlayback(grpc_command)
            return status_from_grpc(res)
        except AioRpcError as e:
            return RecordingSessionPlaybackError(e.details() or "Unknown error occurred")
