from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class StatelyErrorDetails(_message.Message):
    __slots__ = ("stately_code", "message", "upstream_cause", "code")
    STATELY_CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    UPSTREAM_CAUSE_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    stately_code: str
    message: str
    upstream_cause: str
    code: int
    def __init__(self, stately_code: _Optional[str] = ..., message: _Optional[str] = ..., upstream_cause: _Optional[str] = ..., code: _Optional[int] = ...) -> None: ...
