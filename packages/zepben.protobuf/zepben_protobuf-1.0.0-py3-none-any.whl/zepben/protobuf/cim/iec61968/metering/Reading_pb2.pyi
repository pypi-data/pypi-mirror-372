from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Reading(_message.Message):
    __slots__ = ("timestamp", "valueNull", "valueSet")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    VALUENULL_FIELD_NUMBER: _ClassVar[int]
    VALUESET_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    valueNull: _struct_pb2.NullValue
    valueSet: float
    def __init__(self, timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., valueNull: _Optional[_Union[_struct_pb2.NullValue, str]] = ..., valueSet: _Optional[float] = ...) -> None: ...
