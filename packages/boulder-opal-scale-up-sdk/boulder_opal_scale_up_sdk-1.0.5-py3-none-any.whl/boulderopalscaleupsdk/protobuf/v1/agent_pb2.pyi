from google.api import annotations_pb2 as _annotations_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RunProgramRequest(_message.Message):
    __slots__ = ("controller_type", "program", "calibrate_elements")
    CONTROLLER_TYPE_FIELD_NUMBER: _ClassVar[int]
    PROGRAM_FIELD_NUMBER: _ClassVar[int]
    CALIBRATE_ELEMENTS_FIELD_NUMBER: _ClassVar[int]
    controller_type: str
    program: str
    calibrate_elements: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, controller_type: _Optional[str] = ..., program: _Optional[str] = ..., calibrate_elements: _Optional[_Iterable[str]] = ...) -> None: ...

class RunProgramResponse(_message.Message):
    __slots__ = ("raw_data",)
    RAW_DATA_FIELD_NUMBER: _ClassVar[int]
    raw_data: _struct_pb2.Struct
    def __init__(self, raw_data: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class RunQuantumMachinesMixerCalibrationRequest(_message.Message):
    __slots__ = ("elements", "config")
    ELEMENTS_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    elements: _containers.RepeatedScalarFieldContainer[str]
    config: str
    def __init__(self, elements: _Optional[_Iterable[str]] = ..., config: _Optional[str] = ...) -> None: ...

class RunQuantumMachinesMixerCalibrationResponse(_message.Message):
    __slots__ = ("success", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    def __init__(self, success: bool = ..., error: _Optional[str] = ...) -> None: ...

class DisplayResultsRequest(_message.Message):
    __slots__ = ("message", "plots")
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    PLOTS_FIELD_NUMBER: _ClassVar[int]
    message: str
    plots: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, message: _Optional[str] = ..., plots: _Optional[_Iterable[str]] = ...) -> None: ...

class DisplayResultsResponse(_message.Message):
    __slots__ = ("empty",)
    EMPTY_FIELD_NUMBER: _ClassVar[int]
    empty: _empty_pb2.Empty
    def __init__(self, empty: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ...) -> None: ...

class AskRequest(_message.Message):
    __slots__ = ("message", "expected_response_type")
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_RESPONSE_TYPE_FIELD_NUMBER: _ClassVar[int]
    message: str
    expected_response_type: str
    def __init__(self, message: _Optional[str] = ..., expected_response_type: _Optional[str] = ...) -> None: ...

class AskResponse(_message.Message):
    __slots__ = ("response",)
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: str
    def __init__(self, response: _Optional[str] = ...) -> None: ...
