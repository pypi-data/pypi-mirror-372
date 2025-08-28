from remotivelabs.broker._generated import common_pb2 as _common_pb2
from remotivelabs.broker._generated import system_api_pb2 as _system_api_pb2
from remotivelabs.broker._generated.google.api import annotations_pb2 as _annotations_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Mode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PLAY: _ClassVar[Mode]
    PAUSE: _ClassVar[Mode]
    STOP: _ClassVar[Mode]
    RECORD: _ClassVar[Mode]
    SEEK: _ClassVar[Mode]
    CLOSE: _ClassVar[Mode]
PLAY: Mode
PAUSE: Mode
STOP: Mode
RECORD: Mode
SEEK: Mode
CLOSE: Mode

class PlaybackMode(_message.Message):
    __slots__ = ("errorMessage", "EOF", "mode", "offsetTime", "startTime", "endTime", "timeDeviation", "offsetWallClockVsSample", "noPlaybackToApplication", "playbackToBus")
    ERRORMESSAGE_FIELD_NUMBER: _ClassVar[int]
    EOF_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    OFFSETTIME_FIELD_NUMBER: _ClassVar[int]
    STARTTIME_FIELD_NUMBER: _ClassVar[int]
    ENDTIME_FIELD_NUMBER: _ClassVar[int]
    TIMEDEVIATION_FIELD_NUMBER: _ClassVar[int]
    OFFSETWALLCLOCKVSSAMPLE_FIELD_NUMBER: _ClassVar[int]
    NOPLAYBACKTOAPPLICATION_FIELD_NUMBER: _ClassVar[int]
    PLAYBACKTOBUS_FIELD_NUMBER: _ClassVar[int]
    errorMessage: str
    EOF: str
    mode: Mode
    offsetTime: int
    startTime: int
    endTime: int
    timeDeviation: int
    offsetWallClockVsSample: int
    noPlaybackToApplication: bool
    playbackToBus: bool
    def __init__(self, errorMessage: _Optional[str] = ..., EOF: _Optional[str] = ..., mode: _Optional[_Union[Mode, str]] = ..., offsetTime: _Optional[int] = ..., startTime: _Optional[int] = ..., endTime: _Optional[int] = ..., timeDeviation: _Optional[int] = ..., offsetWallClockVsSample: _Optional[int] = ..., noPlaybackToApplication: bool = ..., playbackToBus: bool = ...) -> None: ...

class PlaybackInfos(_message.Message):
    __slots__ = ("playbackInfo",)
    PLAYBACKINFO_FIELD_NUMBER: _ClassVar[int]
    playbackInfo: _containers.RepeatedCompositeFieldContainer[PlaybackInfo]
    def __init__(self, playbackInfo: _Optional[_Iterable[_Union[PlaybackInfo, _Mapping]]] = ...) -> None: ...

class PlaybackConfig(_message.Message):
    __slots__ = ("fileDescription", "namespace")
    FILEDESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    fileDescription: _system_api_pb2.FileDescription
    namespace: _common_pb2.NameSpace
    def __init__(self, fileDescription: _Optional[_Union[_system_api_pb2.FileDescription, _Mapping]] = ..., namespace: _Optional[_Union[_common_pb2.NameSpace, _Mapping]] = ...) -> None: ...

class PlaybackInfo(_message.Message):
    __slots__ = ("playbackConfig", "playbackMode")
    PLAYBACKCONFIG_FIELD_NUMBER: _ClassVar[int]
    PLAYBACKMODE_FIELD_NUMBER: _ClassVar[int]
    playbackConfig: PlaybackConfig
    playbackMode: PlaybackMode
    def __init__(self, playbackConfig: _Optional[_Union[PlaybackConfig, _Mapping]] = ..., playbackMode: _Optional[_Union[PlaybackMode, _Mapping]] = ...) -> None: ...
