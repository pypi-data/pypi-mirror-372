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

# pyright: reportPrivateImportUsage=false
"""qm-qua imports.

This module standardizes all the qm-qua imports across the various versions we will
support.
"""

__all__ = [
    "Constants",
    "QuaExpression",
    "QuaProgram",
    "QuaProgramMessage",
    "version",
]


import importlib.metadata
import logging
import os
from unittest.mock import patch

from packaging.version import Version

if os.environ.get("QCTRL_SU_DISABLE_QM_LOGGING", "False") == "True":
    # Disable QM logging and telemetry
    os.environ["QM_DISABLE_STREAMOUTPUT"] = "true"  # Used in 1.1.0
    _qm_logger = logging.getLogger("qm")
    _qm_logger.disabled = True

# Disable unwanted telemetry/logging modules in QM
_qm_patch_targets = [
    "qm._loc._get_loc",
    "qm.program.expressions._get_loc",
    "qm.program.StatementsCollection._get_loc",
    "qm.qua._get_loc",
    "qm.qua._dsl._get_loc",
    "qm.qua._expressions._get_loc",
    "qm.qua.AnalogMeasureProcess._get_loc",
    "qm.qua.DigitalMeasureProcess._get_loc",
    "qm.datadog_api.DatadogHandler",
]
for target in _qm_patch_targets:
    try:
        _m = patch(target).__enter__()
        _m.return_value = ""
    except (AttributeError, ModuleNotFoundError):
        pass


from qm.grpc.qua import QuaProgram as QuaProgramMessage  # noqa: E402

version = Version(importlib.metadata.version("qm-qua"))
if version >= Version("1.2.0"):
    from qm.api.models.capabilities import OPX_FEM_IDX
    from qm.program import Program as QuaProgram
    from qm.qua._expressions import QuaExpression
else:
    from qm.qua import Program as QuaProgram  # type: ignore[attr-defined,no-redef]
    from qm.qua._dsl import (  # type: ignore[attr-defined,no-redef]
        _Expression as QuaExpression,  # pyright: ignore[reportAttributeAccessIssue]
    )

    OPX_FEM_IDX = None  # type: ignore[assignment]


class Constants:
    """QM-Qua constants."""

    opx_fem_idx: int | None = OPX_FEM_IDX
    """The default FEM port for OPX. Only available for >=1.2.0"""
