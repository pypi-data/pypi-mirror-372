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

from typing import Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    field_validator,
    model_validator,
)

from boulderopalscaleupsdk.common.dtypes import Duration, DurationNsLike, TimeUnit
from boulderopalscaleupsdk.device.controller.base import ControllerType
from boulderopalscaleupsdk.third_party import quantum_machines as qm
from boulderopalscaleupsdk.third_party.quantum_machines import config as qm_config
from boulderopalscaleupsdk.third_party.quantum_machines.constants import (
    MIN_TIME_OF_FLIGHT,
    QUA_CLOCK_CYCLE,
)

QPUPortRef = str
OctaveRef = str
ControllerRef = str
ControllerPort = int


class QuaProgram(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    program: qm.QuaProgramMessage
    config: qm_config.QuaConfig

    @field_serializer("program")
    def serialize_program(self, program: qm.QuaProgramMessage) -> str:
        return program.to_json()

    @field_validator("program", mode="before")
    @classmethod
    def deserialize_program(cls, program: object) -> qm.QuaProgramMessage:
        if isinstance(program, qm.QuaProgramMessage):
            return program
        if isinstance(program, str | bytes):
            return qm.QuaProgramMessage().from_json(program)
        raise TypeError(f"Could not parse program from {type(program).__name__}.")

    def dumps(self) -> str:
        return self.model_dump_json()

    @classmethod
    def loads(cls, data: str) -> Self:
        return cls.model_validate_json(data)


class OctaveConfig(qm_config.OctaveConfig121):
    host: str | None = Field(default=None)
    port: int | None = Field(default=None)

    def to_qm_octave_config_121(self) -> qm_config.OctaveConfig121:
        return qm_config.OctaveConfig121.model_validate(self.model_dump())


class DrivePortConfig(BaseModel):
    port_type: Literal["drive"] = "drive"
    port_mapping: tuple[OctaveRef, ControllerPort]


class FluxPortConfig(BaseModel):
    port_type: Literal["flux"] = "flux"
    port_mapping: tuple[ControllerRef, ControllerPort]


class ReadoutPortConfig(BaseModel):
    port_type: Literal["readout"] = "readout"
    port_mapping: tuple[OctaveRef, ControllerPort]
    time_of_flight: DurationNsLike
    smearing: DurationNsLike = Field(default=Duration(0, TimeUnit.NS))

    @model_validator(mode="after")
    def _validate_readout_port_config(self) -> Self:
        time_of_flight_ns = self.time_of_flight.to_ns().value
        if time_of_flight_ns < MIN_TIME_OF_FLIGHT.to_ns().value:
            raise ValueError(f"time_of_flight must be >= {MIN_TIME_OF_FLIGHT}")

        if time_of_flight_ns % QUA_CLOCK_CYCLE.to_ns().value != 0:
            raise ValueError(f"time_of_flight must be a multiple of {QUA_CLOCK_CYCLE}")

        if self.smearing.to_ns().value > time_of_flight_ns - 8:
            raise ValueError(f"smearing must be at most {time_of_flight_ns - 8} ns")

        return self


OPXControllerConfig = qm_config.ControllerConfigType
OPX1000ControllerConfig = qm_config.OPX1000ControllerConfigType


class QuantumMachinesControllerInfo(BaseModel):
    """
    QuantumMachinesControllerInfo is a data model that represents the configuration
    and port settings for quantum machine controllers.

    NOTE: Interface must match OPX Config for first set of parameters, remainder are ours
        https://docs.quantum-machines.co/1.2.1/assets/qua_config.html#/paths/~1/get

    Attributes
    ----------
    controller_type : Literal[ControllerType.QUANTUM_MACHINES]
        The type of controller, which is always `ControllerType.QUANTUM_MACHINES`.
    controllers : dict[ControllerRef, OPXControllerConfig | OPX1000ControllerConfig]
        A dictionary mapping controller references to their respective configurations.
        The configurations can be either OPXControllerConfig or OPX1000ControllerConfig.
        Derived from OPX Config.
    octaves : dict[OctaveRef, OctaveConfig]
        A dictionary mapping octave references to their respective configurations.
        Derived from OPX Config.
    port_config : dict[PortRef, DrivePortConfig | FluxPortConfig | ReadoutPortConfig]
        A dictionary mapping port references to their respective port configurations.
        The configurations can be DrivePortConfig, FluxPortConfig, or ReadoutPortConfig.
        Not derived from OPX Config, this is our custom config.
    """

    controller_type: Literal[ControllerType.QUANTUM_MACHINES] = ControllerType.QUANTUM_MACHINES
    controllers: dict[ControllerRef, OPXControllerConfig | OPX1000ControllerConfig] = Field(
        default={},
    )
    octaves: dict[OctaveRef, OctaveConfig] = Field(default={})
    port_config: dict[QPUPortRef, DrivePortConfig | FluxPortConfig | ReadoutPortConfig]
