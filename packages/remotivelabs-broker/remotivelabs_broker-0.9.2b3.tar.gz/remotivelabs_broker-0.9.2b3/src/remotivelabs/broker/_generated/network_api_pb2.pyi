from remotivelabs.broker._generated import common_pb2 as _common_pb2
from remotivelabs.broker._generated.google.api import annotations_pb2 as _annotations_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SubscriberConfig(_message.Message):
    __slots__ = ("clientId", "signals", "onChange", "initialEmpty")
    CLIENTID_FIELD_NUMBER: _ClassVar[int]
    SIGNALS_FIELD_NUMBER: _ClassVar[int]
    ONCHANGE_FIELD_NUMBER: _ClassVar[int]
    INITIALEMPTY_FIELD_NUMBER: _ClassVar[int]
    clientId: _common_pb2.ClientId
    signals: SignalIds
    onChange: bool
    initialEmpty: bool
    def __init__(self, clientId: _Optional[_Union[_common_pb2.ClientId, _Mapping]] = ..., signals: _Optional[_Union[SignalIds, _Mapping]] = ..., onChange: bool = ..., initialEmpty: bool = ...) -> None: ...

class SubscriberWithScriptConfig(_message.Message):
    __slots__ = ("clientId", "script", "onChange")
    CLIENTID_FIELD_NUMBER: _ClassVar[int]
    SCRIPT_FIELD_NUMBER: _ClassVar[int]
    ONCHANGE_FIELD_NUMBER: _ClassVar[int]
    clientId: _common_pb2.ClientId
    script: bytes
    onChange: bool
    def __init__(self, clientId: _Optional[_Union[_common_pb2.ClientId, _Mapping]] = ..., script: _Optional[bytes] = ..., onChange: bool = ...) -> None: ...

class FramesDistributionConfig(_message.Message):
    __slots__ = ("namespace",)
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    namespace: _common_pb2.NameSpace
    def __init__(self, namespace: _Optional[_Union[_common_pb2.NameSpace, _Mapping]] = ...) -> None: ...

class CountByFrameId(_message.Message):
    __slots__ = ("frameId", "count")
    FRAMEID_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    frameId: int
    count: int
    def __init__(self, frameId: _Optional[int] = ..., count: _Optional[int] = ...) -> None: ...

class FramesDistribution(_message.Message):
    __slots__ = ("countsByFrameId",)
    COUNTSBYFRAMEID_FIELD_NUMBER: _ClassVar[int]
    countsByFrameId: _containers.RepeatedCompositeFieldContainer[CountByFrameId]
    def __init__(self, countsByFrameId: _Optional[_Iterable[_Union[CountByFrameId, _Mapping]]] = ...) -> None: ...

class SignalIds(_message.Message):
    __slots__ = ("signalId",)
    SIGNALID_FIELD_NUMBER: _ClassVar[int]
    signalId: _containers.RepeatedCompositeFieldContainer[_common_pb2.SignalId]
    def __init__(self, signalId: _Optional[_Iterable[_Union[_common_pb2.SignalId, _Mapping]]] = ...) -> None: ...

class Signals(_message.Message):
    __slots__ = ("signal",)
    SIGNAL_FIELD_NUMBER: _ClassVar[int]
    signal: _containers.RepeatedCompositeFieldContainer[Signal]
    def __init__(self, signal: _Optional[_Iterable[_Union[Signal, _Mapping]]] = ...) -> None: ...

class PublisherConfig(_message.Message):
    __slots__ = ("signals", "clientId", "frequency")
    SIGNALS_FIELD_NUMBER: _ClassVar[int]
    CLIENTID_FIELD_NUMBER: _ClassVar[int]
    FREQUENCY_FIELD_NUMBER: _ClassVar[int]
    signals: Signals
    clientId: _common_pb2.ClientId
    frequency: int
    def __init__(self, signals: _Optional[_Union[Signals, _Mapping]] = ..., clientId: _Optional[_Union[_common_pb2.ClientId, _Mapping]] = ..., frequency: _Optional[int] = ...) -> None: ...

class Signal(_message.Message):
    __slots__ = ("id", "integer", "double", "arbitration", "empty", "strValue", "raw", "timestamp")
    ID_FIELD_NUMBER: _ClassVar[int]
    INTEGER_FIELD_NUMBER: _ClassVar[int]
    DOUBLE_FIELD_NUMBER: _ClassVar[int]
    ARBITRATION_FIELD_NUMBER: _ClassVar[int]
    EMPTY_FIELD_NUMBER: _ClassVar[int]
    STRVALUE_FIELD_NUMBER: _ClassVar[int]
    RAW_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    id: _common_pb2.SignalId
    integer: int
    double: float
    arbitration: bool
    empty: bool
    strValue: str
    raw: bytes
    timestamp: int
    def __init__(self, id: _Optional[_Union[_common_pb2.SignalId, _Mapping]] = ..., integer: _Optional[int] = ..., double: _Optional[float] = ..., arbitration: bool = ..., empty: bool = ..., strValue: _Optional[str] = ..., raw: _Optional[bytes] = ..., timestamp: _Optional[int] = ...) -> None: ...

class Value(_message.Message):
    __slots__ = ("integer", "raw", "double", "strValue")
    INTEGER_FIELD_NUMBER: _ClassVar[int]
    RAW_FIELD_NUMBER: _ClassVar[int]
    DOUBLE_FIELD_NUMBER: _ClassVar[int]
    STRVALUE_FIELD_NUMBER: _ClassVar[int]
    integer: int
    raw: bytes
    double: float
    strValue: str
    def __init__(self, integer: _Optional[int] = ..., raw: _Optional[bytes] = ..., double: _Optional[float] = ..., strValue: _Optional[str] = ...) -> None: ...
