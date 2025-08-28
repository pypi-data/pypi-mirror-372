from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ContinueListDirection(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CONTINUE_LIST_FORWARD: _ClassVar[ContinueListDirection]
    CONTINUE_LIST_BACKWARD: _ClassVar[ContinueListDirection]
CONTINUE_LIST_FORWARD: ContinueListDirection
CONTINUE_LIST_BACKWARD: ContinueListDirection

class ContinueListRequest(_message.Message):
    __slots__ = ("token_data", "direction", "schema_version_id", "schema_id")
    TOKEN_DATA_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_ID_FIELD_NUMBER: _ClassVar[int]
    token_data: bytes
    direction: ContinueListDirection
    schema_version_id: int
    schema_id: int
    def __init__(self, token_data: _Optional[bytes] = ..., direction: _Optional[_Union[ContinueListDirection, str]] = ..., schema_version_id: _Optional[int] = ..., schema_id: _Optional[int] = ...) -> None: ...
