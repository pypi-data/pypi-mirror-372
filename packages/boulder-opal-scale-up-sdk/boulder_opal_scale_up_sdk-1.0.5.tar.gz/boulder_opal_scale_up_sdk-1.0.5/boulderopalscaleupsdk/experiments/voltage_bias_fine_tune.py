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

from .common import Experiment, RangeIterable


class VoltageBiasFineTune(Experiment):
    """
    Parameters for running voltage bias fine-tune experiment.

    Attributes
    ----------
    transmon : str
        The reference for the transmon to XY drive in the experiment.
    delays_ns : list[int] or RangeIterable
        The delay times, in nanoseconds.
    flux_count : int
        Number of flux bias points to sample around the current bias offset.
    flux_delta : float
        Flux difference between flux points, in units of the voltage period.
    virtual_detuning : float
        The difference between the drive signal frequency and the qubit frequency, in Hz.
    bias_transmon : str or None, optional
        The reference for the transmon to flux tune in the experiment.
        Defaults to transmon.
    recycle_delay_ns : int, optional
        The delay time between consecutive shots of the experiment, in nanoseconds.
        Defaults to 100_000 ns.
    shot_count : int, optional
        The number of shots to be taken in the experiment.
        Defaults to 400.
    """

    _experiment_name: str = PrivateAttr("voltage_bias_fine_tune")

    transmon: str
    delays_ns: list[int] | RangeIterable
    flux_count: int
    flux_delta: float
    virtual_detuning: float
    bias_transmon: str | None = None
    recycle_delay_ns: int = 100_000
    shot_count: int = 400
    update: Literal["auto", "off", "prompt"] = "auto"
