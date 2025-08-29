"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 1, '', 'connection/connection_status.proto')
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n"connection/connection_status.proto\x12\x19ares.datamodel.connection"\'\n\x17ConnectionStatusRequest\x12\x0c\n\x04name\x18\x01 \x01(\t"W\n\x10ConnectionStatus\x125\n\x06status\x18\x01 \x01(\x0e2%.ares.datamodel.connection.AresStatus\x12\x0c\n\x04info\x18\x02 \x01(\t*L\n\nAresStatus\x12\x1d\n\x19UNKNOWN_CONNECTION_STATUS\x10\x00\x12\r\n\tCONNECTED\x10\x01\x12\x10\n\x0cDISCONNECTED\x10\x02b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'connection.connection_status_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_ARESSTATUS']._serialized_start = 195
    _globals['_ARESSTATUS']._serialized_end = 271
    _globals['_CONNECTIONSTATUSREQUEST']._serialized_start = 65
    _globals['_CONNECTIONSTATUSREQUEST']._serialized_end = 104
    _globals['_CONNECTIONSTATUS']._serialized_start = 106
    _globals['_CONNECTIONSTATUS']._serialized_end = 193