from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional
DESCRIPTOR: _descriptor.FileDescriptor

class ProvisionRequest(_message.Message):
    __slots__ = ('api_base_url', 'project_id', 'region_id', 'registry_id', 'serial_number', 'asset_type_id', 'access_token', 'replace_existing')
    API_BASE_URL_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    REGION_ID_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_ID_FIELD_NUMBER: _ClassVar[int]
    SERIAL_NUMBER_FIELD_NUMBER: _ClassVar[int]
    ASSET_TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    REPLACE_EXISTING_FIELD_NUMBER: _ClassVar[int]
    api_base_url: str
    project_id: int
    region_id: int
    registry_id: int
    serial_number: str
    asset_type_id: int
    access_token: str
    replace_existing: bool

    def __init__(self, api_base_url: _Optional[str]=..., project_id: _Optional[int]=..., region_id: _Optional[int]=..., registry_id: _Optional[int]=..., serial_number: _Optional[str]=..., asset_type_id: _Optional[int]=..., access_token: _Optional[str]=..., replace_existing: bool=...) -> None:
        ...

class ProvisionResponse(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class RegisterShelfRequest(_message.Message):
    __slots__ = ('api_base_url', 'project_id', 'region_id', 'serial_number', 'asset_type_id', 'access_token')
    API_BASE_URL_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    REGION_ID_FIELD_NUMBER: _ClassVar[int]
    SERIAL_NUMBER_FIELD_NUMBER: _ClassVar[int]
    ASSET_TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    api_base_url: str
    project_id: int
    region_id: int
    serial_number: str
    asset_type_id: int
    access_token: str

    def __init__(self, api_base_url: _Optional[str]=..., project_id: _Optional[int]=..., region_id: _Optional[int]=..., serial_number: _Optional[str]=..., asset_type_id: _Optional[int]=..., access_token: _Optional[str]=...) -> None:
        ...

class RegisterShelfResponse(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...