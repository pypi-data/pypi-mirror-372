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

from .common import (
    CWSIterable,
    Experiment,
    HypIterable,
    LinspaceIterable,
    RangeIterable,
)
from .waveforms import ConstantWaveform, Waveform


class PowerRabi(Experiment):
    """
    Parameters for running a Power Rabi experiment.

    Attributes
    ----------
    transmon : str
        The reference for the transmon to target.
    scales : list[float] or LinspaceIterable or RangeIterable \
            or CWSIterable or HypIterable or None, optional
        The scaling factors for the drive pulse amplitude.
        If None, a default scan will be used.
    drive_waveform : Waveform
        The waveform to use for the drive pulse.
    recycle_delay_ns : int
        The delay between consecutive shots, in nanoseconds. Defaults to 200,000 ns.
    shot_count : int, optional
        The number of shots to take. Defaults to 400.
    pulse_vp : float, optional
        The voltage per pulse, in Volts. Defaults to the amplitude of the X gate.
    measure_waveform : ConstantWaveform or None, optional
        The waveform to use for the measurement pulse.
        Defaults to the measurement defcal.
    run_mixer_calibration: bool
        Whether to run mixer calibrations before running a program. Defaults to False.
    update : "auto" or "off" or "prompt", optional
        How the device should be updated after an experiment run. Defaults to auto.
    """

    _experiment_name: str = PrivateAttr("power_rabi")

    transmon: str
    scales: list[float] | LinspaceIterable | RangeIterable | CWSIterable | HypIterable | None = None
    drive_waveform: Waveform
    recycle_delay_ns: int = 200_000
    shot_count: int = 400
    pulse_vp: float | None = None
    measure_waveform: ConstantWaveform | None = None
    run_mixer_calibration: bool = False
    update: Literal["auto", "off", "prompt"] = "auto"
