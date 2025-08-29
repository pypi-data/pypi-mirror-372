"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 1, '', 'planning/remote/ares_remote_planner_service.proto')
_sym_db = _symbol_database.Default()
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from ...planning import plan_pb2 as planning_dot_plan__pb2
from ...planning import planner_service_capabilities_pb2 as planning_dot_planner__service__capabilities__pb2
from ...connection import connection_state_pb2 as connection_dot_connection__state__pb2
from ...connection import connection_status_pb2 as connection_dot_connection__status__pb2
from ...connection import connection_info_pb2 as connection_dot_connection__info__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n1planning/remote/ares_remote_planner_service.proto\x12\x1eares.datamodel.planning.remote\x1a\x1bgoogle/protobuf/empty.proto\x1a\x13planning/plan.proto\x1a+planning/planner_service_capabilities.proto\x1a!connection/connection_state.proto\x1a"connection/connection_status.proto\x1a connection/connection_info.proto2\xdb\x03\n\x18AresRemotePlannerService\x12[\n\x04Plan\x12(.ares.datamodel.planning.PlanningRequest\x1a).ares.datamodel.planning.PlanningResponse\x12l\n\x1dGetPlannerServiceCapabilities\x12\x16.google.protobuf.Empty\x1a3.ares.datamodel.planning.PlannerServiceCapabilities\x12L\n\x08GetState\x12\x16.google.protobuf.Empty\x1a(.ares.datamodel.connection.StateResponse\x12Z\n\x13GetConnectionStatus\x12\x16.google.protobuf.Empty\x1a+.ares.datamodel.connection.ConnectionStatus\x12J\n\x07GetInfo\x12\x16.google.protobuf.Empty\x1a\'.ares.datamodel.connection.InfoResponseb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'planning.remote.ares_remote_planner_service_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_ARESREMOTEPLANNERSERVICE']._serialized_start = 286
    _globals['_ARESREMOTEPLANNERSERVICE']._serialized_end = 761