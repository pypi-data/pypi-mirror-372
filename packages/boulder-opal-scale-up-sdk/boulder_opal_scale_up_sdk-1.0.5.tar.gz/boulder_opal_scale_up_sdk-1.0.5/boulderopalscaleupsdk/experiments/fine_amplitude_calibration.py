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

from typing import Literal

from pydantic import Field, PrivateAttr

from .common import Experiment
from .waveforms import ConstantWaveform


class FineAmplitudeCalibration(Experiment):
    """
    Parameters for running a fine amplitude calibration experiment for
    a specified gate on a transmon.

    Attributes
    ----------
    transmon : str
        The reference for the transmon to target.
    gate : Literal["sx", "x"]
        The gate to be calibrated.
    repetitions : list[int]
        List of repetition counts for the calibration experiment.
    recycle_delay_ns : int
        The delay between consecutive shots, in nanoseconds. Defaults to 10,000 ns.
    shot_count : int, optional
        The number of shots to take. Defaults to 1000.
    measure_waveform : ConstantWaveform or None, optional
        The waveform to use for the measurement pulse.
        Defaults to the measurement defcal.
    update : "auto" or "off" or "prompt", optional
        How the device should be updated after an experiment run. Defaults to auto.
    """

    _experiment_name: str = PrivateAttr("fine_amplitude_calibration")

    transmon: str
    gate: Literal["sx", "x"]
    repetitions: list[int] = Field(default=list(range(0, 100, 4)))
    recycle_delay_ns: int = 10_000
    shot_count: int = 1000
    measure_waveform: ConstantWaveform | None = None
    update: Literal["auto", "off", "prompt"] = "auto"
