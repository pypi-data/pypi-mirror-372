# Copyright 2025 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.

"""Base agent module.

Contains logic for agent worker.
"""

import logging
from abc import abstractmethod
from typing import Protocol

from google.protobuf import any_pb2
from google.protobuf.message import Message
from google.protobuf.struct_pb2 import Struct
from grpc import aio as grpc
from grpc import ssl_channel_credentials
from pydantic_settings import BaseSettings, SettingsConfigDict

from boulderopalscaleupsdk.common.dtypes import GrpcMetadata, JobId
from boulderopalscaleupsdk.protobuf.v1 import agent_pb2, task_pb2, task_pb2_grpc

LOG = logging.getLogger(__name__)


class AgentSettings(BaseSettings):
    """Configuration for the Agent."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="QCTRL_SCALE_UP_",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )

    agent_id: str
    remote_url: str


class TaskHandler(Protocol):
    @abstractmethod
    async def handle(
        self,
        request: agent_pb2.RunProgramRequest
        | agent_pb2.RunQuantumMachinesMixerCalibrationRequest
        | agent_pb2.DisplayResultsRequest
        | agent_pb2.AskRequest,
    ) -> (
        agent_pb2.RunProgramResponse
        | agent_pb2.RunQuantumMachinesMixerCalibrationResponse
        | agent_pb2.DisplayResultsResponse
        | agent_pb2.AskResponse
        | task_pb2.TaskErrorDetail
    ): ...

    async def run(
        self,
        task: task_pb2.Task,
    ) -> any_pb2.Any | task_pb2.TaskErrorDetail:
        request = (
            _as_run_program_request(task.data)
            or _as_ask_request(task.data)
            or _as_run_qua_calibration_request(task.data)
            or _as_display_results_request(task.data)
        )
        match request:
            case (
                agent_pb2.RunProgramRequest()
                | agent_pb2.RunQuantumMachinesMixerCalibrationRequest()
                | agent_pb2.DisplayResultsRequest()
                | agent_pb2.AskRequest()
            ):
                return _as_any_message(await self.handle(request))
            case None:
                return task_pb2.TaskErrorDetail(
                    code=task_pb2.TaskError.TASK_ERROR_NOT_IMPLEMENTED,
                    detail="Unknown or unrecognized request.",
                )


def _as_any_message(message: Message) -> any_pb2.Any:
    msg = any_pb2.Any()
    msg.Pack(message)  # type: ignore[reportUnknownMemberType]
    return msg


def _as_run_program_request(
    task_result: any_pb2.Any,
) -> agent_pb2.RunProgramRequest | None:
    request = agent_pb2.RunProgramRequest()
    unpacked: bool = task_result.Unpack(request)  # type: ignore[reportUnknownMemberType]
    if not unpacked:
        return None

    return request


def _as_ask_request(
    task_result: any_pb2.Any,
) -> agent_pb2.AskRequest | None:
    request = agent_pb2.AskRequest()
    unpacked: bool = task_result.Unpack(request)  # type: ignore[reportUnknownMemberType]
    if not unpacked:
        return None

    return request


def _as_run_qua_calibration_request(
    task_result: any_pb2.Any,
) -> agent_pb2.RunQuantumMachinesMixerCalibrationRequest | None:
    request = agent_pb2.RunQuantumMachinesMixerCalibrationRequest()
    unpacked: bool = task_result.Unpack(request)  # type: ignore[reportUnknownMemberType]
    if not unpacked:
        return None

    return request


def _as_display_results_request(
    task_result: any_pb2.Any,
) -> agent_pb2.DisplayResultsRequest | None:
    request = agent_pb2.DisplayResultsRequest()
    unpacked: bool = task_result.Unpack(request)  # type: ignore[reportUnknownMemberType]
    if not unpacked:
        return None

    return request


class Agent:
    """Agent implementation."""

    def __init__(
        self,
        agent_settings: AgentSettings,
        handler: TaskHandler,
        grpc_interceptors: list[grpc.ClientInterceptor] | None = None,
    ) -> None:
        self._settings = agent_settings
        self._handler = handler
        self._channel: grpc.Channel | None = self._create_channel(
            agent_settings.remote_url,
            grpc_interceptors,
        )
        self._agent_manager = task_pb2_grpc.AgentManagerServiceStub(self._channel)
        self._state: task_pb2.AgentState = task_pb2.AGENT_STATE_ACTIVE_IDLE

    @property
    def agent_id(self) -> str:
        """The agent identifier."""
        return self._settings.agent_id

    def _create_channel(
        self,
        url: str,
        interceptors: list[grpc.ClientInterceptor] | None = None,
    ) -> grpc.Channel:
        """
        Create a gRPC channel.
        """
        host = url.split(":")[0]
        options = [
            ("grpc.max_send_message_length", 1024 * 1024 * 50),  # 50MB
            ("grpc.max_receive_message_length", 1024 * 1024 * 50),  # 50MB
        ]
        if host in ["localhost", "127.0.0.1", "0.0.0.0", "::"]:
            channel = grpc.insecure_channel(
                url,
                interceptors=interceptors,
                options=options,
            )
        else:
            channel = grpc.secure_channel(
                url,
                credentials=ssl_channel_credentials(),
                interceptors=interceptors,
                options=options,
            )
        return channel

    async def start_session(
        self,
        app: str,
        metadata: GrpcMetadata,
        device_name: str,
        routine: str,
        data: Struct | None,
    ) -> JobId | None:
        if not self._channel:
            raise RuntimeError("Cannot start session: agent is shutdown.")
        _data = any_pb2.Any()
        if data:
            _data.Pack(data)

        response: task_pb2.AgentTasksResponse = await self._agent_manager.StartSession(
            task_pb2.StartSessionRequest(
                agent_id=self.agent_id,
                app_name=app,
                device_name=device_name,
                routine_name=routine,
                data=_data,
            ),
            metadata=metadata,
        )
        self._state = response.target_state
        job_id: JobId | None = await self._resume(response, metadata)
        await self.shutdown()

        return job_id

    async def _resume(
        self,
        response: task_pb2.AgentTasksResponse,
        metadata: GrpcMetadata,
    ) -> JobId | None:
        tasks = response.tasks
        job_id = None
        while self._state not in [
            task_pb2.AGENT_STATE_SHUTDOWN_MANAGER_INITIATED,
            task_pb2.AGENT_STATE_SHUTDOWN_FAULT,
            task_pb2.AGENT_STATE_SHUTDOWN_CLIENT_INITIATED,
        ]:
            task_results: list[task_pb2.TaskResult] = []
            for task in tasks:
                err: task_pb2.TaskErrorDetail | None = None
                result: any_pb2.Any | None = None

                match await self._handler.run(task):
                    case task_pb2.TaskErrorDetail() as err:
                        pass
                    case any_pb2.Any() as result:
                        pass

                task_results.append(
                    task_pb2.TaskResult(
                        task_id=task.task_id,
                        session_id=task.session_id,
                        result=result,
                        error=err,
                    ),
                )

            _resp: task_pb2.AgentTasksResponse = await self._agent_manager.UpdateSession(
                task_pb2.UpdateSessionRequest(
                    session_id=response.session_id,
                    current_state=self._state,
                    results=task_results,
                    task_in_progress=[],
                ),
                metadata=metadata,
            )

            tasks = _resp.tasks
            self._state = _resp.target_state
            job_id = _resp.job_id

        return job_id or response.job_id

    async def shutdown(
        self,
        timeout: float | None = None,
        _: BaseException | None = None,
    ) -> None:
        """Shutdown the agent."""
        if self._channel:
            await self._channel.close(grace=timeout)
            self._channel = None
