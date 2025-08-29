from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf import struct_pb2 as _struct_pb2
import qos_pb2 as _qos_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class FirmwareUpdateRequest(_message.Message):
    __slots__ = ('id', 'updates')

    class Update(_message.Message):
        __slots__ = ('name', 'identifier', 'target_devices', 'metadata', 'urls')
        NAME_FIELD_NUMBER: _ClassVar[int]
        IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
        TARGET_DEVICES_FIELD_NUMBER: _ClassVar[int]
        METADATA_FIELD_NUMBER: _ClassVar[int]
        URLS_FIELD_NUMBER: _ClassVar[int]
        name: str
        identifier: str
        target_devices: _containers.RepeatedScalarFieldContainer[str]
        metadata: _struct_pb2.Struct
        urls: _containers.RepeatedScalarFieldContainer[str]

        def __init__(self, name: _Optional[str]=..., identifier: _Optional[str]=..., target_devices: _Optional[_Iterable[str]]=..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]]=..., urls: _Optional[_Iterable[str]]=...) -> None:
            ...
    ID_FIELD_NUMBER: _ClassVar[int]
    UPDATES_FIELD_NUMBER: _ClassVar[int]
    id: int
    updates: _containers.RepeatedCompositeFieldContainer[FirmwareUpdateRequest.Update]

    def __init__(self, id: _Optional[int]=..., updates: _Optional[_Iterable[_Union[FirmwareUpdateRequest.Update, _Mapping]]]=...) -> None:
        ...

class FirmwareUpdateResponse(_message.Message):
    __slots__ = ('id', 'success', 'error', 'ongoing', 'serial_numbers', 'message', 'qos')

    class SuccessStatus(_message.Message):
        __slots__ = ()

        def __init__(self) -> None:
            ...

    class ErrorStatus(_message.Message):
        __slots__ = ('code',)

        class Code(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            CODE_UNSPECIFIED: _ClassVar[FirmwareUpdateResponse.ErrorStatus.Code]
            CODE_EXPIRED_RESOURCE: _ClassVar[FirmwareUpdateResponse.ErrorStatus.Code]
        CODE_UNSPECIFIED: FirmwareUpdateResponse.ErrorStatus.Code
        CODE_EXPIRED_RESOURCE: FirmwareUpdateResponse.ErrorStatus.Code
        CODE_FIELD_NUMBER: _ClassVar[int]
        code: FirmwareUpdateResponse.ErrorStatus.Code

        def __init__(self, code: _Optional[_Union[FirmwareUpdateResponse.ErrorStatus.Code, str]]=...) -> None:
            ...

    class OngoingStatus(_message.Message):
        __slots__ = ('progress',)
        PROGRESS_FIELD_NUMBER: _ClassVar[int]
        progress: int

        def __init__(self, progress: _Optional[int]=...) -> None:
            ...
    ID_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    ONGOING_FIELD_NUMBER: _ClassVar[int]
    SERIAL_NUMBERS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    QOS_FIELD_NUMBER: _ClassVar[int]
    id: int
    success: FirmwareUpdateResponse.SuccessStatus
    error: FirmwareUpdateResponse.ErrorStatus
    ongoing: FirmwareUpdateResponse.OngoingStatus
    serial_numbers: _containers.RepeatedScalarFieldContainer[str]
    message: str
    qos: _qos_pb2.Qos

    def __init__(self, id: _Optional[int]=..., success: _Optional[_Union[FirmwareUpdateResponse.SuccessStatus, _Mapping]]=..., error: _Optional[_Union[FirmwareUpdateResponse.ErrorStatus, _Mapping]]=..., ongoing: _Optional[_Union[FirmwareUpdateResponse.OngoingStatus, _Mapping]]=..., serial_numbers: _Optional[_Iterable[str]]=..., message: _Optional[str]=..., qos: _Optional[_Union[_qos_pb2.Qos, str]]=...) -> None:
        ...