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


class ResonatorSpectroscopyByPower(Experiment):
    """
    Parameters for running a resonator spectroscopy by power experiment.

    Attributes
    ----------
    resonator : str
        The reference for the resonator to target.
    frequencies : list[int] or LinspaceIterable or RangeIterable or CWSIterable \
                  or HypIterable or None, optional
        The frequencies at which to scan, in Hz.
        Defaults to a scan around the readout frequency.
    powers_dbm : list[float] or None, optional
        The powers at which to scan the readout pulse, in dBm.
        If None, a default power scan will be used.
    duration_ns : int, optional
        The duration of the readout pulse, in nanoseconds. Defaults to 2,000 ns.
    recycle_delay_ns : int, optional
        The delay between consecutive shots, in nanoseconds. Defaults to 1,000 ns.
    shot_count : int, optional
        The number of shots to take. Defaults to 100.
    run_mixer_calibration: bool
        Whether to run mixer calibrations before running a program. Defaults to False.
    update : "auto" or "off" or "prompt", optional
        How the device should be updated after an experiment run. Defaults to auto.
    """

    _experiment_name: str = PrivateAttr("resonator_spectroscopy_by_power")

    resonator: str
    frequencies: list[int] | LinspaceIterable | RangeIterable | CWSIterable | HypIterable | None = (
        None
    )
    powers_dbm: list[float] | None = None
    duration_ns: int = 2_000
    recycle_delay_ns: int = 1_000
    shot_count: int = 100
    run_mixer_calibration: bool = False
    update: Literal["auto", "off", "prompt"] = "auto"
