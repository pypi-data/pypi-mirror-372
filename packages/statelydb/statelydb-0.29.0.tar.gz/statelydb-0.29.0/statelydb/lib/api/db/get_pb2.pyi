from . import item_pb2 as _item_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetRequest(_message.Message):
    __slots__ = ("store_id", "gets", "allow_stale", "schema_version_id", "schema_id")
    STORE_ID_FIELD_NUMBER: _ClassVar[int]
    GETS_FIELD_NUMBER: _ClassVar[int]
    ALLOW_STALE_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_ID_FIELD_NUMBER: _ClassVar[int]
    store_id: int
    gets: _containers.RepeatedCompositeFieldContainer[GetItem]
    allow_stale: bool
    schema_version_id: int
    schema_id: int
    def __init__(self, store_id: _Optional[int] = ..., gets: _Optional[_Iterable[_Union[GetItem, _Mapping]]] = ..., allow_stale: bool = ..., schema_version_id: _Optional[int] = ..., schema_id: _Optional[int] = ...) -> None: ...

class GetItem(_message.Message):
    __slots__ = ("key_path",)
    KEY_PATH_FIELD_NUMBER: _ClassVar[int]
    key_path: str
    def __init__(self, key_path: _Optional[str] = ...) -> None: ...

class GetResponse(_message.Message):
    __slots__ = ("items",)
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[_item_pb2.Item]
    def __init__(self, items: _Optional[_Iterable[_Union[_item_pb2.Item, _Mapping]]] = ...) -> None: ...
