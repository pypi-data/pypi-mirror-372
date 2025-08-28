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

DEFAULT_RECYCLE_DELAY_NS = 1_000  # ns


class TransmonAnharmonicity(Experiment):
    """
    Parameters for running a transmon anharmonicity experiment.

    Attributes
    ----------
    transmon : str
        The reference for the transmon to target.
    frequencies : list[int] or LinspaceIterable or RangeIterable or CWSIterable \
                  or HypIterable or None, optional
        The frequencies at which to scan, in Hz.
        Defaults to a scan based on the transmon's frequency and anharmonicity.
    anharmonicity : float, optional
        The guessed anharmonicity of the transmon, in Hz.
        Used to determine the scan frequencies if not provided. Defaults to -200 MHz.
    recycle_delay_ns : int, optional
        The delay between consecutive shots, in nanoseconds. Defaults to 10,000 ns.
    shot_count : int, optional
        The number of shots to take. Defaults to 400.
    spectroscopy_waveform : ConstantWaveform or None, optional
        The waveform to use in the spectroscopy pulse.
        Defaults to a constant waveform with a duration of 2,000 ns
        and an amplitude of 1.5 times the transmon's x_vp.
    measure_waveform : ConstantWaveform or None, optional
        The waveform to use for the measurement pulse.
        Defaults to the measurement defcal.
    run_mixer_calibration: bool
        Whether to run mixer calibrations before running a program. Defaults to False.
    update : "auto" or "off" or "prompt", optional
        How the device should be updated after an experiment run. Defaults to auto.
    """

    _experiment_name: str = PrivateAttr("transmon_anharmonicity")

    transmon: str
    frequencies: list[int] | LinspaceIterable | RangeIterable | CWSIterable | HypIterable | None = (
        None
    )
    anharmonicity: float = -200e6
    recycle_delay_ns: int = 10_000
    shot_count: int = 400
    spectroscopy_waveform: ConstantWaveform | None = None
    measure_waveform: ConstantWaveform | None = None
    run_mixer_calibration: bool = False
    update: Literal["auto", "off", "prompt"] = "auto"
