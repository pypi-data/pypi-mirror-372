from planning import planner_service_info_pb2 as _planner_service_info_pb2
from planning import planner_settings_pb2 as _planner_settings_pb2
from planning import manual_planner_pb2 as _manual_planner_pb2
from connection import connection_state_pb2 as _connection_state_pb2
import ares_struct_pb2 as _ares_struct_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PlannerInfoRequest(_message.Message):
    __slots__ = ("planner_id",)
    PLANNER_ID_FIELD_NUMBER: _ClassVar[int]
    planner_id: str
    def __init__(self, planner_id: _Optional[str] = ...) -> None: ...

class PlannerInfoResponse(_message.Message):
    __slots__ = ("info",)
    INFO_FIELD_NUMBER: _ClassVar[int]
    info: _planner_service_info_pb2.PlannerServiceInfo
    def __init__(self, info: _Optional[_Union[_planner_service_info_pb2.PlannerServiceInfo, _Mapping]] = ...) -> None: ...

class PlannerSettingsRequest(_message.Message):
    __slots__ = ("planner_id",)
    PLANNER_ID_FIELD_NUMBER: _ClassVar[int]
    planner_id: str
    def __init__(self, planner_id: _Optional[str] = ...) -> None: ...

class GetAllPlannersResponse(_message.Message):
    __slots__ = ("planners",)
    PLANNERS_FIELD_NUMBER: _ClassVar[int]
    planners: _containers.RepeatedCompositeFieldContainer[_planner_service_info_pb2.PlannerServiceInfo]
    def __init__(self, planners: _Optional[_Iterable[_Union[_planner_service_info_pb2.PlannerServiceInfo, _Mapping]]] = ...) -> None: ...

class AddPlannerRequest(_message.Message):
    __slots__ = ("name", "address")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    name: str
    address: str
    def __init__(self, name: _Optional[str] = ..., address: _Optional[str] = ...) -> None: ...

class AddPlannerResponse(_message.Message):
    __slots__ = ("success", "error_message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error_message: str
    def __init__(self, success: bool = ..., error_message: _Optional[str] = ...) -> None: ...

class UpdatePlannerRequest(_message.Message):
    __slots__ = ("planner_id", "name", "url")
    PLANNER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    planner_id: str
    name: str
    url: str
    def __init__(self, planner_id: _Optional[str] = ..., name: _Optional[str] = ..., url: _Optional[str] = ...) -> None: ...

class UpdatePlannerResponse(_message.Message):
    __slots__ = ("success", "error_message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error_message: str
    def __init__(self, success: bool = ..., error_message: _Optional[str] = ...) -> None: ...

class RemovePlannerRequest(_message.Message):
    __slots__ = ("planner_id",)
    PLANNER_ID_FIELD_NUMBER: _ClassVar[int]
    planner_id: str
    def __init__(self, planner_id: _Optional[str] = ...) -> None: ...
