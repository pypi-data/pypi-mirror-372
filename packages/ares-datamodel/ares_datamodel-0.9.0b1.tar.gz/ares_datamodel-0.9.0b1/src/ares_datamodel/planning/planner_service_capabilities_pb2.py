"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 1, '', 'planning/planner_service_capabilities.proto')
_sym_db = _symbol_database.Default()
from .. import ares_data_schema_pb2 as ares__data__schema__pb2
from ..planning import planner_pb2 as planning_dot_planner__pb2
from .. import ares_data_type_pb2 as ares__data__type__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n+planning/planner_service_capabilities.proto\x12\x17ares.datamodel.planning\x1a\x16ares_data_schema.proto\x1a\x16planning/planner.proto\x1a\x14ares_data_type.proto"\xf8\x01\n\x1aPlannerServiceCapabilities\x12\x14\n\x0cservice_name\x18\x01 \x01(\t\x12\x17\n\x0ftimeout_seconds\x18\x02 \x01(\x03\x12<\n\x12available_planners\x18\x03 \x03(\x0b2 .ares.datamodel.planning.Planner\x127\n\x0fsettings_schema\x18\x04 \x01(\x0b2\x1e.ares.datamodel.AresDataSchema\x124\n\x0eaccepted_types\x18\x05 \x03(\x0e2\x1c.ares.datamodel.AresDataTypeb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'planning.planner_service_capabilities_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_PLANNERSERVICECAPABILITIES']._serialized_start = 143
    _globals['_PLANNERSERVICECAPABILITIES']._serialized_end = 391