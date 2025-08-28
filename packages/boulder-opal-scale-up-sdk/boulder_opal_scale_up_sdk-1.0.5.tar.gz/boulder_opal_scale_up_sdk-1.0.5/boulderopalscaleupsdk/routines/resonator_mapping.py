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

from pydantic import PrivateAttr

from boulderopalscaleupsdk.routines import Routine


class ResonatorMapping(Routine):
    """
    Parameters for running a resonator mapping routine.

    Attributes
    ----------
    feedlines : list[str] or None
        The feedlines to target in the routine.
        If not provided, all feedlines in the device will be targeted.
    run_mixer_calibration: bool
        Whether to run mixer calibrations before running each program. Defaults to True.
    """

    _routine_name: str = PrivateAttr("resonator_mapping")

    feedlines: list[str] | None = None
    run_mixer_calibration: bool = True
