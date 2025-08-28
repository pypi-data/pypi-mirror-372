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

from pydantic import PrivateAttr

from .common import Experiment
from .waveforms import ConstantWaveform


class Ramsey(Experiment):
    """
    Parameters for running a Ramsey experiment.

    Attributes
    ----------
    transmon : str
        The reference for the transmon to target.
    min_delay_ns : int
        The minimum delay time, in nanoseconds.
    max_delay_ns : int
        The maximum delay time, in nanoseconds.
    delay_step_ns : int
        The step for generating the list of delays, in nanoseconds.
    virtual_detuning : float
        The virtual detuning added between SX pulses, in Hz.
    recycle_delay_ns : int, optional
        The delay between consecutive shots, in nanoseconds. Defaults to 200,000 ns.
    shot_count : int, optional
        The number of shots to take. Defaults to 400.
    measure_waveform : ConstantWaveform or None, optional
        The waveform to use for the measurement pulse.
        Defaults to the measurement defcal.
    run_mixer_calibration: bool
        Whether to run mixer calibrations before running a program. Defaults to False.
    update : "auto" or "off" or "prompt", optional
        How the device should be updated after an experiment run. Defaults to auto.
    """

    _experiment_name: str = PrivateAttr("ramsey")

    transmon: str
    min_delay_ns: int
    max_delay_ns: int
    delay_step_ns: int
    virtual_detuning: float
    recycle_delay_ns: int = 200_000
    shot_count: int = 400
    measure_waveform: ConstantWaveform | None = None
    run_mixer_calibration: bool = False
    update: Literal["auto", "off", "prompt"] = "auto"
