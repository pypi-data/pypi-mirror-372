from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FilterCondition(_message.Message):
    __slots__ = ("item_type", "cel_expression")
    ITEM_TYPE_FIELD_NUMBER: _ClassVar[int]
    CEL_EXPRESSION_FIELD_NUMBER: _ClassVar[int]
    item_type: str
    cel_expression: CelExpression
    def __init__(self, item_type: _Optional[str] = ..., cel_expression: _Optional[_Union[CelExpression, _Mapping]] = ...) -> None: ...

class CelExpression(_message.Message):
    __slots__ = ("item_type", "expression")
    ITEM_TYPE_FIELD_NUMBER: _ClassVar[int]
    EXPRESSION_FIELD_NUMBER: _ClassVar[int]
    item_type: str
    expression: str
    def __init__(self, item_type: _Optional[str] = ..., expression: _Optional[str] = ...) -> None: ...
