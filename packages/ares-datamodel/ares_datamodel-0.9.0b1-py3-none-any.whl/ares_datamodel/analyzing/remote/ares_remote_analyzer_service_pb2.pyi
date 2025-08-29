from analyzing import analysis_pb2 as _analysis_pb2
import ares_struct_pb2 as _ares_struct_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from analyzing import analyzer_capabilities_pb2 as _analyzer_capabilities_pb2
import ares_data_schema_pb2 as _ares_data_schema_pb2
from connection import connection_status_pb2 as _connection_status_pb2
from connection import connection_info_pb2 as _connection_info_pb2
from connection import connection_state_pb2 as _connection_state_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ParameterValidationRequest(_message.Message):
    __slots__ = ("input_schema",)
    INPUT_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    input_schema: _ares_data_schema_pb2.AresDataSchemaSimplified
    def __init__(self, input_schema: _Optional[_Union[_ares_data_schema_pb2.AresDataSchemaSimplified, _Mapping]] = ...) -> None: ...

class ParameterValidationResult(_message.Message):
    __slots__ = ("success", "messages")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGES_FIELD_NUMBER: _ClassVar[int]
    success: bool
    messages: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, success: bool = ..., messages: _Optional[_Iterable[str]] = ...) -> None: ...

class AnalysisRequest(_message.Message):
    __slots__ = ("inputs", "settings")
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    SETTINGS_FIELD_NUMBER: _ClassVar[int]
    inputs: _ares_struct_pb2.AresStruct
    settings: _ares_struct_pb2.AresStruct
    def __init__(self, inputs: _Optional[_Union[_ares_struct_pb2.AresStruct, _Mapping]] = ..., settings: _Optional[_Union[_ares_struct_pb2.AresStruct, _Mapping]] = ...) -> None: ...

class AnalysisParametersResponse(_message.Message):
    __slots__ = ("parameter_schema",)
    PARAMETER_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    parameter_schema: _ares_data_schema_pb2.AresDataSchema
    def __init__(self, parameter_schema: _Optional[_Union[_ares_data_schema_pb2.AresDataSchema, _Mapping]] = ...) -> None: ...
