from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ContinueScanRequest(_message.Message):
    __slots__ = ("token_data", "schema_version_id", "schema_id")
    TOKEN_DATA_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_ID_FIELD_NUMBER: _ClassVar[int]
    token_data: bytes
    schema_version_id: int
    schema_id: int
    def __init__(self, token_data: _Optional[bytes] = ..., schema_version_id: _Optional[int] = ..., schema_id: _Optional[int] = ...) -> None: ...
