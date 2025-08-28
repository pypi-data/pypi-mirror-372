from remotivelabs.broker._generated import common_pb2 as _common_pb2
from remotivelabs.broker._generated.google.api import annotations_pb2 as _annotations_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LinkTimers(_message.Message):
    __slots__ = ("maxResponseTimeout", "delayResponse")
    MAXRESPONSETIMEOUT_FIELD_NUMBER: _ClassVar[int]
    DELAYRESPONSE_FIELD_NUMBER: _ClassVar[int]
    maxResponseTimeout: int
    delayResponse: int
    def __init__(self, maxResponseTimeout: _Optional[int] = ..., delayResponse: _Optional[int] = ...) -> None: ...

class PublisherConfig(_message.Message):
    __slots__ = ("link", "payload", "linkTimers", "noPadding")
    LINK_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    LINKTIMERS_FIELD_NUMBER: _ClassVar[int]
    NOPADDING_FIELD_NUMBER: _ClassVar[int]
    link: Link
    payload: Payload
    linkTimers: LinkTimers
    noPadding: bool
    def __init__(self, link: _Optional[_Union[Link, _Mapping]] = ..., payload: _Optional[_Union[Payload, _Mapping]] = ..., linkTimers: _Optional[_Union[LinkTimers, _Mapping]] = ..., noPadding: bool = ...) -> None: ...

class SubscriberConfig(_message.Message):
    __slots__ = ("link", "linkTimers", "rawPayload", "noPadding")
    LINK_FIELD_NUMBER: _ClassVar[int]
    LINKTIMERS_FIELD_NUMBER: _ClassVar[int]
    RAWPAYLOAD_FIELD_NUMBER: _ClassVar[int]
    NOPADDING_FIELD_NUMBER: _ClassVar[int]
    link: Link
    linkTimers: LinkTimers
    rawPayload: bool
    noPadding: bool
    def __init__(self, link: _Optional[_Union[Link, _Mapping]] = ..., linkTimers: _Optional[_Union[LinkTimers, _Mapping]] = ..., rawPayload: bool = ..., noPadding: bool = ...) -> None: ...

class Payload(_message.Message):
    __slots__ = ("bytes",)
    BYTES_FIELD_NUMBER: _ClassVar[int]
    bytes: bytes
    def __init__(self, bytes: _Optional[bytes] = ...) -> None: ...

class Link(_message.Message):
    __slots__ = ("clientId", "publishSignal", "subscribeSignal")
    CLIENTID_FIELD_NUMBER: _ClassVar[int]
    PUBLISHSIGNAL_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIBESIGNAL_FIELD_NUMBER: _ClassVar[int]
    clientId: _common_pb2.ClientId
    publishSignal: _common_pb2.SignalId
    subscribeSignal: _common_pb2.SignalId
    def __init__(self, clientId: _Optional[_Union[_common_pb2.ClientId, _Mapping]] = ..., publishSignal: _Optional[_Union[_common_pb2.SignalId, _Mapping]] = ..., subscribeSignal: _Optional[_Union[_common_pb2.SignalId, _Mapping]] = ...) -> None: ...
