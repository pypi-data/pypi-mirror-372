from . import item_pb2 as _item_pb2
from . import list_pb2 as _list_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SyncListRequest(_message.Message):
    __slots__ = ("token_data", "schema_version_id", "schema_id")
    TOKEN_DATA_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_ID_FIELD_NUMBER: _ClassVar[int]
    token_data: bytes
    schema_version_id: int
    schema_id: int
    def __init__(self, token_data: _Optional[bytes] = ..., schema_version_id: _Optional[int] = ..., schema_id: _Optional[int] = ...) -> None: ...

class SyncListResponse(_message.Message):
    __slots__ = ("reset", "result", "finished")
    RESET_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_FIELD_NUMBER: _ClassVar[int]
    reset: SyncListReset
    result: SyncListPartialResponse
    finished: _list_pb2.ListFinished
    def __init__(self, reset: _Optional[_Union[SyncListReset, _Mapping]] = ..., result: _Optional[_Union[SyncListPartialResponse, _Mapping]] = ..., finished: _Optional[_Union[_list_pb2.ListFinished, _Mapping]] = ...) -> None: ...

class SyncListReset(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SyncListPartialResponse(_message.Message):
    __slots__ = ("changed_items", "deleted_items", "updated_item_keys_outside_list_window")
    CHANGED_ITEMS_FIELD_NUMBER: _ClassVar[int]
    DELETED_ITEMS_FIELD_NUMBER: _ClassVar[int]
    UPDATED_ITEM_KEYS_OUTSIDE_LIST_WINDOW_FIELD_NUMBER: _ClassVar[int]
    changed_items: _containers.RepeatedCompositeFieldContainer[_item_pb2.Item]
    deleted_items: _containers.RepeatedCompositeFieldContainer[DeletedItem]
    updated_item_keys_outside_list_window: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, changed_items: _Optional[_Iterable[_Union[_item_pb2.Item, _Mapping]]] = ..., deleted_items: _Optional[_Iterable[_Union[DeletedItem, _Mapping]]] = ..., updated_item_keys_outside_list_window: _Optional[_Iterable[str]] = ...) -> None: ...

class DeletedItem(_message.Message):
    __slots__ = ("key_path",)
    KEY_PATH_FIELD_NUMBER: _ClassVar[int]
    key_path: str
    def __init__(self, key_path: _Optional[str] = ...) -> None: ...
