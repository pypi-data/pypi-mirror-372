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

from pathlib import Path
from typing import Any

from pydantic import TypeAdapter
from pydantic.dataclasses import dataclass


@dataclass
class StubMetadata:
    api_url: str
    app_name: str
    device_name: str
    controller_type: str
    routine_name: str
    parameters: dict[str, Any]
    created_at: str


@dataclass
class StubData:
    raw_data: dict[str, Any]
    metadata: StubMetadata | None = None

    def to_dict(self) -> dict[str, Any]:
        return TypeAdapter(type(self)).dump_python(self)

    @classmethod
    def from_str(cls, data: str) -> "StubData":
        return TypeAdapter(cls).validate_json(data)

    @classmethod
    def load_from_file(cls, file_path: Path) -> "StubData":
        with file_path.open("rb") as file:
            return cls.from_str(file.read().decode("utf-8"))
