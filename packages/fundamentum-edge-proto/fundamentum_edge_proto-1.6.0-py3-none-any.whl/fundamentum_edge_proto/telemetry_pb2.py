"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from . import qos_pb2 as qos__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0ftelemetry.proto\x12\x17com.fundamentum.edge.v1\x1a\x1bgoogle/protobuf/empty.proto\x1a\tqos.proto"n\n\x10TelemetryRequest\x12\x0f\n\x07payload\x18\x01 \x01(\x0c\x12\x11\n\tsub_topic\x18\x02 \x01(\t\x12.\n\x03qos\x18\x03 \x01(\x0e2\x1c.com.fundamentum.edge.v1.QosH\x00\x88\x01\x01B\x06\n\x04_qos2\xac\x01\n\tTelemetry\x12N\n\x07Publish\x12).com.fundamentum.edge.v1.TelemetryRequest\x1a\x16.google.protobuf.Empty(\x01\x12O\n\nPublishOne\x12).com.fundamentum.edge.v1.TelemetryRequest\x1a\x16.google.protobuf.Emptyb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'telemetry_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    _globals['_TELEMETRYREQUEST']._serialized_start = 84
    _globals['_TELEMETRYREQUEST']._serialized_end = 194
    _globals['_TELEMETRY']._serialized_start = 197
    _globals['_TELEMETRY']._serialized_end = 369