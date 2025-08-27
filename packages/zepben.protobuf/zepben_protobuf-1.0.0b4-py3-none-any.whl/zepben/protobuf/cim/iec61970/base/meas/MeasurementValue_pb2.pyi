from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MeasurementValue(_message.Message):
    __slots__ = ("timeStamp",)
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    timeStamp: _timestamp_pb2.Timestamp
    def __init__(self, timeStamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
