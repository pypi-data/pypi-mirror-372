from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Planner(_message.Message):
    __slots__ = ("unique_id", "planner_name", "description", "version")
    UNIQUE_ID_FIELD_NUMBER: _ClassVar[int]
    PLANNER_NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    unique_id: str
    planner_name: str
    description: str
    version: str
    def __init__(self, unique_id: _Optional[str] = ..., planner_name: _Optional[str] = ..., description: _Optional[str] = ..., version: _Optional[str] = ...) -> None: ...
