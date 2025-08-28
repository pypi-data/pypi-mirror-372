from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class E2eProfile(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PROFILE_AR_01A: _ClassVar[E2eProfile]
PROFILE_AR_01A: E2eProfile

class Empty(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ClientId(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class SignalId(_message.Message):
    __slots__ = ("name", "namespace")
    NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    name: str
    namespace: NameSpace
    def __init__(self, name: _Optional[str] = ..., namespace: _Optional[_Union[NameSpace, _Mapping]] = ...) -> None: ...

class SignalInfo(_message.Message):
    __slots__ = ("id", "metaData")
    ID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    id: SignalId
    metaData: MetaData
    def __init__(self, id: _Optional[_Union[SignalId, _Mapping]] = ..., metaData: _Optional[_Union[MetaData, _Mapping]] = ...) -> None: ...

class Multiplex(_message.Message):
    __slots__ = ("none", "select", "filter")
    NONE_FIELD_NUMBER: _ClassVar[int]
    SELECT_FIELD_NUMBER: _ClassVar[int]
    FILTER_FIELD_NUMBER: _ClassVar[int]
    none: Empty
    select: Empty
    filter: int
    def __init__(self, none: _Optional[_Union[Empty, _Mapping]] = ..., select: _Optional[_Union[Empty, _Mapping]] = ..., filter: _Optional[int] = ...) -> None: ...

class E2e(_message.Message):
    __slots__ = ("profile", "dataId", "signalCrc", "signalCounter")
    PROFILE_FIELD_NUMBER: _ClassVar[int]
    DATAID_FIELD_NUMBER: _ClassVar[int]
    SIGNALCRC_FIELD_NUMBER: _ClassVar[int]
    SIGNALCOUNTER_FIELD_NUMBER: _ClassVar[int]
    profile: E2eProfile
    dataId: int
    signalCrc: str
    signalCounter: str
    def __init__(self, profile: _Optional[_Union[E2eProfile, str]] = ..., dataId: _Optional[int] = ..., signalCrc: _Optional[str] = ..., signalCounter: _Optional[str] = ...) -> None: ...

class Group(_message.Message):
    __slots__ = ("start", "length", "e2e")
    START_FIELD_NUMBER: _ClassVar[int]
    LENGTH_FIELD_NUMBER: _ClassVar[int]
    E2E_FIELD_NUMBER: _ClassVar[int]
    start: int
    length: int
    e2e: E2e
    def __init__(self, start: _Optional[int] = ..., length: _Optional[int] = ..., e2e: _Optional[_Union[E2e, _Mapping]] = ...) -> None: ...

class MetaData(_message.Message):
    __slots__ = ("description", "max", "min", "unit", "size", "isRaw", "factor", "offset", "sender", "receiver", "cycleTime", "startValue", "multiplex", "e2e", "groups", "frameId", "namedValues")
    class NamedValuesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: str
        def __init__(self, key: _Optional[int] = ..., value: _Optional[str] = ...) -> None: ...
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    MAX_FIELD_NUMBER: _ClassVar[int]
    MIN_FIELD_NUMBER: _ClassVar[int]
    UNIT_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    ISRAW_FIELD_NUMBER: _ClassVar[int]
    FACTOR_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    SENDER_FIELD_NUMBER: _ClassVar[int]
    RECEIVER_FIELD_NUMBER: _ClassVar[int]
    CYCLETIME_FIELD_NUMBER: _ClassVar[int]
    STARTVALUE_FIELD_NUMBER: _ClassVar[int]
    MULTIPLEX_FIELD_NUMBER: _ClassVar[int]
    E2E_FIELD_NUMBER: _ClassVar[int]
    GROUPS_FIELD_NUMBER: _ClassVar[int]
    FRAMEID_FIELD_NUMBER: _ClassVar[int]
    NAMEDVALUES_FIELD_NUMBER: _ClassVar[int]
    description: str
    max: float
    min: float
    unit: str
    size: int
    isRaw: bool
    factor: float
    offset: float
    sender: _containers.RepeatedScalarFieldContainer[str]
    receiver: _containers.RepeatedScalarFieldContainer[str]
    cycleTime: float
    startValue: float
    multiplex: Multiplex
    e2e: E2e
    groups: _containers.RepeatedCompositeFieldContainer[Group]
    frameId: int
    namedValues: _containers.ScalarMap[int, str]
    def __init__(self, description: _Optional[str] = ..., max: _Optional[float] = ..., min: _Optional[float] = ..., unit: _Optional[str] = ..., size: _Optional[int] = ..., isRaw: bool = ..., factor: _Optional[float] = ..., offset: _Optional[float] = ..., sender: _Optional[_Iterable[str]] = ..., receiver: _Optional[_Iterable[str]] = ..., cycleTime: _Optional[float] = ..., startValue: _Optional[float] = ..., multiplex: _Optional[_Union[Multiplex, _Mapping]] = ..., e2e: _Optional[_Union[E2e, _Mapping]] = ..., groups: _Optional[_Iterable[_Union[Group, _Mapping]]] = ..., frameId: _Optional[int] = ..., namedValues: _Optional[_Mapping[int, str]] = ...) -> None: ...

class NameSpace(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class Namespaces(_message.Message):
    __slots__ = ("items",)
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[NameSpace]
    def __init__(self, items: _Optional[_Iterable[_Union[NameSpace, _Mapping]]] = ...) -> None: ...

class NetworkInfo(_message.Message):
    __slots__ = ("namespace", "type", "description")
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    namespace: NameSpace
    type: str
    description: str
    def __init__(self, namespace: _Optional[_Union[NameSpace, _Mapping]] = ..., type: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class FrameInfo(_message.Message):
    __slots__ = ("signalInfo", "childInfo")
    SIGNALINFO_FIELD_NUMBER: _ClassVar[int]
    CHILDINFO_FIELD_NUMBER: _ClassVar[int]
    signalInfo: SignalInfo
    childInfo: _containers.RepeatedCompositeFieldContainer[SignalInfo]
    def __init__(self, signalInfo: _Optional[_Union[SignalInfo, _Mapping]] = ..., childInfo: _Optional[_Iterable[_Union[SignalInfo, _Mapping]]] = ...) -> None: ...

class Frames(_message.Message):
    __slots__ = ("frame",)
    FRAME_FIELD_NUMBER: _ClassVar[int]
    frame: _containers.RepeatedCompositeFieldContainer[FrameInfo]
    def __init__(self, frame: _Optional[_Iterable[_Union[FrameInfo, _Mapping]]] = ...) -> None: ...
