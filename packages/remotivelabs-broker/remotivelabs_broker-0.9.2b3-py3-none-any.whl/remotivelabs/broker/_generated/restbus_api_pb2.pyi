from remotivelabs.broker._generated import common_pb2 as _common_pb2
from remotivelabs.broker._generated import network_api_pb2 as _network_api_pb2
from remotivelabs.broker._generated.google.api import annotations_pb2 as _annotations_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StartOption(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    START_AFTER_ADD: _ClassVar[StartOption]
    NOP: _ClassVar[StartOption]
START_AFTER_ADD: StartOption
NOP: StartOption

class RestbusRequest(_message.Message):
    __slots__ = ("namespaces",)
    NAMESPACES_FIELD_NUMBER: _ClassVar[int]
    namespaces: _common_pb2.Namespaces
    def __init__(self, namespaces: _Optional[_Union[_common_pb2.Namespaces, _Mapping]] = ...) -> None: ...

class AddRequest(_message.Message):
    __slots__ = ("clientId", "startOption", "frames", "defaultSignals")
    CLIENTID_FIELD_NUMBER: _ClassVar[int]
    STARTOPTION_FIELD_NUMBER: _ClassVar[int]
    FRAMES_FIELD_NUMBER: _ClassVar[int]
    DEFAULTSIGNALS_FIELD_NUMBER: _ClassVar[int]
    clientId: _common_pb2.ClientId
    startOption: StartOption
    frames: FrameConfigs
    defaultSignals: _containers.RepeatedCompositeFieldContainer[SignalSequence]
    def __init__(self, clientId: _Optional[_Union[_common_pb2.ClientId, _Mapping]] = ..., startOption: _Optional[_Union[StartOption, str]] = ..., frames: _Optional[_Union[FrameConfigs, _Mapping]] = ..., defaultSignals: _Optional[_Iterable[_Union[SignalSequence, _Mapping]]] = ...) -> None: ...

class RemoveRequest(_message.Message):
    __slots__ = ("namespaces", "frameIds")
    NAMESPACES_FIELD_NUMBER: _ClassVar[int]
    FRAMEIDS_FIELD_NUMBER: _ClassVar[int]
    namespaces: _common_pb2.Namespaces
    frameIds: _network_api_pb2.SignalIds
    def __init__(self, namespaces: _Optional[_Union[_common_pb2.Namespaces, _Mapping]] = ..., frameIds: _Optional[_Union[_network_api_pb2.SignalIds, _Mapping]] = ...) -> None: ...

class ResetRequest(_message.Message):
    __slots__ = ("namespaces", "frameIds", "signalIds")
    NAMESPACES_FIELD_NUMBER: _ClassVar[int]
    FRAMEIDS_FIELD_NUMBER: _ClassVar[int]
    SIGNALIDS_FIELD_NUMBER: _ClassVar[int]
    namespaces: _common_pb2.Namespaces
    frameIds: _network_api_pb2.SignalIds
    signalIds: _network_api_pb2.SignalIds
    def __init__(self, namespaces: _Optional[_Union[_common_pb2.Namespaces, _Mapping]] = ..., frameIds: _Optional[_Union[_network_api_pb2.SignalIds, _Mapping]] = ..., signalIds: _Optional[_Union[_network_api_pb2.SignalIds, _Mapping]] = ...) -> None: ...

class UpdateRequest(_message.Message):
    __slots__ = ("signals",)
    SIGNALS_FIELD_NUMBER: _ClassVar[int]
    signals: _containers.RepeatedCompositeFieldContainer[SignalSequence]
    def __init__(self, signals: _Optional[_Iterable[_Union[SignalSequence, _Mapping]]] = ...) -> None: ...

class FrameConfigs(_message.Message):
    __slots__ = ("items",)
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[FrameConfig]
    def __init__(self, items: _Optional[_Iterable[_Union[FrameConfig, _Mapping]]] = ...) -> None: ...

class FrameConfig(_message.Message):
    __slots__ = ("frameId", "cycleTime")
    FRAMEID_FIELD_NUMBER: _ClassVar[int]
    CYCLETIME_FIELD_NUMBER: _ClassVar[int]
    frameId: _common_pb2.SignalId
    cycleTime: float
    def __init__(self, frameId: _Optional[_Union[_common_pb2.SignalId, _Mapping]] = ..., cycleTime: _Optional[float] = ...) -> None: ...

class SignalSequence(_message.Message):
    __slots__ = ("id", "loop", "initial")
    ID_FIELD_NUMBER: _ClassVar[int]
    LOOP_FIELD_NUMBER: _ClassVar[int]
    INITIAL_FIELD_NUMBER: _ClassVar[int]
    id: _common_pb2.SignalId
    loop: _containers.RepeatedCompositeFieldContainer[_network_api_pb2.Value]
    initial: _containers.RepeatedCompositeFieldContainer[_network_api_pb2.Value]
    def __init__(self, id: _Optional[_Union[_common_pb2.SignalId, _Mapping]] = ..., loop: _Optional[_Iterable[_Union[_network_api_pb2.Value, _Mapping]]] = ..., initial: _Optional[_Iterable[_Union[_network_api_pb2.Value, _Mapping]]] = ...) -> None: ...
