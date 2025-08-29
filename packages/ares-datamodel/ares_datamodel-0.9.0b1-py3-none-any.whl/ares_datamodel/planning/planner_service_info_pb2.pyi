from planning import planner_service_capabilities_pb2 as _planner_service_capabilities_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PlannerServiceInfo(_message.Message):
    __slots__ = ("unique_id", "name", "type", "version", "address", "description", "capabilities")
    UNIQUE_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CAPABILITIES_FIELD_NUMBER: _ClassVar[int]
    unique_id: str
    name: str
    type: str
    version: str
    address: str
    description: str
    capabilities: _planner_service_capabilities_pb2.PlannerServiceCapabilities
    def __init__(self, unique_id: _Optional[str] = ..., name: _Optional[str] = ..., type: _Optional[str] = ..., version: _Optional[str] = ..., address: _Optional[str] = ..., description: _Optional[str] = ..., capabilities: _Optional[_Union[_planner_service_capabilities_pb2.PlannerServiceCapabilities, _Mapping]] = ...) -> None: ...
