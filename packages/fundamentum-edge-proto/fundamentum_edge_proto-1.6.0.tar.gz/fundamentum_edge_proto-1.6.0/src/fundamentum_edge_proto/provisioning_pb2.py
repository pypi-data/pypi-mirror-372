"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x12provisioning.proto\x12\x17com.fundamentum.edge.v1"\xc2\x01\n\x10ProvisionRequest\x12\x14\n\x0capi_base_url\x18\x01 \x01(\t\x12\x12\n\nproject_id\x18\x02 \x01(\r\x12\x11\n\tregion_id\x18\x03 \x01(\r\x12\x13\n\x0bregistry_id\x18\x04 \x01(\r\x12\x15\n\rserial_number\x18\x05 \x01(\t\x12\x15\n\rasset_type_id\x18\x06 \x01(\x05\x12\x14\n\x0caccess_token\x18\x07 \x01(\t\x12\x18\n\x10replace_existing\x18\x08 \x01(\x08"\x13\n\x11ProvisionResponse"\x97\x01\n\x14RegisterShelfRequest\x12\x14\n\x0capi_base_url\x18\x01 \x01(\t\x12\x12\n\nproject_id\x18\x02 \x01(\r\x12\x11\n\tregion_id\x18\x03 \x01(\r\x12\x15\n\rserial_number\x18\x04 \x01(\t\x12\x15\n\rasset_type_id\x18\x05 \x01(\x05\x12\x14\n\x0caccess_token\x18\x06 \x01(\t"\x17\n\x15RegisterShelfResponse2\xe8\x01\n\x0cProvisioning\x12b\n\tProvision\x12).com.fundamentum.edge.v1.ProvisionRequest\x1a*.com.fundamentum.edge.v1.ProvisionResponse\x12t\n\x13RegisterShelfDevice\x12-.com.fundamentum.edge.v1.RegisterShelfRequest\x1a..com.fundamentum.edge.v1.RegisterShelfResponseb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'provisioning_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    _globals['_PROVISIONREQUEST']._serialized_start = 48
    _globals['_PROVISIONREQUEST']._serialized_end = 242
    _globals['_PROVISIONRESPONSE']._serialized_start = 244
    _globals['_PROVISIONRESPONSE']._serialized_end = 263
    _globals['_REGISTERSHELFREQUEST']._serialized_start = 266
    _globals['_REGISTERSHELFREQUEST']._serialized_end = 417
    _globals['_REGISTERSHELFRESPONSE']._serialized_start = 419
    _globals['_REGISTERSHELFRESPONSE']._serialized_end = 442
    _globals['_PROVISIONING']._serialized_start = 445
    _globals['_PROVISIONING']._serialized_end = 677