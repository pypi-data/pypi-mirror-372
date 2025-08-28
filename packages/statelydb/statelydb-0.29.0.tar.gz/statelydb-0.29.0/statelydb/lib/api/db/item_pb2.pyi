from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Item(_message.Message):
    __slots__ = ("item_type", "proto", "json")
    ITEM_TYPE_FIELD_NUMBER: _ClassVar[int]
    PROTO_FIELD_NUMBER: _ClassVar[int]
    JSON_FIELD_NUMBER: _ClassVar[int]
    item_type: str
    proto: bytes
    json: _struct_pb2.Struct
    def __init__(self, item_type: _Optional[str] = ..., proto: _Optional[bytes] = ..., json: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...
