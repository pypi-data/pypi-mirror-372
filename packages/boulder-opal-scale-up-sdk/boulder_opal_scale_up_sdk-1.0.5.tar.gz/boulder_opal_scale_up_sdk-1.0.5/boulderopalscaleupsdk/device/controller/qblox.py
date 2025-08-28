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

"""
QBLOX Quantum Control Stack
"""

__all__ = (
    "DEFAULT_MODULE_CONSTRAINTS",
    "AcquisitionConfig",
    "BitStrideArrayEncoding",
    "ChannelType",
    "ComplexChannel",
    "IndexedData",
    "ModuleAddr",
    "ModuleAddrType",
    "ModuleConstraints",
    "ModuleType",
    "OutputAcquisition",
    "OutputBinnedAcquisition",
    "OutputBinnedAcquisitionIntegrationData",
    "OutputIndexedAcquisition",
    "OutputScopedAcquisition",
    "OutputScopedAcquisitionData",
    "OutputSequencerAcquisitions",
    "PortAddr",
    "PortAddrType",
    "PreparedProgram",
    "PreparedSequenceProgram",
    "RealChannel",
    "SequenceProgram",
    "SequencerAddr",
    "SequencerAddrType",
    "SequencerResults",
    "process_sequencer_output",
    "validate_channel",
)

import dataclasses
import enum
import math
import re
from dataclasses import dataclass
from typing import Annotated, Any, ClassVar, Literal, Self, TypeVar

import numpy as np
from pydantic import BaseModel, BeforeValidator, Field, PlainSerializer, model_validator

from boulderopalscaleupsdk.device.controller.base import Backend, ControllerType

# ==================================================================================================
# Addressing
# ==================================================================================================
_RE_SEQUENCER_ADDR = re.compile(r"^(?P<cluster>[^:]+):(?P<slot>\d+):s(?P<num>\d+)$")
_RE_MODULE_ADDR = re.compile(r"^(?P<cluster>[^:]+):(?P<slot>\d+)$")
_RE_PORT_ADDR = re.compile(
    r"^(?P<cluster>[^:]+):(?P<slot>\d+):p(?P<dir>(O|I))(?P<num>\d+)$",
)


class ModuleType(str, enum.Enum):
    """Enumeration of QBLOX modules."""

    QCM = "QCM"
    QRM = "QRM"
    QCM_RF = "QCM_RF"
    QRM_RF = "QRM_RF"
    QTM = "QTM"
    QDM = "QDM"
    EOM = "EOM"
    LINQ = "LINQ"
    QRC = "QRC"


@dataclass(frozen=True, eq=True)
class ModuleAddr:
    """Address to a module in a QBLOX control stack."""

    cluster: str
    slot: int

    def __str__(self) -> str:
        """Address as a string.

        This is used for serialization/deserialization and must match the Regex pattern defined in
        this module. See `_RE_MODULE_ADDR`
        """
        return f"{self.cluster}:{self.slot}"

    @classmethod
    def parse(cls, data: str) -> Self:
        mch = _RE_MODULE_ADDR.match(data)
        if mch is None:
            raise ValueError("Could not parse module address.")
        return cls(cluster=mch.group("cluster"), slot=int(mch.group("slot")))


@dataclass(frozen=True)
class SequencerAddr:
    """Address to a sequencer (located on a specific module) in a QBLOX control stack."""

    cluster: str
    slot: int
    number: int

    @property
    def module(self) -> ModuleAddr:
        return ModuleAddr(self.cluster, self.slot)

    def __hash__(self) -> int:
        return hash(str(self))

    def __eq__(self, other) -> bool:
        return isinstance(other, SequencerAddr) and str(other) == str(self)

    def __str__(self) -> str:
        """Address as a string.

        This is used for serialization/deserialization and must match the Regex pattern defined in
        this module. See `_RE_SEQUENCER_ADDR`
        """
        return f"{self.cluster}:{self.slot}:s{self.number}"

    @classmethod
    def parse(cls, data: str) -> Self:
        mch = _RE_SEQUENCER_ADDR.match(data)
        if mch is None:
            raise ValueError("Could not parse sequencer address.")
        return cls(
            cluster=mch.group("cluster"),
            slot=int(mch.group("slot")),
            number=int(mch.group("num")),
        )


@dataclass(frozen=True, eq=True)
class PortAddr:
    """Address to a hardware port (located on a specific module) in a QBLOX control stack."""

    cluster: str
    slot: int
    direction: Literal["out", "in"]
    number: int

    @property
    def module(self) -> ModuleAddr:
        return ModuleAddr(self.cluster, self.slot)

    def __str__(self) -> str:
        """Address as a string.

        This is used for serialization/deserialization and must match the Regex pattern defined in
        this module. See `_RE_PORT_ADDR`
        """
        direction = "O" if self.direction == "out" else "I"
        return f"{self.cluster}:{self.slot}:p{direction}{self.number}"

    @classmethod
    def parse(cls, data: str) -> Self:
        mch = _RE_PORT_ADDR.match(data)
        if mch is None:
            raise ValueError("Could not parse port address.")
        direction: Literal["out", "in"] = "out" if mch.group("dir") == "O" else "in"
        return cls(
            cluster=mch.group("cluster"),
            slot=int(mch.group("slot")),
            direction=direction,
            number=int(mch.group("num")),
        )


T = TypeVar("T", bound=ModuleAddr | SequencerAddr | PortAddr)


def _addr_validator(dtype: type[T]) -> BeforeValidator:
    """Return a Pydantic BeforeValidator to adapt address type with Pydantic."""

    def _validator(obj: object):
        if isinstance(obj, dtype):  # Allow instantiation with Python object
            return obj
        if isinstance(obj, str):  # Parse from JSON
            return dtype.parse(obj)
        raise TypeError(f"Invalid type {type(obj).__name__} for {type(dtype).__name__}.")

    return BeforeValidator(_validator)


# Annotated types with Pydantic validator and serializer.
ModuleAddrType = Annotated[ModuleAddr, _addr_validator(ModuleAddr), PlainSerializer(str)]
SequencerAddrType = Annotated[SequencerAddr, _addr_validator(SequencerAddr), PlainSerializer(str)]
PortAddrType = Annotated[PortAddr, _addr_validator(PortAddr), PlainSerializer(str)]


# ==================================================================================================
# Signalling Channels
# ==================================================================================================
class RealChannel(BaseModel):
    """A real channel targeting a single hardware port on a QBLOX module."""

    mode: Literal["real"] = "real"
    port: PortAddrType

    @property
    def module(self) -> ModuleAddr:
        return ModuleAddr(self.port.cluster, self.port.slot)

    @property
    def direction(self) -> Literal["out", "in"]:
        return self.port.direction

    def __str__(self) -> str:
        return f"{self.port!s}[R]"


class ComplexChannel(BaseModel):
    """A Complex channel targeting a single hardware port on a QBLOX module."""

    mode: Literal["complex"] = "complex"
    i_port: PortAddrType
    q_port: PortAddrType

    @property
    def module(self) -> ModuleAddr:
        return ModuleAddr(self.i_port.cluster, self.i_port.slot)

    @property
    def direction(self) -> Literal["out", "in"]:
        return self.i_port.direction

    def __str__(self) -> str:
        return f"{self.i_port!s}_{self.q_port.number}[Z]"

    @model_validator(mode="after")
    def validate_i_q_ports(self) -> "ComplexChannel":
        ii = self.i_port
        qq = self.q_port
        if ii.cluster != qq.cluster or ii.slot != qq.slot:
            raise ValueError("I and Q ports must be on the same cluster+module.")
        if ii.direction != qq.direction:
            raise ValueError("I and Q ports must be in the same direction.")
        return self


ChannelType = RealChannel | ComplexChannel


# ==================================================================================================
# Controller information
# ==================================================================================================
class PortConnection(BaseModel):  # pragma: no cover
    """
    The connections involved for a QPU port.

    Attributes
    ----------
    ch_out: ChannelType
        The output channel that will signal towards the QPU port
    ch_in: ChannelType or None, optional
        The input channel from which signals will be acquired from the QPU port. This is optional,
        as not all modules support acquisitions. If an input channel is specified, it must be
        located on the same module as the output channel.

    Notes
    -----
    The direction of channels is referenced against the QBLOX control stack. I.e. the "out"
    direction is outwards from the control stack. The following diagram depicts a simple setup with
    the arrows indicating a control channel.

        ┌────────┐           ┌───────────────┐
        │        │─── out ──►│ Port: p_xy1   │
        │ QBLOX  │           └───────────────┘
        │ Stack  │           ┌───────────────┐
        │        │─── out ──►│ Port: p_flrr0 │
        │        │◄── in ────│               │
        └────────┘           └───────────────┘
                                 QPU fridge
    """

    ch_out: ChannelType
    ch_in: ChannelType | None = None

    @model_validator(mode="after")
    def validate_channels(self) -> "PortConnection":
        if self.ch_in is not None and self.ch_in.module != self.ch_out.module:
            raise ValueError("I/O channels for an element must be on the same module.")
        return self

    @property
    def module(self) -> ModuleAddr:
        return self.ch_out.module


class QBLOXControllerInfo(BaseModel):  # pragma: no cover
    """
    Controller information needed for program compilation and control.

    Attributes
    ----------
    controller_type: Literal[ControllerType.QBLOX]
        The type of controller, which is always `ControllerType.QBLOX` for this class.
    modules: dict[ModuleAddrType, ModuleType]
        The modules connected to the QBLOX stack.
    port_config: dict[str, PortConnection]
        The dictionary of ports with their types and addresses.
    """

    controller_type: Literal[ControllerType.QBLOX] = ControllerType.QBLOX
    modules: dict[ModuleAddrType, ModuleType]
    port_config: dict[str, PortConnection]


# ==================================================================================================
# Instrument management
# ==================================================================================================
class SequencerParams(BaseModel):
    nco_freq: float | None = Field(default=None)
    gain_awg_path0: float | None = Field(default=None, ge=-1.0, le=1.0)
    offset_awg_path0: float | None = Field(default=None, ge=-1.0, le=1.0)
    gain_awg_path1: float | None = Field(default=None, ge=-1.0, le=1.0)
    offset_awg_path1: float | None = Field(default=None, ge=-1.0, le=1.0)
    marker_ovr_en: bool | None = Field(default=None)
    marker_ovr_value: int | None = Field(default=None, ge=0, le=15)
    mod_en_awg: bool | None = Field(default=None)
    demod_en_acq: bool | None = Field(default=None)
    sync_en: bool | None = Field(default=None)
    nco_prop_delay_comp_en: bool | None = Field(default=True)
    integration_length_acq: int | None = Field(default=None, ge=4, le=16777212, multiple_of=4)


class QcmParams(BaseModel):
    out0_offset: float | None = Field(default=None, ge=-2.5, le=2.5)
    out1_offset: float | None = Field(default=None, ge=-2.5, le=2.5)
    out2_offset: float | None = Field(default=None, ge=-2.5, le=2.5)
    out3_offset: float | None = Field(default=None, ge=-2.5, le=2.5)

    def update(self, other: Self) -> None:
        if self == other:
            return  # Nothing to do

        self.out0_offset = pick_only_one_or_raise(self.out0_offset, other.out0_offset)
        self.out1_offset = pick_only_one_or_raise(self.out1_offset, other.out1_offset)
        self.out2_offset = pick_only_one_or_raise(self.out2_offset, other.out2_offset)
        self.out3_offset = pick_only_one_or_raise(self.out3_offset, other.out3_offset)


class QcmRfParams(BaseModel):
    out0_att: int | None = Field(default=None, ge=0, le=60, multiple_of=2)
    out1_att: int | None = Field(default=None, ge=0, le=60, multiple_of=2)

    out0_lo_freq: float | None = Field(default=None, gt=0)
    out0_lo_en: bool | None = Field(default=None)
    out1_lo_freq: float | None = Field(default=None, gt=0)
    out1_lo_en: bool | None = Field(default=None)

    def update(self, other: Self) -> None:
        if self == other:
            return  # Nothing to do

        self.out0_att = pick_only_one_or_raise(self.out0_att, other.out0_att)
        self.out1_att = pick_only_one_or_raise(self.out1_att, other.out1_att)
        self.out0_lo_freq = pick_only_one_or_raise(self.out0_lo_freq, other.out0_lo_freq)
        self.out0_lo_en = pick_only_one_or_raise(self.out0_lo_en, other.out0_lo_en)
        self.out1_lo_freq = pick_only_one_or_raise(self.out1_lo_freq, other.out1_lo_freq)
        self.out1_lo_en = pick_only_one_or_raise(self.out1_lo_en, other.out1_lo_en)


class QrmRfParams(BaseModel):
    out0_att: int | None = Field(default=None, ge=0, le=60, multiple_of=2)

    out0_in0_lo_freq: float | None = Field(default=None, gt=0)
    out0_in0_lo_en: bool | None = Field(default=None)

    def update(self, other: Self) -> None:
        if self == other:
            return  # Nothing to do

        self.out0_att = pick_only_one_or_raise(self.out0_att, other.out0_att)
        self.out0_in0_lo_freq = pick_only_one_or_raise(
            self.out0_in0_lo_freq,
            other.out0_in0_lo_freq,
        )
        self.out0_in0_lo_en = pick_only_one_or_raise(self.out0_in0_lo_en, other.out0_in0_lo_en)


ModuleParams = QcmParams | QcmRfParams | QrmRfParams


T0 = TypeVar("T0")


def pick_only_one_or_raise(a: T0 | None, b: T0 | None) -> T0 | None:
    if a == b:
        return a
    if a is None:
        return b
    if b is None:
        return a
    raise ValueError(f"Cannot resolve conflict between given parameters {a} and {b}!")


# ==================================================================================================
# Programs
# ==================================================================================================
class IndexedData(BaseModel):
    """Used for sequence waveforms and weights."""

    data: list[float]
    index: int

    def data_equal(self, samples: list[float]) -> bool:
        """Whether the samples provided match the data in this object."""
        if len(samples) != len(self.data):
            return False
        return all(
            sample_1 == sample_2 for sample_1, sample_2 in zip(samples, self.data, strict=False)
        )


class AcquisitionConfig(BaseModel):
    """Acquisition configuration for Q1ASM programs."""

    num_bins: int
    index: int


class SequenceProgram(BaseModel):
    """A Q1 Sequence Program."""

    backend: ClassVar = Backend.QBLOX_Q1ASM

    program: str
    waveforms: dict[str, IndexedData] = {}
    weights: dict[str, IndexedData] = {}
    acquisitions: dict[str, AcquisitionConfig] = {}
    acquisition_scopes: list[str] = []
    acquisition_shapes: dict[str, tuple[int, ...]] = {}
    params: SequencerParams = SequencerParams()
    params_only: bool = False

    def sequence_data(self) -> dict[str, Any] | None:
        if self.params_only:
            return None
        return self.model_dump(include={"program", "waveforms", "weights", "acquisitions"})

    def dumps(self) -> str:
        return self.model_dump_json()

    @classmethod
    def loads(cls, data: str) -> Self:
        return cls.model_validate_json(data)


class PreparedSequenceProgram(BaseModel):  # pragma: no cover
    """A sequence program that is mapped to a specific module & sequencer."""

    sequence_program: SequenceProgram
    sequencer_number: int
    ch_out: ChannelType
    ch_in: ChannelType | None = None

    @property
    def sequencer_addr(self) -> SequencerAddr:
        mod_addr = self.ch_out.module
        return SequencerAddr(
            cluster=mod_addr.cluster,
            slot=mod_addr.slot,
            number=self.sequencer_number,
        )


class PreparedModule(BaseModel):
    params: ModuleParams


class PreparedProgram(BaseModel):
    """A program representing a multi-element circuit."""

    modules: dict[ModuleAddrType, PreparedModule]  # The set of modules this program will target.
    sequence_programs: dict[str, PreparedSequenceProgram]  # The individual element programs.

    @property
    def sequencers(self) -> dict[SequencerAddr, str]:
        return {psp.sequencer_addr: name for name, psp in self.sequence_programs.items()}

    def get_sequencer_program(self, seq_addr: SequencerAddr) -> SequenceProgram:
        prog_name = self.sequencers[seq_addr]
        return self.sequence_programs[prog_name].sequence_program

    def dumps(self) -> str:
        return self.model_dump_json()

    @classmethod
    def loads(cls, data: str) -> Self:
        return cls.model_validate_json(data)


# ==================================================================================================
# Results
# ==================================================================================================
MAX_ACQUISITION_BINS = 131072


class OutputScopedAcquisitionData(BaseModel):  # pragma: no cover
    """
    Scoped acquisition data for a single path in `OutputScopedAcquisition`.

    This schema is defined by QBLOX.
    """

    data: list[float]
    out_of_range: bool = Field(validation_alias="out-of-range")
    avg_cnt: int


class OutputScopedAcquisition(BaseModel):  # pragma: no cover
    """
    Scoped acquisition data for a single acquisition index in the SequenceProgram.

    This schema is defined by QBLOX.
    """

    path0: OutputScopedAcquisitionData
    path1: OutputScopedAcquisitionData


class OutputBinnedAcquisitionIntegrationData(BaseModel):  # pragma: no cover
    """
    Binned values in `OutputBinnedAcquisition`.

    This schema is defined by QBLOX.
    """

    path0: list[float]
    path1: list[float]


class OutputBinnedAcquisition(BaseModel):  # pragma: no cover
    """
    Binned acquisition data for a single acquisition index in the SequenceProgram.

    This schema is defined by QBLOX.
    """

    integration: OutputBinnedAcquisitionIntegrationData
    threshold: list[float]
    avg_cnt: list[int]


class OutputAcquisition(BaseModel):  # pragma: no cover
    """
    Acquisition data for a single acquisition index in the SequenceProgram.

    Note, this type is wrapped by `OutputIndexedAcquisition`.

    This schema is defined by QBLOX.
    """

    scope: OutputScopedAcquisition
    bins: OutputBinnedAcquisition


class OutputIndexedAcquisition(BaseModel):  # pragma: no cover
    """
    Acquisition data (wrapper) for a single acquisition index in the SequenceProgram.

    This type simply wraps `OutputAcquisition` with an additional `index` attribute. The index in
    `SequenceProgram.acquisitions[...].index` will correspond to `OutputIndexedAcquisition.index`.

    Note, this type is used as the values in the `OutputSequencerAcquisitions` dict-type; the keys
    will correspond to the acquisition name.

    This schema is defined by QBLOX.
    """

    index: int
    acquisition: OutputAcquisition


# Results returned by a single sequencer.
# This schema is defined by QBLOX.
# Example result in JSON (redacted for brevity):
#
# // {
# //    'weighted': {
# //        'index': 0
# //        'acquisition': {
# //            'scope': {
# //                'path0': {
# //                    'out_of_range': False,
# //                    'avg_cnt': 0,
# //                    'data': [...]
# //                },
# //                'path1': {
# //                    'out_of_range': False,
# //                    'avg_cnt': 0,
# //                    'data': [...]
# //                }
# //            },
# //            'bins': {
# //                'integration': {
# //                    'path0': [10.0],
# //                    'path1': [10.0],
# //                },
# //                'threshold': [1.0],
# //                'avg_cnt': [1],
# //            }
# //        }
# //    }
# // }
#
# This results must come from a SequenceProgram that defines
#
# // acquisitions = {
# //    {'weighed': {'num_bins': 1, 'index': 0}}
# // }
OutputSequencerAcquisitions = dict[str, OutputIndexedAcquisition]  # pragma: no cover


@dataclass
class SequencerResults:
    """
    Sequencer results formatted as a complex signal.

    The real component corresponds to results on path0, whilst the imaginary component corresponds
    to the results on path1.
    """

    scopes: dict[str, np.ndarray]
    bins: dict[str, np.ndarray]


def process_sequencer_output(
    program: SequenceProgram,
    output: OutputSequencerAcquisitions,
) -> SequencerResults:
    """
    Process the output from executing a sequencer into a simplified SequencerResults data structure.

    Parameters
    ----------
    program: SequenceProgram
        The corresponding program that was executed
    output: OutputSequencerAcquisitions
        The results of one sequencer's execution

    Returns
    -------
    SequencerResults
    """
    bins = {}
    scopes = {}
    for acq_ref, acq_result in output.items():
        acquisition = acq_result.acquisition

        raw_bin = acquisition.bins.integration
        shape = program.acquisition_shapes.get(acq_ref)
        if shape is None or len(shape) == 1:
            bins[acq_ref] = np.array(raw_bin.path0) + 1j * np.array(raw_bin.path1)
        else:
            bse = BitStrideArrayEncoding.from_desired(shape)
            bins[acq_ref] = bse.decode(raw_bin.path0) + 1j * bse.decode(raw_bin.path1)

        raw_scope = acquisition.scope
        if acq_ref in program.acquisition_scopes:
            scopes[acq_ref] = np.array(raw_scope.path0.data) + 1j * np.array(raw_scope.path1.data)

    return SequencerResults(scopes=scopes, bins=bins)


@dataclass
class BitStrideArrayEncoding:
    """
    Encode a multi-dimensional array such that each dimensional index occupies an integer number of
    bits (the bit-stride).

    In this encoding, a linear index is calculated by left-shifting each element in the index by its
    corresponding bit-stride:

        linear_index = Σ (ii << bb) ∀ (ii, bb) ∈ zip(index, bit_strides)

    Examples
    --------
    Given a desired_shape of (3, 5), the first index will have a bit-stride of 2 and the second
    index will have a bit-stride of 3. To determine the linear index for a sample, we will use:

        def linear_index(idx0: int, idx1: int) -> int:
            return (idx0 << 2) + (idx1 << 3)

    Note, the encoded data will occupy 2^2 * 2^3 samples and have (2^2 * 2^3 - 3 * 5) unused data
    points.

    >>> bse = BitStrideArrayEncoding.from_desired((3, 5))
    >>> bse.encoded_shape
    (4, 8)
    >>> bse.bit_stride
    (2, 3)
    """

    desired_shape: tuple[int, ...]
    encoded_shape: tuple[int, ...]
    bit_stride: tuple[int, ...]

    @staticmethod
    def _round_power2_32bit(val: int) -> int:
        val -= 1
        val |= val >> 1
        val |= val >> 2
        val |= val >> 4
        val |= val >> 8
        val |= val >> 16
        val += 1
        return val

    @classmethod
    def from_desired(cls, desired_shape: tuple[int, ...]) -> Self:
        encoded_shape = tuple(
            BitStrideArrayEncoding._round_power2_32bit(dim) for dim in desired_shape
        )
        # Right-most (most nested) dimension takes least significant bits!
        exponents = tuple(int(math.log2(dim)) for dim in encoded_shape)
        n_bits = sum(exponents)
        bit_stride = tuple(n_bits - sum(exponents[: idx + 1]) for idx in range(len(exponents)))
        return cls(
            desired_shape=desired_shape,
            encoded_shape=encoded_shape,
            bit_stride=bit_stride,
        )

    def decode(self, values: list[float]) -> np.ndarray:
        decoded = np.reshape(values, self.encoded_shape)
        return decoded[tuple(slice(0, dim) for dim in self.desired_shape)]


# ==================================================================================================
# Utilities
# ==================================================================================================
@dataclasses.dataclass
class ModuleConstraints:
    """Physical constraints of a module."""

    n_sequencers: int
    n_markers: int = 0
    n_ch_out: int = 0
    n_ch_in: int = 0
    n_digital_io: int = 0

    # TODO: Confirm if ordering is important.
    ch_out_iq_pairs: list[set[int]] = dataclasses.field(default_factory=list)
    ch_in_iq_pairs: list[set[int]] = dataclasses.field(default_factory=list)


# Default module constraints by module type.
DEFAULT_MODULE_CONSTRAINTS: dict[ModuleType, ModuleConstraints] = {
    ModuleType.QCM: ModuleConstraints(
        n_sequencers=6,
        n_markers=4,
        n_ch_out=4,
        n_ch_in=0,
        ch_out_iq_pairs=[{0, 1}, {2, 3}],
    ),
    ModuleType.QCM_RF: ModuleConstraints(
        n_sequencers=6,
        n_markers=2,
        n_ch_out=2,
        n_ch_in=0,
    ),
    ModuleType.QRM: ModuleConstraints(
        n_sequencers=6,
        n_markers=4,
        n_ch_out=2,
        n_ch_in=2,
        ch_out_iq_pairs=[{0, 1}],
        ch_in_iq_pairs=[{2, 3}],
    ),
    ModuleType.QRM_RF: ModuleConstraints(
        n_sequencers=6,
        n_markers=2,
        n_ch_out=1,
        n_ch_in=1,
    ),
    ModuleType.QRC: ModuleConstraints(
        n_sequencers=12,
        n_ch_out=6,
        n_ch_in=2,
    ),
    ModuleType.QTM: ModuleConstraints(
        n_sequencers=8,
        n_digital_io=8,
    ),
    ModuleType.QDM: ModuleConstraints(n_sequencers=0),
    ModuleType.EOM: ModuleConstraints(n_sequencers=0),
    ModuleType.LINQ: ModuleConstraints(n_sequencers=0),
}


def validate_channel(ch: ChannelType, constraint: ModuleConstraints) -> list[str]:
    """Validates a channel against a module constraint.

    Parameters
    ----------
    ch: ChannelType
        The channel to validate
    constraint: ModuleConstraints
        The module's physical constraints

    Returns
    -------
    list[str]
        A list of issue descriptions

    Notes
    -----
    Possible issues reported:

    - "module has no <input/output> ports."
    - "<input/output> port number # out-of-bounds for module, must be between [#, #)."
    - "module does not support complex <input/output> channels."
    - "invalid <input/output> IQ pair {#, #}, module only supports pairs [{#, #}, ...]."
    """
    # TODO: Consider simplifying these separate input/output private validators into a single func
    #       since they share the same overall logic, and simply require different error messaging
    #       and attribute access...
    if ch.direction == "out":
        return _validate_output_channel(ch, constraint)
    return _validate_input_channel(ch, constraint)


def _validate_output_channel(ch_out: ChannelType, constraint: ModuleConstraints) -> list[str]:
    issues = []
    if isinstance(ch_out, RealChannel):
        po_out = ch_out.port
        if constraint.n_ch_out == 0:
            issues.append("module has no output ports.")
        elif po_out.number < 0 or po_out.number >= constraint.n_ch_out:
            issues.append(
                f"output port number {po_out.number} out-of-bounds for module, "
                f"must be between [0, {constraint.n_ch_out}).",
            )
    else:
        valid_pairs = constraint.ch_out_iq_pairs
        if not valid_pairs:
            issues.append("module does not support complex output channels.")
        else:
            po_out_i = ch_out.i_port
            po_out_q = ch_out.q_port
            if {po_out_i.number, po_out_q.number} not in valid_pairs:
                issues.append(
                    f"invalid output IQ pair {{{po_out_i.number}, {po_out_q.number}}}, module only "
                    f"supports pairs {valid_pairs}.",
                )
    return issues


def _validate_input_channel(ch_in: ChannelType, constraint: ModuleConstraints) -> list[str]:
    issues = []
    if isinstance(ch_in, RealChannel):
        po_in = ch_in.port
        if constraint.n_ch_in == 0:
            issues.append("module has no input ports.")
        elif po_in.number < 0 or po_in.number >= constraint.n_ch_in:
            issues.append(
                f"input port number {po_in.number} out-of-bounds for module, "
                f"must be between [0, {constraint.n_ch_in}).",
            )
    else:
        valid_pairs = constraint.ch_in_iq_pairs
        if not valid_pairs:
            issues.append("module does not support complex input channels.")
        else:
            po_in_i = ch_in.i_port
            po_in_q = ch_in.q_port
            if {po_in_i.number, po_in_q.number} not in valid_pairs:
                issues.append(
                    f"invalid input IQ pair {{{po_in_i.number}, {po_in_q.number}}}, module only "
                    f"supports pairs {valid_pairs}.",
                )
    return issues
