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

__all__ = [
    "ControllerType",
    "QBLOXControllerInfo",
    "QuantumMachinesControllerInfo",
]

from typing import TypeVar

from pydantic import TypeAdapter

from .base import ControllerType
from .qblox import QBLOXControllerInfo
from .quantum_machines import QuantumMachinesControllerInfo

ControllerInfoType = TypeVar(
    "ControllerInfoType",
    bound=QBLOXControllerInfo | QuantumMachinesControllerInfo,
)

ControllerInfoTypeAdapter: TypeAdapter[QBLOXControllerInfo | QuantumMachinesControllerInfo] = (
    TypeAdapter(QBLOXControllerInfo | QuantumMachinesControllerInfo)
)
