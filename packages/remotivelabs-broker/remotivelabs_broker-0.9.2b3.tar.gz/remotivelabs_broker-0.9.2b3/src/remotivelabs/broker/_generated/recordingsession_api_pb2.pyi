from remotivelabs.broker._generated import common_pb2 as _common_pb2
from remotivelabs.broker._generated import traffic_api_pb2 as _traffic_api_pb2
from remotivelabs.broker._generated.google.api import annotations_pb2 as _annotations_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FileType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FILE_TYPE_UNKNOWN: _ClassVar[FileType]
    FILE_TYPE_FOLDER: _ClassVar[FileType]
    FILE_TYPE_VIDEO: _ClassVar[FileType]
    FILE_TYPE_AUDIO: _ClassVar[FileType]
    FILE_TYPE_IMAGE: _ClassVar[FileType]
    FILE_TYPE_RECORDING: _ClassVar[FileType]
    FILE_TYPE_RECORDING_SESSION: _ClassVar[FileType]
    FILE_TYPE_RECORDING_MAPPING: _ClassVar[FileType]
    FILE_TYPE_PLATFORM: _ClassVar[FileType]
    FILE_TYPE_INSTANCE: _ClassVar[FileType]
    FILE_TYPE_SIGNAL_DATABASE: _ClassVar[FileType]

class PlaybackCommand(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PLAYBACK_PLAY: _ClassVar[PlaybackCommand]
    PLAYBACK_PAUSE: _ClassVar[PlaybackCommand]
    PLAYBACK_SEEK: _ClassVar[PlaybackCommand]
    PLAYBACK_CLOSE: _ClassVar[PlaybackCommand]

class PlaybackStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PLAYBACK_PLAYING: _ClassVar[PlaybackStatus]
    PLAYBACK_PAUSED: _ClassVar[PlaybackStatus]
    PLAYBACK_CLOSED: _ClassVar[PlaybackStatus]
FILE_TYPE_UNKNOWN: FileType
FILE_TYPE_FOLDER: FileType
FILE_TYPE_VIDEO: FileType
FILE_TYPE_AUDIO: FileType
FILE_TYPE_IMAGE: FileType
FILE_TYPE_RECORDING: FileType
FILE_TYPE_RECORDING_SESSION: FileType
FILE_TYPE_RECORDING_MAPPING: FileType
FILE_TYPE_PLATFORM: FileType
FILE_TYPE_INSTANCE: FileType
FILE_TYPE_SIGNAL_DATABASE: FileType
PLAYBACK_PLAY: PlaybackCommand
PLAYBACK_PAUSE: PlaybackCommand
PLAYBACK_SEEK: PlaybackCommand
PLAYBACK_CLOSE: PlaybackCommand
PLAYBACK_PLAYING: PlaybackStatus
PLAYBACK_PAUSED: PlaybackStatus
PLAYBACK_CLOSED: PlaybackStatus

class FileListingRequest(_message.Message):
    __slots__ = ("path", "types")
    PATH_FIELD_NUMBER: _ClassVar[int]
    TYPES_FIELD_NUMBER: _ClassVar[int]
    path: str
    types: _containers.RepeatedScalarFieldContainer[FileType]
    def __init__(self, path: _Optional[str] = ..., types: _Optional[_Iterable[_Union[FileType, str]]] = ...) -> None: ...

class FileListingResponse(_message.Message):
    __slots__ = ("files",)
    FILES_FIELD_NUMBER: _ClassVar[int]
    files: _containers.RepeatedCompositeFieldContainer[File]
    def __init__(self, files: _Optional[_Iterable[_Union[File, _Mapping]]] = ...) -> None: ...

class File(_message.Message):
    __slots__ = ("path", "type", "createdTime", "modifiedTime", "size")
    PATH_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    CREATEDTIME_FIELD_NUMBER: _ClassVar[int]
    MODIFIEDTIME_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    path: str
    type: FileType
    createdTime: int
    modifiedTime: int
    size: int
    def __init__(self, path: _Optional[str] = ..., type: _Optional[_Union[FileType, str]] = ..., createdTime: _Optional[int] = ..., modifiedTime: _Optional[int] = ..., size: _Optional[int] = ...) -> None: ...

class RecordingSessionPlaybackStatus(_message.Message):
    __slots__ = ("path", "status", "offset", "repeat")
    PATH_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    REPEAT_FIELD_NUMBER: _ClassVar[int]
    path: str
    status: PlaybackStatus
    offset: PlaybackOffset
    repeat: PlaybackRepeat
    def __init__(self, path: _Optional[str] = ..., status: _Optional[_Union[PlaybackStatus, str]] = ..., offset: _Optional[_Union[PlaybackOffset, _Mapping]] = ..., repeat: _Optional[_Union[PlaybackRepeat, _Mapping]] = ...) -> None: ...

class RecordingSessionPlaybackStatuses(_message.Message):
    __slots__ = ("items",)
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[RecordingSessionPlaybackStatus]
    def __init__(self, items: _Optional[_Iterable[_Union[RecordingSessionPlaybackStatus, _Mapping]]] = ...) -> None: ...

class RecordingSessionPlaybackCommand(_message.Message):
    __slots__ = ("path", "command", "offset")
    PATH_FIELD_NUMBER: _ClassVar[int]
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    path: str
    command: PlaybackCommand
    offset: PlaybackOffset
    def __init__(self, path: _Optional[str] = ..., command: _Optional[_Union[PlaybackCommand, str]] = ..., offset: _Optional[_Union[PlaybackOffset, _Mapping]] = ...) -> None: ...

class RecordingSessionRepeatCommand(_message.Message):
    __slots__ = ("path", "repeat")
    PATH_FIELD_NUMBER: _ClassVar[int]
    REPEAT_FIELD_NUMBER: _ClassVar[int]
    path: str
    repeat: PlaybackRepeat
    def __init__(self, path: _Optional[str] = ..., repeat: _Optional[_Union[PlaybackRepeat, _Mapping]] = ...) -> None: ...

class PlaybackOffset(_message.Message):
    __slots__ = ("offsetTime",)
    OFFSETTIME_FIELD_NUMBER: _ClassVar[int]
    offsetTime: int
    def __init__(self, offsetTime: _Optional[int] = ...) -> None: ...

class PlaybackRepeat(_message.Message):
    __slots__ = ("cycleStartTime", "cycleEndTime")
    CYCLESTARTTIME_FIELD_NUMBER: _ClassVar[int]
    CYCLEENDTIME_FIELD_NUMBER: _ClassVar[int]
    cycleStartTime: int
    cycleEndTime: int
    def __init__(self, cycleStartTime: _Optional[int] = ..., cycleEndTime: _Optional[int] = ...) -> None: ...
