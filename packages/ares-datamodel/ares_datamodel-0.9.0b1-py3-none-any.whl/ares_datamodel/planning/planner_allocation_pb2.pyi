from planning import planner_service_info_pb2 as _planner_service_info_pb2
from templates import parameter_metadata_pb2 as _parameter_metadata_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PlannerAllocation(_message.Message):
    __slots__ = ("unique_id", "planner", "parameter")
    UNIQUE_ID_FIELD_NUMBER: _ClassVar[int]
    PLANNER_FIELD_NUMBER: _ClassVar[int]
    PARAMETER_FIELD_NUMBER: _ClassVar[int]
    unique_id: str
    planner: _planner_service_info_pb2.PlannerServiceInfo
    parameter: _parameter_metadata_pb2.ParameterMetadata
    def __init__(self, unique_id: _Optional[str] = ..., planner: _Optional[_Union[_planner_service_info_pb2.PlannerServiceInfo, _Mapping]] = ..., parameter: _Optional[_Union[_parameter_metadata_pb2.ParameterMetadata, _Mapping]] = ...) -> None: ...
