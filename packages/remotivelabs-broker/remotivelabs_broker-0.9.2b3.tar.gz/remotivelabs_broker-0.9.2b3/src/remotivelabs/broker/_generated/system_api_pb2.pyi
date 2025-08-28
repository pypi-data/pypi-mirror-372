from remotivelabs.broker._generated import common_pb2 as _common_pb2
from remotivelabs.broker._generated.google.api import annotations_pb2 as _annotations_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LicenseStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNSET: _ClassVar[LicenseStatus]
    VALID: _ClassVar[LicenseStatus]
    EXPIRED: _ClassVar[LicenseStatus]
    BADDATE: _ClassVar[LicenseStatus]
    WRONGMACHINE: _ClassVar[LicenseStatus]
    INCOMPLETEJSON: _ClassVar[LicenseStatus]
    INVALIDJSON: _ClassVar[LicenseStatus]
    BADSIGNATURE: _ClassVar[LicenseStatus]
    MALFORMED: _ClassVar[LicenseStatus]
    SERVERERROR: _ClassVar[LicenseStatus]
    NOTERMSAGREEMENT: _ClassVar[LicenseStatus]
UNSET: LicenseStatus
VALID: LicenseStatus
EXPIRED: LicenseStatus
BADDATE: LicenseStatus
WRONGMACHINE: LicenseStatus
INCOMPLETEJSON: LicenseStatus
INVALIDJSON: LicenseStatus
BADSIGNATURE: LicenseStatus
MALFORMED: LicenseStatus
SERVERERROR: LicenseStatus
NOTERMSAGREEMENT: LicenseStatus

class Configuration(_message.Message):
    __slots__ = ("networkInfo", "interfacesJson", "publicAddress", "serverVersion", "interfacesInfo")
    NETWORKINFO_FIELD_NUMBER: _ClassVar[int]
    INTERFACESJSON_FIELD_NUMBER: _ClassVar[int]
    PUBLICADDRESS_FIELD_NUMBER: _ClassVar[int]
    SERVERVERSION_FIELD_NUMBER: _ClassVar[int]
    INTERFACESINFO_FIELD_NUMBER: _ClassVar[int]
    networkInfo: _containers.RepeatedCompositeFieldContainer[_common_pb2.NetworkInfo]
    interfacesJson: bytes
    publicAddress: str
    serverVersion: str
    interfacesInfo: str
    def __init__(self, networkInfo: _Optional[_Iterable[_Union[_common_pb2.NetworkInfo, _Mapping]]] = ..., interfacesJson: _Optional[bytes] = ..., publicAddress: _Optional[str] = ..., serverVersion: _Optional[str] = ..., interfacesInfo: _Optional[str] = ...) -> None: ...

class ReloadMessage(_message.Message):
    __slots__ = ("configuration", "errorMessage")
    CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    ERRORMESSAGE_FIELD_NUMBER: _ClassVar[int]
    configuration: Configuration
    errorMessage: str
    def __init__(self, configuration: _Optional[_Union[Configuration, _Mapping]] = ..., errorMessage: _Optional[str] = ...) -> None: ...

class FileDescription(_message.Message):
    __slots__ = ("sha256", "path")
    SHA256_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    sha256: str
    path: str
    def __init__(self, sha256: _Optional[str] = ..., path: _Optional[str] = ...) -> None: ...

class FileDescriptions(_message.Message):
    __slots__ = ("fileDescriptions",)
    FILEDESCRIPTIONS_FIELD_NUMBER: _ClassVar[int]
    fileDescriptions: _containers.RepeatedCompositeFieldContainer[FileDescription]
    def __init__(self, fileDescriptions: _Optional[_Iterable[_Union[FileDescription, _Mapping]]] = ...) -> None: ...

class FileUploadRequest(_message.Message):
    __slots__ = ("fileDescription", "chunk")
    FILEDESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CHUNK_FIELD_NUMBER: _ClassVar[int]
    fileDescription: FileDescription
    chunk: bytes
    def __init__(self, fileDescription: _Optional[_Union[FileDescription, _Mapping]] = ..., chunk: _Optional[bytes] = ...) -> None: ...

class FileUploadChunkRequest(_message.Message):
    __slots__ = ("fileDescription", "chunks", "chunkId", "chunk", "cancelUpload", "uploadTimeout")
    FILEDESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CHUNKS_FIELD_NUMBER: _ClassVar[int]
    CHUNKID_FIELD_NUMBER: _ClassVar[int]
    CHUNK_FIELD_NUMBER: _ClassVar[int]
    CANCELUPLOAD_FIELD_NUMBER: _ClassVar[int]
    UPLOADTIMEOUT_FIELD_NUMBER: _ClassVar[int]
    fileDescription: FileDescription
    chunks: int
    chunkId: int
    chunk: bytes
    cancelUpload: bool
    uploadTimeout: int
    def __init__(self, fileDescription: _Optional[_Union[FileDescription, _Mapping]] = ..., chunks: _Optional[int] = ..., chunkId: _Optional[int] = ..., chunk: _Optional[bytes] = ..., cancelUpload: bool = ..., uploadTimeout: _Optional[int] = ...) -> None: ...

class FileUploadResponse(_message.Message):
    __slots__ = ("finished", "cancelled", "errorMessage")
    FINISHED_FIELD_NUMBER: _ClassVar[int]
    CANCELLED_FIELD_NUMBER: _ClassVar[int]
    ERRORMESSAGE_FIELD_NUMBER: _ClassVar[int]
    finished: bool
    cancelled: bool
    errorMessage: str
    def __init__(self, finished: bool = ..., cancelled: bool = ..., errorMessage: _Optional[str] = ...) -> None: ...

class FileDownloadResponse(_message.Message):
    __slots__ = ("chunk", "errorMessage")
    CHUNK_FIELD_NUMBER: _ClassVar[int]
    ERRORMESSAGE_FIELD_NUMBER: _ClassVar[int]
    chunk: bytes
    errorMessage: str
    def __init__(self, chunk: _Optional[bytes] = ..., errorMessage: _Optional[str] = ...) -> None: ...

class BatchDownloadFileChunksRequest(_message.Message):
    __slots__ = ("fileDescriptions", "timeout")
    FILEDESCRIPTIONS_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    fileDescriptions: _containers.RepeatedCompositeFieldContainer[FileDescription]
    timeout: int
    def __init__(self, fileDescriptions: _Optional[_Iterable[_Union[FileDescription, _Mapping]]] = ..., timeout: _Optional[int] = ...) -> None: ...

class BatchDownloadFileChunksResponse(_message.Message):
    __slots__ = ("lastChunk", "chunkId", "chunk", "estimatedTotalSize")
    LASTCHUNK_FIELD_NUMBER: _ClassVar[int]
    CHUNKID_FIELD_NUMBER: _ClassVar[int]
    CHUNK_FIELD_NUMBER: _ClassVar[int]
    ESTIMATEDTOTALSIZE_FIELD_NUMBER: _ClassVar[int]
    lastChunk: bool
    chunkId: int
    chunk: bytes
    estimatedTotalSize: int
    def __init__(self, lastChunk: bool = ..., chunkId: _Optional[int] = ..., chunk: _Optional[bytes] = ..., estimatedTotalSize: _Optional[int] = ...) -> None: ...

class LicenseInfo(_message.Message):
    __slots__ = ("status", "json", "expires", "requestId", "requestMachineId")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    JSON_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_FIELD_NUMBER: _ClassVar[int]
    REQUESTID_FIELD_NUMBER: _ClassVar[int]
    REQUESTMACHINEID_FIELD_NUMBER: _ClassVar[int]
    status: LicenseStatus
    json: bytes
    expires: str
    requestId: str
    requestMachineId: bytes
    def __init__(self, status: _Optional[_Union[LicenseStatus, str]] = ..., json: _Optional[bytes] = ..., expires: _Optional[str] = ..., requestId: _Optional[str] = ..., requestMachineId: _Optional[bytes] = ...) -> None: ...

class License(_message.Message):
    __slots__ = ("data", "termsAgreement")
    DATA_FIELD_NUMBER: _ClassVar[int]
    TERMSAGREEMENT_FIELD_NUMBER: _ClassVar[int]
    data: bytes
    termsAgreement: bool
    def __init__(self, data: _Optional[bytes] = ..., termsAgreement: bool = ...) -> None: ...

class PropertyValue(_message.Message):
    __slots__ = ("name", "scope", "raw", "integer", "double")
    NAME_FIELD_NUMBER: _ClassVar[int]
    SCOPE_FIELD_NUMBER: _ClassVar[int]
    RAW_FIELD_NUMBER: _ClassVar[int]
    INTEGER_FIELD_NUMBER: _ClassVar[int]
    DOUBLE_FIELD_NUMBER: _ClassVar[int]
    name: str
    scope: _containers.RepeatedScalarFieldContainer[str]
    raw: bytes
    integer: int
    double: float
    def __init__(self, name: _Optional[str] = ..., scope: _Optional[_Iterable[str]] = ..., raw: _Optional[bytes] = ..., integer: _Optional[int] = ..., double: _Optional[float] = ...) -> None: ...
