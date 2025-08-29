from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar
DESCRIPTOR: _descriptor.FileDescriptor

class Qos(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    QOS_AT_MOST_ONCE: _ClassVar[Qos]
    QOS_AT_LEAST_ONCE: _ClassVar[Qos]
    QOS_EXACTLY_ONCE: _ClassVar[Qos]
QOS_AT_MOST_ONCE: Qos
QOS_AT_LEAST_ONCE: Qos
QOS_EXACTLY_ONCE: Qos