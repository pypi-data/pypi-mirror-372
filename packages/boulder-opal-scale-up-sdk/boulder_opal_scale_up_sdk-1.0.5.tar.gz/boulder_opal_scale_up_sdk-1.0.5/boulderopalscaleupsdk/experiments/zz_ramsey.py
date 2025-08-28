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


class ZZRamsey(Experiment):
    """
    Parameters for running a ZZ Ramsey experiment.

    Attributes
    ----------
    control_transmon : str
        The control transmon to target in the experiment.
    target_transmon : str
        The target transmon to pair with the control transmon.
    max_delay_ns : int
        The maximum delay time, in nanoseconds.
    min_delay_ns : int
        The minimum delay time, in nanoseconds.
    delay_step_ns : int
        The step for generating the list of delays, in nanoseconds.
    virtual_detuning : float
        The difference between the drive signal frequency and the qubit frequency, in Hz.
    recycle_delay_ns : int, optional
        The delay time between consecutive shots of the experiment, in nanoseconds.
        Defaults to 10,000 ns.
    shot_count : int, optional
        The number of shots to be taken in the experiment.
        Defaults to 400.
    update : "auto" or "off" or "prompt", optional
        How the device should be updated after an experiment run. Defaults to auto.
    """

    _experiment_name: str = PrivateAttr("zz_ramsey")

    control_transmon: str
    target_transmon: str
    max_delay_ns: int
    min_delay_ns: int
    delay_step_ns: int
    virtual_detuning: float
    recycle_delay_ns: int = 10_000
    shot_count: int = 400
    update: Literal["auto", "off", "prompt"] = "auto"
