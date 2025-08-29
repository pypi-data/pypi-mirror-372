import ares_struct_pb2 as _ares_struct_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PlannerSettings(_message.Message):
    __slots__ = ("planner_id", "settings")
    PLANNER_ID_FIELD_NUMBER: _ClassVar[int]
    SETTINGS_FIELD_NUMBER: _ClassVar[int]
    planner_id: str
    settings: _ares_struct_pb2.AresStruct
    def __init__(self, planner_id: _Optional[str] = ..., settings: _Optional[_Union[_ares_struct_pb2.AresStruct, _Mapping]] = ...) -> None: ...
