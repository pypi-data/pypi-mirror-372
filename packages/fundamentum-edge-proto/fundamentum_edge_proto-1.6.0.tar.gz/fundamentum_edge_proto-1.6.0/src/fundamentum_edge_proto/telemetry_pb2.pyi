from google.protobuf import empty_pb2 as _empty_pb2
import qos_pb2 as _qos_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class TelemetryRequest(_message.Message):
    __slots__ = ('payload', 'sub_topic', 'qos')
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    SUB_TOPIC_FIELD_NUMBER: _ClassVar[int]
    QOS_FIELD_NUMBER: _ClassVar[int]
    payload: bytes
    sub_topic: str
    qos: _qos_pb2.Qos

    def __init__(self, payload: _Optional[bytes]=..., sub_topic: _Optional[str]=..., qos: _Optional[_Union[_qos_pb2.Qos, str]]=...) -> None:
        ...