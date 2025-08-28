from google.api import annotations_pb2 as _annotations_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetJobSummaryRequest(_message.Message):
    __slots__ = ("job_id",)
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    def __init__(self, job_id: _Optional[str] = ...) -> None: ...

class GetJobSummaryResponse(_message.Message):
    __slots__ = ("job_summary_data",)
    JOB_SUMMARY_DATA_FIELD_NUMBER: _ClassVar[int]
    job_summary_data: _struct_pb2.Struct
    def __init__(self, job_summary_data: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class GetJobRequest(_message.Message):
    __slots__ = ("job_id",)
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    def __init__(self, job_id: _Optional[str] = ...) -> None: ...

class GetJobResponse(_message.Message):
    __slots__ = ("job_data",)
    JOB_DATA_FIELD_NUMBER: _ClassVar[int]
    job_data: _struct_pb2.Struct
    def __init__(self, job_data: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class ListJobsRequest(_message.Message):
    __slots__ = ("device_name", "job_name", "page", "limit", "sort_order")
    DEVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    JOB_NAME_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    device_name: str
    job_name: str
    page: int
    limit: int
    sort_order: int
    def __init__(self, device_name: _Optional[str] = ..., job_name: _Optional[str] = ..., page: _Optional[int] = ..., limit: _Optional[int] = ..., sort_order: _Optional[int] = ...) -> None: ...

class ListJobsResponse(_message.Message):
    __slots__ = ("jobs", "total_pages")
    JOBS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_PAGES_FIELD_NUMBER: _ClassVar[int]
    jobs: _containers.RepeatedCompositeFieldContainer[_struct_pb2.Struct]
    total_pages: int
    def __init__(self, jobs: _Optional[_Iterable[_Union[_struct_pb2.Struct, _Mapping]]] = ..., total_pages: _Optional[int] = ...) -> None: ...

class CreateRequest(_message.Message):
    __slots__ = ("app_name", "device_name", "device_data")
    APP_NAME_FIELD_NUMBER: _ClassVar[int]
    DEVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    DEVICE_DATA_FIELD_NUMBER: _ClassVar[int]
    app_name: str
    device_name: str
    device_data: _struct_pb2.Struct
    def __init__(self, app_name: _Optional[str] = ..., device_name: _Optional[str] = ..., device_data: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class CreateResponse(_message.Message):
    __slots__ = ("done",)
    DONE_FIELD_NUMBER: _ClassVar[int]
    done: bool
    def __init__(self, done: bool = ...) -> None: ...

class CopyRequest(_message.Message):
    __slots__ = ("from_device_name", "to_device_name")
    FROM_DEVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    TO_DEVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    from_device_name: str
    to_device_name: str
    def __init__(self, from_device_name: _Optional[str] = ..., to_device_name: _Optional[str] = ...) -> None: ...

class CopyResponse(_message.Message):
    __slots__ = ("done",)
    DONE_FIELD_NUMBER: _ClassVar[int]
    done: bool
    def __init__(self, done: bool = ...) -> None: ...

class GetDataRequest(_message.Message):
    __slots__ = ("app_name", "device_name")
    APP_NAME_FIELD_NUMBER: _ClassVar[int]
    DEVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    app_name: str
    device_name: str
    def __init__(self, app_name: _Optional[str] = ..., device_name: _Optional[str] = ...) -> None: ...

class GetDataResponse(_message.Message):
    __slots__ = ("processor_data", "controller_data", "defcals")
    PROCESSOR_DATA_FIELD_NUMBER: _ClassVar[int]
    CONTROLLER_DATA_FIELD_NUMBER: _ClassVar[int]
    DEFCALS_FIELD_NUMBER: _ClassVar[int]
    processor_data: _struct_pb2.Struct
    controller_data: _struct_pb2.Struct
    defcals: _containers.RepeatedCompositeFieldContainer[_struct_pb2.Struct]
    def __init__(self, processor_data: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., controller_data: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., defcals: _Optional[_Iterable[_Union[_struct_pb2.Struct, _Mapping]]] = ...) -> None: ...

class UpdateRequest(_message.Message):
    __slots__ = ("app_name", "device_name", "processor_data")
    APP_NAME_FIELD_NUMBER: _ClassVar[int]
    DEVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    PROCESSOR_DATA_FIELD_NUMBER: _ClassVar[int]
    app_name: str
    device_name: str
    processor_data: _struct_pb2.Struct
    def __init__(self, app_name: _Optional[str] = ..., device_name: _Optional[str] = ..., processor_data: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class UpdateResponse(_message.Message):
    __slots__ = ("processor_data", "controller_data")
    PROCESSOR_DATA_FIELD_NUMBER: _ClassVar[int]
    CONTROLLER_DATA_FIELD_NUMBER: _ClassVar[int]
    processor_data: _struct_pb2.Struct
    controller_data: _struct_pb2.Struct
    def __init__(self, processor_data: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., controller_data: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class DeleteRequest(_message.Message):
    __slots__ = ("app_name", "device_name")
    APP_NAME_FIELD_NUMBER: _ClassVar[int]
    DEVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    app_name: str
    device_name: str
    def __init__(self, app_name: _Optional[str] = ..., device_name: _Optional[str] = ...) -> None: ...

class DeleteResponse(_message.Message):
    __slots__ = ("done",)
    DONE_FIELD_NUMBER: _ClassVar[int]
    done: bool
    def __init__(self, done: bool = ...) -> None: ...

class GetMetadataRequest(_message.Message):
    __slots__ = ("device_name",)
    DEVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    device_name: str
    def __init__(self, device_name: _Optional[str] = ...) -> None: ...

class GetMetadataResponse(_message.Message):
    __slots__ = ("metadata",)
    METADATA_FIELD_NUMBER: _ClassVar[int]
    metadata: _struct_pb2.Struct
    def __init__(self, metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class GetAllDevicesMetadataRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetAllDevicesMetadataResponse(_message.Message):
    __slots__ = ("metadatas",)
    METADATAS_FIELD_NUMBER: _ClassVar[int]
    metadatas: _containers.RepeatedCompositeFieldContainer[_struct_pb2.Struct]
    def __init__(self, metadatas: _Optional[_Iterable[_Union[_struct_pb2.Struct, _Mapping]]] = ...) -> None: ...
