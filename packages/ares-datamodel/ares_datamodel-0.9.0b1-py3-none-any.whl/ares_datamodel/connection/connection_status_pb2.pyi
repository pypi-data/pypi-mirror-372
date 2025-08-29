from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AresStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_CONNECTION_STATUS: _ClassVar[AresStatus]
    CONNECTED: _ClassVar[AresStatus]
    DISCONNECTED: _ClassVar[AresStatus]
UNKNOWN_CONNECTION_STATUS: AresStatus
CONNECTED: AresStatus
DISCONNECTED: AresStatus

class ConnectionStatusRequest(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class ConnectionStatus(_message.Message):
    __slots__ = ("status", "info")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    INFO_FIELD_NUMBER: _ClassVar[int]
    status: AresStatus
    info: str
    def __init__(self, status: _Optional[_Union[AresStatus, str]] = ..., info: _Optional[str] = ...) -> None: ...
