"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 1, '', 'limits.proto')
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0climits.proto\x12\x0eares.datamodel"_\n\x06Limits\x12\x16\n\tunique_id\x18\x01 \x01(\tH\x00\x88\x01\x01\x12\x0f\n\x07minimum\x18\x02 \x01(\x02\x12\x0f\n\x07maximum\x18\x03 \x01(\x02\x12\r\n\x05index\x18\x04 \x01(\x03B\x0c\n\n_unique_idb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'limits_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_LIMITS']._serialized_start = 32
    _globals['_LIMITS']._serialized_end = 127