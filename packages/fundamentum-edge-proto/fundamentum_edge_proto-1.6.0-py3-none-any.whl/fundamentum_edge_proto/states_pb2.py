"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from google.protobuf import struct_pb2 as google_dot_protobuf_dot_struct__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
from . import qos_pb2 as qos__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0cstates.proto\x12\x17com.fundamentum.edge.v1\x1a\x1bgoogle/protobuf/empty.proto\x1a\x1cgoogle/protobuf/struct.proto\x1a\x1fgoogle/protobuf/timestamp.proto\x1a\tqos.proto"\xb3\x02\n\rStateJsonData\x12-\n\ttimestamp\x18\x01 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12\'\n\x06states\x18\x02 \x01(\x0b2\x17.google.protobuf.Struct\x12E\n\x0bsub_devices\x18\x03 \x03(\x0b20.com.fundamentum.edge.v1.StateJsonData.SubDevice\x12.\n\x03qos\x18\x04 \x01(\x0e2\x1c.com.fundamentum.edge.v1.QosH\x00\x88\x01\x01\x1aK\n\tSubDevice\x12\x15\n\rserial_number\x18\x01 \x01(\t\x12\'\n\x06states\x18\x02 \x01(\x0b2\x17.google.protobuf.StructB\x06\n\x04_qos2\\\n\x0bStatesEvent\x12M\n\x0bPublishJson\x12&.com.fundamentum.edge.v1.StateJsonData\x1a\x16.google.protobuf.Emptyb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'states_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    _globals['_STATEJSONDATA']._serialized_start = 145
    _globals['_STATEJSONDATA']._serialized_end = 452
    _globals['_STATEJSONDATA_SUBDEVICE']._serialized_start = 369
    _globals['_STATEJSONDATA_SUBDEVICE']._serialized_end = 444
    _globals['_STATESEVENT']._serialized_start = 454
    _globals['_STATESEVENT']._serialized_end = 546