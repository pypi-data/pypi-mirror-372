from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DeleteRequest(_message.Message):
    __slots__ = ("store_id", "deletes", "schema_version_id", "schema_id")
    STORE_ID_FIELD_NUMBER: _ClassVar[int]
    DELETES_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_ID_FIELD_NUMBER: _ClassVar[int]
    store_id: int
    deletes: _containers.RepeatedCompositeFieldContainer[DeleteItem]
    schema_version_id: int
    schema_id: int
    def __init__(self, store_id: _Optional[int] = ..., deletes: _Optional[_Iterable[_Union[DeleteItem, _Mapping]]] = ..., schema_version_id: _Optional[int] = ..., schema_id: _Optional[int] = ...) -> None: ...

class DeleteItem(_message.Message):
    __slots__ = ("key_path",)
    KEY_PATH_FIELD_NUMBER: _ClassVar[int]
    key_path: str
    def __init__(self, key_path: _Optional[str] = ...) -> None: ...

class DeleteResult(_message.Message):
    __slots__ = ("key_path",)
    KEY_PATH_FIELD_NUMBER: _ClassVar[int]
    key_path: str
    def __init__(self, key_path: _Optional[str] = ...) -> None: ...

class DeleteResponse(_message.Message):
    __slots__ = ("results",)
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[DeleteResult]
    def __init__(self, results: _Optional[_Iterable[_Union[DeleteResult, _Mapping]]] = ...) -> None: ...
