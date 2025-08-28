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


from pydantic import BaseModel
from pydantic.dataclasses import dataclass

from boulderopalscaleupsdk.common.dtypes import ISO8601DatetimeUTCLike
from boulderopalscaleupsdk.device.controller import (
    QBLOXControllerInfo,
    QuantumMachinesControllerInfo,
)
from boulderopalscaleupsdk.device.defcal import DefCalData
from boulderopalscaleupsdk.device.processor import SuperconductingProcessor


@dataclass
class EmptyDefCalData:
    message: str


DeviceName = str


@dataclass
class DeviceData:
    # TODO: retire DeviceInfo the next SDK release
    qpu: SuperconductingProcessor  # | OtherSDKProcessorType
    controller_info: QBLOXControllerInfo | QuantumMachinesControllerInfo
    _defcals: dict[tuple[str, tuple[str, ...]], DefCalData]

    def get_defcal(self, gate: str, addr: tuple[str, ...]) -> DefCalData | EmptyDefCalData:
        """
        Get the defcal data for a specific gate and address alias.
        """
        if self._defcals == {}:
            return EmptyDefCalData(message="No defcal data available in a fresh device.")
        _addr = tuple(i.lower() for i in sorted(addr))
        defcal = self._defcals.get((gate, _addr))
        if defcal is None:
            return EmptyDefCalData(
                message=f"No defcal data found for gate '{gate}' and address '{_addr}'.",
            )
        return defcal


class DeviceSummary(BaseModel):
    id: str
    organization_id: str
    name: str
    provider: str
    updated_at: ISO8601DatetimeUTCLike
    created_at: ISO8601DatetimeUTCLike
    copied_from: DeviceName | None = None

    def __str__(self):
        return f'DeviceSummary(name="{self.name}", id="{self.id}")'
