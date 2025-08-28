from . import item_pb2 as _item_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PutRequest(_message.Message):
    __slots__ = ("store_id", "puts", "schema_version_id", "schema_id")
    STORE_ID_FIELD_NUMBER: _ClassVar[int]
    PUTS_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_ID_FIELD_NUMBER: _ClassVar[int]
    store_id: int
    puts: _containers.RepeatedCompositeFieldContainer[PutItem]
    schema_version_id: int
    schema_id: int
    def __init__(self, store_id: _Optional[int] = ..., puts: _Optional[_Iterable[_Union[PutItem, _Mapping]]] = ..., schema_version_id: _Optional[int] = ..., schema_id: _Optional[int] = ...) -> None: ...

class PutItem(_message.Message):
    __slots__ = ("item", "overwrite_metadata_timestamps", "must_not_exist")
    ITEM_FIELD_NUMBER: _ClassVar[int]
    OVERWRITE_METADATA_TIMESTAMPS_FIELD_NUMBER: _ClassVar[int]
    MUST_NOT_EXIST_FIELD_NUMBER: _ClassVar[int]
    item: _item_pb2.Item
    overwrite_metadata_timestamps: bool
    must_not_exist: bool
    def __init__(self, item: _Optional[_Union[_item_pb2.Item, _Mapping]] = ..., overwrite_metadata_timestamps: bool = ..., must_not_exist: bool = ...) -> None: ...

class PutResponse(_message.Message):
    __slots__ = ("items",)
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[_item_pb2.Item]
    def __init__(self, items: _Optional[_Iterable[_Union[_item_pb2.Item, _Mapping]]] = ...) -> None: ...
