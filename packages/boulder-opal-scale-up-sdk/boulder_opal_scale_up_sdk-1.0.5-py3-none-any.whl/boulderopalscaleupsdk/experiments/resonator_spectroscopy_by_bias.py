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

DEFAULT_BIASES = LinspaceIterable(start=-0.49, stop=0.49, count=21)


class ResonatorSpectroscopyByBias(Experiment):
    """
    Parameters for running a resonator spectroscopy by power experiment.

    Attributes
    ----------
    resonator : str
        The reference for the resonator to target.
    bias_transmons : list[str] or None, optional
        The references for the transmons to bias.
        Defaults to transmon coupled to the resonator.
    frequencies : list[int] or LinspaceIterable or RangeIterable or CWSIterable \
                  or HypIterable or None, optional
        The frequencies at which to scan, in Hz.
        Defaults to a scan around the readout frequency.
    biases : list[int] or LinspaceIterable or RangeIterable or CWSIterable \
             or HypIterable, optional
        The biases at which to scan, in Volts.
        Defaults to 21 points between -0.49 and 0.49.
    recycle_delay_ns : int, optional
        The delay between consecutive shots, in nanoseconds. Defaults to 1,000 ns.
    shot_count : int, optional
        The number of shots to take. Defaults to 100.
    measure_waveform : ConstantWaveform or None, optional
        The waveform to use for the measurement pulse.
        Defaults to the measurement defcal.
    run_mixer_calibration: bool
        Whether to run mixer calibrations before running a program. Defaults to False.
    update : "auto" or "off" or "prompt", optional
        How the device should be updated after an experiment run. Defaults to auto.
    """

    _experiment_name: str = PrivateAttr("resonator_spectroscopy_by_bias")

    resonator: str
    bias_transmons: list[str] | None = None
    frequencies: list[int] | LinspaceIterable | RangeIterable | CWSIterable | HypIterable | None = (
        None
    )
    biases: list[float] | LinspaceIterable | RangeIterable | CWSIterable | HypIterable = (
        DEFAULT_BIASES
    )
    recycle_delay_ns: int = 1_000
    shot_count: int = 100
    measure_waveform: ConstantWaveform | None = None
    run_mixer_calibration: bool = False
    update: Literal["auto", "off", "prompt"] = "auto"
