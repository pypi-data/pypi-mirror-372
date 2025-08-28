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

from collections.abc import Callable
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

TraitT = TypeVar("TraitT", bound=str)
JsonDict = dict[str, Any]
ExtraType = JsonDict | Callable[[JsonDict], None] | None

ComponentRef = str


class Component(BaseModel, Generic[TraitT]):
    traits: list[TraitT]

    def get_summary_dict(self) -> dict[str, dict[str, Any]]:
        summary_dict = {}  # {field: value}

        for field, value in self.model_dump().items():
            if field not in ["dtype", "traits"] and value:
                tmp = {}
                v = value.get("value", None)

                tmp["value"] = v["value"] if isinstance(v, dict) else v
                tmp["err_minus"] = value.get("err_minus", None)
                tmp["err_plus"] = value.get("err_plus", None)
                tmp["calibration_status"] = value.get("calibration_status", None)

                extra = self.model_fields[field].json_schema_extra
                if isinstance(extra, dict):
                    tmp["display"] = extra.get("display", {})
                elif callable(extra):
                    tmp["display"] = extra({"display": "value"})
                summary_dict[field] = tmp

        return summary_dict


class ComponentUpdate(BaseModel): ...


class ProcessorUpdate(BaseModel): ...
