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

from pydantic import PrivateAttr, field_validator

from .common import CWSIterable, Experiment


class DragLeakageCalibration(Experiment):
    """
    Parameters for running a DRAG leakage calibration experiment for
    a specified gate on a transmon.

    Attributes
    ----------
    transmon : str
        The reference for the transmon to target.
    recycle_delay_ns : int
        The delay between consecutive shots, in nanoseconds. Defaults to 10,000 ns.
    shot_count : int, optional
        The number of shots to take. Defaults to 1,000.
    alphas: list[float] or CWSIterable
        List of values to sweep for DRAG parameter alpha.
    repetitions : list[int]
        List of repetition counts for the calibration experiment.
    gate : "sx" or "x"
        The gate to calibrate.
    anharmonicity : float or None, optional
        The anharmonicity of the transmon, in Hz.
        Defaults to None, in which case the anharmonicity of the transmon will be used.
    drag_guess : float
        Initial guess for the DRAG parameter.
    update : "auto" or "off" or "prompt", optional
        How the device should be updated after an experiment run. Defaults to auto.
    """

    _experiment_name: str = PrivateAttr("drag_leakage_calibration")

    transmon: str
    recycle_delay_ns: int = 10_000
    shot_count: int = 1_000
    alphas: list[float] | CWSIterable
    repetitions: list[int]
    gate: Literal["x", "sx"]
    anharmonicity: float | None = None
    drag_guess: float
    update: Literal["auto", "off", "prompt"] = "auto"

    @field_validator("alphas")
    @classmethod
    def validate_alphas(cls, value: list[float] | CWSIterable):
        if isinstance(value, CWSIterable) and value.center is None:
            raise TypeError("The center of alphas must not be None.")
        return value
