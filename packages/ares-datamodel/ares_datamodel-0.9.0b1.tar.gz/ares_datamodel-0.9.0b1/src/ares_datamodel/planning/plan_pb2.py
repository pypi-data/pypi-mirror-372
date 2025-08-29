"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 1, '', 'planning/plan.proto')
_sym_db = _symbol_database.Default()
from .. import ares_struct_pb2 as ares__struct__pb2
from .. import ares_data_type_pb2 as ares__data__type__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x13planning/plan.proto\x12\x17ares.datamodel.planning\x1a\x11ares_struct.proto\x1a\x14ares_data_type.proto"\x90\x01\n\x0fPlanningRequest\x12G\n\x13planning_parameters\x18\x01 \x03(\x0b2*.ares.datamodel.planning.PlanningParameter\x124\n\x10adapter_settings\x18\x02 \x01(\x0b2\x1a.ares.datamodel.AresStruct"Y\n\x10PlanningResponse\x12E\n\x12planned_parameters\x18\x01 \x03(\x0b2).ares.datamodel.planning.PlannedParameter"\x9d\x03\n\x11PlanningParameter\x12\x16\n\x0eparameter_name\x18\x01 \x01(\t\x12\x1a\n\rminimum_value\x18\x02 \x01(\x01H\x00\x88\x01\x01\x12\x1a\n\rmaximum_value\x18\x03 \x01(\x01H\x01\x88\x01\x01\x12\x1e\n\x11minimum_precision\x18\x04 \x01(\x01H\x02\x88\x01\x01\x124\n\x11parameter_history\x18\x05 \x03(\x0b2\x19.ares.datamodel.AresValue\x12/\n\tdata_type\x18\x06 \x01(\x0e2\x1c.ares.datamodel.AresDataType\x12:\n\x08metadata\x18\x07 \x01(\x0b2(.ares.datamodel.planning.PlannerMetadata\x12\x12\n\nis_planned\x18\x08 \x01(\x08\x12\x11\n\tis_result\x18\t \x01(\x08\x12\x14\n\x0cplanner_name\x18\n \x01(\tB\x10\n\x0e_minimum_valueB\x10\n\x0e_maximum_valueB\x14\n\x12_minimum_precision"\x9a\x01\n\x10PlannedParameter\x12\x16\n\x0eparameter_name\x18\x01 \x01(\t\x122\n\x0fparameter_value\x18\x02 \x01(\x0b2\x19.ares.datamodel.AresValue\x12:\n\x08metadata\x18\x03 \x01(\x0b2(.ares.datamodel.planning.PlannerMetadata"(\n\x0fPlannerMetadata\x12\x15\n\rmetadata_name\x18\x01 \x01(\tb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'planning.plan_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_PLANNINGREQUEST']._serialized_start = 90
    _globals['_PLANNINGREQUEST']._serialized_end = 234
    _globals['_PLANNINGRESPONSE']._serialized_start = 236
    _globals['_PLANNINGRESPONSE']._serialized_end = 325
    _globals['_PLANNINGPARAMETER']._serialized_start = 328
    _globals['_PLANNINGPARAMETER']._serialized_end = 741
    _globals['_PLANNEDPARAMETER']._serialized_start = 744
    _globals['_PLANNEDPARAMETER']._serialized_end = 898
    _globals['_PLANNERMETADATA']._serialized_start = 900
    _globals['_PLANNERMETADATA']._serialized_end = 940