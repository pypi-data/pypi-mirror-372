"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from google.protobuf import struct_pb2 as google_dot_protobuf_dot_struct__pb2
from . import qos_pb2 as qos__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0cupdate.proto\x12\x17com.fundamentum.edge.v1\x1a\x1bgoogle/protobuf/empty.proto\x1a\x1cgoogle/protobuf/struct.proto\x1a\tqos.proto"\xe8\x01\n\x15FirmwareUpdateRequest\x12\n\n\x02id\x18\x01 \x01(\x04\x12F\n\x07updates\x18\x02 \x03(\x0b25.com.fundamentum.edge.v1.FirmwareUpdateRequest.Update\x1a{\n\x06Update\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x12\n\nidentifier\x18\x02 \x01(\t\x12\x16\n\x0etarget_devices\x18\x03 \x03(\t\x12)\n\x08metadata\x18\x04 \x01(\x0b2\x17.google.protobuf.Struct\x12\x0c\n\x04urls\x18\x05 \x03(\t"\xce\x04\n\x16FirmwareUpdateResponse\x12\n\n\x02id\x18\x01 \x01(\x04\x12P\n\x07success\x18\x02 \x01(\x0b2=.com.fundamentum.edge.v1.FirmwareUpdateResponse.SuccessStatusH\x00\x12L\n\x05error\x18\x03 \x01(\x0b2;.com.fundamentum.edge.v1.FirmwareUpdateResponse.ErrorStatusH\x00\x12P\n\x07ongoing\x18\x04 \x01(\x0b2=.com.fundamentum.edge.v1.FirmwareUpdateResponse.OngoingStatusH\x00\x12\x16\n\x0eserial_numbers\x18\x0c \x03(\t\x12\x0f\n\x07message\x18\r \x01(\t\x12.\n\x03qos\x18\x0f \x01(\x0e2\x1c.com.fundamentum.edge.v1.QosH\x01\x88\x01\x01\x1a\x0f\n\rSuccessStatus\x1a\x96\x01\n\x0bErrorStatus\x12N\n\x04code\x18\x01 \x01(\x0e2@.com.fundamentum.edge.v1.FirmwareUpdateResponse.ErrorStatus.Code"7\n\x04Code\x12\x14\n\x10CODE_UNSPECIFIED\x10\x00\x12\x19\n\x15CODE_EXPIRED_RESOURCE\x10\x01\x1a!\n\rOngoingStatus\x12\x10\n\x08progress\x18\x01 \x01(\rB\x08\n\x06statusB\x06\n\x04_qos2\xc0\x01\n\x0eFirmwareUpdate\x12U\n\tSubscribe\x12\x16.google.protobuf.Empty\x1a..com.fundamentum.edge.v1.FirmwareUpdateRequest0\x01\x12W\n\x0cUpdateStatus\x12/.com.fundamentum.edge.v1.FirmwareUpdateResponse\x1a\x16.google.protobuf.Emptyb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'update_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    _globals['_FIRMWAREUPDATEREQUEST']._serialized_start = 112
    _globals['_FIRMWAREUPDATEREQUEST']._serialized_end = 344
    _globals['_FIRMWAREUPDATEREQUEST_UPDATE']._serialized_start = 221
    _globals['_FIRMWAREUPDATEREQUEST_UPDATE']._serialized_end = 344
    _globals['_FIRMWAREUPDATERESPONSE']._serialized_start = 347
    _globals['_FIRMWAREUPDATERESPONSE']._serialized_end = 937
    _globals['_FIRMWAREUPDATERESPONSE_SUCCESSSTATUS']._serialized_start = 716
    _globals['_FIRMWAREUPDATERESPONSE_SUCCESSSTATUS']._serialized_end = 731
    _globals['_FIRMWAREUPDATERESPONSE_ERRORSTATUS']._serialized_start = 734
    _globals['_FIRMWAREUPDATERESPONSE_ERRORSTATUS']._serialized_end = 884
    _globals['_FIRMWAREUPDATERESPONSE_ERRORSTATUS_CODE']._serialized_start = 829
    _globals['_FIRMWAREUPDATERESPONSE_ERRORSTATUS_CODE']._serialized_end = 884
    _globals['_FIRMWAREUPDATERESPONSE_ONGOINGSTATUS']._serialized_start = 886
    _globals['_FIRMWAREUPDATERESPONSE_ONGOINGSTATUS']._serialized_end = 919
    _globals['_FIRMWAREUPDATE']._serialized_start = 940
    _globals['_FIRMWAREUPDATE']._serialized_end = 1132