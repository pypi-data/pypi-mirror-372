from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ListToken(_message.Message):
    __slots__ = ("token_data", "can_continue", "can_sync", "schema_version_id")
    TOKEN_DATA_FIELD_NUMBER: _ClassVar[int]
    CAN_CONTINUE_FIELD_NUMBER: _ClassVar[int]
    CAN_SYNC_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    token_data: bytes
    can_continue: bool
    can_sync: bool
    schema_version_id: int
    def __init__(self, token_data: _Optional[bytes] = ..., can_continue: bool = ..., can_sync: bool = ..., schema_version_id: _Optional[int] = ...) -> None: ...
