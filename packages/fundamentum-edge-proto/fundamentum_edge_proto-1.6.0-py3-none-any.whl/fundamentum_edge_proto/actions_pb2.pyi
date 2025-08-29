from google.protobuf import empty_pb2 as _empty_pb2
import qos_pb2 as _qos_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class ActionRequest(_message.Message):
    __slots__ = ('id', 'target_devices', 'version', 'type', 'payload')
    ID_FIELD_NUMBER: _ClassVar[int]
    TARGET_DEVICES_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    id: int
    target_devices: _containers.RepeatedScalarFieldContainer[str]
    version: int
    type: int
    payload: bytes

    def __init__(self, id: _Optional[int]=..., target_devices: _Optional[_Iterable[str]]=..., version: _Optional[int]=..., type: _Optional[int]=..., payload: _Optional[bytes]=...) -> None:
        ...

class ActionResponse(_message.Message):
    __slots__ = ('id', 'success', 'failure', 'ongoing', 'deferred', 'serial_numbers', 'message', 'payload', 'qos')

    class SuccessStatus(_message.Message):
        __slots__ = ()

        def __init__(self) -> None:
            ...

    class FailureStatus(_message.Message):
        __slots__ = ()

        def __init__(self) -> None:
            ...

    class OngoingStatus(_message.Message):
        __slots__ = ('progress',)
        PROGRESS_FIELD_NUMBER: _ClassVar[int]
        progress: int

        def __init__(self, progress: _Optional[int]=...) -> None:
            ...

    class DeferredStatus(_message.Message):
        __slots__ = ()

        def __init__(self) -> None:
            ...
    ID_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    FAILURE_FIELD_NUMBER: _ClassVar[int]
    ONGOING_FIELD_NUMBER: _ClassVar[int]
    DEFERRED_FIELD_NUMBER: _ClassVar[int]
    SERIAL_NUMBERS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    QOS_FIELD_NUMBER: _ClassVar[int]
    id: int
    success: ActionResponse.SuccessStatus
    failure: ActionResponse.FailureStatus
    ongoing: ActionResponse.OngoingStatus
    deferred: ActionResponse.DeferredStatus
    serial_numbers: _containers.RepeatedScalarFieldContainer[str]
    message: str
    payload: bytes
    qos: _qos_pb2.Qos

    def __init__(self, id: _Optional[int]=..., success: _Optional[_Union[ActionResponse.SuccessStatus, _Mapping]]=..., failure: _Optional[_Union[ActionResponse.FailureStatus, _Mapping]]=..., ongoing: _Optional[_Union[ActionResponse.OngoingStatus, _Mapping]]=..., deferred: _Optional[_Union[ActionResponse.DeferredStatus, _Mapping]]=..., serial_numbers: _Optional[_Iterable[str]]=..., message: _Optional[str]=..., payload: _Optional[bytes]=..., qos: _Optional[_Union[_qos_pb2.Qos, str]]=...) -> None:
        ...