import ares_data_schema_pb2 as _ares_data_schema_pb2
from planning import planner_pb2 as _planner_pb2
import ares_data_type_pb2 as _ares_data_type_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PlannerServiceCapabilities(_message.Message):
    __slots__ = ("service_name", "timeout_seconds", "available_planners", "settings_schema", "accepted_types")
    SERVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_SECONDS_FIELD_NUMBER: _ClassVar[int]
    AVAILABLE_PLANNERS_FIELD_NUMBER: _ClassVar[int]
    SETTINGS_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    ACCEPTED_TYPES_FIELD_NUMBER: _ClassVar[int]
    service_name: str
    timeout_seconds: int
    available_planners: _containers.RepeatedCompositeFieldContainer[_planner_pb2.Planner]
    settings_schema: _ares_data_schema_pb2.AresDataSchema
    accepted_types: _containers.RepeatedScalarFieldContainer[_ares_data_type_pb2.AresDataType]
    def __init__(self, service_name: _Optional[str] = ..., timeout_seconds: _Optional[int] = ..., available_planners: _Optional[_Iterable[_Union[_planner_pb2.Planner, _Mapping]]] = ..., settings_schema: _Optional[_Union[_ares_data_schema_pb2.AresDataSchema, _Mapping]] = ..., accepted_types: _Optional[_Iterable[_Union[_ares_data_type_pb2.AresDataType, str]]] = ...) -> None: ...
