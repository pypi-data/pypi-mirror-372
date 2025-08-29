"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x13configuration.proto\x12\x17com.fundamentum.edge.v1\x1a\x1bgoogle/protobuf/empty.proto"\x1d\n\nConfigData\x12\x0f\n\x07payload\x18\x01 \x01(\x0c"\x1d\n\nUpdateData\x12\x0f\n\x07payload\x18\x01 \x01(\x0c2\xa2\x01\n\rConfiguration\x12B\n\x03Get\x12\x16.google.protobuf.Empty\x1a#.com.fundamentum.edge.v1.ConfigData\x12M\n\x0cUpdateStream\x12\x16.google.protobuf.Empty\x1a#.com.fundamentum.edge.v1.UpdateData0\x01b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'configuration_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    _globals['_CONFIGDATA']._serialized_start = 77
    _globals['_CONFIGDATA']._serialized_end = 106
    _globals['_UPDATEDATA']._serialized_start = 108
    _globals['_UPDATEDATA']._serialized_end = 137
    _globals['_CONFIGURATION']._serialized_start = 140
    _globals['_CONFIGURATION']._serialized_end = 302