"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 1, '', 'ares_planner_management_service.proto')
_sym_db = _symbol_database.Default()
from .planning import planner_service_info_pb2 as planning_dot_planner__service__info__pb2
from .planning import planner_settings_pb2 as planning_dot_planner__settings__pb2
from .planning import manual_planner_pb2 as planning_dot_manual__planner__pb2
from .connection import connection_state_pb2 as connection_dot_connection__state__pb2
from . import ares_struct_pb2 as ares__struct__pb2
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n%ares_planner_management_service.proto\x12\rares.services\x1a#planning/planner_service_info.proto\x1a\x1fplanning/planner_settings.proto\x1a\x1dplanning/manual_planner.proto\x1a!connection/connection_state.proto\x1a\x11ares_struct.proto\x1a\x1bgoogle/protobuf/empty.proto"(\n\x12PlannerInfoRequest\x12\x12\n\nplanner_id\x18\x01 \x01(\t"P\n\x13PlannerInfoResponse\x129\n\x04info\x18\x01 \x01(\x0b2+.ares.datamodel.planning.PlannerServiceInfo",\n\x16PlannerSettingsRequest\x12\x12\n\nplanner_id\x18\x01 \x01(\t"W\n\x16GetAllPlannersResponse\x12=\n\x08planners\x18\x01 \x03(\x0b2+.ares.datamodel.planning.PlannerServiceInfo"C\n\x11AddPlannerRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x14\n\x07address\x18\x02 \x01(\tH\x00\x88\x01\x01B\n\n\x08_address"S\n\x12AddPlannerResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x1a\n\rerror_message\x18\x02 \x01(\tH\x00\x88\x01\x01B\x10\n\x0e_error_message"`\n\x14UpdatePlannerRequest\x12\x12\n\nplanner_id\x18\x01 \x01(\t\x12\x11\n\x04name\x18\x02 \x01(\tH\x00\x88\x01\x01\x12\x10\n\x03url\x18\x03 \x01(\tH\x01\x88\x01\x01B\x07\n\x05_nameB\x06\n\x04_url"V\n\x15UpdatePlannerResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x1a\n\rerror_message\x18\x02 \x01(\tH\x00\x88\x01\x01B\x10\n\x0e_error_message"*\n\x14RemovePlannerRequest\x12\x12\n\nplanner_id\x18\x01 \x01(\t2\xd2\x07\n\x1cAresPlannerManagementService\x12]\n\x08GetState\x12\'.ares.datamodel.connection.StateRequest\x1a(.ares.datamodel.connection.StateResponse\x12P\n\x07GetInfo\x12!.ares.services.PlannerInfoRequest\x1a".ares.services.PlannerInfoResponse\x12V\n\x12SetPlannerSettings\x12(.ares.datamodel.planning.PlannerSettings\x1a\x16.google.protobuf.Empty\x12W\n\x12GetPlannerSettings\x12%.ares.services.PlannerSettingsRequest\x1a\x1a.ares.datamodel.AresStruct\x12W\n\x11SeedManualPlanner\x12*.ares.datamodel.planning.ManualPlannerSeed\x1a\x16.google.protobuf.Empty\x12c\n\x14GetManualPlannerSeed\x12\x16.google.protobuf.Empty\x1a3.ares.datamodel.planning.ManualPlannerSetCollection\x12D\n\x12ResetManualPlanner\x12\x16.google.protobuf.Empty\x1a\x16.google.protobuf.Empty\x12O\n\x0eGetAllPlanners\x12\x16.google.protobuf.Empty\x1a%.ares.services.GetAllPlannersResponse\x12Q\n\nAddPlanner\x12 .ares.services.AddPlannerRequest\x1a!.ares.services.AddPlannerResponse\x12Z\n\rUpdatePlanner\x12#.ares.services.UpdatePlannerRequest\x1a$.ares.services.UpdatePlannerResponse\x12L\n\rRemovePlanner\x12#.ares.services.RemovePlannerRequest\x1a\x16.google.protobuf.Emptyb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'ares_planner_management_service_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_PLANNERINFOREQUEST']._serialized_start = 240
    _globals['_PLANNERINFOREQUEST']._serialized_end = 280
    _globals['_PLANNERINFORESPONSE']._serialized_start = 282
    _globals['_PLANNERINFORESPONSE']._serialized_end = 362
    _globals['_PLANNERSETTINGSREQUEST']._serialized_start = 364
    _globals['_PLANNERSETTINGSREQUEST']._serialized_end = 408
    _globals['_GETALLPLANNERSRESPONSE']._serialized_start = 410
    _globals['_GETALLPLANNERSRESPONSE']._serialized_end = 497
    _globals['_ADDPLANNERREQUEST']._serialized_start = 499
    _globals['_ADDPLANNERREQUEST']._serialized_end = 566
    _globals['_ADDPLANNERRESPONSE']._serialized_start = 568
    _globals['_ADDPLANNERRESPONSE']._serialized_end = 651
    _globals['_UPDATEPLANNERREQUEST']._serialized_start = 653
    _globals['_UPDATEPLANNERREQUEST']._serialized_end = 749
    _globals['_UPDATEPLANNERRESPONSE']._serialized_start = 751
    _globals['_UPDATEPLANNERRESPONSE']._serialized_end = 837
    _globals['_REMOVEPLANNERREQUEST']._serialized_start = 839
    _globals['_REMOVEPLANNERREQUEST']._serialized_end = 881
    _globals['_ARESPLANNERMANAGEMENTSERVICE']._serialized_start = 884
    _globals['_ARESPLANNERMANAGEMENTSERVICE']._serialized_end = 1862