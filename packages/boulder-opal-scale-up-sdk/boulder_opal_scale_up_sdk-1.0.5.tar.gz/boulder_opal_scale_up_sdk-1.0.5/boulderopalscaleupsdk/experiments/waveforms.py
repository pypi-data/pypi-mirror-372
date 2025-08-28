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

from dataclasses import replace
from typing import Annotated, Literal, Protocol, TypeVar

from pydantic import Discriminator
from pydantic.dataclasses import dataclass


class _Waveform(Protocol):  # pragma: no cover
    duration_ns: int
    amplitude: float


@dataclass
class ConstantWaveform(_Waveform):  # pragma: no cover
    duration_ns: int
    amplitude: float
    waveform_type: Literal["Constant"] = "Constant"


@dataclass
class GaussianWaveform(_Waveform):  # pragma: no cover
    duration_ns: int
    amplitude: float
    sigma: float
    waveform_type: Literal["Gaussian"] = "Gaussian"


@dataclass
class DragCosineWaveform(_Waveform):  # pragma: no cover
    duration_ns: int
    amplitude: float
    drag: float
    buffer_ns: int
    center: float
    waveform_type: Literal["DragCosineWaveform"] = "DragCosineWaveform"


Waveform = Annotated[
    ConstantWaveform | GaussianWaveform | DragCosineWaveform,
    Discriminator("waveform_type"),
]

T = TypeVar("T", bound=Waveform)


def update_amplitude(waveform: T, amplitude: float) -> T:
    """
    Update the amplitude of a waveform.
    """
    return replace(waveform, amplitude=amplitude)
