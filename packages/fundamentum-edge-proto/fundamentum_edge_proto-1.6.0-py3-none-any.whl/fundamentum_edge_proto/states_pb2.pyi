from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
import qos_pb2 as _qos_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class StateJsonData(_message.Message):
    __slots__ = ('timestamp', 'states', 'sub_devices', 'qos')

    class SubDevice(_message.Message):
        __slots__ = ('serial_number', 'states')
        SERIAL_NUMBER_FIELD_NUMBER: _ClassVar[int]
        STATES_FIELD_NUMBER: _ClassVar[int]
        serial_number: str
        states: _struct_pb2.Struct

        def __init__(self, serial_number: _Optional[str]=..., states: _Optional[_Union[_struct_pb2.Struct, _Mapping]]=...) -> None:
            ...
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    STATES_FIELD_NUMBER: _ClassVar[int]
    SUB_DEVICES_FIELD_NUMBER: _ClassVar[int]
    QOS_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    states: _struct_pb2.Struct
    sub_devices: _containers.RepeatedCompositeFieldContainer[StateJsonData.SubDevice]
    qos: _qos_pb2.Qos

    def __init__(self, timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]]=..., states: _Optional[_Union[_struct_pb2.Struct, _Mapping]]=..., sub_devices: _Optional[_Iterable[_Union[StateJsonData.SubDevice, _Mapping]]]=..., qos: _Optional[_Union[_qos_pb2.Qos, str]]=...) -> None:
        ...