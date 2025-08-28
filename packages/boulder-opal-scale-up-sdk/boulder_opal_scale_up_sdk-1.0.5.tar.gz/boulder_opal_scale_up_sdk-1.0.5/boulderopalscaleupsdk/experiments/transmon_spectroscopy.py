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
from .waveforms import ConstantWaveform


class TransmonSpectroscopy(Experiment):
    """
    Parameters for running a transmon spectroscopy experiment.

    Attributes
    ----------
    transmon : str
        The reference for the transmon to target.
    frequencies : list[int] or LinspaceIterable or RangeIterable or CWSIterable \
                  or HypIterable or None, optional
        The frequencies at which to scan, in Hz.
        Default to a scan around the transmon frequency.
    recycle_delay_ns : int, optional
        The delay between consecutive shots, in nanoseconds. Defaults to 50,000 ns.
    shot_count : int, optional
        The number of shots to take. Defaults to 100.
    spectroscopy_waveform : ConstantWaveform
        The waveform to use in the spectroscopy pulse.
    measure_waveform : ConstantWaveform or None, optional
        The waveform to use for the measurement pulse.
        Defaults to the measurement defcal.
    run_mixer_calibration: bool
        Whether to run mixer calibrations before running a program. Defaults to False.
    update : "auto" or "off" or "prompt", optional
        How the device should be updated after an experiment run. Defaults to auto.
    """

    _experiment_name: str = PrivateAttr("transmon_spectroscopy")

    transmon: str
    frequencies: list[int] | LinspaceIterable | RangeIterable | CWSIterable | HypIterable | None = (
        None
    )
    recycle_delay_ns: int = 50_000
    shot_count: int = 400
    spectroscopy_waveform: ConstantWaveform
    measure_waveform: ConstantWaveform | None = None
    run_mixer_calibration: bool = False
    update: Literal["auto", "off", "prompt"] = "auto"
