"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 1, '', 'ares_analyzer_management_service.proto')
_sym_db = _symbol_database.Default()
from .analyzing import analyzer_info_pb2 as analyzing_dot_analyzer__info__pb2
from .connection import connection_state_pb2 as connection_dot_connection__state__pb2
from .analyzing import analyzer_settings_pb2 as analyzing_dot_analyzer__settings__pb2
from . import ares_struct_pb2 as ares__struct__pb2
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n&ares_analyzer_management_service.proto\x12\rares.services\x1a\x1danalyzing/analyzer_info.proto\x1a!connection/connection_state.proto\x1a!analyzing/analyzer_settings.proto\x1a\x11ares_struct.proto\x1a\x1bgoogle/protobuf/empty.proto"T\n\x17GetAllAnalyzersResponse\x129\n\tanalyzers\x18\x01 \x03(\x0b2&.ares.datamodel.analyzing.AnalyzerInfo"5\n\x18AddRemoteAnalyzerRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0b\n\x03url\x18\x02 \x01(\t"o\n\x19AddRemoteAnalyzerResponse\x12\x13\n\x0banalyzer_id\x18\x01 \x01(\t\x12\x0f\n\x07success\x18\x02 \x01(\x08\x12\x1a\n\rerror_message\x18\x03 \x01(\tH\x00\x88\x01\x01B\x10\n\x0e_error_message"h\n\x1bUpdateRemoteAnalyzerRequest\x12\x13\n\x0banalyzer_id\x18\x01 \x01(\t\x12\x11\n\x04name\x18\x02 \x01(\tH\x00\x88\x01\x01\x12\x10\n\x03url\x18\x03 \x01(\tH\x01\x88\x01\x01B\x07\n\x05_nameB\x06\n\x04_url"]\n\x1cUpdateRemoteAnalyzerResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x1a\n\rerror_message\x18\x02 \x01(\tH\x00\x88\x01\x01B\x10\n\x0e_error_message"q\n\x1bRemoveRemoteAnalyzerRequest\x12\x13\n\x0banalyzer_id\x18\x01 \x01(\t\x12\x0f\n\x07success\x18\x02 \x01(\x08\x12\x1a\n\rerror_message\x18\x03 \x01(\tH\x00\x88\x01\x01B\x10\n\x0e_error_message"*\n\x13AnalyzerInfoRequest\x12\x13\n\x0banalyzer_id\x18\x01 \x01(\t"L\n\x14AnalyzerInfoResponse\x124\n\x04info\x18\x01 \x01(\x0b2&.ares.datamodel.analyzing.AnalyzerInfo".\n\x17AnalyzerSettingsRequest\x12\x13\n\x0banalyzer_id\x18\x01 \x01(\t2\x90\x06\n\x1dAresAnalyzerManagementService\x12]\n\x08GetState\x12\'.ares.datamodel.connection.StateRequest\x1a(.ares.datamodel.connection.StateResponse\x12R\n\x07GetInfo\x12".ares.services.AnalyzerInfoRequest\x1a#.ares.services.AnalyzerInfoResponse\x12Y\n\x13SetAnalyzerSettings\x12*.ares.datamodel.analyzing.AnalyzerSettings\x1a\x16.google.protobuf.Empty\x12Y\n\x13GetAnalyzerSettings\x12&.ares.services.AnalyzerSettingsRequest\x1a\x1a.ares.datamodel.AresStruct\x12Q\n\x0fGetAllAnalyzers\x12\x16.google.protobuf.Empty\x1a&.ares.services.GetAllAnalyzersResponse\x12f\n\x11AddRemoteAnalyzer\x12\'.ares.services.AddRemoteAnalyzerRequest\x1a(.ares.services.AddRemoteAnalyzerResponse\x12o\n\x14UpdateRemoteAnalyzer\x12*.ares.services.UpdateRemoteAnalyzerRequest\x1a+.ares.services.UpdateRemoteAnalyzerResponse\x12Z\n\x14RemoveRemoteAnalyzer\x12*.ares.services.RemoveRemoteAnalyzerRequest\x1a\x16.google.protobuf.Emptyb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'ares_analyzer_management_service_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_GETALLANALYZERSRESPONSE']._serialized_start = 206
    _globals['_GETALLANALYZERSRESPONSE']._serialized_end = 290
    _globals['_ADDREMOTEANALYZERREQUEST']._serialized_start = 292
    _globals['_ADDREMOTEANALYZERREQUEST']._serialized_end = 345
    _globals['_ADDREMOTEANALYZERRESPONSE']._serialized_start = 347
    _globals['_ADDREMOTEANALYZERRESPONSE']._serialized_end = 458
    _globals['_UPDATEREMOTEANALYZERREQUEST']._serialized_start = 460
    _globals['_UPDATEREMOTEANALYZERREQUEST']._serialized_end = 564
    _globals['_UPDATEREMOTEANALYZERRESPONSE']._serialized_start = 566
    _globals['_UPDATEREMOTEANALYZERRESPONSE']._serialized_end = 659
    _globals['_REMOVEREMOTEANALYZERREQUEST']._serialized_start = 661
    _globals['_REMOVEREMOTEANALYZERREQUEST']._serialized_end = 774
    _globals['_ANALYZERINFOREQUEST']._serialized_start = 776
    _globals['_ANALYZERINFOREQUEST']._serialized_end = 818
    _globals['_ANALYZERINFORESPONSE']._serialized_start = 820
    _globals['_ANALYZERINFORESPONSE']._serialized_end = 896
    _globals['_ANALYZERSETTINGSREQUEST']._serialized_start = 898
    _globals['_ANALYZERSETTINGSREQUEST']._serialized_end = 944
    _globals['_ARESANALYZERMANAGEMENTSERVICE']._serialized_start = 947
    _globals['_ARESANALYZERMANAGEMENTSERVICE']._serialized_end = 1731