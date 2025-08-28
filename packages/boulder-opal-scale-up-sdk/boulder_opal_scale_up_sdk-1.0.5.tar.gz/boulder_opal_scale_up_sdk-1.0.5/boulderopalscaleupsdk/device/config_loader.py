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

from enum import Enum
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel

from boulderopalscaleupsdk.device.controller import (
    ControllerInfoTypeAdapter,
    QBLOXControllerInfo,
    QuantumMachinesControllerInfo,
)
from boulderopalscaleupsdk.device.processor import (
    SuperconductingProcessor,
    SuperconductingProcessorTemplate,
)
from boulderopalscaleupsdk.utils.serial_utils import sanitize_keys


class ProcessorArchitecture(str, Enum):
    Superconducting = "superconducting"


# TODO: Remove this in the next release of SDK
class DeviceInfo(BaseModel):
    controller_info: QBLOXControllerInfo | QuantumMachinesControllerInfo
    processor: SuperconductingProcessor  # | OtherSDKProcessorType

    def to_dict(self) -> dict[str, Any]:
        return sanitize_keys(self.model_dump(by_alias=True, mode="json"))


class DeviceConfigLoader:
    def __init__(self, config_path: Path):
        self.config_path = config_path

    def load(self) -> dict[str, Any]:
        device_config_data = self._load_yaml_file(self.config_path)

        layout_file = device_config_data.pop("layout_file", None)
        if layout_file is None:
            raise ValueError("Layout file is missing from device configuration data.")

        layout_path = Path(layout_file)
        if not layout_path.is_absolute():
            self._validate_file_is_filename(layout_path.name)
            layout_path = self.config_path.parent / layout_file

        device_layout_data = self._load_yaml_file(layout_path)

        processed_device_config = {**device_config_data, **device_layout_data}
        return sanitize_keys(processed_device_config)

    def load_device_info(self) -> DeviceInfo:
        device_config_dict = self.load()
        match device_config_dict["device_arch"]:
            case "superconducting":
                superconducting_template = SuperconductingProcessorTemplate.model_validate(
                    device_config_dict,
                )
                device_info = DeviceInfo(
                    controller_info=ControllerInfoTypeAdapter.validate_python(
                        device_config_dict["controller_info"],
                    ),
                    processor=SuperconductingProcessor.from_template(superconducting_template),
                )
            case other:
                raise ValueError(f"Invalid or unsupported architecture {other}.")
        return device_info

    @staticmethod
    def _load_yaml_file(yaml_file_path: Path) -> dict[str, Any]:
        with yaml_file_path.open("rb") as fd:
            return yaml.safe_load(fd)

    @staticmethod
    def _validate_file_is_filename(file_name: str) -> None:
        if "/" in file_name or "\\" in file_name:
            raise ValueError(
                f"'{file_name}' must be a file name, not a path.",
            )
