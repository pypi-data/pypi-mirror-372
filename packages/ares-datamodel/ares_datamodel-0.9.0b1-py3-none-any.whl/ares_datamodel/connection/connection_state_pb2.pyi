from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class State(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNSPECIFIED_STATE: _ClassVar[State]
    ACTIVE: _ClassVar[State]
    INACTIVE: _ClassVar[State]
    ERROR: _ClassVar[State]
UNSPECIFIED_STATE: State
ACTIVE: State
INACTIVE: State
ERROR: State

class StateRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class StateResponse(_message.Message):
    __slots__ = ("state", "state_message")
    STATE_FIELD_NUMBER: _ClassVar[int]
    STATE_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    state: State
    state_message: str
    def __init__(self, state: _Optional[_Union[State, str]] = ..., state_message: _Optional[str] = ...) -> None: ...
