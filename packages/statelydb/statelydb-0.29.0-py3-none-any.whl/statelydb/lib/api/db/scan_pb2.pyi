from . import list_filters_pb2 as _list_filters_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BeginScanRequest(_message.Message):
    __slots__ = ("store_id", "filter_conditions", "limit", "segmentation_params", "schema_version_id", "schema_id")
    STORE_ID_FIELD_NUMBER: _ClassVar[int]
    FILTER_CONDITIONS_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    SEGMENTATION_PARAMS_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_ID_FIELD_NUMBER: _ClassVar[int]
    store_id: int
    filter_conditions: _containers.RepeatedCompositeFieldContainer[_list_filters_pb2.FilterCondition]
    limit: int
    segmentation_params: SegmentationParams
    schema_version_id: int
    schema_id: int
    def __init__(self, store_id: _Optional[int] = ..., filter_conditions: _Optional[_Iterable[_Union[_list_filters_pb2.FilterCondition, _Mapping]]] = ..., limit: _Optional[int] = ..., segmentation_params: _Optional[_Union[SegmentationParams, _Mapping]] = ..., schema_version_id: _Optional[int] = ..., schema_id: _Optional[int] = ...) -> None: ...

class SegmentationParams(_message.Message):
    __slots__ = ("total_segments", "segment_index")
    TOTAL_SEGMENTS_FIELD_NUMBER: _ClassVar[int]
    SEGMENT_INDEX_FIELD_NUMBER: _ClassVar[int]
    total_segments: int
    segment_index: int
    def __init__(self, total_segments: _Optional[int] = ..., segment_index: _Optional[int] = ...) -> None: ...
