from . import continue_list_pb2 as _continue_list_pb2
from . import delete_pb2 as _delete_pb2
from . import get_pb2 as _get_pb2
from . import item_pb2 as _item_pb2
from . import list_pb2 as _list_pb2
from . import list_filters_pb2 as _list_filters_pb2
from . import put_pb2 as _put_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TransactionRequest(_message.Message):
    __slots__ = ("message_id", "begin", "get_items", "begin_list", "continue_list", "put_items", "delete_items", "commit", "abort")
    MESSAGE_ID_FIELD_NUMBER: _ClassVar[int]
    BEGIN_FIELD_NUMBER: _ClassVar[int]
    GET_ITEMS_FIELD_NUMBER: _ClassVar[int]
    BEGIN_LIST_FIELD_NUMBER: _ClassVar[int]
    CONTINUE_LIST_FIELD_NUMBER: _ClassVar[int]
    PUT_ITEMS_FIELD_NUMBER: _ClassVar[int]
    DELETE_ITEMS_FIELD_NUMBER: _ClassVar[int]
    COMMIT_FIELD_NUMBER: _ClassVar[int]
    ABORT_FIELD_NUMBER: _ClassVar[int]
    message_id: int
    begin: TransactionBegin
    get_items: TransactionGet
    begin_list: TransactionBeginList
    continue_list: TransactionContinueList
    put_items: TransactionPut
    delete_items: TransactionDelete
    commit: _empty_pb2.Empty
    abort: _empty_pb2.Empty
    def __init__(self, message_id: _Optional[int] = ..., begin: _Optional[_Union[TransactionBegin, _Mapping]] = ..., get_items: _Optional[_Union[TransactionGet, _Mapping]] = ..., begin_list: _Optional[_Union[TransactionBeginList, _Mapping]] = ..., continue_list: _Optional[_Union[TransactionContinueList, _Mapping]] = ..., put_items: _Optional[_Union[TransactionPut, _Mapping]] = ..., delete_items: _Optional[_Union[TransactionDelete, _Mapping]] = ..., commit: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., abort: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ...) -> None: ...

class TransactionResponse(_message.Message):
    __slots__ = ("message_id", "get_results", "put_ack", "list_results", "finished")
    MESSAGE_ID_FIELD_NUMBER: _ClassVar[int]
    GET_RESULTS_FIELD_NUMBER: _ClassVar[int]
    PUT_ACK_FIELD_NUMBER: _ClassVar[int]
    LIST_RESULTS_FIELD_NUMBER: _ClassVar[int]
    FINISHED_FIELD_NUMBER: _ClassVar[int]
    message_id: int
    get_results: TransactionGetResponse
    put_ack: TransactionPutAck
    list_results: TransactionListResponse
    finished: TransactionFinished
    def __init__(self, message_id: _Optional[int] = ..., get_results: _Optional[_Union[TransactionGetResponse, _Mapping]] = ..., put_ack: _Optional[_Union[TransactionPutAck, _Mapping]] = ..., list_results: _Optional[_Union[TransactionListResponse, _Mapping]] = ..., finished: _Optional[_Union[TransactionFinished, _Mapping]] = ...) -> None: ...

class TransactionBegin(_message.Message):
    __slots__ = ("store_id", "schema_version_id", "schema_id")
    STORE_ID_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_ID_FIELD_NUMBER: _ClassVar[int]
    store_id: int
    schema_version_id: int
    schema_id: int
    def __init__(self, store_id: _Optional[int] = ..., schema_version_id: _Optional[int] = ..., schema_id: _Optional[int] = ...) -> None: ...

class TransactionGet(_message.Message):
    __slots__ = ("gets",)
    GETS_FIELD_NUMBER: _ClassVar[int]
    gets: _containers.RepeatedCompositeFieldContainer[_get_pb2.GetItem]
    def __init__(self, gets: _Optional[_Iterable[_Union[_get_pb2.GetItem, _Mapping]]] = ...) -> None: ...

class TransactionBeginList(_message.Message):
    __slots__ = ("key_path_prefix", "limit", "sort_direction", "filter_conditions", "key_conditions")
    KEY_PATH_PREFIX_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    SORT_DIRECTION_FIELD_NUMBER: _ClassVar[int]
    FILTER_CONDITIONS_FIELD_NUMBER: _ClassVar[int]
    KEY_CONDITIONS_FIELD_NUMBER: _ClassVar[int]
    key_path_prefix: str
    limit: int
    sort_direction: _list_pb2.SortDirection
    filter_conditions: _containers.RepeatedCompositeFieldContainer[_list_filters_pb2.FilterCondition]
    key_conditions: _containers.RepeatedCompositeFieldContainer[_list_pb2.KeyCondition]
    def __init__(self, key_path_prefix: _Optional[str] = ..., limit: _Optional[int] = ..., sort_direction: _Optional[_Union[_list_pb2.SortDirection, str]] = ..., filter_conditions: _Optional[_Iterable[_Union[_list_filters_pb2.FilterCondition, _Mapping]]] = ..., key_conditions: _Optional[_Iterable[_Union[_list_pb2.KeyCondition, _Mapping]]] = ...) -> None: ...

class TransactionContinueList(_message.Message):
    __slots__ = ("token_data", "direction")
    TOKEN_DATA_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    token_data: bytes
    direction: _continue_list_pb2.ContinueListDirection
    def __init__(self, token_data: _Optional[bytes] = ..., direction: _Optional[_Union[_continue_list_pb2.ContinueListDirection, str]] = ...) -> None: ...

class TransactionPut(_message.Message):
    __slots__ = ("puts",)
    PUTS_FIELD_NUMBER: _ClassVar[int]
    puts: _containers.RepeatedCompositeFieldContainer[_put_pb2.PutItem]
    def __init__(self, puts: _Optional[_Iterable[_Union[_put_pb2.PutItem, _Mapping]]] = ...) -> None: ...

class TransactionDelete(_message.Message):
    __slots__ = ("deletes",)
    DELETES_FIELD_NUMBER: _ClassVar[int]
    deletes: _containers.RepeatedCompositeFieldContainer[_delete_pb2.DeleteItem]
    def __init__(self, deletes: _Optional[_Iterable[_Union[_delete_pb2.DeleteItem, _Mapping]]] = ...) -> None: ...

class TransactionGetResponse(_message.Message):
    __slots__ = ("items",)
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[_item_pb2.Item]
    def __init__(self, items: _Optional[_Iterable[_Union[_item_pb2.Item, _Mapping]]] = ...) -> None: ...

class GeneratedID(_message.Message):
    __slots__ = ("uint", "bytes")
    UINT_FIELD_NUMBER: _ClassVar[int]
    BYTES_FIELD_NUMBER: _ClassVar[int]
    uint: int
    bytes: bytes
    def __init__(self, uint: _Optional[int] = ..., bytes: _Optional[bytes] = ...) -> None: ...

class TransactionPutAck(_message.Message):
    __slots__ = ("generated_ids",)
    GENERATED_IDS_FIELD_NUMBER: _ClassVar[int]
    generated_ids: _containers.RepeatedCompositeFieldContainer[GeneratedID]
    def __init__(self, generated_ids: _Optional[_Iterable[_Union[GeneratedID, _Mapping]]] = ...) -> None: ...

class TransactionListResponse(_message.Message):
    __slots__ = ("result", "finished")
    RESULT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_FIELD_NUMBER: _ClassVar[int]
    result: _list_pb2.ListPartialResult
    finished: _list_pb2.ListFinished
    def __init__(self, result: _Optional[_Union[_list_pb2.ListPartialResult, _Mapping]] = ..., finished: _Optional[_Union[_list_pb2.ListFinished, _Mapping]] = ...) -> None: ...

class TransactionFinished(_message.Message):
    __slots__ = ("committed", "put_results", "delete_results")
    COMMITTED_FIELD_NUMBER: _ClassVar[int]
    PUT_RESULTS_FIELD_NUMBER: _ClassVar[int]
    DELETE_RESULTS_FIELD_NUMBER: _ClassVar[int]
    committed: bool
    put_results: _containers.RepeatedCompositeFieldContainer[_item_pb2.Item]
    delete_results: _containers.RepeatedCompositeFieldContainer[_delete_pb2.DeleteResult]
    def __init__(self, committed: bool = ..., put_results: _Optional[_Iterable[_Union[_item_pb2.Item, _Mapping]]] = ..., delete_results: _Optional[_Iterable[_Union[_delete_pb2.DeleteResult, _Mapping]]] = ...) -> None: ...
