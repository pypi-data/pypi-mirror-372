"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 1, '', 'planning/planner_service_info.proto')
_sym_db = _symbol_database.Default()
from ..planning import planner_service_capabilities_pb2 as planning_dot_planner__service__capabilities__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n#planning/planner_service_info.proto\x12\x17ares.datamodel.planning\x1a+planning/planner_service_capabilities.proto"\xed\x01\n\x12PlannerServiceInfo\x12\x16\n\tunique_id\x18\x01 \x01(\tH\x00\x88\x01\x01\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x0c\n\x04type\x18\x03 \x01(\t\x12\x0f\n\x07version\x18\x04 \x01(\t\x12\x0f\n\x07address\x18\x05 \x01(\t\x12\x18\n\x0bdescription\x18\x06 \x01(\tH\x01\x88\x01\x01\x12I\n\x0ccapabilities\x18\x07 \x01(\x0b23.ares.datamodel.planning.PlannerServiceCapabilitiesB\x0c\n\n_unique_idB\x0e\n\x0c_descriptionb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'planning.planner_service_info_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_PLANNERSERVICEINFO']._serialized_start = 110
    _globals['_PLANNERSERVICEINFO']._serialized_end = 347