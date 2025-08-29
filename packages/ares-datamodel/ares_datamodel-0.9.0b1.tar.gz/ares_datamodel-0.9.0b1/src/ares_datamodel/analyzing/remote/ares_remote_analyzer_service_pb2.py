"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 1, '', 'analyzing/remote/ares_remote_analyzer_service.proto')
_sym_db = _symbol_database.Default()
from ...analyzing import analysis_pb2 as analyzing_dot_analysis__pb2
from ... import ares_struct_pb2 as ares__struct__pb2
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from ...analyzing import analyzer_capabilities_pb2 as analyzing_dot_analyzer__capabilities__pb2
from ... import ares_data_schema_pb2 as ares__data__schema__pb2
from ...connection import connection_status_pb2 as connection_dot_connection__status__pb2
from ...connection import connection_info_pb2 as connection_dot_connection__info__pb2
from ...connection import connection_state_pb2 as connection_dot_connection__state__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n3analyzing/remote/ares_remote_analyzer_service.proto\x12\x1fares.datamodel.analyzing.remote\x1a\x18analyzing/analysis.proto\x1a\x11ares_struct.proto\x1a\x1bgoogle/protobuf/empty.proto\x1a%analyzing/analyzer_capabilities.proto\x1a\x16ares_data_schema.proto\x1a"connection/connection_status.proto\x1a connection/connection_info.proto\x1a!connection/connection_state.proto"\\\n\x1aParameterValidationRequest\x12>\n\x0cinput_schema\x18\x01 \x01(\x0b2(.ares.datamodel.AresDataSchemaSimplified">\n\x19ParameterValidationResult\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x10\n\x08messages\x18\x02 \x03(\t"k\n\x0fAnalysisRequest\x12*\n\x06inputs\x18\x01 \x01(\x0b2\x1a.ares.datamodel.AresStruct\x12,\n\x08settings\x18\x02 \x01(\x0b2\x1a.ares.datamodel.AresStruct"V\n\x1aAnalysisParametersResponse\x128\n\x10parameter_schema\x18\x01 \x01(\x0b2\x1e.ares.datamodel.AresDataSchema2\xcf\x05\n\x19AresRemoteAnalyzerService\x12_\n\x07Analyze\x120.ares.datamodel.analyzing.remote.AnalysisRequest\x1a".ares.datamodel.analyzing.Analysis\x12a\n\x17GetAnalyzerCapabilities\x12\x16.google.protobuf.Empty\x1a..ares.datamodel.analyzing.AnalyzerCapabilities\x12\x89\x01\n\x0eValidateInputs\x12;.ares.datamodel.analyzing.remote.ParameterValidationRequest\x1a:.ares.datamodel.analyzing.remote.ParameterValidationResult\x12l\n\x15GetAnalysisParameters\x12\x16.google.protobuf.Empty\x1a;.ares.datamodel.analyzing.remote.AnalysisParametersResponse\x12Z\n\x13GetConnectionStatus\x12\x16.google.protobuf.Empty\x1a+.ares.datamodel.connection.ConnectionStatus\x12L\n\x08GetState\x12\x16.google.protobuf.Empty\x1a(.ares.datamodel.connection.StateResponse\x12J\n\x07GetInfo\x12\x16.google.protobuf.Empty\x1a\'.ares.datamodel.connection.InfoResponseb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'analyzing.remote.ares_remote_analyzer_service_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_PARAMETERVALIDATIONREQUEST']._serialized_start = 330
    _globals['_PARAMETERVALIDATIONREQUEST']._serialized_end = 422
    _globals['_PARAMETERVALIDATIONRESULT']._serialized_start = 424
    _globals['_PARAMETERVALIDATIONRESULT']._serialized_end = 486
    _globals['_ANALYSISREQUEST']._serialized_start = 488
    _globals['_ANALYSISREQUEST']._serialized_end = 595
    _globals['_ANALYSISPARAMETERSRESPONSE']._serialized_start = 597
    _globals['_ANALYSISPARAMETERSRESPONSE']._serialized_end = 683
    _globals['_ARESREMOTEANALYZERSERVICE']._serialized_start = 686
    _globals['_ARESREMOTEANALYZERSERVICE']._serialized_end = 1405