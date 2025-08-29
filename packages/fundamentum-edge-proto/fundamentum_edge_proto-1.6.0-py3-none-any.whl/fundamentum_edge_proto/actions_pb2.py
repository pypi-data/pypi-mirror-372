"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from . import qos_pb2 as qos__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\ractions.proto\x12\x17com.fundamentum.edge.v1\x1a\x1bgoogle/protobuf/empty.proto\x1a\tqos.proto"c\n\rActionRequest\x12\n\n\x02id\x18\x01 \x01(\x04\x12\x16\n\x0etarget_devices\x18\x02 \x03(\t\x12\x0f\n\x07version\x18\x03 \x01(\r\x12\x0c\n\x04type\x18\x04 \x01(\r\x12\x0f\n\x07payload\x18\x05 \x01(\x0c"\x99\x04\n\x0eActionResponse\x12\n\n\x02id\x18\x01 \x01(\x04\x12H\n\x07success\x18\x02 \x01(\x0b25.com.fundamentum.edge.v1.ActionResponse.SuccessStatusH\x00\x12H\n\x07failure\x18\x03 \x01(\x0b25.com.fundamentum.edge.v1.ActionResponse.FailureStatusH\x00\x12H\n\x07ongoing\x18\x04 \x01(\x0b25.com.fundamentum.edge.v1.ActionResponse.OngoingStatusH\x00\x12J\n\x08deferred\x18\x05 \x01(\x0b26.com.fundamentum.edge.v1.ActionResponse.DeferredStatusH\x00\x12\x16\n\x0eserial_numbers\x18\x0c \x03(\t\x12\x0f\n\x07message\x18\r \x01(\t\x12\x0f\n\x07payload\x18\x0e \x01(\x0c\x12.\n\x03qos\x18\x0f \x01(\x0e2\x1c.com.fundamentum.edge.v1.QosH\x01\x88\x01\x01\x1a\x0f\n\rSuccessStatus\x1a\x0f\n\rFailureStatus\x1a!\n\rOngoingStatus\x12\x10\n\x08progress\x18\x01 \x01(\r\x1a\x10\n\x0eDeferredStatusB\x08\n\x06statusB\x06\n\x04_qos2\xa9\x01\n\x07Actions\x12M\n\tSubscribe\x12\x16.google.protobuf.Empty\x1a&.com.fundamentum.edge.v1.ActionRequest0\x01\x12O\n\x0cUpdateStatus\x12\'.com.fundamentum.edge.v1.ActionResponse\x1a\x16.google.protobuf.Emptyb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'actions_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    _globals['_ACTIONREQUEST']._serialized_start = 82
    _globals['_ACTIONREQUEST']._serialized_end = 181
    _globals['_ACTIONRESPONSE']._serialized_start = 184
    _globals['_ACTIONRESPONSE']._serialized_end = 721
    _globals['_ACTIONRESPONSE_SUCCESSSTATUS']._serialized_start = 618
    _globals['_ACTIONRESPONSE_SUCCESSSTATUS']._serialized_end = 633
    _globals['_ACTIONRESPONSE_FAILURESTATUS']._serialized_start = 635
    _globals['_ACTIONRESPONSE_FAILURESTATUS']._serialized_end = 650
    _globals['_ACTIONRESPONSE_ONGOINGSTATUS']._serialized_start = 652
    _globals['_ACTIONRESPONSE_ONGOINGSTATUS']._serialized_end = 685
    _globals['_ACTIONRESPONSE_DEFERREDSTATUS']._serialized_start = 687
    _globals['_ACTIONRESPONSE_DEFERREDSTATUS']._serialized_end = 703
    _globals['_ACTIONS']._serialized_start = 724
    _globals['_ACTIONS']._serialized_end = 893