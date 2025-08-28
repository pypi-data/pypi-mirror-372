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

from .common import Routine


class TransmonCoherence(Routine):
    """
    Parameters for running a transmon coherence routine.

    Attributes
    ----------
    transmon : str
        The reference for the transmon to target.
    run_mixer_calibration : bool, optional
        Whether to run mixer calibrations before running each program. Defaults to False.
    """

    _routine_name: str = PrivateAttr("transmon_coherence")

    transmon: str
    run_mixer_calibration: bool = False
