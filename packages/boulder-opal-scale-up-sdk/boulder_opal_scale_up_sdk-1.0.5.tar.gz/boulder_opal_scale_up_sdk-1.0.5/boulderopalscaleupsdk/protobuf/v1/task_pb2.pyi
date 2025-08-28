from google.api import annotations_pb2 as _annotations_pb2
from google.protobuf import any_pb2 as _any_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AgentState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AGENT_STATE_UNSPECIFIED: _ClassVar[AgentState]
    AGENT_STATE_ACTIVE_SESSION: _ClassVar[AgentState]
    AGENT_STATE_ACTIVE_IDLE: _ClassVar[AgentState]
    AGENT_STATE_SHUTDOWN_CLIENT_INITIATED: _ClassVar[AgentState]
    AGENT_STATE_SHUTDOWN_MANAGER_INITIATED: _ClassVar[AgentState]
    AGENT_STATE_SHUTDOWN_FAULT: _ClassVar[AgentState]

class TaskError(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TASK_ERROR_UNSPECIFIED: _ClassVar[TaskError]
    TASK_ERROR_NOT_IMPLEMENTED: _ClassVar[TaskError]
AGENT_STATE_UNSPECIFIED: AgentState
AGENT_STATE_ACTIVE_SESSION: AgentState
AGENT_STATE_ACTIVE_IDLE: AgentState
AGENT_STATE_SHUTDOWN_CLIENT_INITIATED: AgentState
AGENT_STATE_SHUTDOWN_MANAGER_INITIATED: AgentState
AGENT_STATE_SHUTDOWN_FAULT: AgentState
TASK_ERROR_UNSPECIFIED: TaskError
TASK_ERROR_NOT_IMPLEMENTED: TaskError

class StartSessionRequest(_message.Message):
    __slots__ = ("agent_id", "app_name", "device_name", "routine_name", "data")
    AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    APP_NAME_FIELD_NUMBER: _ClassVar[int]
    DEVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    ROUTINE_NAME_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    agent_id: str
    app_name: str
    device_name: str
    routine_name: str
    data: _any_pb2.Any
    def __init__(self, agent_id: _Optional[str] = ..., app_name: _Optional[str] = ..., device_name: _Optional[str] = ..., routine_name: _Optional[str] = ..., data: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...

class UpdateSessionRequest(_message.Message):
    __slots__ = ("session_id", "current_state", "results", "task_in_progress")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENT_STATE_FIELD_NUMBER: _ClassVar[int]
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    TASK_IN_PROGRESS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    current_state: AgentState
    results: _containers.RepeatedCompositeFieldContainer[TaskResult]
    task_in_progress: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, session_id: _Optional[str] = ..., current_state: _Optional[_Union[AgentState, str]] = ..., results: _Optional[_Iterable[_Union[TaskResult, _Mapping]]] = ..., task_in_progress: _Optional[_Iterable[str]] = ...) -> None: ...

class AgentTasksResponse(_message.Message):
    __slots__ = ("session_id", "target_state", "tasks", "invalidate_tasks", "retry_tasks", "job_id")
    class RetryTasksEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    TARGET_STATE_FIELD_NUMBER: _ClassVar[int]
    TASKS_FIELD_NUMBER: _ClassVar[int]
    INVALIDATE_TASKS_FIELD_NUMBER: _ClassVar[int]
    RETRY_TASKS_FIELD_NUMBER: _ClassVar[int]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    target_state: AgentState
    tasks: _containers.RepeatedCompositeFieldContainer[Task]
    invalidate_tasks: _containers.RepeatedScalarFieldContainer[str]
    retry_tasks: _containers.ScalarMap[str, str]
    job_id: str
    def __init__(self, session_id: _Optional[str] = ..., target_state: _Optional[_Union[AgentState, str]] = ..., tasks: _Optional[_Iterable[_Union[Task, _Mapping]]] = ..., invalidate_tasks: _Optional[_Iterable[str]] = ..., retry_tasks: _Optional[_Mapping[str, str]] = ..., job_id: _Optional[str] = ...) -> None: ...

class Task(_message.Message):
    __slots__ = ("task_id", "session_id", "task_type", "data", "timeout_seconds", "deadline", "depends_on")
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_TYPE_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_SECONDS_FIELD_NUMBER: _ClassVar[int]
    DEADLINE_FIELD_NUMBER: _ClassVar[int]
    DEPENDS_ON_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    session_id: str
    task_type: str
    data: _any_pb2.Any
    timeout_seconds: int
    deadline: int
    depends_on: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, task_id: _Optional[str] = ..., session_id: _Optional[str] = ..., task_type: _Optional[str] = ..., data: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., timeout_seconds: _Optional[int] = ..., deadline: _Optional[int] = ..., depends_on: _Optional[_Iterable[str]] = ...) -> None: ...

class TaskResult(_message.Message):
    __slots__ = ("task_id", "session_id", "result_type", "result", "error")
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    RESULT_TYPE_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    session_id: str
    result_type: str
    result: _any_pb2.Any
    error: TaskErrorDetail
    def __init__(self, task_id: _Optional[str] = ..., session_id: _Optional[str] = ..., result_type: _Optional[str] = ..., result: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., error: _Optional[_Union[TaskErrorDetail, _Mapping]] = ...) -> None: ...

class TaskErrorDetail(_message.Message):
    __slots__ = ("code", "detail")
    CODE_FIELD_NUMBER: _ClassVar[int]
    DETAIL_FIELD_NUMBER: _ClassVar[int]
    code: TaskError
    detail: str
    def __init__(self, code: _Optional[_Union[TaskError, str]] = ..., detail: _Optional[str] = ...) -> None: ...
