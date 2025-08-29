"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 1, '', 'templates/campaign_template.proto')
_sym_db = _symbol_database.Default()
from ..templates import experiment_template_pb2 as templates_dot_experiment__template__pb2
from ..templates import parameter_metadata_pb2 as templates_dot_parameter__metadata__pb2
from ..planning import planner_allocation_pb2 as planning_dot_planner__allocation__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n!templates/campaign_template.proto\x12\x18ares.datamodel.templates\x1a#templates/experiment_template.proto\x1a"templates/parameter_metadata.proto\x1a!planning/planner_allocation.proto"\xb6\x03\n\x10CampaignTemplate\x12\x16\n\tunique_id\x18\x01 \x01(\tH\x00\x88\x01\x01\x12F\n\x10startup_template\x18\x02 \x01(\x0b2,.ares.datamodel.templates.ExperimentTemplate\x12I\n\x13experiment_template\x18\x03 \x01(\x0b2,.ares.datamodel.templates.ExperimentTemplate\x12G\n\x11closeout_template\x18\x04 \x01(\x0b2,.ares.datamodel.templates.ExperimentTemplate\x12\x0c\n\x04name\x18\x05 \x01(\t\x12I\n\x14plannable_parameters\x18\x06 \x03(\x0b2+.ares.datamodel.templates.ParameterMetadata\x12G\n\x13planner_allocations\x18\x07 \x03(\x0b2*.ares.datamodel.planning.PlannerAllocationB\x0c\n\n_unique_idb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'templates.campaign_template_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_CAMPAIGNTEMPLATE']._serialized_start = 172
    _globals['_CAMPAIGNTEMPLATE']._serialized_end = 610