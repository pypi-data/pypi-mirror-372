from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class GetAuthTokenRequest(_message.Message):
    __slots__ = ("access_key",)
    ACCESS_KEY_FIELD_NUMBER: _ClassVar[int]
    access_key: str
    def __init__(self, access_key: _Optional[str] = ...) -> None: ...

class GetAuthTokenResponse(_message.Message):
    __slots__ = ("auth_token", "expires_in_s")
    AUTH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_IN_S_FIELD_NUMBER: _ClassVar[int]
    auth_token: str
    expires_in_s: int
    def __init__(self, auth_token: _Optional[str] = ..., expires_in_s: _Optional[int] = ...) -> None: ...
