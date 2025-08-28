from __future__ import annotations

import datetime

from remotivelabs.broker._generated import recordingsession_api_pb2 as recordingsession__api__pb2
from remotivelabs.broker.recording_session.file import File, FileType


def file_from_grpc(file: recordingsession__api__pb2.File) -> File:
    return File(
        path=file.path,
        type=FileType(file.type),
        created_time=datetime.datetime.fromtimestamp(file.createdTime),
        modified_time=datetime.datetime.fromtimestamp(file.modifiedTime),
        size=file.size,
    )


def file_to_grpc(file: File) -> recordingsession__api__pb2.File:
    return recordingsession__api__pb2.File(
        path=file.path,
        type=file.type.name,
        createdTime=int(file.created_time.timestamp()),
        modifiedTime=int(file.modified_time.timestamp()),
        size=file.size,
    )
