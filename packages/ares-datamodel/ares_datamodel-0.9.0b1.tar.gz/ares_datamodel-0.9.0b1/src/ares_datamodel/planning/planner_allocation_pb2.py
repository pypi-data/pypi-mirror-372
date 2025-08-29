"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 1, '', 'planning/planner_allocation.proto')
_sym_db = _symbol_database.Default()
from ..planning import planner_service_info_pb2 as planning_dot_planner__service__info__pb2
from ..templates import parameter_metadata_pb2 as templates_dot_parameter__metadata__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n!planning/planner_allocation.proto\x12\x17ares.datamodel.planning\x1a#planning/planner_service_info.proto\x1a"templates/parameter_metadata.proto"\xb7\x01\n\x11PlannerAllocation\x12\x16\n\tunique_id\x18\x01 \x01(\tH\x00\x88\x01\x01\x12<\n\x07planner\x18\x02 \x01(\x0b2+.ares.datamodel.planning.PlannerServiceInfo\x12>\n\tparameter\x18\x03 \x01(\x0b2+.ares.datamodel.templates.ParameterMetadataB\x0c\n\n_unique_idb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'planning.planner_allocation_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_PLANNERALLOCATION']._serialized_start = 136
    _globals['_PLANNERALLOCATION']._serialized_end = 319